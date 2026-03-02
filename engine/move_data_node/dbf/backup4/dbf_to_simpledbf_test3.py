from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf





# file_path = "永安期货_0000_20220818_1_SettlementDetail.DBF"
file_path = "/Users/douming/Documents/读数工具重构/文件/测试文件/compare/2/永安期货_0000_20220818_1_SettlementDetail.DBF"
dbf = Dbf5(file_path, codec='gbk')


df = dbf.to_dataframe()
print(df)



