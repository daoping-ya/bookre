#!/bin/bash
# BookRe 一键更新脚本 (update.sh)
# 自动识别当前目录，从 Git 拉取并重启服务

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取脚本所在目录作为项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")"; pwd)
echo -e "${GREEN}项目路径: ${PROJECT_ROOT}${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   BookRe 快速迭代更新${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 拉取代码
echo -e "${YELLOW}[1/4] 拉取最新代码...${NC}"
cd "$PROJECT_ROOT"
git pull
echo -e "${GREEN}✓ Git Pull 完成${NC}"

# 2. 后端处理
echo -e "${YELLOW}[2/4] 更新后端环境...${NC}"
if [ -d "backend" ]; then
    cd backend
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt -q
    fi
    # 确保目录存在
    mkdir -p data/{covers,audio,books} temp logs
    
    # 停止旧进程
    echo "停止旧服务..."
    pkill -f "python3 app.py" || true
    
    # 启动新进程
    echo "启动新服务..."
    nohup python3 app.py > logs/backend.log 2>&1 &
    NEW_PID=$!
    echo -e "${GREEN}✓ 后端已重启 (PID: $NEW_PID)${NC}"
    cd ..
else
    echo -e "${RED}❌ 错误: 未找到 backend 目录${NC}"
    exit 1
fi

# 3. 前端构建
echo -e "${YELLOW}[3/4] 构建前端资源...${NC}"
npm install --silent
npm run build
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 4. Nginx (可选)
echo -e "${YELLOW}[4/4] 刷新 Nginx...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl reload nginx || echo -e "${YELLOW}⚠ Nginx reload skipped (no sudo/perm)${NC}"
else
    echo "跳过 Nginx reload (非 systemd 环境)"
fi

echo ""
echo -e "${GREEN}🎉 更新完成！${NC}"
