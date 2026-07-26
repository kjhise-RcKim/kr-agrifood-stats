# -*- coding: utf-8 -*-
"""축산 2단계: 육류 축종별 생산량·수입량 (p.378 축산물 수급실적)
열(연도 뒤): 수요0 공급1 생산계2 쇠생산3 돼지생산4 닭생산5 수입계6 쇠수입7 돼지수입8 닭수입9
→ 기존 meat_production(계)에 축종 breakdown 추가 + 신규 meat_import(수입량, 계+축종)
검증: 생산계=쇠+돼지+닭, 수입계=쇠+돼지+닭. 단위 천t.
실행: python3 data/extract_livestock_supply.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def toN(t):
    c = t.replace(',', '')
    return int(c) if re.fullmatch(r'-?\d+', c) else (float(c) if re.fullmatch(r'-?\d+\.\d+', c) else None)


out = subprocess.run(['pdftotext', '-layout', '-f', '382', '-l', '382', PDF, '-'],
                     capture_output=True, text=True).stdout
rows = {}
for ln in out.split('\n'):
    m = re.match(r'^\s*(\d{2})\s', ln)
    if not m:
        continue
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 11:
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    rows[yy(y)] = [toN(t) for t in toks[1:]]

assert rows, "p.378 파싱 실패"
# 검증 (원문이 각 값을 개별 반올림해 합계가 ±1 어긋날 수 있음 → 허용오차 2)
for y, v in rows.items():
    if None not in (v[3], v[4], v[5]):
        assert abs(v[2] - (v[3] + v[4] + v[5])) <= 2, "생산계 불일치 %d" % y
    if None not in (v[7], v[8], v[9]):
        assert abs(v[6] - (v[7] + v[8] + v[9])) <= 2, "수입계 불일치 %d" % y


def ser(idx):
    return [{"year": y, "value": rows[y][idx]} for y in sorted(rows)]


NOTE = "2020년부터 쇠고기·돼지고기 생산량은 축산물등급판정 통계연보 기준으로 바뀌어 이전 연도와 단순 비교에 주의가 필요합니다. (p.378)"

prod_breakdown = [{"label": "쇠고기", "series": ser(3)},
                  {"label": "돼지고기", "series": ser(4)},
                  {"label": "닭고기", "series": ser(5)}]
prod_check = ser(2)

meat_import = {
    "id": "meat_import", "name": "육류 수입량", "group": "축산", "unit": "천t",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "육류 수입량. 계 + 축종별(쇠고기·돼지고기·닭고기)",
    "keywords": ["육류", "수입", "쇠고기", "돼지고기", "닭고기", "수입의존"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "농업·농촌 Ⅵ.축산 2.축산물 수급 및 유통 (1) 축산물 수급실적",
               "page": 378, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser(6), "series_label": "수입 계",
    "breakdown": [{"label": "쇠고기", "series": ser(7)},
                  {"label": "돼지고기", "series": ser(8)},
                  {"label": "닭고기", "series": ser(9)}],
    "related_ids": ["meat_production", "livestock_self_suff", "meat_consumption_pc"],
    "tip": "육류 수입량(천t)입니다. 계 = 쇠고기 + 돼지고기 + 닭고기. "
           "「축산물(육류) 생산량」과 나란히 보면 축종별 수입 의존 정도를 알 수 있습니다. (p.378)"
}

json.dump({"prod_breakdown": prod_breakdown, "prod_check": prod_check, "meat_import": meat_import},
          open('/tmp/lsupply.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 육류 축종별 생산량 / 수입량 (천t) — 2024 ===")
last = max(rows)
v = rows[last]
print("생산: 계 %s = 쇠 %s + 돼지 %s + 닭 %s" % (v[2], v[3], v[4], v[5]))
print("수입: 계 %s = 쇠 %s + 돼지 %s + 닭 %s" % (v[6], v[7], v[8], v[9]))
print("→ 쇠고기: 생산 %s < 수입 %s (수입 우위) / 돼지: 생산 %s > 수입 %s" % (v[3], v[7], v[4], v[8]))
