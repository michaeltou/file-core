import psycopg2
import os

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

cur.execute('''CREATE TABLE COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')

conn.commit()
cur.close()
conn.close()
