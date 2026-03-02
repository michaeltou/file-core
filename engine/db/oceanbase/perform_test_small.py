# engine/db/oceanbase/demo_large_txt_to_sql.py
import os
import random
import string
import time
import pandas as pd
from sqlalchemy import create_engine


# ====================== 第一部分：生成 TXT ======================
def generate_random_string(length=8):
    """生成指定长度的随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_file_size(file_path):
    """获取文件大小并转换为易读格式"""
    size_bytes = os.path.getsize(file_path)
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def create_sample_txt(file_path="large_sample_data.txt", num_rows=15102020):
    """生成大型 TXT 文件，| 分隔，前 8 列数字，后 8 列字符串"""
    start_time = time.time()
    print(f"开始生成 {num_rows:,} 行数据...")

    with open(file_path, 'w', encoding='utf-8') as f:
        for i in range(num_rows):
            # 前 8 列随机整数 (0-999999)
            num_cols = [str(random.randint(0, 999999)) for _ in range(8)]
            # 后 8 列随机字符串 (最大 8 位)
            str_cols = [generate_random_string(random.randint(1, 8)) for _ in range(8)]
            # 用 | 连接并写入
            line = "|".join(num_cols + str_cols) + "\n"
            f.write(line)

            # 每处理100万行打印一次进度
            if (i + 1) % 1000000 == 0:
                elapsed = time.time() - start_time
                print(f"已生成 {i + 1:,} 行，耗时 {elapsed:.2f} 秒")

    elapsed = time.time() - start_time
    file_size = get_file_size(file_path)
    print(f"文件生成完成！共 {num_rows:,} 行，耗时 {elapsed:.2f} 秒，文件大小: {file_size}")
    return file_path


# ====================== 第二部分：分块读取 ======================
def read_txt_in_chunks(file_path, chunk_size=10000):
    """分块读取 TXT 文件，返回 DataFrame 迭代器"""
    print(f"开始分块读取文件，每块 {chunk_size:,} 行...")
    start_time = time.time()

    # 定义列名
    col_names = [f"num_{i}" for i in range(1, 9)] + [f"str_{i}" for i in range(1, 9)]

    # 使用 pd.read_csv 分块读取
    reader = pd.read_csv(
        file_path,
        sep="|",
        header=None,
        names=col_names,
        dtype={f"num_{i}": "int64" for i in range(1, 9)},  # 前 8 列设为整数
        chunksize=chunk_size,
        encoding='utf-8'
    )

    elapsed = time.time() - start_time
    print(f"分块读取初始化完成，耗时 {elapsed:.2f} 秒")
    return reader


# ====================== 第三部分：分块写入数据库 ======================
def write_chunks_to_db(reader, engine, table_name="TEMP_TEXT_TEST", if_exists="replace"):
    """
    将分块读取的 DataFrame 写入数据库
    :param reader: pd.read_csv 返回的 TextFileReader 对象
    :param engine: SQLAlchemy Engine
    :param table_name: 目标表名
    :param if_exists: 'replace', 'append', 'fail'
    """
    print(f"开始分块写入数据库表 {table_name}...")
    start_time = time.time()
    total_rows = 0
    chunk_count = 0
    read_time = 0
    write_time = 0

    for i, chunk in enumerate(reader):
        # 记录读取时间
        read_start = time.time()
        # 这里chunk已经从reader中读取，所以不需要额外操作
        read_elapsed = time.time() - read_start
        read_time += read_elapsed

        # 记录写入时间
        write_start = time.time()
        # 写入数据库
        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",  # 第一块建表，后续追加
            index=False
        )
        write_elapsed = time.time() - write_start
        write_time += write_elapsed

        chunk_count += 1
        total_rows += len(chunk)

        # 每处理10块打印一次进度
        if chunk_count % 10 == 0:
            elapsed = time.time() - start_time
            print(f"已处理 {chunk_count} 块，{total_rows:,} 行，总耗时 {elapsed:.2f} 秒")

    total_elapsed = time.time() - start_time
    print(f"完成！共处理 {chunk_count} 块，{total_rows:,} 行数据")
    print(f"总耗时: {total_elapsed:.2f} 秒")
    print(f"读取耗时: {read_time:.2f} 秒 ({read_time / total_elapsed * 100:.1f}%)")
    print(f"写入耗时: {write_time:.2f} 秒 ({write_time / total_elapsed * 100:.1f}%)")
    print(f"平均每块处理时间: {total_elapsed / chunk_count:.2f} 秒")
    print(f"平均每行处理时间: {total_elapsed / total_rows * 1000:.3f} 毫秒")

    return total_rows, total_elapsed


# ====================== 主程序 ======================
if __name__ == "__main__":
    # 1. 创建数据库引擎
    engine = create_engine(
        "oracle+cx_oracle://DOUMING:$tm1Alove$tm1Alove@t7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING",
        pool_size=3,  # 连接池大小
        max_overflow=20,  # 额外可溢出连接
        echo=True  # 打印实际发出的 SQL，调试用
    )

    # 2. 生成大型 TXT 文件
    txt_file = create_sample_txt(num_rows=10000)  # 生成 15102020 行数据

    # 3. 分块读取
    chunk_reader = read_txt_in_chunks(txt_file, chunk_size=1000)  # 每块 10000 行

    # 4. 分块写入数据库
    write_chunks_to_db(chunk_reader, engine, table_name="TEMP_TEXT_TEST", if_exists="replace")

    # 5. 可选：删除临时文件
    # os.remove(txt_file)
