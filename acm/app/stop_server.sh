#!/bin/bash

# 定义Gunicorn的PID文件路径
PIDFILE=./gunicorn.pid




# 检查PID文件是否存在
if [ -f "$PIDFILE" ]; then
    # 读取PID文件中的进程ID
    PID=$(cat "$PIDFILE")

    # 检查进程是否存在
    if ps -p $PID > /dev/null; then
        # 发送SIGTERM信号来停止Gunicorn进程
        echo "Stopping Gunicorn process with PID $PID"
        kill -TERM $PID


        # 等待进程终止，最多重试N次，每次间隔1秒
        for i in {1..120}; do
            if ps -p $PID > /dev/null; then
                echo "Waiting for Gunicorn to stop..."
                sleep 1
            else
                echo "Gunicorn stopped gracefully"
                break
            fi
        done

         # 如果进程仍然存在，使用kill -9强制终止
        if ps -p $PID > /dev/null; then
            echo "Gunicorn process with PID $PID did not stop gracefully, using kill -9"
            kill -9 $PID
            echo "Gunicorn forcefully stopped"
        fi

         # 删除PID文件
        rm  -rf "$PIDFILE"
        rm  -rf "nohup.out"


    else
        echo "Gunicorn process with PID $PID is not running"
    fi

else
    echo "PID file $PIDFILE not found, 程序未启动，无需停止"
fi

# 强制杀死所有gunicorn进程
# ps -ef |grep gunicorn | grep -v grep | awk '{print $2}' | xargs kill -9