import os
import subprocess
from pathlib import Path

# moviepy 1.0.3 兼容补丁：Pillow 10+ 移除了 ANTIALIAS
from PIL import Image as _PILImage
if not hasattr(_PILImage, "ANTIALIAS"):
    _PILImage.ANTIALIAS = _PILImage.LANCZOS

from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, ColorClip
)

TARGET_W = 1080
TARGET_H = 1920


def _fit_clip(img_clip: ImageClip) -> ImageClip:
    """将图片裁剪/缩放到目标尺寸 1080x1920"""
    iw, ih = img_clip.size

    # 按高度缩放，保持比例
    scale = TARGET_H / ih
    new_w = int(iw * scale)
    new_h = TARGET_H

    clip = img_clip.resize((new_w, new_h))

    # 横向裁剪到 1080
    if new_w > TARGET_W:
        x_center = new_w / 2
        clip = clip.crop(x1=x_center - TARGET_W / 2,
                         x2=x_center + TARGET_W / 2)
    else:
        # 不够宽则居中放在黑色背景上
        bg = ColorClip((TARGET_W, TARGET_H), color=(0, 0, 0),
                        duration=clip.duration)
        clip = CompositeVideoClip(
            [bg, clip.set_position("center")]
        )

    return clip


def _make_scene_clip(scene: dict) -> ImageClip:
    img_path = scene["rendered_image_path"]
    audio_path = scene["audio_path"]

    base_clip = ImageClip(img_path)

    # 时长以音频为准（确保旁白说完）
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        duration = audio.duration + 0.4   # 结尾留 0.4 秒停顿
        base_clip = base_clip.set_duration(duration).set_audio(audio)
    else:
        duration = float(scene.get("duration", 4))
        base_clip = base_clip.set_duration(duration)

    clip = _fit_clip(base_clip)

    # 淡入淡出
    clip = clip.fadein(0.4).fadeout(0.4)

    return clip


def assemble_video(scenes: list, output_path: str, fps: int = 24) -> str:
    """
    将所有场景合并为最终 MP4 视频

    scenes: list of dicts，每个包含：
      - rendered_image_path: 带字幕的图片
      - audio_path: 语音文件
      - duration: 默认时长（秒）
    """
    print(f"  合成 {len(scenes)} 个场景...")

    clips = []
    for i, scene in enumerate(scenes):
        print(f"    场景 {i+1}/{len(scenes)}")
        try:
            clips.append(_make_scene_clip(scene))
        except Exception as e:
            print(f"    ⚠️  场景 {i+1} 出错，跳过: {e}")

    if not clips:
        raise RuntimeError("没有可用的场景片段")

    final = concatenate_videoclips(clips, method="compose")

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"  导出视频: {output_path}")
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(Path(output_path).parent / "temp_audio.m4a"),
        remove_temp=True,
        logger=None,   # 静默 moviepy 日志
    )

    # 清理 moviepy 对象
    final.close()
    for c in clips:
        c.close()

    print(f"  视频已保存: {output_path}")
    return output_path
