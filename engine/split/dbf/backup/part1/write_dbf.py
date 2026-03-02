from engine.split.dbf.backup.part1.dftodbf import dbfwrite
import pandas as pd
import time


# 创建大数据量示例（10万行）
big_data = {
    'Name': ['name_'+str(i) for i in range(100000)],
    'Age': [i % 100 for i in range(100000)],
    'City': ['city_'+str(i) for i in range(100000)]
}
df = pd.DataFrame(big_data)

# 批量写入优化方案
start_time = time.time()

dbfwrite(df, 'big_data.dbf')

print(f"总耗时: {time.time() - start_time:.2f}秒")