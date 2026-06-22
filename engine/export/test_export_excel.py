"""
测试 export_xls_file 和 export_xlsx_file 方法
覆盖: 字符串、整数、浮点数、日期、带时分秒的日期、布尔、NaN值、空DataFrame
"""
import os
import uuid
import pandas as pd
import numpy as np

from engine.core.context import Context
from engine.export.export_file import export_xls_file, export_xlsx_file

TEST_DIR = '/tmp/export_test'


def build_test_df():
    """构造包含各种类型的测试DataFrame"""
    df = pd.DataFrame({
        'XM': ['张三', '李四', '王五', '赵六', '钱七'],
        'NL': [25, 30, 28, 35, 40],
        'GZ': [8500.50, 12000.75, 9300.00, 15600.88, 7800.33],
        'RQ': pd.to_datetime(['20240101', '20240315', '20240720',
                              '20241130', '20241225'], format='%Y%m%d'),
        'CJSJ': pd.to_datetime(['20240101 093000', '20240315 143045',
                                '20240720 081500', '20241130 170012',
                                '20241225 235959'], format='%Y%m%d %H%M%S'),
        'HF': [True, False, True, False, True],
        'BZ': ['正常', '异常', '', '待确认', '正常'],
        'KH': ['A001', 'B002', 'C003', 'D004', 'E005'],
    })
    return df


def build_context(export_file_name):
    """构造上下文"""
    ctx = Context()
    ctx.set('[TARGET_PATH]', TEST_DIR)
    ctx.set('[EXPORT_FILE_NAME]', export_file_name)
    ctx.set('[FILE_EXPORT_FMT]', 'XLSX')
    ctx.set('[UUID]', str(uuid.uuid4()))
    return ctx


def verify_file(full_path, description):
    """验证文件是否生成并回读"""
    if not os.path.exists(full_path):
        print(f'  ❌ {description} 文件未生成！')
        return False

    file_size = os.path.getsize(full_path)
    print(f'  ✅ {description} 文件生成成功，大小: {file_size} bytes')

    try:
        result_df = pd.read_excel(full_path, engine='openpyxl')
        print(f'  回读行数: {len(result_df)}, 列: {list(result_df.columns)}')
        if not result_df.empty:
            print(result_df.head(3).to_string(index=False))
        return True
    except Exception as e:
        print(f'  ❌ 回读失败: {e}')
        return False


# ==================== XLSX 测试 ====================

def test_xlsx_normal():
    """测试1: 正常DataFrame导出XLSX"""
    print('--- test_xlsx_normal ---')
    df = build_test_df()
    ctx = build_context('test_normal.xlsx')
    export_xlsx_file(df, ctx)
    full_path = os.path.join(TEST_DIR, 'test_normal.xlsx')
    verify_file(full_path, '正常XLSX')


def test_xlsx_empty():
    """测试2: 空DataFrame导出XLSX"""
    print('--- test_xlsx_empty ---')
    df = pd.DataFrame()
    ctx = build_context('test_empty.xlsx')
    export_xlsx_file(df, ctx)
    full_path = os.path.join(TEST_DIR, 'test_empty.xlsx')
    verify_file(full_path, '空XLSX')


def test_xlsx_only_header():
    """测试4: 只有表头无数据的DataFrame导出XLSX"""
    print('--- test_xlsx_only_header ---')
    df = build_test_df().iloc[0:0]
    ctx = build_context('test_header_only.xlsx')
    export_xlsx_file(df, ctx)
    full_path = os.path.join(TEST_DIR, 'test_header_only.xlsx')
    verify_file(full_path, '仅表头XLSX')




# ==================== XLS 测试 ====================

def test_xls_normal():
    """测试7: 正常DataFrame导出XLS"""
    print('--- test_xls_normal ---')
    df = build_test_df()
    ctx = build_context('test_xls_normal.xls')
    export_xls_file(df, ctx)
    full_path = os.path.join(TEST_DIR, 'test_xls_normal.xls')
    verify_file(full_path, '正常XLS')


def test_xls_empty():
    """测试8: 空DataFrame导出XLS"""
    print('--- test_xls_empty ---')
    df = build_test_df()
    # 把df的数据删除，只留表头
    df_empty = df.iloc[0:0]


    ctx = build_context('test_xls_empty.xls')
    export_xls_file(df_empty, ctx)
    full_path = os.path.join(TEST_DIR, 'test_xls_empty.xls')
    verify_file(full_path, '空XLS')


def test_xls_with_nan():
    """测试9: 含NaN的DataFrame导出XLS"""
    print('--- test_xls_with_nan ---')
    df = build_test_df()
    df.loc[1, 'BZ'] = np.nan
    df.loc[2, 'GZ'] = np.nan
    ctx = build_context('test_xls_nan.xls')
    export_xls_file(df, ctx)
    full_path = os.path.join(TEST_DIR, 'test_xls_nan.xls')
    verify_file(full_path, '含NaN XLS')


# ==================== 主入口 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('XLSX 导出测试')
    print('=' * 60)
    test_xlsx_normal()
    test_xlsx_empty()
    test_xlsx_only_header()

    print()
    print('=' * 60)
    print('XLS 导出测试')
    print('=' * 60)
    test_xls_normal()
    test_xls_empty()
    test_xls_with_nan()
