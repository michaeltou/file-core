

import pandas as pd

# 定义列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
# column_positions = [(0, 2), (2, 10), (10, 16), (16, 25), (25, 29)]
# column_count = len(column_positions)

file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/Income20241203"

# 拆分字段列表，分号分割，格式为 字段名称:所在列:所在位置 ,
# 例如：F1:1:;F2:2:;F3:3: 或者F1::POSITION(1,2);F2::POSITION(3,2) 等
file_split_field_list = 'F1::POSITION(10,24);F2::POSITION(24,30);'
field_list = file_split_field_list.split(';')
column_position_list = [eval(field.split('POSITION')[1]) for field in field_list if 'POSITION' in field]

print(column_position_list)
column_count = len(column_position_list)
file_encoding = 'gbk'

txt_skip_rows = 0

# 定义列名
file_column_names = ['F' + str(i) for i in range(1, column_count + 1)]

# dtype=str 所有列在读取的时候，都使用str类型进行读取，防止读取到数字类型出现自动加0的情况
# 定义列的数据类型
column_dtypes = {col: 'str' for col in file_column_names}

# 读取txt文件
txt_df = pd.read_fwf(file_path_and_name,
                     colspecs= column_position_list,
                     names=file_column_names,
                     header=None,
                     encoding=file_encoding,
                     skiprows=txt_skip_rows,
                     dtype=column_dtypes,
                      )

print(txt_df)


# 高效读取 txt 文件并构造 DataFrame
line_df = pd.read_csv(file_path_and_name,
                      sep='\x00', # 使用 \x00 作为分隔符
                      skiprows=txt_skip_rows,
                       names=['LINE'],
                      index_col=False,
                      encoding=file_encoding,
                      dtype=str)

print('一行数据：',line_df)

# 确保两个 DataFrame 行数相同
if len(txt_df) == len(line_df):
    # 使用 pd.concat 进行左右拼接
    combined_df = pd.concat([txt_df, line_df], axis=1)
    print(combined_df)
else:
    print("两个 DataFrame 的行数不同，无法进行左右拼接。")