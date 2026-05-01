# WISET AI 직무 복귀 프로그램 — 랜딩 페이지

이공계 경력 보유 여성을 위한 8주 120시간 AI 직무 복귀 프로그램 랜딩 페이지.

- 주관: WISET (한국여성과학기술인육성재단)
- 운영: (주)상상력집단
- 개강: 2026.06.17 / 50명 한정 / 전액 무료 (복권기금 지원)

## Tech Stack

순수 정적 사이트 — 빌드 도구 없음, 파일 그대로 서빙.

- HTML / CSS / Vanilla JS (단일 파일)
- 폰트: Pretendard + Inter + JetBrains Mono (Google Fonts)
- 이미지: gpt-image-2 생성 (PNG)
- 영상: Veo 3 생성 (MP4, hero 백그라운드)

## 로컬 실행

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## 자산 생성 스크립트

`gen_*.py` 스크립트는 OPENAI / Gemini API 키가 필요합니다.
프로젝트 루트의 `.env` 파일에 다음 키를 설정한 뒤 실행:

```
OPENAI_API_KEY=...
GEMINI_API_KEY=...   # 또는 GOOGLE_API_KEY
```

| 스크립트 | 산출물 |
|---------|--------|
| `gen_images.py` | hero-stage / track-bio / track-eng / cta-stage |
| `gen_images_2.py` | benefit-bg-internship / laptop / mentoring / section-bg-curriculum / environment |
| `gen_images_3.py` | benefit-bg-textbook / ai-tools / dataset |
| `gen_images_4.py` | industry-mobility / cloud / bio / manufacturing |
| `gen_video.py` | hero-video.mp4 (Veo 3, 8s, 16:9) |

## Vercel 배포

자세한 가이드는 본 repo의 PR 설명 또는 `docs/` 참고. 정적 사이트라 Build Command 없이 바로 deploy 가능.

## License

본 페이지의 디자인과 카피는 WISET / (주)상상력집단의 자산입니다.
