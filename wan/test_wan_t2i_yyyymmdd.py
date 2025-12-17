import os
import time
import requests
from datetime import datetime  # 👈 新增：用于获取当前日期

# 从环境变量读取 API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY_WAN")
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY_WAN")

# API 地址（国际站）
BASE_URL = "https://dashscope-intl.aliyuncs.com"
TEXT2IMAGE_URL = f"{BASE_URL}/api/v1/services/aigc/text2image/image-synthesis"
TASK_STATUS_URL_TEMPLATE = f"{BASE_URL}/api/v1/tasks/{{task_id}}"

# 请求参数
payload = {
    "model": "wan2.5-t2i-preview",
    "input": {
        "prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵"
    },
    "parameters": {
        "size": "1024*1024",  # 注意：官方实际支持 '1024x1024'，但 '*' 可能也兼容
        "n": 1
    }
}

headers = {
    "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable"
}

def submit_text2image_task():
    """提交异步文生图任务，返回 task_id"""
    response = requests.post(TEXT2IMAGE_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"提交失败: {response.status_code}, {response.text}")
        response.raise_for_status()
    
    result = response.json()
    task_id = result.get("output", {}).get("task_id")
    request_id = result.get("request_id")
    print(f"任务已提交，request_id: {request_id}, task_id: {task_id}")
    return task_id

def poll_task_status(task_id, max_retries=60, interval=10):
    """轮询任务状态，直到成功或超时"""
    url = TASK_STATUS_URL_TEMPLATE.format(task_id=task_id)
    auth_header = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}
    
    for attempt in range(max_retries):
        print(f"轮询第 {attempt + 1} 次...")
        response = requests.get(url, headers=auth_header)
        if response.status_code != 200:
            print(f"查询失败: {response.status_code}, {response.text}")
            time.sleep(interval)
            continue

        data = response.json()
        status = data.get("output", {}).get("task_status")
        print(f"当前状态: {status}")

        if status == "SUCCEEDED":
            results = data.get("output", {}).get("results", [])
            if results and "url" in results[0]:
                image_url = results[0]["url"]
                print(f"✅ 图片生成成功！URL: {image_url}")
                return image_url
            else:
                print("⚠️ 任务成功但未返回图片 URL")
                return None

        elif status in ["FAILED", "CANCELLED"]:
            print(f"❌ 任务失败或被取消: {data}")
            return None

        time.sleep(interval)

    print("⏰ 轮询超时，任务仍未完成")
    return None

def download_image(url, filename=None):
    """下载图片到本地，文件名自动加上 yyyymmdd 后缀"""
    if filename is None:
        # 生成带日期的文件名，例如: generated_image_20250405.jpg
        today = datetime.now().strftime("%Y%m%d")
        filename = f"generated_image_{today}.jpg"
    
    print(f"正在下载图片到 {filename} ...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ 图片已保存为 {filename}")
    else:
        print(f"下载失败: {response.status_code}")

def main():
    try:
        task_id = submit_text2image_task()
        if not task_id:
            print("未能获取 task_id")
            return

        image_url = poll_task_status(task_id)
        if image_url:
            download_image(image_url)  # 自动使用带日期的文件名
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
