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

cur.execute('SELECT * FROM tm_test_table')
results = cur.fetchall()
print(results)

cur.close()
conn.close()
