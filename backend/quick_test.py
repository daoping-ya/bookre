import asyncio
import edge_tts

async def quick_test():
    try:
        communicate = edge_tts.Communicate("测试", "zh-CN-XiaoxiaoNeural")
        await communicate.save("quick_test.mp3")
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

asyncio.run(quick_test())
