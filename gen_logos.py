#!/usr/bin/env python3
"""
WISET 랜딩 — LEARN 섹션 도구 로고 아이콘 9종 생성
gpt-image-2로 brand-recognizable flat icon (1024x1024, white bg) 생성.

생성물 → assets/logos/
  chatgpt.png, gemini.png, claude.png
  python.png, pandas.png, jupyter.png
  scikit-learn.png, huggingface.png, pytorch.png
"""
import base64
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]  # claude-projects/
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("[ERROR] OPENAI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

CLIENT = OpenAI(api_key=API_KEY)
MODEL = "gpt-image-2"
OUT_DIR = Path(__file__).resolve().parent / "assets" / "logos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMON = (
    "Centered single icon on a clean pure white #ffffff background. "
    "Flat modern vector-style icon, bold solid colors, crisp edges, no gradient noise. "
    "Generous padding around the mark — icon occupies ~60% of the canvas. "
    "No text, no caption, no labels, no watermark, no border, no shadow. "
    "Square 1:1 composition."
)

JOBS = [
    {
        "name": "chatgpt.png",
        "prompt": (
            "OpenAI ChatGPT brand icon: a hexagonal knot pattern formed by six "
            "interlocking petal-like loops, rendered in solid OpenAI green #10a37f. "
            "Symmetric, geometric, knot-like flower silhouette. " + COMMON
        ),
    },
    {
        "name": "gemini.png",
        "prompt": (
            "Google Gemini brand icon: a four-pointed sparkle / star shape with "
            "elongated concave sides, filled with a smooth diagonal gradient from "
            "Google blue #1c69d4 to violet #9168f7 to coral #d96570. "
            "Symmetric, polished, modern. " + COMMON
        ),
    },
    {
        "name": "claude.png",
        "prompt": (
            "Anthropic Claude brand icon: an eight-pointed radial asterisk / starburst, "
            "all eight rays equal length and slightly tapered, in solid burnt-orange "
            "color #d97757. Symmetric mark, flat fill, no outline. " + COMMON
        ),
    },
    {
        "name": "python.png",
        "prompt": (
            "Python programming language official logo: two interlocking snake "
            "silhouettes facing opposite directions, the upper one in Python blue "
            "#3776ab, the lower one in Python yellow #ffd43b, each with a small white "
            "eye dot. Symmetric, friendly, geometric flat style. " + COMMON
        ),
    },
    {
        "name": "pandas.png",
        "prompt": (
            "Pandas Python library logo: three vertical rounded bars of equal width "
            "side by side. Left bar dark navy #150458, middle bar pink/magenta "
            "#e70488, right bar yellow #ffca00. Bars have slightly different heights "
            "(short, medium, tall). Flat, geometric, minimalist. " + COMMON
        ),
    },
    {
        "name": "jupyter.png",
        "prompt": (
            "Project Jupyter official planet logo: a large open ring (orbit) and three "
            "solid circles arranged like planets, all in Jupyter orange #f37726. "
            "Two larger circles top-left and bottom-right inside the ring, one smaller "
            "circle at lower-left. Geometric, friendly, flat. " + COMMON
        ),
    },
    {
        "name": "scikit-learn.png",
        "prompt": (
            "scikit-learn Python library icon: a large open circle ring in scikit "
            "orange #f7931e, with one small accent circle in scikit blue #3499cd "
            "intersecting near the top of the ring. Flat geometric data-science mark. "
            + COMMON
        ),
    },
    {
        "name": "huggingface.png",
        "prompt": (
            "Hugging Face brand emoji icon: a round yellow #fbbf24 smiley face with "
            "two black oval eyes, a wide curved smile, and two open hand silhouettes "
            "raised next to the cheeks (the 'hugging face' emoji). Solid flat fills. "
            + COMMON
        ),
    },
    {
        "name": "pytorch.png",
        "prompt": (
            "PyTorch deep learning library logo: a stylized flame silhouette with a "
            "small dot near the top, all rendered in PyTorch orange #ee4c2c. "
            "Smooth curves, flat fill, minimal geometric flame mark. " + COMMON
        ),
    },
]


def generate(job: dict, max_retries: int = 3) -> bool:
    out = OUT_DIR / job["name"]
    for attempt in range(max_retries):
        try:
            print(f"[{job['name']}] attempt {attempt+1}", flush=True)
            t0 = time.time()
            resp = CLIENT.images.generate(
                model=MODEL,
                prompt=job["prompt"],
                size="1024x1024",
                quality="high",
                output_format="png",
                n=1,
            )
            if not resp.data or not resp.data[0].b64_json:
                print(f"[{job['name']}] empty response", flush=True)
                time.sleep(2 ** attempt)
                continue
            img_bytes = base64.b64decode(resp.data[0].b64_json)
            out.write_bytes(img_bytes)
            sz = out.stat().st_size
            dt = time.time() - t0
            print(f"[{job['name']}] OK — {sz:,}B in {dt:.1f}s", flush=True)
            return True
        except Exception as e:
            msg = str(e)
            print(f"[{job['name']}] error: {msg[:280]}", flush=True)
            lower = msg.lower()
            if any(s in lower for s in ("401", "403", "moderation", "verification", "billing")):
                print(f"[{job['name']}] hard stop", flush=True)
                return False
            time.sleep(min(15 * (2 ** attempt), 60))
    print(f"[{job['name']}] FAILED", flush=True)
    return False


def main():
    print(f"Output → {OUT_DIR}\n")
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(generate, j): j["name"] for j in JOBS}
        for f in as_completed(futures):
            results[futures[f]] = f.result()
    print("\n=== SUMMARY ===")
    for name, ok in results.items():
        print(f"  {'OK ' if ok else 'FAIL'} {name}")
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
