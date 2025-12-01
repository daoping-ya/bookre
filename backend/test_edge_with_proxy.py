#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Edge-TTS 是否能通过代理工作
"""
import asyncio
import edge_tts
import os

async def test_edge_with_proxy():
    print("=" * 60)
    print("测试 Edge-TTS 通过代理连接")
    print("=" * 60)
    
    # 设置代理环境变量
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10808'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10808'
    
    print("\n已设置代理:")
    print(f"  HTTP_PROXY: {os.environ['HTTP_PROXY']}")
    print(f"  HTTPS_PROXY: {os.environ['HTTPS_PROXY']}")
    
    print("\n正在测试 Edge-TTS...")
    
    try:
        communicate = edge_tts.Communicate(
            "你好，这是Edge-TTS测试。",
            "zh-CN-XiaoxiaoNeural"
        )
        
        print("正在生成音频...")
        await communicate.save("test_with_proxy.mp3")
        
        import os as os_check
        if os_check.path.exists("test_with_proxy.mp3"):
            size = os_check.path.getsize("test_with_proxy.mp3")
            print(f"\n✅ 成功！Edge-TTS 可以通过代理工作")
            print(f"   文件: test_with_proxy.mp3")
            print(f"   大小: {size} bytes")
            print("\n【结论】Edge-TTS + 代理配置成功！")
            print("\n下一步：")
            print("1. 在后端代码中添加代理配置")
            print("2. 重启后端")
            print("3. 测试语音切换")
            return True
        else:
            print("\n❌ 失败：文件未生成")
            return False
            
    except Exception as e:
        print(f"\n❌ Edge-TTS 失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)[:200]}")
        print("\n【结论】Edge-TTS 即使通过代理也无法工作")
        print("\n可能原因：")
        print("1. edge-tts 库不支持代理")
        print("2. WebSocket 连接被阻止")
        print("3. 需要其他配置")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_edge_with_proxy())
    
    print("\n" + "=" * 60)
    if not result:
        print("\n建议：考虑使用本地 TTS 方案（VITS 等）")
    print("=" * 60)
