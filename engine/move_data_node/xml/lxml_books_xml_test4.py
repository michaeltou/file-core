from lxml import etree

# 解析 XML 文件
tree = etree.parse('books.xml')
root = tree.getroot()

# get_data_type = 1
# source_field = 'title'
get_data_type = 2
source_field = 'category'


# 节点xpath语法, 选择要从xml中读取的节点
records = root.xpath('/root/book')
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
        if attr_value is None:
            attr_value = item.get(attr_name.upper())
        print(f"属性值:{attr_name}={attr_value}")

