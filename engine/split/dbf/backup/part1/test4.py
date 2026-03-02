import dbfdm as dbf

# 创建一个新的 DBF 文件
table = dbf.Table('example.dbf',
                  'name C(20); age N(3,0)',
                  on_disk=False)
table.open(mode=dbf.READ_WRITE)

# 定义要写入的数据
data = [
    ('Alice', 25),
    ('Bob', 30),
    ('Charlie', 35)
]

for record in data:
    table.append(record)

table.create_backup('new_example.dbf',on_disk=True)
# 关闭表
table.close()