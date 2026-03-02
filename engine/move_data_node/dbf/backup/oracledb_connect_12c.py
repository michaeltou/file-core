import oracledb

import oracledb

# 11g 连接数据库
#connection = oracledb.connect(user='hs_fam_jx', password='hs_fam_jx', dsn='10.20.28.61:1521/orcl')

#12g 连接数据库
connection = oracledb.connect(user='fam_66', password='fam_66', dsn='10.20.146.69:1521/orcl')

# 创建游标
cursor = connection.cursor()

# 查询操作
query = "SELECT * FROM TSYS_MENU"
cursor.execute(query)

# 获取查询结果并打印
results = cursor.fetchall()
for row in results:
    print(row)

# # 插入操作
# insert_data = [
#     ('value1', 123),
#     ('value2', 456)
# ]
# insert_query = "INSERT INTO your_table_name (column1, column2) VALUES (:1, :2)"
# cursor.executemany(insert_query, insert_data)
# connection.commit()
#
# # 更新操作
# update_query = "UPDATE your_table_name SET column2 = :new_value WHERE column1 = :target_value"
# cursor.execute(update_query, {'new_value': 789, 'target_value': 'value1'})
# connection.commit()

# 关闭游标和连接
cursor.close()
connection.close()