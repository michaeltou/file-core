file_path_and_name = 'ALLOT20180419'
column_position_list = [(0, 10), (10, 22), (22, 31), (31, 50)]
# 以字节模式读取文件
with open(file_path_and_name, 'rb') as f:
    byte_data = f.read()

# 初始化空列表用于存储每行的数据
rows = []
skip_rows = 3

# 逐行处理数据
lines = byte_data.split(b'\n')
index = 0
for line in lines:
    if index <= skip_rows:
        index += 1
        continue
    elif line is not None and len(line) > 0:
        row = []
        for start, end in column_position_list:
            # 按字节位置提取数据
            if start < len(line) and end <= len(line):
                value = line[start:end].decode('gbk')
                row.append(value)
        rows.append(row)
        index += 1


print(rows)