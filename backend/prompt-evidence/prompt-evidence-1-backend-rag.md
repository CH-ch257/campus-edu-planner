# Prompt证据1：后端基础与RAG检索模块
## 1. 初始需求
我：帮我搭一个FastAPI后端，实现上传PDF/Word/TXT文档，自动提取文本、分块、存向量数据库，支持相似度检索。系统现在太基础了，还要加：AI自动给文档分类、两级权限（只有管理员能上传）、文档版本管理（同名文档自动保留旧版本）
AI：搭了FastAPI骨架和SQLAlchemy数据库ORM，实现pdf/word/txt文本提取、按500字分块、bge-small-zh-v1.5向量化存入SQLite；documents表加category/version/is_latest/parent_doc_id字段，上传后自动调用大模型按校园场景分6类（培养方案/考试通知/课件资料/行政通知/社团文件/作业），同名上传自动标记旧版本并升级版本号
## 2. 遇到的Bug与修复
- Bug1：导入numpy/sentence-transformers报ModuleNotFoundError
  我：提示缺numpy，帮我解决
  AI：指导在虚拟环境里pip安装依赖，不要用全局Python
- Bug2：启动时连接huggingface官网超时，WinError10060
  我：为什么加载向量模型一直超时？
  AI：配置国内HF镜像export HF_ENDPOINT=https://hf-mirror.com，解决下载超时
- Bug3：向量模型仓库名写错报404
  我：加载模型报404，找不到BAAI/bge-small-zh-v1.5
  AI：核对正确模型仓库地址，修正导入路径
- Bug4：上传后学生列表看不到新文档
  我：我刚传完文档，右边列表里根本不显示
  AI：新上传的文档is_latest字段没设成1被学生列表过滤，显式赋值doc.is_latest=1解决
- Bug5：前端fetch调用后端接口报CORS错误
  我：浏览器控制台全是CORS报错
  AI：FastAPI加CORSMiddleware中间件允许跨域访问
- Bug6：上传同名文档时版本号没自动升级
  我：传了同名的第二次文档，列表里还是旧版本
  AI：加版本升级逻辑，旧文档is_latest置0，新文档版本号+1，学生只看最新版，管理员能查全部历史版本
- 最终验证：上传文档自动分类到6类、同名上传版本自动+1、search_top3_chunks能正确返回Dart实验报告相关片段，检索链路正常
