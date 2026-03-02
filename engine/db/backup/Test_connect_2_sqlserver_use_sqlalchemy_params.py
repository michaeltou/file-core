
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd


db_connection_url = "mssql+pymssql://douming:$tm1Atest@rm-bp1y3r8130mcj6k80vo.sqlserver.rds.aliyuncs.com:3433/testdb"


engine = create_engine(
                # 'oracle+oracledb://hs_fam_jx:hs_fam_jx@10.20.28.61:1521/orcl',
                # 'oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                db_connection_url,
                echo=True,  # 打印sql语句
                pool_size=8,  # 连接池大小
                pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                pool_timeout=30,  # 指定了从连接池中获取连接的超时时间，单位是秒。
            )


session_maker = sessionmaker(bind=engine)


# sql = "SELECT  * FROM [db_owner].[tm_test_table];"
sql = "SELECT  * FROM db_owner.tm_test_table where name = :name ;"
params = {
    'name': 'Tom'
}

with session_maker() as session:
    result = session.execute(text(sql), params)
    column_names = result.keys()
    column_names = [item.upper() for item in column_names]
    all_data = result.fetchall()
    df = pd.DataFrame(all_data, columns=column_names)
    print(df)



