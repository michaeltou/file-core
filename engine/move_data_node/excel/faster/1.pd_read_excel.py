from xlsx2csv import Xlsx2csv
import pandas as pd
import time
if __name__ == '__main__':
    file_path_and_name = "lytz_knock_20250514-外包估值系统格式.xlsx"
    sheet_name = 0
    skip_rows = 1
    header_line = None
    total_column_count = 30
    auto_gen_column_names = [f'F{i}' for i in range(1, total_column_count+1+10)]
    start_time = time.time()
    print('开始读取excel文件')

    excel_df = pd.read_excel(file_path_and_name,
                             sheet_name=sheet_name,
                             skiprows=skip_rows,
                             header=header_line,
                             names=auto_gen_column_names,
                             dtype=str,

                             )


    end_time = time.time()
    print(f"读取完成，len(excel_df)={len(excel_df)}，耗时 {end_time - start_time} 秒")
