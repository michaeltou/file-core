
from dbfreaddm import DBF

import pandas as pd
import time


file_path = "/Users/douming/Documents/读数工具重构/文件/测试文件/compare/2/永安期货_0000_20220818_1_SettlementDetail.DBF"


table = DBF(file_path  ,load=True)

# delete_df = pd.DataFrame(iter(table.deleted))
print(table.deleted)


original_df = pd.DataFrame(iter(table))
print("加载数据,转成DataFrame ,记录数:", len(original_df))
print(original_df)






