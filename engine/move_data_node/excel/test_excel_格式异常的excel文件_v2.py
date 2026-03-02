import pandas as pd
from xlsx2csv import Xlsx2csv
import uuid
import os


def excel_to_dataframe(file_path_and_name, skip_rows, total_column_count, header_line=None):
    # pd.read_excel 如果传入的列名称比文件中的列数量少，则会导致列的对应关系不正确，这里人工在用户设置的列名称列表基础上，额外增加10列（做冗余，以防文件做了列增加）
    auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1+10)]
    try:
        excel_df = pd.read_excel(file_path_and_name,
                                 skiprows=skip_rows,
                                 header=header_line,
                                 names=auto_gen_column_names
                                 )

        return excel_df
    except TypeError as e:
        print(f'Error: {e}')
        print('由于excel格式（比如wind万德导出的xls文件格式）异常，尝试使用 xlsx2csv 转换为 csv 文件再读取')
        random_filename = generate_random_filename()
        Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert(random_filename)
        # Xlsx2csv 转换后的 csv 文件，分割符为逗号，这里使用了默认的分隔符
        default_sep = ","
        csv_data_frame = pd.read_csv(random_filename,
                                     sep=default_sep,
                                     header=header_line,
                                     skiprows=skip_rows,
                                     names=auto_gen_column_names,
                                     index_col=False)
        delete_file(random_filename)
        return csv_data_frame


def generate_random_filename():
    # 生成一个随机的UUID
    random_uuid = uuid.uuid4()
    # 将UUID转换为字符串，并去掉连字符
    random_filename = str(random_uuid).replace('-', '')
    random_filename = random_filename + '.csv'
    return random_filename

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"文件 {file_path} 已成功删除。")
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
    except PermissionError:
        print(f"没有权限删除文件 {file_path}。")
    except Exception as e:
        print(f"删除文件 {file_path} 时发生错误: {e}")

if __name__ == '__main__':
    my_skip_rows = 4
    my_total_column_count = 12
    my_dataframe = excel_to_dataframe('2062_信托测试估值表-无法打开.xlsx',
                                      my_skip_rows, my_total_column_count)
    print(my_dataframe)