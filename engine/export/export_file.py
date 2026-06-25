import os
import numpy as np
import pandas as pd
from io import BytesIO
from engine.db.oceanbase.ocean_base_db_util import OceanBaseDbUtil
from ydbfdm import YDbfWriter
import engine.util.log as log


def export(context_instance):
    export_type = context_instance.get('[EXPORT_TYPE]')
    df = pd.DataFrame()
    if export_type == 'SQL':
        df = build_sql_dataframe(context_instance)
        log.info('Built SQL dataframe,记录数量：%s',len(df))


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
    # log.info("执行sql记录: app=%s, sql=%s",app,sql)
    df = OceanBaseDbUtil.execute_query_sql_by_context_instance_for_app(app, sql,context_instance)
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
            # 注意: DBF字段长度是字节数，中文在cp936下1个字符占2字节，必须按编码后的字节长度计算
            max_len = df[col_name].astype(str).map(lambda x: len(x.encode('cp936'))).max()
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


def _truncate_str_by_bytes(val, max_bytes, encoding='cp936'):
    """
    按字节长度截断字符串，确保编码后不超过max_bytes字节。
    YDbfWriter内部用val[:size]按字符截断，中文编码后会超出字段字节长度导致乱码，
    因此需要在此预先按字节截断。
    """
    if not val:
        return val
    encoded = val.encode(encoding)
    if len(encoded) <= max_bytes:
        return val
    # 逐字符截断，直到编码后字节数不超过max_bytes
    truncated = ''
    for ch in val:
        if len((truncated + ch).encode(encoding)) > max_bytes:
            break
        truncated += ch
    return truncated


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
    my_uuid = context_instance.get('[UUID]')

    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出DBF文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

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

    # 构建C类型字段的字节长度映射，用于预截断
    c_field_max_bytes = {}
    for name, typ, size, dec in fields:
        if typ == 'C':
            c_field_max_bytes[name] = size

    # 将DataFrame转为字典列表，并对C类型字段按字节长度预截断
    # 原因: YDbfWriter内部用val[:size]按字符截断，中文编码后会超出字段字节长度导致乱码
    start_time = _time.time()
    records = df.to_dict(orient='records')
    for rec in records:
        for field_name, max_bytes in c_field_max_bytes.items():
            val = rec.get(field_name)
            if val and isinstance(val, str):
                rec[field_name] = _truncate_str_by_bytes(val, max_bytes)
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


def _write_df_to_xls(df, file_path):
    """
    使用xlwt直接写出.xls格式文件（绕开pandas 2.x移除xlwt引擎的限制）
    :param df: DataFrame
    :param file_path: 输出文件路径
    """
    import xlwt
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('Sheet1')

    # 写表头
    for col_idx, col_name in enumerate(df.columns):
        sheet.write(0, col_idx, str(col_name))

    # 写数据行
    for row_idx, row in enumerate(df.itertuples(index=False), start=1):
        for col_idx, value in enumerate(row):
            if pd.isna(value):
                sheet.write(row_idx, col_idx, '')
            elif isinstance(value, (np.integer,)):
                sheet.write(row_idx, col_idx, int(value))
            elif isinstance(value, (np.floating,)):
                sheet.write(row_idx, col_idx, float(value))
            elif isinstance(value, (np.bool_,)):
                sheet.write(row_idx, col_idx, bool(value))
            elif isinstance(value, pd.Timestamp):
                if value.hour == 0 and value.minute == 0 and value.second == 0:
                    sheet.write(row_idx, col_idx, value.strftime('%Y-%m-%d'))
                else:
                    sheet.write(row_idx, col_idx, value.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                sheet.write(row_idx, col_idx, value)

    workbook.save(file_path)


def export_xls_file(df, context_instance):
    """
    将DataFrame导出为XLS文件(真正的.xls格式，使用xlwt直接写出)
    :param df: 要导出的DataFrame
    :param context_instance: 上下文实例，需要包含以下key:
        [TARGET_PATH] - 目标路径(目录)
        [EXPORT_FILE_NAME] - 导出文件名
        [FILE_EXPORT_FMT] - 导出文件格式
    """
    target_path = context_instance.get('[TARGET_PATH]')
    export_file_name = context_instance.get('[EXPORT_FILE_NAME]')
    my_uuid = context_instance.get('[UUID]')

    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出XLS文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    import time as _time
    start_time_total = _time.time()
    _write_df_to_xls(df, full_file_path)

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


    full_file_path = os.path.join(target_path, export_file_name)

    log.info('UUID: %s, 开始导出XLSX文件: %s', my_uuid, full_file_path)

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    import time as _time
    start_time_total = _time.time()

    df.to_excel(full_file_path, index=False, engine='openpyxl')

    log.info('UUID: %s, 导出XLSX文件完成: %s，总耗时: %s s', my_uuid, full_file_path, _time.time() - start_time_total)



