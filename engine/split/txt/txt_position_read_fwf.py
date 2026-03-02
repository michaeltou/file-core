

import pandas as pd
from io import StringIO

file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/Income20241203"


file_split_field_list = 'F1::POSITION(10,22);F2::POSITION(22,28);'
field_list = file_split_field_list.split(';')
column_position_list = [eval(field.split('POSITION')[1]) for field in field_list if 'POSITION' in field]

column_count = len(column_position_list)
file_encoding = 'gbk'
txt_skip_rows = 0

# 定义列名
file_column_names = ['F' + str(i) for i in range(1, column_count + 1)]
column_dtypes = {col: 'str' for col in file_column_names}

# 以字节模式读取文件
with open(file_path_and_name, 'rb') as f:
    byte_data = f.read()

# 将字节数据转换为字符串
str_data = byte_data.decode(file_encoding)

# 使用 StringIO 将字符串数据转换为类文件对象
data = StringIO(str_data)


# 读取txt文件
txt_df = pd.read_fwf(data,
                     colspecs=column_position_list,
                     names=file_column_names,
                     header=None,
                     encoding=file_encoding,
                     skiprows=txt_skip_rows,
                     dtype=column_dtypes,
                      )

print(txt_df)

