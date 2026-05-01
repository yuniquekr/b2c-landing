#!/usr/bin/env python3
"""
WISET 랜딩 v3 — 혜택 카드용 이미지 3장 추가 (AI 도구 / 데이터셋 / 멘토링 대체).
gpt-image-2 · 흑백 monochrome · 텍스트 0.
"""
import base64, os, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("[ERROR] OPENAI_API_KEY not set", file=sys.stderr); sys.exit(1)

CLIENT = OpenAI(api_key=API_KEY)
MODEL = "gpt-image-2"
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

COMMON = (
    "Absolutely no text, no letters, no numbers, no logos, no watermarks. "
    "Pure visual atmosphere. Monochromatic black-and-white grayscale. "
    "Cinematic, premium, museum-grade, gallery lighting. "
    "Soft uniform light. Subtle film grain. "
    "Minimalist composition with significant negative space."
)

JOBS = [
    {
        "name": "benefit-bg-ai-tools.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: an abstract close-up of multiple translucent glass orbs or smooth marble spheres "
            "of varying sizes floating in deep dark space, suggesting AI tools / models / agents. "
            "Each orb glows softly from within with subtle internal light. "
            "Background: deep matte black with very faint particle dust drifting. "
            "Lit from upper-right with soft volumetric beams. "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
    {
        "name": "benefit-bg-dataset.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: an abstract macro close-up of layered translucent glass plates or sheets "
            "stacked at slight angles, suggesting datasets / data layers / research samples. "
            "Soft refraction and reflection on the glass edges, deep shadows between layers. "
            "Background: deep matte black with subtle haze. "
            "Lit from a single soft side light. "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
    {
        "name": "benefit-bg-textbook.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: a soft-focus close-up of an open hardcover notebook or textbook with blank pages, "
            "a fountain pen resting on the page. Premium leather binding suggested in deep shadow. "
            "Background: dark wooden desk surface with soft bokeh of an office. "
            "Lit from above-left with warm window light feel (still grayscale). "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
]

def generate(job):
    out = OUT / job["name"]
    for attempt in range(3):
        try:
            print(f"[{job['name']}] try {attempt+1}", flush=True)
            t0 = time.time()
            resp = CLIENT.images.generate(
                model=MODEL, prompt=job["prompt"], size=job["size"],
                quality="high", output_format="png", n=1,
            )
            if not resp.data or not resp.data[0].b64_json:
                time.sleep(2 ** attempt); continue
            out.write_bytes(base64.b64decode(resp.data[0].b64_json))
            sz = out.stat().st_size
            print(f"[{job['name']}] OK — {sz:,}B in {time.time()-t0:.1f}s", flush=True)
            return True
        except Exception as e:
            msg = str(e); print(f"[{job['name']}] err: {msg[:240]}", flush=True)
            if any(s in msg.lower() for s in ("401","403","moderation","verification","billing")):
                return False
            time.sleep(min(15 * (2 ** attempt), 60))
    return False

def main():
    print(f"Output → {OUT}\n")
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(generate, j): j["name"] for j in JOBS}
        for f in as_completed(futures):
            results[futures[f]] = f.result()
    print("\n=== SUMMARY ===")
    for n, ok in results.items(): print(f"  {'OK ' if ok else 'FAIL'} {n}")
    sys.exit(0 if all(results.values()) else 1)

if __name__ == "__main__":
    main()
