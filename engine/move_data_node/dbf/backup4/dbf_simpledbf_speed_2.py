from simpledbfdm import Dbf5
import pandas as pd
import time


def optimize_dbf_read(file_path, codec='gbk', chunk_size=None):
    """优化后的DBF读取函数（适用于机械硬盘）"""
    chunk_size = 1000
    dbf = Dbf5(file_path, codec=codec)

    # 禁用类型推断（最快读取方式）
    chunks = []
    for chunk in dbf.to_dataframe(chunksize=chunk_size, na=''):
        # 强制转换为字符串避免类型推断开销
        chunks.append(chunk.astype(str))

    return pd.concat(chunks)


# 使用示例
file_path = "test.dbf"
start_time = time.time()

df = optimize_dbf_read(file_path)
print(f'读取耗时: {time.time() - start_time:.2f}秒, 记录数: {len(df)}')