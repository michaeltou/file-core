import pandas as pd
from io import BytesIO

from ydbfdm import YDbfReader
import time
# dbf文件说明：https://github.com/y10h/ydbf/blob/master/doc/links.md

dbf_file_path = 'SJSMX1_split.DBF'


# 以二进制模式打开 DBF 文件
with open(dbf_file_path, 'rb') as fh:
    start = time.time()
    dbf_reader = YDbfReader(fh)
    records = dbf_reader.read()
    print('读取 DBF 文件耗时：', time.time() - start, '秒')
    start = time.time()
    print('开始转换为 DataFrame')
    # 将列表数据转换为 DataFrame
    whole_dbf = pd.DataFrame(records)
    print('转换为 DataFrame：', time.time() - start, '秒')




