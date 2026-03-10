import requests
import time
import base64
import hmac
import hashlib
import json as _json

KLING_BASE_URL = "https://api.klingai.com"


def _kling_jwt(access_key: str, secret_key: str) -> str:
    """生成 Kling API 认证 JWT（纯标准库，无需 PyJWT）"""
    now = int(time.time())

    def b64url(data: dict) -> str:
        return base64.urlsafe_b64encode(
            _json.dumps(data, separators=(",", ":")).encode("utf-8")
        ).rstrip(b"=").decode("utf-8")

    header  = b64url({"alg": "HS256", "typ": "JWT"})
    payload = b64url({"iss": access_key, "exp": now + 1800, "nbf": now - 5})
    msg = f"{header}.{payload}"

    sig = base64.urlsafe_b64encode(
        hmac.new(secret_key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).digest()
    ).rstrip(b"=").decode("utf-8")

    return f"{msg}.{sig}"


def animate_image(image_path: str, access_key: str, secret_key: str,
                  output_path: str, prompt: str = "",
                  duration: str = "5", mode: str = "std") -> str:
    """
    用 Kling AI 将本地图片转为动态视频。

    image_path : 本地图片路径（jpg/png）
    duration   : "5" 或 "10" 秒
    mode       : "std"（省积分）或 "pro"（高质量）
    """
    print(f"    Kling 动画生成中...")

    # 图片转 base64
    with open(image_path, "rb") as f:
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

    def _headers():
        return {
            "Authorization": f"Bearer {_kling_jwt(access_key, secret_key)}",
            "Content-Type": "application/json",
        }

    # 提交任务
    resp = requests.post(
        f"{KLING_BASE_URL}/v1/videos/image2video",
        headers=_headers(),
        json={
            "model_name": "kling-v1-5",
            "image": img_b64,
            "prompt": prompt,
            "duration": duration,
            "mode": mode,
            "cfg_scale": 0.5,
        },
        timeout=30,
    )
    resp.raise_for_status()

    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Kling 任务提交失败: {result}")

    task_id = result["data"]["task_id"]
    print(f"    任务ID: {task_id}，等待渲染...")

    # 轮询（最长 5 分钟）
    for _ in range(60):
        time.sleep(5)
        query = requests.get(
            f"{KLING_BASE_URL}/v1/videos/image2video/{task_id}",
            headers=_headers(),
            timeout=15,
        ).json()

        status = query["data"]["task_status"]
        if status == "succeed":
            video_url = query["data"]["task_result"]["videos"][0]["url"]
            break
        elif status == "failed":
            raise RuntimeError(f"Kling 生成失败: {query}")
    else:
        raise TimeoutError("Kling 视频生成超时（5分钟）")

    # 下载视频
    video_data = requests.get(video_url, timeout=60).content
    with open(output_path, "wb") as f:
        f.write(video_data)

    print(f"    动画视频已保存: {output_path}")
    return output_path
