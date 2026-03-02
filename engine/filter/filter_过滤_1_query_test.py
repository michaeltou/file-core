
from simpledbfdm import Dbf5
import time


file_path_and_name = r'/Users/douming/Documents/读数工具重构/文件/国君文件/20240905行情/nqhq.dbf'
start_time = time.time()
dbf = Dbf5(file_path_and_name, codec='gbk')

df = dbf.to_dataframe()
end_time = time.time()

# 获取字段名称
field_names = df.columns

index_list = field_names.tolist()
print("字段名称:", index_list)


print('python 加载dbf文件耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)

fitler_df = df.query('HQZRSP >= 2.09 & HQJRKP >= 2.09 & HQCJJE == 12331')

print(fitler_df)