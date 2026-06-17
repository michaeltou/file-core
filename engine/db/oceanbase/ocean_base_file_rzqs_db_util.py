
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pandas as pd
import numpy as np

import engine.util.config as config
import urllib.parse
from engine.util.sql.SqlUtil import replace_sql


class OceanBaseFileRzqsDbUtil:
    """
    Oracle 连接池，
    1：可以获取engine和session（单例模式），
    2：也可以使用execute_query_sql和execute_dml_sql方法执行SQL语句
    """
    _engine = None
    _session_maker = None

    @staticmethod
    def get_engine():
        if OceanBaseFileRzqsDbUtil._engine is None:
            # 1. 配置参数
            username = config.get_config_value("read_tool.oceanbase.app.file_rzqs.username")
            password = config.get_config_value("read_tool.oceanbase.app.file_rzqs.password")
            host = config.get_config_value("read_tool.oceanbase.app.file_rzqs.host")
            port = config.get_config_value("read_tool.oceanbase.app.file_rzqs.port")
            database = config.get_config_value("read_tool.oceanbase.app.file_rzqs.database")

            # 2. 转义密码特殊字符
            username = urllib.parse.quote_plus(username)
            print('用户名是:'+username)
            password = urllib.parse.quote_plus(password)

            # 3. 拼接 URL（service_name = 集群.租户.数据库）
            CONN_URL = (
                f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
            )


            ocean_base_pool_size = config.get_config_value("read_tool.oceanbase.app.file_rzqs.pool_size")



            OceanBaseFileRzqsDbUtil._engine = create_engine(
                CONN_URL,
                pool_size=ocean_base_pool_size, # 连接池大小
                max_overflow=20,  # 额外可溢出连接
                pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                pool_timeout=30,  # 指定了从连接池中获取连接的超时时间，单位是秒。
                echo=False  # 打印实际发出的 SQL，调试用
            )

        return OceanBaseFileRzqsDbUtil._engine

    @staticmethod
    def get_session():
        if OceanBaseFileRzqsDbUtil._session_maker is None:
            OceanBaseFileRzqsDbUtil._session_maker = sessionmaker(bind=OceanBaseFileRzqsDbUtil.get_engine())
        return OceanBaseFileRzqsDbUtil._session_maker()

    @staticmethod
    def execute_dml_sql(sql, params=None):
        with OceanBaseFileRzqsDbUtil.get_session() as session:
            try:
                processed_params = convert_int64_to_int(params)
                session.execute(text(sql), processed_params)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def execute_dml_sql_by_context_instance(exec_sql, context_instance):
        if exec_sql is None or len(exec_sql) == 0:
            return
        # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
        params = context_instance.gen_simple_context_dict()
        sql = replace_sql(exec_sql, context_instance)
        OceanBaseFileRzqsDbUtil.execute_dml_sql(sql, params)

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
        with OceanBaseFileRzqsDbUtil.get_session() as session:
            result = session.execute(text(sql), params)
            column_names = result.keys()
            column_names = [item.upper() for item in column_names]
            all_data = result.fetchall()
            df = pd.DataFrame(all_data, columns=column_names)
            return df

    @staticmethod
    def execute_query_sql_by_context_instance(exec_sql, context_instance):
        if exec_sql is None or len(exec_sql) == 0:
            return
        # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
        params = context_instance.gen_simple_context_dict()
        sql = replace_sql(exec_sql, context_instance)
        df = execute_auto_query_sql(sql, params)
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
    with OceanBaseFileRzqsDbUtil.get_session() as session:
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
    with OceanBaseFileRzqsDbUtil.get_session() as session:
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


