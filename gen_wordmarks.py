#!/usr/bin/env python3
"""
WISET 랜딩 — LEARN 섹션 9개 도구 wordmark 타일 생성 (gpt-image-2 + reference logos).

각 도구별 입력:
  image #1 : 해당 도구의 공식 SVG → PNG 변환본 (브랜드 마크 보존)
  image #2 : 레퍼런스 디자인 캡처 (wordmark 박스 스타일 참고)

출력: assets/logos/wordmark/<name>.png  (1024x1024 정사각형)
"""
import base64
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("[ERROR] OPENAI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

CLIENT = OpenAI(api_key=API_KEY)
MODEL = "gpt-image-2"
OUT_DIR = Path(__file__).resolve().parent / "assets" / "logos" / "wordmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE = Path("/Users/yundaehyeok/Library/Application Support/CleanShot/media/media_SAJVU1PAub/CleanShot 2026-05-02 at 13.34.58.png")
LOGO_DIR = Path("/tmp/wordmark")

TOOLS = [
    {"name": "chatgpt",      "label": "ChatGPT",      "logo": LOGO_DIR / "chatgpt.svg.png"},
    {"name": "gemini",       "label": "Gemini",       "logo": LOGO_DIR / "gemini.svg.png"},
    {"name": "claude",       "label": "Claude",       "logo": LOGO_DIR / "claude-ai.svg.png"},
    {"name": "python",       "label": "Python",       "logo": LOGO_DIR / "python.svg.png"},
    {"name": "pandas",       "label": "pandas",       "logo": LOGO_DIR / "pandas.svg.png"},
    {"name": "jupyter",      "label": "Jupyter",      "logo": LOGO_DIR / "jupyter.svg.png"},
    {"name": "scikit-learn", "label": "scikit-learn", "logo": LOGO_DIR / "scikit-learn.svg.png"},
    {"name": "huggingface",  "label": "Hugging Face", "logo": LOGO_DIR / "hugging-face.svg.png"},
    {"name": "pytorch",      "label": "PyTorch",      "logo": LOGO_DIR / "pytorch.svg.png"},
]

for t in TOOLS:
    if not t["logo"].exists():
        print(f"[ERROR] missing logo: {t['logo']}", file=sys.stderr)
        sys.exit(1)
if not REFERENCE.exists():
    print(f"[ERROR] missing reference: {REFERENCE}", file=sys.stderr)
    sys.exit(1)


def build_prompt(label: str) -> str:
    return f"""
Single brand-tile graphic, 1024x1024 square canvas, on a pure WHITE #ffffff background.

Centered on the canvas: a soft white rounded card (radius 60px) about 78% of the canvas with a very subtle drop shadow #00000010. Inside the card, render the brand wordmark — a horizontal layout of:
   [LOGO ICON]   [TEXT "{label}"]

Specifications:
- LOGO ICON = the symbol from reference image #1, preserved EXACTLY (same colors, same proportions, same fill style). Do NOT redraw or restyle it. Size ≈ 360px tall, vertically centered.
- TEXT = the literal string "{label}" in bold modern sans-serif (Inter / Pretendard family), dark charcoal #1f2937, weight 700, size ≈ 130pt, vertically centered next to the icon. Spelling MUST be exactly "{label}".
- Spacing: ~40px gap between icon and text. Generous padding so the wordmark sits visually centered in the card.

Reference image #2 illustrates the desired tile aesthetic (clean white rounded tiles with brand wordmark — for layout reference only, ignore which specific brands appear there).

Style: clean, professional, Korean SaaS landing-page asset. Sharp edges, crisp anti-aliased rendering. No extra text, no watermark, no decorations, no border outline, no description labels. ONLY the icon + the wordmark "{label}".
"""


def generate(tool: dict, max_retries: int = 3) -> bool:
    out = OUT_DIR / f"{tool['name']}.png"
    prompt = build_prompt(tool["label"])
    for attempt in range(max_retries):
        try:
            print(f"[{tool['name']}] attempt {attempt+1}", flush=True)
            t0 = time.time()
            with open(tool["logo"], "rb") as f1, open(REFERENCE, "rb") as f2:
                resp = CLIENT.images.edit(
                    model=MODEL,
                    image=[f1, f2],
                    prompt=prompt,
                    size="1024x1024",
                    quality="high",
                    n=1,
                )
            if not resp.data or not resp.data[0].b64_json:
                print(f"[{tool['name']}] empty", flush=True)
                time.sleep(2 ** attempt)
                continue
            out.write_bytes(base64.b64decode(resp.data[0].b64_json))
            sz = out.stat().st_size
            dt = time.time() - t0
            print(f"[{tool['name']}] OK — {sz:,}B in {dt:.1f}s", flush=True)
            return True
        except Exception as e:
            msg = str(e)[:240]
            print(f"[{tool['name']}] error: {msg}", flush=True)
            lower = msg.lower()
            if any(s in lower for s in ("401", "403", "moderation", "verification", "billing")):
                return False
            time.sleep(min(15 * (2 ** attempt), 60))
    return False


def main():
    print(f"OUT → {OUT_DIR}\n")
    results = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(generate, t): t["name"] for t in TOOLS}
        for f in as_completed(futures):
            results[futures[f]] = f.result()
    print("\n=== SUMMARY ===")
    for name, ok in results.items():
        print(f"  {'OK ' if ok else 'FAIL'} {name}")
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
