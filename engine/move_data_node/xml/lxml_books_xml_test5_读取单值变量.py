from lxml import etree

# 解析 XML 文件
tree = etree.parse('books.xml')
root = tree.getroot()



# 节点xpath语法, 选择要从xml中读取的节点
# records = root.xpath('/root/book[1]/title[1]/text()')
records = root.xpath('/root/book/title/text()')
records = root.xpath('/root/book/@category')

for item in records:
    print(item)

