import pandas as pd

from engine.core.migrate_core_engine import *
from engine.cnst.ColumnGetType import ColumnGetType
import engine.util.config as config
import traceback
import fnmatch

def move_txt_to_oracle(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance):
    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    filter_logic = flow_node_txt_config.get('filterLogic')
    target_interface_table = flow_node_txt_config['targetIntfTbl']

    column_get_type = flow_node_txt_config.get('columnGetType')

    if column_get_type == ColumnGetType.SEPERATOR.value:
        # 获取文件的大小，如果文件大小大于100M,则分块读取
        file_size = os.path.getsize(file_path_and_name)
        if file_size > 100 * 1024 * 1024:
            # # 将txt文件以分隔符的方式转换成dataframe
            reader = txt_to_dataframe_reader_for_separator(flow_node_txt_config, file_path_and_name, context_instance)
            for my_dataframe in reader:
                # 调用核心引擎，将dataframe数据插入数据库
                migrate_core_engine.dataframe_to_oracle(flow_node_txt_config,
                                                        my_dataframe, filter_logic,
                                                        target_interface_table,
                                                        field_mapping_config_list,
                                                        context_instance)
        else:
            # 将txt文件以分隔符的方式转换成dataframe
            my_dataframe = txt_to_dataframe_for_separator(flow_node_txt_config, file_path_and_name, context_instance)

            # 调用核心引擎，将dataframe数据插入数据库
            migrate_core_engine.dataframe_to_oracle(flow_node_txt_config,
                                                    my_dataframe, filter_logic,
                                                    target_interface_table,
                                                    field_mapping_config_list,
                                                    context_instance)

    elif column_get_type == ColumnGetType.POSITION.value:
        # 将txt文件以字节位置的方式转换成dataframe
        my_dataframe = txt_to_dataframe_for_byte_position(flow_node_txt_config, file_path_and_name, context_instance)
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


def txt_to_dataframe_reader_for_separator(flow_node_txt_config, file_path_and_name, context_instance):
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

    # file_encoding = flow_node_txt_config.get('encoding')
    file_encoding = context_instance.get('[ENCODING]')
    default_chunk_size = 100000
    chunk_size = config.get_config_value('txt.chunk_size', default_chunk_size)

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


def txt_to_dataframe_for_separator(flow_node_txt_config, file_path_and_name, context_instance):
    # txt头部文件所在行，这里设置为None，通过column_names来指定
    txt_header_line = None
    txt_skip_rows = flow_node_txt_config['skipRows']
    txt_skip_rows = str(txt_skip_rows)

    if txt_skip_rows.isdigit():
        txt_skip_rows = int(txt_skip_rows)
    else:
        txt_skip_rows = context_instance.get(txt_skip_rows)
        txt_skip_rows = str(txt_skip_rows)
        if txt_skip_rows.isdigit():
            txt_skip_rows = int(txt_skip_rows)
        else:
            raise ValueError(f"skipRows配置错误，请检查配置项{skip_rows}是否存在上下文变量或数字")


    file_encoding = context_instance.get('[ENCODING]')
    # default_chunk_size = 100000
    # chunk_size = config.get_config_value('txt.chunk_size', default_chunk_size)

    txt_separator = flow_node_txt_config.get('separator')

    total_column_count = flow_node_txt_config.get('totalColumnCount')
    total_column_count = str(total_column_count)
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

    # 以字节模式读取文件
    with open(file_path_and_name, 'rb') as f:
        byte_data = f.read()
    # 初始化空列表用于存储每行的数据
    rows = []
    file_name = os.path.basename(file_path_and_name)
    if fnmatch.fnmatch(file_name, 'mktdt04*.txt'):
        # 逐行处理数据
        lines = byte_data.split(b'\n')
        line_no = 0
        prev_line = b''
        max_column_count = 0
        for line in lines:
            line_no += 1
            if line_no <= 1:
                continue
            if line is not None and len(line) > 0:
                # 乱码行后面的字节数为44， 当小于这个44个字节，认为是被乱码导致换行，则进行拼接处理
                if len(line) <= 44:
                    if len(prev_line) > 0:
                        prev_line = prev_line + b'\r' + line
                    else:
                        prev_line = line
                    continue
                else:
                    if len(prev_line) > 0:
                        final_line = prev_line + b'\r' + line
                        prev_line = b''
                    else:
                        final_line = line

                row = []
                one_line = final_line.decode(file_encoding, errors='ignore')

                # 由于第3列乱码，可能存在乱码中有|的情况，这里进行处理。
                # 获取第3列最后一个位置
                end_index = one_line.index('\x000|')
                if end_index > 0:
                   #  "\x00" 为一个字符，0 为一个字符 ，加2是为了跳过\x000，拿到最后一个位置
                    end_index = end_index + 2
                else: # 如果没有最后一个位置的识别，则默认截取30个字符
                    end_index = 30
                # 由于第3列乱码，可能存在乱码中有|的情况，这里进行处理。
                line_section = one_line[12:end_index]
                if '|' in line_section:
                    line_list = list(one_line)  # 转换为列表方便修改
                    for i in range(12, 30):
                        if i < len(line_list) and line_list[i] == '|':
                            line_list[i] = ' '
                    one_line = ''.join(line_list)  # 重新组合字符串
                    # print('已替换错误的|')


                row = one_line.split(txt_separator)
                max_column_count = max(max_column_count, len(row))
                rows.append(row)
        # end for line in lines:

        # 定义列名
        column_name_list = ['F' + str(i) for i in range(1, max_column_count + 1)]
        # 创建 DataFrame
        txt_dataframe = pd.DataFrame(rows, columns=column_name_list)

        txt_dataframe.insert(0, '[LINE_NO]', range(1, len(rows)+1))


    else:
        try:
            # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
            txt_dataframe = pd.read_csv(file_path_and_name,
                                 sep=txt_separator, header=txt_header_line,
                                 skiprows=txt_skip_rows, names=auto_gen_column_names,
                                 index_col=False,  encoding=file_encoding,
                                 dtype=str)
            txt_dataframe.insert(0, '[LINE_NO]', range(1, txt_dataframe.shape[0] + 1))
        except UnicodeDecodeError as e:
            if file_encoding.upper() == 'GBK':
                file_encoding = 'UTF-8'
            else:
                file_encoding = 'GBK'
            txt_dataframe = pd.read_csv(file_path_and_name,
                                        sep=txt_separator, header=txt_header_line,
                                        skiprows=txt_skip_rows, names=auto_gen_column_names,
                                        index_col=False, encoding=file_encoding,
                                        dtype=str)
            txt_dataframe.insert(0, '[LINE_NO]', range(1, txt_dataframe.shape[0] + 1))
    return txt_dataframe


def txt_to_dataframe_for_byte_position(flow_node_txt_config, file_path_and_name, context_instance):

    txt_skip_rows = str(flow_node_txt_config['skipRows'])


    if txt_skip_rows.isdigit():
        txt_skip_rows = int(txt_skip_rows)
    else:
        txt_skip_rows = context_instance.get(txt_skip_rows)
        txt_skip_rows = str(txt_skip_rows)
        if txt_skip_rows.isdigit():
            txt_skip_rows = int(txt_skip_rows)
        else:
            raise ValueError(f"skipRows配置错误，请检查配置项{skip_rows}是否存在上下文变量或数字")

    file_encoding = context_instance.get('[ENCODING]')
    # 定义列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
    # column_position_list = [(0, 2), (2, 10), (10, 16), (16, 25), (25, 29)]
    column_position_list = flow_node_txt_config.get('columnPositionList')
    column_position_list = eval(column_position_list)
    column_count = len(column_position_list)

    # 以字节模式读取文件
    with open(file_path_and_name, 'rb') as f:
        byte_data = f.read()
    # 初始化空列表用于存储每行的数据
    rows = []
    file_name = os.path.basename(file_path_and_name)
    # 1008 接口特殊处理，1008接口文件里面有一列是乱码，其中一些乱码字符，导致一行数据变成2行。
    if fnmatch.fnmatch(file_name, 'mktdt04*.txt'):
        # 逐行处理数据
        lines = byte_data.split(b'\n')
        line_no = 0
        prev_line = b''
        for line in lines:
            line_no += 1
            if line_no <= 1:
                continue
            if line is not None and len(line) > 0:
                # 乱码行后面的字节数为44， 当小于这个44个字节，认为是被乱码导致换行，则进行拼接处理
                if len(line) <= 44:
                    if len(prev_line) > 0:
                        prev_line = prev_line + b'\r' + line
                    else:
                        prev_line = line
                    continue
                else:
                    if len(prev_line) > 0:
                        final_line = prev_line + b'\r' + line
                        prev_line = b''
                    else:
                        final_line = line

                row = []


                for start, end in column_position_list:
                    # 按字节位置提取数据
                    if start < len(final_line) and end <= len(final_line):
                        value = final_line[start:end].decode(file_encoding, errors='ignore')
                        row.append(value)
                    else:
                        row.append('')

                rows.append(row)
    else:
        # 逐行处理数据
        lines = byte_data.split(b'\n')
        line_no = 0
        for line in lines:
            line_no += 1
            if line_no <= txt_skip_rows:
                continue
            if line is not None and len(line) > 0:
                row = []
                for start, end in column_position_list:
                    # 按字节位置提取数据
                    if start < len(line) and end <= len(line):
                        value = line[start:end].decode(file_encoding, errors='ignore')
                        # try:
                        #     value = line[start:end].decode(file_encoding)
                        # except UnicodeDecodeError as e:
                        #     value = line[start:end].decode(file_encoding, errors='ignore')
                        #     # stack_trace = traceback.format_exc()
                        #     # message = 'uuid:%s, 行号%s, 列号(%s,%s) 转换字节为字符串发生异常，异常信息：%s' % (my_uuid, line_no, start, end, stack_trace)
                        #     # log.error(message)

                        row.append(value)
                    else:
                        row.append('')
                rows.append(row)

    # 定义列名
    column_name_list = ['F' + str(i) for i in range(1, column_count + 1)]
    # 创建 DataFrame
    txt_df = pd.DataFrame(rows, columns=column_name_list)
    txt_df.insert(0, '[LINE_NO]', range(1, txt_df.shape[0] + 1))
    return txt_df




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