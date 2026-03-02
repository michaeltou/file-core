import cx_Oracle

#数据库连接信息
username = 'DOUMING'
password = '$tm1Alove$tm1Alove'
oracle_connection = 't7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING'

#创建数据库连接
print('开始连接数据库...')
conn = cx_Oracle.connect(username, password, oracle_connection)
print('数据库连接成功')



def exec_sql(sql):
    """执行 SQL 语句"""
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(f"SQL 执行成功: {sql}")
    except Exception as e:
        print(f"SQL 执行失败: {sql}")
        print(f"错误信息: {e}")
    finally:
        cur.close()


def print_data(sql):
    """查询并打印数据"""
    cur = conn.cursor()
    try:
        cur.execute(sql)
        data = cur.fetchall()
        print(f"查询结果: {data}")
        return data
    except Exception as e:
        print(f"查询失败: {sql}")
        print(f"错误信息: {e}")
        return None
    finally:
        cur.close()


def test_char_types():
    """测试字符类型"""
    print("\n=== 测试字符类型 ===")
    exec_sql("DROP TABLE test_char")
    exec_sql("""
        CREATE TABLE test_char (
            id INT, 
            a VARCHAR2(20), 
            b CHAR(10), 
            c NCHAR(10), 
            d NVARCHAR2(10)
        )
    """)
    exec_sql("INSERT INTO test_char VALUES (1, 'hello', 'adffdf', '2df4d', 'dsf44f')")
    print_data("SELECT * FROM test_char")


def test_number_types():
    """测试数值类型"""
    print("\n=== 测试数值类型 ===")
    exec_sql("DROP TABLE test_number")
    exec_sql("""
        CREATE TABLE test_number (
            a NUMBER, 
            b FLOAT(126), 
            c BINARY_FLOAT, 
            d BINARY_DOUBLE
        )
    """)
    exec_sql("INSERT INTO test_number VALUES (12.32, 12.34, 14.23, 123.3433)")
    print_data("SELECT * FROM test_number")


def test_time_types():
    """测试时间类型"""
    print("\n=== 测试时间类型 ===")
    exec_sql("DROP TABLE test_time")
    exec_sql("""
        CREATE TABLE test_time (
            a DATE, 
            b TIMESTAMP, 
            c TIMESTAMP WITH TIME ZONE, 
            d TIMESTAMP WITH LOCAL TIME ZONE
        )
    """)
    exec_sql("""
        INSERT INTO test_time VALUES (
            TIMESTAMP'2022-08-29 14:44:30', 
            TIMESTAMP'2022-08-29 14:44:30', 
            TIMESTAMP'2022-08-29 14:44:30', 
            TIMESTAMP'2022-08-29 14:44:30'
        )
    """)
    print_data("SELECT * FROM test_time")


def test_lob_types():
    """测试 LOB 类型"""
    print("\n=== 测试 LOB 类型 ===")
    exec_sql("DROP TABLE test_lob")
    exec_sql("""
        CREATE TABLE test_lob (
            a CLOB, 
            b BLOB, 
            c RAW(100)
        )
    """)
    exec_sql("INSERT INTO test_lob VALUES ('sdfdslkfjldsf', '31323334353637', '31323334')")
    print_data("SELECT * FROM test_lob")


def main():
    """主函数"""
    try:
        print("开始测试 OceanBase 数据库 Oracle 模式连接...")
        # 测试各种数据类型
        test_char_types()
        test_number_types()
        test_time_types()
        test_lob_types()

        print("\n所有测试完成！")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        #关闭数据库连接
        if conn:
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    main()
