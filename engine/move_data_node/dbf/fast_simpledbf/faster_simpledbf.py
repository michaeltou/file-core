import datetime
import pandas as pd
from simpledbfdm import Dbf5

import struct
from engine.core.migrate_core_engine import *
#https://github.com/rnelsonchem/simpledbf
import engine.util.config as config
from multiprocessing import Pool, freeze_support

# 批量处理进程池大小
BATCH_PROCESS_COUNT = config.get_config_value("read_tool.file.batch.process.pool.size",4)

def one_process_do_task_for_simpledbf(file_path_and_name, encoding,start_index, end_index
                            ,my_uuid,
                            flow_node_dbf_config,
                            filter_logic,
                            target_interface_table,
                            field_mapping_config_list,
                            context_instance
                        ):


    start_time = time.time()
    log.info('my_uuid %s 并发 id %s 开始处理数据，记录个数是 %s, start_index= %s, end_index= %s',
             my_uuid,os.getpid(), end_index - start_index + 1 ,start_index, end_index )

    with open(file_path_and_name, 'rb') as file_for_one_process:
        num_rec,  len_header = struct.unpack('<xxxxLH22x',
                                                    file_for_one_process.read(32))
        num_fields = (len_header - 33) // 32

        # The first field is always a one byte deletion flag
        fields = [('DeletionFlag', 'C', 1), ]
        for fieldno in range(num_fields):
            name, typ, size = struct.unpack('<11sc4xB15x', file_for_one_process.read(32))
            # eliminate NUL bytes from name string
            name = name.strip(b'\x00')
            fields.append((name.decode(encoding), typ.decode(encoding), size))

        # Get the names only for DataFrame generation, skip delete flag
        columns = [f[0] for f in fields[1:]]

        terminator = file_for_one_process.read(1)
        assert terminator == b'\r'

        # Make a format string for extracting the data. In version 5 DBF, all
        # fields are some sort of structured string
        fmt = ''.join(['{:d}s'.format(fieldinfo[2]) for
                            fieldinfo in fields])
        fmt_size = struct.calcsize(fmt)

       # start of read data------------

        # 一次性读取多条记录
        all_record_size = num_rec
        start_time_batch = time.time()
        data = file_for_one_process.read(fmt_size * all_record_size)
        elapsed = time.time() - start_time_batch  # 计算耗时（单位：秒）
        # log.info('my_uuid %s 进程id %s 批量读取文件，耗时秒：%s 秒',my_uuid,os.getpid(),elapsed)  # 显示6位小数

        # 解析数据

    raw_record_list = []
    start_time_unpack = time.time()
    for i in range(all_record_size):
        if start_index <= i  and i <= end_index:
            record = struct.unpack(fmt, data[i * fmt_size:(i + 1) *  fmt_size])
            # If delete byte is not a space, record was deleted so skip
            '''
            --changed by douming on 2025-02-27
             reason:  
             0X20（即空格）:代表未删除
             0X2A（即星号）:代表已删除
             0X00（即空字符）:代表空值,   这种状态simpledbf没有进行处理，会导致部分数据读取不出来。我们需要把这类数据也归为正常数据。

             if record[0] != b' ':  # 原始逻辑 start
                continue            # 原始逻辑 end
            '''
            # 0X2A（即星号）:代表已删除, 如果该标志位是其它值，也需要进行读取，即把逻辑反过来。
            if record[0] == b'\x2A':
                continue

            raw_record_list.append(record)
        else:
            continue
    # log.info('uuid:%s, 进程id:%s, 把读取的文件通过struct.unpack转成raw原始数据列表，耗时 %s 秒 本次记录数量是: %s',my_uuid,os.getpid(),
    #       time.time() - start_time_unpack,  len(raw_record_list))

   # end of read data------------

    decoded_record_list = []

    for record_raw in raw_record_list:
        one_decoded_record = []
        for idx, value in enumerate(record_raw):
            name, typ, size = fields[idx]
            if name == 'DeletionFlag':
                continue

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
                if value in b'TyTt':
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

        # 把一行记录添加到列表中
        decoded_record_list.append(one_decoded_record)
    end_time = time.time()
    # log.info("uuid:%s, 进程id:%s, 单个进程解析数据，耗时 %s 秒 start_time = %s end_time = %s",
    #          my_uuid,os.getpid(),(end_time - start_time),  start_time,   end_time)

    start_time = time.time()
    df_for_one_process = pd.DataFrame(decoded_record_list, columns=columns)
    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    # print('文件类型',flow_node_dbf_config.get('fileType'),
    #      '过滤逻辑', filter_logic,
    #       '目标表：',target_interface_table,
    #       '字段映射配置列表：',field_mapping_config_list,
    #       '上下文实例：',context_instance
    #       )
    migrate_core_engine.dataframe_to_oracle(flow_node_dbf_config,
                                            df_for_one_process, filter_logic,
                                            target_interface_table,
                                            field_mapping_config_list,
                                            context_instance)

    end_time = time.time()
    # log.info("单个进程插入数据库，耗时 %s 秒 start_time = %s end_time = %s",(end_time - start_time),  start_time,   end_time)
    return None


class FasterDbf5(Dbf5):
    def __init__(self, dbf, codec='gbk' ):



        # 使用全局进程池
        self.pool = self.gen_pool()

        # 内存映射
        # file_path_and_name = dbf
        # with open(file_path_and_name, 'rb') as f:
        #     mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        #     # 使用mm对象代替self.f
        #     self.f = mm

        # Reading as binary so bytes will always be returned
        self.f = open(dbf, 'rb')

        self._enc = codec
        path, name = os.path.split(dbf)
        self.dbf = name
        self.file_path_and_name = dbf
        # Escape quotes, set by indiviual runners
        self._esc = None
        # Reading as binary so bytes will always be returned
        # self.f = open(dbf, 'rb')

        self.numrec, self.lenheader = struct.unpack('<xxxxLH22x',
                                                    self.f.read(32))
        self.numfields = (self.lenheader - 33) // 32

        # The first field is always a one byte deletion flag
        fields = [('DeletionFlag', 'C', 1), ]
        for fieldno in range(self.numfields):
            name, typ, size = struct.unpack('<11sc4xB15x', self.f.read(32))
            # eliminate NUL bytes from name string
            name = name.strip(b'\x00')
            fields.append((name.decode(self._enc), typ.decode(self._enc), size))
        self.fields = fields
        # Get the names only for DataFrame generation, skip delete flag
        self.columns = [f[0] for f in self.fields[1:]]

        terminator = self.f.read(1)
        assert terminator == b'\r'

        # Make a format string for extracting the data. In version 5 DBF, all
        # fields are some sort of structured string
        self.fmt = ''.join(['{:d}s'.format(fieldinfo[2]) for
                            fieldinfo in self.fields])
        self.fmtsiz = struct.calcsize(self.fmt)

    def __del__(self):
        # 确保关闭内存映射
        if hasattr(self, 'f') and self.f:
            self.f.close()

    @staticmethod
    def gen_pool(process_count = BATCH_PROCESS_COUNT):
        local_pool = Pool(processes=BATCH_PROCESS_COUNT)
        return local_pool

    def close_global_pool(self):
        """关闭全局进程池"""
        self.pool.close()  # 关闭进程池，不再接受新任务
        self.pool.join()  # 等待所有任务完成
        self.pool = None  # 将全局变量重置为None



    def to_dataframe_and_push_to_db(self
                                    ,my_uuid,
                                    flow_node_dbf_config,
                                    filter_logic,
                                    target_interface_table,
                                    field_mapping_config_list,
                                    context_instance
                                    ):
        # 总记录数
        total_record_size = self.numrec
        process_count = BATCH_PROCESS_COUNT  # 进程数

        # 计算每个进程处理的记录范围
        records_per_process = total_record_size // process_count
        remainder = total_record_size % process_count
        '''
         假设总记录数为10，进程数为4，则：
         tuple_param_list 里面的开始和结束索引元组为：
         [(0, 2), (3, 5), (6, 7), (8, 9)]
         重点说明： 1： start_index 从0开始。 2：end_index 结束索引，包含在内，为需要处理的最后一条记录的索引。
        '''
        # 生成每个进程的(start_index, end_index)元组
        tuple_param_list = []
        start = 0
        for i in range(process_count):
            end = start + records_per_process - 1
            if i < remainder:  # 将余数均匀分配到前几个进程
                end += 1
            tuple_param_list.append((self.file_path_and_name, self._enc, start, end
                                     ,my_uuid,
                                     flow_node_dbf_config,
                                     filter_logic,
                                     target_interface_table,
                                     field_mapping_config_list,
                                     context_instance
                                     ))
            start = end + 1

        start_time_submit = time.time()
        # 提交任务到进程池
        self.pool.starmap(one_process_do_task_for_simpledbf, tuple_param_list)

        # print("提交任务到进程池，总耗时", time.time() - start_time_submit, "秒")
        log.info("uuid:%s, 提交任务到进程池，总耗时 %s 秒", my_uuid,time.time() - start_time_submit)
        self.close_global_pool()

        return None




if __name__ == '__main__':
    freeze_support()
    file_path = "../backup4/test.dbf"

    start_time = time.time()
    dbf = FasterDbf5(file_path, codec='gbk')


    chunk_size = 100000
    df = dbf.to_dataframe()

    end_time = time.time()
    print('python 加载dbf转成dataframe耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)





