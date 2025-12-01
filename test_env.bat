@echo off
chcp 65001 >nul
cls
echo ========================================
echo  环境快速测试
echo ========================================
echo.

echo 测试 1/3: Node.js
node --version
if %errorlevel% equ 0 (
    echo ✅ Node.js 正常
) else (
    echo ❌ Node.js 不可用
)
echo.

echo 测试 2/3: npm
npm --version
if %errorlevel% equ 0 (
    echo ✅ npm 正常
) else (
    echo ❌ npm 不可用
)
echo.

echo 测试 3/3: Python
python --version
if %errorlevel% equ 0 (
    echo ✅ Python 正常
) else (
    echo ⚠️ Python 未安装（可选）
)
echo.

echo ========================================
echo  测试完成
echo ========================================
echo.
echo 按任意键继续...
pause >nul
