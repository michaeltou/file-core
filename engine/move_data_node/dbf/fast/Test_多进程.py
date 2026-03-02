from multiprocessing import Pool
import time
import os

def task(n):
    print(f"进程 {os.getpid()} 正在处理任务 {n}")
    time.sleep(2)
    return n * n

if __name__ == '__main__':
    # 单进程测试
    start = time.time()
    single_results = [task(i) for i in range(10)]
    print(f"单进程耗时: {time.time() - start:.2f}秒")

    # 多进程测试
    start = time.time()
    # 创建包含4个工作进程的进程池
    with Pool(processes=4) as pool:
        # 提交任务到进程池
        results = pool.map(task, range(10))
        print(results)
    print(f"4进程耗时: {time.time() - start:.2f}秒")