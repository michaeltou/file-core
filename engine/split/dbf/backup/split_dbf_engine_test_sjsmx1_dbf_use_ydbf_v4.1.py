

import os
import time
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd

import dbf


from io import BytesIO

from ydbfdm import YDbfWriter

def delete_existing_file(dst_file):
    # 如果文件存在，则先删除，防止数据重复写入
    if os.path.exists(dst_file):
        os.remove(dst_file)


def create_empty_dbf_file_if_not_exist(src_file, dst_file):
    """
     如果不存在，则创建相同结构的空DBF文件
    :param src_file:
    :param dst_file:
    :return:
    """
    # 判断文件是否存在,
    if os.path.exists(dst_file):
        return
    # 如果文件不存在，则创建空文件
    with dbf.Table(src_file) as src:
        src.open()
        dst = src.new(dst_file)
        dst.open()
        # do something
        dst.close()

def get_dbf_fields(dbf_file_path_and_name,encoding='gbk'):
    # 打开 DBF 文件
    table = DBFREAD_DBF(dbf_file_path_and_name,encoding=encoding)

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
    return fields

# file_path_and_name = "/Users/douming/Downloads/中泰文件拆分慢/SJSMX1.DBF"
# destination_file_path_and_name  = "/Users/douming/Downloads/中泰文件拆分慢_publish_pdf/BELONG_NOT_FOUND/SJSMX1_split.DBF"
file_path_and_name = "../SJSMX1.DBF"
destination_file_path_and_name  = "SJSMX1_split.DBF"
file_encoding = 'gbk'
total_start_time = time.time()
table = DBFREAD_DBF(file_path_and_name, encoding=file_encoding)

print(f"读取文件 {file_path_and_name}开始。")
print('读取DBF文件，转换成list-开始')
start_time = time.time()
# 将 DBF 数据转换为列表，每个元素是一个字典，表示一行数据
data = list(table)
print('读取DBF文件，转换成list-结束,耗时：',time.time() - start_time,'秒')
start_time = time.time()
# 将列表数据转换为 DataFrame
whole_dbf = pd.DataFrame(data)

print('读取DBF文件，转换成DataFrame-结束,耗时：',time.time() - start_time,'秒')


whole_dbf.columns = whole_dbf.columns.str.upper()
uuid = "123-456"

dataframe_for_one_belong = whole_dbf
delete_existing_file(destination_file_path_and_name)
create_empty_dbf_file_if_not_exist(file_path_and_name, destination_file_path_and_name)





# 批量写入优化 - 使用extend方法
batch_size = 10000  # 可根据实际情况调整
total_rows = len(dataframe_for_one_belong)
start_time = time.time()
# # 将DataFrame转换为元组列表
# records = [tuple(row) for row in dataframe_for_one_belong.itertuples(index=False)]

# 将 DataFrame 按行转换为字典列表
records = dataframe_for_one_belong.to_dict(orient='records')

end_time = time.time()
print(f"DataFrame转换为字典列表， 耗时 {end_time - start_time} 秒。")


# 获取字段结构
fields = get_dbf_fields(file_path_and_name)
# 创建 BytesIO 对象
fh = BytesIO()
# 创建 DBFWriter 对象
dbf_writer = YDbfWriter(fh, fields, encoding='cp936')
print('dbf_writer写入内存数据开始')
start_time = time.time()
# 保存 DBF 文件
dbf_writer.write(records)
print('dbf_writer写入内存数据结束，耗时', time.time() - start_time, '秒。')
bytes_io = fh
# 将文件指针移动到开头，以便后续读取内容
bytes_io.seek(0)
print('开始将内存数据写入文件-开始')
start_time = time.time()
# 以二进制写入模式打开文件并将 BytesIO 中的内容写入文件
with open(destination_file_path_and_name, 'wb') as file:
    # 读取 BytesIO 中的所有内容并写入文件
    file.write(bytes_io.read())
print('开始将内存数据写入文件-结束,耗时', time.time() - start_time, '秒。')
# 关闭 BytesIO 对象
bytes_io.close()

print(f"数据已成功写入 {destination_file_path_and_name}")



print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - total_start_time} 秒。")
