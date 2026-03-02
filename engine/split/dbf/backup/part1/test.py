import pandas as pd

# 创建一个示例 DataFrame
data = {
    'Column1': ['apple', 'banana', 'cherry', 'date'],
    'Column2': [1, 2, 3, 4]
}
df = pd.DataFrame(data)

# 获取第一列数据
first_column = df.iloc[:, 0]

# 将第一列数据转换为以逗号分割的字符串
result = ','.join(map(str, first_column))

all_belong_value = result

print(result)

all_belong_df = pd.DataFrame(all_belong_value.split(','), columns=['fund_code'])

print(all_belong_df)