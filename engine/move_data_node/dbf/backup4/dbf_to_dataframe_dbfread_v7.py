
from dbfreaddm import DBF

import pandas as pd
import time


file_path = "/Users/douming/Documents/读数工具重构/文件/测试文件/compare/2/永安期货_0000_20220818_1_SettlementDetail.DBF"


table = DBF(file_path, encoding='gbk',load=True)

print("加载dbf数据, 记录数:", len(table))


start_time = time.time()
original_df = pd.DataFrame(iter(table))
end_time = time.time()
print("转换dbf数据到dataframe耗时:", end_time - start_time)






