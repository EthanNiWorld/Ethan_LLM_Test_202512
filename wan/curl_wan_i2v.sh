curl --location 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.5-i2v-preview",
    "input": {
        "prompt": "阿里云新加坡展会颁奖现场。灯光明亮，舞台中央的大屏幕显示阿里云与德勤合作的标志和庆祝画面。一群阿里云员工和德勤客户身着正式服装，神采飞扬地走上舞台领奖，互相握手、拥抱，脸上充满自豪和喜悦。台下观众热烈鼓掌欢呼，镜头扫过人群，大家举起双手庆祝。会场内有五彩气球、花束和横幅装饰，整体氛围热烈、积极、充满团队荣誉感和合作精神，展现阿里云和德勤合作双赢的精彩瞬间。镜头后拉",
        "img_url": "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/delt.png",
        "audio_url": "https://ethan-ai-test.oss-ap-southeast-1.aliyuncs.com/zhouxingchi.mp3"
    },
    "parameters": {
        "resolution": "720P",
        "duration": 10,
        "prompt_extend": true,
        "watermark": true,
        "negative_prompt": "不清晰，模糊",
        "seed": 12345
    }
}'
 # prompt_extend 会自动润色提示词
curl -X GET \
  "https://dashscope-intl.aliyuncs.com/api/v1/tasks/67b15df0-3ffa-455c-a62c-3c87927b895a" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY"


