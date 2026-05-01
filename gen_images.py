#!/usr/bin/env python3
"""
WISET AI 랜딩페이지 — Apple 스타일 hero / track stage 이미지 생성
gpt-image-2로 텍스트가 들어가지 않은 추상 무드 이미지를 생성한다.
HTML overlay에서 텍스트는 모두 별도로 얹기 때문에 이미지에는 텍스트 0.

생성물:
  assets/hero-stage.png        — hero 메인 무대 (16:9, 다크→인디고 그라데이션 + 추상 입자)
  assets/track-bio.png         — 트랙 1: 생명/의학/화학 (4:5, 다크→블러쉬)
  assets/track-eng.png         — 트랙 2: IT/전자/기계 (4:5, 다크→시트러스)
  assets/cta-stage.png         — final CTA backdrop (16:9, deep obsidian 추상)
"""
import base64
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]  # claude-projects/
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("[ERROR] OPENAI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

CLIENT = OpenAI(api_key=API_KEY)
MODEL = "gpt-image-2"
OUT_DIR = Path(__file__).resolve().parent / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Apple finish-style: 다크 상단 → 컬러 중간 → 더 진한 컬러 하단 (linear-gradient 184deg)
# 이미지엔 텍스트 절대 X — HTML에서 overlay
COMMON_CONSTRAINTS = (
    "Absolutely no text, no letters, no numbers, no logos, no watermarks. "
    "Pure abstract atmospheric visual. Apple product page style. "
    "Cinematic, museum-grade, premium minimalism. "
    "Soft uniform lighting, no harsh highlights, no glare. "
    "Subtle film grain, ultra clean composition."
)

JOBS = [
    {
        "name": "hero-stage.png",
        "size": "1536x1024",  # 16:9-ish landscape
        "prompt": (
            "Wide cinematic abstract composition for an Apple-style product page hero backdrop. "
            "Smooth seamless gradient from deep midnight navy #1d1d1f at the top, "
            "transitioning through soft sky-cyan #a8d3fb in the upper-mid, "
            "into vivid electric indigo #0012f9 in the lower-mid, "
            "settling into deeper indigo #2535e2 at the bottom. "
            "Suggest the silhouette of an open laptop emerging from light at the center, "
            "but render it as a luminous abstract glow rather than a literal product. "
            "Soft volumetric light beams radiating gently from center. "
            "Faint particle field, like dust in a beam of light. "
            "Polished, high-end, gallery-lit, dramatic but quiet. "
            + COMMON_CONSTRAINTS
        ),
    },
    {
        "name": "track-bio.png",
        "size": "1024x1536",  # 4:5-ish portrait
        "prompt": (
            "Tall vertical abstract composition for an Apple-style product finish backdrop. "
            "Linear gradient at 184 degrees: deep midnight navy #1d1d1f at the top 20%, "
            "transitioning through pale lavender-pink #f3c4f6 around 43%, "
            "into vivid magenta #f500b4 around 76%, "
            "ending with rich orchid #cc29bc at 95%. "
            "Above this gradient, suggest faint molecular structure: "
            "organic flowing glass orbs, biological cell-like luminous shapes, "
            "subtle DNA double-helix curve hinted in soft light. "
            "Render structures as out-of-focus volumetric glow, not literal illustration. "
            "Glossy, smooth, museum lighting. "
            + COMMON_CONSTRAINTS
        ),
    },
    {
        "name": "track-eng.png",
        "size": "1024x1536",
        "prompt": (
            "Tall vertical abstract composition for an Apple-style product finish backdrop. "
            "Linear gradient at 184 degrees: deep midnight navy #1d1d1f at the top, "
            "transitioning through warm yellow-green #dfe74f around 33%, "
            "into vivid leaf green #5e9c2a around 66%, "
            "ending with rich emerald #0a8619 at 95%. "
            "Above this gradient, suggest abstract industrial geometry: "
            "soft circuit board traces hinted as luminous lines, "
            "out-of-focus chip wafer textures, faint hexagonal lattice patterns. "
            "All structures rendered as quiet volumetric glow, no literal illustration. "
            "Polished engineering aesthetic, gallery lighting. "
            + COMMON_CONSTRAINTS
        ),
    },
    {
        "name": "cta-stage.png",
        "size": "1536x1024",
        "prompt": (
            "Wide cinematic abstract composition for a final call-to-action dark stage backdrop. "
            "Predominantly deep obsidian black #000000 with a soft luminous radial glow "
            "at the lower-center, fading from warm white #f5f5f7 through soft graphite #707070 "
            "back into pure black at the edges. "
            "Suggest light pouring through an open doorway in the distance, "
            "but render it as pure abstract glow with no architectural details. "
            "Faint particle dust drifting through the light. "
            "Quiet, contemplative, hopeful, premium. "
            + COMMON_CONSTRAINTS
        ),
    },
]


def generate(job: dict, max_retries: int = 3) -> bool:
    out = OUT_DIR / job["name"]
    for attempt in range(max_retries):
        try:
            print(f"[{job['name']}] attempt {attempt+1} (size={job['size']})", flush=True)
            t0 = time.time()
            resp = CLIENT.images.generate(
                model=MODEL,
                prompt=job["prompt"],
                size=job["size"],
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
            print(f"[{job['name']}] error: {msg[:260]}", flush=True)
            lower = msg.lower()
            if any(s in lower for s in ("401", "403", "moderation", "verification", "billing")):
                print(f"[{job['name']}] hard stop", flush=True)
                return False
            time.sleep(min(15 * (2 ** attempt), 60))
    print(f"[{job['name']}] FAILED", flush=True)
    return False


def main():
    print(f"Output → {OUT_DIR}\n")
    # 동시 2개 (Tier 1 IPM=5 고려)
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
