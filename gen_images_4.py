#!/usr/bin/env python3
"""WISET 랜딩 v4 — KANT dot-matrix 스타일 산업 이미지 4장."""
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
OUT = Path(__file__).resolve().parent / "assets"

DOT_STYLE = (
    "Rendered as a black-and-white halftone dot-matrix illustration: "
    "the entire image composed of small white dots of varying density on pure black background, "
    "creating the appearance of a halftone print or risograph posterization. "
    "High contrast, organic dot variation, premium editorial quality. "
    "No text, no letters, no logos, no watermarks. "
    "Dramatic single-source lighting from upper-right. "
    "Subject placed in the right two-thirds of the frame, leaving left third darker. "
)

JOBS = [
    {"name": "industry-mobility.png", "size": "1536x1024",
     "prompt": "Wide cinematic photograph of an autonomous vehicle steering wheel and dashboard interior, glowing softly at night. " + DOT_STYLE},
    {"name": "industry-cloud.png", "size": "1536x1024",
     "prompt": "Wide cinematic photograph of a futuristic city skyline at twilight with light trails from highways suggesting data flow. " + DOT_STYLE},
    {"name": "industry-bio.png", "size": "1536x1024",
     "prompt": "Wide cinematic macro photograph of an abstract DNA double helix structure suspended in dark space, glowing softly. " + DOT_STYLE},
    {"name": "industry-manufacturing.png", "size": "1536x1024",
     "prompt": "Wide cinematic photograph of an abstract semiconductor chip surface with circuit traces glowing, deep matte black background. " + DOT_STYLE},
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
    res = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        for f in as_completed({ex.submit(gen, j): j["name"] for j in JOBS}):
            pass
    for j in JOBS: res[j["name"]] = (OUT / j["name"]).exists()
    print("\n=== SUMMARY ==="); [print(f"  {'OK' if v else 'FAIL'} {k}") for k,v in res.items()]

if __name__ == "__main__": main()
