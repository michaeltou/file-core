import pandas as pd


file_split_field_list = 'F1::POSITION(10,22);F2::POSITION(22,28);'
field_list = file_split_field_list.split(';')
column_position_list = [eval(field.split('POSITION')[1]) for field in field_list if 'POSITION' in field]



# 文件路径
file_path = "/Users/douming/Documents/采集发布/测试文件/Income20241203"

# 以字节模式读取文件
with open(file_path, 'rb') as f:
    byte_data = f.read()

# 初始化空列表用于存储每行的数据
rows = []

# 逐行处理数据
lines = byte_data.split(b'\n')
for line in lines:
    if line is not None and len(line) > 0:
        row = []
        for start, end in column_position_list:
            # 按字节位置提取数据
            if start < len(line) and end <= len(line):
                value = line[start:end].decode('gbk')  # 假设编码为 gbk
                row.append(value)
        rows.append(row)

# 定义列名
column_names = ['F' + str(i) for i in range(1, len(column_position_list) + 1)]

# 创建 DataFrame
df = pd.DataFrame(rows, columns=column_names)

print(df)