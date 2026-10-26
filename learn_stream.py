import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用三句话介绍 Python"}],
    stream=True,
    stream_options={"include_usage": True},  # 流式下要它才返回 token 统计
)

full_text = ""
for chunk in stream:
    if chunk.choices:                     # 最后一个 chunk 的 choices 是空列表
        piece = chunk.choices[0].delta.content
        if piece:
            full_text += piece
            print(piece, end="", flush=True)
    if chunk.usage:                       # 只在最后一块出现
        print(f"\n\n本次消耗: {chunk.usage.total_tokens} tokens")
