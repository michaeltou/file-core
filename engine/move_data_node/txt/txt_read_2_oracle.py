import pandas as pd
import time
from sqlalchemy import create_engine


seperator = "|"
header = None
skip_rows = 12
names = ['F'+str(i) for i in range(1,12)]
names.insert(0,'column1')


"""默认读数 sheet1 """
mytxt = pd.read_csv('20180302BOND_VALUATION.txt', sep="|", header=None, skiprows=12, names=names, index_col=False)
# mytxt = pd.read_csv('20180302BOND_VALUATION.txt', sep="|", header=None, skiprows=12, names=names, index_col=False)

print(mytxt)

df = mytxt


# Oracle配置
#旧包：https://cx-oracle.readthedocs.io/en/latest/api_manual/deprecations.html
#新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
engine = create_engine('oracle+oracledb://fam_dev_65:fam_dev_65@10.20.146.67:1521/orcl')

# 字段映射配置
mapping_dict = {
    'F1': 'F1',
    'F4': 'F4'
}

# 字段加工代码
process_code = 'targetDF["F4"] = df["F4"] + "abc"'


## 字段映射后的DataFrame
targetDF = pd.DataFrame()
for col_n,value in mapping_dict.items():
    targetDF[col_n] = df[value]
    exec(process_code)



startTime = time.time()
# 耗时： 0.34716129302978516 记录数： 3526
targetDF.to_sql('txt_oracle_table', engine, if_exists='append', index=False,chunksize=1000)

endTime = time.time()
print("耗时：", endTime - startTime, '记录数：', len(targetDF))