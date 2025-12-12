#!/bin/bash
echo "===== BookRe VPS 诊断脚本 ====="
echo "运行时间: $(date)"
echo ""

# 1. 检查服务状态
echo "[1] 服务状态:"
if command -v pm2 &> /dev/null; then
    pm2 status
else
    echo "PM2 未安装，尝试 systemctl..."
    systemctl status bookre 2>/dev/null || echo "服务未配置为 systemd"
fi
echo ""

# 2. 检查端口
echo "[2] 端口监听:"
ss -tlnp 2>/dev/null | grep -E "8000|3000|5173" || netstat -tlnp 2>/dev/null | grep -E "8000|3000|5173"
echo ""

# 3. 检查日志错误
echo "[3] 最近错误日志 (最后20行):"
if [ -f "/var/log/bookre/error.log" ]; then
    tail -20 /var/log/bookre/error.log
elif command -v pm2 &> /dev/null; then
    pm2 logs bookre --lines 20 --err 2>/dev/null || echo "无 PM2 日志"
else
    echo "未找到日志文件"
fi
echo ""

# 4. 检查数据目录权限
echo "[4] 数据目录权限:"
DATA_DIR="./data/books"
if [ -d "$DATA_DIR" ]; then
    ls -la "$DATA_DIR" | head -10
    echo "文件数量: $(ls -1 "$DATA_DIR" | wc -l)"
else
    echo "数据目录不存在: $DATA_DIR"
fi
echo ""

# 5. 检查磁盘空间
echo "[5] 磁盘空间:"
df -h . | head -5
echo ""

# 6. 测试 API
echo "[6] API 健康检查:"
curl -s http://localhost:8000/api/health 2>/dev/null || echo "后端未响应"
echo ""

# 7. 测试保存接口
echo "[7] 测试保存接口 (模拟):"
TEST_RESPONSE=$(curl -s -X PATCH http://localhost:8000/api/books/test \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"diagnose","progress": 10}' 2>/dev/null)
echo "$TEST_RESPONSE"
echo ""

# 8. 检查 Nginx 配置 (如果存在)
echo "[8] Nginx 代理配置:"
if [ -f "/etc/nginx/sites-enabled/bookre" ]; then
    grep -A5 "location /api" /etc/nginx/sites-enabled/bookre 2>/dev/null || echo "未找到 API 代理配置"
elif [ -f "/etc/nginx/conf.d/bookre.conf" ]; then
    grep -A5 "location /api" /etc/nginx/conf.d/bookre.conf 2>/dev/null
else
    echo "未找到 Nginx 配置"
fi
echo ""

echo "===== 诊断完成 ====="
echo ""
echo "常见问题排查:"
echo "1. 如果端口未监听: 检查服务是否启动"
echo "2. 如果保存失败: 检查 data/books 目录权限"
echo "3. 如果 API 404: 检查 Nginx 代理配置"
echo "4. 如果超时: 检查网络或防火墙"
