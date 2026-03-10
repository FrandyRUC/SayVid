# SayVid

AI-powered short video generator that turns a single title into a fully produced vertical video — complete with manga-style images, Chinese narration, and subtitles.

## What it does

Given a title like `"生命是一场体验"`, SayVid will:

1. **Generate a script** — Claude AI writes an 8–10 scene storyboard with narration and image prompts
2. **Generate images** — Leonardo.ai renders each scene in ink wash manga style (fallback: gradient placeholder)
3. **Render subtitles** — Chinese text is overlaid on each image
4. **Generate voiceover** — Microsoft Edge TTS reads each line in natural Chinese speech
5. **Assemble video** — All scenes are combined into a 9:16 vertical MP4 ready for Douyin / Reels / Shorts

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
cp .env.example .env
# Edit .env with your keys

# Run
python main.py "你的标题"
```

Output is saved to `output/<title>/final_video.mp4`.

## API keys

| Key | Required | Purpose |
|-----|----------|---------|
| `CLAUDE_API_KEY` | Yes | Script generation (Claude claude-sonnet-4-6) |
| `LEONARDO_API_KEY` | No | Image generation (falls back to placeholder) |

Create a `.env` file:

```
CLAUDE_API_KEY=your_key_here
LEONARDO_API_KEY=your_key_here
```

## Tech stack

- [Claude API](https://anthropic.com) — script generation
- [Leonardo.ai](https://leonardo.ai) — image generation
- [Edge TTS](https://github.com/rany2/edge-tts) — Chinese text-to-speech
- [MoviePy](https://zulko.github.io/moviepy/) — video assembly
- [Pillow](https://pillow.readthedocs.io) — subtitle rendering
