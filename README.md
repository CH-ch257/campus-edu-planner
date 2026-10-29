# 校园资料AI检索助手（campus-edu-planner）

基于本地 RAG 的校园文档智能问答系统。全部功能离线可运行，不依赖任何云端 API，自带本地向量模型与本地大模型，适合在无外网/内网环境演示。

## 功能特性

- 👤 **三角色体系**：高级管理员（用户管理+公开内容总管理）、教师（文档管理+问答评语）、学生（自由问答+历史留痕）
- 📄 **文档管理**：教师上传/删除/改分类/历史版本回滚，学生默认只看最新版
- 🏷️ **AI 自动分类**：上传后自动分为 6 类（培养方案/考试通知/课件资料/行政通知/社团文件/作业），可人工修正
- 🔍 **本地 RAG 检索**：BAAI/bge-small-zh-v1.5 中文向量模型 + 相似度检索
- 🤖 **本地大模型流式问答**：Ollama + qwen2.5:3b，SSE 打字机输出，回答自动标注参考来源防幻觉；相似度阈值 0.45 自动区分"文档问答/闲聊"
- 📝 **问答留痕与分享**：每次问答自动存档，支持私有/仅链接/公开三档权限、生成分享链接、个人公开主页
- 🌐 **问答广场**：学生端聚合浏览全校公开问答的入口，点击提问者名字可进入其个人主页
- 💬 **追加备注**：学生可对公开问答追加多条备注（非覆盖，上限 10 条防刷屏），教师可直接整条删除问答兜底（级联清理备注）
- ⭐ **教师评语**：教师可对自己文档相关的公开问答写评语，学生端全页可见
- 🎨 **前端工程**：Vue3 + Vite + Pinia + Element Plus，路由级角色守卫

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy / SQLite |
| 向量 | sentence-transformers + BAAI/bge-small-zh-v1.5 |
| 大模型 | Ollama + qwen2.5:3b（OpenAI 兼容接口） |
| 前端 | Vue3 + Vite + Pinia + Vue Router + Element Plus |

## 10 分钟极速复现

> 全程离线运行，只需一次性联网下载模型。

### 0. 环境要求

- Windows 10/11（或 Linux/macOS）
- Python 3.10+
- Node.js 18+
- 已安装 [Ollama](https://ollama.com/download)

### 1. 克隆仓库

```bash
git clone <你的仓库地址>.git
cd campus-edu-planner
```

### 2. 拉取本地大模型（约 2 分钟，需联网）

```bash
ollama pull qwen2.5:3b
```

### 3. 启动后端（backend/ 目录）

```bash
cd backend

# 创建虚拟环境并安装依赖
python -m venv venv
venv\Scripts\activate        # Windows；Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# 国内网络需配置 HF 镜像（海外可跳过）
export HF_ENDPOINT=https://hf-mirror.com   # Windows PowerShell: $env:HF_ENDPOINT="https://hf-mirror.com"

# 启动服务（监听 0.0.0.0:8000，首次启动自动建库并下载向量模型）
uvicorn main:app --host 0.0.0.0
```

### 4. 启动前端（frontend/ 目录，另开一个终端）

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问与登录

浏览器打开 <http://localhost:5173>

| 角色 | 账号 | 密码 | 说明 |
|---|---|---|---|
| 高级管理员 | admin | admin123 | 用户管理、公开内容总管理 |
| 教师 | teacher | teacher123 | 文档上传/删除/评语 |
| 学生 | 自行注册 | — | 问答、历史、分享 |

> 局域网演示：同 WiFi 设备访问 `http://<本机IP>:5173`（服务已监听 0.0.0.0）。

### 6. 快速验证（2 分钟）

1. 用 `teacher/teacher123` 登录 → 上传 1 份 PDF/Word 文档 → 系统自动分类
2. 注册学生账号登录 → 提问文档相关问题 → 得到带参考来源的回答（打字机流式输出）
3. 切回教师 → 给该公开问答写评语 → 学生历史页可见
4. 学生进入「问答广场」→ 浏览他人公开问答 → 追加一条备注（上限 10 条，可连加验证）
5. 用 `admin/admin123` 登录 → 用户管理/公开内容管理可用

## 目录结构

```
campus-edu-planner/
├── backend/               # FastAPI 后端
│   ├── main.py            # 路由与业务逻辑
│   ├── database.py        # 数据模型/建表/迁移
│   ├── llm.py             # Ollama 调用与流式输出
│   ├── rag.py             # 向量检索
│   ├── static/uploads/    # 上传文档存储
│   ├── prompt-evidence/   # AI 协同开发过程证据（3 份）
│   └── campus.db          # SQLite 数据库（首次启动自动生成）
├── frontend/              # Vue3 前端
│   └── src/views/         # 登录/问答/历史/教师管理/后台等页面
├── demo_docs/             # 演示用校园文档样例
├── images/                # 界面截图（技术文档用）
├── 技术文档.pdf           # 参赛技术文档（<30 页）
└── README.md
```

## 比赛材料索引

| 材料 | 位置 |
|---|---|
| 技术文档（PDF，含截图） | `技术文档.pdf` / `技术文档.html` |
| AI 协同开发证据（3 份 Prompt 链） | `backend/prompt-evidence/` |
| 演示截图 | `images/` |
| 演示文档样例 | `demo_docs/` |

## 说明

- 开源模型与第三方资源来源已注明（BAAI/bge-small-zh-v1.5、Ollama、Qwen2.5），遵循各自开源协议。
- 数据库 `campus.db` 首次启动自动创建并预置 admin/teacher 账号；若需全新环境删除该文件重启即可。
