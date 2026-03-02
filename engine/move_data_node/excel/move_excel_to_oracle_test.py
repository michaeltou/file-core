from engine.core.migrate_core_engine import *
from xlsx2csv import Xlsx2csv
import uuid
import os


def move_excel_to_oracle(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance):
    # 构造excel字段名列表，把上下文的变量去除，只留下excel文件中出现的字段名
    # txt_in_file_column_name_list = [field_mapping_config['sourceField'].upper()
    #                                 for field_mapping_config in field_mapping_config_list
    #                                 if field_mapping_config['sourceField'] not in context_instance]

    # excel头部文件所在行，这里设置为None，通过column_names来指定
    excel_header_line = None
    excel_skip_rows = flow_node_excel_config['skipRows']
    excel_column_count = flow_node_excel_config['totalColumnCount']

    # 将excel文件转换成dataframe
    excel_data_frame = excel_to_dataframe(file_path_and_name, excel_skip_rows, excel_column_count, excel_header_line)

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_excel_config.get('filterLogic')
    target_interface_table = flow_node_excel_config['targetIntfTbl']

    # 调用核心引擎，将dataframe数据插入数据库
    migrate_core_engine.dataframe_to_oracle(flow_node_excel_config,
        excel_data_frame, filter_logic, target_interface_table, field_mapping_config_list, context_instance)


def excel_to_dataframe(file_path_and_name, target_sheet_name=0, header_line=0):
    # 定义新的列名称
    new_columns = {'日期': 'New_A', '指数代码': 'New_B'}

    try:
        excel_df = pd.read_excel(file_path_and_name,
                                 sheet_name=target_sheet_name,
                                 header=header_line
                                 )
        excel_df.rename(columns=new_columns, inplace=True)

        return excel_df
    except TypeError as e:
        print(f'Error: {e}')
        print('由于excel格式（比如wind万德导出的xls文件格式）异常，尝试使用 xlsx2csv 转换为 csv 文件再读取')
        random_filename = generate_random_filename()
        Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert(random_filename)
        # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
        default_sep = ","
        csv_data_frame = pd.read_csv(random_filename,
                                     sep=default_sep,
                                     header=header_line,
                                     # skiprows=skip_rows,
                                     # names=auto_gen_column_names,
                                     index_col=False)
        delete_file(random_filename)
        return csv_data_frame


def excel_to_dataframe_by_certain_columns(file_path_and_name, target_sheet_name=0, header_line=0):
    # 定义新的列名称
    new_columns = {'日期': 'New_A', '指数代码': 'New_B'}

    try:
        excel_df = pd.read_excel(file_path_and_name,
                                 sheet_name=target_sheet_name,
                                 header=header_line,
                                 usecols= ['日期', '指数代码'])
        excel_df.rename(columns=new_columns, inplace=True)

        return excel_df
    except TypeError as e:
        print(f'Error: {e}')
        print('由于excel格式（比如wind万德导出的xls文件格式）异常，尝试使用 xlsx2csv 转换为 csv 文件再读取')
        random_filename = generate_random_filename()
        Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert(random_filename)
        # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
        default_sep = ","
        csv_data_frame = pd.read_csv(random_filename,
                                     sep=default_sep,
                                     header=header_line,
                                     # skiprows=skip_rows,
                                     # names=auto_gen_column_names,
                                     index_col=False)
        delete_file(random_filename)
        return csv_data_frame


def generate_random_filename():
    # 生成一个随机的UUID
    random_uuid = uuid.uuid4()
    # 将UUID转换为字符串，并去掉连字符
    random_filename = str(random_uuid).replace('-', '')
    random_filename = random_filename + '.csv'
    return random_filename


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"文件 {file_path} 已成功删除。")
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
    except PermissionError:
        print(f"没有权限删除文件 {file_path}。")
    except Exception as e:
        print(f"删除文件 {file_path} 时发生错误: {e}")

if __name__ == '__main__':
    target_sheet_name = 0
    header_line = 0
    # my_dataframe = excel_to_dataframe('CSRCPERF.xls', target_sheet_name, header_line)
    my_dataframe =  excel_to_dataframe_by_certain_columns('CSRCPERF.xls')
    print(my_dataframe)