
from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd
import engine.util.log as log
from engine.split.core.split_engine import split_dataframe
import dbfdm as dbf



def delete_existing_file(dst_file):
    # 如果文件存在，则先删除，防止数据重复写入
    if os.path.exists(dst_file):
        os.remove(dst_file)

def get_field_names_with_case(file_path_and_name):
    table = DBFREAD_DBF(file_path_and_name, encoding="gbk")
    # 获取原始列名（保留大小写）
    original_columns = table.field_names
    return original_columns

def get_field_name_dict_with_case(file_path_and_name):
    table = DBFREAD_DBF(file_path_and_name, encoding="gbk")
    # 获取原始列名（保留大小写）
    original_column_name_dict = { field_name.upper():field_name  for field_name in  table.field_names }
    return original_column_name_dict

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
        print(src.field_names)
        dst = src.new(dst_file)
        dst.open()
        # do something here
        dst.close()


def modify_column_names(file_path_and_name, rename_dict):
    dbf_table = dbf.Table(file_path_and_name, codepage='cp936')
    try:
        dbf_table.open(mode=dbf.READ_WRITE)
        for old_name, new_name in rename_dict.items():
            dbf_table.rename_field(old_name, new_name)


    except Exception as e:
        print(f"uuid:{uuid},修改文件 {file_path_and_name} 列名称失败。失败原因：{e}")
    finally:
        # 关闭文件
        dbf_table.close()



file_path_and_name = "/Users/douming/Documents/读数工具重构/文件/测试文件/0126_0000_20180418_1_Trade.DBF"
destination_file_path_and_name  = "/Users/douming/Documents/读数工具重构/文件/测试文件/0126_0000_20180418_1_Trade_publish.DBF"
file_encoding = 'gbk'
table = DBFREAD_DBF(file_path_and_name, encoding=file_encoding)

whole_dbf = pd.DataFrame(iter(table))
whole_dbf.columns = whole_dbf.columns.str.upper()
uuid = "123-456"

dataframe_for_one_belong = whole_dbf

file_encoding = 'cp936'

delete_existing_file(destination_file_path_and_name)
create_empty_dbf_file_if_not_exist(file_path_and_name, destination_file_path_and_name)

start_time = time.time()
'''写入文件
另外：'cp936'：这是 Windows 系统中用于中文的编码，
它等同于 GBK 编码。GBK 是在 GB2312 基础上扩展的中文编码，支持更多的中文字符，包括繁体字等。
在 dbf 库中使用 'cp936' 可以很好地处理中文数据。
'''
dest_table = dbf.Table(destination_file_path_and_name, codepage='cp936')
try:
    dest_table.open(mode=dbf.READ_WRITE)

    # 批量写入优化 - 使用extend方法
    batch_size = 10  # 可根据实际情况调整
    total_rows = len(dataframe_for_one_belong)
    # 将DataFrame转换为元组列表
    records = [tuple(row) for row in dataframe_for_one_belong.itertuples(index=False)]

    # 分批次写入
    for i in range(0, total_rows, batch_size):
        start_time = time.time()
        batch = records[i:i + batch_size]
        for record in batch:  # 改为逐条append
            dest_table.append(record, multiple=True)


        if i % (batch_size * 1) == 0:  # 减少日志频率
            end_time = time.time()
            print(f"uuid:{uuid},写入文件 {destination_file_path_and_name},记录数:{i + batch_size}, 进度：{i + batch_size}/{total_rows},耗时 {end_time - start_time} 秒。")

    # dest_table.rename_field('USERID', 'USERID_new')


except Exception as e:
    print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 失败。失败原因：{e}")
finally:
    # 关闭文件
    dest_table.close()


field_name_dict = get_field_name_dict_with_case(file_path_and_name)
modify_column_names(destination_file_path_and_name, field_name_dict)


print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")
