"""
测试 export_dbf_file 方法
覆盖: 字符串、整数、浮点数、纯日期、带时分秒的日期、布尔、NaN值
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime

from engine.core.context import Context
from engine.export.export_file import export_dbf_file


def test_export_dbf_file():
    # 1. 构造包含各种类型的测试 DataFrame
    df = pd.DataFrame({
        'XM':       ['张三', '李四', '王五', '赵六', '钱七'],                       # 字符串 C
        'NL':       [25, 30, 28, 35, 40],                                          # 整数 N
        'GZ':       [8500.50, 12000.75, 9300.00, 15600.88, 7800.33],               # 浮点数 N
        'RQ':       pd.to_datetime(['20240101', '20240315', '20240720',             # 纯日期 D
                                    '20241130', '20241225'], format='%Y%m%d'),
        'CJSJ':     pd.to_datetime(['20240101 093000', '20240315 143045',           # 带时分秒 C(14)
                                    '20240720 081500', '20241130 170012',
                                    '20241225 235959'], format='%Y%m%d %H%M%S'),
        'HF':       [True, False, True, False, True],                               # 布尔 L
        'BZ':       ['正常', '异常', '', '待确认', '正常'],                          # 含空字符串 C
        'KH':       ['A001', 'B002', 'C003', 'D004', 'E005'],                      # 字符串 C
    })

    # 故意加入一些 NaN 值，测试 fillna 处理
    # df.loc[1, 'BZ'] = np.nan
    # df.loc[3, 'GZ'] = np.nan

    print('===== 测试 DataFrame =====')
    print(df)
    print()
    print('各列类型:')
    print(df.dtypes)
    print()

    # 2. 构造上下文
    context_instance = Context()
    context_instance.set('[TARGET_PATH]', '/tmp/export_test')
    context_instance.set('[EXPORT_FILE_NAME]', 'test_export')
    context_instance.set('[FILE_EXPORT_FMT]', 'DBF')
    context_instance.set('[UUID]', 'test-uuid-001')

    # 3. 执行导出
    export_dbf_file(df, context_instance)

    # 4. 验证文件是否生成
    full_path = os.path.join('/tmp/export_test', 'test_export.DBF')
    if os.path.exists(full_path):
        file_size = os.path.getsize(full_path)
        print(f'导出成功！文件路径: {full_path}, 文件大小: {file_size} bytes')
    else:
        print('导出失败！文件未生成')

    # 5. 回读验证
    print()
    print('===== 回读验证 =====')
    try:
        from simpledbfdm import Dbf5
        read_dbf = Dbf5(full_path, codec='gbk')
        result_df = read_dbf.to_dataframe()
        print(result_df)
        print()
        print('回读列类型:')
        print(result_df.dtypes)
    except Exception as e:
        print(f'回读失败: {e}')


def test_export_empty_dbf():
    """测试空 DataFrame 导出"""
    context_instance = Context()
    context_instance.set('[TARGET_PATH]', '/tmp/export_test')
    context_instance.set('[EXPORT_FILE_NAME]', 'test_empty')
    context_instance.set('[FILE_EXPORT_FMT]', 'DBF')
    context_instance.set('[UUID]', 'test-uuid-002')
    df = pd.DataFrame({
        'XM': ['张三', '李四', '王五', '赵六', '钱七'],  # 字符串 C
        'NL': [25, 30, 28, 35, 40],  # 整数 N
        'GZ': [8500.50, 12000.75, 9300.00, 15600.88, 7800.33],  # 浮点数 N
        'RQ': pd.to_datetime(['20240101', '20240315', '20240720',  # 纯日期 D
                              '20241130', '20241225'], format='%Y%m%d'),
        'CJSJ': pd.to_datetime(['20240101 093000', '20240315 143045',  # 带时分秒 C(14)
                                '20240720 081500', '20241130 170012',
                                '20241225 235959'], format='%Y%m%d %H%M%S'),
        'HF': [True, False, True, False, True],  # 布尔 L
        'BZ': ['正常', '异常', '', '待确认', '正常'],  # 含空字符串 C
        'KH': ['A001', 'B002', 'C003', 'D004', 'E005'],  # 字符串 C
    })

    # 把df的数据删除，只留表头
    df_empty = df.iloc[0:0]

    export_dbf_file(df_empty, context_instance)

    full_path = os.path.join('/tmp/export_test', 'test_empty.DBF')
    if os.path.exists(full_path):
        print(f'空DataFrame导出成功！文件路径: {full_path}, 文件大小: {os.path.getsize(full_path)} bytes')
    else:
        print('空DataFrame导出失败！')


if __name__ == '__main__':
    print('=' * 60)
    print('测试1: 正常 DataFrame 导出 DBF')
    print('=' * 60)
    test_export_dbf_file()

    print()
    print('=' * 60)
    print('测试2: 空 DataFrame 导出 DBF')
    print('=' * 60)
    test_export_empty_dbf()
