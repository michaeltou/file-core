import pandas as pd

# 创建一个DataFrame
data = {'Name': ['Tom', 'Jack', 'Steve', 'Ricky'],
        'Age': [28, 34, 29, 42]}
df = pd.DataFrame(data)

# 将DataFrame转换为列表，其中每个元素是一个字典
data_list = df.to_dict(orient='records')

# 打印列表
print(data_list)