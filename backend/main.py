"""
校园资料AI检索系统 - 主接口
"""
import os
import uuid
import json
import hashlib
import logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import (
    init_db, get_db, save_document, list_documents,
    get_document_by_id,
    extract_text_from_pdf, extract_text_from_word, extract_text_from_txt,
    UPLOAD_DIR, Document, User, QuestionAnswer
)
from rag import save_chunks_to_db, search_top3_chunks
from llm import chat_with_llm, chat_stream, classify_document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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


def get_current_teacher(current_user: User = Depends(get_current_user)):
    """文档管理鉴权依赖：仅教师角色可执行"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可执行此操作")
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)):
    """后台管理鉴权依赖：仅高级管理员可执行"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅高级管理员可执行此操作")
    return current_user


@app.get("/me/", summary="获取当前登录用户信息")
def me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username, "role": current_user.role}


@app.post("/upload/", summary="【教师专用】上传文档")
async def upload_document(
    file: UploadFile = File(...),
    confirm: str = Query(None, description="存在同名文档时传yes确认覆盖升级"),
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
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
    doc.teacher_id = teacher.id
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
def del_doc(doc_id:int, db:Session=Depends(get_db), teacher: User = Depends(get_current_teacher)):
    doc = get_document_by_id(db, doc_id)
    if not doc: raise HTTPException(404, "文档不存在")
    if os.path.exists(doc.file_path): os.remove(doc.file_path)
    db.delete(doc); db.commit()
    return {"msg":"删除成功"}

@app.put("/admin/documents/{doc_id}/category")
def fix_cat(doc_id:int, new_category:str, db:Session=Depends(get_db), teacher: User = Depends(get_current_teacher)):
    doc = get_document_by_id(db, doc_id)
    doc.category = new_category
    db.commit()
    return {"msg":"分类已更新"}

@app.get("/admin/documents/{doc_id}/versions")
def get_versions(doc_id:int, db:Session=Depends(get_db), teacher: User = Depends(get_current_teacher)):
    res = []
    seen = set()
    cur = get_document_by_id(db, doc_id)
    while cur and cur.id not in seen:
        seen.add(cur.id)
        res.append({"id":cur.id, "filename":cur.filename, "version":cur.version, "is_latest":cur.is_latest})
        cur = get_document_by_id(db, cur.parent_doc_id) if cur.parent_doc_id else None
    return res

@app.post("/admin/documents/{doc_id}/rollback", summary="【教师专用】回滚到指定历史版本")
def rollback_doc(doc_id:int, db:Session=Depends(get_db), teacher: User = Depends(get_current_teacher)):
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

@app.post("/ask/", summary="AI问答（登录用户，自动留痕，流式输出）")
def ask(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    top = search_top3_chunks("./campus.db", q)
    if not top:
        def gen_no_doc():
            text = "暂无相关文档，请先上传文档后再提问"
            yield f"data: {json.dumps({'c': text}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'sources': []}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            _save_qa(db, current_user.id, q, text, [], [])
        return StreamingResponse(gen_no_doc(), media_type="text/event-stream")
    if top[0]["score"] < 0.45:
        # 相似度阈值：检索结果与问题明显不相关时（如闲聊"你好"），走正常对话，不硬套文档
        prompt = f"你是校园资料助手，请正常回答用户的问题：{q}"
        srcs = []
        doc_ids = []
    else:
        # 每个片段限300字：控制输入长度，显著降低本地CPU模型prefill耗时
        context = "\n".join([i["text"][:300] for i in top])
        prompt = (
            f"你是校园资料助手。请根据下面检索到的文档片段回答用户问题。"
            f"注意：如果文档片段与用户问题明显无关（比如用户只是打招呼、闲聊、问候），请不要引用文档，直接正常回答用户。\n\n"
            f"文档片段：\n{context}\n\n用户问题：{q}"
        )
        srcs = []
        seen = set()
        for i in top:
            if i["doc_id"] not in seen:
                seen.add(i["doc_id"])
                d = get_document_by_id(db, i["doc_id"])
                if d:
                    srcs.append({"doc_id": i["doc_id"], "doc_name": d.filename})
        doc_ids = sorted({i["doc_id"] for i in top})

    def gen_stream():
        full = ""
        try:
            for piece in chat_stream(prompt):
                full += piece
                yield f"data: {json.dumps({'c': piece}, ensure_ascii=False)}\n\n"
        except Exception as e:
            err = f"[大模型临时无响应] {e}"
            full = err
            yield f"data: {json.dumps({'c': err}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'sources': srcs}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        _save_qa(db, current_user.id, q, full, srcs, doc_ids)

    return StreamingResponse(gen_stream(), media_type="text/event-stream")


def _save_qa(db, user_id, question, answer, srcs, doc_ids):
    """流式结束后保存问答记录（留痕）"""
    qa = QuestionAnswer(
        user_id=user_id,
        question=question,
        answer=answer,
        sources=json.dumps(srcs, ensure_ascii=False),
        source_doc_ids=",".join(str(x) for x in doc_ids) if doc_ids else "",
        permission="private",
        note="",
        share_token=uuid.uuid4().hex
    )
    db.add(qa)
    db.commit()
    return qa


def _qa_to_dict(r):
    """问答记录序列化（登录用户自己的历史）"""
    return {
        "id": r.id,
        "question": r.question,
        "answer": r.answer,
        "sources": json.loads(r.sources) if r.sources else [],
        "note": r.note or "",
        "teacher_note": r.teacher_note or "",
        "permission": r.permission,
        "share_token": r.share_token,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
    }


@app.get("/qa/history/", summary="我的问答历史（支持搜索）")
def qa_history(keyword: str = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(QuestionAnswer).filter(QuestionAnswer.user_id == current_user.id)
    if keyword:
        q = q.filter(QuestionAnswer.question.contains(keyword) | QuestionAnswer.answer.contains(keyword))
    records = q.order_by(QuestionAnswer.created_at.desc()).all()
    return [_qa_to_dict(r) for r in records]


@app.put("/qa/{qa_id}/note", summary="给问答记录写备注")
def qa_note(qa_id: int, note: str = Query(""), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id, QuestionAnswer.user_id == current_user.id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    qa.note = note
    db.commit()
    return {"msg": "备注已保存"}


@app.put("/qa/{qa_id}/permission", summary="修改问答权限")
def qa_permission(qa_id: int, permission: str = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if permission not in ("private", "link", "public"):
        raise HTTPException(status_code=400, detail="无效权限")
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id, QuestionAnswer.user_id == current_user.id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    qa.permission = permission
    db.commit()
    return {"msg": "权限已更新", "permission": permission}


@app.post("/qa/{qa_id}/share", summary="生成分享链接")
def qa_share(qa_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id, QuestionAnswer.user_id == current_user.id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    if qa.permission == "private":
        raise HTTPException(status_code=400, detail="私有问答不能分享，请先修改权限")
    return {"share_token": qa.share_token}


@app.get("/qa/share/{token}", summary="分享落地页（无需登录）")
def qa_share_view(token: str, db: Session = Depends(get_db)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.share_token == token).first()
    if not qa or qa.permission == "private":
        raise HTTPException(status_code=404, detail="分享内容不存在或已失效")
    owner = db.query(User).filter(User.id == qa.user_id).first()
    return {
        "question": qa.question,
        "answer": qa.answer,
        "sources": json.loads(qa.sources) if qa.sources else [],
        "note": qa.note or "",
        "teacher_note": qa.teacher_note or "",
        "owner": owner.username if owner else ""
    }


@app.get("/users/{user_id}/profile", summary="用户公开主页信息（无需登录）")
def user_profile(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user_id": u.id, "username": u.username}


@app.get("/users/{user_id}/qa_public", summary="用户公开问答列表（无需登录）")
def user_public_qa(user_id: int, db: Session = Depends(get_db)):
    records = db.query(QuestionAnswer).filter(
        QuestionAnswer.user_id == user_id, QuestionAnswer.permission == "public"
    ).order_by(QuestionAnswer.created_at.desc()).all()
    return [
        {"question": r.question, "answer": r.answer, "note": r.note or "", "teacher_note": r.teacher_note or "",
         "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""}
        for r in records
    ]


@app.post("/change_password/", summary="修改密码")
def change_password(old_password: str = Query(...), new_password: str = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(new_password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4位")
    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"msg": "密码修改成功"}


@app.delete("/qa/{qa_id}", summary="【教师】删除公开问答（仅限本人上传文档关联）")
def del_public_qa(qa_id: int, db: Session = Depends(get_db), teacher: User = Depends(get_current_teacher)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    if qa.permission != "public":
        raise HTTPException(status_code=403, detail="只能删除公开问答")
    doc_ids = [int(x) for x in (qa.source_doc_ids or "").split(",") if x.strip()]
    if doc_ids:
        owned = db.query(Document).filter(Document.id.in_(doc_ids), Document.teacher_id == teacher.id).count()
    else:
        owned = 0
    if owned == 0:
        raise HTTPException(status_code=403, detail="只能删除与你上传文档相关的公开问答")
    db.delete(qa)
    db.commit()
    return {"msg": "删除成功"}


@app.put("/teacher/qa/{qa_id}/note", summary="【教师】给学生公开问答写评语（仅限本人上传文档关联）")
def teacher_qa_note(qa_id: int, note: str = Query(...), db: Session = Depends(get_db), teacher: User = Depends(get_current_teacher)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    if qa.permission != "public":
        raise HTTPException(status_code=403, detail="只能给公开问答写评语")
    doc_ids = [int(x) for x in (qa.source_doc_ids or "").split(",") if x.strip()]
    if doc_ids:
        owned = db.query(Document).filter(Document.id.in_(doc_ids), Document.teacher_id == teacher.id).count()
    else:
        owned = 0
    if owned == 0:
        raise HTTPException(status_code=403, detail="只能给与你上传文档相关的公开问答写评语")
    qa.teacher_note = note.strip()
    db.commit()
    return {"msg": "评语已保存"}


@app.get("/teacher/qa/public/", summary="【教师】查看学生公开问答")
def teacher_public_qa(db: Session = Depends(get_db), teacher: User = Depends(get_current_teacher)):
    rows = db.query(QuestionAnswer, User).join(User, QuestionAnswer.user_id == User.id).filter(
        QuestionAnswer.permission == "public", User.role == "student"
    ).order_by(QuestionAnswer.created_at.desc()).all()
    return [
        {"id": qa.id, "username": u.username, "question": qa.question, "answer": qa.answer,
         "note": qa.note or "", "teacher_note": qa.teacher_note or "",
         "created_at": qa.created_at.strftime("%Y-%m-%d %H:%M") if qa.created_at else ""}
        for qa, u in rows
    ]


@app.get("/admin/qa/public/", summary="【管理员】查看全部公开问答")
def admin_public_qa(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    rows = db.query(QuestionAnswer, User).join(User, QuestionAnswer.user_id == User.id).filter(
        QuestionAnswer.permission == "public"
    ).order_by(QuestionAnswer.created_at.desc()).all()
    return [
        {"id": qa.id, "username": u.username, "question": qa.question, "answer": qa.answer,
         "note": qa.note or "", "teacher_note": qa.teacher_note or "",
         "created_at": qa.created_at.strftime("%Y-%m-%d %H:%M") if qa.created_at else ""}
        for qa, u in rows
    ]


@app.delete("/admin/qa/{qa_id}", summary="【管理员】删除任意公开问答")
def admin_del_public_qa(qa_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    qa = db.query(QuestionAnswer).filter(QuestionAnswer.id == qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    if qa.permission != "public":
        raise HTTPException(status_code=403, detail="只能删除公开问答")
    db.delete(qa)
    db.commit()
    return {"msg": "删除成功"}


@app.get("/admin/users/", summary="【管理员】查看全部用户")
def admin_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {"id": u.id, "username": u.username, "role": u.role, "status": u.status,
         "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else ""}
        for u in users
    ]


@app.post("/admin/teachers/", summary="【管理员】新增老师账号")
def admin_create_teacher(username: str = Query(...), password: str = Query(...), db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4位")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    u = User(username=username, password_hash=hash_password(password), role="teacher", status=1)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"msg": "老师账号已创建", "user_id": u.id, "username": u.username}


@app.delete("/admin/users/{user_id}", summary="【管理员】直接删除用户账号（级联清理其文档与问答）")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    if u.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    if u.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除高级管理员账号")
    # 级联清理：该用户上传的文档 + 该用户的所有问答记录
    db.query(Document).filter(Document.teacher_id == user_id).delete(synchronize_session=False)
    db.query(QuestionAnswer).filter(QuestionAnswer.user_id == user_id).delete(synchronize_session=False)
    db.delete(u)
    db.commit()
    return {"msg": "用户已删除"}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 让局域网内其他设备也能通过本机IP访问
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
