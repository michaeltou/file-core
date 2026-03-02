from lxml import etree

xml_data = '''
<root xmlns="http://example.com/default-namespace">
    <book>
        <title>Python Programming</title>
        <author>John Doe</author>
    </book>
</root>
'''

# 解析 XML 数据
root = etree.fromstring(xml_data)

# 为默认命名空间指定前缀
namespace = {'ns': 'http://example.com/default-namespace'}

# 使用指定的前缀进行 XPath 查询
books = root.xpath('//ns:book', namespaces=namespace)
for book in books:
    title = book.xpath('ns:title/text()', namespaces=namespace)[0]
    author = book.xpath('ns:author/text()', namespaces=namespace)[0]
    print(f"书名: {title}, 作者: {author}")

