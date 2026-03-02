import pandas as pd
from engine.util.redis.redis_util import RedisUtil
import json
# ... existing code ...

# 定义 Redis 键名
redis_key = "one_batch_belong_df_cache"

# 从 Redis 中获取 JSON 字符串
df_json = RedisUtil.get_string(redis_key)

if df_json is not None:
    # 解析 JSON 字符串为 Python 对象
    df_dict = json.loads(df_json)
    # 使用解析后的字典创建 DataFrame
    one_batch_belong_df = pd.DataFrame(df_dict['data'], index=df_dict['index'], columns=df_dict['columns'])
    print(one_batch_belong_df)
else:
    print("Redis 中没有找到对应的缓存数据")

# ... existing code ...