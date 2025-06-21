@echo off
setlocal enabledelayedexpansion

REM 创建虚拟环境
python -m venv venv
call venv\Scripts\activate.bat

REM 安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 使用 PyInstaller 构建
pyinstaller --clean --noconfirm build.spec

echo 构建完成！可执行文件位于 dist 目录下
pause
