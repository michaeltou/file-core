import time

from engine.cnst.FieldType import *
from engine.cnst.ProcessLogicType import *
from engine.db.oracle_read_tool_db_util import *
from datetime import datetime
import pandas as pd
import engine.util.log as log

class ProcessEngine:
    def __init__(self):
        pass

    @staticmethod
    def process_process_logic(context_instance,df, source_field, process_logic, process_logic_type, field_type, date_format):
        process_start_time = time.time()
        my_uuid = context_instance.get('[UUID]')


        # # 1 对dataFrame进行预处理（按照类型进行转换，去除空格，按照时间格式进行转换）
        if field_type == FieldType.DECIMAL.value:
            df[source_field] = pd.to_numeric(df[source_field], errors='coerce')
        elif field_type == FieldType.STRING.value:
            if process_logic is not None and 'keep_original_space' in process_logic:
                # 保留原始空格
                df[source_field] = df[source_field].astype(str)
            else:
                # 去除空格 - 优化：先判断类型避免重复转换
                if df[source_field].dtype != object:
                    df[source_field] = df[source_field].astype(str)
                df[source_field] = df[source_field].str.strip()
        if field_type == FieldType.DATETIME.value:
            date_start_time =  time.time()
            # 转成字符串
            #df[source_field] = df[source_field].astype(str).str.strip()
            # 把'nan'字符串，转成空字符串
            df[source_field] = df[source_field].replace('nan', None)
            # app_start_time = time.time()
            # 按照指定格式，进行日期转换
            # df[source_field] = df[source_field].apply(my_parse_date, point_format=date_format)
            # app_end_time = time.time()
            # log.info('UUID: %s,字段 %s apply 日期转换耗时：%s s', my_uuid, source_field, app_end_time-app_start_time)

            try:
                datetime_start_time = time.time()
                # 先按照字符串的方式和指定的格式，进行数据转换
                # df[source_field] = pd.to_datetime(df[source_field])
                df[source_field] = pd.to_datetime(df[source_field], format='mixed', errors='coerce')

                datetime_end_time = time.time()
                log.info('UUID: %s,字段 %s to_datetime 日期转换耗时：%s s', my_uuid, source_field, datetime_end_time-datetime_start_time)
            except ValueError as e:
                # 如果转换失败，则按照混合格式进行转换（自动失败日期格式，如果无法转换，则会置为空）
                df[source_field] = pd.to_datetime(df[source_field], format='mixed', errors='coerce')

            date_end_time = time.time()
            log.info('UUID: %s,字段 %s 的日期转换耗时：%s s', my_uuid, source_field, date_end_time-date_start_time)


            # try:
            #     # 先按照字符串的方式和指定的格式，进行数据转换
            #      df[source_field] = pd.to_datetime(df[source_field], format=date_format)
            # except ValueError as e:
            #     # 如果转换失败，则按照混合格式进行转换（自动失败日期格式，如果无法转换，则会置为空）
            #     df[source_field] = pd.to_datetime(df[source_field], format='mixed', errors='coerce')


        # 2 再根据配置的[加工逻辑]对原始dataFrame的字段进行处理
        if process_logic_type is None or process_logic is None or process_logic.strip() == '':  # 没有配置加工逻辑，直接返回
            return

        if 'keep_original_space' in process_logic:
            pass
        else:
            if process_logic_type == ProcessLogicType.SIMPLE.value:
                dynamic_process_logic = process_logic.replace('$', 'x')
                df[source_field] = df[source_field].apply(lambda x: eval(dynamic_process_logic))
            elif process_logic_type == ProcessLogicType.ORIGINAL.value:
                exec(process_logic)
            else:
                raise RuntimeError("未知的加工逻辑类型")

        process_end_time = time.time()
        log.info('UUID: %s,字段 %s 的加工逻辑耗时：%s s', my_uuid, source_field, process_end_time-process_start_time)


# 能自动失败日期格式，如果无法转换，则会置为空字符串
def my_parse_date(date_str, point_format='%Y-%m-%d'):
    try:
        # 1、先使用指定的格式解析日期字符串
        date_obj = datetime.strptime(date_str, point_format)
        return date_obj
    except (ValueError, TypeError):
        # 2、如果解析失败，则尝试使用预定义的日期格式列表进行解析
        # 预定义常见日期格式列表
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
        ]
        for fmt in date_formats:
            try:
                # 尝试使用当前格式解析日期字符串
                date_obj = datetime.strptime(date_str, fmt)
                # 如果解析成功，则返回日期对象
                return date_obj
            except (ValueError, TypeError):
                # 如果解析失败，则尝试下一个格式
                continue
        return None

if __name__ == '__main__':
    my_date_str = '2024-01-01'
    my_date_obj = my_parse_date(my_date_str)
    my_date_obj = pd.to_datetime(my_date_obj)
    print(my_date_obj)
