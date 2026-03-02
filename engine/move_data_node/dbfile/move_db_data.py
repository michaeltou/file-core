from engine.move_data_node.dbfile.move_db_data_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_db_data(flow_node, source_db_id, source_exec_sql, flow_node_db_config, field_mapping_config_list, context_instance):
    # 把数据从源数据库移动到目标Oracle数据库
    move_db_data_to_oracle(flow_node, source_db_id, source_exec_sql, flow_node_db_config, field_mapping_config_list, context_instance)


def my_test():
    file_type = FileType.DB.value
    file_path_and_name = None
    flow_node = {
        'fieldMappingConfigList': [
            {
                "sourceField": "name",
                "targetField": "name"
            },
            {
                "sourceField": "age",
                "targetField": "age"
            }
        ],
        'flowNodeDbConfig': {
            'targetIntfTbl': 'MY_TEST_TABLE',
            'sourceDbId': 'test_db',
            'sourceExecSql': 'select * from MY_TEST_TABLE where name = :NAME'
        }
    }
    context_instance = Context()
    context_instance.set('[NAME]', 'Tom')
    context_instance.set('[age]', '18')

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_db_config = flow_node['flowNodeDbConfig']
    source_db_id = flow_node_db_config['sourceDbId']
    source_exec_sql = flow_node_db_config['sourceExecSql']
    move_db_data(flow_node, source_db_id, source_exec_sql, flow_node_db_config, field_mapping_config_list, context_instance)

if __name__ == '__main__':
    my_test()