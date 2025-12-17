# speech/qwen_tts.py
# 用法: python qwen_tts.py "文本" [--voice VOICE] [--lang LANG]

import os
import sys
import argparse

from dotenv import load_dotenv
load_dotenv()

import dashscope
import pyaudio
import time
import base64
import numpy as np

# 设置地域（北京）
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

def play_tts_text(text: str, voice: str = "Cherry", lang: str = "Chinese"):
    """播放 TTS 合成的语音"""
    p = None
    stream = None
    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

        print(f"🔊 合成语音 | 文本: 「{text}」 | 音色: {voice} | 语言: {lang}")
        
        response = dashscope.MultiModalConversation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY_WAN"),
            model="qwen3-tts-flash",
            text=text,
            voice=voice,
            language_type=lang,  # 支持 Chinese / English 等
            stream=True
        )

        for chunk in response:
            if chunk.output is not None:
                audio = chunk.output.audio
                if audio.data is not None:
                    wav_bytes = base64.b64decode(audio.data)
                    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                    stream.write(audio_np.tobytes())
                if chunk.output.finish_reason == "stop":
                    print(f"\n✅ 播放完成 (过期时间: {chunk.output.audio.expires_at})")
                    break

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()

def main():
    parser = argparse.ArgumentParser(
        description="Qwen-TTS 语音合成播放器（支持中英文）",
        epilog="示例: python qwen_tts.py '你好' --voice Cherry --lang Chinese"
    )
    parser.add_argument(
        "text",
        nargs="?",
        default="你好，我是通义千问！",
        help="要合成的文本（默认中文示例）"
    )
    parser.add_argument(
        "--voice",
        default="Cherry",
        choices=["Cherry", "Mia", "Stella", "Li"],  # 可根据官方文档扩展
        help="音色名称（默认: Cherry）"
    )
    parser.add_argument(
        "--lang",
        default="Chinese",
        choices=["Chinese", "English","Portuguese","Japanese"],
        help="语言类型（默认: Chinese）"
    )

    args = parser.parse_args()
    play_tts_text(args.text, args.voice, args.lang)

if __name__ == "__main__":
    print("接收到的参数:", sys.argv)   
    main()
