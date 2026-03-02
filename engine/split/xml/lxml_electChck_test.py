from lxml import etree
import pandas as pd


# 解析 XML 文件
tree = etree.parse('82911103_20180420_ElectCheck.xml')
root = tree.getroot()

# 获取result节点
records = root.xpath('//result')
# 构造result字典，key为name属性值，value为节点属性
result_dict = {item.attrib.get('name'): item.attrib for item in records}


# 构造 DataFrame
data = []
# 节点xpath语法, 选择要从xml中读取的节点
records = root.xpath('//*[@CLIENTID]')
for item in records:
    client_id = item.attrib.get('CLIENTID')
    tag_name = item.tag
    attrib_str = str(item.attrib)
    data.append([client_id, tag_name, attrib_str])

df = pd.DataFrame(data, columns=['CLIENTID', 'tag_name', 'attrib_str'])
print(df)

result_name = 'CLIENTMISFEE'
query_condition = f'tag_name == "{result_name}"'

new_df = df.query(query_condition)
print(new_df)



