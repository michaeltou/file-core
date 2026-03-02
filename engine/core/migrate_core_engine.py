import time

from engine.db.oceanbase.ocean_base_db_util import OceanBaseDbUtil
from engine.db.oracle_read_tool_db_util import *

from engine.filter.filter_engine import FilterEngine
from engine.mapping.field_mapping import FieldMapping
from engine.cnst.InvokeMode import InvokeMode
from engine.clean.clean_engine import CleanEngine

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from engine.cnst.FieldType import *
import engine.util.log as log




class MigrateCoreEngine(object):
    def __init__(self):
        pass

    def dataframe_to_oracle(self, flow_node_config, dataframe_view,
                            filter_logic, target_interface_table,
                            field_mapping_config_list, context_instance):
        """
        将dataframe数据插入oracle数据库
        核心流程
        1: 过滤数据
        2: 处理字段映射
        3: 写入oracle数据库
        """

        if target_interface_table is None or target_interface_table == '':
            raise Exception("target_interface_table不能为空")

        # 获取到sqlalchemy的engine对象
        # oracle_engine = OracleConnectionPool.get_engine()
        start_time = time.time()

        end_time = time.time()
        log.info("获取oracle engine耗时：%s 秒", end_time - start_time)

        # 复制一份dataFrame数据，防止上游传过来的dataframe_view是视图，直接修改视图会导致SettingWithCopyWarning错误。
        df = dataframe_view.copy()

        my_uuid = context_instance.get('[UUID]')
        # log.info("uuid: %s,过滤前，要处理的dataFrame的记录数：%s", my_uuid,df.shape[0])

        # 导入文件前，执行清理逻辑
        CleanEngine.process_clean_before_import(flow_node_config, context_instance)


        # 1 处理过滤逻辑
        df = FilterEngine.process_filter(df, filter_logic, context_instance)
        log.info("uuid: %s,过滤后，要处理的dataFrame的记录数：%s", my_uuid, df.shape[0])
        if df.empty:
            log.info("uuid: %s,过滤后，没有数据需要继续处理", my_uuid)
            return

        # 2 处理字段映射
        target_df = FieldMapping.process_field_mapping(df, field_mapping_config_list, context_instance)

        # 校验文件,如果校验不通过，则直接抛出异常，不再进行后续处理。
        # 放在加工逻辑后面，原因：按照加工逻辑后的字段值进行比较。
        # 比如 FXFSRQ设置为字符串类型，日期字符串字段的校验写法：FXFSRQ != '[BUSINESS_DATE]'，
        # check_file(flow_node_config, df, context_instance)

        start_time = time.time()
        # target_interface_table = flow_node_dbf_config['targetIntfTbl']
        # 将自动名称转成小写，能提高写入速度。
        # 原因：
        # 如果是小写 构造的sql语句为 insert into talbe_name.
        # 如果是大写 构造的sql语句为 insert into ”TABLE_NAME“，sqlalchemy会自动加上双引号。 双引号会慢，影响写入速度。
        #
        target_interface_table = target_interface_table.lower()

        dtype_dict = {}
        for column in target_df.columns:
            if target_df[column].dtype in ['int', 'int64']:
                dtype_dict[column] = Integer
            elif target_df[column].dtype in ['object', 'bool']:
                dtype_dict[column] = String(2000)
            elif target_df[column].dtype in ['float', 'float64']:
                dtype_dict[column] = Float
            else:
                pass

        if target_df.empty:
            print("没有数据需要写入数据库")
        else:
            invoke_mode = context_instance.get('[INVOKE_MODE]')
            # target_df = target_df.fillna('')
            # 处理空值
            target_df = target_df.replace({'nan': None})
            target_df = target_df.replace({'None': None})
            target_df = target_df.replace({np.nan: None})

            # if 'COMMENT' in df.columns:
            #     # COMMENT大写为oracle关键字，修改为小写可正常insert数据
            #     target_df = target_df.rename(columns={'COMMENT': 'comment'})
            # if 'BY' in df.columns:
            #     # COMMENT大写为oracle关键字，修改为小写可正常insert数据
            #     target_df = target_df.rename(columns={'BY': 'by'})
            #     log.info('进入了by字段的处理')
            # 根据数据量动态设置chunksize
            data_size = len(target_df)
            if data_size > 50000:
                db_insert_chunk_size = 3000
            elif data_size > 30000:
                db_insert_chunk_size = 2000
            else:
                db_insert_chunk_size = 1000

            # oracle_engine = get_global_engine()
            ocean_base_engine = OceanBaseDbUtil.get_engine();

            if invoke_mode == InvokeMode.NORMAL.value:
                # 普通模式下，将dataFrame数据插入数据库
                target_df.to_sql(target_interface_table, con=ocean_base_engine, if_exists='append',
                                 dtype=dtype_dict,
                                 index=False, chunksize=db_insert_chunk_size)
            elif invoke_mode == InvokeMode.TEST_WRITE_TO_DB.value:
                # 普通模式下，将dataFrame数据插入数据库
                target_df.to_sql(target_interface_table, con=ocean_base_engine, if_exists='append',
                                 dtype=dtype_dict,
                                 index=False, chunksize=db_insert_chunk_size)
                # 测试模式下，将DataFrame返回部分数据到上下文中，方便测试
                df_head = target_df.head(10)
                df_head_copy = formate_datetime_column(df_head, field_mapping_config_list)

                # 将DataFrame转换为字典列表
                data_list = df_head_copy.to_dict(orient='records')
                context_instance.set('[__DATA_LIST__]', data_list)
                context_instance.set('[__FIELD_NAME_LIST__]', df_head_copy.columns.tolist())
            elif invoke_mode == InvokeMode.TEST_NO_WRITE_TO_DB.value:
                # 测试模式下，将DataFrame返回部分数据到上下文中，方便测试
                df_head = target_df.head(10)
                df_head_copy = formate_datetime_column(df_head, field_mapping_config_list)

                # 将DataFrame转换为字典列表
                data_list = df_head_copy.to_dict(orient='records')
                context_instance.set('[__DATA_LIST__]', data_list)
                context_instance.set('[__FIELD_NAME_LIST__]', df_head_copy.columns.tolist())

            #  节点导入完成后，执行后置sql
            CleanEngine.execute_end_sql_after_import(flow_node_config, context_instance)

            end_time = time.time()

            execution_time = end_time - start_time
            log.info("uuid: %s, 进程ID:%s,插入数据库总耗时：%s 秒,记录数:%s", my_uuid,os.getpid(),execution_time,len(target_df))


def formate_datetime_column(df_head, field_mapping_config_list):
    # Create a copy of df_head
    df_head_copy = df_head.copy()

    # 处理日期格式化
    for field_mapping_item in field_mapping_config_list:
        target_field = field_mapping_item['targetField']
        field_type = field_mapping_item.get('fieldType')
        format_arg = field_mapping_item.get('dateFormat')

        if field_type == FieldType.DATETIME.value:
            # 将日期列应用格式化函数
            df_head_copy[target_field] = df_head_copy[target_field].apply(lambda x: format_date(x, format_arg))

    return df_head_copy


def format_date(date, format_arg):
    if date is None:
        return None
    return date.strftime(format_arg)  # 这里指定了日期格式





