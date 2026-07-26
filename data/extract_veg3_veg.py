# -*- coding: utf-8 -*-
"""채소·과일 3단계: 채소류 생산량·재배면적 (두 쪽에 걸친 매트릭스)
  p.340 왼쪽: 연도 | 채소류계 근채류계 무 엽채류계 배추  (각 면적,생산)
  p.341 오른쪽: (연도 없음) 노지계 건고추 마늘 양파 (…) 시설  (각 면적,생산)
  ※ 열 매핑은 문자위치 + 부모-자식 값 검증으로 확정(2025-08 작업 기록 참조):
     p.340 pair0=계, pair2=무, pair4=배추 / p.341 pair1=건고추, pair2=마늘, pair3=양파
  두 쪽 모두 23행(1970~2024). 단위: 면적 천ha · 생산 천t.
실행: python3 data/extract_veg3_veg.py
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


# p.340 (연도 있는 왼쪽, 11토큰 = 연도 + 5쌍)
left = []
for ln in page(340).split('\n'):
    if not re.match(r'^\s*\d{2}\s', ln):
        continue
    toks = [t.replace(',', '') for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 11 or not all(re.fullmatch(r'\d+(\.\d+)?', t) for t in toks):
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    left.append((yy(y), [toN(t) for t in toks[1:]]))

# p.341 (연도 없는 오른쪽, 12토큰 = 6쌍)
right = []
for ln in page(341).split('\n'):
    toks = [t.replace(',', '') for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 12 or not all(re.fullmatch(r'\d+(\.\d+)?', t) for t in toks):
        continue
    right.append([toN(t) for t in toks])

assert len(left) == len(right) == 23, "행수 불일치 L=%d R=%d" % (len(left), len(right))

# 품목 → (쪽, 면적idx, 생산idx)
# 왼쪽 vals: [계F,계P, 근채F,근채P, 무F,무P, 엽채F,엽채P, 배추F,배추P]
# 오른쪽 vals:[노지F,노지P, 건고추F,건고추P, 마늘F,마늘P, 양파F,양파P, ?F,?P, 시설F,시설P]
AREA = {"계": ("L", 0), "무": ("L", 4), "배추": ("L", 8),
        "마늘": ("R", 4), "양파": ("R", 6), "건고추": ("R", 2)}
PROD = {"계": ("L", 1), "무": ("L", 5), "배추": ("L", 9),
        "마늘": ("R", 5), "양파": ("R", 7), "건고추": ("R", 3)}
ITEMS = ["무", "배추", "마늘", "양파", "건고추"]


def ser(mp, key):
    side, idx = mp[key]
    return [{"year": y, "value": (lv if side == "L" else right[i])[idx]}
            for i, (y, lv) in enumerate(left)]


TIP_A = ("계는 전국 채소류 전체입니다. 표시된 5개 품목 외 기타가 포함돼 있어 품목 합계보다 큽니다. "
         "고추는 생산량·재배면적에서 **건고추 기준**입니다(소비량은 고추 기준). (p.340~341)")

veg_area = {
    "id": "vegetable_area", "name": "채소류 재배면적", "group": "채소·과일", "unit": "천ha",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "채소류 재배면적. 계 + 품목별(무·배추·마늘·양파·건고추)",
    "keywords": ["채소", "재배면적", "무", "배추", "마늘", "양파", "건고추", "고추"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "농업·농촌 Ⅴ.경제작물 1.채소 (1)",
               "page": 340, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser(AREA, "계"), "series_label": "계(전체)",
    "breakdown": [{"label": nm, "series": ser(AREA, nm)} for nm in ITEMS],
    "related_ids": ["vegetable_production", "vegetable_consumption_pc"], "tip": TIP_A
}

veg_prod_breakdown = [{"label": nm, "series": ser(PROD, nm)} for nm in ITEMS]
veg_prod_check = ser(PROD, "계")

json.dump({"vegetable_area": veg_area,
           "veg_prod_breakdown": veg_prod_breakdown,
           "veg_prod_check": veg_prod_check},
          open('/tmp/veg3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 채소류 재배면적(천ha)/생산량(천t) — 2024 ===")
li = 22
print("계     면적 %s / 생산 %s" % (left[li][1][0], left[li][1][1]))
for nm in ITEMS:
    print("%-4s   면적 %s / 생산 %s" % (nm, ser(AREA, nm)[li]["value"], ser(PROD, nm)[li]["value"]))
