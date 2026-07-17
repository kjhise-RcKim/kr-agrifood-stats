# -*- coding: utf-8 -*-
"""식량·곡물 자급률에 품목별 breakdown 추가 → indicators.json 병합
- 식량자급률(p335): 계, 쌀, 보리쌀, 밀, 옥수수, 콩, 서류, 기타
- 곡물자급률(p334): 계, 쌀, 보리쌀, 밀, 옥수수, 두류, 서류, 기타
계(series)는 유지, 품목은 breakdown으로 추가(기타 제외).
"""
import json, re, os
BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))
data = json.load(open(os.path.join(BASE, 'indicators.json'), encoding='utf-8'))

def yy(y): return 1900 + y if y >= 53 else 2000 + y

def toks(line):
    out = []
    for t in line.split():
        if t in ('-', '–', '－'): out.append(None); continue
        c = t.replace(',', '').replace('p', '')
        out.append(float(c) if re.fullmatch(r'-?\d+(\.\d+)?', c) else 'X')
    return out

def col_series(pageidx, col):
    out = []
    for ln in PAGES[pageidx - 1].split('\n'):
        m = re.match(r'^\s*(\d{2})\s+(.*)$', ln)
        if not m: continue
        y = int(m.group(1))
        if 25 <= y <= 52: continue
        vals = toks(m.group(2))
        v = vals[col] if col < len(vals) else None
        out.append({"year": yy(y), "value": v if isinstance(v, (int, float)) else None})
    for r in out:
        if r["year"] == 2024 and r["value"] is not None: r["flag"] = "p"
    return out

# 품목 매핑 (계=0 제외, 기타 제외)
FOOD = [("쌀",1),("보리쌀",2),("밀",3),("옥수수",4),("콩",5),("서류",6)]      # p335
GRAIN = [("쌀",1),("보리쌀",2),("밀",3),("옥수수",4),("두류",5),("서류",6)]   # p334

def breakdown(pageidx, cols):
    return [{"label": nm, "series": col_series(pageidx, c)} for nm, c in cols]

for ind in data["indicators"]:
    if ind["id"] == "food_self_suff":
        ind["breakdown"] = breakdown(335, FOOD)
        ind["description"] = "식량자급률(사료용 제외). 계 라인 + 품목별(쌀·보리쌀·밀·옥수수·콩·서류)"
    elif ind["id"] == "grain_self_suff":
        ind["breakdown"] = breakdown(334, GRAIN)
        ind["description"] = "곡물자급률(사료용 포함). 계 라인 + 품목별(쌀·보리쌀·밀·옥수수·두류·서류)"

data["meta"]["status"] = "v4 (34지표 + 자급률 품목별)"
json.dump(data, open('/tmp/indicators.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 검증 출력
for ind in data["indicators"]:
    if ind["id"] in ("food_self_suff", "grain_self_suff"):
        print(ind["id"], "계 최신:", [p for p in ind["series"] if p["value"] is not None][-1])
        for b in ind["breakdown"]:
            v = [p for p in b["series"] if p["value"] is not None]
            print("   ", b["label"], f"{len(v)}pts 최신", v[-1] if v else None)
