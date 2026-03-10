import asyncio
import edge_tts

# 角色 → 微软 TTS 声线（全部免费，无需 API Key）
VOICE_MAP = {
    "narrator":    "zh-CN-YunxiNeural",      # 成熟男声，适合旁白
    "旁白":         "zh-CN-YunxiNeural",
    "male":        "zh-CN-YunfengNeural",    # 年轻男声
    "female":      "zh-CN-XiaoxiaoNeural",   # 温柔女声
    "child":       "zh-CN-XiaoyiNeural",     # 儿童声
    "old_male":    "zh-CN-YunjianNeural",    # 沧桑男声
    "protagonist": "zh-CN-YunxiNeural",
    # 英文扩展（老外视频用）
    "en_male":     "en-US-AndrewNeural",
    "en_female":   "en-US-JennyNeural",
}

# 旁白语速稍慢，对话正常
RATE_MAP = {
    "narrator": "-10%",
    "旁白":     "-10%",
}


async def _tts(text: str, voice: str, rate: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_voice(text: str, speaker: str, output_path: str) -> str:
    """生成语音文件，返回文件路径"""
    voice = VOICE_MAP.get(speaker, VOICE_MAP["narrator"])
    rate = RATE_MAP.get(speaker, "+0%")

    asyncio.run(_tts(text, voice, rate, output_path))
    return output_path
