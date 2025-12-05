import aiohttp
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def search_cover_online(title: str, author: str = "") -> Optional[str]:
    """
    在线搜索书籍封面
    策略：优先 Google Books，失败后尝试 OpenLibrary
    """
    if not title:
        return None
        
    # 清理标题 (去除扩展名等)
    clean_title = title.replace(".epub", "").replace(".txt", "").split("(")[0].strip()
    clean_author = author.replace("Unknown", "").strip() if author else ""
    
    logger.info(f"正在搜索封面: {clean_title} {clean_author}")
    
    async with aiohttp.ClientSession() as session:
        # 1. 尝试 Google Books API
        try:
            query = f"intitle:{clean_title}"
            if clean_author:
                query += f"+inauthor:{clean_author}"
                
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "items" in data and len(data["items"]) > 0:
                        volume_info = data["items"][0].get("volumeInfo", {})
                        image_links = volume_info.get("imageLinks", {})
                        # 优先取大图
                        cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
                        if cover_url:
                            # Google Books 返回的 URL 经常是 http，强制转 https
                            return cover_url.replace("http://", "https://")
        except Exception as e:
            logger.warning(f"Google Books 搜索失败: {e}")

        # 2. 尝试 OpenLibrary API
        try:
            query = f"title={clean_title}"
            if clean_author:
                query += f"&author={clean_author}"
                
            url = f"https://openlibrary.org/search.json?{query}&limit=1"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "docs" in data and len(data["docs"]) > 0:
                        doc = data["docs"][0]
                        cover_i = doc.get("cover_i")
                        if cover_i:
                            return f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
        except Exception as e:
            logger.warning(f"OpenLibrary 搜索失败: {e}")
            
    return None

async def download_image(url: str) -> Optional[bytes]:
    """下载图片数据"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as e:
        logger.error(f"图片下载失败 {url}: {e}")
    return None
