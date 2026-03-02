import pandas as pd

# 假设你有一个DataFrame df
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

print(df.index)

# 使用reset_index方法添加一列行号，并将其重命名为RECNUM
df['RECNUM'] = df.reset_index().index + 1
# df['RECNUM'] = df.index + 1

# 打印结果
print(df)