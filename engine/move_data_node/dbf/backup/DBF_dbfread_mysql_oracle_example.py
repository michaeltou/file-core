from dbfreaddm import DBF

import pandas as pd
import time
from sqlalchemy import create_engine
 

table = DBF('/Users/douming/Documents/读数工具重构/dbf_files/ZZGZ20180307.dbf',encoding='gbk')


##1 获取基本信息
print("总记录数：", len(table))
field_names = table.field_names
print("字段名：", field_names)
dbversion = table.dbversion
print("数据库版本：", dbversion)
date = table.date
print("创建日期：", date)


##2 打印记录
print('--------------打印10条记录------------------start--------------------------')
count = 0
print_total_cnt = 10
## 这里的循环迭代，不会把文件全部加载到内存中，而是按需加载，所以不会占用过多内存。所以速度很快。
for record in table:
    if count < print_total_cnt:
        # 打印每一条记录，记录是以字典的形式呈现的，字段名作为键，字段值作为值。
        print(record)
    else:
        break
    count += 1
print('--------------打印10条记录------------------end--------------------------')


##3 与pandas库结合使用
start_time = time.time()

df = pd.DataFrame(iter(table))
end_time = time.time()
execution_time = end_time - start_time
print("加载数据,转成DataFrame耗时：", execution_time,',记录数:', len(table))





# mysql配置
mysql_engine = create_engine('mysql+pymysql://root:tm123456@localhost:3306/test')

# Oracle配置
#旧包：https://cx-oracle.readthedocs.io/en/latest/api_manual/deprecations.html
#新包： https://oracle.github.io/python-oracledb/  https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#quickstart
oracle_engine = create_engine('oracle+oracledb://fam_dev_65:fam_dev_65@10.20.146.67:1521/orcl')

start_time = time.time()




# 字段映射配置
mapping_dict = {
    'ZQJC': 'ZQJC',
    'ZQDM': 'ZQDM'
}

# 字段加工代码
process_code = 'targetDF["ZQJC"] = df["ZQJC"] + "456"'


## 字段映射后的DataFrame
targetDF = pd.DataFrame()
for col_n,value in mapping_dict.items():
    targetDF[col_n] = df[value]
    exec(process_code)



# targetDF.to_sql('dbf_2_mysql_table', con=mysql_engine, if_exists='append', index=False,chunksize=1000)

#插入数据库总耗时： 1.4078011512756348 记录数: 42286
targetDF.to_sql('dbf_2_oracle_table', con=oracle_engine, if_exists='append', index=False, chunksize=1000)



end_time = time.time()
execution_time = end_time - start_time
print("插入数据库总耗时：", execution_time,'记录数:', len(table))




