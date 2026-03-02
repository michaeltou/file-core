from engine.cnst.FileType import FileType
from engine.move_data_node.dbf.move_dbf import move_dbf
from engine.move_data_node.dbfile.move_db_data import move_db_data
from engine.move_data_node.txt.move_txt import move_txt
from engine.move_data_node.xml.move_xml import move_xml
from engine.move_data_node.excel.move_excel import move_excel
from engine.move_data_node.csv.move_csv import move_csv
from engine.move_data_node.t2.move_t2 import move_t2


def move_data(file_type, file_path_and_name, flow_node, context_instance):
    # 字段映射配置列表
    field_mapping_config_list = flow_node.get('fileFieldMappingDTOList')
    # 实现方式，page：页面配置  script：脚本实现
    implement_type = flow_node.get('rdMode')
    if implement_type == 'PAGE':
        if file_type == FileType.DBF.value:
            # dbf文件节点配置
            flow_node_dbf_config = flow_node['fileDbfParseRuleDTO']
            # 调用dbf文件节点的move_dbf方法
            move_dbf(flow_node, file_path_and_name, flow_node_dbf_config,field_mapping_config_list, context_instance)
        elif file_type == FileType.TXT.value:
            flow_node_txt_config = flow_node['fileTxtParseRuleDTO']
            move_txt(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)
        elif file_type == FileType.XML.value:
            pass
            #flow_node_xml_config = flow_node['flowNodeXmlConfig']
            #move_xml(flow_node, file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance)
        elif file_type == FileType.EXCEL.value:
            flow_node_excel_config = flow_node['fileExcelParseRuleDTO']
            move_excel(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance)
        elif file_type == FileType.CSV.value:
            # flow_node_csv_config = flow_node['flowNodeCsvConfig']
            # move_csv(flow_node, file_path_and_name, flow_node_csv_config, field_mapping_config_list, context_instance)
            pass
        else:
            pass

    elif implement_type == 'SCRIPT':
        # 脚本实现
        script_code = flow_node.get('scptCode')
        exec(script_code)

    else:
        pass