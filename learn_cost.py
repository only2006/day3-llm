import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 单价模拟平台定价页抄来的数字（元 / 百万 tokens）
PRICE_INPUT = 2.0
PRICE_OUTPUT = 8.0


def cost(usage) -> float:
    """返回本次调用的美元成本。"""
    return (
        usage.prompt_tokens * PRICE_INPUT
        + usage.completion_tokens * PRICE_OUTPUT
    ) / 1_000_000


resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话解释什么是RAG"}],
    max_tokens=100,
)
usage = resp.usage
print("回答：", resp.choices[0].message.content)
print(f"本次消耗：输入 {usage.prompt_tokens} + 输出 {usage.completion_tokens} token")
print(f"本次成本：约 {cost(usage):.6f} 元")