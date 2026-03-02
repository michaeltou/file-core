
import time
import os
import platform

from simpledbfdm import Dbf5
import pandas as pd

import oracledb
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float


def move_dbf_to_oracle(file_path_and_name, flow_node_dbf_config):
    # 将dbf文件转换成dataframe
    my_dataframe = dbf_to_dataframe(file_path_and_name, flow_node_dbf_config)
    # 将dataframe转换成oracle表
    dataframe_to_oracle(my_dataframe)


def dbf_to_dataframe(file_path_and_name, flow_node_dbf_config):
    start_time = time.time()
    dbf = Dbf5(file_path_and_name, codec='gbk')

    df = dbf.to_dataframe()
    end_time = time.time()

    # 获取字段名称
    field_names = df.columns
    # print("字段名称:", field_names)
    # 将Index对象转换成列表
    index_list = field_names.tolist()
    print("字段名称:", index_list)

    # 获取字段类型（通过查看DataFrame的数据类型推断DBF文件的字段类型）
    # field_types = df.dtypes
    # print("字段类型:", field_types)
    # dtype_map = df.dtypes.to_dict()
    # print("字段类型:", dtype_map)
    # for key, value in dtype_map.items():
    #     print(key, value)

    print('python 加载dbf文件耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)
    return df


def dataframe_to_oracle(df):
    #
    # # 链接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
    # # 这里调用后使用的是oracle的thick mode

    d = None  # On Linux, no directory should be passed
    if platform.system() == "Darwin":  # macOS
        d = os.environ.get("HOME") + ("/Downloads/instantclient_23_3")
    elif platform.system() == "Windows":  # Windows
        d = r"C:\oracle\instantclient_23_5"
    oracledb.init_oracle_client(lib_dir=d)

    # Oracle配置
    # 新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
    # oracle_engine = create_engine('oracle+oracledb://hs_fam_jx:hs_fam_jx@10.20.28.61:1521/orcl',
    #                               # echo=True,  # 打印sql语句
    #                               pool_size=8,  # 连接池大小
    #                               pool_recycle=60 * 30  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
    #                               )

    oracle_engine = create_engine('oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                                  # echo=True,  # 打印sql语句
                                  pool_size=8,  # 连接池大小
                                  pool_recycle=60 * 30  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                                  )



    dtype_dict = {}
    for column in df.columns:
        if df[column].dtype in ['float', 'float64']:
            dtype_dict[column] = Float
        elif df[column].dtype in ['int', 'int64']:
            dtype_dict[column] = Integer
        elif df[column].dtype in ['object']:
            dtype_dict[column] = String(512)
        else:
            dtype_dict[column] = String(256)
    start_time = time.time()

    ## 将dataFrame数据插入数据库
    df.to_sql('dbf_2_oracle_table_1m', con=oracle_engine, if_exists='append',
              dtype=dtype_dict,
              index=False, chunksize=1000)

    end_time = time.time()
    execution_time = end_time - start_time

    print("插入数据库总耗时：", execution_time, '秒,记录数:', len(df))

