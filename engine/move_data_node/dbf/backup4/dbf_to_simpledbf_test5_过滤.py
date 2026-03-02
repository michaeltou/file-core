from simpledbfdm import Dbf5
import pandas as pd
import time

#https://github.com/rnelsonchem/simpledbf

from datetime import datetime

def convert_date_format(date_str, from_format='%Y%m%d', target_format='%Y-%m-%d'):
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, from_format)
    # 格式化日期对象为目标字符串格式
    formatted_date_str = date_obj.strftime(target_format)
    return formatted_date_str

file_path = "/Users/douming/Documents/读数工具重构/文件/测试文件/SJSFX-TEST2.DBF"
dbf = Dbf5(file_path, codec='gbk')


df = dbf.to_dataframe()
df['FXFSRQ'] = pd.to_datetime(df['FXFSRQ'])
print('原始数据：\n',df, df.dtypes)

# # df['FXFSRQ'] = df['FXFSRQ'].astype(str)
# check_logic = "FXFSRQ == '2018-04-27'"



check_logic = "FXFSRQ == @pd.Timestamp('2018-04-27')"
# FXFSRQ != @pd.Timestamp('[BUSINESS_DATE]')
my_checked_dataframe = df.query(check_logic)




print('过滤后数据：\n',my_checked_dataframe)



