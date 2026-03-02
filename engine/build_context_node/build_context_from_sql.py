from engine.cnst.BuildType import BuildType
from engine.db.oracle_read_tool_db_util import *
from engine.cnst.ContextParamType import ContextParamType
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql

def build_context_from_sql(flow_node, context_instance):
    # 上下文是个map，里面包含了所有变量和参数，刚好可以传给sql语句
    params = context_instance.gen_simple_context_dict()

    flow_node_build_context_config = flow_node['flowNodeBContextConfig']
    sql = flow_node_build_context_config['executeSql']
    sql = replace_sql(sql, context_instance)

    context_param_type = flow_node_build_context_config['contextParamType']

    flow_node_context_item_list = flow_node.get('flowNodeContextItemList')
    if not flow_node_context_item_list:
        return

    context_param_key_names = []
    if flow_node_context_item_list:
        # 获取上下文变量的变量名列表
        context_param_key_names = [item['contextKey'].upper() for item in flow_node_context_item_list]

    # 没有上下文变量，不设置结果
    if len(context_param_key_names) == 0:
        return

    # 执行查询语句
    data_frame_result = execute_query_sql(sql, params)
    if context_param_type == ContextParamType.SIMPLE.value:
        if len(data_frame_result) > 1:
            raise Exception('查询结果超过1行，无法设置上下文变量')
        elif len(data_frame_result) == 0:
            # 没有查询到结果，不设置上下文变量
            raise Exception('执行sql节点，没有查询到结果')
        else:  # 只有一条记录情况下，将结果设置到上下文变量中
            sql_returned_column_names = data_frame_result.columns
            sql_returned_column_names = [column.upper() for column in sql_returned_column_names]
            # 遍历查询到的结果的每一列名
            for sql_returned_column_name in sql_returned_column_names:
                # 如果sql查询到的列名在上下文变量中，则将结果设置到上下文变量中
                if sql_returned_column_name in context_param_key_names:
                    value = data_frame_result[sql_returned_column_name][0]
                    if isinstance(value,  pd.Timestamp):
                        value = value.strftime('%Y%m%d')
                    # 变量名称格式化为"[变量名]",带有方括号
                    # 例如：变量名为"name"，则格式化为"[NAME]"
                    context_instance.set('[' + sql_returned_column_name + ']', value)
    elif context_param_type == ContextParamType.COLLECTION.value:
        # 设置变量校验 start
        if len(context_param_key_names) > 1:  # 多变量的情况，说明配置错误，上下文变量类型为结果集类型时，只能有一个变量名
            raise Exception('上下文变量类型为结果集类型时，只能设置一个上下文变量')
        # 设置变量校验 end

        if len(data_frame_result) == 0:
            raise Exception('执行sql节点，没有查询到结果,至少要查询到一条记录')
        elif len(data_frame_result) >= 1:  # 至少要查询到一条记录
            # 将dataframe转换为list,这个list的元素是字典，即构造一个字典列表
            data_list = data_frame_result.to_dict(orient='records')
            context_instance.set('[[' + context_param_key_names[0] + ']]', data_list)


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
    with OracleConnectionPool.get_session() as session:
        result = session.execute(text(sql), params)
        column_names = result.keys()
        column_names = [item.upper() for item in column_names]
        all_data = result.fetchall()
        df = pd.DataFrame(all_data, columns=column_names)
        return df


def test_sql_simple_context():
    flow_node = {
        "flowNodeBContextConfig": {


            "interfaceId": "rule1_id",
            "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
            "nodeName": "node1_name",
            "nodeSeqNo": 0,
            "nodeType": 4,
            # 构建类型
            "buildType": BuildType.QUERY_SQL.value,
            # 执行sql语句
            "executeSql": "select * from (SELECT * FROM MY_TEST_TABLE WHERE name = :NAME AND age = :AGE ) WHERE ROWNUM = 1",
            "contextParamType": ContextParamType.SIMPLE.value,


            "createTime": 20241204.152206,
            "updateTime": 20241204.152206
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

    file_path_and_name = "test-抽取valuePath上下文.xml"

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    context_instance.set('[NAME]', 'Tom')
    context_instance.set('[AGE]', 25)

    build_context_from_sql(flow_node, context_instance)
    print(context_instance)



def test_sql_collection_context():
    flow_node = {
        "flowNodeBContextConfig": {
            "interfaceId": "rule1_id",
            "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
            "nodeName": "node1_name",
            "nodeSeqNo": 0,
            "nodeType": 4,
            # 构建类型
            "buildType": BuildType.QUERY_SQL.value,
            # 执行sql语句
            "executeSql": "SELECT * FROM MY_TEST_TABLE WHERE name = :NAME AND age = :AGE ",
            "contextParamType": ContextParamType.COLLECTION.value,


            "createTime": 20241204.152206,
            "updateTime": 20241204.152206
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "mylist",

            }
        ]
    }

    file_path_and_name = "test-抽取valuePath上下文.xml"

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    context_instance.set('[NAME]', 'Tom')
    context_instance.set('[AGE]', 25)

    build_context_from_sql(flow_node, context_instance)
    print(context_instance)



if __name__ == '__main__':
    test_sql_simple_context()
    test_sql_collection_context()


