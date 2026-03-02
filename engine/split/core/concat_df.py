import pandas as pd

# 创建第一个 DataFrame
data1 = {
    'Name': ['Alice', 'Bob'],
    'Age': [25, 30]
}
df1 = None

# 创建第二个 DataFrame
data2 = {
    'Name': ['Charlie', 'David'],
    'Age': [35, 40]
}
df2 = pd.DataFrame(data2)

# 使用 DataFrame.append 进行上下拼接
result_append = pd.concat([df1, df2], ignore_index=True)
print("使用 DataFrame.append 拼接结果：")
print(result_append)