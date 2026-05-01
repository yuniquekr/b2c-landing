#!/usr/bin/env python3
"""WISET 랜딩 v5 — Hero marquee용 한국 여성 30~40대 인터뷰 컷 6장."""
import base64, os, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY: print("[ERROR] OPENAI_API_KEY", file=sys.stderr); sys.exit(1)
CLIENT = OpenAI(api_key=API_KEY)
OUT = Path(__file__).resolve().parent / "assets" / "interviews"
OUT.mkdir(parents=True, exist_ok=True)

BASE = (
    "Photorealistic editorial portrait photograph of a Korean woman, "
    "warm and approachable, looking slightly off-camera at an interviewer (3/4 view). "
    "Natural unforced expression, gentle real smile, eye crinkles. "
    "Shoulder-up close-up shot, color photography, premium magazine-quality lighting. "
    "Soft single-source studio lighting from upper-front-right, slight rim light. "
    "Plain off-white seamless paper background (#f5f3ee), shallow depth of field. "
    "Realistic skin texture, no heavy makeup, natural and genuine. "
    "No text, no logos, no watermarks, no blur. Sharp focus on eyes."
)

JOBS = [
    {
        "name": "person-1.png", "size": "1024x1536",
        "prompt": "Korean woman aged 38, short bob haircut just below the chin, thin-rim glasses, "
                  "wearing a soft beige knit sweater, calm and intelligent demeanor. " + BASE,
    },
    {
        "name": "person-2.png", "size": "1024x1536",
        "prompt": "Korean woman aged 34, shoulder-length straight hair, no glasses, "
                  "wearing a crisp white collared blouse, bright optimistic smile. " + BASE,
    },
    {
        "name": "person-3.png", "size": "1024x1536",
        "prompt": "Korean woman aged 41, long straight hair past shoulders, "
                  "wearing a navy silk blouse with simple gold earrings, composed and elegant expression. " + BASE,
    },
    {
        "name": "person-4.png", "size": "1024x1536",
        "prompt": "Korean woman aged 36, hair pulled back into a neat low ponytail, "
                  "wearing a soft gray knit cardigan over a white tee, thoughtful warm smile. " + BASE,
    },
    {
        "name": "person-5.png", "size": "1024x1536",
        "prompt": "Korean woman aged 39, natural soft wave shoulder-length hair, "
                  "wearing a camel-colored wool coat over a cream sweater, sophisticated warm expression. " + BASE,
    },
    {
        "name": "person-6.png", "size": "1024x1536",
        "prompt": "Korean woman aged 33, short pixie haircut, no makeup look, "
                  "wearing a black mock-neck top, confident and friendly smile. " + BASE,
    },
]

def gen(job):
    out = OUT / job["name"]
    for a in range(3):
        try:
            print(f"[{job['name']}] try {a+1}", flush=True); t0 = time.time()
            r = CLIENT.images.generate(model="gpt-image-2", prompt=job["prompt"], size=job["size"], quality="high", output_format="png", n=1)
            if not r.data or not r.data[0].b64_json: time.sleep(2**a); continue
            out.write_bytes(base64.b64decode(r.data[0].b64_json))
            print(f"[{job['name']}] OK {out.stat().st_size:,}B in {time.time()-t0:.1f}s", flush=True); return True
        except Exception as e:
            print(f"[{job['name']}] err: {str(e)[:200]}", flush=True)
            if any(s in str(e).lower() for s in ("401","403","moderation","billing")): return False
            time.sleep(min(15*(2**a), 60))
    return False

def main():
    print(f"OUT → {OUT}\n")
    with ThreadPoolExecutor(max_workers=2) as ex:
        for f in as_completed({ex.submit(gen, j): j["name"] for j in JOBS}):
            pass
    print("\n=== SUMMARY ===")
    for j in JOBS: print(f"  {'OK' if (OUT / j['name']).exists() else 'FAIL'} {j['name']}")

if __name__ == "__main__": main()
