# -*- coding: utf-8 -*-
"""축산 1단계: 1인당 축산물 소비량 (p.379)
여러 표가 합쳐진 페이지. 데이터행에 연도 라벨이 없어 p.378의 연도순서로 정렬(둘 다 23행).
열(합계검증 확정): [육류계, 쇠고기, 돼지고기, 닭고기, 자급률, 계란생산, 계란소비, 우유수요, 우유공급, 우유생산, 우유수입, 우유이월, 우유소비]
  ※ 육류계 = 쇠고기+돼지고기+닭고기 로 검증됨.
실행: python3 data/extract_livestock_consume.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def page(printed):
    return subprocess.run(['pdftotext', '-layout', '-f', str(printed + 4), '-l', str(printed + 4), PDF, '-'],
                          capture_output=True, text=True).stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def toN(t):
    c = t.replace(',', '')
    return int(c) if re.fullmatch(r'-?\d+', c) else (float(c) if re.fullmatch(r'-?\d+\.\d+', c) else None)


# 연도 순서 (p.378에서)
YEARS = []
for ln in page(378).split('\n'):
    m = re.match(r'^\s*(\d{2})\s', ln)
    if m:
        y = int(m.group(1))
        if not (25 <= y <= 52):
            YEARS.append(yy(y))

# p.379 데이터행 (연도 없음, 13값)
rows = []
for ln in page(379).split('\n'):
    toks = [t.replace(',', '') for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) >= 12 and sum(1 for t in toks if re.fullmatch(r'-?\d+(\.\d+)?', t)) >= 10:
        rows.append([toN(t) for t in toks])

assert len(rows) == len(YEARS) == 23, "행수 불일치 rows=%d years=%d" % (len(rows), len(YEARS))

# 합계 검증: 육류계 ≈ 쇠+돼지+닭 (최신연도)
c = rows[-1]
assert abs(c[0] - (c[1] + c[2] + c[3])) < 0.5, "합계 검증 실패: %s vs %s" % (c[0], c[1] + c[2] + c[3])


def ser(col):
    return [{"year": YEARS[i], "value": rows[i][col]} for i in range(len(rows))]


SRC = {"publication": "농림축산식품 주요통계 2025",
       "section": "농업·농촌 Ⅵ.축산 2.축산물 수급 및 유통 (1)",
       "page": 379, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"}

meat = {
    "id": "meat_consumption_pc", "name": "1인당 육류 소비량", "group": "축산", "unit": "kg",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "국민 1인당 연간 육류 소비량. 계 + 축종별(쇠고기·돼지고기·닭고기)",
    "keywords": ["육류", "고기", "소비량", "쇠고기", "돼지고기", "닭고기"],
    "source": SRC, "series": ser(0), "series_label": "육류 계",
    "breakdown": [{"label": "쇠고기", "series": ser(1)},
                  {"label": "돼지고기", "series": ser(2)},
                  {"label": "닭고기", "series": ser(3)}],
    "related_ids": ["milk_consumption_pc", "egg_consumption_pc", "meat_production", "livestock_self_suff"],
    "tip": "국민 한 사람이 1년에 먹는 육류의 무게(kg)입니다. 계 = 쇠고기 + 돼지고기 + 닭고기. (p.379)"
}
milk = {
    "id": "milk_consumption_pc", "name": "1인당 우유 소비량", "group": "축산", "unit": "kg",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "국민 1인당 연간 우유(백색시유 등) 소비량",
    "keywords": ["우유", "유제품", "소비량"],
    "source": SRC, "series": ser(12), "breakdown": [],
    "related_ids": ["meat_consumption_pc", "egg_consumption_pc"],
    "tip": "국민 한 사람이 1년에 소비하는 우유의 무게(kg)입니다. (p.379)"
}
egg = {
    "id": "egg_consumption_pc", "name": "1인당 계란 소비량", "group": "축산", "unit": "개",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "국민 1인당 연간 계란 소비량(개)",
    "keywords": ["계란", "달걀", "소비량"],
    "source": SRC, "series": ser(6), "breakdown": [],
    "related_ids": ["meat_consumption_pc", "milk_consumption_pc"],
    "tip": "국민 한 사람이 1년에 소비하는 계란의 개수입니다. 단위는 무게가 아니라 **개**입니다. (p.379)"
}

json.dump([meat, milk, egg], open('/tmp/lc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 1인당 축산물 소비량 — 2024 ===")
print("육류 계 %s kg = 쇠고기 %s + 돼지고기 %s + 닭고기 %s" % (c[0], c[1], c[2], c[3]))
print("우유 %s kg · 계란 %s 개" % (c[12], c[6]))
for ind in [meat, milk, egg]:
    s = [p for p in ind["series"] if p["value"] is not None]
    print("■ %s (%s): %d~%d 최신 %s" % (ind["name"], ind["unit"], s[0]["year"], s[-1]["year"], s[-1]["value"]))
