import requests
import logging

logger = logging.getLogger(__name__)

def search_cover_online(title: str, author: str = "") -> str:
    """
    从 Google Books API 搜索书籍封面
    """
    try:
        query = f"intitle:{title}"
        if author:
            query += f"+inauthor:{author}"
            
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                volume_info = data["items"][0].get("volumeInfo", {})
                image_links = volume_info.get("imageLinks", {})
                
                # 优先使用大图
                cover_url = image_links.get("extraLarge") or \
                           image_links.get("large") or \
                           image_links.get("medium") or \
                           image_links.get("small") or \
                           image_links.get("thumbnail")
                           
                if cover_url:
                    # Google Books API 返回的 URL 可能是 http，强制转为 https
                    return cover_url.replace("http://", "https://")
                    
    except Exception as e:
        logger.error(f"在线封面搜索失败: {str(e)}")
        
    return None
