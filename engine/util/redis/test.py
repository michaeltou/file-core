from engine.util.redis.redis_util import RedisUtil

# RedisUtil.set_string("test_key1", "test_value1",60*60)
# RedisUtil.set_string("test_key1", "test_value1",1)
print(RedisUtil.get_string("test_key1"))

