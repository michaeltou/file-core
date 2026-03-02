from engine.core.migrate_core_engine import *
from engine.cnst.ColumnGetType import ColumnGetType
import engine.util.config as config


def move_txt_to_oracle(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance):

    # 将txt文件转换成dataframe
    reader = txt_to_dataframe_reader(flow_node_txt_config, file_path_and_name, field_mapping_config_list, context_instance)
    for my_dataframe in reader:
        # 创建读数引擎
        migrate_core_engine = MigrateCoreEngine()
        filter_logic = flow_node_txt_config.get('filterLogic')
        target_interface_table = flow_node_txt_config['targetIntfTbl']

        # 调用核心引擎，将dataframe数据插入数据库
        migrate_core_engine.dataframe_to_oracle(flow_node_txt_config,
                                                my_dataframe, filter_logic,
                                                target_interface_table,
                                                field_mapping_config_list,
                                                context_instance)


# 这个方法暂时不用，这里只是做保留，以后可以考虑用这个方法来处理txt文件
def generate_filtered_text_file(file_path_and_name, filter_logic):
    with open(file_path_and_name, 'r') as input_file, open(file_path_and_name + '_filtered', 'w') as output_file:
        for line in input_file:
            # 执行过滤逻辑，满足条件的行写入输出文件
            if eval(filter_logic):
                output_file.write(line)


def txt_to_dataframe_reader(flow_node_txt_config, file_path_and_name,
                            field_mapping_config_list, context_instance):


    # txt头部文件所在行，这里设置为None，通过column_names来指定
    txt_header_line = None
    txt_skip_rows = flow_node_txt_config['skipRows']

    if txt_skip_rows.isdigit():
        txt_skip_rows = int(txt_skip_rows)
    else:
        txt_skip_rows = context_instance.get(txt_skip_rows)
        txt_skip_rows = str(txt_skip_rows)
        if txt_skip_rows.isdigit():
            txt_skip_rows = int(txt_skip_rows)
        else:
            raise ValueError(f"skipRows配置错误，请检查配置项{skip_rows}是否存在上下文变量或数字")

    file_encoding = flow_node_txt_config.get('encoding')
    column_get_type = flow_node_txt_config.get('columnGetType')

    default_chunk_size = 100000
    chunk_size = config.get_config_value('txt.chunk_size', default_chunk_size)

    if column_get_type == ColumnGetType.SEPERATOR.value:
        txt_separator = flow_node_txt_config.get('separator')

        total_column_count = flow_node_txt_config.get('totalColumnCount')
        if total_column_count.isdigit():
            total_column_count = int(total_column_count)
        else:
            total_column_count = context_instance.get(total_column_count)
            total_column_count = str(total_column_count)
            if total_column_count.isdigit():
                total_column_count = int(total_column_count)
            else:
                raise ValueError(f"totalColumnCount配置错误，请检查配置项{total_column_count}是否存在上下文变量或数字")

        # pd.read_csv 如果传入的列名称比文件中的列数量少，则会报错，这里人工在用户设置的列名称列表基础上，
        # 增加10个额外的列名称，以防报错，这个额外的列名称不会被任何地方使用到。
        auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count + 1 + 10)]

        # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
        reader = pd.read_csv(file_path_and_name,
                             sep=txt_separator, header=txt_header_line,
                             skiprows=txt_skip_rows, names=auto_gen_column_names,
                             index_col=False, chunksize=chunk_size, encoding=file_encoding,
                             dtype=str)
        return reader
    elif column_get_type == ColumnGetType.POSITION.value:
        # 构造txt字段名列表，把上下文的变量去除，只留下txt文件中出现的字段名
        # txt_in_file_column_name_list = [field_mapping_config['sourceField'].upper()
        #                                 for field_mapping_config in field_mapping_config_list
        #                                 if field_mapping_config['sourceField'] not in context_instance]
        #
        # txt_column_names = txt_in_file_column_name_list

        # 定义列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
        # column_positions = [(0, 2), (2, 10), (10, 16), (16, 25), (25, 29)]
        # column_count = len(column_positions)

        column_position_list = flow_node_txt_config.get('columnPositionList')
        column_position_list = eval(column_position_list)
        column_count = len(column_position_list)

        # 定义列名
        file_column_names = ['F' + str(i) for i in range(1, column_count + 1)]

        # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
        # 定义列的数据类型
        column_dtypes = {col: 'str' for col in file_column_names}

        # 读取txt文件
        reader = pd.read_fwf(file_path_and_name,
                             colspecs=column_position_list,
                             names=file_column_names,
                             header=None,
                             encoding=file_encoding,
                             skiprows=txt_skip_rows,
                             dtype=column_dtypes,
                             chunksize=chunk_size)
        return reader
    else:
        raise Exception('不支持的字段获取方式,column_get_type: %s' % column_get_type)



def check_char_in_position():
    line = '600011              |华能国际|     900|1|0.10000|0.00000|            |    | |                              |'
    if line[20:21] == '|':
        print('yes')
    else:
        print('no')


if __name__ == '__main__':

    separator = "|"
    header = None
    skip_rows = 12
    column_names = ['F' + str(i) for i in range(1, 3)]
    column_names.insert(0, 'column1')
    column_names.insert(1, 'column2')

    # txt_to_dataframe('20180302BOND_VALUATION.txt', separator, header, skip_rows, column_names)
    check_char_in_position()