from engine.split.dbf.backup.part1.dftodbf import dbfwrite
import pandas as pd
import time
from dbfreaddm import DBF


file_path = '/Users/douming/Downloads/中泰文件拆分慢/SJSMX1.DBF'

start_time = time.time()

table = DBF(file_path,encoding='gbk')

##1 获取基本信息
print("总记录数：", len(table))
field_names = table.field_names
print("字段名：", field_names)
end_time = time.time()
print('获取基础字段信息，耗时', end_time - start_time,'秒')
##3 与pandas库结合使用
start_time = time.time()

df = pd.DataFrame(iter(table))

head = df.iloc[0:10]

# 批量写入优化方案
start_time = time.time()
print("开始写入dbf文件")
dbfwrite(head, 'big_data.dbf')

print(f"总耗时: {time.time() - start_time:.2f}秒")