#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Edge-TTS 详细诊断脚本
"""
import asyncio
import edge_tts
import sys
import traceback

async def test_edge_tts():
    print("=" * 60)
    print("Edge-TTS 详细诊断")
    print("=" * 60)
    
    # 测试1: 检查版本
    print("\n1. 检查 edge-tts 版本")
    try:
        import pkg_resources
        version = pkg_resources.get_distribution("edge-tts").version
        print(f"   edge-tts 版本: {version}")
    except:
        print("   无法获取版本信息")
    
    # 测试2: 列出可用语音
    print("\n2. 尝试获取可用语音列表")
    try:
        voices = await edge_tts.list_voices()
        print(f"   ✅ 成功获取 {len(voices)} 个语音")
        print(f"   前3个语音: {[v['ShortName'] for v in voices[:3]]}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 测试3: 简单文本合成（保存文件）
    print("\n3. 尝试合成简单文本（文件模式）")
    try:
        test_text = "你好，这是一个测试。"
        communicate = edge_tts.Communicate(
            text=test_text,
            voice="zh-CN-XiaoxiaoNeural"
        )
        await communicate.save("test_edge_output.mp3")
        import os
        if os.path.exists("test_edge_output.mp3"):
            size = os.path.getsize("test_edge_output.mp3")
            print(f"   ✅ 成功生成音频文件，大小: {size} bytes")
        else:
            print("   ❌ 文件未生成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 测试4: 流式合成
    print("\n4. 尝试流式合成")
    try:
        test_text = "流式测试文本"
        communicate = edge_tts.Communicate(
            text=test_text,
            voice="zh-CN-XiaoxiaoNeural"
        )
        chunk_count = 0
        total_bytes = 0
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunk_count += 1
                total_bytes += len(chunk["data"])
        
        print(f"   ✅ 成功接收 {chunk_count} 个音频块，总大小: {total_bytes} bytes")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 测试5: 测试不同语音模型
    print("\n5. 测试不同语音模型")
    test_voices = [
        "zh-CN-XiaoxiaoNeural",  # 女声
        "zh-CN-YunxiNeural",      # 男声
        "zh-CN-liaoning-XiaobeiNeural"  # 方言
    ]
    
    for voice in test_voices:
        try:
            communicate = edge_tts.Communicate(
                text="测试",
                voice=voice
            )
            chunk_count = 0
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunk_count += 1
            print(f"   ✅ {voice}: 成功 ({chunk_count} 块)")
        except Exception as e:
            print(f"   ❌ {voice}: 失败 - {type(e).__name__}: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_edge_tts())
