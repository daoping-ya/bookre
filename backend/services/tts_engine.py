import edge_tts
import asyncio
from pathlib import Path
import hashlib
import logging
import os
import time

# 配置代理 - Edge-TTS 通过 V2Tun/V2Ray 访问 Microsoft 服务
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10808'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self):
        # 移植自 EasyVoice 的完整中文语音列表
        self.voices = {
            # 普通话 - 女声
            'zh-CN-XiaoxiaoNeural': {'name': '晓晓 (温柔)', 'gender': 'female'},
            'zh-CN-XiaoyiNeural': {'name': '晓伊 (活泼)', 'gender': 'female'},
            'zh-CN-YunxiaNeural': {'name': '云夏 (亲切)', 'gender': 'female'},
            
            # 普通话 - 男声
            'zh-CN-YunxiNeural': {'name': '云希 (沉稳)', 'gender': 'male'},
            'zh-CN-YunyangNeural': {'name': '云扬 (专业)', 'gender': 'male'},
            
            # 方言
            'zh-CN-liaoning-XiaobeiNeural': {'name': '晓北 (东北话)', 'gender': 'female'},
            'zh-CN-shaanxi-XiaoniNeural': {'name': '晓妮 (陕西话)', 'gender': 'female'},
            'zh-CN-sichuan-YunxiNeural': {'name': '云希 (四川话)', 'gender': 'male'},
            
            # 粤语
            'zh-HK-HiuGaaiNeural': {'name': '晓佳 (粤语女声)', 'gender': 'female'},
            'zh-HK-HiuMaanNeural': {'name': '晓曼 (粤语女声)', 'gender': 'female'},
            'zh-HK-WanLungNeural': {'name': '云龙 (粤语男声)', 'gender': 'male'},
            
            # 台湾
            'zh-TW-HsiaoChenNeural': {'name': '晓臻 (台湾女声)', 'gender': 'female'},
            'zh-TW-HsiaoYuNeural': {'name': '晓雨 (台湾女声)', 'gender': 'female'},
            'zh-TW-YunJheNeural': {'name': '云哲 (台湾男声)', 'gender': 'male'},
        }
        
        self.default_voice = 'zh-CN-XiaoxiaoNeural'
        
        
        # 音频输出目录 - 与 app.py 中的静态文件目录匹配
        self.audio_dir = Path('data/audio')
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 启动时清理旧文件
        self.cleanup_old_audio_files()
        
        logger.info(f"TTS引擎初始化完成，支持 {len(self.voices)} 种语音")
        
        # 熔断器状态
        self.ev_failure_count = 0
        self.ev_circuit_open = False
        self.ev_circuit_open_time = 0
        self.EV_MAX_FAILURES = 2
        self.EV_COOLDOWN_SECONDS = 60

    def cleanup_old_audio_files(self, max_age_hours=24):
        """清理超过指定时间的音频文件"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            total_size = 0
            
            for audio_file in self.audio_dir.glob('*.mp3'):
                try:
                    file_age = current_time - audio_file.stat().st_mtime
                    file_size = audio_file.stat().st_size
                    
                    if file_age > max_age_seconds:
                        total_size += file_size
                        audio_file.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"删除文件失败 {audio_file}: {e}")
            
            if deleted_count > 0:
                logger.info(f"🧹 清理了 {deleted_count} 个旧音频文件，释放 {total_size/1024/1024:.2f} MB")
        except Exception as e:
            logger.error(f"清理音频文件失败: {e}")

    def get_available_voices(self):
        """获取可用的语音列表"""
        voice_list = []
        for voice_id, info in self.voices.items():
            voice_list.append({
                'id': voice_id,
                'name': info['name'],
                'gender': info['gender']
            })
        return {'voices': voice_list}

    async def synthesize(self, text: str, voice_model: str = "default", rate: str = "+0%", volume: str = "+0%"):
        """
        合成语音（优先使用 EasyVoice，失败则降级）
        """
        # 尝试使用 EasyVoice
        try:
            return await self._synthesize_easyvoice(text, voice_model, rate, volume)
        except Exception as e:
            logger.warning(f"EasyVoice 调用失败，尝试降级到 Edge-TTS: {e}")
            
        # 降级到 Edge-TTS
        voice = voice_model if voice_model in self.voices else self.default_voice
        
        # 生成文件名
        text_hash = hashlib.md5(f"{text}_{voice}_{rate}_{volume}".encode()).hexdigest()[:12]
        output_filename = f"tts_{text_hash}.mp3"
        output_path = self.audio_dir / output_filename
        
        # 如果文件已存在，直接返回
        if output_path.exists():
            logger.info(f"使用缓存的音频: {output_path.name}")
            return output_path
        
        try:
            logger.info(f"正在合成语音(Edge-TTS): {text[:30]}... (语音: {voice})")
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume
            )
            
            await communicate.save(str(output_path))
            return output_path
            
        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}")
            raise

    async def _synthesize_easyvoice(self, text: str, voice_model: str, rate: str, volume: str) -> Path:
        """调用本地 EasyVoice 服务"""
        import aiohttp
        
        # EasyVoice API 地址
        api_url = "http://localhost:3000/api/v1/tts/generateJson"
        
        voice = voice_model if voice_model in self.voices else self.default_voice
        
        # 构建请求体
        payload = {
            "data": [
                {
                    "text": text,
                    "voice": voice,
                    "rate": rate,
                    "volume": volume
                }
            ]
        }
        
        # 生成文件名
        text_hash = hashlib.md5(f"ev_{text}_{voice}_{rate}_{volume}".encode()).hexdigest()[:12]
        output_filename = f"tts_ev_{text_hash}.mp3"
        output_path = self.audio_dir / output_filename
        
        if output_path.exists():
            logger.info(f"使用缓存的音频(EasyVoice): {output_path.name}")
            return output_path

        logger.info(f"调用 EasyVoice API: {text[:30]}...")
        
        # 设置超时
        timeout = aiohttp.ClientTimeout(total=60)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(api_url, json=payload) as response:
                    if response.status != 200:
                        text_resp = await response.text()
                        raise Exception(f"EasyVoice API Error: {response.status} - {text_resp}")
                    
                    audio_data = await response.read()
                    
                    if not audio_data or len(audio_data) == 0:
                        raise Exception("EasyVoice 返回空数据")
                    
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                        
                    logger.info(f"EasyVoice 合成成功: {output_path.name}, 大小: {len(audio_data)} bytes")
                    return output_path
        except aiohttp.ClientConnectorError:
            logger.warning("EasyVoice 服务未连接 (可能正在重启)，降级到 Edge-TTS")
            raise
        except Exception as e:
            logger.error(f"EasyVoice 调用异常: {e}")
            raise

    async def stream_synthesize(self, text: str, voice_model: str = "default", rate: str = "+0%", volume: str = "+0%"):
        """
        流式合成语音 - 优先使用 EasyVoice
        """
        try:
            # --- 熔断器检查 ---
            if self.ev_circuit_open:
                elapsed = time.time() - self.ev_circuit_open_time
                if elapsed < self.EV_COOLDOWN_SECONDS:
                    logger.warning(f"⚡ 熔断器开启中 (剩余 {int(self.EV_COOLDOWN_SECONDS - elapsed)}s)，直接使用 Edge-TTS")
                    raise Exception("Circuit Breaker Open")
                else:
                    logger.info("🔄 熔断器冷却结束，尝试恢复 EasyVoice")
                    self.ev_circuit_open = False
                    self.ev_failure_count = 0

            # --- 严格的语音验证 (成熟的机制) ---
            # 确保传给 EasyVoice 的语音一定在白名单中，防止崩溃
            safe_voice = voice_model
            if voice_model not in self.voices:
                logger.warning(f"⚠️ 语音 '{voice_model}' 不在白名单中，自动降级到默认语音 '{self.default_voice}'")
                safe_voice = self.default_voice
            
            logger.info(f"🎯 尝试使用 EasyVoice (语音: {safe_voice})...")
            
            # 设置更短的超时，快速失败
            output_path = await self._synthesize_easyvoice(text, safe_voice, rate, volume)
            
            if not output_path.exists():
                raise Exception("EasyVoice 文件不存在")
            
            file_size = output_path.stat().st_size
            if file_size == 0:
                raise Exception("EasyVoice 文件为空")
            
            logger.info(f"✅ EasyVoice 成功: {file_size} bytes")
            
            # 成功，重置失败计数
            self.ev_failure_count = 0
            
            with open(output_path, "rb") as f:
                complete_audio = f.read()
                if not complete_audio:
                    raise Exception("读取音频失败")
                yield complete_audio
            return
            
        except Exception as e:
            # 记录失败
            if str(e) != "Circuit Breaker Open":
                self.ev_failure_count += 1
                logger.warning(f"⚠️ EasyVoice 失败 ({self.ev_failure_count}/{self.EV_MAX_FAILURES}): {e}")
                
                if self.ev_failure_count >= self.EV_MAX_FAILURES:
                    self.ev_circuit_open = True
                    self.ev_circuit_open_time = time.time()
                    logger.error(f"🔥 EasyVoice 连续失败，熔断器开启！将在 {self.EV_COOLDOWN_SECONDS} 秒内降级到 Edge-TTS")
            else:
                pass # 熔断中，不记录日志


        # 降级到 Edge-TTS
        voice = voice_model if voice_model in self.voices else self.default_voice
        
        logger.info(f"🎤 使用语音模型: {voice}")
        logger.info(f"📝 合成文本长度: {len(text)}")
        
        try:
            audio_chunks = []
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume
            )
            
            logger.info("⏳ 开始生成音频...")
            chunk_count = 0
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
                    chunk_count += 1
            
            complete_audio = b''.join(audio_chunks)
            total_size = len(complete_audio)
            
            logger.info(f"✅ Edge-TTS 合成成功: {chunk_count} 块, 总大小: {total_size} bytes")
            
            yield complete_audio
                    
        except Exception as e:
            logger.error(f"❌ Edge-TTS 合成失败: {type(e).__name__}: {str(e)}")
            raise

# 全局 TTS 引擎实例
_tts_engine = None

def get_tts_engine():
    """获取 TTS 引擎单例"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
