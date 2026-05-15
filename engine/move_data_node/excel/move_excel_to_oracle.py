import pandas as pd

from engine.core.migrate_core_engine import *
from xlsx2csv import Xlsx2csv
import uuid
import os


def move_excel_to_oracle(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance):
    # 构造excel字段名列表，把上下文的变量去除，只留下excel文件中出现的字段名
    # txt_in_file_column_name_list = [field_mapping_config['sourceField'].upper()
    #                                 for field_mapping_config in field_mapping_config_list
    #                                 if field_mapping_config['sourceField'] not in context_instance]



    # sheet名称，数字代表sheet的序号, 字符串代表sheet的名称
    sheet_name = str(flow_node_excel_config.get('sheetName'))

    # 配置方式：1-按照列位置配置，2-按照列名称配置
    config_type = flow_node_excel_config.get('configType')

    # 列名称所在行号
    header_line = flow_node_excel_config.get('headerLine')
    flow_node_rename_config_list = flow_node.get('fileExcelRenameRuleDTOList')


    excel_data_frame = pd.DataFrame()
    if config_type == 'BY_COL_POSITION':
        # 按照列位置配置
        excel_data_frame = excel_to_dataframe_by_position(context_instance,file_path_and_name, flow_node_excel_config, sheet_name)
    elif config_type == 'BY_COL_NAME':
        # 按照列名称配置
        excel_data_frame = excel_to_dataframe_by_column_name(context_instance,file_path_and_name, flow_node_rename_config_list, sheet_name, header_line)

    # 将excel文件转换成dataframe
    # excel_data_frame = excel_to_dataframe(file_path_and_name, excel_skip_rows, excel_column_count)

    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_excel_config.get('filterLogic')
    target_interface_table = flow_node_excel_config['targetIntfTbl']

    CleanEngine.process_clean_before_import(flow_node_excel_config, context_instance)



    # 调用核心引擎，将dataframe数据插入数据库
    migrate_core_engine.dataframe_to_oracle(flow_node_excel_config,
                                            excel_data_frame,
                                            filter_logic,
                                            target_interface_table,
                                            field_mapping_config_list,
                                            context_instance)


def excel_to_dataframe(file_path_and_name, skip_rows, total_column_count, header_line=None):
    # pd.read_excel 如果传入的列名称比文件中的列数量少，则会导致列的对应关系不正确，这里人工在用户设置的列名称列表基础上，额外增加10列（做冗余，以防文件做了列增加）
    auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1+10)]
    try:
        excel_df = pd.read_excel(file_path_and_name,
                                 skiprows=skip_rows,
                                 header=header_line,
                                 names=auto_gen_column_names
                                 )

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
                                     skiprows=skip_rows,
                                     names=auto_gen_column_names,
                                     index_col=False)
        delete_file(random_filename)
        return csv_data_frame


# 按照列位置读取excel文件,并返回dataframe
def excel_to_dataframe_by_position(context_instance,file_path_and_name, flow_node_excel_config, sheet_name=0):
    skip_rows = str(flow_node_excel_config.get('skipRows'))
    total_column_count = str(flow_node_excel_config.get('excelFileColCount'))
    my_uuid = context_instance.get('[UUID]')

    # excel头部文件所在行，这里设置为None，通过column_names来指定
    header_line = None
    # sheet名称，数字代表sheet的序号, 字符串代表sheet的名称
    if sheet_name.isdigit():
        sheet_name = int(sheet_name)
        # 页面操作是从1开始，程序中从0开始，所以这里需要减1
        sheet_name = sheet_name - 1

    if skip_rows.isdigit():
        skip_rows = int(skip_rows)
    else:
        skip_rows = context_instance.get(skip_rows)
        skip_rows = str(skip_rows)
        if skip_rows.isdigit():
            skip_rows = int(skip_rows)
        else:
            raise ValueError(f"skipRows配置错误，请检查配置项{skip_rows}是否存在上下文变量或数字")

    if total_column_count.isdigit():
        total_column_count = int(total_column_count)
    else:
        total_column_count = context_instance.get(total_column_count)
        total_column_count = str(total_column_count)
        if total_column_count.isdigit():
            total_column_count = int(total_column_count)
        else:
            raise ValueError(f"totalColumnCount配置错误，请检查配置项{total_column_count}是否存在上下文变量或数字")



    # pd.read_excel 如果传入的列名称比文件中的列数量少，则会导致列的对应关系不正确，这里人工在用户设置的列名称列表基础上，额外增加10列（做冗余，以防文件做了列增加）
    auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1+10)]


    # 如果xlsx文件大于1M ，则优先将xlsx文件转换为csv文件，然后再读取csv文件
    file_size = os.path.getsize(file_path_and_name)
    if file_size > 1024 * 1024 and file_path_and_name.endswith('.xlsx'):
        try:
            random_filename = generate_random_filename()
            start_time = time.time()
            Xlsx2csv(file_path_and_name, outputencoding="utf-8", sheet_name=sheet_name).convert(random_filename)
            end_time = time.time()
            log.info(f"uuid:{my_uuid} , 优先代码块, xlsx转换csv文件耗时 {end_time - start_time} 秒")
            # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
            default_sep = ","
            # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
            start_time = time.time()
            csv_data_frame = pd.read_csv(random_filename,
                                         sep=default_sep,
                                         header=header_line,
                                         skiprows=skip_rows,
                                         names=auto_gen_column_names,
                                         index_col=False,
                                         dtype=str)
            end_time = time.time()
            log.info(f"uuid:{my_uuid} , 优先代码块, 读取csv文件耗时 {end_time - start_time} 秒")
            delete_file(random_filename)
            return csv_data_frame
        except Exception as e:
            log.info(f"uuid:{my_uuid} , 优先代码块, 尝试使用 xlsx2csv 转换为 csv 文件再读取失败，原因是{e}")


    # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
    try:
        start_time = time.time()
        excel_df = pd.read_excel(file_path_and_name,
                                 sheet_name=sheet_name,
                                 skiprows=skip_rows,
                                 header=header_line,
                                 names=auto_gen_column_names,
                                 dtype=str
                                 )
        end_time = time.time()
        log.info(f"uuid:{my_uuid} , 按列位置读取: pd.read_excel读取excel文件转成dataframe耗时 {end_time - start_time} 秒,文件是{file_path_and_name}")
        return excel_df
    except TypeError as e:
        print(f'Error: {e}')
        print('由于excel格式（比如wind万德导出的xls文件格式）异常，尝试使用 xlsx2csv 转换为 csv 文件再读取')
        random_filename = generate_random_filename()
        Xlsx2csv(file_path_and_name, outputencoding="utf-8", sheet_name=sheet_name).convert(random_filename)
        # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
        default_sep = ","
        # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
        csv_data_frame = pd.read_csv(random_filename,
                                     sep=default_sep,
                                     header=header_line,
                                     skiprows=skip_rows,
                                     names=auto_gen_column_names,
                                     index_col=False,
                                     dtype=str)
        delete_file(random_filename)
        return csv_data_frame


def excel_to_dataframe_by_column_name(context_instance, file_path_and_name,flow_node_rename_config_list, sheet_name = 0, header_line =0):
    source_name_list = []
    target_name_list = []
    source_and_target_name_dict = {}
    my_uuid = context_instance.get('[UUID]')

    for flow_node_rename_config in flow_node_rename_config_list:
        source_name = flow_node_rename_config.get('sourceName')
        target_name = flow_node_rename_config.get('targetName')
        source_name_list.append(source_name)
        target_name_list.append(target_name)
        source_and_target_name_dict[source_name] = target_name
    # sheet名称，数字代表sheet的序号, 字符串代表sheet的名称
    if sheet_name.isdigit():
        sheet_name = int(sheet_name)
        # 页面操作是从1开始，程序中从0开始，所以这里需要减1
        sheet_name = sheet_name - 1

    # 名称所在行号，页面操作是从1开始，程序中从0开始，所以这里需要减1
    header_line = header_line - 1

    # 如果xlsx文件大于1M ，则优先将xlsx文件转换为csv文件，然后再读取csv文件
    file_size = os.path.getsize(file_path_and_name)
    if file_size > 1024 * 1024 and file_path_and_name.endswith('.xlsx'):
        try:
            random_filename = generate_random_filename()
            start_time = time.time()
            Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert(random_filename)
            end_time = time.time()
            log.info(f"uuid:{my_uuid} ,优先代码块2,  xlsx转换csv文件耗时 {end_time - start_time} 秒")
            # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
            default_sep = ","
            auto_gen_column_names = [f'FF{i}' for i in range(1, 30)]
            # 这里将指定的列名称，加上30个冗余列，以防文件做了列增加
            target_name_list.extend(auto_gen_column_names)
            start_time = time.time()
            # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
            # 这里使用target_name_list，有个要求：需要用户在配置读数规则的时候，把excel文件里面所有的列名称重命名都按顺序配置上，
            # 不然会导致列的对应关系不正确
            csv_data_frame = pd.read_csv(random_filename,
                                         sep=default_sep,
                                         names=target_name_list,
                                         index_col=False,
                                         dtype=str)
            end_time = time.time()
            log.info(f"uuid:{my_uuid} , 优先代码块2, 读取csv文件耗时 {end_time - start_time} 秒")
            delete_file(random_filename)
            return csv_data_frame
        except Exception as e:
            log.info(f"uuid:{my_uuid} ,  优先代码块2,尝试使用 xlsx2csv 转换为 csv 文件再读取失败，原因是{e}")


    # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
    try:
        start_time = time.time()
        excel_df = pd.read_excel(file_path_and_name,
                                 sheet_name=sheet_name,
                                 header=header_line,
                                 usecols=source_name_list,
                                 dtype=str)
        end_time = time.time()
        log.info(f"uuid:{my_uuid} , 按列名称读取: pd.read_excel读取excel文件转成dataframe耗时 {end_time - start_time} 秒,"
                 f"文件是{file_path_and_name}")
        # 重命名列
        excel_df.rename(columns=source_and_target_name_dict, inplace=True)

        return excel_df

    except TypeError as e:
        print(f'Error: {e}')
        print('由于excel格式（比如wind万德导出的xls文件格式）异常，尝试使用 xlsx2csv 转换为 csv 文件再读取')
        random_filename = generate_random_filename()
        Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert(random_filename)
        # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
        default_sep = ","
        auto_gen_column_names = [f'F{i}' for i in range(1, 30)]
        # 这里将指定的列名称，加上20个冗余列，以防文件做了列增加
        target_name_list.append(auto_gen_column_names)
        # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况;
        # 这里使用target_name_list，有个要求：需要用户在配置读数规则的时候，把excel文件里面所有的列名称重命名都按顺序配置上，
        # 不然会导致列的对应关系不正确
        csv_data_frame = pd.read_csv(random_filename,
                                     sep=default_sep,
                                     names=target_name_list,
                                     index_col=False,
                                     dtype=str)
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

def test_excel_to_dataframe():
    my_skip_rows = 1
    my_total_column_count = 50
    my_dataframe = excel_to_dataframe('CSRCPERF.xls', my_skip_rows, my_total_column_count)
    print(my_dataframe)

def test_excel_to_dataframe_by_column_name():

    flow_node_rename_config_list = [
        {"sourceName": "指数代码", "targetName": "index_code"},
        {"sourceName": "指数名称", "targetName": "index_name"},
    ]

    my_dataframe = excel_to_dataframe_by_column_name('CSRCPERF.xls',  flow_node_rename_config_list)
    print(my_dataframe)


def test_excel_to_dataframe_by_position():
    excel_skip_rows, excel_column_count = 1, 30
    my_dataframe = excel_to_dataframe_by_position('CSRCPERF.xls',  excel_skip_rows, excel_column_count)
    print(my_dataframe)

if __name__ == '__main__':
    # test_excel_to_dataframe_by_column_name()
    test_excel_to_dataframe_by_position()