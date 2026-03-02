import pandas as pd
from engine.util.redis.redis_util import RedisUtil

# ... existing code ...

# 假设 one_batch_belong_df 是你要缓存的 DataFrame
one_batch_belong_df = pd.DataFrame({
    "split_fields_combined": ["ZJZH1_ZJZH2", "ZJZH3_ZJZH4"],
    "product_id": ["产品ID1", "产品ID2"]
})

# 定义 Redis 键名
redis_key = "one_batch_belong_df_cache"

# 将 DataFrame 转换为 JSON 字符串
df_json = one_batch_belong_df.to_json(orient='split')

# 存储到 Redis 中，设置缓存时间为 1 小时
RedisUtil.set_string(redis_key, df_json, 60 * 60 * 1)

# ... existing code ...