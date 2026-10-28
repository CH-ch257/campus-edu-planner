from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120.0,   # 本地模型推理较慢，最多等120秒
    max_retries=0    # 不自动重试，避免等待时间翻倍
)

def chat_with_llm(prompt: str) -> str:
    """调用本地千问模型生成回答（非流式，用于分类等短任务）"""
    try:
        response = client.chat.completions.create(
            model="qwen2.5:3b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
            extra_body={"keep_alive": -1}   # 模型常驻内存，避免每次问答重新加载
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[本地大模型暂时无响应] 检索到的相关内容：{prompt[-500:]}"

def chat_stream(prompt: str):
    """流式调用本地千问模型，逐块 yield 生成内容；模型常驻内存 + 限制输出长度保证响应速度"""
    try:
        stream = client.chat.completions.create(
            model="qwen2.5:3b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,                 # 限制单次回答长度，防止无限生成拖慢演示
            stream=True,
            extra_body={"keep_alive": -1}   # 模型常驻内存，避免每次问答重新加载
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
    except Exception as e:
        yield f"[本地大模型暂时无响应] {e}"

def classify_document(doc_content: str) -> str:
    """自动给上传的文档分类"""
    preview = doc_content[:500]
    prompt = f"""你是校园文档分类助手，把下面这份文档分到以下6类中的一类：
    可选分类：培养方案、考试通知、课件资料、行政通知、社团文件、作业
    作业指学生提交的实验报告、课程作业、用例规约等；课件资料指老师上课用的PPT、讲义、教案。
    只返回分类名称。
    文档内容：{preview}
    分类结果："""
    try:
        result = chat_with_llm(prompt).strip()
        # 优先精确匹配
        allowed_cats = ["培养方案", "考试通知", "课件资料", "行政通知", "社团文件", "作业"]
        for cat in allowed_cats:
            if cat in result:
                return cat
        # 同义词兜底：模型回答不标准时也能归类
        if any(k in result for k in ["实验", "作业", "用例", "报告"]):
            return "作业"
        if any(k in result for k in ["课件", "讲义", "教案", "PPT", "ppt"]):
            return "课件资料"
    except:
        pass
    return "未分类"
