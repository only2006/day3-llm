
import logging
import os
import sys

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

PRICE_INPUT = 2.0      # 元 / 百万 tokens，按平台定价页填写
PRICE_OUTPUT = 8.0

MAX_TURNS = 10         # 只保留最近 10 轮，防止上下文无限增长

SYSTEM_PROMPT = "你是一个耐心的技术助教，回答简洁，必要时给例子。"

EXIT_WORDS = {"exit", "quit", "q", "退出", "再见", "拜拜"}


def make_client() -> OpenAI:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        logger.error("没读到 DEEPSEEK_API_KEY，请检查 .env")
        raise SystemExit(1)
    return OpenAI(api_key=key, base_url=BASE_URL)


def trim_history(messages: list[dict], max_turns: int) -> list[dict]:
    """保留 system + 最近 max_turns 轮对话。"""
    system = [m for m in messages if m["role"] == "system"]
    dialogue = [m for m in messages if m["role"] != "system"]
    return system + dialogue[-(max_turns * 2):]


def stream_reply(client: OpenAI, messages: list[dict]) -> tuple[str, object]:
    """流式请求，返回（完整回答, usage）。"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        temperature=1.0,
        max_tokens=800,
    )

    pieces: list[str] = []
    usage = None
    for chunk in stream:
        if chunk.choices:
            piece = chunk.choices[0].delta.content
            if piece:
                pieces.append(piece)
                print(piece, end="", flush=True)
        if chunk.usage:
            usage = chunk.usage

    print()
    return "".join(pieces), usage


def main() -> int:
    client = make_client()
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    total_cost = 0.0

    print("AI 助手已就绪。输入 exit / 退出 结束。\n")

    while True:
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_WORDS:
            print("已退出。")
            break

        messages.append({"role": "user", "content": user_input})

        print("AI：", end="", flush=True)
        try:
            reply, usage = stream_reply(client, messages)
        except AuthenticationError:
            logger.error("API Key 无效（401），检查 .env")
            return 1
        except RateLimitError:
            logger.error("触发限流（429），稍后重试或充值")
            return 2
        except APITimeoutError:
            logger.error("请求超时，检查网络")
            return 3
        except APIConnectionError:
            logger.error("连接失败，检查网络或 base_url")
            return 4
        except BadRequestError as exc:
            logger.error("请求被拒绝（400）：%s", exc)
            logger.info("常见原因：上下文超出上限 / 参数非法")
            return 5

        messages.append({"role": "assistant", "content": reply})

        if usage:
            turn_cost = (
                usage.prompt_tokens * PRICE_INPUT
                + usage.completion_tokens * PRICE_OUTPUT
            ) / 1_000_000
            total_cost += turn_cost
            logger.info(
                "本轮 in=%d out=%d  %.4f 元 | 累计 %.4f 元",
                usage.prompt_tokens,
                usage.completion_tokens,
                turn_cost,
                total_cost,
            )

        messages = trim_history(messages, MAX_TURNS)

    logger.info("本次会话共花费 %.4f 元", total_cost)
    return 0


if __name__ == "__main__":
    sys.exit(main())