from enum import Enum


class FieldType(Enum):
    # 字符串
    STRING = 'STRING'
    # 数值
    DECIMAL = 'DECIMAL'
    # 日期
    DATETIME = 'DATETIME'

if __name__ == '__main__':
    print('STRING' == FieldType.STRING.value)

    print('STRING1' == FieldType.STRING.value)
