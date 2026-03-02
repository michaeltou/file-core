import pandas as pd
from sqlalchemy import create_engine

# 1. 创建引擎
engine = create_engine(
    "oracle+cx_oracle://DOUMING:$tm1Alove$tm1Alove@t7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING",
    pool_size=3,           # 连接池大小
    max_overflow=20,        # 额外可溢出连接
    echo=True               # 打印实际发出的 SQL，调试用
)

# 2. 造一个示例 DataFrame
df = pd.DataFrame({
    "id":   [1, 2, 3],
    "name": ["Alice", "Bob", "Cathy"],
    "age":  [25, 30, 28]
})

# 3. 写入数据库
#    参数说明：
#    - name：目标表名，大小写不敏感 Oracle 会转成大写
#    - con：SQLAlchemy Engine
#    - if_exists='replace' 表示表若已存在则先删后建；可改成 'append' 追加
#    - index=False 不把 DataFrame 的行索引写进去
#    - dtype 可选，指定字段类型；不指定则由 SQLAlchemy 自动推断
df.to_sql(
    name="demo_person",
    con=engine,
    if_exists="append",   # 首次跑建表，后续可改 append
    index=False,
    chunksize=1000         # 批量提交行数，默认 1000
)

print("写入完成！共写入", len(df), "条数据。")