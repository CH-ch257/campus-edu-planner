"""
RAG向量检索模块：文本分块、向量生成、相似度检索
"""
import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载中文向量模型（BAAI官方正确仓库名）
print("正在加载向量模型，请稍等...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
print("✅ 向量模型加载完成")


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """把长文本切分成固定长度的块，块之间保留重叠避免语义断裂"""
    chunks = []
    text_len = len(text)
    start = 0
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def save_chunks_to_db(db_path: str, doc_id: int, full_text: str):
    """把文档切分后生成向量，存入sqlite的chunks表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 先删除这个文档旧的分块（重复上传时覆盖）
    cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
    chunks = split_text(full_text)
    for chunk_text in chunks:
        # 生成向量，转成json字符串存数据库
        embedding = model.encode(chunk_text).tolist()
        cursor.execute(
            "INSERT INTO chunks (doc_id, chunk_text, embedding) VALUES (?, ?, ?)",
            (doc_id, chunk_text, json.dumps(embedding))
        )
    conn.commit()
    conn.close()
    print(f"✅ 文档id:{doc_id} 已完成分块，共{len(chunks)}个文本块")


def search_top3_chunks(db_path: str, question: str) -> list:
    """根据用户问题，检索相似度最高的3个文本块"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, doc_id, chunk_text, embedding FROM chunks")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # 把用户问题转成向量
    query_emb = model.encode(question)
    scored = []
    for row_id, doc_id, chunk_text, emb_str in rows:
        chunk_emb = np.array(json.loads(emb_str))
        # 余弦相似度计算
        sim = np.dot(query_emb, chunk_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb))
        scored.append((sim, chunk_text, doc_id))

    # 按相似度从高到低排序，取前3
    scored.sort(reverse=True, key=lambda x: x[0])
    top3 = scored[:3]
    return [{"score": float(sim), "text": txt, "doc_id": did} for sim, txt, did in top3]
