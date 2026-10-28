from database import get_db, Document
from sqlalchemy import text

db = next(get_db())
# 查chunks表里doc_id=1（实验报告）的所有分块
rows = db.execute(text("SELECT id, doc_id, chunk_text FROM chunks WHERE doc_id=1")).fetchall()
print(f'实验报告(doc_id=1)的分块数: {len(rows)}')
for r in rows[:10]:
    print(f'chunk_id={r[0]} text={r[2][:80]}')
print('---包含List关键词的分块---')
hits = [r for r in rows if 'List' in r[2] or 'list' in r[2]]
print(f'数量: {len(hits)}')
for r in hits[:5]:
    print(f'chunk_id={r[0]} text={r[2][:120]}')
