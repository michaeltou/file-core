import xml.etree.ElementTree as ET
from engine.core.context import Context
from engine.cnst.BuildType import BuildType
from lxml import etree


def build_context_from_xml(flow_node, context_instance):
    xml_file = context_instance.get('[FILE_PATH_AND_NAME]')

    # 解析 XML 文件
    tree = etree.parse(xml_file)
    root = tree.getroot()
    root =remove_namespaces(root)

    flow_node_context_item_list = flow_node['flowNodeContextItemList']
    # for flow_context_item in flow_node_context_item_list:
    #     param_key = flow_context_item['contextKey']
    #     value_path = flow_context_item['contextValue']
    #     # 根据路径value_path获取节点的值
    #     value = get_node_value_by_path(root, value_path)
    #     # 将值设置到上下文实例中
    #     context_instance.set('['+param_key+']', value)
    #     print(f'路径{value_path}找到了值:{value}')

    for flow_context_item in flow_node_context_item_list:
        param_key = flow_context_item['contextKey'].upper()
        x_path_str = flow_context_item['contextValue']
        # 根据路径x_path获取节点的值
        value = get_node_value_by_x_path(root, x_path_str)
        # 将值设置到上下文实例中
        context_instance.set('['+param_key+']', value)



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

def get_node_namespace(node):
    # 如果节点的tag中有'}’字符，则说明该节点有命名空间，返回命名空间的字符串；
    # 否则，返回None
    if node.tag.find('}') != -1:
        return node.tag.split('}')[0][1:]
    else:
        return None


def get_node_value_by_x_path(root, x_path_str):
    # 节点xpath语法, 选择要从xml中读取的节点
    # records = root.xpath('/root/book[1]/title[1]/text()')
    # records = root.xpath('/root/book/title/text()')
    # records = root.xpath('/root/book/@category')
    values = root.xpath(x_path_str)
    if len(values) == 0:
        return None
    else:
        first_value = values[0]
        return first_value

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


def test_xml_extract():
    flow_node = {
        "flowNodeBContextConfig": {
            "interfaceId": "rule1_id",
            "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
            "nodeName": "node1_name",
            "nodeSeqNo": 0,
            "nodeType": 4,
            # 2表示XML_EXTRACT
            "buildType": BuildType.XML_EXTRACT.value,
            # 执行sql语句
            "executeSql": '',
            "contextParamType": 1,
            "createTime": 20241204.152206,
            "updateTime": 20241204.152206
        },
        "flowNodeContextItemList": [
            {
                "contextKey": "name",
                "contextValue": 'level1/level2/name'
            },
            {
                "contextKey": "age",
                "contextValue": 'level1/level2/age'
            },
            {
                "contextKey": "gender",
                "contextValue": 'level1/level2/gender'
            },
            {
                "contextKey": "education",
                "contextValue": 'level1/level2/education'
            }
        ]
    }

    file_path_and_name = "test-抽取valuePath上下文.xml"

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    context_instance.set('[FILE_PATH_AND_NAME]', file_path_and_name)

    build_context_from_xml(flow_node, context_instance)
    print(context_instance)


if __name__ == '__main__':
    test_xml_extract()