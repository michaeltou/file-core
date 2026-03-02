import dbfread

# 指定DBF文件的路径
dbf_file_path = 'path/to/your_file.dbf'

# 尝试不同的编码来读取DBF文件
encodings_to_try = ['latin1', 'cp850', 'utf-8']  # 根据需要添加更多编码

for encoding in encodings_to_try:
    try:
        # 尝试使用当前编码打开DBF文件
        table = dbfread.DBF(dbf_file_path, encoding=encoding)

        # 如果成功打开，则遍历并打印每一行数据
        for record in table:
            print(record)

            # 如果成功读取并打印数据，则跳出循环
        break
    except UnicodeDecodeError:
        # 如果当前编码失败，则打印错误信息并继续尝试下一个编码
        print(f"Failed to decode with {encoding}. Trying next encoding...")
else:
    # 如果所有编码都尝试过了还是失败，则打印最终错误信息
    print("Failed to decode the DBF file with any of the tried encodings.")