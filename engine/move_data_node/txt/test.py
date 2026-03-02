file_encoding = 'gbk'
# 定义列的位置 (start, end) 包含开始位置，索引从0开始。不包含结束位置。字符个数为：end-start。
# column_position_list = [(0, 2), (2, 10), (10, 16), (16, 25), (25, 29)]
column_position_list = '[(0,5),(6,11),(12,44),(45,60),(61,77),(78,94),(95,106),(107,118),(119,130),(131,142),(143,154),(155,166),(167,179),(180,191),(192,204),(205,213),(214,226)]'
column_position_list = eval(column_position_list)
column_count = len(column_position_list)

# 以字节模式读取文件
with open('mktdt04.txt', 'rb') as f:
    byte_data = f.read()
# 初始化空列表用于存储每行的数据
rows = []
# 1008 接口特殊处理，1008接口文件里面有一列是乱码，其中一些乱码字符，导致一行数据变成2行。

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

        rows.append(row)