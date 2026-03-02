import time

import pandas as pd

df = pd.DataFrame({
    'date_str': ['2024-01-01', '2024-02-01', '2024-03-01']
})

df['date'] = pd.to_datetime(df['date_str'])

mytype = df.dtypes
print('字段类型:',mytype)
#---------------字段类型---------------
print('date_str字段类型:',df['date_str'].dtype)
print('date字段类型:',df['date'].dtype)


date_str = '01/01/2024'
date_time = pd.to_datetime(date_str, format='%d/%m/%Y')
print('01/01/2024转换为日期类型:',date_time)

#时间戳的转换
timestamp_list = [int(time.time()), int(time.time()) + 3600]
date_time_series = pd.to_datetime(timestamp_list, unit='s')
print(date_time_series)

# 获取当前时间的时间戳（以秒为单位）
timestamp_seconds = int(time.time())
# 使用pd.to_datetime进行转换
datetime_obj = pd.to_datetime(timestamp_seconds, unit='s')
print(datetime_obj)
print("年:", datetime_obj.year)
print("月:", datetime_obj.month)
print("日:", datetime_obj.day)
print("时:", datetime_obj.hour)
print("分:", datetime_obj.minute)
print("秒:", datetime_obj.second)

# 假设这是一个以毫秒为单位的时间戳
timestamp_milliseconds = 1672531200000
datetime_obj_millis = pd.to_datetime(timestamp_milliseconds, unit='ms')
print(datetime_obj_millis)




'''
原理：当日期字符串的格式不是pandas能够自动识别的标准格式（如YYYY - MM - DD HH:MM:SS）时，需要使用format参数来明确指定日期字符串的格式。
日期格式代码示例
%Y：代表四位的年份，如2024。
%y：代表两位的年份，如24（范围是00 - 99）。
%m：代表两位的月份，范围是01 - 12。
%d：代表两位的日期，范围是01 - 31。
%H：代表 24 小时制的小时数，范围是00 - 23。
%I：代表 12 小时制的小时数，范围是01 - 12。
%M：代表分钟数，范围是00 - 59。
%S：代表秒数，范围是00 - 59。
%a：星期几的缩写（英文），如Mon。
%A：星期几的全称（英文），如Monday。
%b：月份的缩写（英文），如Jan。
%B：月份的全称（英文），如January。



'''