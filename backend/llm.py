from openai import OpenAI


# 连接本地Ollama服务，key随便填
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def chat_with_llm(prompt: str) -> str:
    """调用本地千问模型生成回答"""
    response = client.chat.completions.create(
        model="qwen2:1.5b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


# 下面是新增的自动分类函数
def classify_document(doc_content: str) -> str:
    """自动给上传的文档分类，返回分类标签"""
    preview = doc_content[:500]
    prompt = f"""你是校园文档分类助手，把下面这份文档分到以下5类中的一类：
    可选分类：培养方案、考试通知、课件资料、行政通知、社团文件
    只返回分类名称，不要返回其他任何解释文字。
    
    文档内容预览：
    {preview}
    分类结果："""
    result = chat_with_llm(prompt).strip()
    allowed_cats = ["培养方案", "考试通知", "课件资料", "行政通知", "社团文件"]
    for cat in allowed_cats:
        if cat in result:
            return cat
    return "未分类"
