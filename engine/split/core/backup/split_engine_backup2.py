
from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
import engine.util.config as config
from dbfreaddm import DBF as DBFREAD_DBF
import pandas as pd
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql
import dbfdm as dbf
from engine.util.redis.redis_util import RedisUtil
import engine.util.log as log
import re
from lxml import etree
import engine.split.record as record
from engine.db.oracle_gz_get_all_product_util import *


def split_dataframe(df, file_path_and_name_dto, file_split_rule, context_instance):
    my_uuid = context_instance.get('[UUID]')

    """
     将dataframe 进行分组，并进行拆分，然后将每个分组的dataframe进行归属分类，每个归属的dataframe写入文件。
    :param df:
    :param file_path_and_name_dto:
    :param file_split_rule:
    :param context_instance:
    :return:
    """

    # 最终的按照归属分组的dataframe字典，key为归属值，value为dataframe格式的记录
    final_df_dict_for_belong = {}

    '''
        使用场景：即每个归属，都有自己的上下文。构造一个以分组为key，value为Context实例的字典。
        目前有的上下文内容包含：BELONG_VALUE(即归属值),归属sql查询的所有列值列表（格式为：列名称：列值），
        路径上的[]通配符（to be added)，文件名称上的[]+捕获组（to be added）。
   '''
    context_dict_for_belong = {}

    # 用于存储按照分组字段进行分组后的dataframe字典
    grouped_df_dict = {}

    # [通用逻辑] 按照分组字段进行分组，构造分组字典
    make_group_for_dataframe(df, file_split_rule, grouped_df_dict)

    log.info(f"uuid:{my_uuid},按照拆分字段进行分组，分组个数为：{len(grouped_df_dict)}")
    ''' 
      遍历分组的dataframe=grouped_df_dict字典,进行处理，生成最终的dataframe=final_df_dict_for_belong。
     grouped_df_dict里面的个数会和final_df_dict_for_belong的个数会不一样，
     因为有些分组的dataframe有相同的归属，就需要进行合并。
    '''
    log.info(f"uuid:{my_uuid},为每个归属构建一个dataframe开始")
    start_time = time.time()
    for group_field_name_tuple_value, group_df_item in grouped_df_dict.items():
        # [通用逻辑] 1、构造一个分组的dataframe字段，key为归属，value为dataframe，2、同时把对应的上下文记录在context_dict_for_belong中
        build_final_df_dict_and_context_for_belong(group_field_name_tuple_value,
                                                   group_df_item,
                                                   file_split_rule,
                                                   file_path_and_name_dto,
                                                   final_df_dict_for_belong,
                                                   context_dict_for_belong,
                                                   context_instance)
    end_time = time.time()
    log.info(f"uuid:{my_uuid},为每个归属构建一个dataframe结束，文件中的归属总数量是：{len(final_df_dict_for_belong)}个, 耗时{end_time - start_time}秒")

    # 是否要拆空文件开关
    split_empty_file_for_none_belong = config.get_config_value('split.split_empty_file_for_none_belong')
    # 如果为True，则拆分一个空文件（即对于全量归属中，不在文件中的归属，增加一个空的dataframe到final_df_dict_for_belong中.）
    if split_empty_file_for_none_belong:
        log.info(f"uuid:{my_uuid},执行拆分空文件逻辑，对于全量归属中，不在文件中的归属，增加一个空的dataframe到final_df_dict_for_belong中.")
        # [通用逻辑] 对于在全量归属中，不在文件中的归属，增加一个空的dataframe到final_df_dict_for_belong中
        add_empty_df_to_final_df_dict_for_belong(file_split_rule,
                                                 file_path_and_name_dto,
                                                 final_df_dict_for_belong,
                                                 context_dict_for_belong
                                                 )

    log.info(f"uuid:{my_uuid},将分组好的dataframe,总共拆分为{len(final_df_dict_for_belong)}个文件，写入文件-start")
    start_time = time.time()
    #  [通用逻辑+ 不同文件类型逻辑] 将分组好的dataframe字典，写入文件
    write_to_file_for_dataframe(final_df_dict_for_belong,
                                file_path_and_name_dto,
                                file_split_rule,
                                context_dict_for_belong,
                                context_instance)
    end_time = time.time()
    log.info(f"uuid:{my_uuid},将分组好的dataframe,总共拆分为{len(final_df_dict_for_belong)}个文件，"
             f"总耗时{end_time - start_time}秒，写入文件-end")

    belong_not_found_df = final_df_dict_for_belong.get('BELONG_NOT_FOUND')
    if belong_not_found_df is not None and not belong_not_found_df.empty:
        len_of_belong_not_found_df = len(belong_not_found_df)
        record.insert_exception_log(my_uuid, file_path_and_name_dto, file_split_rule, 1,
                                    f"存在无法找到归属的记录，总记录有:{len_of_belong_not_found_df}")

    total_multi_belong_count = context_instance.get('[MULTI_BELONG_COUNT]')
    if total_multi_belong_count is not None and total_multi_belong_count > 0:
        record.insert_exception_log(my_uuid, file_path_and_name_dto, file_split_rule, 2,
                                    f"存在多归属的记录，总记录有:{total_multi_belong_count}")

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


def create_empty_xml_file_if_not_exist(src_file, dst_file, file_encoding):
    """
     如果不存在，则创建相同结构的空xml文件
    :param src_file:
    :param dst_file:
    :return:
    """
    # 判断文件是否存在,
    if os.path.exists(dst_file):
        return
    # 如果文件不存在，则创建空文件
    with open(dst_file, 'w', encoding=file_encoding) as file:
        pass


def create_empty_txt_file_if_not_exist(src_file, dst_file, file_encoding):
    """
     如果不存在，则创建相同结构的空txt文件
    :param src_file:
    :param dst_file:
    :param file_encoding:
    :return:
    """
    # 判断文件是否存在,
    if os.path.exists(dst_file):
        return
    # 如果文件不存在，则创建空文件
    with open(dst_file, 'w', encoding=file_encoding) as file:
        pass


# 写入文件 追加写入
def write_to_file_for_dbf(destination_file_path_and_name, dataframe_for_one_belong, file_split_rule, uuid):
    if dataframe_for_one_belong is None or dataframe_for_one_belong.empty:
        log.info(f"uuid:{uuid},写入空文件 {destination_file_path_and_name} 完成。耗时 0 秒。")
        return

    file_encoding = file_split_rule.get('encoding')
    # 在 dbf 库中使用 'cp936' 处理中文数据
    if file_encoding == 'gbk':
        file_encoding = 'cp936'
    if file_encoding is None or len(file_encoding) == 0:
        file_encoding = 'cp936'

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
        batch_size = 10000  # 可根据实际情况调整
        total_rows = len(dataframe_for_one_belong)
        start_time = time.time()
        # 将DataFrame转换为元组列表
        records = [tuple(row) for row in dataframe_for_one_belong.itertuples(index=False)]
        end_time = time.time()
        print(f"DataFrame转换为元组列表， 耗时 {end_time - start_time} 秒。")


        index = 0
        start_time = time.time()
        for one_record in records:
            dest_table.append(one_record)
            if index % batch_size == 0:  # 减少日志频率
                print(f"{index}/{total_rows} ，耗时 {time.time() - start_time} 秒。")
                start_time = time.time()
            index += 1


    except Exception as e:
        log.error(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 失败。失败原因：{e}")
    finally:
        # 关闭文件
        dest_table.close()

    log.info(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")


# 写入文件 追加写入
def write_to_file_for_xml(destination_file_path_and_name, dataframe_for_one_belong, file_split_rule, context_instance, file_encoding):
    interface_id = file_split_rule.get('interfaceId')
    elect_check_xml_interface_id_list_str = config.get_config_value('split.elect_check_xml_interface_id_list')
    elect_check_xml_interface_id_list = elect_check_xml_interface_id_list_str.split(',')
    # xml 文件格式千奇百怪（不像dbf，txt等文件有固定规律可以进行抽象），目前只碰到一个xml接口，所以这里按照接口ID来区分，进行定制化拆分。
    if interface_id in elect_check_xml_interface_id_list:
        # 构造上下文实例
        result_dict = context_instance.get('result_dict')

        uuid = context_instance.get('[UUID]')
        if dataframe_for_one_belong is None or dataframe_for_one_belong.empty:
            log.info(f"uuid:{uuid},写入空文件 {destination_file_path_and_name} 完成。耗时0秒。")
            return
        start_time = time.time()

        # 创建根元素
        root = etree.Element("clear-data")
        # 创建子元素
        response_node = etree.SubElement(root, "response")
        response_node.set("errno", "0")    # 添加属性
        response_node.set("info", "导出成功")    # 添加属性
        # 创建子元素
        resultsum_node = etree.SubElement(root, "resultsum")
        resultsum_node.set("count", str(len(result_dict)))  # 添加属性

        for key, value in result_dict.items():
            result_name = key
            result_attr = value
            query_condition = f'tag_name == "{result_name}"'
            dataframe_for_one_result_type = dataframe_for_one_belong.query(query_condition)

            # 创建子元素
            result_node = etree.SubElement(root, "result")
            result_node.set("name", result_name)  # 添加属性
            result_node.set("description", result_attr.get("description"))  # 添加属性
            result_node.set("count", str(len(dataframe_for_one_result_type)))  # 添加属性

            for index, row in dataframe_for_one_result_type.iterrows():
                # 创建子元素
                result_item_node = etree.SubElement(result_node, result_name)
                attrib_str = row['attrib_str']
                attrib_dict = eval(attrib_str)
                # 将字典的所有值赋给节点的属性
                for attr_key, attr_value in attrib_dict.items():
                    result_item_node.set(attr_key, attr_value)

        # 将 XML 写入文件
        with open(destination_file_path_and_name, "wb") as f:
            f.write(etree.tostring(root, pretty_print=True, encoding=file_encoding))

        log.info(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")


def write_header_lines_to_file(lines, output_file_path, encoding='gbk'):
    """
    将行数据写入到指定的文件中。
    :param lines: 要写入的行数据列表
    :param output_file_path: 输出文件的路径
    :param encoding: 文件编码，默认为 'gbk'
    """
    with open(output_file_path, 'w', encoding=encoding) as file:
        for line in lines:
            file.write(line)


# 写入文件 追加写入
def write_to_file_for_txt(destination_file_path_and_name,
                          dataframe_for_one_belong, file_encoding,
                          uuid, context_instance):
    if dataframe_for_one_belong is None or dataframe_for_one_belong.empty:
        log.info(f"uuid:{uuid},写入空文件 {destination_file_path_and_name} 完成。耗时0秒。")
        return
    start_time = time.time()
    column_position_list = ['LINE']
    # 获取需要删除的列名
    columns_to_drop = [col for col in dataframe_for_one_belong.columns if col not in column_position_list]
    # 删除指定列
    dataframe_for_one_belong = dataframe_for_one_belong.drop(columns=columns_to_drop)

    file_header_lines = context_instance.get('file_header')
    if file_header_lines is not None and len(file_header_lines) > 0:
        # 把文件头部非数据部分写入文件
        write_header_lines_to_file(file_header_lines, destination_file_path_and_name, file_encoding)

    # 新增写入逻辑
    try:
        # 获取 LINE 列数据并写入文件
        dataframe_for_one_belong['LINE'].to_csv(
            destination_file_path_and_name,
            sep='\n',  # 使用换行符作为分隔符
            header=False,  # 不写入列名
            index=False,  # 不写入索引
            mode='a',  # 追加模式
            encoding=file_encoding,  # 保持与创建文件时一致的编码
            na_rep=''  # 空值替换为空字符串
        )
    except KeyError:
        log.error(f"uuid:{uuid},写入文件中不存在 LINE 列: {destination_file_path_and_name}")
    except Exception as e:
        log.error(f"uuid:{uuid},写入文件失败: {destination_file_path_and_name}, 错误: {str(e)}")

    log.info(f"uuid:{uuid},写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")


def make_group_for_dataframe(df, file_split_rule, grouped_df_dict):
    """
    将dataframe 按照分组字段进行分组，并放入grouped_df_dict字典中
    :param df: dataframe数据
    :param file_split_rule: 文件拆分规则
    :param grouped_df_dict: 分组好的dataframe字典，key为分组值，value为dataframe格式的记录
    :return:
    """
    # 拆分字段列表，分号分割，格式为 字段名称:所在列:所在位置 ,
    # 例如：F1:1:;F2:2:;F3:3: 或者F1::POSITION(1,2);F2::POSITION(3,2) '''
    file_split_field_list = file_split_rule.get('fileSplitFieldList')
    # dbf只需设置字段名称即可，当为DBF文件时，file_split_field_list的格式为  F1::;F2::;F3::  ['F1::','F2::','F3::']
    field_compose_list = file_split_field_list.split(';')

    # 最终使用的分组字段名称列表,举例：['GBLB'], 或者['F1','F2','F3']，即按照这些字段进行分组进行文件拆分
    group_field_name_list = [item.split(':')[0] for item in field_compose_list]

    # 根据分组列的列表，进行分组，支持多个字段进行分组。 例如：['Name', 'Age']
    grouped_chunk = df.groupby(group_field_name_list)

    # 这里的group_field_name_tuple_value是一个tuple，表示分组的字段值，例如（'张三', '25'）
    for group_field_name_tuple_value, group_df_item in grouped_chunk:
        # 构造一个分组号的dataframe字段，key为字段名称，value为dataframe
        grouped_df_dict[group_field_name_tuple_value] = group_df_item
    # print(f"分组字段：{group_field_name_list}，分组数量：{len(grouped_df_dict)}")


def add_empty_df_to_final_df_dict_for_belong(file_split_rule,
                                             file_path_and_name_dto,
                                             final_df_dict_for_belong,
                                             context_dict_for_belong):
    """
     获取全量归属，对于在文件中没有的归属，则增加一个空的dataframe到final_df_dict_for_belong中，后面只需要创建一个空文件即可
    :param file_split_rule:  文件拆分规则
    :param file_path_and_name_dto: 文件路径和名称DTO
    :param final_df_dict_for_belong: 最终的按照归属分组的dataframe字典，key为归属值，value为dataframe格式的记录
    :param context_dict_for_belong: 上下文字典
    :return:
    """

    all_belong_df = pd.DataFrame()
    # 从配置获取全量归属的sql
    get_all_belong_sql = config.get_config_value('split.get_all_belong_sql')

    all_belong_redis_key = get_all_belong_sql
    all_belong_value = RedisUtil.get_string(all_belong_redis_key)
    if all_belong_value is None or all_belong_value == '':
        # 获取所有归属，并缓存到redis
        all_belong_df = get_all_belong(get_all_belong_sql)
        # 获取第一列数据
        first_column = all_belong_df.iloc[:, 0]

        # 将第一列数据转换为以逗号分割的字符串
        all_belong_value = ','.join(map(str, first_column))
        # 缓存到redis，缓存时间为1天
        RedisUtil.set_string(all_belong_redis_key, all_belong_value, 60 * 60 * 24 * 1)
    else:
        all_belong_df = pd.DataFrame(all_belong_value.split(','), columns=['ALL_BELONG_VALUE'])

    if all_belong_df is None or all_belong_df.empty:
        return

    # 获取第一列的列名（ 默认第一列为归属字段）
    first_column_name = all_belong_df.columns[0]
    # 获取第一列的列值(即多个归属值) 转成list
    all_belong_value_list = all_belong_df[first_column_name].tolist()
    # 获取文件路径上下文
    file_path_context = file_path_and_name_dto.get('filePathContext')
    for belong_value in all_belong_value_list:
        # 判断belong_value 是否在final_df_dict_for_belong中，
        # 如果不在，则加入一个空的dataframe，后面只需要创建一个空文件即可
        # 如果存在，则不处理
        if belong_value not in final_df_dict_for_belong:
            final_df_dict_for_belong[belong_value] = pd.DataFrame()
            # 构造上下文
            # 构造某个归属的上下文实例 start
            context_instance_for_one_belong = Context()
            context_instance_for_one_belong.set('[BELONG_VALUE]', belong_value)

            # 将路径上下文添加到归属上下文实例中
            for key, value in file_path_context.items():
                context_instance_for_one_belong.set(key, value)
            ''' 
                key为归属值，value为上下文实例。这个字典context_dict_for_belong会在后续文件拆分时使用。
            '''
            context_dict_for_belong[belong_value] = context_instance_for_one_belong


def build_final_df_dict_and_context_for_belong(group_field_name_tuple_value,
                                               group_df_item,
                                               file_split_rule,
                                               file_path_and_name_dto,
                                               final_df_dict_for_belong,
                                               context_dict_for_belong,
                                               context_instance
                                               ):
    """
     构造最终的dataframe字典（final_df_dict_for_belong）和上下文字典 context_dict_for_belong
    :param group_field_name_tuple_value:
    :param group_df_item:
    :param file_split_rule:
    :param file_path_and_name_dto:
    :param final_df_dict_for_belong:
    :param context_dict_for_belong:
    :param context_instance:
    :return:
    """
    file_path_context = file_path_and_name_dto.get('filePathContext')

    # 拆分字段定位类型  1：按分隔符拆分，2：按位置拆分
    split_field_type = file_split_rule.get('splitFieldType')
    # 分隔符
    split_separator = file_split_rule.get('splitSeparator')

    # 拆分字段列表，分号分割，格式为 字段名称:所在列:所在位置 ,
    # 例如：F1:1:;F2:2:;F3:3: 或者F1::POSITION(1,2);F2::POSITION(3,2) '''
    file_split_field_list = file_split_rule.get('fileSplitFieldList')
    # dbf只需设置字段名称即可，当为DBF文件时，file_split_field_list的格式为  F1::;F2::;F3::
    # ['F1::','F2::','F3::']
    field_compose_list = file_split_field_list.split(';')

    # 最终使用的分组字段名称列表,举例：['GBLB'], 或者['F1','F2','F3']，即按照这些字段进行分组进行文件拆分
    group_field_name_list = [item.split(':')[0] for item in field_compose_list]


    # 分组上下文，仅用于sql执行
    group_context_instance = Context()
    '''
    group_field_name_list 和group_field_name_tuple_value 组成一个新的dict，作为上下文参数
    group_field_name_list 举例： ['name', 'age']， 
    group_field_name_tuple_value 举例：('张三', '25')
    dict(zip(group_field_name_list, group_field_name_tuple_value)) 后结果为 {'name': '张三', 'age': '25'}
    '''
    field_name_and_value_dict = dict(zip(group_field_name_list, group_field_name_tuple_value))
    for key, value in field_name_and_value_dict.items():
        group_context_instance.set(key, str(value))

    belong_df = pd.DataFrame()
    # 文件获取归属类型 1 执行sql 2 拆分字段
    file_get_belong_type = file_split_rule.get('fileGetBelongType')
    # 1 执行sql 2 拆分字段
    if file_get_belong_type == 1:
        # 获取sql语句  文件获取归属sql
        # file_get_belong_sql = "SELECT 'fund_id_1' as fund_id ,'func_code_2' as fund_code  from dual"
        file_get_belong_sql = file_split_rule.get('fileGetBelongSql')
        # 获取归属，1：执行sql 2：字段即归属
        # 根据分组的字段值，执行sql，获取归属。
        belong_df = execute_get_belong_sql(file_get_belong_sql, group_context_instance)
    # 1 执行sql 2 拆分字段
    elif file_get_belong_type == 2:
        # 将字典包装在列表中创建单行DataFrame
        df = pd.DataFrame([field_name_and_value_dict])
        # file_get_belong_expression = df['F1'] + df['F2']
        file_get_belong_expression = file_split_rule.get('fileGetBelongExpression')
        # 最终字符串是：df['BELONG_VALUE'] = df['F1'] + df['F2']
        file_get_belong_expression = "df['BELONG_VALUE'] = " + file_get_belong_expression
        exec(file_get_belong_expression)
        # 将 BELONG_VALUE 列移动到第一列，主要目的：后面默认第一列为归属字段
        if 'BELONG_VALUE' in df.columns:
            col = df.pop('BELONG_VALUE')  # 移除该列
            df.insert(0, 'BELONG_VALUE', col)  # 插入到第一列
        belong_df = df

    # 获取归属的记录数
    record_count = len(belong_df)

    #  1、获取到一个归属 ，正常处理
    if record_count == 1:
        # 默认第一列为归属字段，由于这里是只有一条记录，所以取第一行第一列即可
        belong_value = belong_df.iat[0, 0]

        previous_group_df_item = final_df_dict_for_belong.get(belong_value)
        # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
        # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
        concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
        final_df_dict_for_belong[belong_value] = concat_group_df

        # 构造某个归属的上下文实例 start
        context_instance_for_one_belong = Context()
        context_instance_for_one_belong.set('[BELONG_VALUE]', belong_value)
        all_column_list = belong_df.columns.tolist()
        # 构造某个分组的上下文实例,把归属的附带列值也添加到上下文实例中
        for column_name in all_column_list:
            column_value = belong_df[column_name].iat[0]  # 因为只有一行记录，所以取第一行即可
            context_instance_for_one_belong.set(column_name, column_value)

        # 将路径上下文添加到归属上下文实例中
        for key, value in file_path_context.items():
            context_instance_for_one_belong.set(key, value)
        # 把字段的名称和值也添加到上下文实例中
        for key, value in field_name_and_value_dict.items():
            context_instance_for_one_belong.set(key, value)
        ''' 
            key为归属值，value为上下文实例。这个字典context_dict_for_belong会在后续文件拆分时使用。
        '''
        context_dict_for_belong[belong_value] = context_instance_for_one_belong

        # 构造某个归属的上下文实例 end
    #  2、获取不到归属，把这类数据统一放到无归属的dataframe中，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
    elif record_count == 0:
        # 1 进行拆分(统一归属到"无归属"文件中) 2 不进行拆分(跳过这些记录，不处理)
        no_belong_process_tag = file_split_rule.get('noBelongProcessTag')
        if no_belong_process_tag == 1:
            previous_group_df_item = final_df_dict_for_belong.get('BELONG_NOT_FOUND')
            concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
            final_df_dict_for_belong['BELONG_NOT_FOUND'] = concat_group_df

            # 构造某个归属的上下文实例 start
            # 无归属的场景，也构造一个分组的上下文实例，并添加到分组上下文字典context_dict_for_belong中
            context_instance_for_one_belong = Context()
            context_instance_for_one_belong.set('[BELONG_VALUE]', 'BELONG_NOT_FOUND')
            # 将路径上下文添加到归属上下文实例中
            for key, value in file_path_context.items():
                context_instance_for_one_belong.set(key, value)

            # 把字段的名称和值也添加到上下文实例中
            for key, value in field_name_and_value_dict.items():
                context_instance_for_one_belong.set(key, value)

            context_dict_for_belong['BELONG_NOT_FOUND'] = context_instance_for_one_belong
        elif no_belong_process_tag == 2:
            pass
        # 构造某个归属的上下文实例 end
    #  3、获取到多个归属，拆分为多个归属文件，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
    elif record_count > 1:
        # 1 进行拆分(归属到多个归属文件中) 2 不进行拆分(跳过这些记录，不处理)
        multi_belong_process_tag = file_split_rule.get('multiBelongProcessTag')

        # 当值为1，进行拆分(归属到多个归属文件中)
        if multi_belong_process_tag == 1:
            # 获取第一列的列名（ 默认第一列为归属字段）
            first_column_name = belong_df.columns[0]
            # 获取第一列的列值(即多个归属值) 转成list
            belong_value_list = belong_df[first_column_name].tolist()

            previous_multi_belong_count = context_instance.get('[MULTI_BELONG_COUNT]')
            current_multi_belong_count = len(group_df_item)
            if previous_multi_belong_count is None:
                previous_multi_belong_count = 0
            # 计算总的多归属数量
            total_multi_belong_count = current_multi_belong_count + previous_multi_belong_count
            context_instance.set('[MULTI_BELONG_COUNT]', total_multi_belong_count)

            for index, belong_value in enumerate(belong_value_list):
                previous_group_df_item = final_df_dict_for_belong.get(belong_value)
                # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
                # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
                concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                final_df_dict_for_belong[belong_value] = concat_group_df

                # 构造某个归属的上下文实例 start
                context_instance_for_one_belong = Context()
                context_instance_for_one_belong.set('[BELONG_VALUE]', belong_value)
                all_column_list = belong_df.columns.tolist()
                # 构造某个归属的上下文实例
                for column_name in all_column_list:
                    column_value = belong_df[column_name].iat[index]
                    context_instance_for_one_belong.set(column_name, column_value)

                # 将路径上下文添加到归属上下文实例中
                for key, value in file_path_context.items():
                    context_instance_for_one_belong.set(key, value)

                # 把字段的名称和值也添加到上下文实例中
                for key, value in field_name_and_value_dict.items():
                    context_instance_for_one_belong.set(key, value)
                ''' 
                    key为归属值，value为上下文实例。这个字典context_dict_for_belong会在后续文件拆分时使用。
                '''
                context_dict_for_belong[belong_value] = context_instance_for_one_belong
                # 构造某个归属的上下文实例
        # 当值为2，不进行拆分(跳过这些记录，不处理)
        elif multi_belong_process_tag == 2:
            pass

    # 其他情况，无需处理
    else:
        pass


def write_to_file_for_dataframe(final_df_dict_for_belong,
                                file_path_and_name_dto,
                                file_split_rule,
                                context_dict_for_belong,
                                context_instance):
    my_uuid = context_instance.get('[UUID]')
    """
         将final_df_dict_for_belong 写入文件

        :param final_df_dict_for_belong: dataframe字典，key为归属值，value为dataframe格式的记录
        :param file_path_and_name_dto:  文件名称和路径DTO
        :param file_split_rule:   文件拆分规则
        :param context_dict_for_belong:  归属上下文字典，key为归属值，value为上下文实例
        :param context_instance: 上下文实例
        :return:
    """
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')
    file_type = file_split_rule.get('fileType')
    # 发布路径
    file_publish_path = file_split_rule.get('filePublishPath')

    # 拆分文件名类型 1 使用源文件名称 2 自定义文件名称
    file_publish_name_type = file_split_rule.get('filePublishNameType')
    # 发布文件名, 支持变量替换
    file_publish_name = file_split_rule.get('filePublishName')

    # 获取文件名
    source_file_name = os.path.basename(file_path_and_name)
    # print(f"来源文件名是: {source_file_name}")

    # 遍历final_group_df_dict，写入dbf文件
    for belong_value, df_for_one_belong in final_df_dict_for_belong.items():
        df_for_one_belong = df_for_one_belong.replace({'nan': None})
        df_for_one_belong = df_for_one_belong.replace({'None': None})
        df_for_one_belong = df_for_one_belong.replace({np.nan: None})

        # 获取目标文件路径
        # 目标文件路径file_publish_path做上下文替换  context_instance_for_one_belong
        # context_instance_for_one_belong 为Context实例，里面包含了归属值、附带列值、路径上下文等信息
        context_instance_for_one_belong = context_dict_for_belong.get(belong_value)

        # dest_file_path 举例： /Users/douming/temp/publish/[YYYYMMDD]/[BELONG_VALUE]/[机构代码]
        dest_file_path = file_publish_path
        dest_file_path = replace_file_path_context(dest_file_path, context_instance_for_one_belong)

        # 获取目标文件名  1 使用源文件名称 2 自定义文件名称
        if file_publish_name_type == 1:
            dest_file_name = source_file_name
        elif file_publish_name_type == 2:
            # 自定义文件名
            dest_file_name = file_publish_name
        else:
            dest_file_name = source_file_name
        # 将文件名称中的上下文进行替换
        dest_file_name = replace_file_name_context(dest_file_name, context_instance_for_one_belong)

        # 构造文件名
        dest_file_path_and_name = os.path.join(dest_file_path, dest_file_name)
        if not os.path.exists(dest_file_path):
            # 如果不存在则创建目录
            os.makedirs(dest_file_path)

        file_encoding = file_split_rule.get('encoding')
        if file_encoding is None or len(file_encoding) == 0:
            file_encoding = 'gbk'

        log.info(f"uuid:{my_uuid},开始写入文件,文件路径是 {dest_file_path_and_name}.....")
        # 删除已存在的文件，防止多次发起拆分，写入重复的数据。
        delete_existing_file(dest_file_path_and_name)

        if file_type.upper() == 'DBF':
            # 如果文件不存在，则创建空文件
            create_empty_dbf_file_if_not_exist(file_path_and_name, dest_file_path_and_name)
            # 写入文件,追加写入
            write_to_file_for_dbf(dest_file_path_and_name, df_for_one_belong, file_split_rule, my_uuid)
            modify_column_names(file_path_and_name, dest_file_path_and_name, my_uuid)
        elif file_type.upper() == 'TXT':
            # 如果文件不存在，则创建空文件
            create_empty_txt_file_if_not_exist(file_path_and_name, dest_file_path_and_name, file_encoding)
            # 写入文件,追加写入
            write_to_file_for_txt(dest_file_path_and_name, df_for_one_belong, file_encoding, my_uuid, context_instance)
        elif file_type.upper() == 'XML':
            # 如果文件不存在，则创建空文件
            create_empty_xml_file_if_not_exist(file_path_and_name, dest_file_path_and_name, file_encoding)
            # 写入文件,追加写入
            write_to_file_for_xml(dest_file_path_and_name, df_for_one_belong,
                                  file_split_rule, context_instance, file_encoding)

# 将拆分后的dbf文件的列名称修改为原始列名（保留大小写）
def modify_column_names(src_file_path_and_name, dest_file_path_and_name, uuid):
    # 例如:rename_dict =  {'ZQDM': 'zqdm', 'CLIENTID': 'clientid'}
    rename_dict = get_field_name_dict_with_case(src_file_path_and_name)

    dbf_table = dbf.Table(dest_file_path_and_name, codepage='cp936')
    try:
        dbf_table.open(mode=dbf.READ_WRITE)
        for old_name, new_name in rename_dict.items():
            if old_name == new_name:
                continue
            # 重命名字段. 这个dbf库是被douming修改优化后的库，可以支持大小写敏感的重命名字段，原来是重命名会把字段名称改成大写。
            dbf_table.rename_field(old_name, new_name)
    except Exception as e:
        log.error(f"uuid:{uuid},修改文件 {dest_file_path_and_name} 列名称失败。失败原因：{e}")
    finally:
        # 关闭文件
        dbf_table.close()

# 获取dbf文件中的列名，并返回一个字典，key为原始列名变成大写的格式，value为原始列名（保留大小写）
# 例如:{'ZQDM': 'zqdm', 'CLIENTID': 'clientid'}
def get_field_name_dict_with_case(file_path_and_name):
    table = DBFREAD_DBF(file_path_and_name, encoding="gbk")
    # 获取原始列名（保留大小写）
    original_column_name_dict = { field_name.upper():field_name  for field_name in  table.field_names }
    return original_column_name_dict

def replace_file_path_context(file_path, context_instance):
    """
    替换文件路径中的参数，例如：/Users/douming/temp/publish/[YYYYMMDD]/[机构代码]
    替换成：/Users/douming/temp/publish/20210801/000001
    """
    used_param_list_in_file_path = get_used_simple_param_list(file_path)
    if used_param_list_in_file_path:
        for param_item in used_param_list_in_file_path:
            context_param_key = '[' + param_item + ']'
            context_param_value = context_instance.get(context_param_key)
            file_path = file_path.replace(context_param_key, str(context_param_value))

    return file_path


def replace_file_name_context(file_name, context_instance):
    """
    1、 当使用自定义文件名称时，支持的通配符包含:<br>
       [YYYYMMDD],
       [拆分字段名称],[BELONG_VALUE],
       资讯商[资讯商],产品代码[产品代码],产品名称[产品名称],账套编号[账套编号],
       机构代码[机构代码],机构名称[机构名称],文件类型[文件类型]
   2、  替换文件路径中的参数，例如：TEST[YYYYMMDD]_[机构代码]_[BELONG_VALUE].TXT
        替换成： TEST20210801_100001_XXXX1.TXT
   3、   这个YYYYMMDD从路径上获取的。
    """
    used_param_list_in_file_path = get_used_simple_param_list(file_name)
    if used_param_list_in_file_path:
        for param_item in used_param_list_in_file_path:
            context_param_key = '[' + param_item + ']'
            context_param_value = context_instance.get(context_param_key)
            file_name = file_name.replace(context_param_key, str(context_param_value))

    return file_name


def get_used_simple_param_list(file_path):
    """
    获取路径中的参数列表，例如：/Users/douming/temp/publish/[YYYYMMDD]/[机构代码]
    返回匹配的列表：['YYYYMMDD', '机构代码']
    """
    pattern = r'[^\[]{0,}\[{1}([\w.]+)\]{1}'
    matches = re.findall(pattern, file_path)
    if matches:
        return matches
    else:
        return None


# 获取某个归属
def execute_get_belong_sql(sql, context_instance):
    # 将[变量名称] 替换为 :变量名称
    final_sql = replace_sql(sql, context_instance)
    # param_dict是个字典，里面包含了所有变量和参数，刚好可以传给sql语句
    params = context_instance.gen_simple_context_dict()
    # 执行sql语句
    df = execute_query_sql(final_sql, params)
    return df


# 获取所有归属
def get_all_belong(get_all_belong_sql):
    params = None
    # 执行sql语句
    df = execute_get_all_product_query_sql(get_all_belong_sql, params)
    return df

def test():
    # 测试用例
    file_path = '/Users/douming/temp/publish/[YYYYMMDD]/[机构代码]/'
    file_path = replace_file_path_context(file_path, {'[YYYYMMDD]': '20210801', '[机构代码]': '000001'})
    print(file_path)



if __name__ == '__main__':
    test()