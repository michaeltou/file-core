import subprocess
import os
import time


def excel_to_csv(excel_file_path, csv_file_path):
    """
    使用 LibreOffice 将 Excel 文件转换为 CSV 文件。

    :param excel_file_path: Excel 文件的路径
    :param csv_file_path: 转换后 CSV 文件的保存路径
    :return: 转换成功返回 True，失败返回 False
    """
    try:
        # 构建 LibreOffice 命令
        command = [
            'libreoffice',
            '--headless',
            '--convert-to',
            'csv:Text - txt - csv (StarCalc):44,34,UTF8,,true',
            '--outdir',
            os.path.dirname(csv_file_path),
            excel_file_path
        ]
        # 执行命令
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("转换成功，输出信息：", result.stdout)

        # 重命名生成的 CSV 文件（LibreOffice 默认使用 Excel 文件名）
        default_csv_path = os.path.splitext(excel_file_path)[0] + '.csv'
        if os.path.exists(default_csv_path):
            os.rename(default_csv_path, csv_file_path)
            print(f"文件已重命名为 {csv_file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print("转换失败，错误信息：", e.stderr)
        return False
    except Exception as e:
        print("发生未知错误：", e)
        return False

if __name__ == "__main__":
    excel_file = 'lytz_knock_20250514-外包估值系统格式.xlsx'
    csv_file = 'output.csv'
    start_time = time.time()
    if excel_to_csv(excel_file, csv_file):
        print("Excel 文件已成功转换为 CSV 文件。")
    else:
        print("Excel 文件转换失败。")
    end_time = time.time()
    print("总耗时：", end_time - start_time, "秒")