import base64
import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import mimetypes
import dashscope
import requests

# 设置新加坡地域 API 地址
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# 获取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise EnvironmentError("请设置环境变量 DASHSCOPE_API_KEY")

# --- 辅助函数：将网络图片转为 Base64 Data URL ---
def encode_image_url_to_data_url(image_url):
    """从公网 URL 下载图片并转为 data:image/...;base64,... 格式"""
    try:
        print(f"正在下载图片: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        mime_type = response.headers.get('content-type', 'image/png')
        if not mime_type.startswith('image/'):
            raise ValueError("URL 返回的不是图像内容")
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        raise RuntimeError(f"无法处理图片 URL: {e}")

# ==============================
# 使用你的资源
# ==============================
original_img_url = "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/delt.png"
audio_url = "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/zhouxingchi.mp3"

# 【方式三】使用 Base64 编码（推荐，避免服务端无法访问 OSS）
img_url = encode_image_url_to_data_url(original_img_url)

def sample_call_i2v():
    print('please wait...')
    print("API Key (前6位):", api_key[:6] + "****")
    print("正在使用 Base64 编码的图片（前80字符）:", img_url[:80] + "...")
    print("audio_url:", audio_url)

    # 注意：字段名必须是 image_url（不是 img_url）
    rsp = VideoSynthesis.call(
        api_key=api_key,
        model='wan2.5-i2v-preview',
        image_url=img_url,  # ✅ 关键：正确字段名 + Base64 内容
        audio_url=audio_url,
        prompt=(
            "阿里云新加坡展会颁奖现场。灯光明亮，舞台中央的大屏幕显示阿里云与德勤合作的标志和庆祝画面。"
            "一群阿里云员工和德勤客户身着正式服装，神采飞扬地走上舞台领奖，互相握手、拥抱，脸上充满自豪和喜悦。"
            "台下观众热烈鼓掌欢呼，镜头扫过人群，大家举起双手庆祝。会场内有五彩气球、花束和横幅装饰，整体氛围热烈、"
            "积极、充满团队荣誉感和合作精神，展现阿里云和德勤合作双赢的精彩瞬间。"
        ),
        resolution="480P",
        duration=10,
        prompt_extend=True,
        watermark=False,
        negative_prompt="",
        seed=12345
    )

    print("\n响应结果:")
    print(rsp)

    if rsp.status_code == HTTPStatus.OK:
        if rsp.output.task_status == "SUCCEEDED":
            print("\n✅ 视频生成成功！")
            print("video_url:", rsp.output.video_url)
        else:
            print(f"\n❌ 任务失败: {rsp.output.code} - {rsp.output.message}")
    else:
        print('\nFailed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

if __name__ == '__main__':
    sample_call_i2v()
