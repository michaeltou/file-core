from engine.core.migrate_core_engine import *
from dbfreaddm import DBF as DBFREAD_DBF
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql
import dbfdm as dbf
from engine.util.redis.redis_util import RedisUtil
import engine.util.log as log
import re
from lxml import etree
import engine.split.record as record
from engine.db.oracle_gz_get_all_product_util import execute_gz_query_sql
from engine.db.oracle_auto_get_all_product_util import execute_auto_query_sql
from io import BytesIO

from ydbfdm import YDbfWriter
from simpledbfdm import Dbf5
import os
import time
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd
import engine.util.log as log
from engine.split.core.split_engine import split_dataframe
import dbf


def get_dbf_fields(dbf_file_path_and_name,encoding='gbk'):
    # 打开 DBF 文件
    table = DBFREAD_DBF(dbf_file_path_and_name,encoding=encoding)

    fields = []
    for field in table.fields:
        # 把字段名称转为大写，因为dataframe的列名全部转为大写，所以这里也统一转为大写. 最后会有逻辑把dbf文件列名称改成原始大小写。
        field_name = field.name.upper()
        field_type = field.type
        field_length = field.length
        # 对于数值类型，decimal_count 才有意义，其他类型默认为 0
        if field_type == 'N':
            decimal_count = field.decimal_count
        else:
            decimal_count = 0
        fields.append((field_name, field_type, field_length, decimal_count))
    return fields



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


def delete_existing_file(dst_file):
    # 如果文件存在，则先删除，防止数据重复写入
    if os.path.exists(dst_file):
        os.remove(dst_file)


if __name__ == '__main__':

    uuid = "123-456"
    # file_path_and_name ="/Users/douming/Documents/采集发布/中泰证券-现场文件/20250417/交易数据/GH.DBF"
    # destination_file_path_and_name = "/Users/douming/Documents/采集发布/中泰证券-现场文件_publish/GH/GH.DBF"

    # file_path_and_name ="/Users/douming/Documents/采集发布/中泰证券-现场文件/20250417/交易数据/rzrq_dzls_20250417.DBF"
    # destination_file_path_and_name = "/Users/douming/Documents/采集发布/中泰证券-现场文件_publish/GH/rzrq_dzls_20250417_publish.DBF"

    file_path_and_name ="/Users/douming/Documents/采集发布/中泰证券-现场文件/20250417/交易数据/rzrq_jyls_20250417.DBF"
    destination_file_path_and_name = "/Users/douming/Documents/采集发布/中泰证券-现场文件_publish/rzrq_jyls/rzrq_jyls_20250417_publish.DBF"


    destination_path = os.path.dirname(destination_file_path_and_name)

    if not os.path.exists(destination_path):
        # 如果不存在则创建目录
        os.makedirs(destination_path)
    delete_existing_file(destination_file_path_and_name)
    create_empty_dbf_file_if_not_exist(file_path_and_name, destination_file_path_and_name)
    file_encoding = "gbk"
    context_instance = Context()
    try:
        my_dbf = Dbf5(file_path_and_name, codec=file_encoding)
        field_objects = my_dbf.fields  # 获取字段对象列表
        # 获取原始列名字典{大写列名称：原始列名称（保留大小写）}
        original_column_name_dict = {field[0].upper(): field[0] for field in field_objects}
        context_instance.set('original_column_name_dict', original_column_name_dict)
        log.info(f"uuid:{uuid} 使用simpledbf库读取dbf文件,转成dataframe开始")
        start_time = time.time()
        whole_dbf = my_dbf.to_dataframe()
        end_time = time.time()
        log.info(f"uuid:{uuid} 使用simpledbf库读取dbf文件,转成dataframe结束,转换耗时:{end_time - start_time}秒")
        # 这里把dataframe的列名全部转为大写，因为发现同一个文件名称的dbf文件还存在大小写不一致的情况。这里统一转为大写后，再拆分字段设置和sql变量里面，都统一使用大写的字段名。
        whole_dbf.columns = whole_dbf.columns.str.upper()

    except AssertionError as e:  # 如果出现这个错误，说明使用simpledbf读取dbf文件出现问题,尝试使用dbfread库读取dbf文件
        table = DBFREAD_DBF(file_path_and_name, encoding=file_encoding)
        # 获取原始列名字典{大写列名称：原始列名称（保留大小写）}
        original_column_name_dict = {field_name.upper(): field_name for field_name in table.field_names}
        context_instance.set('original_column_name_dict', original_column_name_dict)
        log.info(f"uuid:{uuid} 使用dbfread库读取dbf文件,转成dataframe开始")
        start_time = time.time()
        whole_dbf = pd.DataFrame(iter(table))
        log.info(f"uuid:{uuid} 使用dbfread库读取dbf文件,转成dataframe结束,转换耗时:{time.time() - start_time}秒")
        # 这里把dataframe的列名全部转为大写，因为发现同一个文件名称的dbf文件还存在大小写不一致的情况。这里统一转为大写后，再拆分字段设置和sql变量里面，都统一使用大写的字段名。
        whole_dbf.columns = whole_dbf.columns.str.upper()


    total_start_time = time.time()

    dataframe_for_one_belong = whole_dbf


    start_time = time.time()
    log.info(f"uuid:{uuid},  {destination_file_path_and_name} 转换成字典列表-开始。")
    # 将 DataFrame 按行转换为字典列表
    dataframe_for_one_belong = dataframe_for_one_belong.fillna('')
    records = dataframe_for_one_belong.to_dict(orient='records')
    log.info(f"uuid:{uuid},  {destination_file_path_and_name} 转换成字典列表-结束。耗时 {time.time() - start_time} 秒。")
    # 获取字段结构
    fields = get_dbf_fields(file_path_and_name )
    # 创建 BytesIO 对象
    fh = BytesIO()
    # 创建 DBFWriter 对象
    dbf_writer = YDbfWriter(fh, fields, encoding='cp936')
    log.info(f"uuid:{uuid},  {destination_file_path_and_name} 写入内存数据-开始。")
    start_time = time.time()
    # 保存 DBF 文件
    dbf_writer.write(records)
    log.info(f"uuid:{uuid},  {destination_file_path_and_name} 写入内存数据-结束。耗时 {time.time() - start_time} 秒。")
    bytes_io = fh
    # 将文件指针移动到开头，以便后续读取内容
    bytes_io.seek(0)

    log.info(f"uuid:{uuid},  将文件{destination_file_path_and_name} 从内存写入磁盘-开始")
    start_time = time.time()
    # 以二进制写入模式打开文件并将 BytesIO 中的内容写入文件
    with open(destination_file_path_and_name, 'wb') as file:
        # 读取 BytesIO 中的所有内容并写入文件
        file.write(bytes_io.read())
        log.info(f"uuid:{uuid},  将文件{destination_file_path_and_name} 从内存写入磁盘-结束,耗时 {time.time() - start_time} 秒。")
        # 关闭 BytesIO 对象
        bytes_io.close()


    log.info(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - total_start_time} 秒。")


