import pandas as pd
from io import BytesIO

from ydbf import YDbfReader

# dbf文件说明：https://github.com/y10h/ydbf/blob/master/doc/links.md

dbf_file_path = 'SJSMX1_split.DBF'


# 以二进制模式打开 DBF 文件
with open(dbf_file_path, 'rb') as file:
    # 读取文件的所有字节内容
    dbf_bytes = file.read()

# 创建 BytesIO 对象
bytes_io = BytesIO()

# 将读取到的字节数据写入 BytesIO 对象
bytes_io.write(dbf_bytes)

# 将文件指针移动到开头，方便后续读取操作
bytes_io.seek(0)

fh =bytes_io
dbf_reader = YDbfReader(fh)

records = dbf_reader.read()

index = 0;
for record in records:
    index += 1
    if index % 10 == 0:
        break
    print(record)





