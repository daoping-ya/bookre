import re
import chardet
from typing import List, Dict

class TxtParser:
    """TXT电子书解析器"""
    
    def __init__(self):
        self.content = ""
        self.encoding = "utf-8"
    
    def parse(self, file_content: bytes) -> Dict:
        """解析TXT文件"""
        try:
            # 自动检测编码
            self.encoding = self._detect_encoding(file_content)
            
            # 解码内容
            self.content = file_content.decode(self.encoding)
            
            # 分割章节
            chapters = self._split_chapters(self.content)
            
            # 提取元数据
            metadata = self._extract_metadata(self.content)
            
            return {
                'success': True,
                'metadata': metadata,
                'chapters': chapters,
                'total_chapters': len(chapters),
                'encoding': self.encoding,
                'total_words': len(self.content)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_encoding(self, content: bytes) -> str:
        """自动检测文件编码"""
        result = chardet.detect(content)
        encoding = result['encoding']
        
        # 常见编码映射
        encoding_map = {
            'GB2312': 'gbk',
            'ISO-8859-1': 'utf-8'
        }
        
        return encoding_map.get(encoding, encoding) if encoding else 'utf-8'
    
    def _extract_metadata(self, content: str) -> Dict:
        """从内容中提取元数据"""
        lines = content.split('\n')[:20]  # 检查前20行
        
        metadata = {
            'title': '未知书名',
            'author': '未知作者',
            'language': 'zh'
        }
        
        # 尝试从前几行提取书名和作者
        for line in lines:
            line = line.strip()
            
            # 匹配书名模式
            title_match = re.search(r'(?:书名|标题)[：:]\s*(.+)', line)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # 匹配作者模式
            author_match = re.search(r'(?:作者|著)[：:]\s*(.+)', line)
            if author_match:
                metadata['author'] = author_match.group(1).strip()
        
        # 如果仍未找到书名，使用第一个非空行
        if metadata['title'] == '未知书名':
            for line in lines:
                if line.strip() and len(line.strip()) < 50:
                    metadata['title'] = line.strip()
                    break
        
        return metadata
    
    def _split_chapters(self, content: str) -> List[Dict]:
        """智能章节分割"""
        # 章节标题模式（支持多种格式）
        chapter_patterns = [
            r'^第[一二三四五六七八九十百千\d]+章\s*.+',
            r'^Chapter\s+\d+',
            r'^\d+\.\s*.+',
            r'^[一二三四五六七八九十]+、.+',
        ]
        
        combined_pattern = '|'.join(f'({p})' for p in chapter_patterns)
        
        # 分行
        lines = content.split('\n')
        
        chapters = []
        current_chapter = {
            'title': '开始',
            'content': '',
            'word_count': 0
        }
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否是章节标题
            if re.match(combined_pattern, line_stripped):
                # 保存上一章节
                if current_chapter['content']:
                    current_chapter['word_count'] = len(current_chapter['content'])
                    chapters.append(current_chapter)
                
                # 开始新章节
                current_chapter = {
                    'title': line_stripped[:100],  # 限制标题长度
                    'content': '',
                    'word_count': 0
                }
            else:
                # 添加到当前章节内容
                current_chapter['content'] += line + '\n'
        
        # 添加最后一章
        if current_chapter['content']:
            current_chapter['word_count'] = len(current_chapter['content'])
            chapters.append(current_chapter)
        
        # 如果没有检测到章节，按固定字数分割
        if len(chapters) == 0 or (len(chapters) == 1 and chapters[0]['title'] == '开始'):
            chapters = self._split_by_length(content)
        
        return chapters
    
    def _split_by_length(self, content: str, chars_per_chapter: int = 5000) -> List[Dict]:
        """按固定字数分割章节"""
        chapters = []
        lines = content.split('\n')
        current_content = ''
        chapter_num = 1
        
        for line in lines:
            current_content += line + '\n'
            
            # 达到字数限制且在句子结尾
            if len(current_content) >= chars_per_chapter and line.strip().endswith(('。', '！', '？', '.', '!', '?')):
                chapters.append({
                    'title': f'第{chapter_num}部分',
                    'content': current_content.strip(),
                    'word_count': len(current_content)
                })
                current_content = ''
                chapter_num += 1
        
        # 添加剩余内容
        if current_content.strip():
            chapters.append({
                'title': f'第{chapter_num}部分',
                'content': current_content.strip(),
                'word_count': len(current_content)
            })
        
        return chapters
