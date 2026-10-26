from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120.0,   # 本地模型推理较慢，最多等120秒
    max_retries=0    # 不自动重试，避免等待时间翻倍
)

def chat_with_llm(prompt: str) -> str:
    """调用本地千问模型生成回答"""
    try:
        response = client.chat.completions.create(
            model="qwen2:1.5b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[本地大模型暂时无响应] 检索到的相关内容：{prompt[-500:]}"

def classify_document(doc_content: str) -> str:
    """自动给上传的文档分类"""
    preview = doc_content[:500]
    prompt = f"""你是校园文档分类助手，把下面这份文档分到以下5类中的一类：
    可选分类：培养方案、考试通知、课件资料、行政通知、社团文件
    只返回分类名称。
    文档内容：{preview}
    分类结果："""
    try:
        result = chat_with_llm(prompt).strip()
        allowed_cats = ["培养方案", "考试通知", "课件资料", "行政通知", "社团文件"]
        for cat in allowed_cats:
            if cat in result:
                return cat
    except:
        pass
    return "未分类"
