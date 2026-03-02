import logging
import os
import engine.util.config as config
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class LogUtil(object):
    print('config.get_root_path()=',config.get_root_path())
    root_path = config.get_root_path()
    parent_path = os.path.dirname(root_path)
    log_path = os.path.join(parent_path, 'migrate-core-logs')
    log_file = os.path.join(parent_path, 'migrate-core-logs', 'app.log')
    log_level = logging.INFO
    logger = None  # 类变量，用于存储日志记录器实例

    @classmethod
    def _setup_logger_if_not_initialed(cls):
        if not cls.logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(cls.log_level)

            # 创建日志目录(如果不存在)
            cls.create_log_dir_if_not_exist()

            # 创建文件处理器
            # file_handler = logging.FileHandler(cls.log_file)
            max_bytes = 1024 * 1024 * 50  # 50 MB
            backup_count = 50  # 保留的备份文件数量
            file_handler = RotatingFileHandler(cls.log_file,
                                               maxBytes=max_bytes,
                                               backupCount=backup_count)
            file_handler.setLevel(cls.log_level)

            # 创建时间滚动处理器
            when = 'D'  # 每天滚动
            interval = 1  # 每天滚动一次
            time_handler = TimedRotatingFileHandler(cls.log_file, when=when, interval=interval, backupCount=backup_count)
            time_handler.setLevel(logging.INFO)

            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(cls.log_level)

            # 创建日志格式
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            time_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 将处理器添加到日志记录器
            # logger.addHandler(file_handler)
            logger.addHandler(time_handler)
            # logger.addHandler(console_handler)

            cls.logger = logger  # 将日志记录器实例存储在类变量中

    @classmethod
    def create_log_dir_if_not_exist(cls):
        # log_path = os.path.join(config.get_root_path(), 'logs')
        if not os.path.exists(cls.log_path):
            os.makedirs(cls.log_path)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        cls._setup_logger_if_not_initialed()
        cls.logger.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        cls._setup_logger_if_not_initialed()
        cls.logger.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        cls._setup_logger_if_not_initialed()
        cls.logger.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls,  msg, *args, **kwargs):
        cls._setup_logger_if_not_initialed()
        cls.logger.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        cls._setup_logger_if_not_initialed()
        cls.logger.critical(msg, *args, **kwargs)


# 使用示例
if __name__ == '__main__':
    data = {'name': 'John', 'age': 30}

    LogUtil.debug('This is a debug message.')
    LogUtil.info('This is an info message.')
    LogUtil.warning('This is an warning message.')
    LogUtil.error('This is an error message.')
    LogUtil.critical('This is an critical message.')
    LogUtil.info(data)
