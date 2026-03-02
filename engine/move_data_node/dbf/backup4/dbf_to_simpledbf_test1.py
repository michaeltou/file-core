from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf





file_path = "HK_TZXX_带有删除标记.DBF"

dbf = Dbf5(file_path, codec='gbk')
print('记录数', dbf.numrec)
print("字段名称:", dbf.columns)

df = dbf.to_dataframe()
print(df)



