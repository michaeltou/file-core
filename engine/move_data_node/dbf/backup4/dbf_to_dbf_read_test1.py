
import dbf


#https://github.com/rnelsonchem/simpledbf


file_path = "永安期货_0000_20220818_1_SettlementDetail.DBF"

tb = dbf.Table(file_path)  # 创建tb实例
print(tb) # 打印tb信息

tb.open(mode=dbf.READ_WRITE)  # 读写方式打开tb    print('title_name=', title_name)
for record in tb:
    value_list = []
    deleted_status = dbf.is_deleted(record)  # 查看当前行是否标记删除
    print('deleted_status=', deleted_status)
    with record as r:
        for field in record:
            value_list.append(field)
    print('value_list=', value_list)



