
from engine.core.migrate_core_engine import MigrateCoreEngine
import xml.etree.ElementTree as ET
import pandas as pd
import engine.util.config as config
import numpy as np

from lxml import etree


def move_xml_to_oracle_with_xpath(flow_node, file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance):
    value_path = flow_node_xml_config.get('valuePath')
    # 读取节点的xPath信息
    x_path_str = flow_node_xml_config.get('xPath')
    # 读取节点的读数类型 1：直接获取节点的text值 2：获取节点的属性值
    read_type = flow_node_xml_config.get('readType')
    filter_logic = flow_node_xml_config.get('filterLogic')
    target_interface_table = flow_node_xml_config['targetIntfTbl']

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()

    default_chunk_size = 100000
    chunk_size = config.get_config_value('xml.chunk_size', default_chunk_size)


    # 解析 XML 文件
    tree = etree.parse(file_path_and_name)
    root = tree.getroot()
    root = remove_namespaces(root)

    # 记录列表
    record_list = []
    records = root.xpath(x_path_str)
    # 索引
    index = 0
    for record in records:
        index = index + 1
        # 一条记录的字典
        record_dict = {}
        # ============================
        if read_type == 1:
            # 方式1: 直接获取节点的text值
            for field_mapping_item in field_mapping_config_list:
                source_field = field_mapping_item['sourceField']
                # 如果包含[]，则说明是上下文变量，这个时候则不要加入到构造的dataframe中.
                # 因为这里构造的dataFrame定位是：代表从原始文件中读取的数据。
                if '[' not in source_field and ']' not in source_field:
                    tag_name = source_field
                    tag_text_xpath = f'{tag_name}/text()'
                    # 获取text值
                    tag_text_value_list = record.xpath(tag_text_xpath)
                    if tag_text_value_list and len(tag_text_value_list) > 0:
                        # 可能会找到多个值，需要处理多个值
                        # 如果是一个值,则直接赋值
                        if len(tag_text_value_list) == 1:
                            tag_text_value = tag_text_value_list[0]
                            # 需要把从xml中读取的字符串，采用str转成普通字符串
                            tag_text_value = str(tag_text_value).strip()
                            record_dict[source_field.upper()] = tag_text_value
                            # 如果有多个值（>1），则需要遍历赋值即：把所有的值，用逗号分割拼接起来。
                        elif len(tag_text_value_list) > 1:
                            final_tag_name = ','.join(str(item) for item in tag_text_value_list)
                            # 赋值
                            record_dict[source_field.upper()] = final_tag_name
                    else:
                        record_dict[source_field.upper()] = None
        elif read_type == 2:
            # 方式2: 获取节点的属性值
            for field_mapping_item in field_mapping_config_list:
                source_field = field_mapping_item['sourceField']
                # 如果包含[]，则说明是上下文变量，这个时候则不要加入到构造的dataframe中.
                # 因为这里构造的dataFrame定位是：代表从原始文件中读取的数据。
                if '[' not in source_field and ']' not in source_field:
                    attr_name = source_field
                    # 获取属性值
                    attr_value = record.get(attr_name)
                    if attr_value is None:
                        attr_value = record.get(attr_name.upper())

                    # 需要把从xml中读取的字符串，采用str转成普通字符串
                    attr_value = str(attr_value).strip()
                    record_dict[source_field.upper()] = attr_value

        # 新增一个索引列，命名为INDEX，这个索引列可以做为一个序号数据使用，例如可以插入数据库
        record_dict['INDEX'] = index
        record_list.append(record_dict)
        # 分块处理xml的记录（可应对大文件）
        if index % chunk_size == 0:
            print(f'已处理{index}条记录')
            # 调用核心引擎，将dataframe数据插入数据库
            my_dataframe_one_batch = pd.DataFrame(record_list)
            my_dataframe_one_batch = my_dataframe_one_batch.replace({'None': None})

            # 调用核心引擎，将dataframe数据插入数据库
            migrate_core_engine.dataframe_to_oracle(flow_node_xml_config,
                my_dataframe_one_batch, filter_logic, target_interface_table, field_mapping_config_list, context_instance)
            # 处理完成后，重新初始化记录
            record_list = []

    if len(record_list) > 0:
        # 处理剩余记录
        my_dataframe_last_batch = pd.DataFrame(record_list)
        # 处理None值,替换为NaN值
        my_dataframe_last_batch = my_dataframe_last_batch.replace({None: np.nan})
        # 调用核心引擎，将dataframe数据插入数据库
        migrate_core_engine.dataframe_to_oracle(flow_node_xml_config,
            my_dataframe_last_batch, filter_logic, target_interface_table, field_mapping_config_list, context_instance)


# 移除命名空间
def remove_namespaces(root):
    has_nsmap = bool(root.nsmap)
    if has_nsmap:
        # 遍历所有元素
        for elem in root.getiterator():
            # 检查元素是否有命名空间前缀
            if isinstance(elem.tag, str) and '}' in elem.tag:
                # 去掉命名空间前缀
                elem.tag = elem.tag.split('}', 1)[1]
            # 处理元素的属性
            for key, value in elem.attrib.items():
                if '}' in key:
                    new_key = key.split('}', 1)[1]
                    elem.attrib[new_key] = value
                    del elem.attrib[key]
        # 移除根元素的命名空间声明
        root.attrib.clear()
        # 移除所有命名空间声明
        etree.cleanup_namespaces(root)
        return root
    else:
        return root


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

