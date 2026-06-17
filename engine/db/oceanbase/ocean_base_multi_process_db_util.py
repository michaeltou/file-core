
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pandas as pd
import numpy as np

import engine.util.config as config
import urllib.parse



class OceanBaseMultiProcessDbUtil:

    @staticmethod
    def get_one_process_engine():

        # 1. 配置参数
        username = config.get_config_value("read_tool.oceanbase.username")
        password = config.get_config_value("read_tool.oceanbase.password")
        host = config.get_config_value("read_tool.oceanbase.host")
        port = config.get_config_value("read_tool.oceanbase.port")
        database = config.get_config_value("read_tool.oceanbase.database")

        # 2. 转义密码特殊字符
        username = urllib.parse.quote_plus(username)
        #print('用户名是:'+username)
        password = urllib.parse.quote_plus(password)

        # 3. 拼接 URL（service_name = 集群.租户.数据库）
        CONN_URL = (
            f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
        )

        ocean_base_pool_size = 1 #config.get_config_value("read_tool.oceanbase.pool_size")

        one_process_engine = create_engine(
            CONN_URL,
            pool_size=ocean_base_pool_size, # 连接池大小
            echo=False  # 打印实际发出的 SQL，调试用
        )

        return one_process_engine

    @staticmethod
    def get_one_process_engine_for_multi_app(app):
        if app == 'file_gz':
            # 1. 配置参数
            username = config.get_config_value("read_tool.oceanbase.app.file_gz.username")
            password = config.get_config_value("read_tool.oceanbase.app.file_gz.password")
            host = config.get_config_value("read_tool.oceanbase.app.file_gz.host")
            port = config.get_config_value("read_tool.oceanbase.app.file_gz.port")
            database = config.get_config_value("read_tool.oceanbase.app.file_gz.database")
        elif app == 'file_tzzj':
            # 1. 配置参数
            username = config.get_config_value("read_tool.oceanbase.app.file_tzzj.username")
            password = config.get_config_value("read_tool.oceanbase.app.file_tzzj.password")
            host = config.get_config_value("read_tool.oceanbase.app.file_tzzj.host")
            port = config.get_config_value("read_tool.oceanbase.app.file_tzzj.port")
            database = config.get_config_value("read_tool.oceanbase.app.file_tzzj.database")
        elif app == 'file_rzqs':
            # 1. 配置参数
            username = config.get_config_value("read_tool.oceanbase.app.file_rzqs.username")
            password = config.get_config_value("read_tool.oceanbase.app.file_rzqs.password")
            host = config.get_config_value("read_tool.oceanbase.app.file_rzqs.host")
            port = config.get_config_value("read_tool.oceanbase.app.file_rzqs.port")
            database = config.get_config_value("read_tool.oceanbase.app.file_rzqs.database")
        else:
            # 1. 配置参数
            username = config.get_config_value("read_tool.oceanbase.username")
            password = config.get_config_value("read_tool.oceanbase.password")
            host = config.get_config_value("read_tool.oceanbase.host")
            port = config.get_config_value("read_tool.oceanbase.port")
            database = config.get_config_value("read_tool.oceanbase.database")


        # 2. 转义密码特殊字符
        username = urllib.parse.quote_plus(username)
        # print('用户名是:'+username)
        password = urllib.parse.quote_plus(password)

        # 3. 拼接 URL（service_name = 集群.租户.数据库）
        CONN_URL = (
            f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
        )

        ocean_base_pool_size = 1  # config.get_config_value("read_tool.oceanbase.pool_size")

        one_process_engine = create_engine(
            CONN_URL,
            pool_size=ocean_base_pool_size,  # 连接池大小
            echo=False  # 打印实际发出的 SQL，调试用
        )

        return one_process_engine



