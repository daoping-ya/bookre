#!/bin/bash
# BookRe PM2 部署脚本
# 使用 PM2 管理后端进程

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取脚本所在目录
PROJECT_ROOT=$(cd "$(dirname "$0")"; pwd)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   BookRe PM2 部署${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 拉取代码
echo -e "${YELLOW}[1/5] 拉取最新代码...${NC}"
cd "$PROJECT_ROOT"
git pull
echo -e "${GREEN}✓ 代码已更新${NC}"

# 2. 后端依赖
echo -e "${YELLOW}[2/5] 更新后端依赖...${NC}"
cd backend
pip3 install -r requirements.txt -q
echo -e "${GREEN}✓ Python 依赖已更新${NC}"

# 3. 前端构建
echo -e "${YELLOW}[3/5] 构建前端...${NC}"
cd "$PROJECT_ROOT"
pnpm install
pnpm run build
echo -e "${GREEN}✓ 前端已构建${NC}"

# 4. PM2 重启
echo -e "${YELLOW}[4/5] 重启 PM2 服务...${NC}"

# 检查 PM2 是否已启动该应用
if pm2 describe bookre-backend > /dev/null 2>&1; then
    echo "重启现有服务..."
    pm2 restart bookre-backend
else
    echo "首次启动服务..."
    pm2 start ecosystem.config.js
    pm2 save
fi

echo -e "${GREEN}✓ PM2 已重启${NC}"

# 5. Nginx 重载
echo -e "${YELLOW}[5/5] 重载 Nginx...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl reload nginx || echo -e "${YELLOW}⚠ Nginx reload 跳过${NC}"
else
    echo "跳过 Nginx (非 systemd)"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   🎉 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 显示状态
pm2 status
echo ""
echo "查看日志: pm2 logs bookre-backend"
echo "查看状态: pm2 status"
echo "重启服务: pm2 restart bookre-backend"
