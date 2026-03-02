import pandas as pd
from io import BytesIO

from ydbfdm import YDbfWriter

# dbf文件说明：https://github.com/y10h/ydbf/blob/master/doc/links.md

# 创建示例 DataFrame
data = {
    'name': ['张三', 'lisi'],
    'age': [28, 34],
    'city': ['beijing', 'shanghai']
}
df = pd.DataFrame(data)

# 将 DataFrame 按行转换为字典列表
records = df.to_dict(orient='records')


# 准备字段结构
fields = [
    ('name', 'C', 10, 0),
    ('age', 'N', 3, 0),
    ('city', 'C', 10, 0)
]

fh = BytesIO()

# 创建 DBFWriter 对象
dbf_writer = YDbfWriter(fh,fields,encoding='cp936')
# 保存 DBF 文件
dbf_writer.write(records)
bytes_io = fh

# 将文件指针移动到开头，以便后续读取内容
bytes_io.seek(0)
# 定义要保存的文件路径
dbf_file_path = "../../output.dbf"

# 以二进制写入模式打开文件并将 BytesIO 中的内容写入文件
with open(dbf_file_path, 'wb') as file:
    # 读取 BytesIO 中的所有内容并写入文件
    file.write(bytes_io.read())

# 关闭 BytesIO 对象
bytes_io.close()

print(f"数据已成功写入 {dbf_file_path}")