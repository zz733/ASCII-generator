#!/bin/bash

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 使用 PyInstaller 构建
pyinstaller --clean --noconfirm build.spec

echo "构建完成！可执行文件位于 dist/ 目录下"
