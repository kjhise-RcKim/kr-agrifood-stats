# -*- coding: utf-8 -*-
"""채소·과일 2단계: 과실류 생산량·재배면적 (두 쪽에 걸친 매트릭스)
  p.348 왼쪽: 연도 | 계(면적,생산) 사과(면적,생산) 배(면적,생산)
  p.349 오른쪽: (연도 없음) 포도(면적,생산) 복숭아(면적,생산) 감귤(면적,생산) 기타(면적,생산)
  → 두 쪽 모두 23행(1970~2024)이라 인덱스로 정렬. 단위: 면적 천ha · 생산 천t.
  ※ 단감은 이 표에 없음(소비량 표에만 있음).
실행: python3 data/extract_veg2_fruit.py
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


def toN(t):
    c = t.replace(',', '')
    return float(c) if re.fullmatch(r'\d+\.\d+', c) else (int(c) if re.fullmatch(r'\d+', c) else None)


# ── p.348: 연도 있는 왼쪽 (7토큰: 연도 + 계·사과·배 각 면적,생산) ──
left = []   # (year, [계면적,계생산, 사과면적,사과생산, 배면적,배생산])
for ln in page(348).split('\n'):
    if not re.match(r'^\s*\d{2}\s', ln):
        continue
    toks = [t.replace(',', '') for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 7 or not all(re.fullmatch(r'\d+(\.\d+)?', t) for t in toks):
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    left.append((yy(y), [toN(t) for t in toks[1:]]))

# ── p.349: 연도 없는 오른쪽 (8토큰: 포도·복숭아·감귤·기타 각 면적,생산) ──
right = []
for ln in page(349).split('\n'):
    toks = [t.replace(',', '') for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 8 or not all(re.fullmatch(r'\d+(\.\d+)?', t) for t in toks):
        continue
    right.append([toN(t) for t in toks])

assert len(left) == len(right) == 23, "행수 불일치 L=%d R=%d" % (len(left), len(right))

# 품목 → (쪽, 면적 인덱스, 생산 인덱스)
# 왼쪽 vals: [계F,계P, 사과F,사과P, 배F,배P]  오른쪽 vals: [포도F,포도P, 복숭아F,복숭아P, 감귤F,감귤P, 기타F,기타P]
AREA = {"계": ("L", 0), "사과": ("L", 2), "배": ("L", 4),
        "포도": ("R", 0), "복숭아": ("R", 2), "감귤": ("R", 4)}
PROD = {"계": ("L", 1), "사과": ("L", 3), "배": ("L", 5),
        "포도": ("R", 1), "복숭아": ("R", 3), "감귤": ("R", 5)}
ITEMS = ["사과", "배", "복숭아", "포도", "감귤"]


def ser(mapping, key):
    side, idx = mapping[key]
    out = []
    for i, (y, lv) in enumerate(left):
        v = (lv if side == "L" else right[i])[idx]
        out.append({"year": y, "value": v})
    return out


AREA_TIP = ("계는 전체 과실류입니다. 표시된 5개 품목 외 기타가 포함돼 있어 품목 합계보다 큽니다. "
            "**단감은 원자료의 생산량·재배면적 표에 없어**(소비량 표에만 있음) 여기서는 제외됩니다. (p.348~349)")

fruit_area = {
    "id": "fruit_area", "name": "과실류 재배면적", "group": "채소·과일", "unit": "천ha",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "과실류 재배면적. 계 + 품목별(사과·배·복숭아·포도·감귤)",
    "keywords": ["과일", "과실", "재배면적", "사과", "배", "복숭아", "포도", "감귤"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "농업·농촌 Ⅴ.경제작물 2.과수 (1)",
               "page": 348, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser(AREA, "계"), "series_label": "계(전체)",
    "breakdown": [{"label": nm, "series": ser(AREA, nm)} for nm in ITEMS],
    "related_ids": ["fruit_production", "fruit_consumption_pc"], "tip": AREA_TIP
}

# 기존 fruit_production(계만 있음)에 붙일 breakdown
fruit_prod_breakdown = [{"label": nm, "series": ser(PROD, nm)} for nm in ITEMS]
fruit_prod_series_check = ser(PROD, "계")   # 기존 계와 대조용

json.dump({"fruit_area": fruit_area,
           "fruit_prod_breakdown": fruit_prod_breakdown,
           "fruit_prod_check": fruit_prod_series_check},
          open('/tmp/veg2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 과실류 재배면적(천ha) / 생산량(천t) — 2024 ===")
last = 22
print("계     면적 %s / 생산 %s" % (left[last][1][0], left[last][1][1]))
for nm in ITEMS:
    a = ser(AREA, nm)[last]["value"]; p = ser(PROD, nm)[last]["value"]
    print("%-4s   면적 %s / 생산 %s" % (nm, a, p))
