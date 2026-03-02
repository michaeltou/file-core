import time
from ratelimit import limits, sleep_and_retry, RateLimitException

# 限制函数每分钟最多调用 3 次
CALLS = 3
PERIOD = 6


# @sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def api_call():
    print("Making an API call...")
    return True


for _ in range(100):
    try:
        time.sleep(1)
        api_call()

    except RateLimitException as e:
        print("发生了限流异常")