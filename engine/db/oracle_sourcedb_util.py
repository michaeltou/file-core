#
# from engine.db.oracle_read_tool_db_util import *
# from engine.db.SourceDb import SourceDb
#
#
# class OracleSourceDbConnectionPool:
#     """
#     Oracle 连接池，
#     1：可以获取engine和session（单例模式），
#     2：也可以使用execute_query_sql和execute_dml_sql方法执行SQL语句
#     """
#     _engine = {}
#     _session_maker = {}
#     _source_db_list = {}
#     _source_db_connection_url_list = {}
#
#     @staticmethod
#     def get_engine(source_db_id):
#         if OracleSourceDbConnectionPool._engine.get(source_db_id) is None:
#             # 连接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
#             # 这里调用后使用的是oracle的thick mode
#             d = None
#             if platform.system() == "Darwin":  # macOS
#                 d = os.environ.get("HOME") + ("/Downloads/instantclient_23_3")
#             elif platform.system() == "Windows":  # Windows
#                 d = r"C:\oracle\instantclient_23_5"
#             oracledb.init_oracle_client(lib_dir=d)
#
#             db_connection_url = ""
#             if source_db_id not in OracleSourceDbConnectionPool._source_db_list:
#                 session = OracleConnectionPool.get_session()
#                 current_source_db = session.query(SourceDb).filter(SourceDb.db_id == source_db_id).one()
#                 if current_source_db is None:
#                     raise Exception("来源数据库不存在")
#                 else:
#                     OracleSourceDbConnectionPool._source_db_list[source_db_id] = current_source_db
#                     db_connection_url = current_source_db.generate_connection_url()
#                     OracleSourceDbConnectionPool._source_db_connection_url_list[source_db_id] = db_connection_url
#
#             else:
#                 db_connection_url = OracleSourceDbConnectionPool._source_db_connection_url_list[source_db_id]
#
#
#             # Oracle配置
#             # 新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
#             OracleSourceDbConnectionPool._engine[source_db_id] = create_engine(
#                 # 'oracle+oracledb://hs_fam_jx:hs_fam_jx@10.20.28.61:1521/orcl',
#                 # 'oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
#                 db_connection_url,
#                 # echo=True,  # 打印sql语句
#                 pool_size=8,  # 连接池大小
#                 pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
#                 pool_timeout=30,  # 指定了从连接池中获取连接的超时时间，单位是秒。
#             )
#         return OracleSourceDbConnectionPool._engine[source_db_id]
#
#     @staticmethod
#     def get_session(source_db_id):
#         if OracleSourceDbConnectionPool._session_maker.get(source_db_id) is None:
#             OracleSourceDbConnectionPool._session_maker[source_db_id] = sessionmaker(bind=OracleSourceDbConnectionPool.get_engine(source_db_id))
#         return OracleSourceDbConnectionPool._session_maker[source_db_id]()
#
#
# def execute_source_db_query_sql(source_db_id, sql, params=None):
#     """
#     :param source_db_id:
#     :param sql:
#     :param params:
#     :return:
#     """"""
#     执行SQL查询语句，返回结果集
#     :param sql: 执行的SQL语句
#     :param params: 字典类型的参数
#     :return:  返回DataFrame
#
#     # 定义SQL查询语句，使用占位符 :param_name
#     sql = "SELECT * FROM my_table WHERE column_name = :param_name"
#
#     # 定义参数字典
#     params = {"param_name": "value"}
#
#     # 执行SQL查询，并传递参数
#     result = session.execute(txt(sql), params)
#     """
#     with OracleSourceDbConnectionPool.get_session(source_db_id) as session:
#         result = session.execute(text(sql), params)
#         column_names = result.keys()
#         column_names = [item.upper() for item in column_names]
#         all_data = result.fetchall()
#         df = pd.DataFrame(all_data, columns=column_names)
#         return df
#
#
# def convert_int64_to_int_for_source_db(params):
#     processed_params = {}
#     for key, value in params.items():
#         if isinstance(value, np.int64):
#             processed_params[key] = int(value)
#         else:
#             processed_params[key] = value
#     return processed_params
#
#
# def execute_source_db_dml_sql(source_db_id, sql, params=None):
#     with OracleSourceDbConnectionPool.get_session(source_db_id) as session:
#         try:
#             processed_params = convert_int64_to_int_for_source_db(params)
#             session.execute(text(sql), processed_params)
#             session.commit()
#         except Exception as e:
#             session.rollback()
#             raise e
#
#
# def test_source_db_query_sql(source_db_id):
#     sql = "select * from TM_TEST_TABLE where name = :NAME"
#     params = {"NAME": "Tom", "key2": "value2"}
#     df = execute_source_db_query_sql(source_db_id, sql, params)
#     print(df)
#
#
# def test_source_db_dml_sql(source_db_id):
#     sql = "insert into TM_TEST_TABLE(name,age) values(:name,:age)"
#     params = {"name": "douming", "age": 39}
#     execute_source_db_dml_sql(source_db_id, sql, params)
#
#
# if __name__ == '__main__':
#     test_source_db_dml_sql('oracledb1')
#     test_source_db_query_sql('oracledb1')
#
#
