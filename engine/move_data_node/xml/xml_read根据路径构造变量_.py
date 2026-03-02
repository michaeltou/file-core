import xml.etree.ElementTree as ET
import pandas as pd


def get_node_namespace(node):
    # 如果节点的tag中有'}’字符，则说明该节点有命名空间，返回命名空间的字符串；
    # 否则，返回None
    if node.tag.find('}') != -1:
        return node.tag.split('}')[0][1:]
    else:
        return None


def get_node_value_by_path(root, value_path):
    # 获取命名空间
    namespace = get_node_namespace(root)
    # print('命名空间是:', namespace)

    # 将value_path分割成路径片段
    path_segments = value_path.split('/')

    # 从根节点开始遍历路径
    node = root
    for segment in path_segments:
        if namespace is None:
            node = node.find(segment)
        else:
            # 查找具有指定标签的子节点
            node = node.find(f'{{{namespace}}}{segment}')
        if node is None:
            # 如果找不到节点，返回None
            return None

    # 返回找到的节点的值
    return node.text

my_dict = {
            'contextKey': "[NAME]",
            'valuePath': "level1/level2/name",
            'contextValue': None
           }

# 使用示例
# xml_file = 'pcf.intf_id1107.xml'
xml_file = 'test1-带有命名空间文件.xml'

value_path_name = 'level1/level2/name'
value_path_age = 'level1/level2/age'
value_path_gender = 'level1/level2/gender'
value_path_education = 'level1/level2/education'

value_path_list = [value_path_name, value_path_age, value_path_gender, value_path_education]

tree = ET.parse(xml_file)
root = tree.getroot()

for value_path in value_path_list:
    value = get_node_value_by_path(root, value_path)
    print(f'路径{value_path}找到了值:{value}')

