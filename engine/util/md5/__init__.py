import hashlib
import os
import time

def get_file_md5(file_path):
    """
    计算文件的MD5值。

    :param file_path: 文件的全路径名称
    :return: 文件的MD5值（十六进制字符串）
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return None

    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # 单位：字节 1024 * 1024 = 1M
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == '__main__':
    file_path = "/Users/douming/Documents/读数工具重构/安装文件/读数工具-python-读数引擎/migrate-core-2025-02-10.zip"
    start_time = time.time()
    md5_value = get_file_md5(file_path)
    end_time = time.time()
    # 592286b9a9363834b4e410b0b7ebc03e
    print(f"文件 的MD5值为：{md5_value}, 耗时：{end_time - start_time} 秒。")