import psycopg2
import os
from psycopg2.extras import execute_values

# 从环境变量中获取用户名和密码
user = os.getenv('user')
password = os.getenv('password')

# 创建连接对象
conn = psycopg2.connect(database="fa6",
                        user='test',
                        password='hshome_123',
                        host="10.20.191.106",
                        port=30100)
cur = conn.cursor()  # 创建指针对象

# https://blog.csdn.net/weixin_41551276/article/details/127759056
# 定义要插入的数据
data = [
    (1, 'Paul', 32, 'California', 20000.00),
    (2, 'Allen', 25, 'Texas', 15000.00),
    (3, 'Teddy', 23, 'Norway', 20000.00),
    (4, 'Mark', 25, 'Rich-Mond ', 65000.00)
]
# 使用 execute_values 进行批量插入


execute_values(cur,"INSERT INTO COMPANY (ID, NAME, AGE, ADDRESS, SALARY) VALUES %s", data)


conn.commit()
cur.close()
conn.close()
