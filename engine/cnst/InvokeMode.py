from enum import Enum


class InvokeMode(Enum):
    # 普通模式
    NORMAL = 1
    # 测试模式-不写入数据库
    TEST_NO_WRITE_TO_DB = 2
    # 测试模式-不写入数据库
    TEST_WRITE_TO_DB = 3



