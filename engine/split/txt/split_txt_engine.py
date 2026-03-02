from engine.cnst.ColumnGetType import ColumnGetType

from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
import engine.util.config as config
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql
import dbf
from engine.util.redis.redis_util import RedisUtil
import engine.util.log as log
import re
from engine.split.core.split_engine import split_dataframe


def split_txt_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance):
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')
    if file_path_and_name is None or not os.path.exists(file_path_and_name):
        log.error(f"文件 {file_path_and_name} 不存在。")
        return

    whole_dbf = txt_to_dataframe_reader(file_split_rule, file_path_and_name_dto, context_instance)

    # 发起dataframe的拆分
    split_dataframe(whole_dbf, file_path_and_name_dto, file_split_rule, context_instance)


def read_header_lines(file_path, skip_rows, encoding='gbk'):
    """
    读取文件数据行前的 标题内容。

    :param file_path: 文件路径
    :param skip_rows: 要读取的行数
    :param encoding: 文件编码，默认为 'gbk'
    :return: 包含前 n 行内容的列表
    """
    lines = []
    with open(file_path, 'r', encoding=encoding) as file:
        for i, line in enumerate(file):
            if i < skip_rows:
                lines.append(line)
            else:
                break
    if len(lines) == 0:
        lines = None
    return lines


def get_txt_column_count(file_path, skip_rows, encoding='gbk'):
    total_column_count = 0
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            for i, line in enumerate(file):
                if i < skip_rows:
                    continue
                elif i == skip_rows + 1:
                    first_data_line = line
                    total_column_count = len(first_data_line.split("@"))
                else:
                    break
        if total_column_count < 1:
            # 当文件为空时，total_column_count小于1，此时默认设置列数为30,这样能够保证后续处理列时，存在对应的列名称
            total_column_count = 30
    except FileNotFoundError:
        raise FileNotFoundError("文件不存在！")

    return total_column_count


def txt_to_dataframe_reader(file_split_rule, file_path_and_name_dto, context_instance):
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')

    # 拆分字段定位类型  1：按分隔符拆分，2：按位置拆分
    split_field_type = file_split_rule.get('splitFieldType')

    # 跳过行数
    txt_skip_rows = file_split_rule.get('skipRows')
    # txt头部文件所在行，这里设置为None，通过column_names来指定
    txt_header_line = None

    # 读取txt文件
    if txt_skip_rows is None:
        txt_skip_rows = 0
    # # todo 待删除，这里仅做测试
    # txt_skip_rows = 4

    file_encoding = file_split_rule.get('encoding')
    if file_encoding is None or len(file_encoding) == 0:
        file_encoding = 'gbk'

    # 拆分字段列表，分号分割，格式为 字段名称:所在列:所在位置 ,
    # 例如：F1:1:;F2:2:;F3:3: 或者F1::POSITION(1,2);F2::POSITION(3,2)
    file_split_field_list = file_split_rule.get('fileSplitFieldList')
    field_list = file_split_field_list.split(';')
    # 读取txt文件头部非数据行
    file_header = read_header_lines(file_path_and_name, txt_skip_rows, file_encoding)
    # 放到上下文中，后面写入文件时，会用到
    context_instance.set('file_header', file_header)

    if split_field_type == ColumnGetType.SEPERATOR.value:

        # 从F1:1:;F2:2:;F3:3: 字符串中 获取 ['F1','F2','F3'] 这样的字段名list
        column_name_list_for_split = [field.split(':')[0] for field in field_list if len(field) > 0]

        # 分隔符
        split_separator = file_split_rule.get('splitSeparator')

        # 读取文件第数据确定列数
        total_column_count = get_txt_column_count(file_path_and_name, txt_skip_rows, file_encoding)
        if total_column_count == 0:
            # 当文件为空时，total_column_count为0，此时默认设置列数为30,这样能够保证后续处理列时，存在对应的列名称
            total_column_count = 30

        auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count + 1)]
        # dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
        txt_df = pd.read_csv(file_path_and_name,
                             sep=split_separator, header=txt_header_line,
                             skiprows=txt_skip_rows, names=auto_gen_column_names,
                             index_col=False,  encoding=file_encoding,
                             dtype=str)
        # 获取需要删除的列名
        columns_to_drop = [col for col in txt_df.columns if col not in column_name_list_for_split]
        # 删除指定列
        txt_df = txt_df.drop(columns=columns_to_drop)

    elif split_field_type == ColumnGetType.POSITION.value:
        #  列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
        column_position_list = [eval(field.upper().split('POSITION')[1])
                                for field in field_list if 'POSITION' in field.upper()]

        # 以字节模式读取文件
        with open(file_path_and_name, 'rb') as f:
            byte_data = f.read()

        # 初始化空列表用于存储每行的数据
        rows = []

        # 逐行处理数据
        lines = byte_data.split(b'\n')
        index = 0
        for line in lines:
            # 跳过非数据行
            if index < txt_skip_rows:
                index += 1
                continue
            elif line is not None and len(line) > 0:
                row = []
                for start, end in column_position_list:
                    # 按字节位置提取数据
                    if start < len(line) and end <= len(line):
                        value = line[start:end].decode(file_encoding)
                        row.append(value)
                rows.append(row)
                index += 1

        # 定义列名
        column_names = ['F' + str(i) for i in range(1, len(column_position_list) + 1)]

        # 创建 DataFrame
        txt_df = pd.DataFrame(rows, columns=column_names)

    else:
        raise Exception('不支持的字段获取方式,column_get_type: %s' % split_field_type)

    combined_df = pd.DataFrame()


    """
    ASCII 码为 0 的空字符：\x00 是 Python 里对 ASCII 码为 0 的空字符的转义表示。在大多数文本文件中，这个字符通常不会出现，因为它一般用于表示字符串的结束，或者在二进制数据里作为填充字符。
    使用场景：当你希望把整个文本行当作一个完整的数据单元，而不进行分割时，就可以使用 \x00 作为分隔符。这在你要将文本文件的每一行数据都作为一个整体来读取，并且构建一个只有一列的 DataFrame 时非常有用。
    """
    # 读取txt文件，构造一个以每行为值的只有一列dataframe，列名称为'LINE'的dataframe
    line_df = pd.read_csv(file_path_and_name,
                          sep='\x00',  # 使用 \x00 作为分隔符
                          skiprows=txt_skip_rows,
                          names=['LINE'],
                          index_col=False,
                          encoding=file_encoding,
                          dtype=str)

    # 确保两个 DataFrame 行数相同
    if len(txt_df) == len(line_df):
        # 使用 pd.concat 进行左右拼接
        combined_df = pd.concat([txt_df, line_df], axis=1)
    else:
        raise Exception("两个 DataFrame 的行数不同，无法进行左右拼接。")

    return combined_df

