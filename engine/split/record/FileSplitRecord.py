from datetime import datetime
from engine.db.oracle_split_db_util import *
from sqlalchemy import Column, String, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class FileSplitRecord(Base):

    __tablename__ = 'fs_file_split_record'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),  # 定义复合主键
    )
    uuid = Column(String(200))
    rule_id = Column(String(200))
    rule_name = Column(String(64))
    file_path_and_name = Column(String(200))
    md5 = Column(String(200))
    status = Column(DECIMAL(10,0))
    message = Column(String(2000))
    start_time = Column(DECIMAL(20, 0))
    end_time = Column(DECIMAL(20, 0))
    elapsed_time = Column(DECIMAL(20, 0))
    create_time = Column(DECIMAL(14, 6))
    update_time = Column(DECIMAL(14, 6))

    def __init__(self, uuid=None, rule_id=None,
                 rule_name=None, file_path_and_name=None,
                 md5=None, status=None, message=None,
                 start_time=None, end_time=None,
                 elapsed_time=None, create_time=None, update_time=None):
        self.uuid = uuid
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.file_path_and_name = file_path_and_name
        self.md5 = md5
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.create_time = create_time
        self.update_time = update_time

    def insert_record(self):
        with OracleSplitConnectionPool.get_session() as session:
            timeStr = datetime.now().strftime('%Y%m%d.%H%M%S')
            self.create_time = float(timeStr)
            self.update_time = float(timeStr)
            if self.end_time is not None and self.start_time is not None:
                self.elapsed_time = self.end_time - self.start_time
            session.add(self)
            session.commit()


if __name__ == "__main__":
    file_split_record = FileSplitRecord(uuid='11111', rule_id='22222', rule_name='33333',
                                        file_path_and_name='44444', md5='55555', status=1, message='66666',
                                        start_time=123455,  end_time=123457, elapsed_time=1,
                                        create_time=20241220.223344, update_time=20241220.334455)

    # 修改uuid

    file_split_record.insert_record()
