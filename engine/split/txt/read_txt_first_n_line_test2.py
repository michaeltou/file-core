def get_txt_column_count(file_path, skip_rows, encoding='gbk'):
    total_column_count = 0
    try:
        with open(file_path, 'r', encoding=file_encoding) as file:
            for i, line in enumerate(file):
                if i <= skip_rows:
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


if __name__ == '__main__':
    file_encoding = 'gbk'
    total_column_count_result = get_txt_column_count('SettlementDetail_has_header_sep.txt', 3, file_encoding)
    print(total_column_count_result)
