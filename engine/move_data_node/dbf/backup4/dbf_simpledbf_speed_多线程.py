from simpledbfdm import Dbf5
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def process_chunk(start, end):
    """处理指定范围的记录块"""
    chunk = dbf.to_dataframe(chunksize=end-start, skiprows=start)
    # 在这里添加你的处理逻辑
    return chunk

file_path = "test.dbf"
dbf = Dbf5(file_path, codec='gbk')
total_records = dbf.numrec
chunk_size = 10000

start_time = time.time()

# 计算分片范围
chunks = [(i, min(i+chunk_size, total_records))
         for i in range(0, total_records, chunk_size)]

# 使用多线程处理
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_chunk, *zip(*chunks)))

end_time = time.time()
print(f'多线程加载总耗时: {end_time-start_time:.2f}秒')