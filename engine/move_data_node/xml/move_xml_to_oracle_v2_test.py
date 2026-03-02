
from engine.core.migrate_core_engine import MigrateCoreEngine
import xml.etree.ElementTree as ET
import pandas as pd
import engine.util.config as config
import re

def get_xml_list_data(file_path_and_name, flow_node_xml_config):
    value_path = flow_node_xml_config['valuePath']

    # xml数据抽取类型
    xml_extract_type = flow_node_xml_config.get('extract_type')

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


# 举例: attribute_text = 'results[name="HISSPOTMATCH"]'
# 从中获取属性值 HISSPOTMATCH
def get_attribute_value(attribute_text):
    # 定义正则表达式模式
    pattern = r'name="([^"]+)"'
    # 查找匹配项
    match = re.search(pattern, attribute_text)
    if match:
        result = match.group(1)
    else:
        result = None
    return result

# 举例: attribute_text = 'results[name="HISSPOTMATCH"]'
# 从中获取属性名称 name
def get_attribute_value(attribute_text):
    # 定义正则表达式模式
    pattern = r'\[(\w+)="'
    # 查找匹配项
    match = re.search(pattern, attribute_text)
    if match:
        result = match.group(1)
    else:
        result = None
    return result


# value_path包含属性的例子: results[name="HISSPOTMATCH"]/BTag[desc="abc"]
def get_record_list_parent_node_by_path_and_attr(root, value_path):
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

