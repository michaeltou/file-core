from simpledbfdm import Dbf5
import pandas as pd
import dbf

file_path = 'CIL20180420.DBF'
# file_path = 'GH99990.DBF'

# 使用 dbf 库读取 DeletionFlag 列
db = dbf.Table(file_path)
db.open()
deletion_flags = []
for record in db:
    deletion_flags.append(record)
db.close()

print(deletion_flags)