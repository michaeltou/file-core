from dbfreaddm import DBF


if __name__ == "__main__":
    # 定义 DBF 文件路径
    dbf_file_path = 'SJSMX1.DBF'

    # 打开 DBF 文件
    table = DBF(dbf_file_path)

    fields = []
    for field in table.fields:
        field_name = field.name
        field_type = field.type
        field_length = field.length
        # 对于数值类型，decimal_count 才有意义，其他类型默认为 0
        if field_type == 'N':
            decimal_count = field.decimal_count
        else:
            decimal_count = 0
        fields.append((field_name, field_type, field_length, decimal_count))

    print(fields)