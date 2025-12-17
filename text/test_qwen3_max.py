# text/test_qwen_max.py
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DASHSCOPE_API_KEY
from dashscope import Generation

# 不要设置 base_http_api_url！使用默认原生接口
response = Generation.call(
    api_key=DASHSCOPE_API_KEY,
    model="qwen3-max",  # 注意：不是 qwen3-max
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    result_format="message"
)

print(response.output.choices[0].message.content)
