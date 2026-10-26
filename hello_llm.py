import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",   # 硅基流动改成 https://api.siliconflow.cn/v1
)

response = client.chat.completions.create(
    model="deepseek-chat",                 # 以平台模型列表为准
    messages=[
        {"role": "system", "content": "你是一个简洁的助手，回答不超过 50 字。"},
        {"role": "user", "content": "用一句话解释什么是 RAG"},
    ],
    temperature=1.0,
    max_tokens=200,
)

print(response.choices[0].message.content)
print("----")
print(response.usage)