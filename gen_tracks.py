#!/usr/bin/env python3
"""
WISET 랜딩 — Track 01 / Track 02 이미지 리디자인 (gpt-image-2)
"3D 아이소메트릭 프롭" → "시네마틱 에디토리얼 매크로 포토그래피".
다크 차콜 + 보라 림 라이트 톤으로 사이트 전체와 통일.

생성물 → assets/
  track-bio.png  — 생명·의학·화학·식품 데이터 (실험실 글래스웨어 매크로)
  track-eng.png  — IT·전자·기계·에너지 데이터 (반도체 웨이퍼/회로 매크로)
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
    "Cinematic macro close-up with extremely shallow depth of field. "
    "Color palette: deep charcoal #14141b base, warm violet rim lighting "
    "(#8b5cf6 / #7c3aed glow on highlights), subtle amber accents. "
    "Avoid sky blue, avoid cyan, avoid pastel light-blue tints, avoid floating 3D icon style. "
    "Premium tech-magazine atmosphere, gallery-grade lighting, slight film grain. "
    "No text, no captions, no UI overlays, no logos, no watermarks. "
    "Vertical portrait 1024x1536 composition with subject filling about 70 percent of frame."
)

JOBS = [
    {
        "name": "track-bio.png",
        "size": "1024x1536",
        "prompt": (
            "A modern bio-chemistry research bench, captured as a cinematic macro shot. "
            "Hero subject: a single tall conical glass flask filled two-thirds with a "
            "translucent violet-tinted liquid, delicate condensation beads visible on the "
            "outside surface, faint vapor curling above the rim. "
            "A second smaller petri dish or glass slide sits softly out of focus to the "
            "side, catching a warm violet rim light. "
            "Background: deep charcoal black laboratory wall, hints of out-of-focus "
            "stainless steel equipment and the soft glow of a monitor at the far edge. "
            "Strong directional violet light from the upper left grazes the glassware, "
            "creating soft caustic reflections on the bench. "
            "Composition: vertical, hero subject slightly left of center, generous dark "
            "negative space around. " + COMMON
        ),
    },
    {
        "name": "track-eng.png",
        "size": "1024x1536",
        "prompt": (
            "A precision semiconductor wafer or modern motherboard close-up, captured as "
            "a cinematic macro photograph. "
            "Hero subject: a single high-end processor chip embedded in a green-black "
            "circuit substrate, fine copper traces fanning outward, surface mount "
            "components catching tiny violet specular highlights. "
            "Slight tilt-shift, depth of field razor-thin so only the chip face is in "
            "perfect focus while the surrounding circuit blurs into bokeh. "
            "Background: deep charcoal black with scattered out-of-focus violet and amber "
            "LED bokeh dots like distant indicator lights in a clean room. "
            "Strong cool violet rim lighting from the right reflects off the metallic "
            "pads, with a soft warm amber glow on the lower-left corner. "
            "Composition: vertical, chip slightly above center, generous dark negative "
            "space above and below. " + COMMON
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
