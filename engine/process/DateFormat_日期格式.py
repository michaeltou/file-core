

'''

日期格式：

%Y:4位数的年份，例如2023
%y:2位数的年份，例如23
%m:2位数的月份，例如01
%d: 2位数的天数，例如01
%H: 2位数的小时数，例如09
%I: 12小时制的小时数，例如09
%M: 2位数的分钟数，例如05
%S: 2位数的秒数，例如03
%f: 微秒数，例如000000
%z: 时区偏移量，例如+0800
%Z: 时区名称，例如China Standard Time


date_str = '2023-04-15'
date = pd.to_datetime(date_str, format='%Y-%m-%d')
print(date)  # 输出: 2023-04-15 00:00:00


date_str = '2023-04-15 14:30:00'
date = pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S')
print(date)  # 输出: 2023-04-15 14:30:00

date_str = '15/04/2023'
date = pd.to_datetime(date_str, format='%d/%m/%Y')
print(date)  # 输出: 2023-04-15 00:00:00


'''