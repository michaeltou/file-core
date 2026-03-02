import pandas as pd
from io import BytesIO

from ydbf import YDbfReader

# dbf文件说明：https://github.com/y10h/ydbf/blob/master/doc/links.md

dbf_file_path = 'SJSMX1_split.DBF'


# 以二进制模式打开 DBF 文件
with open(dbf_file_path, 'rb') as fh:
    dbf_reader = YDbfReader(fh)
    records = dbf_reader.read()
    index = 0;
    for record in records:
        index += 1
        if index % 10 == 0:
            break
        print(record)





