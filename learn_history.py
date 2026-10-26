import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

messages = [{"role": "system", "content": "你叫小助。"}]

def ask(question: str) -> str:
    messages.append({"role": "user", "content": question})
    global resp
    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, max_tokens=100
    )
    answer = resp.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer

print(ask("我叫小明，记住。"))
print(ask("我叫什么？"))          # 能答出"小明"，因为历史带上了
print(f"当前消息数：{len(messages)}，本次输入 token：{resp.usage.prompt_tokens}")

