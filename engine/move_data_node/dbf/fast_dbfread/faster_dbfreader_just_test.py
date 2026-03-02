
from dbfreaddm import DBF as DBFReaderDBF, FieldParser

from dbfreaddm.dbf import ORDERED_DICT

import pandas as pd
import time
import os
import sys
import datetime
import struct
from multiprocessing import Pool, freeze_support
from dbfreaddm.memo import BinaryMemo
from decimal import Decimal
# 批量处理进程池大小
BATCH_PROCESS_COUNT = 4
# print("批量处理进程数：",BATCH_PROCESS_COUNT)

# 全局进程池变量
_global_pool = None

def get_global_pool(process_count=BATCH_PROCESS_COUNT):
    global _global_pool
    if _global_pool is None:
        _global_pool = Pool(processes=process_count)
    return _global_pool



from dbfreaddm.struct_parser import StructParser


DBFHeader = StructParser(
    'DBFHeader',
    '<BBBBLHHHBBLLLBBH',
    ['dbversion',
     'year',
     'month',
     'day',
     'numrecords',
     'headerlen',
     'recordlen',
     'reserved1',
     'incomplete_transaction',
     'encryption_flag',
     'free_record_thread',
     'reserved2',
     'reserved3',
     'mdx_flag',
     'language_driver',
     'reserved4',
     ])

DBFField = StructParser(
    'DBFField',
    '<11scLBBHBBBB7sB',
    ['name',
     'type',
     'address',
     'length',
     'decimal_count',
     'reserved1',
     'workarea_id',
     'reserved2',
     'reserved3',
     'set_fields_flag',
     'reserved4',
     'index_field_flag',
     ])


class PureFieldParser:
    def __init__(self, dbversion, encoding, char_decode_errors='strict', memofile=None):
        """Create a new field parser

        encoding is the character encoding to use when parsing
        strings."""
        # self.table = table
        self.dbversion = dbversion
        self.encoding =  encoding
        self.char_decode_errors =  char_decode_errors
        self._lookup = self._create_lookup_table()
        if memofile:
            self.get_memo = memofile.__getitem__
        else:
            self.get_memo = lambda x: None

    def decode_text(self, text):
        return str(text, self.encoding, errors=self.char_decode_errors)

    def _create_lookup_table(self):
        """Create a lookup table for field types."""
        lookup = {}

        for name in dir(self):
            if name.startswith('parse'):
                field_type = name[5:]
                if len(field_type) == 1:
                    lookup[field_type] = getattr(self, name)
                elif len(field_type) == 2:
                    # Hexadecimal ASCII code for field name.
                    # Example: parse2B() ('+' field)
                    field_type = chr(int(field_type, 16))
                    lookup[field_type] = getattr(self, name)

        return lookup

    def field_type_supported(self, field_type):
        """Checks if the field_type is supported by the parser

        field_type should be a one-character string like 'C' and 'N'.
        Returns a boolen which is True if the field type is supported.
        """
        return field_type in self._lookup

    def parse(self, field, data):
        """Parse field and return value"""
        try:
            func = self._lookup[field.type]
        except KeyError:
            raise ValueError('Unknown field type: {!r}'.format(field.type))
        else:
            return func(field, data)

    def parse0(self, field, data):
        """Parse flags field and return as byte string"""
        return data

    def parseC(self, field, data):
        """Parse char field and return unicode string"""
        return self.decode_text(data.rstrip(b'\0 '))

    def parseD(self, field, data):
        """Parse date field and return datetime.date or None"""
        try:
            return datetime.date(int(data[:4]), int(data[4:6]), int(data[6:8]))
        except ValueError:
            if data.strip(b' 0\0') == b'':
                # A record containing only spaces and/or zeros is
                # a NULL value.
                return None
            else:
                raise ValueError('invalid date {!r}'.format(data))

    def parseF(self, field, data):
        """Parse float field and return float or None"""
        # In some files * is used for padding.
        data = data.strip().strip(b'*')

        if data:
            return float(data)
        else:
            return None

    def parseI(self, field, data):
        """Parse integer or autoincrement field and return int."""
        # Todo: is this 4 bytes on every platform?
        return struct.unpack('<i', data)[0]

    def parseL(self, field, data):
        """Parse logical field and return True, False or None"""
        if data in b'TtYy':
            return True
        elif data in b'FfNn':
            return False
        elif data in b'? \0':
            return None
        else:
            # Todo: return something? (But that would be misleading!)
            message = 'Illegal value for logical field: {!r}'
            raise ValueError(message.format(data))

    def _parse_memo_index(self, data):
        if len(data) == 4:
            return struct.unpack('<I', data)[0]
        else:
            try:
                return int(data)
            except ValueError:
                if data.strip(b' \x00') == b'':
                    return 0
                else:
                    raise ValueError(
                        'Memo index is not an integer: {!r}'.format(data))

    def parseM(self, field, data):
        """Parse memo field (M, G, B or P)

        Returns memo index (an integer), which can be used to look up
        the corresponding memo in the memo file.
        """
        memo = self.get_memo(self._parse_memo_index(data))
        # Visual FoxPro allows binary data in memo fields.
        # These should not be decoded as string.
        if isinstance(memo, BinaryMemo):
            return memo
        else:
            if memo is None:
                return None
            else:
                return self.decode_text(memo)

    def parseN(self, field, data):
        """Parse numeric field (N)

        Returns int, float or None if the field is empty.
        """
        # In some files * is used for padding.
        data = data.strip().strip(b'*\0')

        try:
            return int(data)
        except ValueError:
            if not data.strip():
                return None
            else:
                # Account for , in numeric fields
                return float(data.replace(b',', b'.'))

    def parseO(self, field, data):
        """Parse long field (O) and return float."""
        return struct.unpack('d', data)[0]

    def parseT(self, field, data):
        """Parse time field (T)

        Returns datetime.datetime or None"""
        # Julian day (32-bit little endian)
        # Milliseconds since midnight (32-bit little endian)
        #
        # "The Julian day or Julian day number (JDN) is the number of days
        # that have elapsed since 12 noon Greenwich Mean Time (UT or TT) on
        # Monday, January 1, 4713 BC in the proleptic Julian calendar
        # 1. That day is counted as Julian day zero. The Julian day system
        # was intended to provide astronomers with a single system of dates
        # that could be used when working with different calendars and to
        # unify different historical chronologies." - wikipedia.org

        # Offset from julian days (used in the file) to proleptic Gregorian
        # ordinals (used by the datetime module)
        offset = 1721425  # Todo: will this work?

        if data.strip():
            # Note: if the day number is 0, we return None
            # I've seen data where the day number is 0 and
            # msec is 2 or 4. I think we can safely return None for those.
            # (At least I hope so.)
            #
            day, msec = struct.unpack('<LL', data)
            if day:
                dt = datetime.datetime.fromordinal(day - offset)
                delta = datetime.timedelta(seconds=msec / 1000)
                return dt + delta
            else:
                return None
        else:
            return None

    def parseY(self, field, data):
        """Parse currency field (Y) and return decimal.Decimal.

        The field is encoded as a 8-byte little endian integer
        with 4 digits of precision."""
        value = struct.unpack('<q', data)[0]

        # Currency fields are stored with 4 points of precision
        return Decimal(value) / 10000



    def parseG(self, field, data):
        """OLE Object stored in memofile.

        The raw data is returned as a binary string."""
        return self.get_memo(self._parse_memo_index(data))

    def parseP(self, field, data):
        """Picture stored in memofile.

        The raw data is returned as a binary string."""
        return self.get_memo(self._parse_memo_index(data))

    # Autoincrement field ('+')
    parse2B = parseI

    # Timestamp field ('@')
    parse40 = parseT

    # Varchar field ('V') (Visual FoxPro)
    parseV = parseC



def _skip_record(infile,header_length):
    # -1 for the record separator which was already read.
    infile.seek(header_length - 1, 1)


def _read_header(infile):
    # Todo: more checks?
    header = DBFHeader.read(infile)
    return header


def _read_field_headers(infile, encoding):
    field_names = []
    fields = []
    while True:
        sep = infile.read(1)
        if sep in (b'\r', b'\n', b''):
            # End of field headers
            break

        field = DBFField.unpack(sep + infile.read(DBFField.size - 1))

        field.type = chr(ord(field.type))

        # For character fields > 255 bytes the high byte
        # is stored in decimal_count.
        if field.type in 'C':
            field.length |= field.decimal_count << 8
            field.decimal_count = 0

        # Field name is b'\0' terminated.
        raw_field_name = field.name.split(b'\0')[0]
        field.name = raw_field_name.decode(encoding)
        field_names.append(field.name)
        fields.append(field)
    return field_names, fields

def one_process_do_task(file_path_and_name, encoding, start_index, end_index
                        # ,
                        # flow_node_dbf_config,
                        # filter_logic,
                        # target_interface_table,
                        # field_mapping_config_list,
                        # context_instance

                        ):
    record_type = b' '
    with open(file_path_and_name, 'rb') as infile:

        header = _read_header(infile)
        field_names, fields = _read_field_headers(infile, encoding)
        # Skip to first record.
        infile.seek(header.headerlen, 0)

        read = infile.read

        print('字段名称列表是:', field_names)
        all_field_total_length = sum([field.length for field in fields]) + 1
        print('所有字段长度之和是:', all_field_total_length)

        # data = infile.read(all_field_total_length * all_record_count)
        pure_field_parser = PureFieldParser(header.dbversion, encoding)
        record_list = []

        index  = 0;
        while True:
            index = index + 1
            if index ==20000:
                break
            sep = read(1)
            ''' 
              changed by douming on 2025/02/27.
              reason:  如果传入record_type为b' '(代表获取非删除记录，则把b'\x00'也加入到判断条件中。) 
            '''
            if sep == record_type or (record_type == b' ' and sep == b'\x00'):
                one_record = [pure_field_parser.parse(field, read(field.length)) for field in fields]
                record_list.append(one_record)

            elif sep in (b'\x1a', b''):
                # End of records.
                break
            else:
                _skip_record(infile, header.headerlen)

        pandas_df = pd.DataFrame(record_list, columns=field_names)
        print('转换后的dataframe:', pandas_df.head())


class FasterDBFReader(DBFReaderDBF):

    def __init__(self, filename, encoding=None, ignorecase=True,
                 lowernames=False,
                 parserclass=FieldParser,
                 recfactory=ORDERED_DICT,
                 load=False,
                 raw=False,
                 ignore_missing_memofile=False,
                 char_decode_errors='strict'):

        super().__init__(filename, encoding=encoding, ignorecase=ignorecase,
                 lowernames=lowernames,
                 parserclass=parserclass,
                 recfactory=recfactory,
                 load=load,
                 raw=raw,
                 ignore_missing_memofile=ignore_missing_memofile,
                 char_decode_errors=char_decode_errors)
        self.file_path_and_name = filename
        with open(filename, 'rb') as file_for_one_process:
            self.num_rec, self.len_header = struct.unpack('<xxxxLH22x',
                                                           file_for_one_process.read(32))
            self.num_fields = (self.len_header - 33) // 32

        # 使用全局进程池
        self.pool = get_global_pool()



    def push_record_to_db_with_multi_process(self):
        start_time_batch = time.time()
        # 总记录数
        total_record_size = self.num_rec
        process_count = BATCH_PROCESS_COUNT  # 进程数

        # 计算每个进程处理的记录范围
        records_per_process = total_record_size // process_count
        remainder = total_record_size % process_count

        # 生成每个进程的(start_index, end_index)元组
        tuple_param_list = []
        start = 0
        for i in range(process_count):
            end = start + records_per_process - 1
            if i < remainder:  # 将余数均匀分配到前几个进程
                end += 1
            tuple_param_list.append((self.file_path_and_name, self.encoding, start, end
                                     # ,
                                     # flow_node_dbf_config,
                                     # filter_logic,
                                     # target_interface_table,
                                     # field_mapping_config_list,
                                     # context_instance
                                     ))
            start = end + 1

        start_time_submit = time.time()

        # 创建包含4个工作进程的进程池

        # 提交任务到进程池
        result_list_for_multi_process = self.pool.starmap(one_process_do_task, tuple_param_list)

        print("提交任务到进程池，总耗时", time.time() - start_time_submit, "秒")




if __name__ == '__main__':
    # file_path = "JSMX_02.DBF"
    file_path = "test.dbf"
    start_time = time.time()
    table = FasterDBFReader(file_path, encoding='gbk' )


    # original_df = pd.DataFrame(iter(table))

    table.push_record_to_db_with_multi_process()
    end_time = time.time()
    print("转换dbf数据到dataframe耗时:", end_time - start_time, '秒，记录数:', len(table))






