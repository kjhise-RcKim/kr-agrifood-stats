# -*- coding: utf-8 -*-
"""3단계-C: 한일 비교용 일본 통계
  p.535 일본 농산물 자급률(전치형: 연도가 열) → 기존 japan_agri에 품목별 breakdown 추가
  p.534 일본 주요식품 1인당 연간 소비량(연도-행)  → 신규 지표
PDF쪽 = 인쇄쪽 + 4.  실행: python3 data/extract_stage3c.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def page(printed):
    p = printed + 4
    return subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), PDF, '-'],
                          capture_output=True, text=True).stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def isnum(t):
    return bool(re.fullmatch(r'-?\d+(\.\d+)?', t.replace(',', '').replace('p', '')))


def num(t):
    c = t.replace(',', '').replace('p', '')
    return float(c) if '.' in c else int(c)


# ── 1) p.535 일본 농산물 자급률 (전치형) ──────────────────────────
txt = page(535)
years = None
jrows = {}
for ln in txt.split('\n'):
    toks = ln.split()
    if not toks:
        continue
    if years is None:
        if toks[0] == '연도':
            ys = [t for t in toks[1:] if re.fullmatch(r'\d{2}p?', t)]
            if len(ys) >= 5:
                years = [yy(int(t.replace('p', ''))) for t in ys]
        continue
    nums = [t for t in toks if isnum(t)]
    if len(nums) != len(years):
        continue
    # 라벨 = 첫 숫자 앞의 글자들. 페이지 옆 세로 장식 1글자는 버린다.
    first = next(i for i, t in enumerate(toks) if isnum(t))
    labtoks = toks[:first]
    if len(labtoks) > 1:   # 앞에 붙은 1글자 세로 장식('주','요','농','산','물')만 제거
        labtoks = [t for t in labtoks if not re.fullmatch(r'[가-힣]', t)] or labtoks[-1:]
    lab = ''.join(labtoks).strip()
    if not lab:
        continue
    jrows[lab] = [num(t) for t in nums]

JMAP = {"쌀": "쌀", "소맥": "밀(소맥)", "두류": "두류", "채소": "채소", "과실": "과실", "육류": "육류"}
missing = [k for k in JMAP if k not in jrows]
assert not missing, "p.535에서 못 찾은 행: %s / 찾은 행: %s" % (missing, list(jrows))

japan_breakdown = [{"label": JMAP[k],
                    "series": [{"year": y, "value": v} for y, v in zip(years, jrows[k])]}
                   for k in JMAP]

# ── 2) p.534 일본 주요식품 1인당 연간 소비량 (연도-행, 10열) ────────
COLS = ["쌀", "밀", "서류", "두류", "채소", "과실", "육류", "달걀", "유제품", "어패류"]
crows = {}
for ln in page(534).split('\n'):
    m = re.match(r'^\s*(\d{2})\s+(.+)$', ln)
    if not m:
        continue
    y = int(m.group(1))
    if 25 <= y <= 52:
        continue
    toks = [t for t in m.group(2).split() if not re.fullmatch(r'[가-힣․·]+', t)]
    if len(toks) != len(COLS) or not all(isnum(t) for t in toks):
        continue
    crows[yy(y)] = [num(t) for t in toks]

assert crows, "p.534 파싱 실패"

japan_cons = {
    "id": "japan_consumption_pc", "name": "일본 1인당 연간 식품 소비량",
    "group": "국제비교", "unit": "kg", "frequency": "연간",
    "is_headline": False, "brief_weight": 0,
    "description": "일본 국민 1인당 연간 주요식품 소비량. 쌀 라인 + 품목별",
    "keywords": ["일본", "소비량", "쌀", "밀"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "외국 주요통계 Ⅱ.일본 주요통계 13",
               "page": 534, "org": "농림축산식품부",
               "license": "공공누리 제1유형(출처표시)"},
    "series": [{"year": y, "value": crows[y][0]} for y in sorted(crows)],
    "series_label": "쌀",
    "breakdown": [{"label": nm,
                   "series": [{"year": y, "value": crows[y][i]} for y in sorted(crows)]}
                  for i, nm in enumerate(COLS) if nm != "쌀"],
    "related_ids": ["rice_consumption_pc", "japan_agri"],
    "tip": "일본 국민 1인당 **연간** 소비량(kg)입니다. 한국의 「1인당 양곡 소비량」과 조사 주체·기준이 달라 "
           "단순 비교에는 주의가 필요합니다. (p.534)"
}

json.dump({"japan_breakdown": japan_breakdown, "japan_years": years, "japan_cons": japan_cons},
          open('/tmp/stage3c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== p.535 일본 자급률 품목별 ===")
print("연도:", years[0], "~", years[-1], "(%d개 시점)" % len(years))
for b in japan_breakdown:
    v = [p for p in b["series"] if p["value"] is not None]
    print("   · %-8s 최신 %s%%" % (b["label"], v[-1]["value"]))
print("\n=== p.534 일본 1인당 소비량 (kg) ===")
last = max(crows)
print("최신 %d년:" % last, ", ".join("%s %s" % (n, v) for n, v in zip(COLS, crows[last])))
print("포인트 %d개 (%d~%d)" % (len(crows), min(crows), max(crows)))
