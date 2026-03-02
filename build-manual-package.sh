#!/bin/bash

# Remove previous build
rm -rf app/*

echo "开始执行工程打包"
# Build package
python3 setup.py bdist_wheel

# 检查打包是否成功
if [ $? -eq 0 ]; then
    echo "打包python工程项目成功"
else
    echo "打包python工程项目失败"
    exit 1
fi

# 删除app目录以前的所有内容
rm -rf acm/app/*

# Copy built package to app directory
cp dist/*.whl acm/app/
cp application.yaml acm/app/
cp gunicorn.conf.py acm/app/
cp gunicorn-logging.conf acm/app/
cp install_package.sh acm/app/
cp start_server.sh acm/app/
cp stop_server.sh acm/app/


# 检查复制是否成功
if [ $? -eq 0 ]; then
    echo "复制成功"
else
    echo "复制失败"
    exit 1
fi

echo "开始压缩文件"
cd acm/app
# 压缩dist目录为zip文件
zip -r ../../file-core-手动安装包-$(date +'%Y%m%d-%H%M%S').zip .

# 检查压缩是否成功
if [ $? -eq 0 ]; then
    echo "压缩成功"
else
    echo "压缩失败"
    exit 1
fi

echo "所有步骤完成"