# -*- coding: utf-8 -*-
"""식량작물 생산량·재배면적(품목별) 추출 → indicators.json 병합
- 계        : p.296 총괄 (PDF 300)  면적계 idx0, 생산량계 idx1
- 쌀(미곡)  : p.296 총괄            면적 idx2, 생산량 idx3
- 보리쌀    : p.313 맥류 (PDF 317)  겉보리(2,3)+쌀보리(4,5)+맥주보리(6,7) 합산
- 밀        : p.313 맥류            면적 idx8, 생산량 idx9
- 감자/고구마/콩/옥수수 : p.321 (PDF 325) 감자(0,1) 고구마(2,3) 콩(4,5) 옥수수(6,7)
- 서류      : 감자+고구마 합산
"""
import json, re, os
BASE = "/sessions/eager-charming-feynman/mnt/kr-agrifood-stats/data"
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))

def yy(y): return 1900 + y if y >= 53 else 2000 + y
def toks(line):
    out=[]
    for t in line.split():
        if t in ('-','–','－','·'): out.append(None); continue
        c=t.replace(',','').replace('p','')
        out.append(float(c) if re.fullmatch(r'-?\d+(\.\d+)?',c) else 'X')
    return out

def rows(pdfpage):
    """{year: [values]} — 연도로 시작하는 데이터행"""
    out={}
    for ln in PAGES[pdfpage-1].split('\n'):
        m=re.match(r'^\s*(\d{2})\s+(.*)$', ln)
        if not m: continue
        y=int(m.group(1))
        if 25<=y<=52: continue
        v=toks(m.group(2))
        if any(isinstance(x,(int,float)) for x in v): out[yy(y)]=v
    return out

R296=rows(300)   # 총괄
R313=rows(317)   # 맥류
R321=rows(325)   # 서류·두류·잡곡

def pick(R, idx):
    s=[]
    for y in sorted(R):
        v=R[y]; x=v[idx] if idx<len(v) else None
        s.append({"year":y,"value": x if isinstance(x,(int,float)) else None})
    for r in s:
        if r["year"]==2024 and r["value"] is not None: r["flag"]="p"
    return s

def addsum(R, idxs):
    s=[]
    for y in sorted(R):
        v=R[y]; tot=0; ok=False
        for i in idxs:
            x=v[i] if i<len(v) else None
            if isinstance(x,(int,float)): tot+=x; ok=True
        s.append({"year":y,"value": round(tot,1) if ok else None})
    for r in s:
        if r["year"]==2024 and r["value"] is not None: r["flag"]="p"
    return s

def src(section,page):
    return {"publication":"농림축산식품 주요통계 2025","section":section,"page":page,
            "org":"국가데이터처 농작물생산조사","license":"공공누리 출처표시"}

# ── 생산량 (천t) ──
prod_total = pick(R296,1)
prod_items = [
    ("쌀",     pick(R296,3)),
    ("보리쌀", addsum(R313,[3,5,7])),
    ("밀",     pick(R313,9)),
    ("옥수수", pick(R321,7)),
    ("콩",     pick(R321,5)),
    ("서류",   addsum(R321,[1,3])),
]
# ── 재배면적 (천ha) ──
area_total = pick(R296,0)
area_items = [
    ("쌀",     pick(R296,2)),
    ("보리쌀", addsum(R313,[2,4,6])),
    ("밀",     pick(R313,8)),
    ("옥수수", pick(R321,6)),
    ("콩",     pick(R321,4)),
    ("서류",   addsum(R321,[0,2])),
]

def last(s):
    v=[p for p in s if p["value"] is not None]
    return v[-1] if v else None

print("=== 생산량(천t) 2024 ===")
print("  계:", last(prod_total))
for n,s in prod_items: print(f"  {n}: {last(s)}")
print("=== 재배면적(천ha) 2024 ===")
print("  계:", last(area_total))
for n,s in area_items: print(f"  {n}: {last(s)}")

json.dump({"prod_total":prod_total,"prod_items":prod_items,
           "area_total":area_total,"area_items":area_items},
          open('/tmp/foodcrops.json','w',encoding='utf-8'), ensure_ascii=False)
