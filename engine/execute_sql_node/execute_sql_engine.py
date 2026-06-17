from engine.db.oracle_read_tool_db_util import *
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql

from engine.clean.clean_engine import CleanEngine


def execute_node_sql(flow_node, context_instance):
    # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
    params = context_instance.gen_simple_context_dict()

    flow_node_sql_config = flow_node['flowNodeSqlConfig']
    sql = flow_node_sql_config['executeSql']
    sql = replace_sql(sql, context_instance)
    # sql_type = flow_node_sql_config['sqlType']
    # context_param_type = flow_node_sql_config['contextParamType']
    #execute_dml_sql(sql, params)




def test_execute_node_sql_with_simple_context_param():
    flow_node = {
        "flowNodeSqlConfig": {
            "executeSql": "SELECT * FROM MY_TEST_TABLE WHERE name = :NAME AND age = :AGE",
            "sqlType": 1,
            "contextParamType": 1
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "name",

            },
            {
                "contextKey": "age",

            }
        ]
    }
    context_instance = Context()
    context_instance.set('[NAME]', 'Tom')
    context_instance.set('[AGE]', 25)

    execute_node_sql(flow_node, context_instance)
    return context_instance


def test_execute_node_sql_with_collection_context_param():
    flow_node = {
        "flowNodeSqlConfig": {
            "executeSql": "SELECT * FROM MY_TEST_TABLE WHERE name = :NAME AND age = :AGE",
            "sqlType": 1,
            "contextParamType": 2
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "mylist",

            }
        ]
    }
    context_instance = Context()
    context_instance.set('[NAME]', 'Tom')
    context_instance.set('[AGE]', 25)

    execute_node_sql(flow_node, context_instance)
    return context_instance


def test_insert_node_sql():
    flow_node = {
        "flowNodeSqlConfig": {
            "executeSql": "insert into MY_TEST_TABLE(name, age) values(:NAME ,:AGE )",
            "sqlType": 2,
            "contextParamType": 1
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "mylist",

            }
        ]
    }
    context_instance = Context()
    context_instance.set('[NAME]', 'Tom2')
    context_instance.set('[AGE]', 252)

    execute_node_sql(flow_node, context_instance)
    return context_instance





if __name__ == '__main__':
    # context_instance_result = test_execute_node_sql_with_simple_context_param()
    # print(context_instance_result)
    # context_instance_result = test_execute_node_sql_with_collection_context_param()
    # print(context_instance_result)
    test_insert_node_sql()


