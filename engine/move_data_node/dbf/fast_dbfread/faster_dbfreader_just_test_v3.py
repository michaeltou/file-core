
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

def parse_record(read,  encoding, fields):
    # one_record = [pure_field_parser.parse(field, read(field.length)) for field in fields]
    one_decoded_record = []
    for field in fields:
        name, typ, size = field.name, field.type, field.length
        value = read(field.length)
        # String (character) types, remove excess white space
        if typ == "C":
            # if name not in self._dtypes:
            #     self._dtypes[name] = "str"
            value = value.strip()
            # Convert empty strings to NaN
            if value == b'':
                value = ''
            else:
                value = value.decode(encoding)
                # Escape quoted characters
                # if self._esc:
                #     value = value.replace('"', self._esc + '"')

        # Numeric type. Stored as string
        elif typ == "N":
            # A decimal should indicate a float
            if b'.' in value:
                # if name not in self._dtypes:
                #     self._dtypes[name] = "float"
                value = float(value)
            # No decimal, probably an integer, but if that fails,
            # probably NaN
            else:
                try:
                    value = int(value)
                    # if name not in self._dtypes:
                    #     self._dtypes[name] = "int"
                except:
                    # I changed this for SQL->Pandas conversion
                    # Otherwise floats were not showing up correctly
                    value = float('nan')

        # Date stores as string "YYYYMMDD", convert to datetime
        elif typ == 'D':
            try:
                y, m, d = int(value[:4]), int(value[4:6]), \
                    int(value[6:8])
                # if name not in self._dtypes:
                #     self._dtypes[name] = "date"
            except:
                value = str('nan')
            else:
                value = datetime.date(y, m, d)

        # Booleans can have multiple entry values
        elif typ == 'L':
            # if name not in self._dtypes:
            #     self._dtypes[name] = "bool"
            if value in b'YyTt':
                value = True
            elif value in b'NnFf':
                value = False
            # '?' indicates an empty value, convert this to NaN
            else:
                value = bool('nan')

                # Floating points are also stored as strings.
        elif typ == 'F':
            # if name not in self._dtypes:
            #     self._dtypes[name] = "float"
            try:
                value = float(value)
            except:
                value = float('nan')

        else:
            err = 'Column type "{}" not yet supported.'
            raise ValueError(err.format(value))

        one_decoded_record.append(value)

    return one_decoded_record




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
                # one_record = [pure_field_parser.parse(field, read(field.length)) for field in fields]
                one_decoded_record = parse_record(read, encoding, fields)
                record_list.append(one_decoded_record)

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






