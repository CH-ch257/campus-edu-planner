# Prompt证据1：RAG向量检索模块开发
## 1. 初始需求
我：帮我搭一个FastAPI后端，实现上传PDF/Word文档，自动提取文本、分块、存向量数据库，支持相似度检索
AI：给我搭了基础FastAPI骨架，写了数据库ORM、pdf/word文本提取函数，用bge-small-zh-v1.5做向量编码
## 2. 遇到的Bug与修复
- Bug1：导入numpy/sentence-transformers报错ModuleNotFoundError
  我：提示缺numpy，帮我解决
  AI：指导我在虚拟环境里pip安装依赖，不要用全局Python
- Bug2：启动时连接huggingface官网超时，WinError10060
  我：为什么加载向量模型一直超时？
  AI：指导我配置国内HF镜像，export HF_ENDPOINT=https://hf-mirror.com，解决下载超时问题
- Bug3：向量模型仓库名写错，404
  我：加载模型报404，找不到BAAI/bge-small-zh-v1.5
  AI：帮我核对正确的模型仓库地址，修正导入路径
- Bug4：手动测试search_top3_chunks函数，成功返回Dart实验报告的相关文本片段，验证检索链路正常
