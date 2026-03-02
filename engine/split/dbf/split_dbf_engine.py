
from simpledbfdm import Dbf5
import os
import time
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd
import engine.util.log as log
from engine.split.core.split_engine import split_dataframe
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


def split_fast():
    file_path_and_name = "/Users/douming/Downloads/中泰文件拆分慢/SJSMX1.DBF"
    destination_file_path_and_name = "/Users/douming/Downloads/中泰文件拆分慢_publish_pdf/BELONG_NOT_FOUND/SJSMX1_split.DBF"
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

        for i in range(0, total_rows, batch_size):
            batch_start_time = time.time()
            batch = records[i:i + batch_size]
            for record in batch:
                dest_table.append(record)
            batch_end_time = time.time()
            progress = i + batch_size if i + batch_size <= total_rows else total_rows
            print(f"uuid:{uuid},{progress}/{total_rows}, 耗时{batch_end_time - batch_start_time}秒")

    except Exception as e:
        print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 失败。失败原因：{e}")
    finally:
        # 关闭文件
        dest_table.close()

    print(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")
# 拆分单个dbf文件
def split_dbf_file(rule_id, file_split_rule, file_path_and_name_dto, context_instance):
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')
    file_encoding = file_split_rule.get('encoding')
    if file_encoding is None or len(file_encoding) == 0:
        file_encoding = 'gbk'
    if file_path_and_name is None or not os.path.exists(file_path_and_name):
        log.error(f"文件 {file_path_and_name} 不存在。")
        return
    my_uuid = context_instance.get('[UUID]')
    ######-----------
    # 快速拆分测试-这个方法拆分很快
    # split_fast()
    ######-----------
    try:
        my_dbf = Dbf5(file_path_and_name, codec=file_encoding)
        field_objects = my_dbf.fields  # 获取字段对象列表
        # 获取原始列名字典{大写列名称：原始列名称（保留大小写）}
        original_column_name_dict = {field[0].upper(): field[0] for field in field_objects}
        context_instance.set('original_column_name_dict', original_column_name_dict)
        log.info(f"uuid:{my_uuid} 使用simpledbf库读取dbf文件,转成dataframe开始")
        start_time = time.time()
        whole_dbf = my_dbf.to_dataframe()
        end_time = time.time()
        log.info(f"uuid:{my_uuid} 使用simpledbf库读取dbf文件,转成dataframe结束,转换耗时:{end_time-start_time}秒")
        # 这里把dataframe的列名全部转为大写，因为发现同一个文件名称的dbf文件还存在大小写不一致的情况。这里统一转为大写后，再拆分字段设置和sql变量里面，都统一使用大写的字段名。
        whole_dbf.columns = whole_dbf.columns.str.upper()
        # 发起dataframe的拆分
        split_dataframe(whole_dbf, file_path_and_name_dto, file_split_rule, context_instance)

    except AssertionError as e:  # 如果出现这个错误，说明使用simpledbf读取dbf文件出现问题,尝试使用dbfread库读取dbf文件
        table = DBFREAD_DBF(file_path_and_name, encoding=file_encoding)
        # 获取原始列名字典{大写列名称：原始列名称（保留大小写）}
        original_column_name_dict = {field_name.upper(): field_name for field_name in table.field_names}
        context_instance.set('original_column_name_dict', original_column_name_dict)
        log.info(f"uuid:{my_uuid} 使用dbfread库读取dbf文件,转成dataframe开始")
        start_time = time.time()
        whole_dbf = pd.DataFrame(iter(table))
        log.info(f"uuid:{my_uuid} 使用dbfread库读取dbf文件,转成dataframe结束,转换耗时:{time.time()-start_time}秒")
        # 这里把dataframe的列名全部转为大写，因为发现同一个文件名称的dbf文件还存在大小写不一致的情况。这里统一转为大写后，再拆分字段设置和sql变量里面，都统一使用大写的字段名。
        whole_dbf.columns = whole_dbf.columns.str.upper()
        # 发起dataframe的拆分
        split_dataframe(whole_dbf, file_path_and_name_dto, file_split_rule, context_instance)

