

import os
import time
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd

import dbf

from engine.split.dbf.backup.part1.dftodbf import dbfwrite


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

total_start_time = time.time()

dbfwrite(dataframe_for_one_belong, destination_file_path_and_name)


print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - total_start_time} 秒。")
