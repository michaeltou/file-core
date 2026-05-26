import pandas as pd

from engine.core.migrate_core_engine import *
import uuid
import os
import json


def move_json_to_oracle(flow_node, json_data_str, flow_node_json_config, field_mapping_config_list, context_instance):

    flow_node_rename_config_list = flow_node.get('fileJsonRenameRuleDTOList')


    json_data_frame = json_to_dataframe(context_instance,json_data_str, flow_node_rename_config_list)

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_json_config.get('filterLogic')
    target_interface_table = flow_node_json_config['targetIntfTbl']

    CleanEngine.process_clean_before_import(flow_node_json_config, context_instance)

    # 调用核心引擎，将dataframe数据插入数据库
    migrate_core_engine.dataframe_to_oracle(flow_node_json_config,
                                            json_data_frame,
                                            filter_logic,
                                            target_interface_table,
                                            field_mapping_config_list,
                                            context_instance)




def json_to_dataframe(context_instance, json_data_str,flow_node_rename_config_list):
    source_name_list = []
    target_name_list = []
    source_and_target_name_dict = {}
    my_uuid = context_instance.get('[UUID]')

    for flow_node_rename_config in flow_node_rename_config_list:
        source_name = flow_node_rename_config.get('sourceName')
        target_name = flow_node_rename_config.get('targetName')
        source_name_list.append(source_name)
        target_name_list.append(target_name)
        source_and_target_name_dict[source_name] = target_name

    json_data = json.loads(json_data_str)
    # 判断是否是list类型，如果不是list，则转换为list类型
    if not isinstance(json_data, list):
        json_data = [json_data]


    # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况

    json_df = pd.DataFrame(json_data)

    # 重命名列
    json_df.rename(columns=source_and_target_name_dict, inplace=True)

    return json_df



# 根据json串生成dataframe
def test_json_to_dataframe():
    single_json_str = '{"name": "张三", "age": 25, "city": "北京"}'
    # 示例2：多个一级JSON对象数组
    array_json_str = '[{"name": "张三", "age": 25}, {"name": "李四", "age": 30}, {"name": "王五", "age": 35}]'

    # 解析JSON字符串为Python列表
    data = json.loads(single_json_str)
    #判断是否是list类型，如果不是list，则转换为list类型
    if not isinstance(data, list):
        data = [data]


    # 生成DataFrame
    df2 = pd.DataFrame(data)
    print("JSON数组生成的DataFrame:")
    print(df2)
    print()

if __name__ == '__main__':
     test_json_to_dataframe()