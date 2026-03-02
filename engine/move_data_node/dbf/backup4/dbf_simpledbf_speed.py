from simpledbfdm import Dbf5
import time

#https://github.com/rnelsonchem/simpledbf


file_path = "test.dbf"

start_time = time.time()
dbf = Dbf5(file_path, codec='gbk')


chunk_size = 100000
for chunk in dbf.to_dataframe(chunksize=chunk_size):

    end_time = time.time()
    print('python 加载dbf转成dataframe耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)

