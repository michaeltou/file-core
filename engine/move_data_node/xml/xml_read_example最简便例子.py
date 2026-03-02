import xml.etree.ElementTree as ET
tree = ET.parse('examples.xml')
# tree = ET.parse('./cashsecurityclosemd_20180419.xml')
root = tree.getroot()

for child in root:
    print(f'{child.tag}: {child.attrib}')
    for subchild in child:
        print(f'{subchild.tag}: {subchild.text}')