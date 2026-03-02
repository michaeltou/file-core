from sqlalchemy import create_engine, text


username = 'DOUMING'
password = '$tm1Alove$tm1Alove'
oracle_connection = 't7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING'


# 1. 创建引擎
engine = create_engine(
    "oracle+cx_oracle://DOUMING:$tm1Alove$tm1Alove@t7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING",
    pool_size=3,           # 连接池大小
    max_overflow=20,        # 额外可溢出连接
    echo=True               # 打印实际发出的 SQL，调试用
)

# 2. 拿到连接，执行原生 SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 FROM dual"))
    print(result.scalar())   # 输出 1