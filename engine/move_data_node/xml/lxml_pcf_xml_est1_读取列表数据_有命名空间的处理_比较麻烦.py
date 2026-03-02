from lxml import etree




get_data_type = 1
source_field = 'UnderlyingSecurityID'
# get_data_type = 2
# source_field = 'UnderlyingSecurityID'

# 解析 XML 文件
tree = etree.parse('pcf.intf_id1107.xml')
root = tree.getroot()


namespace_prefix = 'ns'

# 获取命名空间映射
namespace_map = root.nsmap
new_nsmap = {}
for prefix, uri in namespace_map.items():
    if prefix is None:
        print(f"默认命名空间: {uri}")
        namespace_prefix = 'ns'
        new_nsmap[namespace_prefix] = uri
    else:
        print(f"前缀: {prefix}, 命名空间 URI: {uri}")
        namespace_prefix = prefix
        new_nsmap[namespace_prefix] = uri



# 节点xpath语法, 选择要从xml中读取的节点
records = root.xpath(f'//{namespace_prefix}:Component', namespaces=new_nsmap)
for item in records:
    if get_data_type == 1:
        # 方式1: 直接获取节点的text值
        tag_name = source_field
        tag_text_xpath = f'{namespace_prefix}:{tag_name}/text()'
        # 获取text值
        tag_text_value = item.xpath(tag_text_xpath, namespaces=new_nsmap)[0]
        print(f"标签text值:{tag_name}={tag_text_value}")
    elif get_data_type == 2:
        # 方式2: 获取节点的属性值
        attr_name = source_field
        # 获取属性值
        attr_value = item.get(attr_name)
        print(f"属性值:{attr_name}={attr_value}")


