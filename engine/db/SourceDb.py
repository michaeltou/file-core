from engine.db.oracle_read_tool_db_util import *
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SourceDb(Base):

    __tablename__ = 'dm_source_db'
    __table_args__ = (
        PrimaryKeyConstraint('db_id'),  # 定义复合主键
    )
    # 数据库ID
    db_id = Column(String(200))
    # 数据库名称
    db_name = Column(String(200))
    # 数据库类型(1:oracle, 2:sqlserver)
    db_type = Column(DECIMAL(10,0))
    # 连接类型(oracle专属),比如:SID、SERVICE_NAME
    db_connection_type = Column(DECIMAL(10,0))
    db_host = Column(String(30))
    db_port = Column(String(10))
    # SID (oracle专属)
    db_sid = Column(String(50))
    # 服务名(oracle专属)
    db_service_name = Column(String(50))
    db_user = Column(String(50))
    db_password = Column(String(50))
    # 实例(sqlserver专属)
    db_instance = Column(String(50))
    # 数据库(sqlserver专属)
    db_database = Column(String(50))
    create_time = Column(DECIMAL(14, 6))
    update_time = Column(DECIMAL(14, 6))

    def __init__(self, db_id=None, db_name=None, db_type=None, db_connection_type=None, db_host=None, db_port=None,
                 db_sid=None, db_service_name=None, db_user=None, db_password=None, db_instance=None, db_database=None,
                 create_time=None, update_time=None):
        self.db_id = db_id
        self.db_name = db_name
        self.db_type = db_type
        self.db_connection_type = db_connection_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_sid = db_sid
        self.db_service_name = db_service_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_instance = db_instance
        self.db_database = db_database
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return ("<SourceDb(db_id='%s', db_name='%s', db_type='%s', "
                "db_connection_type='%s', db_host='%s', db_port='%s', "
                "db_sid='%s', db_service_name='%s', db_user='%s', "
                "db_password='%s', db_instance='%s', db_database='%s', "
                "create_time='%s', update_time='%s')>" % (
                    self.db_id, self.db_name, self.db_type, self.db_connection_type, self.db_host, self.db_port,
                    self.db_sid, self.db_service_name, self.db_user, self.db_password, self.db_instance, self.db_database,
                    self.create_time, self.update_time))

    def generate_connection_url(self):
        sql_str = ""
        if self.db_type == 1:  # oracle
            if self.db_connection_type == 1:  # SID
                sql_str = "oracle+oracledb://" + self.db_user + ":" + self.db_password + "@" + self.db_host + ":" + self.db_port + "/" + self.db_sid
            elif self.db_connection_type == 2:  # SERVICE_NAME
                sql_str = "oracle+oracledb://" + self.db_user + ":" + self.db_password + "@" + self.db_host + ":" + self.db_port + "/" + self.db_service_name
        elif self.db_type == 2:  # sqlserver
            sql_str = "mssql+pymssql://" + self.db_user + ":" + self.db_password + "@" + self.db_host + ":" + self.db_port + "/" + self.db_database
        return sql_str




if __name__ == '__main__':
    session = OracleConnectionPool.get_session()
    result = session.query(SourceDb).filter(SourceDb.db_id == 'oracledb1').one()

    print(result)

