from locust import HttpUser, task, between
import json
from dotenv import load_dotenv
import os

load_dotenv()  # 加载.env中的API_KEY
API_KEY = os.getenv("DASHSCOPE_API_KEY")

class QwenUser(HttpUser):
    wait_time = between(0.1, 0.5)  # 模拟用户请求间隔（可调整）
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    @task
    def qwen_request(self):
        # 构造请求体
        data = {
            "model": "qwen3-max",
            "input": {
                "messages": [{"role": "user", "content": "请简要介绍人工智能的发展历程"}]
            },
            "parameters": {"result_format": "message"}
        }
        # 发送POST请求
        self.client.post(
            url="/api/v1/services/aigc/text-generation/generation",
            headers=self.headers,
            data=json.dumps(data)
        )
