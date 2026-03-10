import os
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "")

# Leonardo.ai model - DreamShaper XL (好用的通用模型)
LEONARDO_MODEL_ID = "aa77f04e-3eec-4034-9c07-d0f619684628"

# 视频尺寸 (9:16 竖屏，适合抖音/Reels/Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# 图片生成尺寸 (Leonardo.ai 支持的接近 9:16 的尺寸)
IMAGE_WIDTH = 832
IMAGE_HEIGHT = 1472

FPS = 24

# 字幕字体 (macOS)
FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode MS.ttf",
]

# TTS 声线映射
VOICE_MAP = {
    "narrator":    "zh-CN-YunxiNeural",
    "male":        "zh-CN-YunxiNeural",
    "female":      "zh-CN-XiaoxiaoNeural",
    "child":       "zh-CN-XiaoyiNeural",
    "old_male":    "zh-CN-YunjianNeural",
    "protagonist": "zh-CN-YunxiNeural",
}
