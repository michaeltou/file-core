import pandas as pd
from xlsx2csv import Xlsx2csv


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
    except Exception as e:
        print(f'Error: {e}')
        print('尝试使用 xlsx2csv 转换为 csv 文件再读取')
        Xlsx2csv(file_path_and_name, outputencoding="utf-8").convert("examplecsv.csv")
        new_dataframe = pd.read_csv("examplecsv.csv")
        print(new_dataframe)



if __name__ == '__main__':
    my_skip_rows = 4
    my_total_column_count = 12
    my_dataframe = excel_to_dataframe('2062_信托测试估值表-无法打开.xlsx',
                                      my_skip_rows, my_total_column_count)
    print(my_dataframe)