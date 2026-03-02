from datetime import datetime
from engine.db.oracle_read_tool_db_util import *
from sqlalchemy import Column, String, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PerformanceMonitorLog(Base):

    __tablename__ = 'dm_performance_monitor_log'
    __table_args__ = (
        PrimaryKeyConstraint('uuid', 'phase'),  # 定义复合主键
    )
    uuid = Column(String(200))
    fund_id = Column(String(64))
    business_date = Column(DECIMAL(10,0))
    interface_id = Column(String(64))
    interface_name = Column(String(200))
    file_path_and_name = Column(String(200))
    read_mode = Column(DECIMAL(10,0))
    phase = Column(String(100))
    status = Column(DECIMAL(10,0))
    message = Column(String(2000))
    ip_address = Column(String(50))
    start_time = Column(DECIMAL(20, 0))
    end_time = Column(DECIMAL(20, 0))
    elapsed_time = Column(DECIMAL(20, 0))
    create_time = Column(DECIMAL(14, 6))
    update_time = Column(DECIMAL(14, 6))

    def __init__(self, uuid=None, fund_id=None, business_date=None, interface_id=None, interface_name=None,
                 file_path_and_name=None, read_mode=None, phase=None, status=None, message=None, ip_address=None,
                 start_time=None, end_time=None, elapsed_time=None, create_time=None, update_time=None):
        self.uuid = uuid
        self.fund_id = fund_id
        self.business_date = business_date
        self.interface_id = interface_id
        self.interface_name = interface_name
        self.file_path_and_name = file_path_and_name
        self.read_mode = read_mode
        self.phase = phase
        self.status = status
        self.message = message
        self.ip_address = ip_address
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.create_time = create_time
        self.update_time = update_time

    def insert_log(self):
        with OracleConnectionPool.get_session() as session:
            timeStr = datetime.now().strftime('%Y%m%d.%H%M%S')
            self.create_time = float(timeStr)
            self.update_time = float(timeStr)
            if self.end_time is not None and self.start_time is not None:
                self.elapsed_time = self.end_time - self.start_time
            session.add(self)
            session.commit()




if __name__ == "__main__":
    performance_monitor_log = PerformanceMonitorLog(uuid='11111', fund_id='123456', business_date=20210101, interface_id='123456',
                          interface_name='123456', file_path_and_name='gh.dbf', read_mode=1,
                          phase='load', status=1, message='python message', ip_address=None, start_time=123455,
                          end_time=123457, elapsed_time=1, create_time=20241220.223344, update_time=20241220.334455)

    # 修改uuid
    performance_monitor_log.fund_id = '654321'

    performance_monitor_log.insert_log()
