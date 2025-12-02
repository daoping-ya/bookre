"""
数据迁移脚本：将旧格式迁移到支持多设备的新格式
"""
import json
from pathlib import Path
import shutil
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path('data/books')
BACKUP_DIR = Path('data/books_backup')

def migrate_books():
    """迁移所有书籍数据"""
    if not DATA_DIR.exists():
        logger.error(f"❌ 数据目录不存在: {DATA_DIR}")
        return

    # 创建备份
    logger.info('📦 创建备份...')
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(DATA_DIR, BACKUP_DIR)
    logger.info(f'✅ 备份完成: {BACKUP_DIR}')
    
    # 迁移数据
    migrated_count = 0
    for file_path in DATA_DIR.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否已迁移
            if 'devices' in data:
                logger.info(f'⏭️  跳过已迁移: {data.get("title", file_path.name)}')
                continue
            
            # 提取旧的进度数据
            old_progress = {
                'progress': data.pop('progress', 0),
                'currentPage': data.pop('currentPage', 0),
                'currentChapter': data.pop('currentChapter', 0),
                'lastReadAt': data.pop('lastReadAt', data.get('createdAt'))
            }
            
            # 创建默认设备（用于已有数据）
            # 使用一个固定的ID或者标记，这里使用 'default_device'
            data['devices'] = {
                'default_device': {
                    'name': '默认设备',
                    **old_progress
                }
            }
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f'✅ 迁移成功: {data.get("title", file_path.name)}')
            migrated_count += 1
            
        except Exception as e:
            logger.error(f'❌ 迁移失败 {file_path}: {e}')
    
    logger.info(f'\n🎉 迁移完成！共迁移 {migrated_count} 本书')
    logger.info(f'💾 备份位置: {BACKUP_DIR}')

if __name__ == '__main__':
    migrate_books()
