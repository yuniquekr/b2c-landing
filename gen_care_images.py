#!/usr/bin/env python3
"""
WISET 랜딩 — CARE 섹션 인물 이미지 3종 생성 (gpt-image-2)
AI로 생성된 한국 직장인 무드 사진 — 멘토링 / 포트폴리오 리뷰 / 팀 분위기

생성물 → assets/
  care-mentor.png      — 1:1 영상 멘토링 (책상 위 노트북, 인물 2명 가벼운 분위기)
  care-portfolio.png   — 포트폴리오/이력서 리뷰 (모니터 화면 + 옆 인물)
  care-team.png        — 4인 팀 분위기 친근한 인물샷 (다양성, 연구·실무 톤)
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
OUT_DIR = Path(__file__).resolve().parent / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMON = (
    "Photorealistic, ultra-detailed, sharp focus, magazine-quality editorial photography. "
    "Subjects look approachable and warm. Slight shallow depth of field, cinematic. "
    "Color palette: deep charcoal #14141b base, warm violet ambient highlights "
    "(#8b5cf6 / #7c3aed soft glow), muted indigo shadows. Avoid sky blue, avoid cyan, "
    "avoid any pastel light-blue tint. Lighting feels like a warm dusk in a premium "
    "tech studio. Clean composition with generous negative space. "
    "No watermarks, no captions, no UI labels, no brand logos in the image. "
    "Polished landing-page aesthetic for an AI bootcamp brand using purple as accent."
)

JOBS = [
    {
        "name": "care-mentor.png",
        "size": "1024x1536",
        "prompt": (
            "Composite scene of an online 1:1 mentoring session, viewed as two adjacent "
            "video-call windows occupying the lower half of the image. "
            "Left window: a friendly Korean male tutor in his late 20s wearing a dark "
            "button-up shirt, slight smile, sitting at a desk with a monitor partially "
            "visible behind him, looking towards camera. "
            "Right window: a Korean woman in her early 30s wearing a navy blue knit top, "
            "warm engaged smile, also at a similar desk setup, looking at her own camera. "
            "Behind both video windows, the upper half of the frame shows a softly blurred "
            "open-plan office at dusk, full of rows of desks and dual monitors lit by "
            "warm violet and amber edge lighting against deep charcoal walls. "
            "Subtle dark vignette around the edges. "
            "The two video windows have slim modern frames as if floating over the office. "
            "No visible text or UI labels. "
            + COMMON
        ),
    },
    {
        "name": "care-portfolio.png",
        "size": "1024x1536",
        "prompt": (
            "A modern laptop browser window facing the camera, taking most of the frame, "
            "displaying a clean professional resume / CV mockup with a profile photo in the "
            "top-left of a Korean man in his late 20s wearing a dark suit, surrounded by "
            "abstract grey text-block placeholders representing skills, education, and "
            "experience sections (no readable text). "
            "Overlapping the lower-left corner of the laptop screen: a small rounded "
            "rectangular video-call thumbnail showing a Korean woman in her early 30s with "
            "long dark hair, wearing a light beige top, smiling warmly at her camera, with "
            "a small red round end-call button below her thumbnail. "
            "Background behind the laptop: softly out of focus dark study wall in deep "
            "charcoal #14141b with warm violet rim light from a side lamp, slight vignette. "
            "Clean composition, premium tech-edu marketing photography. No readable text. "
            + COMMON
        ),
    },
    {
        "name": "care-team.png",
        "size": "1024x1536",
        "prompt": (
            "A studio-style group portrait of four young Korean professionals — two men "
            "and two women in their late 20s to early 30s — standing close together in a "
            "slight staggered arrangement, all looking directly at the camera with confident "
            "warm friendly smiles. "
            "Outfits: man on far left wears a black sweater, woman second from left wears a "
            "soft light-blue button-up shirt, woman third from left wears a cream-white "
            "blouse, man on far right wears a light blue dress shirt. All smart-casual, "
            "relaxed but professional posture, arms gently crossed or hands at sides. "
            "Background: very softly blurred upscale modern studio in deep charcoal "
            "#14141b with subtle warm violet rim lighting and a faint amber backlight, "
            "lots of negative space, no bright sky-blue or cyan anywhere. "
            "Even soft key light on faces, gentle warm skin tones, magazine-quality "
            "editorial photography. "
            + COMMON
        ),
    },
]


def generate(job, max_retries=3):
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
