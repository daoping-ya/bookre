import asyncio
import edge_tts
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tts():
    text = "Hello World"
    voice = "zh-CN-XiaoxiaoNeural"
    output_file = "test_audio_fixed.mp3"
    
    logger.info(f"Synthesizing: {text}")
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        if Path(output_file).exists():
            logger.info(f"Success: {output_file}")
            # Cleanup
            Path(output_file).unlink()
        else:
            logger.error("Failed: File not created")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tts())
