
from engine.split.dbf.split_dbf_engine import split_dbf_file
from engine.split.txt.split_txt_engine import split_txt_file
from engine.split.xml.split_xml_engine import split_xml_file


def split_file(rule_id, file_split_rule, file_path_and_name_dto,  context_instance):
    # 文件类型 文件类型,比如:TXT,DBF,XML等字符串
    file_type = file_split_rule.get('fileType')
    if file_type == 'DBF':
        split_dbf_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance)
    elif file_type == 'TXT':
        split_txt_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance)
    elif file_type == 'XML':
        split_xml_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance)
    else:
        raise Exception('不支持的文件类型')

