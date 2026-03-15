
from sqlalchemy import create_engine, text, Integer, String, Float
from sqlalchemy.orm import sessionmaker

import pandas as pd
import numpy as np

import engine.util.config as config
import urllib.parse



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
            # 1. 配置参数
            username = "Y7PHFUND_REALTIME@UAT_GZ01#UAT_Cluster05"
            password = "aaAA11##2025"
            host = "uatobc05.phfund.com.cn"
            port = 2883
            database = "Y7PHFUND_REALTIME"  # 数据库名


            # 2. 转义密码特殊字符
            username = urllib.parse.quote_plus(username)
            print('用户名是:'+username)
            password = urllib.parse.quote_plus(password)

            # 3. 拼接 URL（service_name = 集群.租户.数据库）
            CONN_URL = (
                f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
            )

            MY_URL="oracle+cx_oracle://Y7PHFUND_REALTIME%40UAT_GZ01%23UAT_Cluster05:aaAA11%23%232025@uatobc05.phfund.com.cn:2883/Y7PHFUND_REALTIME"

            OceanBaseDbUtil._engine = create_engine(
                MY_URL,
                pool_size=3, # 连接池大小
                max_overflow=20,  # 额外可溢出连接
                echo=False  # 打印实际发出的 SQL，调试用
            )

        return OceanBaseDbUtil._engine

if __name__ == '__main__':

    # 构造一个dataframe测试护具

    target_df = pd.DataFrame({
        'ID': [1, 2, 3],
        'NAME': ['Alice', 'Bob', 'Charlie'],
        'AGE': [25, 30, 35]
    })

    # dataframe写入数据库
    dtype_dict = {}
    for column in target_df.columns:
        if target_df[column].dtype in ['int', 'int64']:
            dtype_dict[column] = Integer
        elif target_df[column].dtype in ['object', 'bool']:
            dtype_dict[column] = String(2000)
        elif target_df[column].dtype in ['float', 'float64']:
            dtype_dict[column] = Float
        else:
            pass

    target_df.to_sql("target_interface_table",
                     con=OceanBaseDbUtil.get_engine(),
                     if_exists='append',
                     dtype=dtype_dict,
                     index=False, chunksize=100)






