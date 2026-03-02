import os
import platform
import oracledb
import pandas as pd
import time
from sqlalchemy import create_engine



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

query = "SELECT * FROM dbf_2_oracle_table"

df = pd.read_sql(query, oracle_engine)



end_time = time.time()





