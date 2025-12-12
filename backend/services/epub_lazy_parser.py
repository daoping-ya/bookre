"""
EPUB 极速元数据解析器 - 真正的懒加载
使用 zipfile 直接读取 EPUB (EPUB本质是ZIP文件)
绝不加载正文内容到内存，24MB文件 < 1秒解析
"""
import zipfile
import xml.etree.ElementTree as ET
import base64
import os
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class EpubLazyParser:
    """真正的懒加载 EPUB 解析器 - 使用 zipfile 而非 ebooklib"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._content_opf_path = None
        self._rootdir = ''
    
    def parse_metadata_only(self) -> Dict:
        """
        极速解析：只提取元数据和目录结构
        绝对不读取正文内容，24MB文件 < 1秒
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
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                # 1. 找到 content.opf 的位置
                container_path = 'META-INF/container.xml'
                if container_path in zf.namelist():
                    container_xml = zf.read(container_path).decode('utf-8')
                    root = ET.fromstring(container_xml)
                    
                    # 查找 rootfile
                    ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                    rootfile = root.find('.//container:rootfile', ns)
                    if rootfile is not None:
                        self._content_opf_path = rootfile.get('full-path')
                        self._rootdir = os.path.dirname(self._content_opf_path)
                
                if not self._content_opf_path:
                    # 如果没找到，尝试常见路径
                    for possible in ['content.opf', 'OEBPS/content.opf', 'OPS/content.opf']:
                        if possible in zf.namelist():
                            self._content_opf_path = possible
                            self._rootdir = os.path.dirname(possible)
                            break
                
                if not self._content_opf_path:
                    print("❌ 找不到 content.opf")
                    return metadata
                
                # 2. 解析 content.opf
                opf_content = zf.read(self._content_opf_path).decode('utf-8')
                opf_root = ET.fromstring(opf_content)
                
                # 获取命名空间
                ns = {
                    'opf': 'http://www.idpf.org/2007/opf',
                    'dc': 'http://purl.org/dc/elements/1.1/'
                }
                
                # 提取标题
                title_elem = opf_root.find('.//dc:title', ns)
                if title_elem is not None and title_elem.text:
                    metadata['title'] = title_elem.text.strip()
                
                # 提取作者
                creator_elem = opf_root.find('.//dc:creator', ns)
                if creator_elem is not None and creator_elem.text:
                    metadata['author'] = creator_elem.text.strip()
                
                # 3. 提取封面 (只取小图)
                cover_id = None
                for meta in opf_root.findall('.//opf:meta[@name="cover"]', ns):
                    cover_id = meta.get('content')
                    break
                
                if cover_id:
                    manifest = opf_root.find('.//opf:manifest', ns)
                    if manifest is not None:
                        for item in manifest.findall('opf:item', ns):
                            if item.get('id') == cover_id:
                                cover_href = item.get('href')
                                cover_path = os.path.join(self._rootdir, cover_href).replace('\\', '/')
                                
                                # 检查封面大小，超过500KB就跳过
                                try:
                                    info = zf.getinfo(cover_path)
                                    if info.file_size < 500 * 1024:
                                        cover_data = zf.read(cover_path)
                                        cover_base64 = base64.b64encode(cover_data).decode('utf-8')
                                        metadata['cover'] = f"data:image/jpeg;base64,{cover_base64}"
                                except:
                                    pass
                                break
                
                # 4. 提取章节列表 (只取 id 和标题，绝不读取内容)
                spine = opf_root.find('.//opf:spine', ns)
                manifest = opf_root.find('.//opf:manifest', ns)
                
                if spine is not None and manifest is not None:
                    # 建立 id -> href 映射
                    id_to_href = {}
                    for item in manifest.findall('opf:item', ns):
                        item_id = item.get('id')
                        item_href = item.get('href')
                        id_to_href[item_id] = item_href
                    
                    # 遍历 spine
                    chapter_index = 0
                    for itemref in spine.findall('opf:itemref', ns):
                        item_id = itemref.get('idref')
                        href = id_to_href.get(item_id, '')
                        
                        if href:
                            metadata['chapters'].append({
                                'index': chapter_index,
                                'id': item_id,
                                'title': f'第 {chapter_index + 1} 章',  # 占位标题
                                'href': href,
                                'content': None,  # !! 关键：绝对为 None
                                'word_count': 0
                            })
                            chapter_index += 1
                
                metadata['total_chapters'] = len(metadata['chapters'])
                
        except Exception as e:
            print(f"❌ EPUB 元数据解析错误: {e}")
        
        return metadata
    
    def parse_single_chapter(self, index: int) -> Optional[Dict]:
        """
        按需解析单个章节 - 只读取这一章的内容
        用于用户翻页时实时加载
        """
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                # 先获取章节信息
                meta = self.parse_metadata_only()
                if index >= len(meta['chapters']):
                    return None
                
                chapter_info = meta['chapters'][index]
                href = chapter_info.get('href', '')
                
                if not href:
                    return None
                
                # 构建完整路径
                chapter_path = os.path.join(self._rootdir, href).replace('\\', '/')
                
                # 尝试多种可能的路径
                possible_paths = [
                    chapter_path,
                    href,
                    f"OEBPS/{href}",
                    f"OPS/{href}"
                ]
                
                content = None
                for path in possible_paths:
                    if path in zf.namelist():
                        raw_content = zf.read(path).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(raw_content, 'html.parser')
                        content = soup.get_text(separator='\n', strip=True)
                        
                        # 提取标题
                        title = chapter_info.get('title', f'第 {index + 1} 章')
                        for tag in ['h1', 'h2', 'h3']:
                            title_tag = soup.find(tag)
                            if title_tag:
                                title = title_tag.get_text(strip=True)
                                break
                        
                        return {
                            'index': index,
                            'id': chapter_info.get('id'),
                            'title': title,
                            'content': content,
                            'word_count': len(content) if content else 0
                        }
                
                return None
                
        except Exception as e:
            print(f"❌ 章节 {index} 解析失败: {e}")
            return None
