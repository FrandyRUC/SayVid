"""
动画 Demo — 取场景 1、5、10 做动态视频（Kling AI）
运行：python animate_demo.py

流程：
  1. 重新生成 3 张图片（Leonardo）
  2. 调 Kling AI image2video 生成动态视频片段
  3. 叠加透明字幕 PNG
  4. 混入 TTS 配音
  5. 合成 final_animated_demo.mp4
"""

import os, json
from pathlib import Path
from dotenv import load_dotenv

# Pillow 兼容补丁
from PIL import Image as _PIL
if not hasattr(_PIL, "ANTIALIAS"):
    _PIL.ANTIALIAS = _PIL.LANCZOS

from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips
)
from moviepy.video.fx.all import loop as vfx_loop

from image_generator import generate_image
from animation_generator import animate_image
from panel_renderer import create_subtitle_overlay
from voice_generator import generate_voice

load_dotenv()
LEONARDO_KEY    = os.getenv("LEONARDO_API_KEY")
KLING_ACCESS    = os.getenv("KLING_ACCESS_KEY")
KLING_SECRET    = os.getenv("KLING_SECRET_KEY")

# ── 选取要做动画的场景 ──────────────────────────────────
DEMO_SCENE_IDS = [1, 5, 10]

TARGET_W, TARGET_H = 1080, 1920

# ── 目录 ───────────────────────────────────────────────
BASE_DIR = Path("output/animated_demo")
for d in ["images", "videos", "overlays", "audio"]:
    (BASE_DIR / d).mkdir(parents=True, exist_ok=True)


def fit_video(clip, w=TARGET_W, h=TARGET_H):
    """缩放+裁剪到目标尺寸"""
    scale = h / clip.h
    clip = clip.resize((int(clip.w * scale), h))
    if clip.w > w:
        clip = clip.crop(x_center=clip.w / 2, width=w)
    return clip


def make_animated_clip(video_path, overlay_path, audio_path):
    """动态视频 + 透明字幕叠加 + TTS 配音"""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    duration = audio.duration + 0.4

    # 循环视频以匹配音频时长
    if video.duration < duration:
        video = video.fx(vfx_loop, duration=duration)
    video = video.subclip(0, duration)
    video = fit_video(video)

    # 字幕叠加（透明 PNG）
    subtitle = ImageClip(overlay_path, duration=duration)

    # 合成
    composite = CompositeVideoClip([video, subtitle], size=(TARGET_W, TARGET_H))
    composite = composite.set_audio(audio)
    composite = composite.fadein(0.4).fadeout(0.4)
    return composite


def main():
    # 读取脚本
    script_path = Path("output/生命是一场体验/script.json")
    if not script_path.exists():
        raise FileNotFoundError("请先运行 main.py 生成静态版本的脚本")

    with open(script_path, encoding="utf-8") as f:
        script = json.load(f)

    art_style = script["art_style"]
    scenes = {s["id"]: s for s in script["scenes"]}

    clips = []
    for sid in DEMO_SCENE_IDS:
        scene = scenes[sid]
        print(f"\n{'─'*40}")
        print(f"场景 {sid}: {scene['text']}")

        img_path     = str(BASE_DIR / "images"   / f"scene_{sid:02d}.jpg")
        video_path   = str(BASE_DIR / "videos"   / f"scene_{sid:02d}.mp4")
        overlay_path = str(BASE_DIR / "overlays" / f"scene_{sid:02d}.png")
        audio_path   = str(BASE_DIR / "audio"    / f"scene_{sid:02d}.mp3")

        # Step A: 生成图片
        print(f"  [1/4] 生成图片")
        full_prompt = f"{scene['image_prompt']}, {art_style}, high quality"
        generate_image(full_prompt, LEONARDO_KEY, img_path)

        # Step B: 图片 → 动态视频（Kling AI）
        print(f"  [2/4] 图片转动画（Kling AI）")
        animate_image(img_path, KLING_ACCESS, KLING_SECRET, video_path,
                      prompt=scene["image_prompt"], duration="5", mode="std")

        # Step C: 透明字幕叠加层
        print(f"  [3/4] 生成字幕叠加层")
        create_subtitle_overlay(
            scene["text"], scene.get("speaker", "narrator"),
            overlay_path, TARGET_W, TARGET_H
        )

        # Step D: TTS 配音
        print(f"  [4/4] 生成配音")
        generate_voice(scene["text"], scene.get("speaker", "narrator"), audio_path)

        # 合成这一段
        clip = make_animated_clip(video_path, overlay_path, audio_path)
        clips.append(clip)
        print(f"  场景 {sid} 完成")

    # 拼接所有片段
    print(f"\n合成 {len(clips)} 个动画场景...")
    final = concatenate_videoclips(clips, method="compose")
    out_path = str(BASE_DIR / "final_animated_demo.mp4")
    final.write_videofile(
        out_path, fps=24, codec="libx264", audio_codec="aac",
        temp_audiofile=str(BASE_DIR / "temp_audio.m4a"),
        remove_temp=True, logger=None,
    )
    final.close()
    for c in clips:
        c.close()

    print(f"\n完成！动画视频: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
