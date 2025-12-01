# Edge-TTS 网络连接配置指南

## 步骤 1：诊断网络连接

运行诊断脚本检查网络状态：

```bash
cd f:\bookre\backend
python diagnose_edge_network.py
```

---

## 步骤 2：根据诊断结果采取行动

### 情况 A：网络连接正常
如果诊断显示所有测试通过，说明网络没问题，可能是代码层面的问题。

**解决方案：**
1. 清空音频缓存
2. 重启后端
3. 测试语音播放

### 情况 B：无法访问 Microsoft 服务
如果诊断显示无法连接到 Microsoft TTS 服务器。

**解决方案（选择其一）：**

#### 方案 1：使用系统代理
1. 在 Windows 设置中配置代理
2. 设置环境变量：
   ```bash
   set HTTP_PROXY=http://your-proxy:port
   set HTTPS_PROXY=http://your-proxy:port
   ```
3. 重启后端

#### 方案 2：使用 VPN
1. 连接 VPN
2. 确保能访问国外网站
3. 重启后端

### 情况 C：防火墙阻止
如果诊断显示端口被阻止。

**解决方案：**
1. 打开 Windows Defender 防火墙
2. 允许 Python 访问网络
3. 添加入站规则允许相关端口

---

## 步骤 3：验证修复

运行测试脚本：
```bash
cd f:\bookre\backend
python test_edge_connectivity.py
```

如果看到 "✅ 成功！Edge-TTS 可以正常工作"，说明配置成功！

---

## 步骤 4：享受多种语音

1. 重启后端
2. 刷新浏览器
3. 选择不同的语音并播放
4. 每种语音的音色应该明显不同

---

## 故障排除

### 问题：诊断脚本报错
**原因：** Python 环境问题  
**解决：** 重新安装依赖 `pip install edge-tts requests`

### 问题：测试一直超时
**原因：** 网络速度慢或被限制  
**解决：** 更换网络或使用代理/VPN

### 问题：403 Forbidden
**原因：** IP 被 Microsoft 限制  
**解决：** 更换 IP 或使用代理

---

## 技术说明

Edge-TTS 需要连接到：
- **域名：** `speech.platform.bing.com`
- **协议：** WebSocket (WSS)
- **端口：** 443 (HTTPS)

如果您的网络环境限制访问这些服务，Edge-TTS 将无法工作。
