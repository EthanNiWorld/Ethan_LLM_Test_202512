# text/test_qwen_max.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DASHSCOPE_API_KEY
from dashscope import Generation

# ====== 1. 获取命令行参数 ======
if len(sys.argv) < 2:
    print("用法: python test_qwen_max.py \"你的提示词\"")
    sys.exit(1)

user_prompt = sys.argv[1]  # 第一个参数就是提示词

# ====== 2. 构造 messages ======
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": user_prompt},
]

# ====== 3. 调用模型 ======
response = Generation.call(
    api_key=DASHSCOPE_API_KEY,
    model="qwen3-max",
    messages=messages,
    result_format="message"
)

# ====== 4. 输出结果 ======
if response.status_code == 200:
    print(response.output.choices[0].message.content)
else:
    print(f"请求失败: {response.code} - {response.message}")
