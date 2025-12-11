# BookRe VPS 部署指南 2024

> **最后更新**: 2024-12-11  
> **适用版本**: BookRe v2.0+ (含自动音频清理、移动端UI优化、设备同步等功能)

---

## 📋 部署前准备

### 环境要求

**VPS 环境**:
- 操作系统: Ubuntu 20.04+ / Debian 11+
- Node.js: v18.0+
- Python: 3.8+
- Nginx: 最新稳定版
- pnpm: v8.0+ (必需)
- Git: 已配置

**本地环境**:
- Git
- 对应的 SSH 密钥已配置

---

## 🚀 首次部署流程

### 步骤 1: 准备 VPS 环境

```bash
# 1.1 安装 Node.js (使用 NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 1.2 安装 pnpm (重要!)
npm install -g pnpm

# 1.3 安装 Python 和 pip
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 1.4 安装 Nginx
sudo apt install -y nginx

# 1.5 验证安装
node -v
pnpm -v
python3 --version
nginx -v
```

### 步骤 2: 克隆项目到 VPS

```bash
# 2.1 创建项目目录
sudo mkdir -p /var/www
cd /var/www

# 2.2 克隆仓库 (替换为你的仓库地址)
sudo git clone https://github.com/YOUR_USERNAME/bookre.git
sudo chown -R $USER:$USER /var/www/bookre

# 2.3 进入项目
cd /var/www/bookre
```

### 步骤 3: 后端环境配置

```bash
# 3.1 进入后端目录
cd /var/www/bookre/backend

# 3.2 安装 Python 依赖
pip3 install -r requirements.txt

# 3.3 测试后端启动 (确保能正常运行)
python3 app.py
# 按 Ctrl+C 停止测试
```

**重要**: 后端会自动创建以下目录，无需手动创建：
- `data/covers` - 封面图片
- `data/audio` - TTS 音频 (自动清理>30分钟)
- `data/books` - 书籍数据
- `temp` - 临时文件
- `logs` - 日志文件

### 步骤 4: 前端构建

```bash
# 4.1 返回项目根目录
cd /var/www/bookre

# 4.2 安装前端依赖
pnpm install

# 4.3 构建生产版本
pnpm run build
```

### 步骤 5: 配置 Nginx

```bash
# 5.1 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/bookre

# 5.2 粘贴以下配置（修改 YOUR_DOMAIN）
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN;  # 例如: bookre.example.com

    # 前端静态文件
    location / {
        root /var/www/bookre/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源 (封面、音频)
    location /covers/ {
        alias /var/www/bookre/backend/data/covers/;
        expires 7d;
    }

    location /audio/ {
        alias /var/www/bookre/backend/data/audio/;
        expires 1h;
    }
}
```

```bash
# 5.3 启用站点
sudo ln -s /etc/nginx/sites-available/bookre /etc/nginx/sites-enabled/

# 5.4 测试配置
sudo nginx -t

# 5.5 重启 Nginx
sudo systemctl restart nginx
```

### 步骤 6: 启动后端服务

```bash
# 6.1 进入后端目录
cd /var/www/bookre/backend

# 6.2 后台启动 (nohup 方式)
nohup python3 app.py > logs/backend.log 2>&1 &

# 6.3 记录进程 ID
echo $! > /tmp/bookre-backend.pid

# 6.4 验证服务
curl http://localhost:8000/api/health
# 应该返回: {"status":"healthy","service":"bookre-api"}
```

### 步骤 7: 赋予脚本执行权限

```bash
cd /var/www/bookre
chmod +x deploy-vps.sh
chmod +x update.sh
```

---

## 🔄 日常更新流程

### 使用一键更新脚本 (推荐)

```bash
cd /var/www/bookre
./update.sh
```

**脚本自动完成**:
1. Git pull 拉取最新代码
2. 更新 Python 依赖
3. 重启后端服务
4. 构建前端资源 (pnpm)
5. 刷新 Nginx

### 手动更新流程

```bash
# 1. 拉取代码
cd /var/www/bookre
git pull origin main

# 2. 更新后端依赖 (如有变化)
cd backend
pip3 install -r requirements.txt

# 3. 重启后端
pkill -f "python3 app.py"
nohup python3 app.py > logs/backend.log 2>&1 &

# 4. 构建前端
cd /var/www/bookre
pnpm install
pnpm run build

# 5. 刷新 Nginx
sudo systemctl reload nginx
```

---

## 📊 服务管理

### 查看服务状态

```bash
# 后端进程
ps aux | grep "python3 app.py"

# 端口占用
lsof -i :8000

# 实时日志
tail -f /var/www/bookre/backend/logs/backend.log

# 错误日志
grep ERROR /var/www/bookre/backend/logs/backend.log | tail -20
```

### 重启服务

```bash
# 方法 1: 使用 update.sh
./update.sh

# 方法 2: 手动重启
pkill -f "python3 app.py"
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &
```

### 清理音频缓存 (可选)

```bash
# 后端会自动每10分钟清理超过30分钟的音频文件
# 手动清理所有音频:
rm -rf /var/www/bookre/backend/data/audio/*.mp3
```

---

## 🔧 故障排查

### 问题 1: 端口被占用

```bash
# 查找占用进程
sudo lsof -ti:8000

# 强制停止
sudo kill -9 $(sudo lsof -ti:8000)
```

### 问题 2: 权限问题

```bash
# 修复项目权限
sudo chown -R $USER:$USER /var/www/bookre
chmod -R 755 /var/www/bookre
```

### 问题 3: pnpm 命令未找到

```bash
# 重新安装 pnpm
npm install -g pnpm

# 验证
pnpm -v
```

### 问题 4: 前端 404 错误

```bash
# 1. 检查构建输出
ls -la /var/www/bookre/dist/

# 2. 重新构建
cd /var/www/bookre
pnpm install
pnpm run build

# 3. 检查 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx
```

### 问题 5: Python 模块缺失

```bash
cd /var/www/bookre/backend
pip3 install -r requirements.txt --upgrade
```

### 问题 6: TTS 功能异常

```bash
# 检查 EasyVoice 服务 (如果使用)
# 或者检查 Edge-TTS 网络连接

# 查看 TTS 相关日志
grep -i "tts\|voice" /var/www/bookre/backend/logs/backend.log | tail -30
```

---

## ⚡ 性能优化建议

### 1. 使用 PM2 管理进程 (推荐)

```bash
# 安装 PM2
npm install -g pm2

# 启动后端
cd /var/www/bookre/backend
pm2 start app.py --name bookre-backend --interpreter python3

# 保存配置
pm2 save

# 自动启动
pm2 startup
# 执行输出的命令

# 常用命令
pm2 status              # 查看状态
pm2 logs bookre-backend # 实时日志
pm2 restart bookre-backend  # 重启
pm2 stop bookre-backend     # 停止
```

使用 PM2 后，更新流程简化为:
```bash
cd /var/www/bookre
git pull
pnpm run build
pm2 restart bookre-backend
sudo systemctl reload nginx
```

### 2. 启用 Gzip 压缩

在 Nginx 配置中添加：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 3. 配置 HTTPS (推荐)

```bash
# 使用 Certbot 自动配置
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN
```

---

## 📝 检查清单

**部署前**:
- [ ] VPS 已安装 Node.js (v18+)
- [ ] VPS 已安装 pnpm
- [ ] VPS 已安装 Python 3.8+
- [ ] VPS 已安装 Nginx
- [ ] SSH 密钥已配置
- [ ] Git 仓库可访问

**首次部署后**:
- [ ] 后端健康检查通过 (`/api/health`)
- [ ] 前端页面可访问
- [ ] Nginx 配置正确
- [ ] 日志文件正常写入
- [ ] TTS 功能正常

**每次更新后**:
- [ ] Git pull 成功
- [ ] 后端重启成功
- [ ] 前端构建完成
- [ ] Nginx 重载成功
- [ ] 应用功能正常

---

## 🆘 常见命令速查

```bash
# === 服务管理 ===
./update.sh                    # 一键更新
ps aux | grep "python3 app.py" # 查看后端进程
tail -f backend/logs/backend.log  # 实时日志

# === Git 操作 ===
git pull origin main           # 拉取最新代码
git status                     # 查看状态
git log -3                     # 查看最近3次提交

# === 构建部署 ===
pnpm install                   # 安装依赖
pnpm run build                 # 构建前端
sudo systemctl reload nginx    # 重载 Nginx

# === 故障排查 ===
sudo lsof -ti:8000            # 查看端口占用
sudo nginx -t                  # 测试 Nginx 配置
curl http://localhost:8000/api/health  # 健康检查
```

---

## 🎯 与旧版部署的区别

**新版改进**:
1. ✅ 使用 **pnpm** 替代 npm (更快、更省空间)
2. ✅ **自动创建目录** (app.py 内置，无需手动)
3. ✅ **自动清理音频** (每10分钟清理>30分钟的文件)
4. ✅ 提供 **update.sh** 简化日常更新
5. ✅ 移动端 UI 已优化 (FAB、目录滚动)
6. ✅ 多设备进度同步支持

**兼容性**:
- 新版部署不会影响现有的 `deploy-vps.sh`
- `update.sh` 可用于日常快速迭代
- 旧的手动部署方式依然有效

---

## 📞 技术支持

如遇问题，请提供：
1. 错误信息截图
2. 后端日志: `tail -100 /var/www/bookre/backend/logs/backend.log`
3. Nginx 错误日志: `sudo tail -50 /var/log/nginx/error.log`
4. 系统信息: `uname -a` 和 `python3 --version`
