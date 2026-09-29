好现在下一步是到完善开发 RAG 文本分块 + 向量检索


基于我现有的 FastAPI 项目。现有项目结构：main.py、database.py，使用 SQLite。
任务：新建独立文件 rag.py，实现 RAG 分块、embedding 生成、余弦相似度检索函数。禁止修改 main.py、database.py 已有代码。
技术约束：
使用 bge-small-zh-v1.5 作为 embedding 模型
文本分块：chunk_size=500，chunk_overlap=100
向量结果转为 json 字符串，存入 sqlite 的 chunks 表
新增数据库表 chunks，字段：id, doc_id（关联文档表）, chunk_text, embedding
实现余弦相似度计算函数，检索返回 top3 最相关 chunk
增加异常捕获，文档为空、模型加载失败返回标准 JSON 错误
只输出代码，附带简短注释，不要重构原有模块。
python
运行
# rag.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3

# 全局加载Embedding模型，增加异常捕获
try:
    model = SentenceTransformer("bge-small-zh-v1.5")
except Exception as e:
    raise RuntimeError(f"模型加载失败: {str(e)}")


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    """文本分块，按固定长度+重叠窗口"""
    if not text or len(text.strip()) == 0:
        raise ValueError("文档文本为空")
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    return chunks


def get_embedding(text: str) -> str:
    """生成向量，转为json字符串用于数据库存储"""
    vec = model.encode(text)
    return json.dumps(vec.tolist())


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """余弦相似度计算"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


def save_chunks_to_db(db_path: str, doc_id: int, text: str):
    """拆分文档、生成向量，批量存入chunks表"""
    chunks = split_text(text)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        for chunk in chunks:
            emb_json = get_embedding(chunk)
            cur.execute(
                "INSERT INTO chunks(doc_id, chunk_text, embedding) VALUES (?, ?, ?)",
                (doc_id, chunk, emb_json)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def search_top3_chunks(db_path: str, query: str) -> list[dict]:
    """根据查询语句做向量检索，返回相似度最高前3个块"""
    query_emb_json = get_embedding(query)
    query_vec = json.loads(query_emb_json)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, doc_id, chunk_text, embedding FROM chunks")
        rows = cur.fetchall()
    finally:
        conn.close()

    result_list = []
    for row in rows:
        chunk_id, doc_id, chunk_text, emb_str = row
        emb_vec = json.loads(emb_str)
        score = cosine_similarity(query_vec, emb_vec)
        result_list.append({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "chunk_text": chunk_text,
            "score": score
        })
    # 相似度降序，取top3
    result_list.sort(key=lambda x: x["score"], reverse=True)
    return result_list[:3]
chunks 建表 SQL（加到 database.py 初始化部分）
sql
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER,
    chunk_text TEXT,
    embedding TEXT,
    FOREIGN KEY(doc_id) REFERENCES documents(id)
);
依赖安装
bash
pip install sentence-transformers numpy
本次 Git 提交
bash
git add rag.py
git commit -m "feat: 新增rag.py，实现文本分块、bge-small-zh向量生成、余弦相似度检索"