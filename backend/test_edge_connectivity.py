#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Edge-TTS 是否能正常工作
"""
import asyncio
import edge_tts

async def test_edge_tts():
    print("=" * 60)
    print("测试 Edge-TTS 连接")
    print("=" * 60)
    
    try:
        print("\n正在尝试连接 Microsoft Edge TTS 服务...")
        communicate = edge_tts.Communicate(
            "你好，这是一个测试。",
            "zh-CN-XiaoxiaoNeural"
        )
        
        print("正在生成音频...")
        await communicate.save("test_edge.mp3")
        
        import os
        if os.path.exists("test_edge.mp3"):
            size = os.path.getsize("test_edge.mp3")
            print(f"\n✅ 成功！Edge-TTS 可以正常工作")
            print(f"   生成文件: test_edge.mp3")
            print(f"   文件大小: {size} bytes")
            print("\n【结论】Edge-TTS 服务可用，重启后端即可使用多种语音")
            return True
        else:
            print(f"\n❌ 失败：文件未生成")
            return False
            
    except Exception as e:
        print(f"\n❌ Edge-TTS 连接失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        print(f"\n【结论】Edge-TTS 服务不可用，需要配置网络或使用离线 TTS")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_edge_tts())
    print("\n" + "=" * 60)
    if not result:
        print("\n建议：")
        print("1. 检查网络连接")
        print("2. 如果在国内，可能需要配置代理或 VPN")
        print("3. 或者接受使用离线 TTS（所有语音音色相同）")
    print("=" * 60)
