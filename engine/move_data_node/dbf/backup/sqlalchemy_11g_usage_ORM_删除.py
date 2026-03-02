import os


from sqlalchemy import create_engine, Column, Integer, String, or_
import oracledb
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import platform
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=True)
    email = Column(String(64), nullable=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"




# # 链接oracle 11g客户端，需要调用init_oracle_client函数，用于初始化，
# # 这里调用后使用的是oracle的thick mode

d = None                               # On Linux, no directory should be passed
if platform.system() == "Darwin":      # macOS
  d = os.environ.get("HOME")+("/Downloads/instantclient_23_3")
elif platform.system() == "Windows":   # Windows
  d = r"C:\oracle\instantclient_23_5"
oracledb.init_oracle_client(lib_dir=d)

# Oracle配置
#新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
oracle_engine = create_engine('oracle+oracledb://IS20170920B77:IS20170920B77@10.20.146.69:1521/orcl',
                              echo=True, # 打印sql语句
                              pool_size=8, # 连接池大小
                              pool_recycle=60 * 30,  # 30 minutes，默认如果不设置，连接将不回收重新连接，有连接被服务端数据库关闭，连接是无效的风险。
                              pool_timeout = 30, # 指定了从连接池中获取连接的超时时间，单位是秒。
                              )


#创建表，如果存在则忽略，执行以上代码，就会发现在db中创建了users表。
Base.metadata.create_all(oracle_engine)


def get_next_id():
    connection = oracle_engine.connect()
    try:
        result = connection.execute(text("SELECT user_seq.NEXTVAL FROM DUAL"))
        return result.scalar()
    finally:
        connection.close()

@event.listens_for(User, 'before_insert')
def assign_id(mapper, connection, target):
 target.id = get_next_id()


# 插入数据
user = User(name='jack', email='jack@example.com')
# sessionmaker是创建session的工厂类,创建了一个session类，不是实例
session_class = sessionmaker(bind=oracle_engine)
session = session_class()
session.add(user)
session.commit()


deleteResult = session.query(User).filter(or_(User.id == 10 ,User.id==11)).delete()
print('删除结果：deleteResult=',deleteResult)
session.commit()

result = session.query(User).filter(User.name == 'jack').all()
for user in result:
    print(user)

session.close()

