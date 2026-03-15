import pandas as pd

#构造一个dataframe ，并且打印出它的内容
df = pd.DataFrame({
    'ID': [1, 2, 3],
    'NAME': ['Alice', 'Bob', 'Charlie'],
    'AGE': [25, 30, 35]
})

print(df)
