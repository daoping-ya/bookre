# BookRe 电子书阅读器

功能完善的桌面电子书阅读应用，支持 EPUB、TXT 格式，集成本地语音朗读功能。

## 核心功能

- 📚 **多格式支持**：EPUB、TXT 等主流电子书格式
- 📖 **流畅阅读**：智能分页、章节导航、进度保存
- 🔖 **书签管理**：添加书签、快速跳转
- 🔊 **语音朗读**：基于 Coqui TTS 的本地语音合成
- 🎨 **精美UI**：现代化设计、流畅动画、主题切换
- 💻 **跨平台**：Windows 桌面应用 + Web 版本

## 技术栈

### 前端
- **框架**：Electron + Vue.js 3 + Vite
- **状态管理**：Pinia
- **路由**：Vue Router
- **样式**：CSS3 + 现代设计系统

### 后端
- **框架**：FastAPI
- **数据库**：SQLite (本地) / PostgreSQL (Web版)
- **电子书解析**：ebooklib, BeautifulSoup
- **语音合成**：Coqui TTS

## 快速开始

### 前置要求
- Node.js >= 18
- Python >= 3.9
- pnpm (推荐) 或 npm

### 安装依赖
在项目根目录运行：
```bash
pnpm install
```

### 启动应用 (推荐)
双击运行根目录下的 **`start_all.bat`**。
它会自动启动所有服务：
1. EasyVoice TTS (端口 3000)
2. Python 后端 (端口 8000)
3. 前端应用 (端口 5173)

### 手动启动 (调试用)
如果需要单独启动服务，请在三个终端中分别运行：

**1. EasyVoice TTS:**
```bash
cd packages/easyvoice
pnpm start
```

**2. Python 后端:**
```bash
cd backend
python app.py
```

**3. 前端应用:**
```bash
pnpm dev
```

### 故障排除
- **依赖问题**: 如果启动失败，尝试运行 `pnpm install`。
- **端口冲突**: 确保 3000, 8000, 5173 端口未被占用。
- **Vite 错误**: 如果提示 `vite` 未找到，请使用 `start_all.bat` 启动，它会自动配置环境。

## 部署

详细的 VPS 部署指南请参考 [DEPLOY.md](./DEPLOY.md)。
主要步骤包括：
1. 准备 VPS 环境 (Node.js, Python, Nginx)
2. 拉取代码并安装依赖
3. 构建前端
4. 配置 Nginx (注意默认端口为 **5173**)

## 项目结构

```
bookre/
├── electron/              # Electron 主进程
│   ├── main.js
│   └── preload.js
├── src/                   # Vue.js 前端
│   ├── views/            # 页面视图
│   ├── components/       # Vue 组件
│   ├── store/            # Pinia 状态管理
│   ├── assets/           # 静态资源
│   └── router/           # 路由配置
├── backend/              # Python 后端
│   ├── app.py           # FastAPI 入口
│   ├── services/        # 业务逻辑
│   │   ├── epub_parser.py
│   │   ├── txt_parser.py
│   │   └── tts_engine.py
│   └── database.py      # 数据库模型
└── public/              # 公共资源
```

## 开发路线图

### ✅ 阶段 1：MVP（已完成基础架构）
- [x] 项目初始化
- [x] 基础UI框架
- [ ] EPUB/TXT 解析
- [ ] 分页阅读
- [ ] 进度保存

### ⏳ 阶段 2：增强功能
- [ ] 语音朗读集成
- [ ] 书签功能
- [ ] 主题切换
- [ ] UI 美化

### 📅 阶段 3：部署扩展
- [ ] Windows 应用打包
- [ ] Web 版本开发
- [ ] VPS 部署
- [ ] 跨设备同步

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
