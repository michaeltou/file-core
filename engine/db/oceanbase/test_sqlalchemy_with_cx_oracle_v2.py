from typing import Optional
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, text

def sql_to_df(engine: Engine,
              sql: str,
              params: Optional[dict] = None,
              index_col: Optional[str] = None) -> pd.DataFrame:
    """
    通用查询 -> DataFrame
    :param engine: 已创建好的 SQLAlchemy Engine
    :param sql:    原生 SQL 字符串，可含命名占位符 :param
    :param params: 命名参数 dict，如 {":k": v}
    :param index_col: 设为行索引的列名，可选
    :return:       pandas.DataFrame
    """
    # 使用 pandas 自带的 read_sql，底层走 sqlalchemy
    # 如果 sql 里含参数，直接传 params 即可
    df = pd.read_sql(sql, con=engine, params=params, index_col=index_col)
    return df

# 1. 创建引擎
engine = create_engine(
    "oracle+cx_oracle://DOUMING:$tm1Alove$tm1Alove@t7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING",
    pool_size=3,           # 连接池大小
    max_overflow=20,        # 额外可溢出连接
    echo=True               # 打印实际发出的 SQL，调试用
)

df = sql_to_df(engine, "SELECT * FROM  TESTT_CHAR")
print(df.head())