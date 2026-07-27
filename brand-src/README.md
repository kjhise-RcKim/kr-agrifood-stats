# 브랜드 에셋 생성 (디자인 리뉴얼 v1)

- `../web/favicon.svg` — 파비콘 마스터(밀 이삭, 골드+그린). 단순형(16px 가독).
- `build_og.py` — OG 이미지(1200×630) 생성. 실제 밀 자급률 시계열 + 검증 KPI.

## 재생성
```bash
pip install cairosvg --break-system-packages
# 파비콘 PNG (16/32/180/192)
python3 -c "import cairosvg;[cairosvg.svg2png(url='../web/favicon.svg',write_to=f'../web/brand/rk-symbol-{s}.png',output_width=s,output_height=s) for s in (16,32,180,192)]"
# OG
python3 build_og.py   # /tmp/og_new.png → ../web/og.png 로 복사
```
한글 렌더에는 Noto Serif/Sans CJK KR 폰트 필요.
포함 수치(2024): 식량자급률 47.9% · 경지면적 1,505천ha · 밀 자급률 15.9%→1.5% · 지표 56.
※ 푸터 서명 심볼(web/brand/rk-symbol.png = RichardKim ㄹㅊㄷㅋ)은 앱 파비콘과 별개로 유지.
