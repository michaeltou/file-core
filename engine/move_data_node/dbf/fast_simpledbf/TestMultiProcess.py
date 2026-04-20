import os
import time
from multiprocessing import Pool, freeze_support
from threading import Thread
from time import sleep

import engine.util.config as config
from cx_Oracle import Object

# 批量处理进程池大小
BATCH_PROCESS_COUNT = config.get_config_value("read_tool.file.batch.process.pool.size",4)


class MyReader:
    def __init__(self ):
        # 使用全局进程池
        self.pool = self.gen_pool()

    @staticmethod
    def gen_pool(process_count=BATCH_PROCESS_COUNT):
        local_pool = Pool(processes=BATCH_PROCESS_COUNT)
        return local_pool

    def close_global_pool(self):
        """关闭全局进程池"""
        self.pool.close()  # 关闭进程池，不再接受新任务
        self.pool.join()  # 等待所有任务完成
        self.pool = None  # 将全局变量重置为None

    def do_sth_with_multi_process(self,count):
        tuple_param_list = []
        for i in range(count):
            name = "michael"
            tuple_param_list.append((name,i))


        start_time_submit = time.time()
        # 提交任务到进程池
        self.pool.starmap(one_process_do_task, tuple_param_list)

        end_time_submit = time.time()
        print('进程执行总耗时:' + str(end_time_submit-start_time_submit))
        self.close_global_pool()

        return None

def one_process_do_task(name,index):

    # 获取进程ID号，并且打印处理
    process_id = os.getpid()
    #睡眠500ms
    sleep(1)

    print('process id:', process_id,'正在处理数据', index)
    return

if __name__ == '__main__':
    reader = MyReader()
    count = 10
    reader.do_sth_with_multi_process(count)
