"""
校园资料AI检索系统 - 主接口
"""
import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import (
    init_db, get_db, save_document, list_documents,
    search_documents, get_document_by_id,
    extract_text_from_pdf, extract_text_from_word,
    UPLOAD_DIR, Document
)
from rag import save_chunks_to_db, search_top3_chunks
from llm import chat_with_llm, classify_document


# ---------------------- 日志配置 ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 管理员密钥
ADMIN_SECRET = "admin123456"

app = FastAPI(
    title="校园资料AI检索助手",
    description="上传PDF/Word校园资料，自动提取文本，支持文档检索与AI问答",
    version="1.0.0"
)

# 启动时建表
@app.on_event("startup")
def startup():
    init_db()

@app.get("/", summary="首页根路径")
def read_root():
    return {"msg": "校园资料AI检索助手启动成功"}

# ========== 文档上传接口（管理员专用） ==========
@app.post("/upload/", summary="【管理员专用】上传文档")
async def upload_document(
    file: UploadFile = File(...),
    admin_secret: str = Query(..., description="管理员操作密钥"),
    db: Session = Depends(get_db)
):
    """上传PDF或Word文档，自动提取文字存入数据库，自动分类，自动版本升级"""
    if admin_secret != ADMIN_SECRET:
        logger.warning(f"非管理员尝试上传文档，密钥错误")
        raise HTTPException(status_code=403, detail="权限不足，只有管理员才能上传文档")

    ext = file.filename.lower().split(".")[-1]
    if ext == "pdf":
        filetype = "pdf"
    elif ext in ["doc", "docx"]:
        filetype = "word"
    else:
        return {"error": "只支持PDF和Word文档"}

    safe_name = str(uuid.uuid4()) + "." + ext
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    if filetype == "pdf":
        content = extract_text_from_pdf(file_path)
    else:
        content = extract_text_from_word(file_path)

    doc = save_document(db, file.filename, filetype, file_path, content)

    # 检查是否有同名旧版本文档，自动做版本升级
    old_latest = db.query(Document).filter(
        Document.filename == file.filename,
        Document.is_latest == 1
    ).first()
    if old_latest:
        old_latest.is_latest = 0
        doc.version = old_latest.version + 1
        doc.parent_doc_id = old_latest.id
        logger.info(f"检测到同名旧文档，升级版本号至v{doc.version}")
    db.commit()

    if doc.content and len(doc.content.strip()) > 0:
        save_chunks_to_db("./campus.db", doc.id, doc.content)
        try:
            auto_cat = classify_document(doc.content)
            doc.category = auto_cat
            db.commit()
            logger.info(f"文档《{doc.filename}》自动分类结果：{auto_cat}")
        except Exception as e:
            logger.warning(f"自动分类失败，默认归为未分类：{str(e)}")

    return {
        "msg": "上传成功",
        "doc_id": doc.id,
        "filename": doc.filename,
        "version": doc.version,
        "content_length": len(content),
        "preview": content[:200] + "..." if len(content) > 200 else content,
        "category": doc.category
    }

# ========== 文档列表接口（学生只看最新版） ==========
@app.get("/documents/", summary="获取全部最新文档列表")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.is_latest == 1).order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "filetype": d.filetype,
            "category": d.category,
            "version": d.version,
            "uploaded_at": d.uploaded_at.isoformat(),
            "content_length": len(d.content) if d.content else 0
        }
        for d in docs
    ]

@app.get("/documents/search/", summary="按文件名搜索文档")
def search_docs(keyword: str, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.filename.contains(keyword), Document.is_latest == 1).all()
    return [{"id": d.id, "filename": d.filename, "filetype": d.filetype, "category": d.category, "version": d.version} for d in docs]

@app.get("/documents/{doc_id}", summary="查看文档详情")
def get_doc_detail(doc_id: int, db: Session = Depends(get_db)):
    doc = get_document_by_id(db, doc_id)
    if not doc:
        return {"error": "文档不存在"}
    return {
        "id": doc.id,
        "filename": doc.filename,
        "filetype": doc.filetype,
        "category": doc.category,
        "version": doc.version,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "content": doc.content
    }

# ---------------------- 管理员删除文档接口 ----------------------
@app.delete("/documents/{doc_id}", summary="【管理员专用】删除文档")
def delete_document(
    doc_id: int,
    admin_secret: str = Query(..., description="管理员操作密钥"),
    db: Session = Depends(get_db)
):
    if admin_secret != ADMIN_SECRET:
        logger.warning(f"有人尝试删除文档id:{doc_id}，密钥错误，权限拒绝")
        raise HTTPException(status_code=403, detail="权限不足，不是管理员")

    doc_info = get_document_by_id(db, doc_id)
    if not doc_info:
        logger.info(f"管理员尝试删除文档id:{doc_id}，文档不存在")
        raise HTTPException(status_code=404, detail="找不到该文档")

    if os.path.exists(doc_info.file_path):
        os.remove(doc_info.file_path)
        logger.info(f"删除本地文件成功：{doc_info.file_path}")

    db.delete(doc_info)
    db.commit()
    logger.info(f"管理员成功删除文档 id:{doc_id}，原文件名：{doc_info.filename}")
    return {"msg": f"文档 {doc_id} 已经删除成功"}

# ========== 管理员：修正文档分类 ==========
@app.put("/admin/documents/{doc_id}/category", summary="【管理员专用】人工修正文档分类")
def update_doc_category(
    doc_id: int,
    new_category: str,
    admin_secret: str = Query(..., description="管理员操作密钥"),
    db: Session = Depends(get_db)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="权限不足，不是管理员")
    doc = get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    allowed_cats = ["培养方案", "考试通知", "课件资料", "行政通知", "社团文件", "未分类"]
    if new_category not in allowed_cats:
        raise HTTPException(status_code=400, detail="分类名不合法，可选分类：" + "/".join(allowed_cats))
    doc.category = new_category
    doc.category_confirmed = 1
    db.commit()
    logger.info(f"管理员修正文档id:{doc_id}分类为：{new_category}")
    return {"msg": f"分类已更新为：{new_category}", "doc_id": doc_id, "category": new_category}

# ========== 管理员：查看全部文档索引列表 ==========
@app.get("/admin/documents", summary="【管理员专用】查看全部文档索引")
def admin_get_all_docs(
    admin_secret: str = Query(..., description="管理员操作密钥"),
    db: Session = Depends(get_db)
):
    if admin_secret != ADMIN_SECRET:
        logger.warning("非法访问管理员文档列表，密钥错误")
        raise HTTPException(status_code=403, detail="权限不足，不是管理员")
    all_docs = list_documents(db)
    result = []
    for item in all_docs:
        result.append({
            "id": item.id,
            "filename": item.filename,
            "filetype": item.filetype,
            "category": item.category,
            "version": item.version,
            "is_latest": item.is_latest,
            "uploaded_at": item.uploaded_at.isoformat() if item.uploaded_at else None
        })
    logger.info(f"管理员查看全部文档，共{len(result)}条记录")
    return result

# ========== 管理员：查看文档历史版本 ==========
@app.get("/admin/documents/{doc_id}/versions", summary="【管理员专用】查看文档所有历史版本")
def get_doc_versions(
    doc_id: int,
    admin_secret: str = Query(..., description="管理员操作密钥"),
    db: Session = Depends(get_db)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="权限不足")
    all_versions = []
    current_doc = get_document_by_id(db, doc_id)
    while current_doc:
        all_versions.append({
            "id": current_doc.id,
            "filename": current_doc.filename,
            "version": current_doc.version,
            "is_latest": current_doc.is_latest,
            "uploaded_at": current_doc.uploaded_at.isoformat()
        })
        current_doc = get_document_by_id(db, current_doc.parent_doc_id) if current_doc.parent_doc_id else None
    return all_versions

# ========== RAG智能问答接口（学生可访问） ==========
@app.post("/ask/", summary="RAG智能问答（本地大模型生成回答）")
def ask_question(question: str, db: Session = Depends(get_db)):
    if not question.strip():
        return {"error": "问题不能为空"}

    top_results = search_top3_chunks("./campus.db", question)
    if not top_results:
        return {
            "answer": "系统里还没有上传任何文档，先让管理员上传资料再提问哦",
            "sources": []
        }

    context = "\n---\n".join([r["text"] for r in top_results])
    prompt = f"""你是校园资料助手，必须严格根据下面给出的文档片段回答学生问题，
    如果文档里没有相关内容，就直接说"根据现有资料暂时找不到相关信息"，绝对不允许编造内容。
    
    参考文档片段：
    {context}
    
    学生问题：{question}
    请用简洁通顺的中文回答："""

    try:
        ai_answer = chat_with_llm(prompt)
    except Exception as e:
        return {"error": f"本地大模型连接失败，请确认Ollama后台已启动: {str(e)}", "sources": []}

    sources = []
    seen_doc_ids = set()
    for item in top_results:
        if item["doc_id"] not in seen_doc_ids:
            seen_doc_ids.add(item["doc_id"])
            doc = get_document_by_id(db, item["doc_id"])
            if doc:
                sources.append({
                    "doc_id": doc.id,
                    "doc_name": doc.filename,
                    "relevance_score": round(item["score"], 3)
                })

    return {
        "answer": ai_answer,
        "sources": sources
    }

# 启动入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
