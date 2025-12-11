# PM2 部署与管理指南

## 安装 PM2

### VPS 上安装

```bash
# 全局安装 PM2
npm install -g pm2

# 验证安装
pm2 -v
```

---

## 首次配置

### 1. 上传配置文件

项目根目录已包含 `ecosystem.config.js`，确保已推送到 Git 仓库。

### 2. 在 VPS 上拉取配置

```bash
cd /var/www/bookre
git pull origin main
```

### 3. 首次启动

```bash
# 方法 1: 使用配置文件启动
pm2 start ecosystem.config.js

# 方法 2: 直接启动
cd /var/www/bookre/backend
pm2 start app.py --name bookre-backend --interpreter python3

# 保存 PM2 配置
pm2 save

# 设置开机自启动
pm2 startup
# 执行输出的命令 (通常是一条 sudo 命令)
```

### 4. 验证运行

```bash
pm2 status
pm2 logs bookre-backend
```

---

## 日常部署

### 使用 PM2 部署脚本（推荐）

```bash
cd /var/www/bookre
chmod +x deploy-pm2.sh
./deploy-pm2.sh
```

**脚本自动完成**：
1. 拉取最新代码
2. 更新后端依赖
3. 构建前端
4. 重启 PM2 服务
5. 重载 Nginx

### 手动更新流程

```bash
# 1. 拉取代码
cd /var/www/bookre
git pull

# 2. 更新依赖 (如有变化)
cd backend
pip3 install -r requirements.txt

# 3. 构建前端
cd /var/www/bookre
pnpm install
pnpm run build

# 4. 重启 PM2
pm2 restart bookre-backend

# 5. 重载 Nginx
sudo systemctl reload nginx
```

---

## PM2 常用命令

### 进程管理

```bash
# 查看所有进程
pm2 status

# 启动应用
pm2 start ecosystem.config.js
# 或
pm2 start bookre-backend

# 停止应用
pm2 stop bookre-backend

# 重启应用
pm2 restart bookre-backend

# 删除应用
pm2 delete bookre-backend

# 重载应用 (0秒停机)
pm2 reload bookre-backend
```

### 日志管理

```bash
# 实时查看所有日志
pm2 logs

# 查看特定应用日志
pm2 logs bookre-backend

# 查看最近 100 行日志
pm2 logs bookre-backend --lines 100

# 清空日志
pm2 flush

# 查看错误日志
pm2 logs bookre-backend --err
```

### 监控与信息

```bash
# 详细信息
pm2 show bookre-backend

# 监控面板
pm2 monit

# 资源占用
pm2 list
```

### 配置管理

```bash
# 保存当前进程列表
pm2 save

# 恢复保存的进程
pm2 resurrect

# 清空保存的进程
pm2 cleardump

# 更新 PM2
pm2 update
```

---

## 开机自启动

### 设置自启动

```bash
# 生成启动脚本
pm2 startup

# 执行输出的命令，例如：
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u your_user --hp /home/your_user

# 保存当前进程列表
pm2 save
```

### 取消自启动

```bash
pm2 unstartup systemd
```

---

## 故障排查

### 应用无法启动

```bash
# 查看详细错误
pm2 logs bookre-backend --err --lines 50

# 尝试手动启动测试
cd /var/www/bookre/backend
python3 app.py

# 检查 PM2 配置
cat /var/www/bookre/ecosystem.config.js
```

### 内存占用过高

```bash
# 查看内存使用
pm2 list

# 重启应用
pm2 restart bookre-backend

# 调整内存限制 (在 ecosystem.config.js 中)
# max_memory_restart: '500M'
```

### 日志文件过大

```bash
# 安装日志轮转
pm2 install pm2-logrotate

# 配置轮转
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

---

## 与手动启动的对比

### PM2 优势

✅ 自动重启 (崩溃后)  
✅ 开机自启动  
✅ 日志管理  
✅ 实时监控  
✅ 零停机重载  
✅ 统一管理  

### 手动启动 (nohup)

⚠️ 手动管理进程  
⚠️ 需要手动重启  
⚠️ 日志需手动查看  
⚠️ 崩溃后不会自动恢复  

---

## 迁移指南

### 从 nohup 迁移到 PM2

```bash
# 1. 停止现有进程
pkill -f "python3 app.py"

# 2. 安装 PM2
npm install -g pm2

# 3. 启动 PM2
cd /var/www/bookre
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # 执行输出的命令

# 4. 验证
pm2 status
pm2 logs bookre-backend
```

---

## 生产环境最佳实践

1. **日志轮转**: 安装 `pm2-logrotate`
2. **监控告警**: 配置 PM2 Plus (可选)
3. **定期备份**: `pm2 save` 定期保存配置
4. **资源限制**: 设置 `max_memory_restart`
5. **健康检查**: 定期运行 `curl http://localhost:8000/api/health`

---

## 快速参考

```bash
# === 部署流程 ===
git pull
pnpm run build
pm2 restart bookre-backend
sudo systemctl reload nginx

# === 日常监控 ===
pm2 status              # 查看状态
pm2 logs bookre-backend # 查看日志
pm2 monit               # 实时监控

# === 故障处理 ===
pm2 restart bookre-backend  # 重启
pm2 logs --err              # 查看错误
pm2 flush                   # 清空日志
```

---

## ecosystem.config.js 配置说明

```javascript
module.exports = {
  apps: [{
    name: 'bookre-backend',          // 应用名称
    script: 'app.py',                // 脚本路径
    cwd: './backend',                // 工作目录
    interpreter: 'python3',          // Python 解释器
    instances: 1,                    // 实例数量
    autorestart: true,               // 自动重启
    watch: false,                    // 不监听文件变化
    max_memory_restart: '500M',      // 内存限制
    error_file: './backend/logs/pm2-error.log',  // 错误日志
    out_file: './backend/logs/pm2-out.log',      // 输出日志
    min_uptime: '10s',               // 最小运行时间
    max_restarts: 10,                // 最大重启次数
    restart_delay: 4000              // 重启延迟
  }]
};
```

调整参数建议：
- **低配 VPS** (1G RAM): `max_memory_restart: '300M'`
- **中等 VPS** (2G RAM): `max_memory_restart: '500M'`
- **高配 VPS** (4G+ RAM): `max_memory_restart: '1G'`
