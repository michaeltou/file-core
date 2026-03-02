import datetime
import os

from simpledbfdm import Dbf5
import time

#https://github.com/rnelsonchem/simpledbf

import struct
import mmap


class MyDbf5(Dbf5):
    def __init__(self, dbf, codec='utf-8'):
        file_path_and_name = dbf
        with open(file_path_and_name, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            # 使用mm对象代替self.f
            self.f = mm

        self._enc = codec
        path, name = os.path.split(dbf)
        self.dbf = name
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


    def _get_recs(self, chunk=None):
        ''' Generator that returns individual records.

                Parameters
                ----------
                chunk : int, optional
                    Number of records to return as a single chunk. Default 'None',
                    which uses all records.
        '''
        if chunk == None:
            chunk = self.numrec

        # 一次性读取多条记录
        my_chunk_size = chunk
        data = self.f.read(self.fmtsiz * my_chunk_size)
        for i in range(my_chunk_size):
            record = struct.unpack(self.fmt, data[i * self.fmtsiz:(i + 1) * self.fmtsiz])

        # for i in range(chunk):
            # Extract a single record
            # record = struct.unpack(self.fmt, self.f.read(self.fmtsiz))
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

            # Save the column types for later
            self._dtypes = {}
            result = []
            for idx, value in enumerate(record):
                name, typ, size = self.fields[idx]
                if name == 'DeletionFlag':
                    continue

                # String (character) types, remove excess white space
                if typ == "C":
                    if name not in self._dtypes:
                        self._dtypes[name] = "str"
                    value = value.strip()
                    # Convert empty strings to NaN
                    if value == b'':
                        value = self._na
                    else:
                        value = value.decode(self._enc)
                        # Escape quoted characters
                        if self._esc:
                            value = value.replace('"', self._esc + '"')

                # Numeric type. Stored as string
                elif typ == "N":
                    # A decimal should indicate a float
                    if b'.' in value:
                        if name not in self._dtypes:
                            self._dtypes[name] = "float"
                        value = float(value)
                    # No decimal, probably an integer, but if that fails,
                    # probably NaN
                    else:
                        try:
                            value = int(value)
                            if name not in self._dtypes:
                                self._dtypes[name] = "int"
                        except:
                            # I changed this for SQL->Pandas conversion
                            # Otherwise floats were not showing up correctly
                            value = float('nan')

                # Date stores as string "YYYYMMDD", convert to datetime
                elif typ == 'D':
                    try:
                        y, m, d = int(value[:4]), int(value[4:6]), \
                            int(value[6:8])
                        if name not in self._dtypes:
                            self._dtypes[name] = "date"
                    except:
                        value = self._na
                    else:
                        value = datetime.date(y, m, d)

                # Booleans can have multiple entry values
                elif typ == 'L':
                    if name not in self._dtypes:
                        self._dtypes[name] = "bool"
                    if value in b'TyTt':
                        value = True
                    elif value in b'NnFf':
                        value = False
                    # '?' indicates an empty value, convert this to NaN
                    else:
                        value = self._na

                # Floating points are also stored as strings.
                elif typ == 'F':
                    if name not in self._dtypes:
                        self._dtypes[name] = "float"
                    try:
                        value = float(value)
                    except:
                        value = float('nan')

                else:
                    err = 'Column type "{}" not yet supported.'
                    raise ValueError(err.format(value))

                result.append(value)
            yield result



file_path = "test.dbf"

start_time = time.time()
dbf = MyDbf5(file_path, codec='gbk')


chunk_size = 100000
for chunk in dbf.to_dataframe(chunksize=chunk_size):

    end_time = time.time()
    print('python 加载dbf转成dataframe耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)





