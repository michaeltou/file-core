from lxml import etree

# 解析 XML 文件
tree = etree.parse('books.xml')
root = tree.getroot()

# 1. 选择所有 book 节点
books = root.xpath('//book')
print("所有书籍节点：")
for book in books:
    title = book.xpath('title/text()')[0]
    attr_name = 'lang'
    attr_value = book.get(attr_name)
    print(f"  - {title}")

# 2. 选择特定属性的节点：选择 category 为 fiction 的 book 节点
fiction_books = root.xpath('//book[@category="fiction"]')
print("\n类别为 fiction 的书籍：")
for book in fiction_books:
    title = book.xpath('title/text()')[0]
    print(f"  - {title}")

# 3. 选择具有特定属性值范围的节点：选择价格大于 12 的书籍
expensive_books = root.xpath('//book[price > 12]')
print("\n价格大于 12 的书籍：")
for book in expensive_books:
    title = book.xpath('title/text()')[0]
    price = book.xpath('price/text()')[0]
    print(f"  - {title} (价格: {price})")

# 4. 选择特定位置的节点：选择第一个 book 节点
first_book = root.xpath('//book[1]')
if first_book:
    title = first_book[0].xpath('title/text()')[0]
    print(f"\n第一本书籍：{title}")

# 5. 选择节点的属性值：选择所有 book 节点的 id 属性值
book_ids = root.xpath('//book/@id')
print("\n所有书籍的 ID：")
for book_id in book_ids:
    print(f"  - {book_id}")

# 6. 选择父节点：选择 title 为 'To Kill a Mockingbird' 的 book 节点
target_book = root.xpath('//title[text()="To Kill a Mockingbird"]/..')
if target_book:
    author = target_book[0].xpath('author/text()')[0]
    print(f"\n《To Kill a Mockingbird》的作者是：{author}")

