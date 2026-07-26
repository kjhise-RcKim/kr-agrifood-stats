# -*- coding: utf-8 -*-
"""농가소득 1단계: 원천별 농가소득 (p.152, 단일 페이지 왼쪽)
열: 연도 | 농가소득 농업소득 농업총수입 농업경영비 농외소득 겸업소득 사업외소득 이전소득 비경상소득
→ 계=농가소득, breakdown=농업소득·농외소득·이전소득·비경상소득 (이 4개가 농가소득의 원천)
단위: 천원(농가 평균). '-'는 결측. PDF쪽=인쇄쪽+4.
실행: python3 data/extract_income1_source.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def toN(t):
    c = t.replace(',', '')
    return int(c) if re.fullmatch(r'-?\d+', c) else (float(c) if re.fullmatch(r'-?\d+\.\d+', c) else None)


out = subprocess.run(['pdftotext', '-layout', '-f', '156', '-l', '156', PDF, '-'],
                     capture_output=True, text=True).stdout
rows = {}
for ln in out.split('\n'):
    if not re.match(r'^\s*\d{2}\s', ln):
        continue
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 10:      # 연도 + 9열('-' 포함)
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    rows[yy(y)] = [toN(t) for t in toks[1:]]

assert rows, "p.152 파싱 실패"
# idx: 0농가소득 1농업소득 2농업총수입 3농업경영비 4농외소득 5겸업 6사업외 7이전 8비경상
COL = {"농가소득": 0, "농업소득": 1, "농외소득": 4, "이전소득": 7, "비경상소득": 8}


def ser(col):
    return [{"year": y, "value": rows[y][col]} for y in sorted(rows)]


ind = {
    "id": "farm_income_source", "name": "원천별 농가소득", "group": "농가경제", "unit": "천원",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "농가소득의 원천별 구성. 계(농가소득) + 농업소득·농외소득·이전소득·비경상소득",
    "keywords": ["농가소득", "농업소득", "농외소득", "이전소득", "보조금"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "기본통계 Ⅶ.농가경제 1.원천별 농가소득",
               "page": 152, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser(COL["농가소득"]), "series_label": "농가소득(계)",
    "breakdown": [{"label": nm, "series": ser(COL[nm])}
                  for nm in ["농업소득", "농외소득", "이전소득", "비경상소득"]],
    "related_ids": ["farm_income", "farm_income_by_size", "farm_income_by_type"],
    "tip": "농가 1호당 연간 소득을 **원천별**로 나눈 것입니다(천원). "
           "농가소득 = 농업소득 + 농외소득 + 이전소득 + 비경상소득.\n"
           "**농업소득**은 농사로 번 돈, **농외소득**은 겸업·사업외 수입, "
           "**이전소득**은 보조금·연금 등, **비경상소득**은 경조수입 등입니다. "
           "이전소득·비경상소득은 각각 1985·2005년부터 집계돼 그 이전은 결측입니다. (p.152)"
}

json.dump(ind, open('/tmp/income1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 원천별 농가소득 (천원) — 2024 ===")
last = max(rows)
print("농가소득(계) %s = 농업 %s + 농외 %s + 이전 %s + 비경상 %s" %
      tuple(format(rows[last][COL[k]], ',') for k in ["농가소득", "농업소득", "농외소득", "이전소득", "비경상소득"]))
for b in ind["breakdown"]:
    v = [p for p in b["series"] if p["value"] is not None]
    print("   · %-6s %2dpt %d~%d 최신 %s" % (b["label"], len(v), v[0]["year"], v[-1]["year"], format(v[-1]["value"], ',')))
