
from engine.core.migrate_core_engine import MigrateCoreEngine
import xml.etree.ElementTree as ET
import pandas as pd
import engine.util.config as config


def move_xml_to_oracle(flow_node, file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance):
    value_path = flow_node_xml_config['valuePath']
    filter_logic = flow_node_xml_config.get('filterLogic')
    target_interface_table = flow_node_xml_config['targetIntfTbl']
    # xml数据抽取类型
    xml_extract_type = flow_node_xml_config.get('extract_type')
    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()

    default_chunk_size = 100000
    chunk_size = config.get_config_value('xml.chunk_size', default_chunk_size)

    tree = ET.parse(file_path_and_name)
    root = tree.getroot()
    # 记录列表
    record_list = []
    record_parent_node = get_record_list_parent_node_by_path(root, value_path)
    index = 0
    for record in record_parent_node:
        index = index + 1
        # 一条记录的字典
        record_dict = {}
        for item in record:
            # print(f'字段标签：{item.tag}, 字段属性：{item.attrib}, 字段内容: {item.text}')
            # 当节点带有命名空间时 ，item.tag = '{http://ts.szse.cn/Fund}RedemptionCashSubstitute'，需要将命名空间去掉
            # 这里去除命名空间，转为RedemptionCashSubstitute
            item_pure_tag = remove_namespace_from_tag(item.tag)
            # 将字段名称转成大写
            item_pure_tag = item_pure_tag.upper()
            record_dict[item_pure_tag] = item.text
        # 新增一个索引列，命名为INDEX，这个索引列可以做为一个序号数据使用，例如可以插入数据库
        record_dict['INDEX'] = index
        record_list.append(record_dict)
        # 分块处理xml的记录（可应对大文件）
        if index % chunk_size == 0:
            print(f'已处理{index}条记录')
            # 调用核心引擎，将dataframe数据插入数据库
            my_dataframe_one_batch = pd.DataFrame(record_list)

            # 调用核心引擎，将dataframe数据插入数据库
            migrate_core_engine.dataframe_to_oracle(flow_node_xml_config,
                my_dataframe_one_batch, filter_logic, target_interface_table, field_mapping_config_list, context_instance)
            # 处理完成后，重新初始化记录
            record_list = []

    if len(record_list) > 0:
        # 处理剩余记录
        my_dataframe_last_batch = pd.DataFrame(record_list)
        # 调用核心引擎，将dataframe数据插入数据库
        migrate_core_engine.dataframe_to_oracle(flow_node_xml_config,
            my_dataframe_last_batch, filter_logic, target_interface_table, field_mapping_config_list, context_instance)


def remove_namespace_from_tag(tag):
    # 如果tag中有'}’字符，则说明该节点有命名空间，返回命名空间的字符串；
    # 否则，返回None
    if '}' in tag:
        return tag.split('}', 1)[1]
    else:
        return tag


def get_node_namespace(node):
    # 如果节点的tag中有'}’字符，则说明该节点有命名空间，返回命名空间的字符串；
    # 否则，返回None
    if node.tag.find('}') != -1:
        return node.tag.split('}')[0][1:]
    else:
        return None


def get_record_list_parent_node_by_path(root, value_path):
    # 获取命名空间
    namespace = get_node_namespace(root)
    # print('命名空间是:', namespace)

    if value_path is None or value_path == '':
        # 如果value_path为空，则返回根节点
        return root

    # 将value_path分割成路径片段 value_path例子: Components/Component
    path_segments = value_path.split('/')

    # 从根节点开始遍历路径
    node = root
    for segment in path_segments:
        # 如果路径片段为空，则跳出循环
        if segment is None or segment == '':
            break
        if namespace is None:
            node = node.find(segment)
        else:
            # 查找具有指定标签的子节点
            node = node.find(f'{{{namespace}}}{segment}')
        if node is None:
            # 如果找不到节点，返回None
            return None

    # 返回记录列表的父节点
    return node

