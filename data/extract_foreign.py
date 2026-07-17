# -*- coding: utf-8 -*-
"""외국 비교 4종 추가 → 기존 indicators.json에 병합
- 일본 곡물자급률(전치형 p539)
- 대만 농가인구 시계열 (p541, 연도행)
- 중국 농촌인구 시계열 (p551, 연도행)
- OECD 주요국 쌀 생산량 비교 (p506, 단년·국가별)
"""
import json, re, os
BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))
data = json.load(open(os.path.join(BASE, 'indicators.json'), encoding='utf-8'))

def nums(line):
    out = []
    for t in line.split():
        c = t.replace(',', '').replace('p', '')
        if re.fullmatch(r'-?\d+(\.\d+)?', c):
            out.append(float(c) if '.' in c else int(c))
    return out

def yy(y): return 1900 + y if y >= 53 else 2000 + y

def year_row_series(pageidx, col):
    out = []
    for ln in PAGES[pageidx - 1].split('\n'):
        s = ln.strip()
        m = re.match(r'^(\d{2})\s+(.*)$', s)
        if not m: continue
        y = int(m.group(1))
        if 25 <= y <= 52: continue
        vv = nums(m.group(2))
        if len(vv) > col:
            out.append({"year": yy(y), "value": vv[col]})
    return out

def src(section, page, org):
    return {"publication": "농림축산식품 주요통계 2025", "section": section,
            "page": page, "org": org, "license": "공공누리 출처표시"}

new = []

# ── 일본 곡물자급률 (p539 전치형) ──
def japan_grain():
    lines = PAGES[538].split('\n')
    years = None
    for ln in lines:
        if re.search(r'연도.*80\s+85\s+90', ln) or re.search(r'\b80\s+85\s+90\s+95\b', ln):
            years = [yy(int(x)) for x in nums(ln) if 0 <= x <= 99]
            break
    vals = None
    for ln in lines:
        if '식용' in ln and '사료' in ln:
            vals = nums(ln); break
    if years and vals:
        n = min(len(years), len(vals))
        return [{"year": years[i], "value": vals[i]} for i in range(n)]
    return []
jp = japan_grain()
new.append({"id": "japan_agri", "name": "일본 곡물자급률", "group": "국제비교", "unit": "%",
    "frequency": "연간", "is_headline": False, "description": "일본 곡물자급률(식용+사료용)",
    "keywords": ["일본", "자급률", "곡물", "국제비교"],
    "source": src("외국 주요통계 > Ⅱ. 일본 > 농산물 자급률", 535, "일본 농림수산성"),
    "series": jp, "related_ids": ["grain_self_suff", "food_self_suff"]})

# ── 대만 농가인구 (p541 연도행 idx1) ──
new.append({"id": "taiwan_agri", "name": "대만 농가인구", "group": "국제비교", "unit": "천명",
    "frequency": "연간", "is_headline": False, "description": "대만 농가인구",
    "keywords": ["대만", "농가인구", "국제비교"],
    "source": src("외국 주요통계 > Ⅲ. 대만 > 농가인구 및 가구", 537, "대만 행정원 농업위원회"),
    "series": year_row_series(541, 1), "related_ids": ["farm_population"]})

# ── 중국 농촌인구 (p551 연도행 idx1) ──
new.append({"id": "china_agri", "name": "중국 농촌인구", "group": "국제비교", "unit": "천명",
    "frequency": "연간", "is_headline": False, "description": "중국 농촌인구",
    "keywords": ["중국", "농촌인구", "국제비교"],
    "source": src("외국 주요통계 > Ⅳ. 중국 > 농촌인구 및 가구", 547, "중국 국가통계국"),
    "series": year_row_series(551, 1), "related_ids": ["farm_population"]})

# ── OECD 주요국 쌀 생산량 비교 (p506 단년·국가별) ──
def oecd_rice():
    rows = []
    for ln in PAGES[505].split('\n'):
        vv = nums(ln)
        if len(vv) == 5 and any(ch >= '가' and ch <= '힣' for ch in ln):
            name = re.sub(r'[\d,\-\.\s]', '', ln).strip()
            if name and vv[0] is not None:
                rows.append((name, vv[0]))  # 쌀 생산량
    return rows
rice = oecd_rice()
# 쌀 생산량 상위 + 한국 포함, 최대 9개국
korea = [r for r in rice if r[0] == '한국']
top = sorted([r for r in rice if r[1] >= 150], key=lambda x: -x[1])[:9]
sel = {n: v for n, v in top}
for n, v in korea: sel[n] = v
compare = sorted([{"label": n, "value": v} for n, v in sel.items()], key=lambda x: -x["value"])
new.append({"id": "intl_rice_compare", "name": "주요국 쌀 생산량 비교", "group": "국제비교",
    "unit": "천t", "frequency": "단년", "is_headline": False,
    "description": "OECD 주요국 쌀 생산량 비교(최근년, 한국 포함)",
    "keywords": ["OECD", "쌀", "생산량", "국제비교", "주요국"],
    "source": src("외국 주요통계 > Ⅰ. 주요국별 기본통계 > 농업", 502, "OECD/국가데이터처"),
    "compare": compare, "related_ids": ["rice_production"]})

# ── 병합 ──
existing_ids = {i["id"] for i in data["indicators"]}
for ind in new:
    if ind["id"] not in existing_ids:
        data["indicators"].append(ind)
if not any(g["id"] == "intl" for g in data["groups"]):
    data["groups"].append({"id": "intl", "name": "국제비교", "order": 11})
data["meta"]["status"] = "v3 (국내 26 + 남북한 4 + 국제비교 4)"
data["meta"]["pending"] = ["meat_consumption_pc", "timber_self_suff",
    "fishery_production·return_farming(본서 미수록)", "OECD 다품목·일본 스냅샷 상세"]

json.dump(data, open('/tmp/indicators.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("총 지표:", len(data["indicators"]))
for ind in new:
    if "series" in ind:
        v = [p for p in ind["series"] if p["value"] is not None]
        print(f'  {ind["id"]:18s} {len(v)}pts  {v[0] if v else None} ~ {v[-1] if v else None}')
    else:
        print(f'  {ind["id"]:18s} 비교 {len(ind["compare"])}개국:', [c["label"] for c in ind["compare"]])
