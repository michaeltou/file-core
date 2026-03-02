from cx_Oracle import SessionPool
#数据库连接信息
username = 'DOUMING'
password = '$tm1Alove$tm1Alove'
oracle_connection = 't7fgjby4vhzq8-mi.aliyun-cn-shenzhen-internet.oceanbase.cloud:1521/DOUMING'


def test_simple_pool():
    """连接池测试"""
    try:
        print("创建连接池...")
        # 创建连接池
        pool = SessionPool(
            user=username,
            password=password,
            dsn=oracle_connection,
            min=2,
            max=5,
            increment=1
        )
        print(f"连接池创建成功！")
        print(f"- 最小连接数: {pool.min}")
        print(f"- 最大连接数: {pool.max}")
        print(f"- 增量: {pool.increment}")

        print("\n测试连接池使用...")
        # 从连接池获取连接
        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                # 执行查询
                cursor.execute("SELECT COUNT(*) FROM test_char")
                result = cursor.fetchone()
                print(f"test_char 表记录数: {result[0]}")

                # 执行另一个查询
                cursor.execute("SELECT * FROM test_char WHERE id = 1")
                data = cursor.fetchone()
                print(f"查询结果: {data}")

        print(f"\n连接池状态:")
        print(f"- 当前打开的连接数: {pool.opened}")
        print(f"- 当前繁忙的连接数: {pool.busy}")

        print("\n连接池测试成功完成！")
        # 注意：不调用 pool.close() 来避免段错误

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    test_simple_pool()