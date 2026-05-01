#!/usr/bin/env python3
"""
WISET hero — Veo 3로 흑백 무드 시네마틱 8초 영상 1장 생성.
모델: veo-3.0-generate-001 · 16:9 · 텍스트 0.

생성 시간: 3~6분 (long-running operation, polling).
출력: assets/hero-video.mp4
"""
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("[ERROR] GEMINI_API_KEY/GOOGLE_API_KEY not set", file=sys.stderr)
    sys.exit(1)

OUT_DIR = Path(__file__).resolve().parent / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "hero-video.mp4"

# Hero 무드: AI / 뉴럴 네트워크 / 데이터 플로우 시네마틱
PROMPT = (
    "Cinematic 8-second high-end AI technology video for a tech education website hero background. "
    "A 3D neural network visualization: glowing nodes connected by thin luminous lines "
    "forming an organic network structure floating in deep dark space. "
    "Subtle pulses of light travel along the connection lines from node to node, "
    "suggesting data flowing through an artificial neural network. "
    "Color palette: deep midnight purple #2D1B69 background, "
    "with violet #8b5cf6 and bright lavender #a78bfa luminous accents on the nodes and signal lines. "
    "Soft particle field drifting through the scene like digital dust. "
    "Very slow camera drift forward and slight rotation, dreamlike, hypnotic. "
    "Premium cinematic quality, depth of field, volumetric atmospheric haze, "
    "evoking artificial intelligence, machine learning, computational thinking. "
    "No people, no faces, no readable text, no logos, no UI elements, no diagrams with labels. "
    "Pure abstract AI visualization. Hypnotic, premium, futuristic, sophisticated."
)

NEGATIVE = "text, letters, numbers, words, captions, subtitles, logos, faces, people, hands, UI screens, code, charts, graphs"


def main():
    print(f"Initializing Veo 3 client...", flush=True)
    client = genai.Client(api_key=API_KEY)

    print(f"Submitting Veo 3 generation request...", flush=True)
    print(f"  Model: veo-3.0-generate-001", flush=True)
    print(f"  Aspect: 16:9, Duration: 8s", flush=True)
    t0 = time.time()

    operation = client.models.generate_videos(
        model="veo-3.0-generate-001",
        prompt=PROMPT,
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
            negative_prompt=NEGATIVE,
        ),
    )

    print(f"Operation submitted: {operation.name}", flush=True)
    print(f"Polling (every 20s)...", flush=True)

    poll_count = 0
    while not operation.done:
        time.sleep(20)
        poll_count += 1
        operation = client.operations.get(operation)
        elapsed = time.time() - t0
        print(f"  [{poll_count:02d}] elapsed={elapsed:.0f}s, done={operation.done}", flush=True)
        if poll_count > 30:  # 10 min timeout safety
            print("[ERROR] Timeout after 10 min", file=sys.stderr)
            sys.exit(1)

    if hasattr(operation, "error") and operation.error:
        print(f"[ERROR] Operation failed: {operation.error}", file=sys.stderr)
        sys.exit(1)

    response = operation.response
    if not response or not response.generated_videos:
        print(f"[ERROR] No videos in response: {response}", file=sys.stderr)
        sys.exit(1)

    video = response.generated_videos[0]
    print(f"Downloading video...", flush=True)
    client.files.download(file=video.video)
    video.video.save(str(OUT))

    sz = OUT.stat().st_size
    total = time.time() - t0
    print(f"\n=== DONE ===", flush=True)
    print(f"  File: {OUT}", flush=True)
    print(f"  Size: {sz:,}B", flush=True)
    print(f"  Total time: {total:.0f}s", flush=True)


if __name__ == "__main__":
    main()
