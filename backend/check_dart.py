from database import get_db, Document
from rag import search_top3_chunks

db = next(get_db())
docs = db.query(Document).filter(Document.filename.like('%Dart%')).all()
for d in docs:
    print(f'id={d.id} v{d.version} is_latest={d.is_latest} parent={d.parent_doc_id} 内容前60字: {d.content[:60]}')

print('---Dart问题检索Top3---')
r = search_top3_chunks('./campus.db', 'Dart里List有哪些常用方法')
for i in r:
    print('score=%.3f doc_id=%s text=%s' % (i['score'], i['doc_id'], i['text'][:50]))
