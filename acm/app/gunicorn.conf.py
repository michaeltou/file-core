import multiprocessing


# 监听的端口
bind = "0.0.0.0:27777"


# 获取工作进程数量，这个workers名字不能改，是内置变量名称
workers =  2 # multiprocessing.cpu_count()

print("系统的CPU核数:", multiprocessing.cpu_count())
print("启动进程数:", workers)

# 每个工作进程的线程数. 推荐配置：针对8核和16G的系统，这里线程数默认设置为10，如果是其他配置，需要根据实际情况调整。
# 如果这里的线程数调整了，请到application.yaml中修改限流的配置。
threads = 10
print("每个工作进程的线程数:", threads)

# 超时时间, 超过这个时间还没响应，就强制关闭连接并重启worker进程, 单位秒.
# 这个参数目前看，只有在 sync模式下，并且threads=2的情况下，才起作用
# timeout = 2
# print("超时时间(超过这个时间还没响应，就强制关闭连接并重启worker进程):", timeout, "秒")

worker_class = "gthread"


print("工作模式:", worker_class)

#
# accesslog = 'logs/access.log'
# errorlog = 'logs/gunicorn.log'
pidfile = './gunicorn.pid'