#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试 TTS API 的请求体接收
"""
import requests
import json

url = "http://localhost:8000/api/voice/synthesize"

# 构建请求
payload = {
    "text": "这是一个简短的测试",
    "voice_model": "zh-CN-XiaoxiaoNeural",
    "rate": "+0%",
    "volume": "+0%",
    "stream": False  # 使用文件模式方便测试
}

headers = {
    "Content-Type": "application/json"
}

print("=" * 60)
print("测试 TTS API - 请求体接收")
print("=" * 60)
print(f"\nURL: {url}")
print(f"\nHeaders: {json.dumps(headers, indent=2)}")
print(f"\nPayload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
print("\n发送请求...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"\n状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 成功！")
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print(f"\n❌ 失败")
        print(f"响应: {response.text}")
        
        # 尝试解析为 JSON
        try:
            error_data = response.json()
            print(f"\n详细错误: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
        except:
            pass
            
except Exception as e:
    print(f"\n❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
