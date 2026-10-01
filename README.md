# 校园资料AI检索助手（campus-edu-planner）
基于本地RAG的校园文档智能问答系统，全部功能离线可运行，不依赖云端API。
## 功能特性
- 📄 支持PDF/Word文档上传，自动提取文本
- 🔍 本地中文向量模型（BAAI/bge-small-zh-v1.5）实现语义检索
- 🤖 本地部署Qwen2:1.5b开源大模型，生成回答自动标注参考文档来源，防止幻觉
- 🏷️ 上传文档后AI自动分类为培养方案/考试通知/课件资料/行政通知/社团文件，支持管理员人工修正
- 🔐 两级权限：学生自由查询问答，管理员密钥才能上传/删除文档
- 📝 文档版本管理：同名文档自动保留历史版本，学生默认只看最新版，管理员可查看历史版本
## 10分钟复现步骤
### 环境要求
- Windows 10/11，Python 3.10+
- 安装Ollama：https://ollama.com/download
### 1. 克隆仓库
```bash
git clone 你的仓库地址.git
cd campus-edu-planner/backend
