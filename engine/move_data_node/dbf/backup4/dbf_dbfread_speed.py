
from dbfreaddm import DBF
import pandas as pd
import time


file_path = "test.dbf"

start_time = time.time()
table = DBF(file_path, encoding='gbk',load=True)

end_time = time.time()

original_df = pd.DataFrame(iter(table))
print('读取dbf文件耗时：',end_time-start_time , '秒，记录数：' , len(original_df))






