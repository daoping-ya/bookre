"""
EPUB 懒解析器 - 实现快速元数据提取和按需章节解析
支持「番茄小说」式秒开体验
"""
import base64
from pathlib import Path
from typing import Dict, List, Optional
from ebooklib import epub
from bs4 import BeautifulSoup


class EpubLazyParser:
    """懒加载 EPUB 解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._book = None
    
    @property
    def book(self):
        """延迟加载 EPUB 文件"""
        if self._book is None:
            self._book = epub.read_epub(self.file_path)
        return self._book
    
    def parse_metadata_only(self) -> Dict:
        """
        仅解析元数据和目录结构，不解析章节内容
        用于快速响应上传请求
        """
        metadata = {
            'title': 'Unknown',
            'author': 'Unknown',
            'cover': None,
            'chapters': [],
            'total_chapters': 0,
            'parsing_status': 'pending'
        }
        
        try:
            # 提取元数据
            title = self.book.get_metadata('DC', 'title')
            if title:
                metadata['title'] = title[0][0]
            
            creator = self.book.get_metadata('DC', 'creator')
            if creator:
                metadata['author'] = creator[0][0]
            
            # 提取封面
            metadata['cover'] = self._extract_cover()
            
            # 提取目录结构 (仅标题，不含内容)
            chapters = []
            for i, item_tuple in enumerate(self.book.spine):
                item_id = item_tuple[0]
                item = self.book.get_item_with_id(item_id)
                
                if item:
                    # 尝试快速提取标题
                    title = self._quick_extract_title(item, i)
                    chapters.append({
                        'index': i,
                        'title': title,
                        'content': None,  # 内容为空，稍后填充
                        'item_id': item_id,
                        'word_count': 0
                    })
            
            metadata['chapters'] = chapters
            metadata['total_chapters'] = len(chapters)
            
        except Exception as e:
            print(f"元数据解析警告: {e}")
        
        return metadata
    
    def _quick_extract_title(self, item, index: int) -> str:
        """快速提取章节标题，不解析全部内容"""
        try:
            content = item.get_content()
            # 只读取前 2000 字符来提取标题
            soup = BeautifulSoup(content[:2000], 'html.parser')
            
            for tag in ['h1', 'h2', 'h3', 'title']:
                title_tag = soup.find(tag)
                if title_tag:
                    text = title_tag.get_text(strip=True)
                    if text and len(text) < 50:
                        return text
            
            # 使用第一行非空文本
            text = soup.get_text(strip=True)
            first_line = text.split('\n')[0][:40] if text else ''
            return first_line or f'第 {index + 1} 章'
            
        except:
            return f'第 {index + 1} 章'
    
    def parse_single_chapter(self, index: int) -> Optional[Dict]:
        """
        按需解析单个章节
        用于用户打开该章节时实时解析
        """
        try:
            if index >= len(self.book.spine):
                return None
            
            item_id = self.book.spine[index][0]
            item = self.book.get_item_with_id(item_id)
            
            if not item:
                return None
            
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            
            # 跳过空章节
            if not text or len(text.strip()) < 10:
                return {
                    'index': index,
                    'title': f'第 {index + 1} 章',
                    'content': '',
                    'word_count': 0
                }
            
            title = self._extract_chapter_title(soup, index)
            
            return {
                'index': index,
                'title': title,
                'content': text,
                'word_count': len(text)
            }
            
        except Exception as e:
            print(f"章节 {index} 解析失败: {e}")
            return None
    
    def _extract_chapter_title(self, soup: BeautifulSoup, index: int) -> str:
        """提取章节标题"""
        for tag in ['h1', 'h2', 'h3']:
            title_tag = soup.find(tag)
            if title_tag:
                return title_tag.get_text(strip=True)
        
        first_line = soup.get_text(strip=True).split('\n')[0]
        if first_line and len(first_line) < 50:
            return first_line
        
        return f'第 {index + 1} 章'
    
    def _extract_cover(self) -> Optional[str]:
        """提取封面图片 (Base64)"""
        try:
            # 尝试获取封面
            for item in self.book.get_items():
                if item.get_type() == epub.ITEM_COVER:
                    cover_data = item.get_content()
                    cover_base64 = base64.b64encode(cover_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{cover_base64}"
            
            # 尝试查找名称包含 cover 的图片
            for item in self.book.get_items():
                if item.get_type() == epub.ITEM_IMAGE and 'cover' in item.get_name().lower():
                    cover_data = item.get_content()
                    cover_base64 = base64.b64encode(cover_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{cover_base64}"
        except:
            pass
        
        return None
    
    def parse_all_chapters(self) -> List[Dict]:
        """
        解析所有章节 (用于后台任务)
        返回完整章节列表
        """
        chapters = []
        for i in range(len(self.book.spine)):
            chapter = self.parse_single_chapter(i)
            if chapter:
                chapters.append(chapter)
        return chapters
