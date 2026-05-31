@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 简历优化助手 - 多线程修复版打包

echo ========================================
echo   简历优化助手 - 多线程修复版打包
echo ========================================
echo.
echo [修复] 使用多线程处理优化任务
echo [修复] 避免GUI主线程阻塞
echo.

cd /d "%~dp0"

echo [检查] Python版本...
python --version

echo.
echo [步骤1/4] 确认依赖已安装...
pip show PyQt6 > nul 2>&1
if errorlevel 1 (
    echo [安装] PyQt6未安装，正在安装...
    pip install PyQt6 -q
) else (
    echo [确认] PyQt6已安装
)

echo.
echo [步骤2/4] 安装其他依赖...
pip install openai python-docx pdfplumber markdown requests pydantic -q
echo [完成] 依赖安装完成

echo.
echo [步骤3/4] 清理旧文件...
if exist "dist" (
    echo       清理dist目录...
    rmdir /s /q dist
)
if exist "build" (
    echo       清理build目录...
    rmdir /s /q build
)

echo.
echo [步骤4/4] 执行打包（预计5-15分钟）...
echo.

pyinstaller "PyQt6专用打包.spec" --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo.
    echo [调试] 请运行以下命令查看详细错误：
    echo pyinstaller PyQt6专用打包.spec --debug=all
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo       多线程修复版打包完成！
echo ========================================
echo.
echo [输出位置]
echo    dist\简历优化助手_PyQt6版\简历优化助手_PyQt6版.exe
echo.
echo [修复内容]
echo    1. 使用QThread多线程处理优化任务
echo    2. 避免GUI主线程阻塞
echo    3. 进度条实时更新
echo    4. 界面保持响应
echo.
echo [测试] 请测试程序是否还会卡在25%
echo.

pause
endlocal
