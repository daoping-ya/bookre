# Node.js 安装指南

## 📥 下载 Node.js

### 方法1：官网下载（推荐）

1. **访问官网**：https://nodejs.org/
   
2. **选择版本**：
   - **LTS版本（推荐）**：长期支持版本，更稳定
     - 当前LTS：Node.js 18.x 或 20.x
   - Current版本：最新功能，适合尝鲜

3. **下载安装包**：
   - Windows 64位：`node-v18.x.x-x64.msi` 或 `node-v20.x.x-x64.msi`
   - Windows 32位：`node-v18.x.x-x86.msi`

### 方法2：国内镜像（下载更快）

- **淘宝镜像**：https://registry.npmmirror.com/binary.html?path=node/
- 选择对应版本的 `.msi` 文件下载

---

## 🔧 安装步骤

### 1. 运行安装程序

双击下载的 `.msi` 文件，启动安装向导。

### 2. 安装配置

按照以下步骤操作：

**第一步：欢迎界面**
- 点击 `Next` 继续

**第二步：许可协议**
- 勾选 `I accept the terms in the License Agreement`
- 点击 `Next`

**第三步：安装路径**
- 默认路径：`C:\Program Files\nodejs\`
- 建议保持默认，点击 `Next`

**第四步：功能选择**
- ✅ **全部默认勾选即可**
- 重要：确保勾选了以下选项：
  - Node.js runtime
  - npm package manager
  - Online documentation shortcuts
  - **Add to PATH**（非常重要！）

**第五步：工具安装（可选）**
- 如果出现"Automatically install the necessary tools"提示
- 建议勾选（会安装Python和Visual Studio构建工具）
- 点击 `Next`

**第六步：开始安装**
- 点击 `Install`
- 等待安装完成（约1-2分钟）

**第七步：完成安装**
- 点击 `Finish`

---

## ✅ 验证安装

### 1. 打开命令提示符

按下 `Win + R`，输入 `cmd`，按回车

### 2. 检查Node.js版本

```bash
node --version
```

应该显示类似：`v18.19.0` 或 `v20.10.0`

### 3. 检查npm版本

```bash
npm --version
```

应该显示类似：`10.2.3`

如果以上命令都正常显示版本号，说明安装成功！✅

---

## 🚀 安装后配置（可选但推荐）

### 配置npm国内镜像源（加速下载）

```bash
npm config set registry https://registry.npmmirror.com
```

验证配置：
```bash
npm config get registry
```

应该显示：`https://registry.npmmirror.com/`

---

## 📦 安装BookRe项目依赖

Node.js安装完成后，在BookRe项目目录执行：

### 方法1：使用启动脚本（最简单）

双击项目根目录的 `start.bat` 文件，脚本会自动：
- 检查环境
- 安装依赖
- 启动服务

### 方法2：手动安装

打开命令提示符，进入项目目录：

```bash
cd f:\bookre
npm install
```

等待安装完成（约2-5分钟），然后：

```bash
# 启动前端开发服务器
npm run dev

# 或启动Electron应用
npm run electron:dev
```

---

## 🔧 常见问题

### Q1: 提示"npm不是内部或外部命令"

**原因**：环境变量PATH未正确配置

**解决方法**：
1. 重启命令提示符（关闭后重新打开）
2. 如果仍不行，重启电脑
3. 手动检查环境变量：
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 在系统变量中找到`Path`
   - 确认包含：`C:\Program Files\nodejs\`

### Q2: npm install 速度很慢

**解决方法**：配置国内镜像源（见上方配置章节）

### Q3: npm install 报错 EACCES 或权限错误

**解决方法**：
1. 以管理员身份运行命令提示符
2. 或修改npm的全局安装路径

### Q4: 安装过程中杀毒软件报警

**解决方法**：
1. Node.js是安全的官方软件
2. 临时关闭杀毒软件或添加信任
3. 从官网下载确保文件安全

---

## 📞 需要帮助？

如果遇到其他问题：

1. **检查版本兼容性**：确保安装的是Node.js 18+
2. **重新安装**：完全卸载后重新安装
3. **查看日志**：npm安装失败时会显示详细错误信息

---

## 🎯 下一步

Node.js安装成功后，您可以：

1. ✅ 运行 `f:\bookre\start.bat` 启动BookRe阅读器
2. ✅ 或手动执行：
   ```bash
   cd f:\bookre
   npm install      # 安装依赖
   npm run dev      # 启动前端开发服务器
   ```

祝您使用愉快！📚
