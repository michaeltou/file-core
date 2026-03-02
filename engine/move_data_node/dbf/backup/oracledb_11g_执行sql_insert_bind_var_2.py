import os

import oracledb
import platform
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
# 创建连接池. 估值库
pool = oracledb.create_pool(user='hs_fam_jx', password='hs_fam_jx', dsn='10.20.28.61:1521/orcl',
                            min=1, max=1, increment=0, getmode= oracledb.POOL_GETMODE_TIMEDWAIT,timeout=3)


with pool.acquire() as connection:
    with connection.cursor() as cursor:
        # 执行sql语句
        cursor.execute("""insert into MyTable (id, name, age) 
                       values (:id, :name, :age)""",
                       id=2, name='Rose', age=18)
        # 提交事务
        connection.commit()




with pool.acquire() as connection:
    with connection.cursor() as cursor:
        result = cursor.execute("select * from MyTable")
        columns = [column[0] for column in result.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        for row in result:
            print(row)
