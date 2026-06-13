#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="/home/phfund/software/file-core"
ZIP_FILE="${SCRIPT_DIR}/file-core.zip"

# 新建目录
mkdir -p "$TARGET_DIR" || { echo "[ERROR] 创建目录失败: $TARGET_DIR"; exit 1; }

# 解压
if [ -f "$ZIP_FILE" ]; then
    unzip -o "$ZIP_FILE" -d "$TARGET_DIR" || { echo "[ERROR] 解压失败: $ZIP_FILE"; exit 1; }
    echo "[INFO] 解压完成: $ZIP_FILE -> $TARGET_DIR"
else
    echo "[ERROR] 找不到 $ZIP_FILE"
    exit 1
fi

# 修正文件属主
chown -R phfund:phfund "$TARGET_DIR"

# 切换到文件网关目录
cd "$TARGET_DIR" || { echo "[ERROR] 切换目录失败: $TARGET_DIR"; exit 1; }

chmod +x *.sh

# 检查并执行安装脚本
if [ -x ./install_package.sh ]; then
    ./install_package.sh || { echo "[ERROR] install_package.sh 执行失败"; exit 1; }
else
    echo "[ERROR] 找不到 install_package.sh 或无执行权限"
    exit 1
fi
