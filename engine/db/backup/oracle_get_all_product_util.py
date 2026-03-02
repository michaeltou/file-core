import platform

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import oracledb
import os
import pandas as pd
import numpy as np

import engine.util.config as config

# 这个类已经废弃不再使用了。
# @deprecated
class OracleGetAllProductConnectionPool:
    """
    Oracle 连接池，
    1：可以获取engine和session（单例模式），
    2：也可以使用execute_query_sql和execute_dml_sql方法执行SQL语句
    """
    _engine = None
    _session_maker = None

    @staticmethod
    def get_engine():
        if OracleGetAllProductConnectionPool._engine is None:
            # Oracle配置
            # 新包官网说明： https://oracle.github.io/python-oracledb/
            # step1: oracledb安装：https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
            # step2:在linux上，如果使用thick模式（11g数据库使用thick模式，12c+数据库使用thin模式），需要安装好oracle客户端（下载地址:https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html），
            # 并设置环境变量(例如：export LD_LIBRARY_PATH=/root/software/instantclient_21_16:$LD_LIBRARY_PATH)
            oracle_mode = config.get_config_value("split.get_all_product_db.mode")
            connect_url = config.get_config_value("split.get_all_product_db.connect_url")

            if oracle_mode == "thin":
                pass
            elif oracle_mode == "thick":
                # 连接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
                # 这里调用后使用的是oracle的thick mode
                d = None  # On Linux, no directory should be passed
                if platform.system() == "Darwin":  # macOS
                    d = os.environ.get("HOME") + ("/Downloads/instantclient_23_3")
                elif platform.system() == "Windows":  # Windows
                    d = r"C:\oracle\instantclient_23_5"

                # oracledb 初始化：https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#initialization
                oracledb.init_oracle_client(lib_dir=d)

            OracleGetAllProductConnectionPool._engine = create_engine(
                # 'oracle+oracledb://hs_fam_jx:hs_fam_jx@10.20.28.61:1521/orcl',
                # 'oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                connect_url,
                # echo=True,  # 打印sql语句
                pool_size=8,  # 连接池大小
                pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                pool_timeout=30,  # 指定了从连接池中获取连接的超时时间，单位是秒。
            )
        return OracleGetAllProductConnectionPool._engine

    @staticmethod
    def get_session():
        if OracleGetAllProductConnectionPool._session_maker is None:
            OracleGetAllProductConnectionPool._session_maker = sessionmaker(bind=OracleGetAllProductConnectionPool.get_engine())
        return OracleGetAllProductConnectionPool._session_maker()


def execute_get_all_product_query_sql(sql, params=None):
    """ 
    :param sql: 
    :param params: 
    :return: 
    """"""
    执行SQL查询语句，返回结果集
    :param sql: 执行的SQL语句
    :param params: 字典类型的参数
    :return:  返回DataFrame
    
    # 定义SQL查询语句，使用占位符 :param_name
    sql = "SELECT * FROM my_table WHERE column_name = :param_name"
    
    # 定义参数字典
    params = {"param_name": "value"}
    
    # 执行SQL查询，并传递参数
    result = session.execute(txt(sql), params)
    """
    with OracleGetAllProductConnectionPool.get_session() as session:
        result = session.execute(text(sql), params)
        column_names = result.keys()
        column_names = [item.upper() for item in column_names]
        all_data = result.fetchall()
        df = pd.DataFrame(all_data, columns=column_names)
        return df


def convert_int64_to_int(params):
    processed_params = {}
    for key, value in params.items():
        if isinstance(value, np.int64):
            processed_params[key] = int(value)
        else:
            processed_params[key] = value
    return processed_params


def execute_get_all_product_dml_sql(sql, params=None):
    with OracleGetAllProductConnectionPool.get_session() as session:
        try:
            processed_params = convert_int64_to_int(params)
            session.execute(text(sql), processed_params)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e


def test_query_sql():
    sql = "select pkg_pubfun.pkgsf_pubfun_getgycs(123,'JCSZ_JKSJDQFS') sjdqfs ,:key1 as key1,:key2 as key2 from dual"
    params = {"key1": "value1", "key2": "value2"}
    df = execute_get_all_product_query_sql(sql, params)
    print(df)


def test_dml_sql():
    sql = "insert into my_test_table(name,age) values(:name,:age)"
    params = {"name": "douming", "age": 39}
    execute_get_all_product_dml_sql(sql, params)

if __name__ == '__main__':
    test_query_sql()


