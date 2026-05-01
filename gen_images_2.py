#!/usr/bin/env python3
"""
WISET 랜딩 v2 — KANT 흑백 톤 무드 이미지 5장 추가 생성.
gpt-image-2 · quality=high · 텍스트 0 · 흑백 monochrome cinematic.
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
        "name": "benefit-bg-internship.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: a soft-focus close-up of a corporate employee badge / ID lanyard "
            "with a generic silhouette icon, hanging on a black corporate jacket. "
            "Shallow depth of field, lit from above, deep shadows on the right. "
            "Background: blurred office interior with soft bokeh, mostly dark. "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
    {
        "name": "benefit-bg-laptop.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: an open silver laptop computer photographed at an angle, "
            "screen glowing softly with abstract code-like patterns (no readable text). "
            "Sleek aluminum body, modern design. "
            "Background: deep matte black with subtle environmental light. "
            "Lit from a single overhead source casting soft shadows. "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
    {
        "name": "benefit-bg-mentoring.png",
        "size": "1024x1024",
        "prompt": (
            "Square monochromatic black-and-white photograph for a premium education benefit card. "
            "Subject: a hand pointing or gesturing toward an out-of-focus laptop screen "
            "during a mentoring session. The hand is in soft focus from one side. "
            "Background: deep dark matte tones, soft bokeh of an office. "
            "Lit from the laptop screen itself plus one soft side light. "
            "Composition leaves the entire upper-left third empty for text overlay. "
            + COMMON
        ),
    },
    {
        "name": "section-bg-curriculum.png",
        "size": "1536x1024",
        "prompt": (
            "Wide ultra-minimalist monochromatic black-and-white background for a curriculum section. "
            "Subject: an abstract texture suggesting a topographic map or chalk dust on a black blackboard, "
            "with a soft circular glow emerging from the upper-left quadrant. "
            "Predominantly very dark, deep black on the right two-thirds. "
            "Subtle film grain throughout. Premium, contemplative mood. "
            "No specific objects or recognizable shapes — pure abstract atmosphere. "
            + COMMON
        ),
    },
    {
        "name": "section-bg-environment.png",
        "size": "1536x1024",
        "prompt": (
            "Wide cinematic monochromatic black-and-white photograph for an education environment section background. "
            "Subject: out-of-focus interior of a modern classroom or coworking space. "
            "Suggest a few people working at desks with laptops in the distance, "
            "but render them heavily blurred so no faces or details are recognizable. "
            "Strong vignette: pure black on the left half, soft details only on the right edge. "
            "Lit by ambient ceiling lights and laptop screen glow. "
            "Composition reserves the entire left two-thirds for headline text overlay. "
            + COMMON
        ),
    },
]

def generate(job):
    out = OUT / job["name"]
    for attempt in range(3):
        try:
            print(f"[{job['name']}] try {attempt+1} (size={job['size']})", flush=True)
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
