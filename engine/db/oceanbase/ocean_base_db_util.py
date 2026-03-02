
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pandas as pd
import numpy as np

import engine.util.config as config



class OceanBaseDbUtil:
    """
    Oracle 连接池，
    1：可以获取engine和session（单例模式），
    2：也可以使用execute_query_sql和execute_dml_sql方法执行SQL语句
    """
    _engine = None
    _session_maker = None

    @staticmethod
    def get_engine():
        if OceanBaseDbUtil._engine is None:
            ocean_base_connect_url = config.get_config_value("read_tool.oceanbase.connect_url")
            ocean_base_pool_size = config.get_config_value("read_tool.oceanbase.pool_size")
            OceanBaseDbUtil._engine = create_engine(
                ocean_base_connect_url,
                pool_size=ocean_base_pool_size, # 连接池大小
                max_overflow=20,  # 额外可溢出连接
                echo=False  # 打印实际发出的 SQL，调试用
            )

        return OceanBaseDbUtil._engine

    @staticmethod
    def get_session():
        if OceanBaseDbUtil._session_maker is None:
            OceanBaseDbUtil._session_maker = sessionmaker(bind=OceanBaseDbUtil.get_engine())
        return OceanBaseDbUtil._session_maker()

    @staticmethod
    def execute_dml_sql(sql, params=None):
        with OceanBaseDbUtil.get_session() as session:
            try:
                processed_params = convert_int64_to_int(params)
                session.execute(text(sql), processed_params)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def execute_query_sql(sql, params=None):
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
        with OceanBaseDbUtil.get_session() as session:
            result = session.execute(text(sql), params)
            column_names = result.keys()
            column_names = [item.upper() for item in column_names]
            all_data = result.fetchall()
            df = pd.DataFrame(all_data, columns=column_names)
            return df

def execute_auto_query_sql(sql, params=None):
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
    with OceanBaseDbUtil.get_session() as session:
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


def execute_auto_get_all_product_dml_sql(sql, params=None):
    with OceanBaseDbUtil.get_session() as session:
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
    df = execute_auto_query_sql(sql, params)
    print(df)


def test_dml_sql():
    sql = "insert into my_test_table(name,age) values(:name,:age)"
    params = {"name": "douming", "age": 39}
    execute_auto_get_all_product_dml_sql(sql, params)

if __name__ == '__main__':
    test_query_sql()


