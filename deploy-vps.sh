#!/bin/bash
# BookRe VPS 一键部署脚本
# 适用于手动启动（非 systemd/PM2）

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   BookRe VPS 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 拉取最新代码
echo -e "${YELLOW}[1/7]${NC} 拉取最新代码..."
cd /var/www/bookre
git pull origin main
echo -e "${GREEN}✓${NC} 代码已更新"
echo ""

# 2. 安装/更新后端依赖
echo -e "${YELLOW}[2/7]${NC} 更新后端依赖..."
cd backend
pip3 install -r requirements.txt -q
echo -e "${GREEN}✓${NC} Python 依赖已更新"
echo ""

# 3. 创建必需的目录（冗余但保险）
echo -e "${YELLOW}[3/7]${NC} 检查目录结构..."
mkdir -p data/{covers,audio,books}
mkdir -p temp
mkdir -p logs
chmod -R 755 data temp logs
echo -e "${GREEN}✓${NC} 目录已就绪"
echo ""

# 4. 构建前端
echo -e "${YELLOW}[4/7]${NC} 构建前端..."
cd /var/www/bookre
pnpm install
pnpm run build
echo -e "${GREEN}✓${NC} 前端构建完成"
echo ""

# 5. 停止旧的后端进程
echo -e "${YELLOW}[5/7]${NC} 停止旧进程..."
OLD_PID=$(pgrep -f "python3.*backend/app.py" || echo "")
if [ -n "$OLD_PID" ]; then
    kill -9 $OLD_PID
    echo -e "${GREEN}✓${NC} 已停止旧进程 (PID: $OLD_PID)"
else
    echo -e "${YELLOW}⚠${NC} 未发现运行中的进程"
fi
sleep 1
echo ""

# 6. 启动新的后端进程
echo -e "${YELLOW}[6/7]${NC} 启动后端服务..."
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &
NEW_PID=$!
echo -e "${GREEN}✓${NC} 后端已启动 (PID: $NEW_PID)"
echo ""

# 7. 验证服务
echo -e "${YELLOW}[7/7]${NC} 验证服务..."
sleep 3

# 检查进程是否还在运行
if ps -p $NEW_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} 进程运行正常"
    
    # 检查 API 健康状态
    HEALTH_CHECK=$(curl -s http://localhost:8000/api/health || echo "failed")
    if [[ $HEALTH_CHECK == *"healthy"* ]]; then
        echo -e "${GREEN}✓${NC} API 健康检查通过"
    else
        echo -e "${RED}✗${NC} API 健康检查失败"
        echo -e "${YELLOW}查看日志:${NC} tail -f /var/www/bookre/backend/logs/backend.log"
    fi
else
    echo -e "${RED}✗${NC} 后端启动失败！"
    echo -e "${YELLOW}最近的错误日志:${NC}"
    tail -20 /var/www/bookre/backend/logs/backend.log
    exit 1
fi
echo ""

# 8. 重新加载 Nginx
echo -e "${YELLOW}[额外]${NC} 重新加载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✓${NC} Nginx 已重新加载"
echo ""

# 部署完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   🎉 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "后端进程: PID $NEW_PID"
echo "日志位置: /var/www/bookre/backend/logs/backend.log"
echo ""
echo "常用命令:"
echo "  查看日志: tail -f /var/www/bookre/backend/logs/backend.log"
echo "  查看进程: ps aux | grep 'python3.*app.py'"
echo "  停止服务: kill -9 $NEW_PID"
