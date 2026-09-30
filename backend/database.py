"""
文档管理模块：文档上传、文本提取、数据库存储
技术栈：SQLAlchemy + SQLite + PyPDF2 + python-docx
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ========== 数据库连接 ==========
DATABASE_URL = "sqlite:///./campus.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 上传文件保存目录
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== 文档表模型 ==========

class Document(Base):
    """文档表：存储上传的课件、作业等资料"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, comment="文件名")
    filetype = Column(String(20), nullable=False, comment="文件类型：pdf / word")
    file_path = Column(String(500), comment="文件保存路径")
    content = Column(Text, comment="提取的文本内容")
    uploaded_at = Column(DateTime, default=datetime.now, comment="上传时间")

    category = Column(String(50), default="未分类", comment="文档自动分类")
    category_confirmed = Column(Integer, default=0, comment="0=AI自动分类，1=管理员人工修正过")

class Chunk(Base):
    """文档分块表，用于RAG向量检索"""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, nullable=False, comment="关联documents表id")
    chunk_text = Column(Text, comment="分块文本")
    embedding = Column(Text, comment="向量json字符串")

# ========== 建表 ==========

def init_db():
    """初始化数据库，创建表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")

def get_db():
    """获取数据库会话（FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== 文本提取函数 ==========

def extract_text_from_pdf(file_path: str) -> str:
    """从PDF文件提取文本"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"[PDF提取失败: {e}]"

def extract_text_from_word(file_path: str) -> str:
    """从Word文件提取文本"""
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"[Word提取失败: {e}]"

# ========== 文档 CRUD ==========

def save_document(db, filename: str, filetype: str, file_path: str, content: str):
    """保存文档记录到数据库"""
    doc = Document(
        filename=filename,
        filetype=filetype,
        file_path=file_path,
        content=content
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(db):
    """查询全部文档列表"""
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()

def search_documents(db, keyword: str):
    """按文件名关键词搜索文档"""
    return db.query(Document).filter(
        Document.filename.contains(keyword)
    ).order_by(Document.uploaded_at.desc()).all()

def get_document_by_id(db, doc_id: int):
    """根据ID获取单篇文档"""
    return db.query(Document).filter(Document.id == doc_id).first()
