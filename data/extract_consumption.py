# -*- coding: utf-8 -*-
"""1인당 양곡 소비량을 계(전체)+품목별 breakdown으로 확장 (p336)
컬럼: 계(0) 쌀(1) 보리쌀(2) 밀(3) 옥수수(4) 콩(5) 서류(6) 기타(7)
"""
import json, re
BASE = "/sessions/eager-charming-feynman/mnt/kr-agrifood-stats/data"
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))
data = json.load(open(BASE + '/indicators.json', encoding='utf-8'))

def yy(y): return 1900 + y if y >= 53 else 2000 + y
def toks(line):
    out = []
    for t in line.split():
        if t in ('-', '–', '－', '·'): out.append(None); continue
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

ITEMS = [("쌀",1),("보리쌀",2),("밀",3),("옥수수",4),("콩",5),("서류",6)]

for ind in data["indicators"]:
    if ind["id"] == "rice_consumption_pc":
        ind["name"] = "1인당 양곡 소비량"
        ind["description"] = "1인당 연간 양곡 소비량(계) + 품목별(쌀·보리쌀·밀·옥수수·콩·서류)"
        ind["keywords"] = ["소비량","1인당","쌀","밀","옥수수","보리","콩","양곡","식생활"]
        ind["series"] = col_series(336, 0)   # 계(전체)
        ind["breakdown"] = [{"label": nm, "series": col_series(336, c)} for nm, c in ITEMS]
        ind["source"]["section"] = "농업·농촌 > Ⅳ. 식량작물 > 양곡 1인당 연간소비량"
        break

data["meta"]["status"] = "v5 (자급률·1인당소비 품목별)"
json.dump(data, open('/tmp/indicators.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

for ind in data["indicators"]:
    if ind["id"] == "rice_consumption_pc":
        print("name:", ind["name"])
        print("계 최신:", [p for p in ind["series"] if p["value"] is not None][-1])
        for b in ind["breakdown"]:
            v = [p for p in b["series"] if p["value"] is not None][-1]
            print("  ", b["label"], "최신", v)
