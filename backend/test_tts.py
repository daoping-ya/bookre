import asyncio
import edge_tts
from pathlib import Path

async def test_tts():
    text = "你好，这是一个测试语音。"
    voice = "zh-CN-XiaoxiaoNeural"
    output_file = "test_audio.mp3"
    
    print(f"正在合成: {text}")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    if Path(output_file).exists():
        print(f"✅ 合成成功: {output_file}")
        # 清理
        Path(output_file).unlink()
    else:
        print("❌ 合成失败")

if __name__ == "__main__":
    asyncio.run(test_tts())
