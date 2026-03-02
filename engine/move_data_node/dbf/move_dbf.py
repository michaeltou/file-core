from engine.move_data_node.dbf.move_dbf_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_dbf(flow_node, file_path_and_name, flow_node_dbf_config, field_mapping_config_list, context_instance):
    # Move DBF file to Oracle
    move_dbf_to_oracle(flow_node, file_path_and_name, flow_node_dbf_config, field_mapping_config_list, context_instance)


def my_test():
    file_type = FileType.DBF.value
    file_path_and_name = "backup4/nqhq.dbf"
    filter_logic = 'HQZRSP >= [[MY_LIST.HQZRSP]] & HQJRKP >= [[MY_LIST.HQJRKP]] & HQCJJE == [HQCJJE]'
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "$ + 2 ",
                "processLogicType": 1,
                "sequence": 1,
                "sourceField": "HQJRKP",
                "targetField": "HQJRKP",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['HQZRSP'] = df['HQZRSP'] + 1 ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "HQZRSP",
                "targetField": "HQZRSP",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 3,
                "sourceField": "[FUND_ID]",
                "targetField": "L_ZTBH",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 3,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "[BUSINESS_DATE]",
                "targetField": "D_YWRQ",
                "updateTime": 20241204.152207
            }
        ],
        "flowNodeDbfConfig": {
          "createTime": 20241204.152206,
          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "targetIntfTbl": "tjk_gzqs_nqhq",
          "updateTime": 20241204.152206
        }
    }



    # 执行sql，获取到数据
    my_list = [
        {'HQZRSP': 2.09, 'HQJRKP': 2.09},
        {'HQZRSP': 0.1, 'HQJRKP': 0.2}
    ]

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20241211)
    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[HQCJJE]', 12331)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_dbf_config = flow_node['flowNodeDbfConfig']

    move_dbf(flow_node, file_path_and_name, flow_node_dbf_config, field_mapping_config_list, context_instance)


if __name__ == '__main__':
    my_test()