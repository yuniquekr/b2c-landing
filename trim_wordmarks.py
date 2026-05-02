#!/usr/bin/env python3
"""
wordmark PNG 후처리:
1) 외곽 흰 배경 누끼 (4 모서리 flood-fill → 알파 0)
2) 투명 border trim
3) 모든 wordmark을 동일 height로 정규화 + 동일 캔버스 중앙 배치
   → 화면에서 9개 wordmark 시각 사이즈 일관
"""
from pathlib import Path
from PIL import Image, ImageDraw

DIR = Path(__file__).resolve().parent / "assets" / "logos" / "wordmark"
TARGETS = ["chatgpt","gemini","claude","python","pandas","jupyter","scikit-learn","huggingface","pytorch"]
THRESH = 25  # 흰색 근사 허용치
CONTENT_H = 480       # wordmark 콘텐츠 통일 높이
CANVAS = (1200, 600)  # 모든 wordmark 동일 캔버스 (2:1)

def process(path: Path):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    for seed in [(0,0), (w-1,0), (0,h-1), (w-1,h-1)]:
        ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=THRESH)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # height 기준으로 동일 scale
    cw, ch = img.size
    scale = CONTENT_H / ch
    nw, nh = int(cw * scale), CONTENT_H
    img = img.resize((nw, nh), Image.LANCZOS)

    # 동일 캔버스 중앙 배치
    canvas = Image.new("RGBA", CANVAS, (0,0,0,0))
    x = (CANVAS[0] - nw) // 2
    y = (CANVAS[1] - nh) // 2
    canvas.paste(img, (x, y), img)
    canvas.save(path, "PNG", optimize=True)
    return canvas.size, (nw, nh)

if __name__ == "__main__":
    for name in TARGETS:
        p = DIR / f"{name}.png"
        if not p.exists():
            print(f"MISS {name}.png"); continue
        canvas_sz, content_sz = process(p)
        print(f"OK   {name}.png → canvas={canvas_sz}, content={content_sz}")
