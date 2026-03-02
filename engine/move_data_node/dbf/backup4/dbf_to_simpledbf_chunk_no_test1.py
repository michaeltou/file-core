from simpledbfdouming import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf


file_path = "永安期货_0000_20220818_1_SettlementDetail.DBF"

dbf = Dbf5(file_path, codec='gbk')


df = dbf.to_dataframe()
print(df)



