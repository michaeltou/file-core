import pandas as pd
from sqlalchemy import create_engine
import psycopg2

from sqlalchemy.dialects.postgresql.base import PGDialect
PGDialect._get_server_version_info = lambda *args: (9, 2)

# 创建一个DataFrame
data = {'Name': ['Tom', 'Jack', 'Steve', 'Ricky'],
        'Age': [28, 34, 29, 42]}
df = pd.DataFrame(data)



# 创建数据库引擎
# engine = create_engine('postgresql+psycopg2://test:hshome_123@10.20.191.106:30100/fa6')
engine = create_engine('postgresql://test:hshome_123@10.20.191.106:30100/fa6')
# 将DataFrame写入高斯数据库
df.to_sql('tm_test_table_v1', con=engine, if_exists='replace', index=False)
