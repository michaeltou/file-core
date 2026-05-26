from engine.move_data_node.json.move_json_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_json(flow_node, json_data_str, flow_node_json_config, field_mapping_config_list, context_instance):
    # Move DBF file to Oracle
    move_json_to_oracle(flow_node, json_data_str, flow_node_json_config, field_mapping_config_list, context_instance)





