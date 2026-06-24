@echo off
REM 电商价格采集与对比工具启动脚本 (Windows)

echo ==================================
echo 电商价格采集与对比工具
echo ==================================
echo.
echo 请选择运行模式:
echo 1. 命令行模式 (CLI)
echo 2. Web服务模式 (需要安装依赖)
echo 3. 仅查看网页 (生成独立HTML文件)
echo.

set /p choice=请输入选择 [1/2/3]:

if "%choice%"=="1" (
    echo.
    echo 运行命令行模式...
    echo 示例: python price_cli.py 手机
    echo.
    python price_cli.py %*
) else if "%choice%"=="2" (
    echo.
    echo 检查依赖...
    pip install -q flask flask-cors 2>nul
    echo 启动Web服务...
    echo 请在浏览器打开: http://localhost:5000
    python api_server.py
) else if "%choice%"=="3" (
    echo.
    echo 复制网页文件到当前目录...
    copy web\index.html price_comparison_tool.html
    echo 已生成: price_comparison_tool.html
    echo 请在浏览器中打开此文件即可使用
) else (
    echo 无效选择，默认运行命令行模式...
    python price_cli.py %*
)
