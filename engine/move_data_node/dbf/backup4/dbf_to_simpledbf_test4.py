from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf





file_path = "HK_ZQYE.DBF"
dbf = Dbf5(file_path, codec='gbk')


df = dbf.to_dataframe()
print(df)



