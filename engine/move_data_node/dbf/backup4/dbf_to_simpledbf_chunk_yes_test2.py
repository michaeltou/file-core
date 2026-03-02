from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf


file_path = "永安期货_0000_20220818_1_SettlementDetail.DBF"

dbf = Dbf5(file_path, codec='gbk')


chunk_size = 100000
for chunk in dbf.to_dataframe(chunksize=chunk_size):
    print(chunk)




