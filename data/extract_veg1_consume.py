# -*- coding: utf-8 -*-
"""채소·과일 1단계: 1인당 연간 소비량
  p.343 채소류 1인당 소비량 (계 무 배추 마늘 양파 고추 기타)
  p.350 과실류 1인당 소비량 (계 사과 배 복숭아 포도 단감 감귤 기타)
PDF쪽 = 인쇄쪽 + 4.  실행: python3 data/extract_veg1_consume.py
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


def num(t):
    c = t.replace(',', '')
    return float(c) if re.fullmatch(r'-?\d+\.\d+', c) else (int(c) if re.fullmatch(r'-?\d+', c) else None)


def rows(printed, ncol):
    """페이지 옆 세로 장식(한글 1글자) 제거 후, 값 개수가 ncol인 연도행만 채택."""
    out = {}
    for ln in page(printed).split('\n'):
        if not re.match(r'^\s*\d{2}\s', ln):
            continue
        toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
        if len(toks) != ncol + 1:
            continue
        y = int(toks[0])
        if 25 <= y <= 52:
            continue
        vals = [num(t) for t in toks[1:]]
        if any(v is None for v in vals):
            continue
        out[yy(y)] = vals
    return out


def series(rowmap, col):
    return [{"year": y, "value": rowmap[y][col]} for y in sorted(rowmap)]


# ── 채소류 소비량: 계 무 배추 마늘 양파 고추 기타 (7열) ──
V = rows(343, 7)
VCOL = ["계", "무", "배추", "마늘", "양파", "고추", "기타"]
assert V, "p.343 파싱 실패"

veg = {
    "id": "vegetable_consumption_pc", "name": "1인당 채소류 소비량",
    "group": "채소·과일", "unit": "kg", "frequency": "연간",
    "is_headline": False, "brief_weight": 1,
    "description": "국민 1인당 연간 채소류 소비량. 계 + 품목별(무·배추·마늘·양파·고추)",
    "keywords": ["채소", "소비량", "무", "배추", "마늘", "양파", "고추"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "농업·농촌 Ⅴ.경제작물 1.채소 (3)",
               "page": 343, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": series(V, 0), "series_label": "계(전체)",
    "breakdown": [{"label": nm, "series": series(V, VCOL.index(nm))}
                  for nm in ["무", "배추", "마늘", "양파", "고추"]],
    "related_ids": ["vegetable_production"],
    "tip": "국민 한 사람이 1년에 먹는 채소류의 무게(kg)입니다. "
           "계는 전체 채소류이고, 표시된 5개 품목 외에 기타가 포함돼 있어 품목 합계보다 큽니다. (p.343)"
}

# ── 과실류 소비량: 계 사과 배 복숭아 포도 단감 감귤 기타 (8열) ──
F = rows(350, 8)
FCOL = ["계", "사과", "배", "복숭아", "포도", "단감", "감귤", "기타"]
assert F, "p.350 파싱 실패"

fruit = {
    "id": "fruit_consumption_pc", "name": "1인당 과실류 소비량",
    "group": "채소·과일", "unit": "kg", "frequency": "연간",
    "is_headline": False, "brief_weight": 1,
    "description": "국민 1인당 연간 과실류 소비량. 계 + 품목별(사과·배·복숭아·포도·단감·감귤)",
    "keywords": ["과일", "과실", "소비량", "사과", "배", "복숭아", "포도", "단감", "감귤"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "농업·농촌 Ⅴ.경제작물 2.과수 (2)",
               "page": 350, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": series(F, 0), "series_label": "계(전체)",
    "breakdown": [{"label": nm, "series": series(F, FCOL.index(nm))}
                  for nm in ["사과", "배", "복숭아", "포도", "단감", "감귤"]],
    "related_ids": ["fruit_production"],
    "tip": "국민 한 사람이 1년에 먹는 과실류의 무게(kg)입니다. "
           "계는 전체 과실류이고, 표시된 6개 품목 외에 기타가 포함돼 있어 품목 합계보다 큽니다. (p.350)"
}

json.dump([veg, fruit], open('/tmp/veg1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 1인당 소비량 (kg) ===")
for ind in [veg, fruit]:
    s = [p for p in ind["series"] if p["value"] is not None]
    print("■ %s  계 %d~%d 최신 %s" % (ind["name"], s[0]["year"], s[-1]["year"], s[-1]["value"]))
    for b in ind["breakdown"]:
        v = [p for p in b["series"] if p["value"] is not None]
        print("   · %-4s %2dpt %d~%d 최신 %s" % (b["label"], len(v), v[0]["year"], v[-1]["year"], v[-1]["value"]))
