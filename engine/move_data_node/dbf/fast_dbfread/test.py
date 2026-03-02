
if __name__ == '__main__':
    process_count = 4  # 进程数
    total_record_size = 10  # 总记录数
    # 计算每个进程处理的记录范围
    records_per_process = total_record_size // process_count
    remainder = total_record_size % process_count

    # 生成每个进程的(start_index, end_index)元组
    tuple_param_list = []
    start = 0
    for i in range(process_count):
        end = start + records_per_process - 1
        if i < remainder:  # 将余数均匀分配到前几个进程
            end += 1
        tuple_param_list.append((  start, end))
        start = end + 1

    print('tuple_param_list', tuple_param_list)