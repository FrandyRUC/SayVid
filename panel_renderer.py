from PIL import Image, ImageDraw, ImageFont
import os

# macOS 字体候选列表
FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode MS.ttf",
]


def _load_font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.Draw, text: str, font, max_width: int) -> list[str]:
    """按像素宽度对中文文本自动换行"""
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def render_panel(image_path: str, text: str, speaker: str,
                 output_path: str) -> str:
    """
    在图片底部叠加字幕条：
    - 半透明黑色背景
    - 角色名（非旁白时显示，金色）
    - 对话/旁白文本（白色）
    """
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_text = _load_font(40)
    font_name = _load_font(30)

    # 计算字幕区域
    padding = 30
    max_text_width = w - padding * 2
    lines = _wrap_text(draw, text, font_text, max_text_width)
    line_height = 52
    has_name = speaker not in ("narrator", "旁白", "")
    name_height = 40 if has_name else 0
    text_block_h = len(lines) * line_height + name_height + padding * 2

    bar_top = h - text_block_h - 40
    bar_bottom = h - 20

    # 半透明背景条（带圆角效果用矩形模拟）
    draw.rectangle([(20, bar_top), (w - 20, bar_bottom)], fill=(0, 0, 0, 190))

    # 角色名
    y_cursor = bar_top + padding
    if has_name:
        draw.text((padding + 10, y_cursor), speaker,
                  fill=(255, 200, 80, 255), font=font_name)
        y_cursor += name_height

    # 对话文本
    for line in lines:
        draw.text((padding + 10, y_cursor), line,
                  fill=(255, 255, 255, 255), font=font_text)
        y_cursor += line_height

    # 合并图层
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=92)
    return output_path


def create_subtitle_overlay(text: str, speaker: str, output_path: str,
                             width: int = 1080, height: int = 1920) -> str:
    """
    生成透明背景的字幕 PNG，用于叠加在动态视频上。
    和 render_panel 逻辑相同，但底图是全透明的。
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_text = _load_font(40)
    font_name = _load_font(30)

    padding = 30
    max_text_width = width - padding * 2
    lines = _wrap_text(draw, text, font_text, max_text_width)
    line_height = 52
    has_name = speaker not in ("narrator", "旁白", "")
    name_height = 40 if has_name else 0
    text_block_h = len(lines) * line_height + name_height + padding * 2

    bar_top = height - text_block_h - 40
    bar_bottom = height - 20

    draw.rectangle([(20, bar_top), (width - 20, bar_bottom)], fill=(0, 0, 0, 190))

    y_cursor = bar_top + padding
    if has_name:
        draw.text((padding + 10, y_cursor), speaker,
                  fill=(255, 200, 80, 255), font=font_name)
        y_cursor += name_height

    for line in lines:
        draw.text((padding + 10, y_cursor), line,
                  fill=(255, 255, 255, 255), font=font_text)
        y_cursor += line_height

    img.save(output_path, "PNG")
    return output_path
