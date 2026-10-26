# check_env.py
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("DEEPSEEK_API_KEY")

if not key:
    raise SystemExit("没读到 DEEPSEEK_API_KEY")

print(f"读到：{key[:6]}...{key[-4:]}")
