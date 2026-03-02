import time

from simpledbfdm import Dbf5
import pandas as pd
from multiprocessing import Pool
import os
import struct
import mmap



def process_chunk(args):
    """多进程处理DBF文件块"""
    file_path, start, end, codec = args
    dbf = Dbf5(file_path, codec=codec)
    # 显式设置_na属性
    dbf._na = float('nan')  # 或者使用其他默认值如''

    records = []
    for i, record in enumerate(dbf._get_recs()):
        if i >= end:
            break
        if i >= start:
            records.append(record)
    return pd.DataFrame(records, columns=dbf.columns)


def concurrent_dbf_to_dataframe(file_path, codec='gbk', workers=4):
    """并发读取DBF文件"""
    # 先获取总记录数
    dbf = Dbf5(file_path, codec=codec)
    total_records = dbf.numrec

    # 计算每个worker处理的范围
    chunk_size = total_records // workers
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(workers - 1)]
    chunks.append(((workers - 1) * chunk_size, total_records))

    # 准备参数
    args = [(file_path, start, end, codec) for start, end in chunks]

    # 使用多进程池
    with Pool(processes=workers) as pool:
        results = pool.map(process_chunk, args)

    return pd.concat(results)

if __name__ == '__main__':
    file_path = "test.dbf"
    start_time = time.time()
    df = concurrent_dbf_to_dataframe(file_path, workers=4)
    end_time = time.time()
    print("读取{}条记录，耗时{}秒".format(len(df), end_time - start_time))
    print(df.head())