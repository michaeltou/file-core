import pandas as pd
import time


class BelongLocalCache:
    # 初始化缓存字典，用于存储缓存数据及其存入时间
    cache = {}
    timeout = 3600 # 默认缓存超时时间为 1 小时

    def __init__(self):
        pass

    @staticmethod
    def get(key):
        # 先清理过期缓存
        BelongLocalCache.clean_expired_cache()
        """
        从本地缓存中获取数据
        :param key: 缓存的键
        :return: 缓存中的数据或新获取的数据
        """
        if key in BelongLocalCache.cache:
            data, timestamp = BelongLocalCache.cache[key]
            if  (time.time() - timestamp) < BelongLocalCache.timeout:
                # 缓存未超时，直接返回缓存的数据
                return data
            else:
                # 缓存已超时，删除缓存并返回 None
                del BelongLocalCache.cache[key]
                return None
        else:
            return None

    @staticmethod
    def set(key, value):
        # 记录当前时间作为存入时间
        timestamp = time.time()
        # 将获取的数据和存入时间存入缓存
        BelongLocalCache.cache[key] = (value, timestamp)


    @staticmethod
    def clean_expired_cache():
        """
        清理缓存中已超时的数据
        """
        current_time = time.time()
        # 找出所有超时的键
        expired_keys = []
        for key, (_, timestamp) in BelongLocalCache.cache.items():
            if (current_time - timestamp) >= BelongLocalCache.timeout:
                expired_keys.append(key)

        # 删除超时的键值对
        for key in expired_keys:
            del BelongLocalCache.cache[key]

# 使用示例
if __name__ == "__main__":
    # 初始化本地缓存实例
    local_cache = BelongLocalCache()

    data = {
        "split_fields_combined": ["ZJZH1_ZJZH2", "ZJZH3_ZJZH4"],
        "product_id": ["产品ID1", "产品ID2"]
    }
    df = pd.DataFrame(data)

    # 定义缓存键
    cache_key = "one_batch_belong_df"
    # 设置超时时间为 10 秒
    timeout = 10

    BelongLocalCache.set(cache_key, df)

    local_data = BelongLocalCache.get(cache_key)
    print(local_data)
