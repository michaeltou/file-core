import pymssql

conn = pymssql.connect(
    server='rm-bp1y3r8130mcj6k80vo.sqlserver.rds.aliyuncs.com:3433',
    user='douming',
    password='$tm1Atest',
    database='testdb',
    as_dict=True
)
cursor = conn.cursor()

# SQL_QUERY = "SELECT  * FROM [db_owner].[tm_test_table];"
SQL_QUERY = "SELECT  * FROM db_owner.tm_test_table;"

cursor.execute(SQL_QUERY)

records = cursor.fetchall()
for r in records:
    print(r)


# 关闭游标和连接
cursor.close()
conn.close()