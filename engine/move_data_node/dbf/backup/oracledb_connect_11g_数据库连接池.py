import os
import platform
import oracledb
from sqlalchemy import create_engine
'''
mac 环境下，oracle 11g客户端的安装路径，
其它环境参考教程：https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#
'''
# 链接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
# 这里调用后使用的是oracle的thick mode
d = None                               # On Linux, no directory should be passed
if platform.system() == "Darwin":      # macOS
  d = os.environ.get("HOME")+("/Downloads/instantclient_23_3")
elif platform.system() == "Windows":   # Windows
  d = r"C:\oracle\instantclient_23_5"
oracledb.init_oracle_client(lib_dir=d)

# 11g 连接数据库
# connection = oracledb.connect(user='hs_fam_jx', password='hs_fam_jx', dsn='10.20.28.61:1521/orcl')
#

'''
getmode= oracledb.POOL_GETMODE_TIMEDWAIT 和 timeout=3（超时3s） 要配套使用
'''

pool = oracledb.create_pool(user='hs_fam_jx', password='hs_fam_jx', dsn='10.20.28.61:1521/orcl',
                            min=1, max=1, increment=0, getmode= oracledb.POOL_GETMODE_TIMEDWAIT,timeout=3)

connection = pool.acquire()

# 这里可以验证超时情况
connection1 = pool.acquire()



# 释放连接回连接池
pool.release(connection)
# 释放连接回连接池
pool.release(connection1)


# 关闭连接池
pool.close()