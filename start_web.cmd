@echo off
REM DRG分组器Web应用启动脚本 (Windows版本)
REM 使用uv工具管理Python环境和依赖

echo 🏥 DRG分组器Web应用启动脚本
echo ================================

REM 检查是否安装了uv
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到uv工具
    echo 请先安装uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM 检查虚拟环境是否存在
if not exist ".venv" (
    echo 📦 创建Python虚拟环境...
    uv venv
    echo ✅ 虚拟环境创建完成
)

REM 安装依赖
echo 📥 安装项目依赖...
uv sync

REM 检查Flask是否正确安装
echo 🔍 检查依赖安装状态...
uv run python -c "import flask; print('Flask版本:', flask.__version__)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Flask未正确安装，尝试重新安装...
    uv add flask
)

REM 检查DRG模块是否可用
echo 🧪 检查DRG分组器模块...
uv run python -c "from drg_group.beijing_2022.GroupProxy import GroupProxy; print('✅ DRG模块加载成功')" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: DRG分组器模块无法加载
    echo 请确保drg_group目录存在且包含必要的文件
    pause
    exit /b 1
)

echo 🚀 启动Web应用...
echo 访问地址: http://localhost:8080
echo 使用Ctrl+C停止服务
echo ================================

REM 设置端口并启动Flask应用
set PORT=8080
uv run python app.py

pause
