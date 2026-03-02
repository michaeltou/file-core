from engine.core.migrate_core_engine import *
import requests
import engine.util.config as config


def move_t2_to_oracle(flow_node, flow_node_t2_config, t2_param_item_list,
                      field_mapping_config_list, context_instance):
    # 将txt文件转换成dataframe
    t2_data_frame = t2_to_dataframe(flow_node_t2_config, t2_param_item_list,context_instance)

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_t2_config.get('filterLogic')
    target_interface_table = flow_node_t2_config['targetIntfTbl']

    # 调用核心引擎，将dataframe数据插入数据库
    migrate_core_engine.dataframe_to_oracle(flow_node_t2_config,
                                            t2_data_frame, filter_logic,
                                            target_interface_table,
                                            field_mapping_config_list,
                                            context_instance)


def t2_to_dataframe(flow_node_t2_config, t2_param_item_list, context_instance):
    t2_request = {'t2_param_item_list': t2_param_item_list, 'flow_node_t2_config': flow_node_t2_config,
                  'context_instance': context_instance.gen_original_context_dict()}

    # url = 'http://10.188.138.24:26666/api/t2/invoke'
    url = config.get_config_value('read_tool.t2.invoke.url')

    # 发起POST请求
    response = requests.post(url, json=t2_request)

    # 检查请求是否成功
    if response.status_code == 200:
        # response.json()为:
        # {'msg':'操作成功',
        #  'code': 200,
        #  'data': {'[{'name': '张三', 'id': 1, 'age': 20}, {'name': '李四', 'id': 2, 'age': 25}]
        # }
        json_data = response.json()
        if json_data['code'] == 200:
            t2_data_frame = pd.DataFrame(json_data['data'])
            # 转换列名为大写
            t2_data_frame.columns = t2_data_frame.columns.str.upper()
            return t2_data_frame
        else:
            # 抛出异常
            raise Exception('请求失败，错误信息：'+json_data['msg'])
    else:
        raise Exception(f'请求失败，状态码：{response.status_code}, 错误信息：{response.text}')


if __name__ == '__main__':
    pass