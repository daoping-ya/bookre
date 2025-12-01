"""
测试 EasyVoice 支持的语音列表
"""
import asyncio
import aiohttp

# 我们当前使用的语音列表
voices_to_test = [
    'zh-CN-XiaoxiaoNeural',
    'zh-CN-XiaoyiNeural',
    'zh-CN-XiaohanNeural',
    'zh-CN-XiaomoNeural',
    'zh-CN-XiaoruiNeural',
    'zh-CN-XiaoshuangNeural',
    'zh-CN-YunxiaNeural',
    'zh-CN-YunxiNeural',
    'zh-CN-YunyangNeural',
    'zh-CN-YunjianNeural',
    'zh-CN-YunfengNeural',
    'zh-CN-YunhaoNeural',
    'zh-CN-YunzeNeural',
]

async def test_voice(session, voice):
    """测试单个语音"""
    url =  "http://localhost:3000/api/v1/tts/generateJson"
    payload = {
        "data": [{
            "text": "测试",
            "voice": voice,
            "rate": "+0%",
            "volume": "+0%"
        }]
    }
    
    try:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.read()
                if len(data) > 0:
                    return f"✅ {voice} - 成功 ({len(data)} bytes)"
                else:
                    return f"❌ {voice} - 返回空数据"
            else:
                text = await response.text()
                return f"❌ {voice} - 错误 {response.status}: {text[:100]}"
    except Exception as e:
        return f"❌ {voice} - 异常: {str(e)[:100]}"

async def main():
    print("开始测试 EasyVoice 语音支持情况...\n")
    
    async with aiohttp.ClientSession() as session:
        tasks = [test_voice(session, voice) for voice in voices_to_test]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
