import pandas as pd

# 假设有一个DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']}


df = pd.DataFrame(data)
print('过滤前的数据表:----------\n', df)


condition = df['Age'] > 30

filtered_df = df[condition]
print('过滤后的数据表:----------\n', filtered_df)



# 字典数据
data = {
     'col1': [1, 2, 3, 4, 5],
        'col2': [6, 7, 8, 9, 10],
        'col3': ['value1 ', ' value2', ' value3 ', 'value4 ', 'value5']
      }

# 创建DataFrame
df = pd.DataFrame(data)

condition = (df['col1'] > 3) & (df['col2'] >= 8) & (df['col3'].str.startswith('value'))

# condition = (df['col1'] > 3) & (df['col2'] >= 8) & (df['col3'].str.strip().str.startswith('value'))
# # 多条件过滤
# condition = (df['col1'] > 3) & (df['col3'].str.strip() == 'value4')

filtered_df1 = df[condition]
print(filtered_df1)
