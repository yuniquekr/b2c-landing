#!/usr/bin/env python3
"""
WISET 랜딩 카톡/OG 공유 이미지 생성.
레퍼런스: 시안 그라데이션 + 좌측 큰 타이틀 + 우측 다트 타겟 일러스트 + 좌하단 로고.

생성물:
  assets/og-cover.png  — 1200×630 (카톡/페북/트위터 OG 표준)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
LOGO = Path("/Users/yundaehyeok/Desktop/(주)상상력집단/상상력집단로고/logo.png")
ICON = ASSETS / "og-chip.png"
OUT = ASSETS / "og-cover.png"

W, H = 1200, 630

PRETENDARD = "/Users/yundaehyeok/Library/Fonts/Pretendard-{}.otf"


def load_font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(PRETENDARD.format(weight), size)


def make_bg() -> Image.Image:
    """홈페이지 톤: 순흑 + 좌상단 보라 글로우 + 도트 패턴 (KANT style)"""
    img = Image.new("RGB", (W, H), (0, 0, 0))
    # 좌상단 보라 글로우 (radial)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    # 부드러운 큰 보라 원 — blur로 글로우 효과
    gdraw.ellipse([-200, -200, 600, 600], fill=(91, 33, 182, 110))
    gdraw.ellipse([-100, -100, 480, 480], fill=(124, 58, 237, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.paste(glow, (0, 0), glow)
    # 우하단 시안 글로우 (살짝)
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g2draw = ImageDraw.Draw(glow2)
    g2draw.ellipse([800, 380, 1280, 800], fill=(55, 100, 140, 70))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(140))
    img.paste(glow2, (0, 0), glow2)
    return img


def add_decoration(img: Image.Image) -> None:
    """홈페이지의 KANT 도트 패턴을 OG에도 적용 — 균일한 그리드 도트"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    spacing = 24
    radius = 1
    for y in range(0, H, spacing):
        for x in range(0, W, spacing):
            odraw.ellipse([x - radius, y - radius, x + radius, y + radius],
                          fill=(255, 255, 255, 18))
    img.paste(overlay, (0, 0), overlay)


def paste_icon(img: Image.Image) -> None:
    """우측에 도트패턴 반도체 칩 이미지 (og-chip.png) 배치.
    검정 배경은 OG 다크 BG와 자연 블렌딩 — Screen 블렌드로 픽셀 합성."""
    if not ICON.exists():
        print(f"[WARN] chip image not found: {ICON}")
        return
    icon = Image.open(ICON).convert("RGB")
    # 우측 영역에 안정적으로 배치 (정사각 1024 기반)
    target = 540
    icon = icon.resize((target, target), Image.LANCZOS)
    # Screen blend: 검정은 사라지고 밝은 픽셀만 남음 — 다크 BG와 매끄러운 결합
    x = W - icon.width - 20
    y = (H - icon.height) // 2
    region = img.crop((x, y, x + icon.width, y + icon.height))
    blended = Image.new("RGB", icon.size)
    bp = blended.load()
    rp = region.load()
    ip = icon.load()
    for j in range(icon.height):
        for i in range(icon.width):
            r1, g1, b1 = rp[i, j][:3]
            r2, g2, b2 = ip[i, j][:3]
            # screen: 1 - (1-a)*(1-b)
            bp[i, j] = (
                255 - (255 - r1) * (255 - r2) // 255,
                255 - (255 - g1) * (255 - g2) // 255,
                255 - (255 - b1) * (255 - b2) // 255,
            )
    img.paste(blended, (x, y))


def draw_title(img: Image.Image) -> None:
    """좌측에 제목 + 부제 + 마이크로 카피 (2-line 타이틀)"""
    draw = ImageDraw.Draw(img)

    # 작은 인트로 (타겟 정의) — 라이트 그레이
    intro_font = load_font("SemiBold", 30)
    intro = "이공계 여성을 위한"
    draw.text((68, 70), intro, font=intro_font, fill=(180, 200, 220))

    # 메인 정식 명칭 (Black, 96px, 2줄)
    title_font = load_font("Black", 96)
    line1 = "AI 직무복귀"
    line2 = "부트캠프"

    base_y = 122
    # line 1: 화이트
    draw.text((68, base_y), line1, font=title_font, fill=(255, 255, 255))
    # line 2: 밝은 보라 (다크 BG 가독)
    draw.text((68, base_y + 116), line2, font=title_font, fill=(167, 139, 250))

    # 서브 카피 (lead) — 시안 액센트
    sub_font = load_font("SemiBold", 30)
    sub = "8주 120시간  ·  전액 무료  ·  오프라인 100%"
    draw.text((68, base_y + 250), sub, font=sub_font, fill=(155, 234, 250))


def paste_logo(img: Image.Image) -> None:
    """좌하단에 상상력집단 로고 (작게)"""
    if not LOGO.exists():
        print(f"[WARN] logo not found: {LOGO}")
        return
    logo = Image.open(LOGO).convert("RGBA")
    # 다크 배경에 다크-원본 로고 그대로 → 검정 픽셀만 투명 처리하여
    # 흰색 로고 마크가 OG의 검정 배경 위에 떠 보이게.
    rgba = logo.load()
    w, h = logo.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = rgba[x, y]
            if r < 30 and g < 30 and b < 30:
                rgba[x, y] = (0, 0, 0, 0)
            # 라이트 픽셀은 그대로 흰색으로 유지

    # 리사이즈 — 좌하단에 작게 (96px wide, 정사각)
    target_w = 96
    ratio = target_w / logo.width
    new_h = int(logo.height * ratio)
    logo = logo.resize((target_w, new_h), Image.LANCZOS)

    # 좌하단 패딩 (left 60, bottom 36)
    x = 60
    y = H - logo.height - 36
    img.paste(logo, (x, y), logo)


def main() -> None:
    img = make_bg()
    add_decoration(img)
    paste_icon(img)
    draw_title(img)
    paste_logo(img)
    img.save(OUT, "PNG", optimize=True)
    print(f"OK → {OUT} ({OUT.stat().st_size:,}B)")


if __name__ == "__main__":
    main()
