import xml.etree.ElementTree as ET


'''XPath（XML Path Language）是一种用于在 XML 文档中定位节点的语言，它在处理 XML 数据时非常有用，例如在 Python 的 xml.etree.ElementTree 模块里就可以使用 XPath 表达式来查找特定的元素。下面为你详细介绍 XPath 表达式的常见用法：
基本语法元素
1. 节点选择
/：从根节点开始选择。例如，/root 表示选择根节点下名为 root 的直接子节点。
//：在整个文档中递归查找匹配的节点。例如，//item 表示查找文档中所有名为 item 的节点，无论它们在文档中的位置如何。
2. 通配符
*：匹配任意节点。例如，/root/* 表示选择根节点下的所有直接子节点。
3. 轴（Axes）
@：用于选择属性。例如，//item[@value] 表示选择所有具有 value 属性的 item 节点。
..：选择当前节点的父节点。
4. 谓语（Predicates）
用于筛选节点。通常用方括号 [] 表示。例如，//results[@name="HISSPOTMATCH"] 表示选择所有 name 属性值为 HISSPOTMATCH 的 results 节点。'''

# 解析 XML 数据
xml_data = '''
<root>
    <results name="HISSPOTMATCH">
        <item value="1">Data 1</item>
        <item value="2">Data 2</item>
    </results>
    <results name="OTHERMATCH">
        <item value="3">Data 3</item>
    </results>
</root>
'''
root = ET.fromstring(xml_data)

# 按照标签名称和属性值查找子元素
# 查找 name 属性为 HISSPOTMATCH 的 results 元素
# target_node = root.find('.//results[@name="HISSPOTMATCH"]')
target_node = root.find('.//results')
if target_node is not None:
    print(f"找到节点: {target_node.tag}, 属性: {target_node.attrib}")
    # 进一步查找其下的 item 元素
    for item in target_node.findall('item'):
        print(f"子节点: {item.tag}, 属性: {item.attrib}, 文本内容: {item.text}")
else:
    print("未找到符合条件的节点。")
