from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path
import logging

from services.epub_parser import EpubParser
from services.txt_parser import TxtParser
from services.tts_engine import get_tts_engine
from database import init_db

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BookRe API",
    description="电子书阅读器后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载音频静态文件目录
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 启动BookRe后端服务...")
    init_db()
    logger.info("✅ 数据库初始化完成")

@app.get("/")
async def root():
    return {
        "message": "BookRe API服务运行中",
        "version": "1.0.0",
        "endpoints": ["/api/books", "/api/parse", "/api/voice"]
    }

@app.post("/api/parse/epub")
async def parse_epub(file: UploadFile = File(...)):
    """解析EPUB文件"""
    try:
        temp_path = Path(f"temp/{file.filename}")
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        parser = EpubParser(str(temp_path))
        result = parser.parse()
        
        temp_path.unlink()
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"EPUB解析错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

@app.post("/api/parse/txt")
async def parse_txt(file: UploadFile = File(...)):
    """解析TXT文件"""
    try:
        content = await file.read()
        
        parser = TxtParser()
        result = parser.parse(content)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"TXT解析错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

# TTS 请求模型
class TTSRequest(BaseModel):
    text: str
    voice_model: Optional[str] = "zh-CN-XiaoxiaoNeural"
    rate: Optional[str] = "+0%"
    volume: Optional[str] = "+0%"
    stream: Optional[bool] = True
    
    class Config:
        # 允许任意类型
        arbitrary_types_allowed = True

# 书籍存储相关端点
BOOKS_DATA_DIR = Path("data/books")
BOOKS_DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/api/books")
async def list_books():
    """列出所有书籍 (仅元数据)"""
    try:
        import json
        books = []
        for file_path in BOOKS_DATA_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 移除章节内容以减少传输量
                    if "chapters" in data:
                        del data["chapters"]
                    books.append(data)
            except Exception as e:
                logger.warning(f"读取书籍文件失败 {file_path}: {e}")
        
        # 按时间倒序排序
        books.sort(key=lambda x: x.get("lastReadAt", x.get("createdAt", "")), reverse=True)
        return books
    except Exception as e:
        logger.error(f"获取书籍列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/books/save")
async def save_book(request: Request):
    """保存书籍数据到后端文件"""
    try:
        import json
        data = await request.json()
        book_id = data.get("id")
        if not book_id:
            raise HTTPException(status_code=400, detail="Missing book ID")
        
        file_path = BOOKS_DATA_DIR / f"{book_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"书籍已保存: {book_id}")
        return {"status": "success", "message": "Book saved"}
    except Exception as e:
        logger.error(f"保存书籍失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/{book_id}")
async def load_book(book_id: str):
    """加载书籍数据"""
    try:
        import json
        file_path = BOOKS_DATA_DIR / f"{book_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Book not found")
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"加载书籍失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/books/{book_id}")
async def delete_book(book_id: str):
    """删除书籍文件"""
    try:
        file_path = BOOKS_DATA_DIR / f"{book_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"书籍已删除: {book_id}")
            
        return {"status": "success", "message": "Book deleted"}
    except Exception as e:
        logger.error(f"删除书籍失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/books/{book_id}")
async def update_book_metadata(book_id: str, request: Request):
    """更新书籍元数据 (不覆盖章节)"""
    try:
        import json
        updates = await request.json()
        file_path = BOOKS_DATA_DIR / f"{book_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Book not found")
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 更新字段 (排除 chapters 以防万一)
        if "chapters" in updates:
            del updates["chapters"]
            
        data.update(updates)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return {"status": "success", "message": "Metadata updated"}
    except Exception as e:
        logger.error(f"更新书籍失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# TTS相关端点
@app.get("/api/voice/list")
async def list_voices():
    """获取可用的语音列表"""
    try:
        engine = get_tts_engine()
        return engine.get_available_voices()
    except Exception as e:
        logger.error(f"获取语音列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/synthesize")
async def synthesize_voice(request: Request):
    """
    语音合成接口 - 使用原始 Request 对象绕过 Pydantic
    """
    try:
        # 手动解析 JSON 请求体
        body = await request.body()
        logger.info(f"===== 收到原始请求体 =====")
        logger.info(f"Body length: {len(body)} bytes")
        logger.info(f"Body (first 500 chars): {body[:500]}")
        
        # 解析 JSON
        import json
        data = json.loads(body)
        logger.info(f"解析后的 JSON: {data}")
        
        # 提取参数
        text = data.get("text", "")
        voice_model = data.get("voice_model", "zh-CN-XiaoxiaoNeural")
        rate = data.get("rate", "+0%")
        volume = data.get("volume", "+0%")
        stream = data.get("stream", True)
        
        logger.info(f"===== 提取的参数 =====")
        logger.info(f"text 长度: {len(text)}")
        logger.info(f"text 预览: {text[:100]}")
        logger.info(f"voice_model: {voice_model}")
        logger.info(f"rate: {rate}")
        logger.info(f"stream: {stream}")
        
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        logger.info(f"开始 TTS 合成...")
        
        engine = get_tts_engine()
        
        if stream:
            logger.info("使用流式合成")
            return StreamingResponse(
                engine.stream_synthesize(text, voice_model, rate, volume),
                media_type="audio/mpeg"
            )
        else:
            logger.info("使用文件合成")
            output_path = await engine.synthesize(text, voice_model, rate, volume)
            return {"audio_url": f"/audio/{output_path.name}"}
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"无效的 JSON: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音合成失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "bookre-api"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
