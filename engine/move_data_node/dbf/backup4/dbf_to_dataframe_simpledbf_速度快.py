from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf

def dbf_to_dataframe(dbf_file_path):
    start_time = time.time()
    dbf = Dbf5(dbf_file_path, codec='gbk')

    df = dbf.to_dataframe()
    end_time = time.time()

    # 获取字段名称
    field_names = df.columns
    # print("字段名称:", field_names)
    # 将Index对象转换成列表
    index_list = field_names.tolist()
    print("字段名称:", index_list)

    # 获取字段类型（通过查看DataFrame的数据类型推断DBF文件的字段类型）
    field_types = df.dtypes
    # print("字段类型:", field_types)
    dtype_map = df.dtypes.to_dict()
    # print("字段类型:", dtype_map)
    # for key, value in dtype_map.items():
    #     print(key, value)



    print('python 加载dbf文件耗时:', end_time - start_time,'秒, 记录数：', dbf.numrec)
    return df

# 假设DBF文件路径为'test.dbf'
file_path = '/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf'
file_path2 = "/Users/douming/Documents/读数工具重构/dbf_files/中债估值20240909.dbf"
file_path3 = "/Users/douming/Documents/读数工具重构/dbf_files/债券估值2023082917542120972.dbf"
dataframe = dbf_to_dataframe(file_path2)




# print(dataframe)

