from engine.core.migrate_core_engine import *


def move_excel_to_oracle(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance):
    # 构造excel字段名列表，把上下文的变量去除，只留下excel文件中出现的字段名
    # txt_in_file_column_name_list = [field_mapping_config['sourceField'].upper()
    #                                 for field_mapping_config in field_mapping_config_list
    #                                 if field_mapping_config['sourceField'] not in context_instance]

    # txt头部文件所在行，这里设置为None，通过column_names来指定
    excel_header_line = None
    excel_skip_rows = flow_node_excel_config['skipRows']
    excel_column_count = flow_node_excel_config['totalColumnCount']

    # 将txt文件转换成dataframe
    excel_data_frame = excel_to_dataframe(file_path_and_name, excel_skip_rows, excel_column_count, excel_header_line)

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_excel_config.get('filterLogic')
    target_interface_table = flow_node_excel_config['targetIntfTbl']

    # 调用核心引擎，将dataframe数据插入数据库
    migrate_core_engine.dataframe_to_oracle(flow_node_excel_config,
        excel_data_frame, filter_logic, target_interface_table, field_mapping_config_list, context_instance)


def excel_to_dataframe(file_path_and_name, skip_rows, total_column_count, header_line=None):
    # pd.read_excel 如果传入的列名称比文件中的列数量少，则会导致列的对应关系不正确，这里人工在用户设置的列名称列表基础上，额外增加10列（做冗余，以防文件做了列增加）
    auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1+10)]
    excel_df = pd.read_excel(file_path_and_name,
                             skiprows=skip_rows, header=header_line, names=auto_gen_column_names)
    return excel_df

if __name__ == '__main__':
    my_skip_rows = 1
    my_total_column_count = 50
    my_dataframe = excel_to_dataframe('CSRCPERF.xls', my_skip_rows, my_total_column_count)
    print(my_dataframe)