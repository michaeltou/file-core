import os
from lxml import etree
import pandas as pd
import engine.util.log as log
from engine.split.core.split_engine import split_dataframe
import engine.util.config as config


def split_xml_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance):
    interface_id = file_split_rule.get('interfaceId')
    elect_check_xml_interface_id_list_str = config.get_config_value('split.elect_check_xml_interface_id_list')
    elect_check_xml_interface_id_list = elect_check_xml_interface_id_list_str.split(',')
    # xml 文件格式千奇百怪（不像dbf，txt等文件有固定规律可以进行抽象），目前只碰到一个xml接口，所以这里按照接口ID来区分，进行定制化拆分。
    if interface_id in elect_check_xml_interface_id_list:
        file_path_and_name = file_path_and_name_dto.get('filePathAndName')
        if file_path_and_name is None or not os.path.exists(file_path_and_name):
            log.error(f"文件 {file_path_and_name} 不存在。")
            return

        # 解析 XML 文件
        tree = etree.parse(file_path_and_name)
        root = tree.getroot()

        # 获取result节点
        records = root.xpath('//result')
        # 构造result字典，key为name属性值，value为节点属性
        result_dict = {item.attrib.get('name'): item.attrib for item in records}

        context_instance.set('result_dict', result_dict)
        # 构造 DataFrame
        data = []
        # 节点xpath语法, 选择要从xml中读取的节点
        records = root.xpath('//*[@CLIENTID]')
        for item in records:
            client_id = item.attrib.get('CLIENTID')
            tag_name = item.tag
            attrib_str = str(item.attrib)
            data.append([client_id, tag_name, attrib_str])

        xml_whole_df = pd.DataFrame(data, columns=['CLIENTID', 'tag_name', 'attrib_str'])
        split_dataframe(xml_whole_df, file_path_and_name_dto, file_split_rule, context_instance)



