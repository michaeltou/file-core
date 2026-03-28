from dbfreaddm import DBF as DBFReaderDBF, FieldParser

from dbfreaddm.dbf import ORDERED_DICT

import pandas as pd
import time
import datetime
import struct

import bigfile_engine.util.config as config
from multiprocessing import Pool

from dbfreaddm.struct_parser import StructParser
from engine.core.migrate_core_engine import *

BATCH_PROCESS_COUNT = config.get_config_value("read_tool.file.batch.process.pool.size",4)

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



'''
跳过一行记录（减去1，代表标志位不包含在内，标志位已经做了读取）
'''
def _skip_record(infile, record_length):
    # -1 for the record separator which was already read.
    infile.seek(record_length - 1, 1)


def _read_header(infile):
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


def parse_record(read, encoding, fields):
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


def one_process_do_task_for_dbfreader(file_path_and_name, encoding, start_index, end_index,
                         my_uuid,
                        flow_node_dbf_config,
                        filter_logic,
                        target_interface_table,
                        field_mapping_config_list,
                        context_instance

                        ):
    start_time = time.time()
    # start_index 从0开始
    # end_index 结束索引，包含在内
    # print('开始处理文件:', file_path_and_name, '开始索引:', start_index, '结束索引:', end_index)
    log.info('uuid: %s,进程id:%s, 开始处理文件:%s, 开始索引:%s, 结束索引:%s', my_uuid, os.getpid(), file_path_and_name, start_index, end_index)

    record_type = b' '
    with open(file_path_and_name, 'rb') as infile:

        header = _read_header(infile)
        field_names, fields = _read_field_headers(infile, encoding)
        # Skip to first record.
        infile.seek(header.headerlen, 0)

        read = infile.read

        record_list = []

        line_index = -1;
        while True:
            # 行号索引加1,第一行索引为0
            line_index = line_index + 1

            #这里对行号进行快速的判断。
            #当前行号在开始和结束行号之间，则处理该行记录（后面会进行处理）。
            if start_index <= line_index <= end_index:
                pass
            # 当前行号大于结束行号的场景，直接退出循环。
            elif line_index > end_index:
                break
            # 当前行号小于开始行号的场景，直接调到开始行号处
            elif line_index < start_index:
                # 跳过开始行之前的记录
                # 头文件长度 + 记录长度 * 起始索引
                skip_length_before_start_index = header.headerlen + (header.recordlen * start_index)
                infile.seek(skip_length_before_start_index, 0)
                # 调到开始行号处
                line_index = start_index

            sep = read(1)
            #
            #changed by douming on 2025/02/27.
            #reason:  如果传入record_type为b' '(代表获取非删除记录，则把b'\x00'也加入到判断条件中。)
            #
            if sep == record_type or (record_type == b' ' and sep == b'\x00'):
                if start_index <= line_index <= end_index:
                    one_decoded_record = parse_record(read, encoding, fields)
                    record_list.append(one_decoded_record)
            elif sep in (b'\x1a', b''):
                # End of records.
                break
            else:
                _skip_record(infile, header.recordlen)

        df_for_one_process = pd.DataFrame(record_list, columns=field_names)
        # print('单进程转换dbf数据到dataframe完成，记录数:', df_for_one_process.shape[0],'耗时:', time.time() - start_time)
        log.info('uuid: %s, 进程id:%s, 单进程转换dbf数据到dataframe完成，记录数:%s, 耗时:%s', my_uuid, os.getpid(), df_for_one_process.shape[0], time.time() - start_time)

        # start_time = time.time()
        # 创建读数引擎
        migrate_core_engine = MigrateCoreEngine()

        migrate_core_engine.dataframe_to_oracle(flow_node_dbf_config,
                                                df_for_one_process, filter_logic,
                                                target_interface_table,
                                                field_mapping_config_list,
                                                context_instance)

        # end_time = time.time()
        #log.info('uuid: %s, 进程id:%s, 单进程插入数据库，耗时 %s 秒', my_uuid, os.getpid(), end_time - start_time)
        # print('单进程插入数据库，耗时: ', end_time - start_time ,'秒')


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
        self.pool = self.gen_pool()

    @staticmethod
    def gen_pool(process_count=BATCH_PROCESS_COUNT):
        local_pool = Pool(processes=BATCH_PROCESS_COUNT)
        return local_pool

    def close_global_pool(self):
        """关闭全局进程池"""
        self.pool.close()  # 关闭进程池，不再接受新任务
        self.pool.join()  # 等待所有任务完成
        self.pool = None  # 将全局变量重置为None

    def push_record_to_db_with_multi_process(self,my_uuid,
                                             flow_node_dbf_config,
                                             filter_logic,
                                             target_interface_table,
                                             field_mapping_config_list,
                                             context_instance):

        # 总记录数
        total_record_size = self.num_rec
        process_count = BATCH_PROCESS_COUNT  # 进程数

        # 计算每个进程处理的记录范围
        records_per_process = total_record_size // process_count
        remainder = total_record_size % process_count

        # 生成每个进程的(start_index, end_index)元组
        tuple_param_list = []

        #
        #      假设总记录数为10，进程数为4，则：
        #      tuple_param_list 里面的开始和结束索引元组为：
        #      [(0, 2), (3, 5), (6, 7), (8, 9)]
        #      重点说明： 1： start_index 从0开始。 2：end_index 结束索引，包含在内，为需要处理的最后一条记录的索引。
        #
        start = 0
        for i in range(process_count):
            end = start + records_per_process - 1
            if i < remainder:  # 将余数均匀分配到前几个进程
                end += 1
            tuple_param_list.append((self.file_path_and_name, self.encoding, start, end,
                                     my_uuid,
                                     flow_node_dbf_config,
                                     filter_logic,
                                     target_interface_table,
                                     field_mapping_config_list,
                                     context_instance
                                     ))
            start = end + 1

        start_time_submit = time.time()

        # 创建包含4个工作进程的进程池

        # 提交任务到进程池
        self.pool.starmap(one_process_do_task_for_dbfreader, tuple_param_list)
        log.info('uuid: %s, 进程池提交任务完成，总耗时 %s 秒', my_uuid, time.time() - start_time_submit)
        # print("提交任务到进程池，总耗时", time.time() - start_time_submit, "秒")
        self.close_global_pool()

if __name__ == '__main__':
    file_path = "JSMX_02.DBF"
    # file_path = "test.dbf"
    start_time = time.time()
    table = FasterDBFReader(file_path, encoding='gbk')

    table.push_record_to_db_with_multi_process( )
    end_time = time.time()
    print("转换dbf数据到dataframe耗时:", end_time - start_time, '秒，记录数:', len(table))






