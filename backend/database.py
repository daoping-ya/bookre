from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

# 数据库模型
class Book(Base):
    """书籍表"""
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    file_path = Column(String(512), unique=True, nullable=False)
    file_hash = Column(String(64))
    cover_path = Column(String(512))
    total_pages = Column(Integer, default=0)
    format = Column(String(10))  # epub, txt
    created_at = Column(DateTime, default=datetime.now)
    last_read_at = Column(DateTime)
    
    # 关系
    progress = relationship("ReadingProgress", back_populates="book", uselist=False, cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="book", cascade="all, delete-orphan")

class ReadingProgress(Base):
    """阅读进度表"""
    __tablename__ = 'reading_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, unique=True)
    current_page = Column(Integer, default=0)
    current_chapter = Column(Integer, default=0)
    scroll_position = Column(Float, default=0.0)
    total_reading_time = Column(Integer, default=0)  # 秒
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    book = relationship("Book", back_populates="progress")

class Bookmark(Base):
    """书签表"""
    __tablename__ = 'bookmarks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    page_number = Column(Integer, nullable=False)
    chapter_title = Column(String(255))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    book = relationship("Book", back_populates="bookmarks")

class Setting(Base):
    """设置表"""
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数据库初始化
def init_db():
    """初始化数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'bookre.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    
    return engine

def get_session():
    """获取数据库会话"""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()
