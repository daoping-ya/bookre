@echo off
chcp 65001 >nul
cls
echo ==========================================
echo       BookRe 一键启动
echo ==========================================
echo.

cd /d "%~dp0"

:: 将 node_modules/.bin 添加到 PATH
set PATH=%PATH%;%~dp0node_modules\.bin

:: 清理旧进程，避免端口冲突
echo [0/3] 清理旧进程...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/3] 启动 EasyVoice (后台)...
start "EasyVoice Service" cmd /k "cd /d %~dp0packages\easyvoice && pnpm start"
timeout /t 8 /nobreak >nul

echo [2/3] 启动后端服务 (后台)...
start "BookRe Backend" cmd /k "cd backend && call venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端 (浏览器)...
start "BookRe Frontend" cmd.exe /K "cd /d %~dp0 && .\node_modules\.bin\vite.cmd"

echo.
echo ✅ 所有服务已启动！
echo.
echo 🌐 前端地址: http://localhost:5173
echo 🔧 后端地址: http://127.0.0.1:8000
echo 🎙️ EasyVoice: http://localhost:3000
echo.
echo 💡 提示: 窗口已保留以便查看报错信息
echo.
pause
