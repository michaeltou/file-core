from dask import delayed
from simpledbfdm import Dbf5
import dask.dataframe as dd
import time
from dask.distributed import Client


def read_dbf_chunk(file_path, start, end, codec='gbk'):
    """读取DBF文件指定范围的块"""
    dbf = Dbf5(file_path, codec=codec)
    return dbf.to_dataframe(chunksize=end - start, skiprows=start)


def dbf_to_dask_dataframe(file_path, npartitions=4, codec='gbk'):
    # 启动本地集群
    client = Client(threads_per_worker=1)  # 避免GIL争用

    # 先获取总记录数
    dbf = Dbf5(file_path, codec=codec)
    total_records = dbf.numrec

    # 计算分块范围
    chunk_size = total_records // npartitions
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(npartitions - 1)]
    chunks.append(((npartitions - 1) * chunk_size, total_records))  # 最后一块

    # 使用dask延迟加载
    ddfs = [
        dd.from_delayed(
            delayed(read_dbf_chunk)(file_path, start, end, codec),
            meta=read_dbf_chunk(file_path, 0, 1, codec).iloc[:0]  # 获取空DataFrame作为元数据
        ) for start, end in chunks
    ]

    # 合并所有分区
    return dd.concat(ddfs)


# 使用示例
file_path = "test.dbf"
start_time = time.time()

ddf = dbf_to_dask_dataframe(file_path, npartitions=4)
df = ddf.compute()  # 触发实际计算

end_time = time.time()
print(f'Dask并行加载耗时: {end_time - start_time:.2f}秒, 记录数: {len(df)}')