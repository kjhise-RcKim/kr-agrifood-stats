# -*- coding: utf-8 -*-
"""3단계-A: 주요작물 10a당 생산비·소득 (원문 Ⅷ. 주요 농축산물 생산비 및 소득)
  p.180 논벼 · p.181 겉보리 · p.182 쌀보리 · p.187 콩
표 구조(4개 표 동일): 연도 | 총수입(A) | 생산비(B) | 단가 | 경영비(C) | 소득(A-C) | 순수익(A-B)
PDF쪽 = 인쇄쪽 + 4.  실행: python3 data/extract_stage3a.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')

COL = {"총수입": 0, "생산비": 1, "단가": 2, "경영비": 3, "소득": 4, "순수익": 5}
CROPS = [("논벼", 180), ("겉보리", 181), ("쌀보리", 182), ("콩", 187)]


def page(printed):
    p = printed + 4
    return subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), PDF, '-'],
                          capture_output=True, text=True).stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def num(t):
    c = t.replace(',', '')
    return int(c) if re.fullmatch(r'-?\d+', c) else None


def rows6(txt):
    """6개 값을 가진 연도 행만 채택. '-'는 결측."""
    out = {}
    for ln in txt.split('\n'):
        m = re.match(r'^\s*(\d{2})\s+(.+)$', ln)
        if not m:
            continue
        y = int(m.group(1))
        if 25 <= y <= 52:
            continue
        toks = m.group(2).split()
        vals = [None if t in ('-', '–', '－') else num(t) for t in toks]
        if len(vals) != 6:
            continue
        out[yy(y)] = vals
    return out


DATA = {name: rows6(page(pg)) for name, pg in CROPS}

# 원문에 값이 실제로 있는지 확인 (안전장치)
for name, rows in DATA.items():
    assert rows, "%s 표 파싱 실패" % name


def series(name, col):
    rows = DATA[name]
    return [{"year": y, "value": rows[y][col]} for y in sorted(rows)]


def make(iid, label, colname, desc, tip):
    return {
        "id": iid, "name": label, "group": "농가경제", "unit": "원/10a",
        "frequency": "연간", "is_headline": False, "brief_weight": 1,
        "description": desc, "keywords": [],
        "source": {"publication": "농림축산식품 주요통계 2025",
                   "section": "기본통계 Ⅷ.주요 농축산물 생산비 및 소득 1",
                   "page": 180, "org": "농림축산식품부",
                   "license": "공공누리 제1유형(출처표시)"},
        "series": [],
        "breakdown": [{"label": nm, "series": series(nm, COL[colname])} for nm, _ in CROPS],
        "related_ids": [], "tip": tip
    }


SRC = ("논벼 p.180 · 겉보리 p.181 · 쌀보리 p.182 · 콩 p.187. "
       "자료: 농축산물생산비조사(2009년까지), 농산물소득조사(2010년부터).")

NEW = [
    make("crop_income_10a", "작물별 10a당 소득", "소득",
         "주요 작물의 10a(300평)당 소득. 총수입에서 경영비를 뺀 값",
         "**소득 = 총수입 − 경영비**입니다. 경영비는 종자·비료·농약·기계 등 실제로 지출한 돈이며, "
         "자기 노동비와 토지용역비는 빠져 있습니다.\n10a는 300평입니다. 물가를 반영하지 않은 그해 금액입니다.\n" + SRC),
    make("crop_netprofit_10a", "작물별 10a당 순수익", "순수익",
         "주요 작물의 10a당 순수익. 총수입에서 생산비를 뺀 값",
         "**순수익 = 총수입 − 생산비**입니다. 생산비에는 경영비에 더해 자기 노동비·토지용역비까지 들어가므로 "
         "순수익은 소득보다 작고, **음수가 나올 수 있습니다**(값을 다 따지면 손해라는 뜻).\n" + SRC),
    make("crop_revenue_10a", "작물별 10a당 총수입", "총수입",
         "주요 작물의 10a당 총수입",
         "10a(300평)에서 나온 총수입입니다. 물가를 반영하지 않은 그해 금액입니다.\n" + SRC),
    make("crop_cost_10a", "작물별 10a당 생산비", "생산비",
         "주요 작물의 10a당 생산비(경영비 + 자기 노동비·토지용역비)",
         "**생산비 = 경영비 + 자기 노동비 + 토지용역비**입니다. 실제 지출만 따진 경영비보다 큽니다.\n" + SRC),
]

json.dump(NEW, open('/tmp/stage3a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 추출 결과 (원/10a) ===")
for ind in NEW:
    print("■", ind["name"])
    for b in ind["breakdown"]:
        v = [p for p in b["series"] if p["value"] is not None]
        print("   · %-5s %2dpt %d~%d  최신 %s" %
              (b["label"], len(v), v[0]["year"], v[-1]["year"], format(v[-1]["value"], ',')))
