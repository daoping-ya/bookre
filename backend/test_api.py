import requests
import json

# 测试语音合成 API
url = "http://localhost:8000/api/voice/synthesize"
payload = {
    "text": "这是一个测试",
    "voice_model": "zh-CN-XiaoxiaoNeural",
    "rate": "+0%",
    "volume": "+0%",
    "stream": True
}

headers = {
    "Content-Type": "application/json"
}

print("发送请求到:", url)
print("请求体:", json.dumps(payload, ensure_ascii=False, indent=2))

try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 保存音频
        with open("test_output.mp3", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("成功！音频已保存到 test_output.mp3")
    else:
        print(f"错误: {response.text}")
        
except Exception as e:
    print(f"请求失败: {e}")
