#export DASHSCOPE_API_KEY=sk-c9017aaa29b04df08081705df763d49b
import base64
import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import mimetypes
import dashscope

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
api_key = os.getenv("DASHSCOPE_API_KEY")

# --- 辅助函数：用于 Base64 编码 ---
# 格式为 data:{MIME_type};base64,{base64_data}
def encode_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("不支持或无法识别的图像格式")
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_string}"

"""
图像输入方式说明：
以下提供了三种图片输入方式，三选一即可

1. 使用公网URL - 适合已有公开可访问的图片
2. 使用本地文件 - 适合本地开发测试
3. 使用Base64编码 - 适合私有图片或需要加密传输的场景
"""

# 【方式一】使用公网可访问的图片URL
# 示例：使用一个公开的图片URL
img_url = "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/delt.png?Expires=1763643527&OSSAccessKeyId=TMP.3KqsJmGBFZgCn98UE6srsFC1HMrr14kDzita7g9KwFKZmeLcef6Baug4jTT8C6A2zcUCDsFut1PooetHHdsXKRq9Rhm6Yi&Signature=yHqMxvV%2BWk1O6x0fDzd5V5pXdEY%3D"

# 【方式二】使用本地文件（支持绝对路径和相对路径）
# 格式要求：file:// + 文件路径
# 示例（绝对路径）：
# img_url = "file://" + "/path/to/your/img.png"    # Linux/macOS
# img_url = "file://" + "C:/path/to/your/img.png"  # Windows
# 示例（相对路径）：
# img_url = "file://" + "./img.png"                # 相对当前执行文件的路径

# 【方式三】使用Base64编码的图片
# img_url = encode_file("./img.png")

# 设置音频audio url
audio_url = "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/zhouxingchi.mp3"

def sample_call_i2v():
    # 同步调用，直接返回结果
    print('please wait...')
    print("api_key (前6位):", (api_key or "")[:6], "****")
    print("img_url:", img_url)
    print("audio_url:", audio_url)
    print('please wait Ethan AI 模型生成视频中...')
    rsp = VideoSynthesis.call(api_key=api_key,
                              model='wan2.5-i2v-preview',
                              prompt='阿里云新加坡展会颁奖现场。灯光明亮，舞台中央的大屏幕显示阿里云与德勤合作的标志和庆祝画面。一群阿里云员工和德勤客户身着正式服装，神采飞扬地走上舞台领奖，互相握手、拥抱，脸上充满自豪和喜悦。台下观众热烈鼓掌欢呼，镜头扫过人群，大家举起双手庆祝。会场内有五彩气球、花束和横幅装饰，整体气氛热烈、积极、充满团队荣誉感和合作精神，展现阿里云和德勤合作双赢的精彩瞬间。',
                              img_url=img_url,
                              audio_url=audio_url,
                              resolution="480P",
                              duration=10,
                              # audio=True, # 可选，因为模型默认开启自动配音
                              prompt_extend=True,
                              watermark=False,
                              negative_prompt="",
                              seed=12345)
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print("video_url:", rsp.output.video_url)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


if __name__ == '__main__':
    sample_call_i2v()