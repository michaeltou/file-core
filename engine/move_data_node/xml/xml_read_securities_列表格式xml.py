import xml.etree.ElementTree as ET
import pandas as pd


tree = ET.parse('cashsecurityclosemd_20180419.xml')
root = tree.getroot()
print(f'根节点标签:{root.tag},根节点属性:{root.attrib},根节点文本:{root.text}')



record_list = []


for record in root:
    record_dict = {}
    print(f'------------------一行记录，行标签:{record.tag}，行属性：{record.attrib},行内容：{record.text} -----------------')
    for item in record:
        print(f'字段标签：{item.tag}, 字段属性：{item.attrib}, 字段内容: {item.text}')
        record_dict[item.tag] = item.text
    record_list.append(record_dict)
df = pd.DataFrame(record_list)
print(df)