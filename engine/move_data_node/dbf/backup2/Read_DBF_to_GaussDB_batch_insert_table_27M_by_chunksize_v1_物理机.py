import time
import psycopg2
import os
from psycopg2.extras import execute_values
from dbfreaddm import DBF
import pandas as pd

table = DBF('ZZGZ20180307.dbf', encoding='gbk')

# 1 获取基本信息
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

# 分批插入数据
batch_size = 1000
total_records = len(df)
num_batches = total_records // batch_size + 1

# 创建连接对象
conn = psycopg2.connect(database="fa6",
                        user='fa68_fam',
                        password='hshome@123',
                        host="10.20.190.30",
                        port=30100)
cur = conn.cursor()  # 创建指针对象

start_time = time.time()
for i in range(num_batches):
    start = i * batch_size
    end = min((i + 1) * batch_size, total_records)
    batch_data = df[start:end]
    data_tuples = list(batch_data.itertuples(index=False, name=None))
    execute_values(cur, "INSERT INTO DBF_2_ORACLE_TABLE_27M (ZQJC, ZQDM, GZRQ, CSJC, "
                        "SJDCQ, GJQJ, YJLX, GJJJ, GJSYL, EVLXZJQ, EVLTX, EVLJDJZ) VALUES %s", data_tuples)
    conn.commit()

end_time = time.time()

print("记录数：", total_records, "插入数据耗时：", end_time - start_time, "秒")
cur.close()
conn.close()
