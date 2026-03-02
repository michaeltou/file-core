import os

from simpledbfdm import Dbf5
import pandas as pd
import io
import time
import tempfile

def dbf_from_memory_to_dataframe(file_path, codec='gbk'):
    """将DBF文件先完整加载到内存再转换"""
    # 1. 将整个文件读入内存
    start_load = time.time()
    with open(file_path, 'rb') as f:
        dbf_data = f.read()
    print(f'文件加载耗时: {time.time() - start_load:.2f}秒')

    # 2. 使用io.BytesIO创建临时文件
    start_create = time.time()
    # 2. 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(dbf_data)
        tmp_path = tmp.name
        print(f'临时文件路径: {tmp_path}')

    end_create = time.time()
    print(f'临时文件创建耗时: {end_create - start_create:.2f}秒')


    # 3. 使用临时文件进行转换
    start_convert = time.time()
    try:
        dbf = Dbf5(tmp_path, codec=codec)
        df = dbf.to_dataframe()
    finally:
        pass
        # 确保删除临时文件
        # os.unlink(tmp_path)

    print(f'内存转换耗时: {time.time() - start_convert:.2f}秒')
    return df


# 使用示例
file_path = "test.dbf"
start_time = time.time()

df = dbf_from_memory_to_dataframe(file_path)
print(f'总耗时: {time.time() - start_time:.2f}秒, 记录数: {len(df)}')