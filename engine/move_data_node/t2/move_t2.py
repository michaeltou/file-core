from engine.move_data_node.t2.move_t2_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_t2(flow_node, flow_node_t2_config, t2_param_item_list, field_mapping_config_list, context_instance):
    # Move t2 to Oracle
    move_t2_to_oracle(flow_node, flow_node_t2_config,t2_param_item_list,
                      field_mapping_config_list, context_instance)


def my_test_interface1_7302():

    file_type = FileType.TXT.value
    file_path_and_name = "20180302BOND_VALUATION.txt"
    filter_logic = 'F1 == [BUSINESS_DATE]'
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " ",
                "processLogicType": 1,
                "sequence": 1,
                "sourceField": "F1",
                "targetField": "S1",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F2'] = df['F2'] + 'abc' ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F2",
                "targetField": "S2",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F3",
                "targetField": "S3",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "S4",
                "targetField": "S4",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " $ + 1",
                "processLogicType": 1,
                "sequence": 2,
                "sourceField": "S5",
                "targetField": "S5",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F6'] = df['F6'] + 1000 ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F6",
                "targetField": "S6",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F7'] = np.where(df['F7'] > 3, df['F7'] + 1000, df['F7']) ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F7",
                "targetField": "S7",
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
        "flowNodeTxtConfig": {
          "createTime": 20241204.152206,
          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "separator": "|",
          "skipRows": 12,
          "totalColumnCount": 12,
          "targetIntfTbl": "tjk_zzqs_bond_valuation",
          "updateTime": 20241204.152206
        }
    }

    # 执行sql，获取到数据
    my_list = [
        {'S5_KEY': 102.3789, 'S6_KEY': 3.5517},
        {'S5_KEY': 0.1, 'S6_KEY': 0.2}
    ]

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[S7]', 1)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_txt_config = flow_node['flowNodeTxtConfig']
    move_t2(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


if __name__ == '__main__':
    my_test_interface1_7302()



