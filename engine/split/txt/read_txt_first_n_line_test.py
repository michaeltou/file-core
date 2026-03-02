def read_first_n_lines(file_path, n, encoding='gbk'):
    """
    读取文件的前 n 行。

    :param file_path: 文件路径
    :param n: 要读取的行数
    :param encoding: 文件编码，默认为 'gbk'
    :return: 包含前 n 行内容的列表
    """
    lines = []
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            for i, line in enumerate(file):
                if i <= n:
                    lines.append(line)
                else:
                    break
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return lines

def write_lines_to_file(lines, output_file_path, encoding='gbk'):
    """
    将行数据写入到指定的文件中。

    :param lines: 要写入的行数据列表
    :param output_file_path: 输出文件的路径
    :param encoding: 文件编码，默认为 'gbk'
    """
    try:
        with open(output_file_path, 'w', encoding=encoding) as file:
            for line in lines:
                file.write(line)
        print(f"数据已成功写入到 {output_file_path}。")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")


if __name__ == '__main__':
    file_encoding = 'gbk'
    lines = read_first_n_lines('SettlementDetail_has_header.txt', 3, file_encoding)
    print(lines)
    output_file_path = 'output.txt'
    write_lines_to_file(lines, output_file_path)