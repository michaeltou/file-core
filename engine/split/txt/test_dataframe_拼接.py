import pandas as pd

# 创建示例 DataFrame
df1 = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

df2 = pd.DataFrame({
    'C': [7, 8, 9],
    'D': [10, 11, 12]
})

# 确保两个 DataFrame 行数相同
if len(df1) == len(df2):
    # 使用 pd.concat 进行左右拼接
    combined_df = pd.concat([df1, df2], axis=1)
    print(combined_df)
else:
    print("两个 DataFrame 的行数不同，无法进行左右拼接。")
