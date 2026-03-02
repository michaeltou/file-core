import pandas as pd
import time
from sqlalchemy import create_engine


"""默认读数 sheet1 """
myexcel = pd.read_excel('CSRCINDUSTRY20180416.xls')

print(myexcel)

df = myexcel


# Oracle配置
#旧包：https://cx-oracle.readthedocs.io/en/latest/api_manual/deprecations.html
#新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
engine = create_engine('oracle+oracledb://fam_dev_65:fam_dev_65@10.20.146.67:1521/orcl')

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
# 耗时： 0.34716129302978516 记录数： 3526
targetDF.to_sql('excel_oracle_table', engine, if_exists='append', index=False,chunksize=1000)

endTime = time.time()
print("插入数据库耗时：", endTime - startTime, '记录数：',len(targetDF))