from lxml import etree



get_data_type = 1
source_field = 'UnderlyingSecurityID'
# get_data_type = 2
# source_field = 'UnderlyingSecurityID'

# 解析 XML 文件
tree = etree.parse('pcf.intf_id1107.xml')
root = tree.getroot()


# 定义移除命名空间的函数
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
        #移除所有命名空间声明
        etree.cleanup_namespaces(root)
        return root
    else:
        return root

# 调用函数移除命名空间
root = remove_namespaces(root)


# 节点xpath语法, 选择要从xml中读取的节点
records = root.xpath('//Component')
for item in records:
    if get_data_type == 1:
        # 方式1: 直接获取节点的text值
        tag_name = source_field
        tag_text_xpath = f'{tag_name}/text()'
        # 获取text值
        tag_text_value = item.xpath(tag_text_xpath)[0]
        print(f"标签text值:{tag_name}={tag_text_value}")
    elif get_data_type == 2:
        # 方式2: 获取节点的属性值
        attr_name = source_field
        # 获取属性值
        attr_value = item.get(attr_name)
        print(f"属性值:{attr_name}={attr_value}")


