
from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
import engine.util.config as config
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd

if __name__ == "__main__":

    file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/SJSMX11204.DBF"

    my_dbf = Dbf5(file_path_and_name, codec='gbk')
    for chunk in my_dbf.to_dataframe(chunksize=100000):
        # 调用核心引擎，将dataframe数据插入数据库
        start_time = time.time()
        # 根据 'Name' 列进行分组
        grouped = chunk.groupby('MXZQZH')

        # 遍历分组对象，将每一组转换为独立的 DataFrame
        grouped_dfs = {}
        for name, group in grouped:
            grouped_dfs[name] = group
        end_time = time.time()
        print(f"Time used: {end_time - start_time} seconds")

        # 打印每个分组的 DataFrame
        for name, group_df in grouped_dfs.items():
            print(f"Group: {name}")
            # print(group_df)
            print()