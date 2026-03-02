

import os
import time
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd

import dbf



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

# file_path_and_name = "/Users/douming/Downloads/中泰文件拆分慢/SJSMX1.DBF"
# destination_file_path_and_name  = "/Users/douming/Downloads/中泰文件拆分慢_publish_pdf/BELONG_NOT_FOUND/SJSMX1_split.DBF"
file_path_and_name = "../SJSMX1.DBF"
destination_file_path_and_name  = "SJSMX1_split.DBF"
file_encoding = 'gbk'
table = DBFREAD_DBF(file_path_and_name, encoding=file_encoding)
start_time = time.time()
print(f"读取文件 {file_path_and_name}开始。")
whole_dbf = pd.DataFrame(iter(table))
end_time = time.time()
print(f"读取文件 {file_path_and_name}转换为DataFrame， 耗时 {end_time - start_time} 秒。")
whole_dbf.columns = whole_dbf.columns.str.upper()
uuid = "123-456"

dataframe_for_one_belong = whole_dbf
delete_existing_file(destination_file_path_and_name)
create_empty_dbf_file_if_not_exist(file_path_and_name, destination_file_path_and_name)


dest_table = dbf.Table(destination_file_path_and_name, codepage='cp936')
try:
    dest_table.open(mode=dbf.READ_WRITE)
    # 批量写入优化 - 使用extend方法
    batch_size = 10000  # 可根据实际情况调整
    total_rows = len(dataframe_for_one_belong)
    start_time = time.time()
    # 将DataFrame转换为元组列表
    records = [tuple(row) for row in dataframe_for_one_belong.itertuples(index=False)]
    end_time = time.time()
    print(f"DataFrame转换为元组列表， 耗时 {end_time - start_time} 秒。")
    total_start_time = time.time()
    index = 0
    start_time = time.time()
    for one_record in records:
        dest_table.append(one_record)
        if index % batch_size == 0:  # 减少日志频率
            print(f"{index}/{total_rows} ，耗时 {time.time() - start_time} 秒。")
            start_time = time.time()
        index += 1

except Exception as e:
    print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 失败。失败原因：{e}")
finally:
    # 关闭文件
    dest_table.close()

print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - total_start_time} 秒。")
