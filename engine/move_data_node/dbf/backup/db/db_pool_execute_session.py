import pandas as pd
import time
from sqlalchemy import create_engine
from dbfreaddm import DBF

from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import   text

table = DBF('/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf', encoding='gbk')

# 连接池大小被设置为 10，获取连接的超时时间为 30 秒。
oracle_engine = create_engine('oracle+oracledb://fam_dev_65:fam_dev_65@10.20.146.67:1521/orcl',poolclass=QueuePool, pool_size=10, pool_timeout=30)

Session = sessionmaker(bind=oracle_engine)
session = Session()

# 在这里使用连接进行数据库操作
result = session.execute(text("SELECT * FROM dbf_2_oracle_table"))
count = 0
for row in result:
    if count == 10:
        break
    print(row)
    count = count + 1


session.close()


