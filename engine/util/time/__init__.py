from datetime import datetime


def get_local_millisecond_timestamp():
    # 获取当前时间
    current_time = datetime.now()
    # 将当前时间转换为本地时间
    local_time = current_time.astimezone()
    # 将本地时间转换为时间戳（秒）
    timestamp_seconds = local_time.timestamp()
    # 将时间戳转换为毫秒
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    return timestamp_milliseconds


if __name__ == '__main__':
    # 获取本地时间的毫秒时间戳
    local_millisecond_timestamp = get_local_millisecond_timestamp()
    print("本地时间的毫秒时间戳:", local_millisecond_timestamp)
