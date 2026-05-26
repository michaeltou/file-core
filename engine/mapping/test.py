import pandas as pd
import uuid
# 假设你有一个DataFrame df
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

print(df.index)

# 使用reset_index方法添加一列行号，并将其重命名为RECNUM
df['RECNUM'] = df.reset_index().index + 1
# df['RECNUM'] = df.index + 1

#给这个dataframe 添加一列，名字叫UUID，这列的值是使用uuid生成的值
df['UUID'] = df.apply(lambda _: str(uuid.uuid4()), axis=1)

# 打印结果
# print(df)

def uuid_to_decimal(uuid_obj):
    """将UUID转换为十进制"""
    # 去掉连字符，得到纯十六进制字符串
    hex_str = str(uuid_obj).replace('-', '')
    # 将十六进制字符串转换为十进制整数
    decimal_value = int(hex_str, 16)
    return decimal_value

my_uuid = uuid.uuid4()
print(f"原始UUID: {my_uuid}")

# 转换为十进制
decimal_value = uuid_to_decimal(my_uuid)
print(f"十进制表示: {decimal_value}")
print(f"十进制位数: {len(str(decimal_value))}位")