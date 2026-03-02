import time

import psycopg2
import os
from psycopg2.extras import execute_values
from dbfreaddm import DBF
import pandas as pd

table = DBF('/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf',encoding='gbk')


##1 获取基本信息
print("总记录数：", len(table))
field_names = table.field_names
print("字段名：", field_names)
original_df = pd.DataFrame(iter(table))

df = pd.DataFrame()
# df = original_df
df['ZQJC'] = original_df['ZQJC']
df['ZQDM'] = original_df['ZQDM']
df['GZRQ'] = original_df['GZRQ']
df['CSJC'] = original_df['CSJC']

df['SJDCQ'] = original_df['SJDCQ']
df['GJQJ'] = original_df['GJQJ']
df['YJLX'] = original_df['YJLX']
df['GJJJ'] = original_df['GJJJ']
df['GJSYL'] = original_df['GJSYL']
df['EVLXZJQ'] = original_df['EVLXZJQ']
df['EVLTX'] = original_df['EVLTX']
df['EVLJDJZ'] = original_df['EVLJDJZ']

head_data_frame = df.head(10)

# print(head_data_frame)

data_tuples = list(df.itertuples(index=False, name=None))

# print(data_tuples)
# 创建连接对象
conn = psycopg2.connect(database="fa6",
                        user='test',
                        password='hshome_123',
                        host="10.20.191.106",
                        port=30100)
cur = conn.cursor()  # 创建指针对象

start_time = time.time()
execute_values(cur,"INSERT INTO DBF_2_ORACLE_TABLE_27M (ZQJC, ZQDM, GZRQ, CSJC, SJDCQ, GJQJ, YJLX, GJJJ, GJSYL, EVLXZJQ, EVLTX, EVLJDJZ) VALUES  %s", data_tuples)
end_time = time.time()

conn.commit()
print("记录数：", len(table),"插入数据耗时：", end_time - start_time, "秒")
cur.close()
conn.close()
