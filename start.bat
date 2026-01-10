@echo off
chcp 65001 >nul
title MindSlot - 脑力老虎机

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   🎰 MindSlot - 脑力老虎机            ║
echo  ╚══════════════════════════════════════╝
echo.

:: 获取脚本所在目录
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: 检查 conda 环境
echo [1/4] 检查环境...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Conda，请先安装 Miniconda 或 Anaconda
    pause
    exit /b 1
)

:: 激活 conda 环境
call conda activate mindslot 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  未找到 mindslot 环境，正在创建...
    call conda create -n mindslot python=3.11 -y
    call conda activate mindslot
    echo 📦 安装后端依赖...
    cd backend
    pip install -r requirements.txt
    cd ..
)

echo ✅ Conda 环境: mindslot
echo.

:: 检查前端依赖
echo [2/4] 检查前端依赖...
if not exist "frontend\node_modules" (
    echo 📦 安装前端依赖...
    cd frontend
    call npm install
    cd ..
)
echo ✅ 前端依赖已就绪
echo.

:: 启动后端
echo [3/4] 启动后端服务...
start "MindSlot Backend" cmd /k "cd /d %PROJECT_ROOT%backend && conda activate mindslot && python app.py"
timeout /t 3 /nobreak >nul
echo ✅ 后端地址: http://localhost:5000
echo.

:: 启动前端
echo [4/4] 启动前端服务...
start "MindSlot Frontend" cmd /k "cd /d %PROJECT_ROOT%frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo ✅ 前端地址: http://localhost:5173
echo.

echo ══════════════════════════════════════
echo.
echo  🎉 MindSlot 已启动！
echo.
echo  📖 打开浏览器访问: http://localhost:5173
echo.
echo  💡 操作提示:
echo     - 双击卡片: 点赞收藏 ❤️
echo     - 点击 ⬆️ 按钮: 下一张
echo     - 空格键/方向键↑: 下一张
echo.
echo  ⚙️ 配置 LLM (可选):
echo     设置环境变量 DEEPSEEK_API_KEY 或 OPENAI_API_KEY
echo     以启用无限内容生成功能
echo.
echo  🛑 关闭服务: 关闭两个弹出的命令行窗口即可
echo.
echo ══════════════════════════════════════
echo.

:: 自动打开浏览器
timeout /t 2 /nobreak >nul
start http://localhost:5173

pause
