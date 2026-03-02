from lxml import etree

# 解析 XML 文件
tree = etree.parse('books.xml')
root = tree.getroot()

# 1. 选择所有 book 节点

# 节点xpath语法, 选择要从xml中读取的节点
records = root.xpath('//book')
for item in records:
    tag_name = 'title'
    tag_text_xpath = f'{tag_name}/text()'
    # 获取text值
    tag_text_value = item.xpath(tag_text_xpath)[0]
    attr_name = 'category'
    # 获取属性值
    attr_value = item.get(attr_name)
    print(f"  - 标签text值{tag_name}={tag_text_value}, 属性值{attr_name}={attr_value}")

