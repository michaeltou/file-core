from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf






# 假设DBF文件路径为'test.dbf'
file_path = '/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf'
file_path2 = "/Users/douming/Documents/读数工具重构/dbf_files/中债估值20240909.dbf"
file_path3 = "/Users/douming/Documents/读数工具重构/dbf_files/债券估值2023082917542120972.dbf"

file_path4 = "ZGH.DBF"

dbf = Dbf5(file_path4, codec='gbk')
print('记录数', dbf.numrec)
print("字段名称:", dbf.columns)

dbf.to_csv('junk.csv')

# for chunk in dbf.to_dataframe(chunksize=100000):
#     print(chunk)



