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
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
        'Date': ['2019-05-01', '2019-05-02', '2019-05-03', '2019-05-04']}


df = pd.DataFrame(data)
print('过滤前的数据表:----------\n', df)



# 使用query方法筛选出City列的前三位字符为Hou的行
filtered_df = df.query("City.str.slice(0,3)  == 'Hou'")

# 打印过滤后的DataFrame
print('过滤后的数据表:----------\n', filtered_df)

