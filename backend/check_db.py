import sqlite3
conn = sqlite3.connect(r'D:\zuoye\campus-edu-planner\backend\campus.db')
c = conn.cursor()
# 删除1.txt的坏记录（id 8、9）及其向量分块
c.execute("DELETE FROM chunks WHERE doc_id IN (8, 9)")
c.execute("DELETE FROM documents WHERE id IN (8, 9)")
conn.commit()
print("已删除1.txt坏记录及对应分块")
c.execute("SELECT id, filename, version, is_latest, parent_doc_id FROM documents")
for r in c.fetchall():
    print(r)
