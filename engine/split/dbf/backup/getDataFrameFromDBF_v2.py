import pandas as pd
from dbfreaddm import DBF as DBFREAD_DBF
import time

# 定义 DBF 文件的路径
dbf_file_path = '../SJSMX1.DBF'

# 读取 DBF 文件
table = DBFREAD_DBF(dbf_file_path, encoding='gbk')

start_time = time.time()
# 将 DBF 数据转换为列表，每个元素是一个字典，表示一行数据
start_time = time.time()
print('读取DBF文件，转换成DataFrame-开始')
# 将列表数据转换为 DataFrame
df = pd.DataFrame(iter(table))


print('读取DBF文件，转换成DataFrame-结束,耗时：',time.time() - start_time,'秒')

