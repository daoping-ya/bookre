#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的 TTS 功能测试脚本
测试从 API 调用到音频生成的完整流程
"""
import requests
import json
import os
import time

# 测试配置
API_BASE = "http://localhost:8000"
TEST_TEXT = "这是一个语音合成测试，请确保能够正常播放。"

def test_health():
    """测试后端健康状态"""
    print("=" * 50)
    print("1. 测试后端健康状态...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端返回异常状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端: {e}")
        print("   请确保后端已启动: python app.py")
        return False

def test_voice_list():
    """测试语音列表接口"""
    print("\n" + "=" * 50)
    print("2. 测试语音列表接口...")
    try:
        response = requests.get(f"{API_BASE}/api/voice/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            voices = data.get('voices', [])
            print(f"✅ 成功获取 {len(voices)} 个语音")
            print(f"   前3个语音: {[v['name'] for v in voices[:3]]}")
            return True
        else:
            print(f"❌ 获取语音列表失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_tts_stream():
    """测试流式 TTS"""
    print("\n" + "=" * 50)
    print("3. 测试流式 TTS 合成...")
    
    payload = {
        "text": TEST_TEXT,
        "voice_model": "zh-CN-XiaoxiaoNeural",
        "rate": "+0%",
        "volume": "+0%",
        "stream": True
    }
    
    print(f"   请求体: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/voice/synthesize",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        print(f"   状态码: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            output_file = "test_tts_output.mp3"
            total_bytes = 0
            
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
            
            file_size = os.path.getsize(output_file)
            print(f"✅ TTS 合成成功!")
            print(f"   音频文件: {output_file}")
            print(f"   文件大小: {file_size} 字节")
            
            if file_size > 1000:
                print("   ✅ 文件大小正常，应该包含有效音频")
                return True
            else:
                print("   ⚠️  文件太小，可能不是有效音频")
                return False
        else:
            print(f"❌ TTS 合成失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tts_file():
    """测试文件模式 TTS"""
    print("\n" + "=" * 50)
    print("4. 测试文件模式 TTS...")
    
    payload = {
        "text": "文件模式测试",
        "voice_model": "zh-CN-XiaoxiaoNeural",
        "rate": "+0%",
        "volume": "+0%",
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/voice/synthesize",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get('audio_url')
            print(f"✅ 文件模式成功")
            print(f"   音频URL: {audio_url}")
            return True
        else:
            print(f"❌ 文件模式失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("BookRe TTS 功能完整测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: 健康检查
    results.append(("后端健康检查", test_health()))
    
    if not results[0][1]:
        print("\n❌ 后端未启动，无法继续测试")
        return
    
    time.sleep(0.5)
    
    # 测试2: 语音列表
    results.append(("语音列表接口", test_voice_list()))
    time.sleep(0.5)
    
    # 测试3: 流式TTS
    results.append(("流式 TTS", test_tts_stream()))
    time.sleep(0.5)
    
    # 测试4: 文件TTS
    results.append(("文件模式 TTS", test_tts_file()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！TTS 功能正常工作")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
    print("=" * 50)

if __name__ == "__main__":
    main()
