
from engine.core.context import Context
from engine.cnst.BuildType import BuildType


def build_context_from_constant(flow_node, context_instance):

    flow_node_context_item_list = flow_node.get('flowNodeContextItemList')
    if not flow_node_context_item_list:
        return
    for flow_node_context_item in flow_node_context_item_list:
        context_key = flow_node_context_item.get('contextKey')
        context_value = flow_node_context_item.get('contextValue')
        # 构建类型为常量设置，则直接设置上下文
        context_instance.set('['+context_key+']', context_value)


def test_constant_set_build_context():
    flow_node = {
        "flowNodeBContextConfig": {
            "interfaceId": "rule1_id",
            "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
            "nodeName": "node1_name",
            "nodeSeqNo": 0,
            "nodeType": 4,
            # 构建类型
            "buildType": BuildType.CONSTANT_SET.value,
            # 执行sql语句
            "executeSql": '',
            "contextParamType": 1,
            "createTime": 20241204.152206,
            "updateTime": 20241204.152206
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "ID",
                "contextValue": '123'
            },
            {
                "contextKey": "NAME",
                "contextValue": 'michael'
            }

        ]
    }


    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)

    build_context_from_constant(flow_node, context_instance)
    print(context_instance)


if __name__ == '__main__':
    test_constant_set_build_context()