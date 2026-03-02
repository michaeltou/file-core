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


print('---------------------------------new -----下面需要手动提交或者回滚------------------------------')
with oracle_engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM dbf_2_oracle_table"))
    # connection.commit()  # commits "some statement"
    # connection.rollback()  # rolls back "some other statement"
    count = 0
    for row in result:
        if count == 10:
            break
        print(row)
        count = count + 1

print('---------------------------------new -----下面可自动提交-------------------------')
with oracle_engine.begin() as connection:
    result = connection.execute(text("SELECT * FROM dbf_2_oracle_table"))
    count = 0
    for row in result:
        if count == 10:
            break
        print(row)
        count = count + 1