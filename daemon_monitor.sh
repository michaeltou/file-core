#!/bin/bash

# 守护进程监控脚本
# 用于监控 file-core 服务，当服务挂掉时自动重启

# 配置参数
APP_NAME="file-core"
APP_DIR="/Users/douming/code/yss/file-core"
LOG_FILE="/Users/douming/code/file-core-logs/daemon_monitor.log"
CHECK_INTERVAL=5  # 检查间隔（秒）

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查进程是否运行
is_process_running() {
    # 检查 gunicorn 进程是否存在
    pgrep -f "gunicorn.*file_core_app:app" > /dev/null 2>&1
    return $?
}

# 启动服务
start_service() {
    log "Starting $APP_NAME service..."
    cd "$APP_DIR" || exit 1

    # 设置环境变量
    export PYTHONPATH="$APP_DIR:$PYTHONPATH"

    # 启动服务（后台运行）
    setsid gunicorn --config gunicorn.conf.py --log-config gunicorn-logging.conf engine.file_core_app:app > /dev/null 2>&1 &

    # 等待一下让进程启动
    sleep 2

    if is_process_running; then
        log "$APP_NAME service started successfully"
        echo "$APP_NAME service started successfully"
    else
        log "Failed to start $APP_NAME service"
        echo "Failed to start $APP_NAME service"
    fi
}

# 停止服务
stop_service() {
    log "Stopping $APP_NAME service..."
    pkill -f "gunicorn.*file_core_app:app"
    sleep 2
    log "$APP_NAME service stopped"
}

# 主监控循环
monitor() {
    log "Starting $APP_NAME daemon monitor..."

    while true; do
        if ! is_process_running; then
            log "$APP_NAME service is not running, restarting..."
            echo "$APP_NAME service is not running, restarting..."
            start_service
        fi
        sleep $CHECK_INTERVAL
    done
}

# 显示使用帮助
usage() {
    echo "Usage: $0 {start|stop|restart|monitor|status}"
    exit 1
}

# 检查服务状态
status() {
    if is_process_running; then
        echo "$APP_NAME service is running"
        log "$APP_NAME service is running"
    else
        echo "$APP_NAME service is not running"
        log "$APP_NAME service is not running"
    fi
}

# 主入口
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        start_service
        ;;
    monitor)
        monitor
        ;;
    status)
        status
        ;;
    *)
        usage
        ;;
esac
