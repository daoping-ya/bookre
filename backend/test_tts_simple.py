import asyncio
import edge_tts

async def test_tts():
    print("Testing edge-tts...")
    communicate = edge_tts.Communicate("Hello, this is a test.", "en-US-AriaNeural")
    try:
        await communicate.save("test_audio.mp3")
        print("Success! Audio saved to test_audio.mp3")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tts())
