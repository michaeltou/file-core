from xlsx2csv import Xlsx2csv

import time

if __name__ == '__main__':
    file_path_and_name = "lytz_knock_20250514-外包估值系统格式.xlsx"
    start_time = time.time()
    print('开始转csv文件')
    Xlsx2csv(file_path_and_name, outputencoding="utf-8", sheet_name=1).convert("lytz_knock_20250515-外包估值系统格式.csv")
    end_time = time.time()
    print("转成csv文件用时： ", end_time - start_time)