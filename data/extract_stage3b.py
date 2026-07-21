# -*- coding: utf-8 -*-
"""3단계-B: 쌀 수급실적 (p.307)
표 구조: 연도 | 이월 | 생산 | 도입 | 계 | 소비 | 수출 | 연말재고 | 자급률   (8개 값)
양곡년도(전년 11.1.~당년 10.31.) 기준. PDF쪽 = 인쇄쪽 + 4.
실행: python3 data/extract_stage3b.py

※ p.306(쌀 매입 및 판매가격)은 원문 머리글의 열 구성이 모호해 제외함.
   (판매원가A·매입가격·판매가격B·결손 4열인데 결손이 B−A와 맞지 않아 열 해석이 불확실)
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')
PRINTED = 307

out = subprocess.run(['pdftotext', '-layout', '-f', str(PRINTED + 4), '-l', str(PRINTED + 4), PDF, '-'],
                     capture_output=True, text=True).stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def num(t):
    c = t.replace(',', '')
    if re.fullmatch(r'-?\d+', c):
        return int(c)
    if re.fullmatch(r'-?\d+\.\d+', c):
        return float(c)
    return None      # '-'(없음), '1(원조)' 같은 주석성 표기는 결측 처리


def clean(toks):
    """페이지 옆 세로 장식글자('농','업','촌' 등)가 행 끝에 붙는 경우가 있어 제거."""
    return [t for t in toks if not re.fullmatch(r'[가-힣․·]+', t)]


rows = {}
for ln in out.split('\n'):
    m = re.match(r'^\s*(\d{2})\s+(.+)$', ln)
    if not m:
        continue
    y = int(m.group(1))
    if 25 <= y <= 52:
        continue
    vals = [num(t) for t in clean(m.group(2).split())]
    if len(vals) != 8:
        continue
    rows[yy(y)] = vals

assert rows, "p.307 파싱 실패"
COL = {"이월": 0, "생산": 1, "도입": 2, "계": 3, "소비": 4, "수출": 5, "연말재고": 6, "자급률": 7}


def ser(col):
    return [{"year": y, "value": rows[y][col]} for y in sorted(rows)]


SRC = {"publication": "농림축산식품 주요통계 2025",
       "section": "농업·농촌 Ⅳ.식량작물 2.미곡 (7) 쌀 수급실적",
       "page": PRINTED, "org": "농림축산식품부",
       "license": "공공누리 제1유형(출처표시)"}

TIPBASE = ("**양곡년도**(전년 11월 1일~당년 10월 31일) 기준입니다. 달력 연도와 다릅니다.\n"
           "공급 = 이월 + 생산 + 도입, 수요 = 소비 + 수출 + 연말재고. (p.307)")

supply = {
    "id": "rice_supply_demand", "name": "쌀 수급실적", "group": "식량·자급률", "unit": "천t",
    "frequency": "연간", "is_headline": False, "brief_weight": 1.5,
    "description": "쌀의 공급(이월·생산·도입)과 수요(소비·수출·연말재고). 계는 총공급량",
    "keywords": ["쌀", "수급", "재고", "소비", "도입", "수입"],
    "source": SRC,
    "series": ser(COL["계"]), "series_label": "총공급 (계)",
    "breakdown": [{"label": nm, "series": ser(COL[nm])}
                  for nm in ["이월", "생산", "도입", "소비", "연말재고"]],
    "related_ids": ["food_crop_production", "rice_consumption_pc", "food_self_suff"],
    "tip": "쌀의 한 해 살림을 보여주는 표입니다. **도입**은 수입량, **이월**은 전년도에서 넘어온 재고입니다.\n" + TIPBASE
}

selfsuff = {
    "id": "rice_self_suff_grainyear", "name": "쌀 자급률(양곡년도)", "group": "식량·자급률", "unit": "%",
    "frequency": "연간", "is_headline": False, "brief_weight": 1.5,
    "description": "쌀 수급실적표에 실린 자급률",
    "keywords": ["쌀", "자급률"],
    "source": SRC, "series": ser(COL["자급률"]), "breakdown": [],
    "related_ids": ["rice_supply_demand", "food_self_suff"],
    "tip": "쌀 수급실적표(p.307)에 실린 자급률로, 식량자급률의 쌀 항목과 같은 값입니다.\n" + TIPBASE
}

NEW = [supply, selfsuff]
json.dump(NEW, open('/tmp/stage3b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 쌀 수급실적 (천t) ===")
last = max(rows)
print("최신 %d년: 이월 %s · 생산 %s · 도입 %s · 계 %s · 소비 %s · 연말재고 %s · 자급률 %s%%" %
      (last, *[format(rows[last][COL[k]], ',') if rows[last][COL[k]] is not None else '-'
               for k in ["이월", "생산", "도입", "계", "소비", "연말재고", "자급률"]]))
for ind in NEW:
    s = [p for p in ind["series"] if p["value"] is not None]
    print("■ %s  계 %d~%d" % (ind["name"], s[0]["year"], s[-1]["year"]))
    for b in ind["breakdown"]:
        v = [p for p in b["series"] if p["value"] is not None]
        print("   · %-5s %2dpt %d~%d 최신 %s" % (b["label"], len(v), v[0]["year"], v[-1]["year"],
                                               format(v[-1]["value"], ',')))
