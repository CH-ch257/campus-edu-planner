"""
校园资料AI检索系统 - 主接口
"""
import os
import uuid
import hashlib
import logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import (
    init_db, get_db, save_document, list_documents,
    get_document_by_id,
    extract_text_from_pdf, extract_text_from_word, extract_text_from_txt,
    UPLOAD_DIR, Document, User
)
from rag import save_chunks_to_db, search_top3_chunks
from llm import chat_with_llm, classify_document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
ADMIN_SECRET = "admin123456"


def hash_password(password: str, salt: str = None) -> str:
    """对密码加盐做SHA256哈希，返回 salt:hash 形式"""
    salt = salt or uuid.uuid4().hex
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码是否与存储的哈希一致"""
    try:
        salt, digest = stored.split(":", 1)
    except ValueError:
        return False
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == digest

app = FastAPI(title="校园资料AI检索助手", version="1.0.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# 挂载静态资源目录（docx-preview等前端库）
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", summary="前端首页")
def read_root():
    return FileResponse("index.html")


@app.post("/register/", summary="用户注册")
def register(username: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4位")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=username, password_hash=hash_password(password), role="student", status=1)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "注册成功", "user_id": user.id, "username": user.username}


@app.post("/login/", summary="用户登录")
def login(username: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=403, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    user.token = uuid.uuid4().hex
    db.commit()
    return {"msg": "登录成功", "user_id": user.id, "username": user.username, "role": user.role, "token": user.token}


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """解析 Authorization: Bearer <token>，返回当前登录用户，未登录/失效返回 401"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization[7:].strip()
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return user


@app.get("/me/", summary="获取当前登录用户信息")
def me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username, "role": current_user.role}


@app.post("/upload/", summary="【管理员专用】上传文档")
async def upload_document(
    file: UploadFile = File(...),
    admin_secret: str = Query(...),
    confirm: str = Query(None, description="存在同名文档时传yes确认覆盖升级"),
    db: Session = Depends(get_db)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="权限不足")
    ext = file.filename.lower().split(".")[-1]
    if ext == "pdf": filetype = "pdf"
    elif ext in ["doc","docx"]: filetype = "word"
    elif ext == "txt": filetype = "txt"
    else: return {"error": "只支持PDF/Word/TXT"}
    # 先检查是否存在同名最新版（写文件之前检查，避免残留孤儿文件）
    old = db.query(Document).filter(Document.filename==file.filename, Document.is_latest==1).first()
    if old and confirm != "yes":
        return {"need_confirm": True, "current_version": old.version, "msg": "存在同名文档，请确认是否覆盖升级"}
    safe_name = str(uuid.uuid4()) + "." + ext
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f: f.write(await file.read())
    if filetype == "pdf": content = extract_text_from_pdf(file_path)
    elif filetype == "word": content = extract_text_from_word(file_path)
    else: content = extract_text_from_txt(file_path)
    # 必须先查同名最新版本（在保存新文档之前查，否则会查到刚插入的自己，导致第一次上传就变v2）
    old = db.query(Document).filter(Document.filename==file.filename, Document.is_latest==1).first()
    doc = save_document(db, file.filename, filetype, file_path, content)
    if old:
        old.is_latest = 0
        doc.version = old.version + 1
        doc.parent_doc_id = old.id
    doc.is_latest = 1
    db.commit()
    if doc.content.strip():
        save_chunks_to_db("./campus.db", doc.id, doc.content)
        try:
            doc.category = classify_document(doc.content)
            db.commit()
        except: pass
    return {"msg":"上传成功", "filename":doc.filename, "version":doc.version, "category":doc.category}

@app.get("/documents/")
def get_docs(db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.is_latest==1).order_by(Document.uploaded_at.desc()).all()
    return [{"id":d.id, "filename":d.filename, "category":d.category, "version":d.version} for d in docs]

@app.get("/documents/search/")
def search_docs(keyword: str, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.filename.contains(keyword), Document.is_latest==1).all()
    return [{"id":d.id, "filename":d.filename, "category":d.category, "version":d.version} for d in docs]

@app.get("/documents/{doc_id}")
def get_doc_detail(doc_id:int, db:Session=Depends(get_db)):
    doc = get_document_by_id(db, doc_id)
    if not doc: raise HTTPException(404, "文档不存在")
    return {"id":doc.id, "filename":doc.filename, "category":doc.category, "version":doc.version, "content":doc.content}

@app.get("/file/{doc_id}", summary="查看/下载原始文件")
def get_file(doc_id:int, db:Session=Depends(get_db)):
    doc = get_document_by_id(db, doc_id)
    if not doc: raise HTTPException(404, "文档不存在")
    if not os.path.exists(doc.file_path): raise HTTPException(404, "原文件已丢失")
    # 按类型返回正确MIME：PDF浏览器直接预览，TXT直接显示，Word可下载后用Word打开
    media_map = {
        "pdf": "application/pdf",
        "word": "application/msword",
        "txt": "text/plain; charset=utf-8"
    }
    return FileResponse(doc.file_path, filename=doc.filename, media_type=media_map.get(doc.filetype, "application/octet-stream"))

@app.delete("/documents/{doc_id}")
def del_doc(doc_id:int, admin_secret:str=Query(...), db:Session=Depends(get_db)):
    if admin_secret != ADMIN_SECRET: raise HTTPException(403, "权限不足")
    doc = get_document_by_id(db, doc_id)
    if not doc: raise HTTPException(404, "文档不存在")
    if os.path.exists(doc.file_path): os.remove(doc.file_path)
    db.delete(doc); db.commit()
    return {"msg":"删除成功"}

@app.put("/admin/documents/{doc_id}/category")
def fix_cat(doc_id:int, new_category:str, admin_secret:str=Query(...), db:Session=Depends(get_db)):
    if admin_secret != ADMIN_SECRET: raise HTTPException(403, "权限不足")
    doc = get_document_by_id(db, doc_id)
    doc.category = new_category
    db.commit()
    return {"msg":"分类已更新"}

@app.get("/admin/documents/{doc_id}/versions")
def get_versions(doc_id:int, admin_secret:str=Query(...), db:Session=Depends(get_db)):
    if admin_secret != ADMIN_SECRET: raise HTTPException(403, "权限不足")
    res = []
    seen = set()
    cur = get_document_by_id(db, doc_id)
    while cur and cur.id not in seen:
        seen.add(cur.id)
        res.append({"id":cur.id, "filename":cur.filename, "version":cur.version, "is_latest":cur.is_latest})
        cur = get_document_by_id(db, cur.parent_doc_id) if cur.parent_doc_id else None
    return res

@app.post("/admin/documents/{doc_id}/rollback", summary="【管理员专用】回滚到指定历史版本")
def rollback_doc(doc_id:int, admin_secret:str=Query(...), db:Session=Depends(get_db)):
    if admin_secret != ADMIN_SECRET: raise HTTPException(403, "权限不足")
    target = get_document_by_id(db, doc_id)
    if not target: raise HTTPException(404, "文档不存在")
    # 把同文件名下当前的最新版标记为历史版
    latest = db.query(Document).filter(Document.filename==target.filename, Document.is_latest==1).first()
    if latest and latest.id != target.id:
        latest.is_latest = 0
        logger.info(f"回滚：旧最新版v{latest.version}已标记为历史版")
    target.is_latest = 1
    db.commit()
    logger.info(f"管理员已将文档《{target.filename}》回滚到v{target.version}")
    return {"msg": f"已回滚到 v{target.version}", "filename": target.filename, "version": target.version}

@app.post("/ask/")
def ask(q:str, db:Session=Depends(get_db)):
    top = search_top3_chunks("./campus.db", q)
    if not top: return {"answer":"暂无相关文档，请先上传文档后再提问", "sources":[]}
    # 相似度阈值：检索结果与问题明显不相关时（如闲聊"你好"），走正常对话，不硬套文档
    if top[0]["score"] < 0.35:
        ans = chat_with_llm(f"你是校园资料助手，请正常回答用户的问题：{q}")
        return {"answer": ans, "sources": []}
    context = "\n".join([i["text"] for i in top])
    try:
        ans = chat_with_llm(
            f"你是校园资料助手。请根据下面检索到的文档片段回答用户问题。"
            f"注意：如果文档片段与用户问题明显无关（比如用户只是打招呼、闲聊、问候），请不要引用文档，直接正常回答用户。\n\n"
            f"文档片段：\n{context}\n\n用户问题：{q}"
        )
    except:
        ans = f"[大模型临时无响应] 检索内容：{context[:500]}"
    srcs = []
    seen = set()
    for i in top:
        if i["doc_id"] not in seen:
            seen.add(i["doc_id"])
            d = get_document_by_id(db, i["doc_id"])
            if d: srcs.append({"doc_name":d.filename})
    return {"answer":ans, "sources":srcs}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 让局域网内其他设备也能通过本机IP访问
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
