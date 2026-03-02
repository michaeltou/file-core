from datetime import datetime
from engine.db.oracle_split_db_util import *
from sqlalchemy import Column, String, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class FileExceptionLog(Base):

    __tablename__ = 'fs_split_exception_log'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),  # 定义复合主键
    )
    uuid = Column(String(200))
    rule_id = Column(String(200))
    rule_name = Column(String(64))
    file_path_and_name = Column(String(200))
    exception_type = Column(DECIMAL(10,0))
    message = Column(String(2000))
    create_time = Column(DECIMAL(14, 6))
    update_time = Column(DECIMAL(14, 6))

    def __init__(self, uuid=None, rule_id=None,
                 rule_name=None, file_path_and_name=None, exception_type=None,
                 message=None, create_time=None, update_time=None):
        self.uuid = uuid
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.file_path_and_name = file_path_and_name
        self.exception_type = exception_type
        self.message = message
        self.create_time = create_time
        self.update_time = update_time

    def insert_record(self):
        with OracleSplitConnectionPool.get_session() as session:
            timeStr = datetime.now().strftime('%Y%m%d.%H%M%S')
            self.create_time = float(timeStr)
            self.update_time = float(timeStr)
            session.add(self)
            session.commit()


if __name__ == "__main__":
    file_exception_log = FileExceptionLog(uuid='11111', rule_id='22222', rule_name='33333',
                                          file_path_and_name='44444',  exception_type=2,  message='66666',
                                          create_time=20241220.223344, update_time=20241220.334455)

    # 修改uuid

    file_exception_log.insert_record()
