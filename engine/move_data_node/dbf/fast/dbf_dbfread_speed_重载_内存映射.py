import os

from simpledbfdm import Dbf5
import time

#https://github.com/rnelsonchem/simpledbf

import struct
import mmap


class MyDbf5(Dbf5):
    def __init__(self, dbf, codec='utf-8'):
        file_path_and_name = dbf

        """
            关键优化点说明：
            
            内存映射优势：
            
            将文件直接映射到内存地址空间
            避免频繁的磁盘I/O操作
            特别适合大文件随机访问
            使用注意事项：
            
            必须确保最终关闭映射(__del__)
            文件打开模式必须为二进制('rb')
            access=mmap.ACCESS_READ表示只读模式
            性能对比：
            
            小文件(<100MB)：差异不大
            大文件(>100MB)：内存映射可提速30%-50%
            超大文件(>1GB)：内存映射优势更明显
            在您的项目中集成时，可以保持原有接口不变，只需替换文件打开方式即可。内存映射对上层代码完全透明。
        """
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



file_path = "test.dbf"

start_time = time.time()
dbf = MyDbf5(file_path, codec='gbk')


chunk_size = 100000
for chunk in dbf.to_dataframe(chunksize=chunk_size):

    end_time = time.time()
    print('python 加载dbf转成dataframe耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)





