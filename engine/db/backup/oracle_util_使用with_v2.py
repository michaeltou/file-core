import platform

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import oracledb
import os

class OracleConnectionPool:
    _engine = None
    _session_maker = None

    @staticmethod
    def get_engine():
        if OracleConnectionPool._engine is None:
            # 链接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
            # 这里调用后使用的是oracle的thick mode
            d = None
            if platform.system() == "Darwin":  # macOS
                d = os.environ.get("HOME") + ("/Downloads/instantclient_23_3")
            elif platform.system() == "Windows":  # Windows
                d = r"C:\oracle\instantclient_23_5"
            oracledb.init_oracle_client(lib_dir=d)

            # Oracle配置
            # 新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
            OracleConnectionPool._engine = create_engine(
                'oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                echo=True,  # 打印sql语句
                pool_size=8,  # 连接池大小
                pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                pool_timeout=30,  # 指定了从连接池中获取连接的超时时间，单位是秒。
            )
        return OracleConnectionPool._engine

    @staticmethod
    def get_session():
        if OracleConnectionPool._session_maker is None:
            OracleConnectionPool._session_maker = sessionmaker(bind=OracleConnectionPool.get_engine())
        return OracleConnectionPool._session_maker()


# 使用示例
with OracleConnectionPool.get_session() as session:
    try:
        result = session.execute(text("SELECT 1 FROM DUAL"))
        print(result.fetchone())
    except Exception as e:
        print(f"An error occurred: {e}")




