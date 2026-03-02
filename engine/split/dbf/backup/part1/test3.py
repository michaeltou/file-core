import dbf

# 创建一个测试表
table = dbf.Table('test.dbf', 'name C(20); age N(3,0)')
table.open(mode=dbf.READ_WRITE)

# 检查是否有 extend 方法
if hasattr(table, 'extend'):
    print("extend 方法可用")
else:
    print("extend 方法不可用")

table.close()