# BookRe 部署指南 (VPS)

本指南将指导您将 BookRe 部署到 Linux VPS (推荐 Ubuntu 20.04/22.04)。

## 1. 准备工作

### 1.1 服务器环境
确保您的 VPS 安装了以下软件：
- **Node.js** (v18+): 用于运行 EasyVoice 和构建前端。
- **Python** (v3.9+): 用于运行后端 API。
- **PNPM**: 包管理器。
- **PM2**: 进程守护。
- **Nginx**: 反向代理。
- **Git**: 拉取代码。

### 1.2 安装命令示例 (Ubuntu)
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3 python3-pip python3-venv -y

# 安装 Node.js (使用 nvm 或直接安装)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装全局工具
sudo npm install -g pnpm pm2
```

## 2. 部署步骤

### 2.1 获取代码
```bash
cd /var/www
git clone https://github.com/您的用户名/bookre.git
cd bookre
```

### 2.2 安装依赖
```bash
# 1. 安装所有依赖 (前端 + EasyVoice)
pnpm install

# 2. 安装 Python 后端依赖
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

### 2.3 构建前端
```bash
pnpm build
```
构建完成后，静态文件将位于 `dist` 目录。

### 2.4 启动服务 (PM2)
我们已经准备好了 `ecosystem.config.js`，直接启动即可：
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 2.5 配置 Nginx
1. 复制配置模板：
   ```bash
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/bookre
   ```
2. 编辑配置 (修改域名和路径)：
   ```bash
   sudo nano /etc/nginx/sites-available/bookre
   # 确保 root 指向 /var/www/bookre/dist
   # 确保 server_name 是您的域名
   ```
3. 启用配置并重启 Nginx：
   ```bash
   sudo ln -s /etc/nginx/sites-available/bookre /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 3. 验证部署
访问您的域名 (例如 `http://your_domain.com`)：
- 页面应正常加载。
- API 请求应成功 (检查网络面板)。
- TTS 功能应可用。

## 4. 常见问题
- **权限问题**: 确保 Nginx 有权读取 `dist` 目录。
- **端口冲突**: 确保 3000 和 8000 端口未被占用。
- **EasyVoice 内存**: 如果 VPS 内存较小 (<2GB)，EasyVoice 可能会 OOM。尝试增加 Swap。
