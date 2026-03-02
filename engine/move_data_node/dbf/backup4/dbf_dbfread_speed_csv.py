
from dbfreaddm import DBF
import csv
import time


def dbf_to_csv(dbf_path, csv_path, encoding='gbk'):
    start_time = time.time()

    # 读取DBF文件
    table = DBF(dbf_path, encoding=encoding)

    # 写入CSV文件
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 写入表头
        writer.writerow(table.field_names)

        # 写入数据行
        for record in table:
            writer.writerow(list(record.values()))

    end_time = time.time()
    print(f'转换完成，耗时: {end_time - start_time:.2f}秒')
    print(f'记录数: {len(table)}')


# 使用示例
dbf_to_csv('test.dbf', 'output.csv')




