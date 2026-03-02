import pandas as pd
import numpy as np

# 假设有一个DataFrame
data = {'column1': [0, 2.34567, 3.45678],
        'column2': [1.23456, 2.34567, 3.45678],
        'column3': ['blank ', 'end ', '6 '],
        'column4': ['我们', 'def', 'ghi'],
        'column5': [3, 4, None],
        'column6': ['2025-01-01', '2025-01-02', '2025-01-03']
        }
df = pd.DataFrame(data)
print('原始DataFrame:----------\n',df)

# 对column2列，进行截取小数位数4位，不进行四舍五入
df['column2'] = df['column2'].apply(lambda x: int(x*10000)/10000)

print('截取后的DataFrame:----------\n',df)


# # 截取column4列的前2个字符
# df['column4'] = df['column4'].str[:1]
# print('截取后的DataFrame:----------\n',df)
# todo add to page
# 对 col1 列进行替换操作
# df['column6'] = df['column6'].str.replace('-', '')
# print('处理后的DataFrame:----------\n',df)

# df['column6'] = df['column6'].apply(lambda x: x.replace('-', ''))
#
# print('处理后的DataFrame:----------\n',df)
# todo add to page
# df['column1'] = np.where(df['column1'] == 0, np.nan, df['column1'])
# df['DQRQ'] = np.where(df['DQRQ'] == 0, np.nan, df['DQRQ'])



# df['column5'] = df['column5'].fillna('-1')
# # df['FISINCODE'] = df['FISINCODE'].fillna('-1')
# print(df)
#
# 将列只保留2位小数(四舍五入)
# 简写方式：round($,2)
# 原生写法如下：
df['column1'] = df['column1'].round(2)
df['column1'] = df['column1'].apply(lambda x: round(x,2))


# 将列进行加减乘除操作（可直接使用算术运算符）
# 简写方式：$ + 1
# 原生写法如下：
df['column2'] = df['column2'] + 1
df['column2'] = df['column2'].apply(lambda x: x + 1)

# 将列转换为字符串类型并去除空格
# 简写方式：$.strip()
# 原生写法如下：
# df['column3'] = df['column3'].astype(str).str.strip()
df['column3'] = df['column3'].apply(lambda x: x.strip())

# 将列加上前缀
# 简写方式：'prefix_' + $
# 原生写法如下：
df['column4'] = 'prefix_' + df['column4']

# 计算列的平方
# 简写方式：$**2
# 使用apply方法对column1列应用lambda表达式
df['column5'] = df['column5'].apply(lambda x: x ** 2)
#
#
# # 打印DataFrame
# print('加工后的DataFrame:----------\n',df)
#
#
# # 创建一个示例DataFrame
# df = pd.DataFrame({
#     'A': [1, 2, 3, 4, 5],
#     'B': [10, 20, 30, 40, 50]
# })
#
# # 使用np.where()函数对列A进行条件运算
# # 如果A列的值大于3，则将B列的值加100，否则保持不变
# df['B'] = np.where(df['A'] > 3, df['B'] + 100, df['B'])
#
# df['B'] = np.where(df['A'] > 3, df['B'] * 2, df['B'])


# df['DQRQ'] = np.where(df['DQRQ'] == 0, np.nan, df['DQRQ'])