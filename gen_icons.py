#!/usr/bin/env python3
"""
WISET 랜딩 — hero-meta + pillars 섹션용 일러스트 아이콘 6종 생성 (gpt-image-2).
flat 3D illustration, 보라(#8b5cf6) 메인 + 시안(#9beafa) 액센트, 다크 배경 카드 위 사용.

생성물 → assets/icon-*.png (1024×1024, transparent)
  icon-target.png    — pillar 1: 직무 적합형 교육 (다트 타겟)
  icon-chart.png     — pillar 2: 현업 ML 프로젝트 (상승 차트)
  icon-mentor.png    — pillar 3: 1:1 취업 컨설팅 (두 사람 대화)
  icon-clock.png     — pillar 4: 10-16시 운영 (시계)
  icon-pin.png       — meta 1: 오프라인 강의장 (지도 핀 + 건물)
  icon-calendar.png  — meta 2: 훈련 시작일 (달력)
"""
import base64
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).resolve().parent
ENV_PATH = HERE.parent / ".env"  # claude-projects/.env
load_dotenv(ENV_PATH)

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print(f"[ERROR] OPENAI_API_KEY not in {ENV_PATH}", file=sys.stderr)
    sys.exit(1)

CLIENT = OpenAI(api_key=API_KEY)
MODEL = "gpt-image-2"
OUT_DIR = HERE / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 일관된 스타일 토큰 — 모든 아이콘이 같은 시각 언어를 갖도록
STYLE = (
    "Modern flat illustration with subtle 3D depth, isometric-ish soft perspective. "
    "Primary color: rich violet purple #8b5cf6. "
    "Accent color: soft mint cyan #9beafa for highlights and inner glow. "
    "Secondary accent: deep indigo #6d28d9 for shadows. "
    "Crisp white #ffffff for inner highlights and rim light. "
    "Clean rounded geometric shapes, slight gradient shading on each surface, "
    "soft drop shadow under the object, no harsh outlines. "
    "Single isolated object centered in frame with generous padding. "
    "Background: a perfectly uniform solid square fill of pure white #ffffff "
    "edge-to-edge with absolutely no gradient, no vignette, no texture, no noise — "
    "the background must be one flat single white tone matching a white UI card. "
    "Drop shadow under the object must be a soft warm light gray (#e5e7ed-ish) "
    "blending naturally into the white background, never dark or saturated. "
    "Designed as a premium UI hero icon for a white card on a landing page. "
    "Absolutely no text, letters, numbers, words, logos, watermarks, or labels of any kind. "
    "Symmetrical balanced composition, premium polished finish, vector-illustration aesthetic."
)

JOBS = [
    {
        "name": "icon-target-light.png",
        "subject": (
            "A stylized dartboard target with concentric rings (purple outer, cyan inner, "
            "white center bullseye), a single sleek dart pinned exactly into the bullseye "
            "at a slight angle. Mint cyan glow halo around the bullseye. "
            "Symbolizes precision and 'right-fit' job placement."
        ),
    },
    {
        "name": "icon-chart-light.png",
        "subject": (
            "A floating glass-like rounded panel showing an upward trending line chart with "
            "4-5 data point dots, the line glowing soft mint cyan, the panel surface in violet "
            "purple gradient. A small cyan AI-circuit dot highlights the peak. "
            "Symbolizes data analysis and ML project completion."
        ),
    },
    {
        "name": "icon-mentor-light.png",
        "subject": (
            "Two friendly stylized human figures from chest up, facing each other in profile, "
            "one purple and one cyan, with a gentle speech-bubble arc connecting them and a "
            "small mint cyan check-mark hovering above. Round soft body shapes, no facial "
            "details. Symbolizes 1:1 mentoring and career consulting."
        ),
    },
    {
        "name": "icon-clock-light.png",
        "subject": (
            "A round wall-clock with a thick violet purple bezel, soft lavender face, mint "
            "cyan hour markers and slim cyan hands pointing to 10 and 4 positions to suggest "
            "a working window. A tiny cyan sparkle at the top. Symbolizes mom-friendly working hours."
        ),
    },
    {
        "name": "icon-pin-light.png",
        "subject": (
            "A glossy violet purple location map-pin with a mint cyan inner circle, planted "
            "on a tiny mint cyan map fragment showing a few rounded streets, with a small "
            "cyan glow ripple beneath. Symbolizes an offline classroom near the subway."
        ),
    },
    {
        "name": "icon-calendar-light.png",
        "subject": (
            "A modern calendar block with a violet purple top header bar (with two tiny cyan "
            "ring binders on top), a clean white face below, a single highlighted mint cyan "
            "circle marking one specific date. No numbers or text on the calendar. "
            "Symbolizes program start date."
        ),
    },
]


def generate(job: dict, max_retries: int = 3) -> bool:
    out = OUT_DIR / job["name"]
    prompt = job["subject"] + " " + STYLE
    for attempt in range(max_retries):
        try:
            print(f"[{job['name']}] attempt {attempt+1}", flush=True)
            t0 = time.time()
            resp = CLIENT.images.generate(
                model=MODEL,
                prompt=prompt,
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
    # IPM=5 고려해 동시 2개
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
