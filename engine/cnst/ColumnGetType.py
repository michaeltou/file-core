from enum import Enum

#字段获取类型 BY_SEPARATOR：按分隔符获取，BY_POSITION：按位置获取
# 列值获取方式
class ColumnGetType(Enum):
    # 根据分隔符获取列值
    SEPERATOR = "BY_SEPARATOR"
    # 根据位置获取列值
    POSITION = "BY_POSITION"

