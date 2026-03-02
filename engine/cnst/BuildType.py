from enum import Enum


# 构建类型枚举
class BuildType(Enum):
    # 查询sql构造上下文
    QUERY_SQL = 1
    # 从XML文件提取数据构造上下文
    XML_EXTRACT = 2
    # 通过常量构造上下文
    CONSTANT_SET = 3

