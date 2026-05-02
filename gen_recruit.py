#!/usr/bin/env python3
"""
WISET 랜딩 — 'IT 대기업 채용 트렌드' 섹션 카드 이미지 생성 (gpt-image-2 + reference logos).

위 박스: Claude Code 로고 + 자격요건 / 우대사항
아래 박스: Cursor 로고 + 필수 역량 / 우대 역량
출력: assets/recruit-cards.png (1536x1024, 가로형 — 한 화면에 들어오는 컴팩트 사이즈)

reference 로고:
  CLAUDE_LOGO = /Users/yundaehyeok/Downloads/다운로드 (2).png  (적갈색 픽셀 마스코트)
  CURSOR_LOGO = /tmp/brand-logo-7.svg.png                     (검정 둥근사각 + 회색 큐브)
"""
import base64
import os
import sys
import time
from pathlib import Path

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
OUT = Path(__file__).resolve().parent / "assets" / "recruit-cards.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

CLAUDE_LOGO = Path("/Users/yundaehyeok/Downloads/다운로드 (2).png")
CURSOR_LOGO = Path("/tmp/brand-logo-7.svg.png")
for p in (CLAUDE_LOGO, CURSOR_LOGO):
    if not p.exists():
        print(f"[ERROR] missing reference logo: {p}", file=sys.stderr)
        sys.exit(1)

PROMPT = """
Korean recruiting-page infographic, 1536x1024 horizontal landscape, on a pure white #ffffff outer background.

Compose TWO horizontally wide cards stacked vertically with a 32px gap between them. Each card fills the full canvas width, has a SOLID CYAN BACKGROUND #21B5C9 (saturated turquoise — must be cyan, NOT white), rounded corners radius 18px, internal padding 40px.

== TOP CARD (Claude Code) ==
Reference image #1 (the orange-red 8-bit pixel mascot character) MUST be used as the brand mark.
- Left zone (~38% width): place the pixel mascot icon at ~140px size, vertically centered, with the wordmark "Claude Code" beside it in BOLD WHITE sans-serif (~52pt). Pixel mascot stays exactly as in reference (small chunky orange-red pixel creature with two short legs).
- Right zone (~58% width): TWO overlapping WHITE rounded-rectangle cards (radius 10px, soft drop shadow). Front card offset down-right from back card by ~24px.
  Back card text:
    자격요건                                       (bold dark-gray #1f2937, 18pt)
    • Cursor, Claude Code, Replit, MCP, Make, n8n 등 최신 AI 개발 툴을 활용한 개발 자동화·워크플로우 구축
    • 내부 개발 파이프라인 자동화 (CI/CD, API 통합, AI Agent 설계)
    • AI 코딩 도구 및 Workflow Automation 툴 검증 경험
  Front card text (the 2nd bullet has a CYAN highlight band #21B5C9 behind it):
    우대사항                                       (bold dark-gray, 18pt)
    • GitHub Actions 기반 CI/CD 구성 및 운영 경험
    • AI 기반 개발 도구(Cursor, Claude Code, MCP 등) 실무 사용 경험   ← cyan highlight band
    • REST API / Webhook / JSON 기반 시스템 연동 이해

== BOTTOM CARD (Cursor) ==
Reference image #2 (a black rounded-square containing a pale-gray isometric cube) MUST be used as the brand mark.
- Left zone (~38% width): place that black-rounded-square-with-cube icon at ~140px size, vertically centered, with the wordmark "Cursor" beside it in BOLD WHITE sans-serif (~52pt).
- Right zone (~58% width): TWO overlapping WHITE rounded-rectangle cards same style as top card.
  Back card text:
    필수 역량                                      (bold dark-gray, 18pt)
    • Cursor, Claude Code 등 코딩 에이전트를 개발 사이클 전반에 자연스럽게 사용하는 분
    • AI 도구를 활용해 서비스 구조나 운영 방식을 개선하며 비즈니스 임팩트를 만들어본 경험
    • 문제 정의부터 구현·배포까지 End-to-End 주도 경험
  Front card text (1st bullet has CYAN highlight band):
    우대 역량                                      (bold dark-gray, 18pt)
    • 프롬프트 설계, RAG 등 LLM 응용 워크플로우 자동화 구축 경험   ← cyan highlight band
    • Cafe24 자사몰 구축/리뉴얼 및 SPA·AWS 클라우드 운영 경험
    • Figma 시안을 디자인 시스템과 MCP로 구현해본 경험

CRITICAL:
1. Card backgrounds must be solid cyan #21B5C9, fully filled.
2. Use the EXACT reference logos provided (don't redraw them differently).
3. Korean text rendered crisply — every Hangul syllable accurate, no garbled glyphs.
4. Body bullet font ~13pt, line-height 1.6, dark-gray #4b5563.
5. No watermark, no extra captions, no labels other than what's specified.
"""


def generate(max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        try:
            print(f"[recruit-cards] attempt {attempt+1} (images.edit + 2 refs)", flush=True)
            t0 = time.time()
            with open(CLAUDE_LOGO, "rb") as f1, open(CURSOR_LOGO, "rb") as f2:
                resp = CLIENT.images.edit(
                    model=MODEL,
                    image=[f1, f2],
                    prompt=PROMPT,
                    size="1536x1024",
                    quality="high",
                    n=1,
                )
            if not resp.data or not resp.data[0].b64_json:
                print("[recruit-cards] empty response", flush=True)
                time.sleep(2 ** attempt)
                continue
            OUT.write_bytes(base64.b64decode(resp.data[0].b64_json))
            sz = OUT.stat().st_size
            dt = time.time() - t0
            print(f"[recruit-cards] OK — {sz:,}B in {dt:.1f}s → {OUT}", flush=True)
            return True
        except Exception as e:
            msg = str(e)
            print(f"[recruit-cards] error: {msg[:300]}", flush=True)
            lower = msg.lower()
            if any(s in lower for s in ("401", "403", "moderation", "verification", "billing")):
                return False
            time.sleep(min(15 * (2 ** attempt), 60))
    return False


if __name__ == "__main__":
    ok = generate()
    sys.exit(0 if ok else 1)
