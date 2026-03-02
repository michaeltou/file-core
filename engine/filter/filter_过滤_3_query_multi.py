import pandas as pd

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

# 也可以使用query方法
filtered_df2= df.query('col1 > 3 and col2 >= 8 and col3.str.startswith("value")')
print(filtered_df2)


filtered_df2= df.query('col3.str.startswith("value")')
print(filtered_df2)




