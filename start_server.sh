#!/bin/bash

cd ..

# 检查父目录中是否存在 file-core-logs 文件夹
if [ ! -d "file-core-logs" ]; then
    echo "file-core-logs 日志文件夹不存在，正在创建..."
    mkdir file-core-logs
else
    echo "file-core-logs 日志文件夹已存在，无需创建"
fi

cd file-core

CURRENT_DIR=$(pwd)



echo "当前目录是:$CURRENT_DIR"

echo "重新安装服务包开始..."
./install_package.sh
echo "重新安装服务包结束..."

export PYTHONPATH=$CURRENT_DIR:$PYTHONPATH


echo "初始化PythonPath，服务启动中..."
setsid gunicorn  --config gunicorn.conf.py --log-config gunicorn-logging.conf  engine.file_core_app:app > /dev/null 2>&1 &

echo "服务启动成功"



