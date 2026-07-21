# -*- coding: utf-8 -*-
"""2단계 브리프용 지표 추출 — 세계 곡물 생산 + 국민 영양
  · p.320 주요국 밀 생산량      · p.326 주요국 옥수수 생산량   · p.327 주요국 콩 생산량
  · p.494 1인 1일당 공급에너지   · p.493 1인 1일당 영양공급량(단백질·지방질)
PDF쪽 = 인쇄쪽 + 4.  실행: python3 data/extract_stage2.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def page(printed):
    """인쇄 쪽번호로 해당 페이지 텍스트를 가져온다."""
    p = printed + 4
    out = subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), PDF, '-'],
                         capture_output=True, text=True)
    return out.stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def num(t):
    c = t.replace(',', '').replace('p', '')
    if not re.fullmatch(r'-?\d+(\.\d+)?', c):
        return None
    return float(c) if '.' in c else int(c)


def yearrows(txt, ncol):
    """'연도 값 값 …' 형태의 행을 뽑아 {연도: [값들]} 로 반환. 열 개수가 맞는 행만 채택."""
    rows = {}
    for ln in txt.split('\n'):
        m = re.match(r'^\s*(\d{2})\s+(.+)$', ln)
        if not m:
            continue
        y = int(m.group(1))
        if 25 <= y <= 52:          # 연도로 볼 수 없는 값
            continue
        vals = [None if t in ('-', '–', '－') else num(t) for t in m.group(2).split()]
        if len(vals) != ncol:
            continue
        rows[yy(y)] = vals
    return rows


def mkseries(rows, col):
    return [{"year": y, "value": rows[y][col]} for y in sorted(rows)]


def indicator(iid, name, group, unit, page_no, section, desc, rows, cols, total_col=None, tip=None):
    """cols = [(라벨, 열번호), …]"""
    ind = {
        "id": iid, "name": name, "group": group, "unit": unit,
        "frequency": "연간", "is_headline": False,
        "description": desc, "keywords": [],
        "source": {"publication": "농림축산식품 주요통계 2025", "section": section,
                   "page": page_no, "org": "농림축산식품부",
                   "license": "공공누리 제1유형(출처표시)"},
        "series": mkseries(rows, total_col) if total_col is not None else [],
        "breakdown": [{"label": lab, "series": mkseries(rows, c)} for lab, c in cols],
        "related_ids": []
    }
    if tip:
        ind["tip"] = tip
    return ind


# ── 1) 주요국 곡물 생산량 (FAO통계) ───────────────────────────────
W = yearrows(page(320), 5)    # 캐나다 미국 프랑스 아르헨티나 호주
M = yearrows(page(326), 6)    # 인도 태국 미국 프랑스 아르헨티나 브라질
S = yearrows(page(327), 5)    # 인도 인도네시아 미국 멕시코 아르헨티나

world_wheat = indicator(
    "world_wheat_production", "주요국 밀 생산량", "국제비교", "백만t", 320,
    "농업·농촌 Ⅳ.식량작물 3.맥류 (8)",
    "FAO통계 기준 주요 밀 생산국의 생산량",
    W, [("캐나다", 0), ("미국", 1), ("프랑스", 2), ("아르헨티나", 3), ("호주", 4)],
    tip="FAO 통계 기준입니다. 원문 표에는 한국이 포함돼 있지 않습니다. (p.320)")

world_maize = indicator(
    "world_maize_production", "주요국 옥수수 생산량", "국제비교", "백만t", 326,
    "농업·농촌 Ⅳ.식량작물 4.서류,두류 및 잡곡 (5)",
    "FAO통계 기준 주요 옥수수 생산국의 생산량",
    M, [("인도", 0), ("태국", 1), ("미국", 2), ("프랑스", 3), ("아르헨티나", 4), ("브라질", 5)],
    tip="FAO 통계 기준입니다. 원문 표에는 한국이 포함돼 있지 않습니다. (p.326)")

world_soy = indicator(
    "world_soybean_production", "주요국 콩(대두) 생산량", "국제비교", "백만t", 327,
    "농업·농촌 Ⅳ.식량작물 4.서류,두류 및 잡곡 (6)",
    "FAO통계 기준 주요 콩(대두) 생산국의 생산량",
    S, [("인도", 0), ("인도네시아", 1), ("미국", 2), ("멕시코", 3), ("아르헨티나", 4)],
    tip="FAO 통계 기준입니다. 원문 표에는 한국이 포함돼 있지 않습니다. (p.327)")

# ── 2) 1인 1일당 공급에너지 (p.494) ───────────────────────────────
# 열: 계 곡류 쌀 밀가루 보리 기타 서류 설탕류 두류
E = yearrows(page(494), 9)
energy = indicator(
    "energy_supply_pc", "1인 1일당 공급에너지", "식품산업", "kcal", 494,
    "식품산업 Ⅱ.생산 및 소비 7",
    "국민 한 사람이 하루에 공급받는 열량과 그 공급원. 계 + 공급원별",
    E, [("곡류", 1), ("쌀", 2), ("밀가루", 3), ("보리", 4), ("서류", 6), ("설탕류", 7), ("두류", 8)],
    total_col=0,
    tip="국민 한 사람이 하루에 **공급**받는 열량(kcal)입니다. 실제로 섭취한 양이 아니라 "
        "식품수급표상 공급량 기준입니다.\n곡류 안에 쌀·밀가루·보리·기타가 들어 있어 "
        "합계가 계와 다릅니다. 자료: 2023 식품수급표(한국농촌경제연구원). (p.494)")

# ── 3) 1인 1일당 영양공급량 (p.493) — 전치형(연도가 열) ─────────────
txt493 = page(493)
years493, prot, fat = None, None, None
for ln in txt493.split('\n'):
    toks = ln.split()
    if years493 is None and toks[:1] == ['구분']:
        years493 = [yy(int(t)) for t in toks[1:] if re.fullmatch(r'\d{2}', t)]
        continue
    if years493 is None:
        continue
    lab = ''.join(toks[:1])
    if lab == '단백질' and prot is None:
        prot = [num(t) for t in toks[1:]]
    elif lab == '지방질' and fat is None:
        fat = [num(t) for t in toks[1:]]

assert years493 and prot and fat, "p.493 파싱 실패"
assert len(prot) == len(years493) and len(fat) == len(years493), \
    "p.493 열 개수 불일치 %d/%d/%d" % (len(years493), len(prot), len(fat))

nutrient = {
    "id": "nutrient_supply_pc", "name": "1인 1일당 단백질·지방질 공급량",
    "group": "식품산업", "unit": "g", "frequency": "연간", "is_headline": False,
    "series_label": "단백질",
    "description": "국민 한 사람이 하루에 공급받는 단백질과 지방질의 양",
    "keywords": [],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "식품산업 Ⅱ.생산 및 소비 6", "page": 493,
               "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": [{"year": y, "value": v} for y, v in zip(years493, prot)],
    "breakdown": [{"label": "지방질", "series": [{"year": y, "value": v} for y, v in zip(years493, fat)]}],
    "related_ids": ["energy_supply_pc"],
    "tip": "식품수급표상 **공급량** 기준이며 실제 섭취량이 아닙니다. "
           "2015년부터 식품성분표(제9개정판) 적용으로 성분 기준이 바뀌었습니다. (p.493 주)"
}

NEW = [world_wheat, world_maize, world_soy, energy, nutrient]
json.dump(NEW, open('/tmp/stage2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ── 검증 출력 ────────────────────────────────────────────────
print("=== 추출 결과 ===")
for ind in NEW:
    s = [p for p in ind["series"] if p["value"] is not None]
    print("■ %s (%s) p.%s" % (ind["name"], ind["unit"], ind["source"]["page"]))
    if s:
        print("   계: %d~%d  최신 %s" % (s[0]["year"], s[-1]["year"], s[-1]["value"]))
    for b in ind["breakdown"]:
        v = [p for p in b["series"] if p["value"] is not None]
        print("   · %-8s %2dpt  %d~%d  최신 %s" %
              (b["label"], len(v), v[0]["year"], v[-1]["year"], v[-1]["value"]))
