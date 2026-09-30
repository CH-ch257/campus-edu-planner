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
