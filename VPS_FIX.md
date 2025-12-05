# BookRe VPS 部署修复指南（手动启动版本）

## ⚠️ 重要说明

**您的后端是通过手动运行 Python 脚本启动的，不是 systemd 服务！**

所以 `sudo systemctl restart bookre-backend` 会报错，因为这个服务根本不存在。

---

## 当前问题修复

### 问题 1：`Directory 'directory' does not exist`

**原因：** 缺少必需的目录

**解决方法（在 VPS 上执行）：**

```bash
cd /var/www/bookre/backend

# 创建目录
mkdir -p data/covers
mkdir -p data/audio  
mkdir -p data/books
mkdir -p temp

# 检查是否创建成功
ls -la data/
```

### 问题 2：如何重启后端？

**❌ 错误做法：**
```bash
sudo systemctl restart bookre-backend  # 这个服务不存在！
```

**✅ 正确做法：**

#### 方法 1：杀死旧进程并重新启动

```bash
# 1. 找到并停止旧的 Python 进程
ps aux | grep "python.*app.py"
kill -9 <进程ID>

# 或者一键杀死所有 Python 后端进程
pkill -f "python.*app.py"

# 2. 启动新的后端进程（后台运行）
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &

# 3. 验证是否启动成功
curl http://localhost:8000/api/health
```

#### 方法 2：使用一键脚本

创建 `/var/www/bookre/backend/restart.sh`：

```bash
#!/bin/bash
echo "🛑 停止旧进程..."
pkill -f "python.*app.py"
sleep 1

echo "🚀 启动新进程..."
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &

sleep 2
echo "✅ 验证服务..."
curl -s http://localhost:8000/api/health && echo " 服务正常!" || echo " 启动失败!"

echo "📋 当前进程："
ps aux | grep "python.*app.py" | grep -v grep
```

使用方式：
```bash
cd /var/www/bookre/backend
chmod +x restart.sh
./restart.sh
```

---

## 完整部署流程（正确版本）

### 1. 本地提交代码
```bash
cd f:\bookre
git add .
git commit -m "feat: 自动封面匹配与UI重构"
git push origin main
```

### 2. VPS 拉取代码
```bash
cd /var/www/bookre
git pull origin main
```

### 3. 确保目录存在
```bash
cd backend
mkdir -p data/{covers,audio,books} temp
```

### 4. 更新依赖（如有新增）
```bash
pip3 install -r requirements.txt
```

### 5. 构建前端
```bash
cd /var/www/bookre
npm install
npm run build
```

### 6. 重启后端
```bash
cd /var/www/bookre/backend

# 停止旧进程
pkill -f "python.*app.py"

# 启动新进程
nohup python3 app.py > logs/backend.log 2>&1 &

# 验证
curl http://localhost:8000/api/health
```

### 7. 重新加载 Nginx（这个才用 systemctl）
```bash
sudo nginx -t  # 检查配置
sudo systemctl reload nginx  # 重新加载
```

---

## 查看日志

### 后端日志
```bash
# 实时查看
tail -f /var/www/bookre/backend/logs/backend.log

# 查看错误
grep -i error /var/www/bookre/backend/logs/backend.log
```

### Nginx 日志
```bash
# 访问日志
sudo tail -f /var/log/nginx/access.log

# 错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 快捷命令汇总

```bash
# 查看后端是否在运行
ps aux | grep "python.*app.py"

# 查看端口占用
lsof -i :8000

# 重启后端（完整版）
pkill -f "python.*app.py" && cd /var/www/bookre/backend && nohup python3 app.py > logs/backend.log 2>&1 &

# 重新加载 Nginx
sudo systemctl reload nginx

# 检查健康状态
curl http://localhost:8000/api/health
```

---

## 可选：升级到 PM2 管理（推荐）

如果觉得手动管理麻烦，可以升级到 PM2：

```bash
# 安装 PM2
npm install -g pm2

# 首次启动
cd /var/www/bookre/backend
pm2 start app.py --name bookre --interpreter python3
pm2 save
pm2 startup  # 按提示执行命令

# 以后就可以用简单的命令了
pm2 restart bookre      # 重启
pm2 logs bookre         # 查看日志
pm2 status              # 查看状态
```

**使用 PM2 后的部署流程：**
```bash
git pull
npm run build
pm2 restart bookre
sudo systemctl reload nginx
```

简单多了！
