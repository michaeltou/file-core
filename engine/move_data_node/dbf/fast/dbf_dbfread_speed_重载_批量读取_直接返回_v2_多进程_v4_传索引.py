import datetime
import os
import pandas as pd

from simpledbfdm import Dbf5
import time

#https://github.com/rnelsonchem/simpledbf

import struct
import mmap
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, freeze_support
import time
import os
import numpy as np

def one_process_do_task(file_path_and_name, encoding,start_index, end_index):

    start_time = time.time()
    print('进程id ', os.getpid(), '开始处理数据，记录个数是', end_index - start_index + 1,',start_index=',start_index,',end_index=',end_index )
    file_for_one_process = open(file_path_and_name, 'rb')

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
    print(f"批量读取文件，耗时秒：{elapsed:.6f}秒")  # 显示6位小数

    raw_record_list = []

    start_time_unpack = time.time()

    for i in range(all_record_size):
        if start_index <= i  and i <= end_index:
            record = struct.unpack(fmt, data[i * fmt_size:(i + 1) *  fmt_size])
            # 0X2A（即星号）:代表已删除, 如果该标志位是其它值，也需要进行读取，即把逻辑反过来。
            if record[0] == b'\x2A':
                continue
            raw_record_list.append(record)
        else:
            continue
    print("把读取的文件通过struct.unpack转成raw原始数据列表，耗时",
          time.time() - start_time_unpack, "秒",'本次记录数量是:',len(raw_record_list))

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

        # 把一行记录添加到列表中
        decoded_record_list.append(one_decoded_record)

    end_time = time.time()
    print("单个进程解析数据，耗时{}秒".format(end_time - start_time),'start_time=',start_time, 'end_time=',end_time)
    return None


class FasterDbf5(Dbf5):
    def __init__(self, dbf, codec='gbk',process_num = 4):
        # ...原有初始化...

        # self.pool = Pool(processes=process_num)  # 预热进程池

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

        if hasattr(self, 'pool'):
            self.pool.close()  # 记得关闭池




    def _get_recs_direct_list(self):
        start_time_batch = time.time()
        # 总记录数
        total_record_size = self.numrec
        process_count = 4  # 进程数

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
            tuple_param_list.append((self.file_path_and_name, self._enc, start, end))
            start = end + 1

        start_time_submit = time.time()

        # 创建包含4个工作进程的进程池
        with Pool(processes=process_count) as pool:
            # 提交任务到进程池
            result_list_for_multi_process = pool.starmap(one_process_do_task, tuple_param_list)


        print("提交任务到进程池，总耗时", time.time() - start_time_submit, "秒")

        # for record in raw_record_list:
        #     # 0X2A（即星号）:代表已删除, 如果该标志位是其它值，也需要进行读取，即把逻辑反过来。
        #     if record[0] == b'\x2A':
        #         continue

        final_record_list = []
        # start_time_for_complete = time.time()
        # for result_list_for_one_process in result_list_for_multi_process:
        #     final_record_list.extend(result_list_for_one_process)
        # print("把多个进程返回的结果合并，耗时", time.time() - start_time_for_complete, "秒")

        end_time = time.time()
        print("通过多进程解析数据，总共耗时{}秒".format(end_time - start_time_batch))
        return final_record_list

    def to_dataframe(self, chunksize=None, na='nan'):
        '''Return the DBF contents as a DataFrame.

        Parameters
        ----------
        chunksize : int, optional
            Maximum number of records to process at any given time. If 'None'
            (defalut), process all records.

        na : various types accepted, optional
            The value that will be used to replace missing or malformed
            entries. Right now this accepts pretty much anything, and that
            value will be used as a replacement. (May not do what you expect.)
            However, the strings 'na' or 'nan' (case insensitive) will insert
            float('nan'), the string 'none' (case insensitive) or will insert
            the Python object `None`. Default for DataFrame is NaN ('nan');
            however, float/int columns are always float('nan')

        Returns
        -------
        DataFrame (chunksize == None)
            The DBF file contents as a Pandas DataFrame

        Generator (chunksize != None)
            This generator returns DataFrames with the maximum number of
            records equal to chunksize. (May be less)

        Notes
        -----
        This method requires Pandas >= 0.15.2.
        '''
        self._na_set(na)
        if not chunksize:
            # _get_recs is a generator, convert to list for DataFrame
            # results = list(self._get_recs(chunk=chunk))
            results = self._get_recs_direct_list()
            df = pd.DataFrame(results, columns=self.columns)
            del(results) # Free up the memory? If GC works properly
            return df
        else:
            # Return a generator function instead
            return self._df_chunks(chunksize)

    def _df_chunks(self, chunksize):
        '''A DataFrame chunk generator.

        See `to_dataframe`.
        '''
        chunks = self._chunker(chunksize)
        # Keep track of the index, otherwise every DataFrame will be indexed
        # starting at 0
        idx = 0
        for chunk in chunks:
            # results = list(self._get_recs(chunk=chunk))
            results = self._get_recs_direct_list(chunk=chunk)
            num = len(results) # Avoids skipped records problem
            start_time = time.time()
            df = pd.DataFrame(results, columns=self.columns,
                              index=range(idx, idx+num))
            end_time = time.time()
            print("pandas 把list转成dataframe，耗时{}秒".format(end_time - start_time))
            idx += num
            del(results)
            yield df



if __name__ == '__main__':
    freeze_support()
    file_path = "test.dbf"

    start_time = time.time()
    dbf = FasterDbf5(file_path, codec='gbk')




    chunk_size = 100000
    df = dbf.to_dataframe()

    end_time = time.time()
    print('python 加载dbf转成dataframe耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)





