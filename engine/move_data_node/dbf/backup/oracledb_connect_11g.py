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
connection = oracledb.connect(user='hs_fam_jx', password='hs_fam_jx', dsn='10.20.28.61:1521/orcl')



# 创建游标
cursor = connection.cursor()


# 插入操作
insert_data = [
    ('value1', 123),
    ('value2', 456)
]
# insert_query = "INSERT INTO your_table_name (column1, column2) VALUES (:1, :2)"
# cursor.executemany(insert_query, insert_data)
# connection.commit()

# # 更新操作
# update_query = "UPDATE your_table_name SET column2 = :new_value WHERE column1 = :target_value"
# cursor.execute(update_query, {'new_value': 789, 'target_value': 'value1'})
# connection.commit()


# 查询操作
query = "SELECT * FROM your_table_name"
cursor.execute(query)

# 获取查询结果并打印
results = cursor.fetchall()
for row in results:
    print(row)


# 关闭游标和连接
cursor.close()
connection.close()