from dbfreaddm import DBF
import pandas as pd
import time

if __name__ == "__main__":

    file_path = 'big_data.dbf'

    start_time = time.time()

    table = DBF(file_path,encoding='gbk')

    ##1 获取基本信息
    print("总记录数：", len(table))
    field_names = table.field_names
    print("字段名：", field_names)
    end_time = time.time()
    print('获取基础字段信息，耗时', end_time - start_time,'秒')
    ##3 与pandas库结合使用
    start_time = time.time()

    original_df = pd.DataFrame(iter(table))
    print(original_df.head())
    end_time = time.time()
execution_time = end_time - start_time
print("加载数据,转成DataFrame耗时：", execution_time,',记录数:', len(table))






