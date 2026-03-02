
from dbfreaddm import DBF

import pandas as pd



table = DBF('/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf',encoding='gbk')


##1 获取基本信息
print("总记录数：", len(table))
field_names = table.field_names
print("字段名：", field_names)


original_df = pd.DataFrame(iter(table))


data_tuples = list(original_df.itertuples(index=False, name=None))

print(data_tuples)






