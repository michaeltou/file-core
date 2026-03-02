import pandas as pd
import time
from sqlalchemy import create_engine


"""默认读数 sheet1 """
myexcel = pd.read_excel('CSRCINDUSTRY20180416.xls')

print(myexcel)

df = myexcel


# mysql配置
engine = create_engine('mysql+pymysql://root:tm123456@localhost:3306/test')

# 字段映射配置
mapping_dict = {
    '证券代码': '证券代码',
    '证券名称': '证券名称'
}

# 字段加工代码
process_code = 'targetDF["证券代码"] = df["证券代码"] + "456"'


## 字段映射后的DataFrame
targetDF = pd.DataFrame()
for col_n,value in mapping_dict.items():
    targetDF[col_n] = df[value]
    exec(process_code)

startTime = time.time()
#耗时： 0.0660090446472168 记录数： 3526
targetDF.to_sql('excel_mysql_table', engine, if_exists='append', index=False,chunksize=1000)
endTime = time.time()
print("耗时：", endTime - startTime, '记录数：',len(targetDF))