import anthropic
import json
import re


SYSTEM_PROMPT = """你是一个AI漫剧编剧和分镜师，擅长创作有哲理、有情感深度的短视频漫剧脚本。

输出规则：
- 只输出 JSON，不要有任何其他文字
- 8-10 个场景，每个场景 3-6 秒
- image_prompt 必须是英文，详细描述画面，适合 AI 生图
- text 是中文旁白或对话，简短有力（15字以内为佳）
- speaker: narrator / protagonist / 或角色名

JSON 格式：
{
  "title": "标题",
  "art_style": "ink wash manga style, black and white with subtle warm gold color accents, dramatic cinematic composition, high contrast lighting, manga panel aesthetics",
  "scenes": [
    {
      "id": 1,
      "type": "narration",
      "image_prompt": "English scene description for image generation, detailed, cinematic",
      "text": "中文旁白文字",
      "speaker": "narrator",
      "emotion": "neutral"
    }
  ]
}"""


def generate_script(title: str, api_key: str) -> dict:
    print(f"  调用 Claude API 生成《{title}》脚本...")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"请为《{title}》创作一个感人的漫剧脚本，要有起承转合，情感真实，引发共鸣。"
            }
        ]
    )

    content = message.content[0].text

    # 提取 JSON（防止模型输出多余内容）
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        return json.loads(json_match.group())

    return json.loads(content)
