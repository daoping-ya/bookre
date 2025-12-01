import os
import base64
import hashlib
from typing import Dict, List, Optional
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
# from services.cover_search import search_cover_online  # 暂时禁用

class EpubParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        try:
            self.book = epub.read_epub(file_path)
        except Exception as e:
            print(f"EPUB读取失败: {str(e)}")
            raise

    def parse(self) -> Dict:
        """解析EPUB文件"""
        metadata = {
            'title': 'Unknown',
            'author': 'Unknown',
            'publisher': '',
            'cover': None,
            'chapters': [],
            'total_chapters': 0
        }
        
        try:
            # 提取基础元数据
            title = self.book.get_metadata('DC', 'title')
            if title:
                metadata['title'] = title[0][0]
                
            creator = self.book.get_metadata('DC', 'creator')
            if creator:
                metadata['author'] = creator[0][0]
                
            publisher = self.book.get_metadata('DC', 'publisher')
            if publisher:
                metadata['publisher'] = publisher[0][0]
            
            # 提取封面
            metadata['cover'] = self._extract_cover(metadata['title'], metadata['author'])
            
            # 提取章节
            metadata['chapters'] = self._extract_chapters()
            metadata['total_chapters'] = len(metadata['chapters'])
            
        except Exception as e:
            print(f"元数据提取警告: {str(e)}")
        
        return metadata
    
    def _extract_cover(self, title: str, author: str) -> Optional[str]:
        """提取封面图片（Base64编码）"""
        # 尝试从 EPUB 提取
        try:
            for item in self.book.get_items():
                if item.get_type() == epub.ITEM_COVER:
                    cover_data = item.get_content()
                    cover_base64 = base64.b64encode(cover_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{cover_base64}"
            
            for item in self.book.get_items():
                if item.get_type() == epub.ITEM_IMAGE and 'cover' in item.get_name().lower():
                    cover_data = item.get_content()
                    cover_base64 = base64.b64encode(cover_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{cover_base64}"
        except:
            pass
            
        # 在线搜索暂时禁用
        return None
    
    def _extract_chapters(self) -> List[Dict]:
        """提取章节内容"""
        chapters = []
        
        # 获取书籍的 spine (阅读顺序)
        for item_id in self.book.spine:
            try:
                item = self.book.get_item_with_id(item_id[0])
                if not item:
                    continue
                    
                # 解析HTML内容
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # 提取文本
                text = soup.get_text(separator='\n', strip=True)
                
                # 跳过空章节
                if not text or len(text.strip()) < 10:
                    continue
                
                # 尝试提取章节标题
                chapter_title = self._extract_chapter_title(soup)
                
                chapters.append({
                    'title': chapter_title,
                    'content': text,
                    'html': str(soup),  # 保留原始HTML用于富文本显示
                    'word_count': len(text)
                })
            
            except Exception as e:
                print(f"章节解析警告: {str(e)}")
                continue
        
        return chapters
    
    def _extract_chapter_title(self, soup: BeautifulSoup) -> str:
        """提取章节标题"""
        # 尝试从h1-h3标签中提取
        for tag in ['h1', 'h2', 'h3']:
            title_tag = soup.find(tag)
            if title_tag:
                return title_tag.get_text(strip=True)
        
        # 如果没找到，使用第一行作为标题
        first_line = soup.get_text(strip=True).split('\n')[0]
        if first_line and len(first_line) < 50:
            return first_line
        
        return '章节'
    
    def _calculate_hash(self) -> str:
        """计算文件哈希值"""
        with open(self.file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def get_toc(self) -> List[Dict]:
        """获取目录结构"""
        toc_items = []
        
        def parse_toc_item(item, level=0):
            if isinstance(item, tuple):
                section, children = item
                toc_items.append({
                    'title': section.title,
                    'href': section.href,
                    'level': level
                })
                for child in children:
                    parse_toc_item(child, level + 1)
            else:
                toc_items.append({
                    'title': item.title,
                    'href': item.href,
                    'level': level
                })
        
        try:
            for item in self.book.toc:
                parse_toc_item(item)
        except:
            pass
        
        return toc_items
