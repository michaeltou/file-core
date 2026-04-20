import pandas as pd
from sqlalchemy import create_engine

import urllib.parse

# 1. 配置参数
username = ''
password = ''
host = ''
port = 2881
database = ''

# 2. 转义密码特殊字符
username = urllib.parse.quote_plus(username)
print('用户名是:'+username)
password = urllib.parse.quote_plus(password)

# 3. 拼接 URL（service_name = 集群.租户.数据库）
CONN_URL = (
    f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
)


ocean_base_pool_size = 3



my_engine = create_engine(
    CONN_URL,
    pool_size=ocean_base_pool_size, # 连接池大小
    max_overflow=20,  # 额外可溢出连接
    echo=False  # 打印实际发出的 SQL，调试用
)


df = pd.DataFrame({
    "id":   [1, 2, 3],
    "name": ["Alice", "Bob", "Cathy"],
    "age":  [25, 30, 28],
    "create_time": pd.to_datetime(["2024-01-01 12:00:00.123456", "2024-01-02 13:30:00.654321", "2024-01-03 14:45:00.987654"])
    # 或使用当前时间：pd.Timestamp.now() 重复 3 次
})


df.to_sql(
    name="demo_person",
    con=my_engine,
    if_exists="append",   # 首次跑建表，后续可改 append
    index=False,
    chunksize=1000         # 批量提交行数，默认 1000
)

print("写入完成！共写入", len(df), "条数据。")