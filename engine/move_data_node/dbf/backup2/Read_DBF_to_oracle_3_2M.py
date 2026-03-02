import os
import platform

import oracledb
from dbfreaddm import DBF

import pandas as pd
import time
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float



#
# # 链接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
# # 这里调用后使用的是oracle的thick mode

d = None                               # On Linux, no directory should be passed
if platform.system() == "Darwin":      # macOS
  d = os.environ.get("HOME")+("/Downloads/instantclient_23_3")
elif platform.system() == "Windows":   # Windows
  d = r"C:\oracle\instantclient_23_5"
oracledb.init_oracle_client(lib_dir=d)

# Oracle配置
#新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
oracle_engine = create_engine('oracle+oracledb://hs_fam_jx:hs_fam_jx@10.20.28.61:1521/orcl',
                              echo=True, # 打印sql语句
                              pool_size=8, # 连接池大小
                              pool_recycle=60 * 30  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                              )


table = DBF('/Users/douming/Documents/读数工具重构/dbf_files/gjshq20240909.dbf',encoding='gbk')


##1 获取基本信息
print("总记录数：", len(table))
field_names = table.field_names
print("字段名：", field_names)



##2 打印记录
print('--------------打印10条记录------------------start--------------------------')
count = 0
print_total_cnt = 10
## 这里的循环迭代，不会把文件全部加载到内存中，而是按需加载，所以不会占用过多内存。所以速度很快。
for record in table:
    if count < print_total_cnt:
        # 打印每一条记录，记录是以字典的形式呈现的，字段名作为键，字段值作为值。
        print(record)
    else:
        break
    count += 1
print('--------------打印10条记录------------------end--------------------------')


##3 与pandas库结合使用
start_time = time.time()

original_df = pd.DataFrame(iter(table))
end_time = time.time()
execution_time = end_time - start_time
print("加载数据,转成DataFrame耗时：", execution_time,',记录数:', len(table))



dtype_dict = {}


# df = pd.DataFrame()
df = original_df
# df['HYDM'] = original_df['HYDM']
# df['HQRQ'] = original_df['HQRQ']
# df['KPJ'] = original_df['KPJ']
# df['ZGJ'] = original_df['ZGJ']
# df['SPJ'] = original_df['SPJ']
# df['JQPJJ'] = original_df['JQPJJ']


for column in df.columns:
    if df[column].dtype in ['float', 'float64']:
        dtype_dict[column] = Float


start_time = time.time()

## 将dataFrame数据插入数据库
df.to_sql('dbf_2_oracle_table_3m', con=oracle_engine, if_exists='append',
                dtype=dtype_dict,
                index=False, chunksize=1000)





end_time = time.time()
execution_time = end_time - start_time

print("插入数据库总耗时：", execution_time,'秒,记录数:', len(table))




