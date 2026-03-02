import pandas as pd

# 假设有一个DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']}
df = pd.DataFrame(data)

# 使用query方法和like操作符过滤城市名中包含'New'的行
filtered_df = df.query('City.str.contains("New")')

# 打印过滤后的DataFrame
print(filtered_df)
