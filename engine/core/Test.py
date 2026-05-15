import pandas as pd
import engine.util.log as log
# 假设有一个DataFrame
data = {'Name': ['Tom', 'Jack', 'Steve', 'Ricky'],
        'Age': [28, 34, 29, 42]}
df = pd.DataFrame(data)


# 将DataFrame转换为字典
data_list = df.head(10).to_dict(orient='records')

print(data_list)
log.info("要处理的dataFrame的前10条数据：%s", data_list)
# 将列表转换为字符串
data_str = str(data_list)

# 将字符串写入文件
with open('data.txt', 'w') as file:
    file.write(data_str)