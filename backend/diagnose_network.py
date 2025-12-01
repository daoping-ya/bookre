import asyncio
import aiohttp
import time
import socket

async def check_connection():
    url = "https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1"
    print(f"正在测试连接: {url}")
    
    # 1. DNS Resolution
    try:
        host = "speech.platform.bing.com"
        ip = socket.gethostbyname(host)
        print(f"✅ DNS 解析成功: {host} -> {ip}")
    except Exception as e:
        print(f"❌ DNS 解析失败: {e}")
        return

    # 2. HTTP Connection
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                duration = time.time() - start_time
                print(f"✅ 连接成功! 状态码: {response.status}")
                print(f"⏱️ 耗时: {duration:.2f}秒")
                
                if response.status == 401:
                    print("ℹ️ 注意: 401 是正常的，说明服务器可达但需要认证（edge-tts 库会自动处理认证）")
                    
    except asyncio.TimeoutError:
        print("❌ 连接超时 (Timeout)")
        print("建议: 检查防火墙或代理设置")
    except aiohttp.ClientConnectorError as e:
        print(f"❌ 连接错误: {e}")
        print("建议: 检查网络连接")
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Windows SelectorPolicy fix
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(check_connection())
