from engine.move_data_node.txt.move_txt_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType

"""
# txt映射示例如下：

指定分隔符 ，例如 "|" 或者 ","，或者其它字符

 来源字段： 
   如果来源字段在文件中
        1 无表头的场景，来源字段可以直接使用目标字段，例如 "S3","VC_CODE"；
        2 有表头的场景，来源字段可以使用表头的字段
   如果来源字段不在文件中
        如果来源字段不在文件中，是上下文变量，则使用 [变量名]，例如 [BUSINESS_DATE]，[FUND_ID]
 
 
 目标字段：填入数据库的字段名称，例如 "S3","VC_CODE"
 
 
"""


def my_test1():
    file_type = FileType.TXT.value
    file_path_and_name = "/Users/douming/Documents/读数工具重构/文件/20180302BOND_VALUATION.txt"
    filter_logic = 'S1 == [BUSINESS_DATE]'
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
                "sourceField": "S1",
                "targetField": "S1",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['S2'] = df['S2'] + 1 ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "S2",
                "targetField": "S2",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "S3",
                "targetField": "S3",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
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
                "processLogic": "  ",
                "processLogicType": None,
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
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "S6",
                "targetField": "S6",
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
    move_txt(file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


def my_test_2_inteface_id_1025():
    file_type = FileType.TXT.value
    file_path_and_name = "/Users/douming/Documents/读数工具重构/文件/国君文件/20240905行情/51001009052.ETF"
    filter_logic = 'VC_SZ.notnull() '
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 1,
                "sourceField": "vc_code",
                "targetField": "vc_code",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "vc_sz",
                "targetField": "vc_sz",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_BH]",
                "targetField": "l_bh",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_LB]",
                "targetField": "l_lb",
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
                "targetField": "l_ztbh",
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
                "targetField": "d_ywrq",
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
          "separator": "=",
          "skipRows": None,
          "targetIntfTbl": "tjk_jyqs_h_shetfqd",
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
    context_instance.set('[L_BH]', 123)
    context_instance.set('[L_LB]', 456)

    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[S7]', 1)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_txt_config = flow_node['flowNodeTxtConfig']
    move_txt(file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


if __name__ == '__main__':
    my_test_2_inteface_id_1025()


