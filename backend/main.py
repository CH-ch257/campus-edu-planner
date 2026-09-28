"""
校园资料AI检索系统 - 主接口
"""
import os
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import (
    init_db, get_db, save_document, list_documents,
    search_documents, get_document_by_id,
    extract_text_from_pdf, extract_text_from_word,
    UPLOAD_DIR
)

app = FastAPI(title="校园资料AI检索助手")

# 启动时建表
@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def read_root():
    return {"msg": "校园资料AI检索助手启动成功"}

# ========== 文档上传接口 ==========

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传PDF或Word文档，自动提取文字存入数据库"""
    # 判断文件类型
    ext = file.filename.lower().split(".")[-1]
    if ext == "pdf":
        filetype = "pdf"
    elif ext in ["doc", "docx"]:
        filetype = "word"
    else:
        return {"error": "只支持PDF和Word文档"}

    # 保存文件到本地
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 提取文本
    if filetype == "pdf":
        content = extract_text_from_pdf(file_path)
    else:
        content = extract_text_from_word(file_path)

    # 存入数据库
    doc = save_document(db, file.filename, filetype, file_path, content)

    return {
        "msg": "上传成功",
        "doc_id": doc.id,
        "filename": doc.filename,
        "content_length": len(content),
        "preview": content[:200] + "..." if len(content) > 200 else content
    }

# ========== 文档列表接口 ==========

@app.get("/documents/")
def get_documents(db: Session = Depends(get_db)):
    """获取全部文档列表"""
    docs = list_documents(db)
    return [{"id": d.id, "filename": d.filename, "type": d.filetype,
              "uploaded_at": d.uploaded_at.isoformat(),
              "content_length": len(d.content) if d.content else 0} for d in docs]

@app.get("/documents/search/")
def search_docs(keyword: str, db: Session = Depends(get_db)):
    """按文件名关键词搜索"""
    docs = search_documents(db, keyword)
    return [{"id": d.id, "filename": d.filename, "type": d.filetype} for d in docs]

@app.get("/documents/{doc_id}")
def get_doc_detail(doc_id: int, db: Session = Depends(get_db)):
    """查看单篇文档的详细内容"""
    doc = get_document_by_id(db, doc_id)
    if not doc:
        return {"error": "文档不存在"}
    return {
        "id": doc.id,
        "filename": doc.filename,
        "type": doc.filetype,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "content": doc.content
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
