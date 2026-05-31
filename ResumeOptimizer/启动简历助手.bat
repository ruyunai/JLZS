@echo off
chcp 65001 > nul
title 简历优化助手

echo ========================================
echo      简历优化助手 v1.0
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo [提示] 首次运行，正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt -q
    echo [完成] 依赖安装完成
    echo.
) else (
    call venv\Scripts\activate
)

echo [启动] 正在启动简历优化助手...
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序启动失败！
    pause
)
