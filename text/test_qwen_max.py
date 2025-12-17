# text/test_qwen_max.py
from dashscope import Generation
from config import DASHSCOPE_API_KEY

response = Generation.call(
    model="qwen-max",
    api_key=DASHSCOPE_API_KEY,
    prompt="请用一句话介绍通义千问。"
)

print("Qwen-Max 回复：", response.output.text)
