
from engine.db.oceanbase.ocean_base_db_util import OceanBaseDbUtil


from engine.util.sql.SqlUtil import replace_sql


class CleanEngine:
    def __init__(self):
        pass

    @staticmethod
    def process_clean_before_import(flow_node_config, context_instance):
        exec_sql = flow_node_config.get('cleanSql')
        if exec_sql is None or len(exec_sql) == 0:
            return
        # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
        params = context_instance.gen_simple_context_dict()
        sql = replace_sql(exec_sql, context_instance)

        app = context_instance.get('[APP]')
        OceanBaseDbUtil.execute_dml_sql_for_app(app, sql, params)



    @staticmethod
    def execute_end_sql_after_import(flow_node_config, context_instance):
        app = context_instance.get('[APP]')
        exec_sql = flow_node_config.get('execSql')
        if exec_sql is None or len(exec_sql) == 0:
            return
        sql_list = exec_sql.split(';')
        for sql in sql_list:
            sql = sql.strip()
            if sql == '':
                continue
            # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
            params = context_instance.gen_simple_context_dict()
            sql = replace_sql(sql, context_instance)
            OceanBaseDbUtil.execute_dml_sql_for_app(app, sql, params)


def test_sql_split():
    my_sql=";sql1;"
    # 按分号分隔
    sql_list = my_sql.split(';')
    print(sql_list)
    for sql in sql_list:
        if sql == '':
            continue
        print(sql)


if __name__ == '__main__':
    test_sql_split();