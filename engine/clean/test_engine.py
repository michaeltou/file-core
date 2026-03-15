from sqlalchemy import create_engine,text
import urllib.parse

# 1. 配置参数（补充集群名）
USERNAME = "Y7PHFUND_REALTIME"
PASSWORD = "aaAA11##2025"
HOST = "uatobc05.phfund.com.cn"
PORT = 2883
CLUSTER = "UAT_Cluster05"  # 集群名
TENANT = "UAT_GZ01"        # 租户名
DATABASE = "Y7PHFUND_REALTIME"  # 数据库名

USERNAME = "Y7PHFUND_REALTIME@UAT_GZ01#UAT_Cluster05"


# 2. 转义密码特殊字符
PASSWORD = urllib.parse.quote_plus(PASSWORD)
USERNAME = urllib.parse.quote_plus(USERNAME)

# 3. 拼接 URL（service_name = 集群.租户.数据库）
CONN_URL = (
    f"oracle+cx_oracle://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)
print(CONN_URL)

# 4. 创建引擎（保持原有参数）
engine = create_engine(
    CONN_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

# 测试连接
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ 连接成功（含集群名标识）！")
            result = conn.execute(text("SELECT 1 FROM DUAL"))
            print(f"查询结果：{result.scalar()}")
    except Exception as e:
        print(f"❌ 连接失败：{e}")