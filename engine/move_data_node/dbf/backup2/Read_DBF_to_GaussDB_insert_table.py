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
cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (1, 'Paul', 32, 'California', 20000.00 )")

cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (2, 'Allen', 25, 'Texas', 15000.00 )")

cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )")

cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )")


conn.commit()
cur.close()
conn.close()
