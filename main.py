"""
AI 漫剧生成器
用法：python main.py "生命是一场体验"

依赖：
  CLAUDE_API_KEY   - 必须（生成脚本）
  LEONARDO_API_KEY - 可选（生成图片；不填则用渐变占位图）
"""

import os
import sys
import json
from pathlib import Path

from config import CLAUDE_API_KEY, LEONARDO_API_KEY
from script_generator import generate_script
from image_generator import generate_image, generate_placeholder_image
from panel_renderer import render_panel
from voice_generator import generate_voice
from video_assembler import assemble_video


def safe_dirname(title: str) -> str:
    """将标题转为安全的目录名"""
    return "".join(c for c in title if c.isalnum() or c in " _-")[:20].strip()


def run(title: str):
    print(f"\n{'='*50}")
    print(f"  AI 漫剧生成器  《{title}》")
    print(f"{'='*50}\n")

    # ── 目录准备 ──────────────────────────────────────
    base_dir = Path("output") / safe_dirname(title)
    dirs = {
        "images":   base_dir / "images",
        "rendered": base_dir / "rendered",
        "audio":    base_dir / "audio",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # ── Step 1: 生成脚本 ──────────────────────────────
    print("Step 1  生成脚本")
    if not CLAUDE_API_KEY:
        print("  ⚠️  未设置 CLAUDE_API_KEY，使用内置示例脚本")
        script = _builtin_script(title)
    else:
        script = generate_script(title, CLAUDE_API_KEY)

    script_path = base_dir / "script.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  脚本已保存: {script_path}（{len(script['scenes'])} 个场景）\n")

    # ── Step 2-4: 逐场景处理 ──────────────────────────
    use_placeholder = not LEONARDO_API_KEY
    if use_placeholder:
        print("  ⚠️  未设置 LEONARDO_API_KEY，将使用渐变占位图\n")

    art_style = script.get("art_style", "ink wash manga style, black and white")
    scenes_data = []

    for scene in script["scenes"]:
        sid = scene["id"]
        print(f"Step 2  场景 {sid}/{len(script['scenes'])} — 生成图片")

        img_path = str(dirs["images"] / f"scene_{sid:02d}.jpg")
        full_prompt = f"{scene['image_prompt']}, {art_style}, high quality"

        if use_placeholder:
            generate_placeholder_image(scene["image_prompt"], img_path)
        else:
            generate_image(full_prompt, LEONARDO_API_KEY, img_path)

        print(f"Step 3  场景 {sid} — 渲染字幕")
        rendered_path = str(dirs["rendered"] / f"scene_{sid:02d}_rendered.jpg")
        render_panel(img_path, scene["text"], scene.get("speaker", "narrator"), rendered_path)

        print(f"Step 4  场景 {sid} — 生成配音")
        audio_path = str(dirs["audio"] / f"scene_{sid:02d}.mp3")
        generate_voice(scene["text"], scene.get("speaker", "narrator"), audio_path)

        scenes_data.append({
            **scene,
            "rendered_image_path": rendered_path,
            "audio_path": audio_path,
        })
        print()

    # ── Step 5: 合成视频 ──────────────────────────────
    print("Step 5  合成最终视频")
    output_video = str(base_dir / "final_video.mp4")
    assemble_video(scenes_data, output_video)

    print(f"\n{'='*50}")
    print(f"  完成！")
    print(f"  视频路径: {output_video}")
    print(f"{'='*50}\n")
    return output_video


def _builtin_script(title: str) -> dict:
    """无 Claude API 时使用的内置示例脚本（《生命是一场体验》）"""
    return {
        "title": title,
        "art_style": "ink wash manga style, black and white with subtle gold accents, dramatic cinematic composition",
        "scenes": [
            {
                "id": 1,
                "type": "narration",
                "image_prompt": "vast universe with stars and nebula, a tiny Earth floating in space, ink wash style, dramatic perspective",
                "text": "生命，是宇宙给你的一张单程票。",
                "speaker": "narrator",
                "emotion": "profound"
            },
            {
                "id": 2,
                "type": "narration",
                "image_prompt": "newborn baby opening eyes for the first time, soft light, ink wash painting, close up portrait",
                "text": "你带着好奇降临，",
                "speaker": "narrator",
                "emotion": "gentle"
            },
            {
                "id": 3,
                "type": "narration",
                "image_prompt": "young child running in a field of flowers, sunlight, ink wash manga style, joyful movement",
                "text": "以为世界都是礼物。",
                "speaker": "narrator",
                "emotion": "joy"
            },
            {
                "id": 4,
                "type": "narration",
                "image_prompt": "teenager standing at crossroads at dusk, looking uncertain, ink wash style, silhouette",
                "text": "慢慢地，你开始迷失，",
                "speaker": "narrator",
                "emotion": "confused"
            },
            {
                "id": 5,
                "type": "narration",
                "image_prompt": "person falling down in rain, dramatic lighting, ink wash manga, emotional scene",
                "text": "跌倒，哭泣，再爬起来。",
                "speaker": "narrator",
                "emotion": "struggle"
            },
            {
                "id": 6,
                "type": "narration",
                "image_prompt": "two people holding hands walking on a mountain path, warm light, ink wash style, hope and companionship",
                "text": "你遇见了一些人，",
                "speaker": "narrator",
                "emotion": "warm"
            },
            {
                "id": 7,
                "type": "narration",
                "image_prompt": "person sitting alone by a window watching rain, contemplative mood, ink wash painting, solitude",
                "text": "也目送了一些离去。",
                "speaker": "narrator",
                "emotion": "melancholy"
            },
            {
                "id": 8,
                "type": "narration",
                "image_prompt": "elderly person sitting on mountaintop overlooking vast landscape at sunset, ink wash manga, wisdom and peace",
                "text": "到最后你才明白——",
                "speaker": "narrator",
                "emotion": "wisdom"
            },
            {
                "id": 9,
                "type": "narration",
                "image_prompt": "close up of person smiling with tears in eyes, golden light, ink wash style, acceptance and peace",
                "text": "这一切，都是体验。",
                "speaker": "narrator",
                "emotion": "peace"
            },
            {
                "id": 10,
                "type": "narration",
                "image_prompt": "single human figure walking into a glowing horizon, universe above, ink wash manga, transcendence",
                "text": "而体验本身，就是意义。",
                "speaker": "narrator",
                "emotion": "transcendent"
            },
        ]
    }


if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "生命是一场体验"
    run(title)
