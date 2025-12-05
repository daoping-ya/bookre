# BookRe 完整部署指南（终极版）

## 问题根源与解决

### 问题分析
1. **目录缺失**：FastAPI 的 `StaticFiles` 要求目录必须存在
2. **日志路径**：Bash 重定向不会自动创建父目录

### 永久解决方案
已修改 `app.py`，在启动时自动创建所有必需目录。

---

## 部署流程（完整版）

### 一、本地准备

#### 1. 提交代码
```bash
cd f:\bookre

# 添加所有更改（包括新的 app.py 和部署脚本）
git add .

# 提交
git commit -m "fix: 自动创建必需目录，优化VPS部署流程"

# 推送
git push origin main
```

---

### 二、VPS 部署（一键脚本）

#### 1. 上传部署脚本（首次）
```bash
# 在 VPS 上执行
cd /var/www/bookre
git pull origin main

# 赋予执行权限
chmod +x deploy-vps.sh
```

#### 2. 执行部署
```bash
# 在 VPS 上执行
cd /var/www/bookre
./deploy-vps.sh
```

脚本会自动完成：
- ✅ 拉取最新代码
- ✅ 更新依赖
- ✅ 创建所有必需目录
- ✅ 构建前端
- ✅ 停止旧进程
- ✅ 启动新进程
- ✅ 验证服务
- ✅ 重载 Nginx

---

### 三、手动部署（如果脚本失败）

#### 1. 拉取代码
```bash
cd /var/www/bookre
git pull origin main
```

#### 2. 更新后端依赖
```bash
cd backend
pip3 install -r requirements.txt
```

#### 3. 创建目录（现在不需要了，但保险起见）
```bash
mkdir -p data/{covers,audio,books}
mkdir -p temp
mkdir -p logs
```

#### 4. 构建前端
```bash
cd /var/www/bookre
npm install
npm run build
```

#### 5. 重启后端
```bash
# 停止旧进程
pkill -f "python3.*backend/app.py"

# 启动新进程
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &

# 记录 PID
echo $! > /tmp/bookre-backend.pid
```

#### 6. 重载 Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. 验证
```bash
# 检查进程
ps aux | grep "python3.*app.py"

# 检查 API
curl http://localhost:8000/api/health

# 查看日志
tail -f /var/www/bookre/backend/logs/backend.log
```

---

## 常用维护命令

### 查看服务状态
```bash
# 后端进程
ps aux | grep "python3.*app.py"

# 端口占用
lsof -i :8000

# 查看日志
tail -f /var/www/bookre/backend/logs/backend.log
```

### 重启服务
```bash
# 使用脚本（推荐）
cd /var/www/bookre
./deploy-vps.sh

# 或手动
pkill -f "python3.*backend/app.py"
cd /var/www/bookre/backend
nohup python3 app.py > logs/backend.log 2>&1 &
```

### 查看最近错误
```bash
# 最后 50 行日志
tail -50 /var/www/bookre/backend/logs/backend.log

# 只看错误
grep -i error /var/www/bookre/backend/logs/backend.log | tail -20
```

---

## 故障排查

### 问题：端口被占用
```bash
# 查找占用进程
sudo lsof -ti:8000

# 强制杀死
sudo lsof -ti:8000 | xargs kill -9
```

### 问题：权限不足
```bash
# 修复项目权限
sudo chown -R $USER:$USER /var/www/bookre
chmod -R 755 /var/www/bookre
```

### 问题：模块缺失
```bash
cd /var/www/bookre/backend
pip3 install -r requirements.txt --upgrade
```

### 问题：前端 404
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查构建输出
ls -la /var/www/bookre/dist/

# 重新构建
cd /var/www/bookre
npm run build
```

---

## 升级到 PM2（可选，更省心）

### 安装 PM2
```bash
npm install -g pm2
```

### 首次启动
```bash
cd /var/www/bookre/backend
pm2 start app.py --name bookre-backend --interpreter python3
pm2 save
pm2 startup  # 按提示执行命令
```

### 以后的部署
```bash
cd /var/www/bookre
git pull
npm run build
pm2 restart bookre-backend
sudo systemctl reload nginx
```

### PM2 管理命令
```bash
pm2 status              # 查看状态
pm2 logs bookre-backend # 查看日志
pm2 restart bookre-backend  # 重启
pm2 stop bookre-backend     # 停止
pm2 delete bookre-backend   # 删除
```

---

## 检查清单

部署前确认：
- [ ] 本地代码已提交并推送
- [ ] VPS 已拉取最新代码
- [ ] Python 依赖已更新
- [ ] 前端已构建
- [ ] 旧进程已停止
- [ ] 新进程已启动
- [ ] API 健康检查通过
- [ ] Nginx 已重载

---

## 总结

**现在的改进：**
1. `app.py` 会自动创建所有必需目录
2. 提供了一键部署脚本
3. 脚本包含完整的错误处理和验证

**不会再出现的错误：**
- ❌ `Directory 'data/audio' does not exist`
- ❌ `bash: logs/backend.log: No such file or directory`

**部署只需一条命令：**
```bash
./deploy-vps.sh
```
