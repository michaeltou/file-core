import os


from sqlalchemy import create_engine, Column, Integer, String
import oracledb
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import platform
from sqlalchemy.orm import declarative_base
from sqlalchemy import event


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
oracle_engine = create_engine('oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                              echo=True, # 打印sql语句
                              pool_size=8, # 连接池大小
                              pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                              pool_timeout = 30, # 指定了从连接池中获取连接的超时时间，单位是秒。
                              )


with oracle_engine.connect() as connection:
    print('id:',connection.connection.connection_id)
    result = connection.execute(text("select seq_public_id.nextval l_id,3 l_value from dual"))
    for row in result:
        print('执行sql查询返回的结果：',row.l_id,row.l_value)

