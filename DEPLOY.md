# BookRe 部署指南

## 一、本地提交到 GitHub

### 1. 检查修改状态
```bash
cd f:\bookre
git status
```

### 2. 添加所有更改
```bash
git add .
```

### 3. 提交更改
```bash
git commit -m "feat: 自动封面匹配、自定义设备ID、移动端UI重构

- 实现三层封面防护系统（本地提取/网络自动匹配/手动上传）
- 添加Google Books和OpenLibrary API集成
- 支持自定义设备ID进行跨设备同步
- 重构移动端UI（仿阅读App双层底部栏）
- 优化护眼模式配色（羊皮纸质感）
- 实现触摸滑动翻页和底部目录弹窗
- 优化封面存储为独立文件，提升加载性能"
```

### 4. 推送到 GitHub
```bash
git push origin main
```

如果是首次推送或设置远程仓库：
```bash
# 设置远程仓库（仅首次）
git remote add origin https://github.com/你的用户名/bookre.git

# 推送
git push -u origin main
```

---

## 二、VPS 部署流程

### 1. SSH 连接到 VPS
```bash
ssh your_user@your_vps_ip
```

### 2. 拉取最新代码
```bash
cd ~/bookre  # 或你的项目路径
git pull origin main
```

### 3. 更新后端依赖（如有新增）
```bash
cd backend
source venv/bin/activate  # 激活虚拟环境（如果使用）
pip install -r requirements.txt
```

### 4. 构建前端
```bash
cd ..  # 回到项目根目录
npm install  # 如果有新的依赖
npm run build
```

### 5. 重启服务

#### 方式 A：使用 systemd（推荐）
```bash
# 重启后端服务
sudo systemctl restart bookre-backend

# 重启前端服务（Nginx无需重启，只需刷新静态文件）
sudo systemctl reload nginx
```

#### 方式 B：使用 PM2
```bash
# 重启后端
pm2 restart bookre-backend

# Nginx 重新加载配置
sudo nginx -s reload
```

#### 方式 C：手动重启
```bash
# 停止旧进程
pkill -f "python.*app.py"

# 启动后端（后台运行）
cd backend
nohup python app.py > logs/backend.log 2>&1 &
```

### 6. 验证部署
```bash
# 检查后端服务状态
curl http://localhost:8000/api/health

# 检查进程
ps aux | grep python
ps aux | grep nginx
```

---

## 三、快捷部署脚本

### 本地：一键提交推送
创建 `deploy-local.sh`：
```bash
#!/bin/bash
echo "📦 开始提交代码..."
git add .
git commit -m "$1"
git push origin main
echo "✅ 代码已推送到 GitHub"
```

使用方式：
```bash
bash deploy-local.sh "feat: 添加新功能"
```

### VPS：一键部署
创建 `deploy-vps.sh`：
```bash
#!/bin/bash
set -e

echo "🚀 开始部署 BookRe..."

# 拉取代码
echo "📥 拉取最新代码..."
git pull origin main

# 更新依赖
echo "📦 更新后端依赖..."
cd backend
pip install -r requirements.txt -q

# 构建前端
echo "🔨 构建前端..."
cd ..
npm install --silent
npm run build

# 重启服务
echo "♻️ 重启服务..."
sudo systemctl restart bookre-backend
sudo systemctl reload nginx

# 验证
echo "✅ 验证部署..."
sleep 2
curl -s http://localhost:8000/api/health

echo "🎉 部署完成！"
```

使用方式：
```bash
bash deploy-vps.sh
```

---

## 四、常见问题排查

### 后端启动失败
```bash
# 查看日志
sudo journalctl -u bookre-backend -f

# 或查看错误日志
tail -f backend/logs/backend.log
```

### 前端404错误
```bash
# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 端口被占用
```bash
# 查找占用8000端口的进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>
```

---

## 五、回滚操作

如果新版本有问题，快速回滚：
```bash
# 回退到上一个提交
git reset --hard HEAD~1
git push -f origin main

# VPS上拉取回退版本
cd ~/bookre
git pull origin main --force

# 重新构建部署
npm run build
sudo systemctl restart bookre-backend
```

---

## 附录：systemd 服务配置示例

如果尚未配置 systemd，创建 `/etc/systemd/system/bookre-backend.service`：
```ini
[Unit]
Description=BookRe Backend API
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/your_user/bookre/backend
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable bookre-backend
sudo systemctl start bookre-backend
```
