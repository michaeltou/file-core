from datetime import datetime

import pandas as pd


def convert_date_format(date_str, from_format='%Y%m%d', target_format='%Y-%m-%d'):
        # 将字符串转换为日期对象
        date_obj = datetime.strptime(date_str, from_format)
        # 格式化日期对象为目标字符串格式
        formatted_date_str = date_obj.strftime(target_format)
        return formatted_date_str

# 假设有一个DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'Los Angeles', 'MD0022', 'Chicago'],
        'Date': ['2019-05-01', '2019-05-02', '2019-05-03', '2019-05-04']}


df = pd.DataFrame(data)
print('过滤前的数据表:----------\n', df)

filtered_df = df.query(' Name.str.len() == 5')

print('过滤后的数据表:----------\n', filtered_df)

# filtered_df = df.query('Date == @convert_date_format("20190503",from_format="%Y%m%d",target_format="%Y-%m-%d") ')
# # 打印过滤后的DataFrame
# print('过滤后的数据表:----------\n', filtered_df)
#
# # # 使用query方法执行过滤逻辑
# filtered_df = df.query('  City == "Chicago"')
# # 打印过滤后的DataFrame
# print('过滤后的数据表:----------\n', filtered_df)
#
#
# 使用query方法执行过滤逻辑
filtered_df = df.query('Name=="Bob" | Name=="Charlie"')
# 打印过滤后的DataFrame
print('过滤后的数据表:----------\n', filtered_df)
#
# # 使用query方法执行过滤逻辑
# filtered_df = df.query('Age == 25   ')
# # 打印过滤后的DataFrame
# print('过滤后的数据表:----------\n', filtered_df)


## 重要提示：
# 并：使用&符号连接多个条件，表示同时满足所有条件。
# 或：使用|符号连接多个条件，表示满足任一条件。

#过滤逻辑举例：HQZRSP >= [[MY_LIST.HQZRSP]] & HQJRKP >= [[MY_LIST.HQJRKP]] & HQCJJE == [HQCJJE]

# 数据集变量采用(双中括号):[[MY_LIST.HQZRSP]]
# 单值变量采用(双中括号):[FUND_ID]


# 使用query方法筛选出Age列不为空的行
# result = df.query("Age.notnull()")
# 使用query方法筛选出Age列为空的行
# result = df.query("Age.isnull()")


# 另外，在query中使用的列名称，需要使用大写(因为DataFrame的列名称是大小写敏感的)




# # 使用query方法筛选出City列的前三位字符为Hou的行
# filtered_df = df.query("City.str.slice(0,3)  == 'Hou'")
#
# # 打印过滤后的DataFrame
# print('过滤后的数据表:----------\n', filtered_df)

# filtered_df = df.query("City.str.slice(0,3)  == 'Hou' & City.str.slice(4,5)  != '1' & City.str.slice(4,5) != '4'")
#
# # 打印过滤后的DataFrame
# print('过滤后的数据表:----------\n', filtered_df)



