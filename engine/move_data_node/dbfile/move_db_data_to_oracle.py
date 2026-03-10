#
#
# from engine.core.migrate_core_engine import *
# # from engine.db.oracle_sourcedb_util import execute_source_db_query_sql
# from engine.util.sql.SqlUtil import replace_sql
#
# def move_db_data_to_oracle(flow_node, source_db_id, source_exec_sql, flow_node_db_config, field_mapping_config_list, context_instance):
#     # 将dbf文件转换成dataframe
#     my_dataframe = db_data_to_dataframe(source_db_id, source_exec_sql, context_instance)
#     # 创建读数引擎
#     migrate_core_engine = MigrateCoreEngine()
#     filter_logic = flow_node_db_config.get('filterLogic')
#     target_interface_table = flow_node_db_config.get('targetIntfTbl')
#     # 调用核心引擎，将dataframe数据插入数据库
#     migrate_core_engine.dataframe_to_oracle(flow_node_db_config,
#                                             my_dataframe,
#                                             filter_logic,
#                                             target_interface_table,
#                                             field_mapping_config_list,
#                                             context_instance)
#
#
# def db_data_to_dataframe(source_db_id, source_exec_sql, context_instance):
#     start_time = time.time()
#     # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
#     params = context_instance.gen_simple_context_dict()
#
#     source_exec_sql = replace_sql(source_exec_sql, context_instance)
#     # 执行查询语句
#     data_frame_result = execute_source_db_query_sql(source_db_id,source_exec_sql, params)
#
#     end_time = time.time()
#     num_rows = data_frame_result.shape[0]
#     print('db 文件，执行sql获取数据耗时:', end_time - start_time, '秒, 记录数：', num_rows)
#     return data_frame_result
#
#
