#复杂文字渲染（如海报、对联）：首选qwen-image-plus、wan2.5-t2i-preview。
#写实场景和摄影风格（通用场景）：可选通义万相模型，如wan2.5-t2i-preview、wan2.2-t2i-flash。
#需要自定义输出图像分辨率：推荐通义万相模型，如wan2.2-t2i-flash，支持 [512, 1440] 像素范围内的任意宽高组合。
#通义千问Qwen-Image仅支持5种固定尺寸：1664*928(16:9)、928*1664(9:16)、1328*1328(1:1)、1472*1140(4:3)、1140*1472(3:4)。

import os
import time
import requests
from datetime import datetime

# === 配置 ===
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY_WAN")
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY_WAN")

BASE_URL = "https://dashscope-intl.aliyuncs.com"
UPLOAD_URL = f"{BASE_URL}/api/v1/uploads"
VIDEO_SYNTHESIS_URL = f"{BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"
TASK_STATUS_URL_TEMPLATE = f"{BASE_URL}/api/v1/tasks/{{task_id}}"

# 本地图片路径（当前目录）
LOCAL_IMAGE_PATH = "generated_image.jpg"
if not os.path.exists(LOCAL_IMAGE_PATH):
    raise FileNotFoundError(f"图片文件不存在: {os.path.abspath(LOCAL_IMAGE_PATH)}")

# 视频提示词（prompt）
PROMPT = (
    "一幅都市奇幻艺术的场景。一个充满动感的涂鸦艺术角色。一个由喷漆所画成的少年，正从一面混凝土墙上活过来。"
    "他一边用极快的语速演唱一首英文rap，一边摆着一个经典的、充满活力的说唱歌手姿势。"
    "场景设定在夜晚一个充满都市感的铁路桥下。灯光来自一盏孤零零的街灯，营造出电影般的氛围，充满高能量和惊人的细节。"
    "视频的音频部分完全由少年的rap构成，没有其他对话或杂音。"
)

# 当前日期（格式 YYYYMMDD）
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_VIDEO_NAME = f"video_{today_str}.mp4"


def upload_image(file_path):
    """上传本地图片到 DashScope，返回临时 img_url"""
    print(f"📤 正在上传图片: {file_path}")
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
        headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}
        response = requests.post(UPLOAD_URL, files=files, headers=headers)

    if response.status_code != 200:
        print(f"❌ 上传失败: {response.status_code}, {response.text}")
        response.raise_for_status()

    result = response.json()
    img_url = result.get("url")
    if not img_url:
        raise RuntimeError("上传成功但未返回 url")
    
    print(f"✅ 图片上传成功，临时 URL: {img_url}")
    return img_url


def submit_i2v_task(img_url):
    """提交图生视频任务"""
    payload = {
        "model": "wan2.5-i2v-preview",
        "input": {
            "prompt": PROMPT,
            "img_url": img_url
        },
        "parameters": {
            "resolution": "480P",
            "prompt_extend": True,
            "duration": 10,
            "audio": True
        }
    }

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }

    print("🎬 正在提交图生视频任务...")
    response = requests.post(VIDEO_SYNTHESIS_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"❌ 提交失败: {response.status_code}")
        print(response.text)
        response.raise_for_status()

    result = response.json()
    task_id = result.get("output", {}).get("task_id")
    request_id = result.get("request_id")
    print(f"✅ 任务已提交 | task_id: {task_id}")
    return task_id


def poll_task_status(task_id, max_retries=120, interval=5):
    """轮询任务状态"""
    url = TASK_STATUS_URL_TEMPLATE.format(task_id=task_id)
    auth_header = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}

    for attempt in range(max_retries):
        print(f"⏳ 轮询第 {attempt + 1} 次...")
        try:
            response = requests.get(url, headers=auth_header)
            if response.status_code == 200:
                data = response.json()
                status = data.get("output", {}).get("task_status")
                print(f"📊 状态: {status}")

                if status == "SUCCEEDED":
                    results = data.get("output", {}).get("results", [])
                    if results and "url" in results[0]:
                        video_url = results[0]["url"]
                        print(f"\n🎉 视频生成成功！\n🔗 URL: {video_url}")
                        return video_url
                elif status in ["FAILED", "CANCELLED"]:
                    print(f"❌ 任务失败: {data}")
                    return None
            else:
                print(f"⚠️ 查询失败: {response.status_code}")

        except Exception as e:
            print(f"⚠️ 异常: {e}")

        time.sleep(interval)

    print("⏰ 超时：任务未完成")
    return None


def download_video(video_url, filename):
    """下载视频"""
    print(f"\n📥 正在下载视频到: {filename}")
    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ 已保存: {os.path.abspath(filename)}")
        else:
            print(f"❌ 下载失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 下载出错: {e}")


def main():
    try:
        # 1. 上传本地图片
        img_url = upload_image(LOCAL_IMAGE_PATH)

        # 2. 提交视频生成任务
        task_id = submit_i2v_task(img_url)

        # 3. 轮询结果
        video_url = poll_task_status(task_id)
        if video_url:
            download_video(video_url, OUTPUT_VIDEO_NAME)
        else:
            print("未能获取视频。")

    except Exception as e:
        print(f"💥 错误: {e}")


if __name__ == "__main__":
    main()
