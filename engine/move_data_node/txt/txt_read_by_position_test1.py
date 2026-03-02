import pandas as pd

# 定义文件路径
file_path = '/Users/douming/Documents/采集发布/测试文件/Income20241203'

skip_rows = 0  # 跳过前几行
file_encoding = 'gbk'
# 定义列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
column_positions = [(0, 2), (2, 10), (10, 22), (22, 28), (28, 44), (44, 60), (60, 76), (76, 77), (77, 93)]

column_count = len(column_positions)
# 定义列名
column_names = ['F'+str(i) for i in range(1, column_count+1)]


# 定义列的数据类型
column_dtypes = {col: 'str' for col in column_names}

# 读取txt文件
reader = pd.read_fwf(file_path,
                     colspecs=column_positions,
                    names=column_names,
                    header=None,
                    encoding=file_encoding,
                    skiprows=skip_rows,
                    dtype=column_dtypes,
                    chunksize=10000*10)

for my_dataframe in reader:
    print(my_dataframe)


