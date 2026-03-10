import requests
import time
import os
from PIL import Image, ImageDraw, ImageFont
import io

LEONARDO_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"


def generate_image(prompt: str, api_key: str, output_path: str,
                   width: int = 832, height: int = 1472) -> str:
    """调用 Leonardo.ai 生成漫画风格图片"""
    print(f"    生成图片: {prompt[:60]}...")

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }

    # 提交生成任务
    resp = requests.post(
        f"{LEONARDO_BASE_URL}/generations",
        headers=headers,
        json={
            "modelId": "aa77f04e-3eec-4034-9c07-d0f619684628",
            "prompt": prompt,
            "negative_prompt": "photo, realistic, 3d render, blurry, low quality",
            "width": width,
            "height": height,
            "num_images": 1,
            "alchemy": False,
            "photoReal": False,
            "expandedDomain": True,
        },
        timeout=30,
    )
    resp.raise_for_status()

    generation_id = resp.json()["sdGenerationJob"]["generationId"]
    print(f"    任务ID: {generation_id}，等待生成...")

    # 轮询结果（最多等 120 秒）
    for _ in range(40):
        time.sleep(3)
        result = requests.get(
            f"{LEONARDO_BASE_URL}/generations/{generation_id}",
            headers=headers,
            timeout=15,
        ).json()

        status = result["generations_by_pk"]["status"]
        if status == "COMPLETE":
            img_info = result["generations_by_pk"]["generated_images"][0]
            image_url = img_info["url"]
            image_id = img_info["id"]
            break
        elif status == "FAILED":
            raise RuntimeError("Leonardo.ai 图片生成失败")
    else:
        raise TimeoutError("图片生成超时")

    # 下载图片
    img_data = requests.get(image_url, timeout=30).content
    with open(output_path, "wb") as f:
        f.write(img_data)

    print(f"    图片已保存: {output_path}")
    return output_path, image_id


def generate_placeholder_image(text: str, output_path: str,
                                width: int = 1080, height: int = 1920) -> str:
    """
    无 API Key 时生成占位图（渐变色 + 文字）
    用于快速测试 pipeline 其余环节
    """
    import random

    # 随机深色渐变背景
    palettes = [
        [(20, 20, 40), (60, 40, 80)],
        [(10, 30, 50), (30, 70, 90)],
        [(40, 20, 20), (80, 40, 40)],
        [(20, 40, 20), (40, 80, 50)],
    ]
    top_color, bottom_color = random.choice(palettes)

    img = Image.new("RGB", (width, height))
    pixels = img.load()

    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)

    # 中心水印文字（提示是占位图）
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
        small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
    except Exception:
        font = ImageFont.load_default()
        small_font = font

    placeholder_text = "[ AI 生图占位 ]"
    bbox = draw.textbbox((0, 0), placeholder_text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, height // 2 - 60),
              placeholder_text, fill=(100, 100, 120), font=font)

    # 场景描述（截断）
    desc = text[:30] + "..." if len(text) > 30 else text
    bbox2 = draw.textbbox((0, 0), desc, font=small_font)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((width - tw2) // 2, height // 2 + 20),
              desc, fill=(80, 80, 100), font=small_font)

    img.save(output_path, "JPEG", quality=90)
    print(f"    占位图已生成: {output_path}")
    return output_path
