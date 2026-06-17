import os
import numpy as np
import pandas as pd
from io import BytesIO

from engine.db.oceanbase.ocean_base_db_util import OceanBaseDbUtil
from engine.db.oceanbase.ocean_base_file_gz_db_util import OceanBaseFileGZDbUtil
from engine.db.oceanbase.ocean_base_file_tzzj_db_util import OceanBaseFileTzzjDbUtil
from engine.db.oceanbase.ocean_base_file_rzqs_db_util import OceanBaseFileRzqsDbUtil
from ydbfdm import YDbfWriter
import engine.util.log as log


def export(context_instance):
    export_type = context_instance.get('[EXPORT_TYPE]')
    df = pd.DataFrame()
    if export_type == 'SQL':
        df = build_sql_dataframe(context_instance)
    file_export_fmt = context_instance.get('[FILE_EXPORT_FMT]')
    if file_export_fmt == 'DBF':
        export_dbf_file(df, context_instance)
    elif file_export_fmt == 'XLS':
        export_xls_file(df, context_instance)
    elif file_export_fmt == 'XLSX':
        export_xlsx_file(df, context_instance)
    else:
        pass


# 执行sql，并构造dataframe
def build_sql_dataframe(context_instance):
    sql = context_instance.get('[SQL_SCRIPT_CODE]')
    app = context_instance.get('[APP]')
    if app == 'file_gz':
        df = OceanBaseFileGZDbUtil.execute_query_sql_by_context_instance(sql, context_instance)
    elif app == 'file_tzzj':
        df = OceanBaseFileTzzjDbUtil.execute_query_sql_by_context_instance(sql, context_instance)
    elif app == 'file_rzqs':
        df = OceanBaseFileRzqsDbUtil.execute_query_sql_by_context_instance(sql, context_instance)
    return df


def _infer_dbf_fields(df):
    """
    根据DataFrame的列类型推断DBF字段定义。
    返回格式: [(field_name, field_type, field_length, decimal_count), ...]
    DBF字段类型: C(字符), N(数值), D(日期), F(浮点), L(逻辑)
    """
    fields = []
    for col_name in df.columns:
        col_name_upper = col_name.upper()
        dtype = df[col_name].dtype

        if pd.api.types.is_datetime64_any_dtype(dtype):
            # 判断该日期列是否包含时分秒信息
            if _has_time_component(df[col_name]):
                # 有时分秒 → 用C(字符)类型存储，格式 YYYYMMDDHHmmSS，14位
                fields.append((col_name_upper, 'C', 14, 0))
            else:
                # 纯日期 → 用D(日期)类型，8位 YYYYMMDD
                fields.append((col_name_upper, 'D', 8, 0))
        elif pd.api.types.is_bool_dtype(dtype):
            # 逻辑类型
            fields.append((col_name_upper, 'L', 1, 0))
        elif pd.api.types.is_integer_dtype(dtype):
            # 整数类型 → 使用N(数值)类型
            max_val = df[col_name].dropna().abs().max() if not df[col_name].dropna().empty else 0
            field_length = max(len(str(int(max_val))) + 1, 10)  # +1留给负号, 最小10位
            field_length = min(field_length, 20)  # DBF数值字段最大20位
            fields.append((col_name_upper, 'N', field_length, 0))
        elif pd.api.types.is_float_dtype(dtype):
            # 浮点类型 → 使用N(数值)类型
            max_val = df[col_name].dropna().abs().max() if not df[col_name].dropna().empty else 0
            decimal_count = _infer_decimal_count(df[col_name])
            int_part_len = max(len(str(int(max_val))) + 1, 5) if max_val > 0 else 2
            field_length = min(int_part_len + decimal_count + 1, 20)  # +1给小数点
            field_length = max(field_length, decimal_count + 2)  # 至少能放0.x
            fields.append((col_name_upper, 'N', field_length, decimal_count))
        else:
            # 字符串类型
            max_len = df[col_name].astype(str).str.len().max()
            field_length = max(int(max_len) if pd.notna(max_len) else 1, 1)
            field_length = min(field_length, 254)  # DBF字符字段最大254
            fields.append((col_name_upper, 'C', field_length, 0))

    return fields


def _infer_decimal_count(series):
    """推断浮点列的小数位数"""
    sample = series.dropna().head(1000)
    if sample.empty:
        return 2
    max_decimals = 0
    for val in sample:
        if isinstance(val, (float, np.floating)):
            str_val = f"{val:.10f}".rstrip('0')
            decimal_part = str_val.split('.')[-1]
            max_decimals = max(max_decimals, len(decimal_part))
        else:
            max_decimals = max(max_decimals, 2)
    return min(max(max_decimals, 2), 10)  # 默认最少2位, 最多10位小数


def _has_time_component(series):
    """
    判断日期列是否包含时分秒信息（即是否存在非 00:00:00 的时间）
    """
    non_null = series.dropna()
    if non_null.empty:
        return False
    # 只需检查是否存在任一值的时间部分不是 00:00:00
    sample = non_null.head(1000)
    has_time = sample.dt.hour.ne(0) | sample.dt.minute.ne(0) | sample.dt.second.ne(0)
    return has_time.any()


# 把dataframe 导出为一个dbf文件
def export_dbf_file(df, context_instance):
    """
    将DataFrame导出为DBF文件
    :param df: 要导出的DataFrame
    :param context_instance: 上下文实例，需要包含以下key:
        [TARGET_PATH] - 目标路径(目录)
        [EXPORT_FILE_NAME] - 导出文件名(不含扩展名)
        [FILE_EXPORT_FMT] - 导出文件格式
    """
    target_path = context_instance.get('[TARGET_PATH]')
    export_file_name = context_instance.get('[EXPORT_FILE_NAME]')
    file_export_fmt = context_instance.get('[FILE_EXPORT_FMT]')
    my_uuid = context_instance.get('[UUID]')

    # 构造完整的文件路径
    if not export_file_name.upper().endswith('.DBF'):
        export_file_name = export_file_name + '.DBF'
    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出DBF文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    # 如果DataFrame为空，创建空DBF文件
    if df is None or df.empty:
        log.info('UUID: %s, DataFrame为空，创建空DBF文件: %s', my_uuid, full_file_path)
        fields = [('EMPTY', 'C', 1, 0)]
        fh = BytesIO()
        dbf_writer = YDbfWriter(fh, fields, encoding='cp936')
        dbf_writer.write([])
        fh.seek(0)
        with open(full_file_path, 'wb') as f:
            f.write(fh.read())
        fh.close()
        return

    import time as _time
    start_time_total = _time.time()

    # 将列名统一转为大写（与项目中读DBF时的逻辑一致）
    df.columns = df.columns.str.upper()

    # 将NaN/None值替换为空字符串，否则YDbfWriter写入时会报错
    df = df.fillna('')

    # 日期列转换：有时分秒用YYYYMMDDHHmmSS(14位字符串)，纯日期用YYYYMMDD(8位字符串)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if _has_time_component(df[col]):
                df[col] = df[col].dt.strftime('%Y%m%d%H%M%S')
            else:
                df[col] = df[col].dt.strftime('%Y%m%d')

    # 推断DBF字段结构
    fields = _infer_dbf_fields(df)
    log.info('UUID: %s, 推断DBF字段结构: %s', my_uuid, fields)

    # 将DataFrame转为字典列表
    start_time = _time.time()
    records = df.to_dict(orient='records')
    log.info('UUID: %s, DataFrame转换成字典列表完成，耗时: %s s', my_uuid, _time.time() - start_time)

    # 写入内存
    fh = BytesIO()
    dbf_writer = YDbfWriter(fh, fields, encoding='cp936')
    start_time = _time.time()
    dbf_writer.write(records)
    log.info('UUID: %s, 写入内存数据完成，耗时: %s s', my_uuid, _time.time() - start_time)

    # 从内存写入磁盘
    fh.seek(0)
    start_time = _time.time()
    with open(full_file_path, 'wb') as f:
        f.write(fh.read())
    fh.close()
    log.info('UUID: %s, 写入磁盘完成，耗时: %s s', my_uuid, _time.time() - start_time)

    log.info('UUID: %s, 导出DBF文件完成: %s，总耗时: %s s', my_uuid, full_file_path, _time.time() - start_time_total)


def export_xls_file(df, context_instance):
    """
    将DataFrame导出为XLS文件。
    注意: 项目未安装xlwt依赖，XLS格式实际以XLSX格式写出(Excel可正常打开)。
    如需严格的XLS格式，请安装xlwt: pip install xlwt
    :param df: 要导出的DataFrame
    :param context_instance: 上下文实例，需要包含以下key:
        [TARGET_PATH] - 目标路径(目录)
        [EXPORT_FILE_NAME] - 导出文件名
        [FILE_EXPORT_FMT] - 导出文件格式
    """
    target_path = context_instance.get('[TARGET_PATH]')
    export_file_name = context_instance.get('[EXPORT_FILE_NAME]')
    my_uuid = context_instance.get('[UUID]')

    # 确保文件名以.xls结尾
    if not export_file_name.upper().endswith('.XLS'):
        export_file_name = export_file_name + '.xls'
    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出XLS文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    if df is None or df.empty:
        log.info('UUID: %s, DataFrame为空，创建空XLS文件: %s', my_uuid, full_file_path)
        pd.DataFrame().to_excel(full_file_path, index=False, engine='openpyxl')
        return

    import time as _time
    start_time_total = _time.time()

    try:
        import xlwt
        # 有xlwt，使用xlwt引擎写出标准XLS格式
        df.to_excel(full_file_path, index=False, engine='xlwt')
    except ImportError:
        # 没有xlwt，以XLSX格式写出（Excel可兼容打开）
        log.info('UUID: %s, 未安装xlwt，以XLSX格式写出文件(Excel可正常打开): %s', my_uuid, full_file_path)
        df.to_excel(full_file_path, index=False, engine='openpyxl')

    log.info('UUID: %s, 导出XLS文件完成: %s，总耗时: %s s', my_uuid, full_file_path, _time.time() - start_time_total)


def export_xlsx_file(df, context_instance):
    """
    将DataFrame导出为XLSX文件
    :param df: 要导出的DataFrame
    :param context_instance: 上下文实例，需要包含以下key:
        [TARGET_PATH] - 目标路径(目录)
        [EXPORT_FILE_NAME] - 导出文件名
        [FILE_EXPORT_FMT] - 导出文件格式
    """
    target_path = context_instance.get('[TARGET_PATH]')
    export_file_name = context_instance.get('[EXPORT_FILE_NAME]')
    my_uuid = context_instance.get('[UUID]')

    # 确保文件名以.xlsx结尾
    if not export_file_name.upper().endswith('.XLSX'):
        export_file_name = export_file_name + '.xlsx'
    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出XLSX文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    if df is None or df.empty:
        log.info('UUID: %s, DataFrame为空，创建空XLSX文件: %s', my_uuid, full_file_path)
        pd.DataFrame().to_excel(full_file_path, index=False, engine='openpyxl')
        return

    import time as _time
    start_time_total = _time.time()

    df.to_excel(full_file_path, index=False, engine='openpyxl')

    log.info('UUID: %s, 导出XLSX文件完成: %s，总耗时: %s s', my_uuid, full_file_path, _time.time() - start_time_total)
