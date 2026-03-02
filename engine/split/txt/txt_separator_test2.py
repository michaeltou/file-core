

import pandas as pd

# 分隔符
txt_separator = '@'
# todo 界面增加：文件列数配置。 提示语：请输入该文件中，至少包含的列总数。
total_column_count = 3
txt_skip_rows = 0
file_encoding = 'gbk'

file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/88862282fundchg20241203.txt"

# 读取文件第一行确定列数
with open(file_path_and_name, 'r', encoding=file_encoding) as f:
    first_line = f.readline()
    total_column_count = len(first_line.split(txt_separator))

# pd.read_csv 如果传入的列名称比文件中的列数量少，则会报错，这里人工在用户设置的列名称列表基础上，
# 增加10个额外的列名称，以防报错，这个额外的列名称不会被任何地方使用到。
auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1)]

# 高效读取 txt 文件并构造 DataFrame
txt_df = pd.read_csv(file_path_and_name,
                      sep=txt_separator,
                      skiprows=txt_skip_rows,
                       names=auto_gen_column_names,
                      index_col=False,
                      encoding=file_encoding,
                      dtype=str)

print(txt_df)


file_split_field_list = 'F3:3:;F4:4:;'
field_list = file_split_field_list.split(';')
column_position_list = [field.split(':')[0] for field in field_list if len(field) > 0]


# 获取需要删除的列名
columns_to_drop = [col for col in txt_df.columns if col not in column_position_list]

# 删除指定列
txt_df = txt_df.drop(columns=columns_to_drop)

print('删除后的dataframe：\n', txt_df)


"""
ASCII 码为 0 的空字符：\x00 是 Python 里对 ASCII 码为 0 的空字符的转义表示。在大多数文本文件中，这个字符通常不会出现，因为它一般用于表示字符串的结束，或者在二进制数据里作为填充字符。
使用场景：当你希望把整个文本行当作一个完整的数据单元，而不进行分割时，就可以使用 \x00 作为分隔符。这在你要将文本文件的每一行数据都作为一个整体来读取，并且构建一个只有一列的 DataFrame 时非常有用。
"""

# 高效读取 txt 文件并构造 DataFrame
line_df = pd.read_csv(file_path_and_name,
                      sep='\x00', # 使用 \x00 作为分隔符
                      skiprows=txt_skip_rows,
                       names=['LINE'],
                      index_col=False,
                      encoding=file_encoding,
                      dtype=str)

print(line_df)

# 确保两个 DataFrame 行数相同
if len(txt_df) == len(line_df):
    # 使用 pd.concat 进行左右拼接
    combined_df = pd.concat([txt_df, line_df], axis=1)
    print(combined_df)
else:
    print("两个 DataFrame 的行数不同，无法进行左右拼接。")

