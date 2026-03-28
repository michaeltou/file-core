import bigfile_engine.util.config as config
from multiprocessing import Pool, freeze_support

# 批量处理进程池大小
BATCH_PROCESS_COUNT = config.get_config_value("read_tool.file.batch.process.pool.size",4)
# print("批量处理进程数：",BATCH_PROCESS_COUNT)

# 全局进程池变量
_global_pool = None

def get_global_pool(process_count=BATCH_PROCESS_COUNT):
    global _global_pool
    if _global_pool is None:
        _global_pool = Pool(processes=process_count)
    return _global_pool

def close_global_pool():
    """关闭全局进程池"""
    global _global_pool
    if _global_pool is not None:
        _global_pool.close()  # 关闭进程池，不再接受新任务
        _global_pool.join()   # 等待所有任务完成
        _global_pool = None   # 将全局变量重置为None

