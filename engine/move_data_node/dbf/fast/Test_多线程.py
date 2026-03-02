from concurrent.futures import ThreadPoolExecutor
import time
import threading

def task(n):
    thread_id = threading.current_thread().ident
    print(f"线程 {thread_id} 正在处理任务 {n}")
    time.sleep(2)
    return n * n


# 创建包含4个工作线程的线程池
with ThreadPoolExecutor(max_workers=4) as executor:
    # 提交任务到线程池
    futures = [executor.submit(task, i) for i in range(10)]

    # 获取结果
    results = [f.result() for f in futures]
    print(results)
