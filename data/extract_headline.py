# -*- coding: utf-8 -*-
"""헤드라인 지표 추출 → indicators.json
원자료: 2025 농림축산식품 주요통계.pdf (pdftotext -layout 텍스트 사용)
PDF페이지 = 인쇄쪽 + 4
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))

def toks(line):
    """숫자/대시 토큰 리스트로. 콤마 제거, '-'→None, 'p' 플래그 무시."""
    out = []
    for t in line.split():
        t = t.strip()
        if t in ('-', '–', '－'):
            out.append(None); continue
        c = t.replace(',', '').replace('p', '')
        if re.fullmatch(r'-?\d+(\.\d+)?', c):
            out.append(float(c) if '.' in c else int(c))
        else:
            out.append('X')  # 비수치 토큰 표식
    return out

def yy(y):
    return 1900 + y if y >= 70 else 2000 + y

def year_rows(pageidx):
    """연도가 행인 표: (연도, [값...]) 반환. 첫 토큰이 2자리 연도인 라인만."""
    rows = []
    for ln in PAGES[pageidx - 1].split('\n'):
        s = ln.strip()
        m = re.match(r'^(\d{2})\s+(.*)$', s)
        if not m:
            continue
        y = int(m.group(1))
        if y > 24 and y < 70:   # 연도 범위 밖(25~69)은 제외
            continue
        vals = toks(m.group(2))
        # 값이 최소 1개 이상 수치여야 데이터행
        if any(isinstance(v, (int, float)) for v in vals):
            rows.append((yy(y), vals))
    return rows

def series(pageidx, col, scale=1.0):
    out = []
    for year, vals in year_rows(pageidx):
        v = vals[col] if col < len(vals) else None
        if isinstance(v, (int, float)):
            out.append({"year": year, "value": round(v * scale, 3) if scale != 1 else v})
        else:
            out.append({"year": year, "value": None})
    # 2024 잠정치 플래그
    for r in out:
        if r["year"] == 2024 and r["value"] is not None:
            r["flag"] = "p"
    return out

def ratio_series(pageidx, num_col, den_col):
    out = []
    for year, vals in year_rows(pageidx):
        try:
            n, d = vals[num_col], vals[den_col]
            if isinstance(n, (int, float)) and isinstance(d, (int, float)) and d:
                out.append({"year": year, "value": round(n / d * 100, 1)})
            else:
                out.append({"year": year, "value": None})
        except IndexError:
            out.append({"year": year, "value": None})
    for r in out:
        if r["year"] == 2024 and r["value"] is not None:
            r["flag"] = "p"
    return out

def src(section, page, org):
    return {"publication": "농림축산식품 주요통계 2025", "section": section,
            "page": page, "org": org, "license": "공공누리 출처표시"}

indicators = []

# 4 경지면적 (p28 인쇄24) idx0 = 경지면적(천ha)
indicators.append({
    "id": "cultivated_area", "name": "경지면적", "group": "농업 한눈에", "unit": "천ha",
    "frequency": "연간", "is_headline": True, "description": "전국 경지면적(논+밭)",
    "keywords": ["경지", "경지면적", "논", "밭", "농지"],
    "source": src("기본통계 > Ⅰ. 국토 및 경지 > 경지이용상황", 24, "국가데이터처 KOSIS"),
    "series": series(28, 0), "related_ids": ["rice_area", "agri_output_value"]})

# 3 농가인구 (p66 인쇄62) idx0 = 농가인구(천명)
indicators.append({
    "id": "farm_population", "name": "농가 인구", "group": "농업 한눈에", "unit": "천명",
    "frequency": "연간", "is_headline": True, "description": "농가에 속한 총 인구",
    "keywords": ["농가인구", "인구", "농촌인구"],
    "source": src("기본통계 > Ⅲ. 인구 및 가구 > 연령별·성별 농가인구", 62, "국가데이터처 농림어업조사"),
    "series": series(66, 0), "related_ids": ["farm_households", "farmer_aging_rate"]})

# 30 경영주 고령화율 (p56 인쇄52) 65세이상(idx7)/농가수(idx0)
indicators.append({
    "id": "farmer_aging_rate", "name": "경영주 고령화율(65세+)", "group": "농촌·사람", "unit": "%",
    "frequency": "연간", "is_headline": True, "description": "경영주가 65세 이상인 농가 비율",
    "keywords": ["고령화", "고령화율", "65세", "경영주", "노령"],
    "source": src("기본통계 > Ⅲ. 인구 및 가구 > 경영주 연령별 농가", 52, "국가데이터처 농림어업조사"),
    "series": ratio_series(56, 7, 0), "related_ids": ["farm_population", "farm_households"]})

# 6 농가소득 (p156 인쇄152) idx0 = 농가소득(천원)
indicators.append({
    "id": "farm_income", "name": "농가소득(호당)", "group": "농업 한눈에", "unit": "천원",
    "frequency": "연간", "is_headline": True,
    "description": "농가 1호당 연간 소득(농업+농외+이전+비경상소득)",
    "keywords": ["농가소득", "소득", "농가경제", "농업소득", "농외소득"],
    "source": src("기본통계 > Ⅶ. 농가경제 > 원천별 농가소득", 152, "국가데이터처 농가경제조사"),
    "series": series(156, 0), "related_ids": ["agri_output_value", "farm_population"]})

# 7 식량자급률 (p335 인쇄331) idx0 = 계
indicators.append({
    "id": "food_self_suff", "name": "식량자급률", "group": "식량·자급률", "unit": "%",
    "frequency": "연간", "is_headline": True, "description": "식량자급률(사료용 소비 제외, 계)",
    "keywords": ["식량자급률", "자급률", "식량안보"],
    "source": src("농업·농촌 > Ⅳ. 식량작물 > 양곡의 자급률(식량자급률)", 331, "식량정책관 식량정책과"),
    "series": series(335, 0), "related_ids": ["grain_self_suff", "rice_production"]})

# 8 곡물자급률 (p334 인쇄330) idx0 = 계 (사료용 포함)
indicators.append({
    "id": "grain_self_suff", "name": "곡물자급률", "group": "식량·자급률", "unit": "%",
    "frequency": "연간", "is_headline": False, "description": "곡물자급률(사료용 소비 포함, 계)",
    "keywords": ["곡물자급률", "자급률", "사료"],
    "source": src("농업·농촌 > Ⅳ. 식량작물 > 양곡의 자급률(곡물자급률)", 330, "식량정책관 식량정책과"),
    "series": series(334, 0), "related_ids": ["food_self_suff"]})

# 9 쌀 생산량 (p306 인쇄302) idx1=생산량, idx0=면적
indicators.append({
    "id": "rice_production", "name": "쌀(미곡) 생산량", "group": "식량·자급률", "unit": "천t",
    "frequency": "연간", "is_headline": True, "description": "미곡(쌀) 생산량(계)",
    "keywords": ["쌀", "미곡", "생산량", "벼"],
    "source": src("농업·농촌 > Ⅳ. 식량작물 > 미곡 재배면적 및 생산량", 302, "국가데이터처"),
    "series": series(306, 1), "related_ids": ["rice_area", "food_self_suff"]})
indicators.append({
    "id": "rice_area", "name": "쌀 재배면적", "group": "식량·자급률", "unit": "천ha",
    "frequency": "연간", "is_headline": False, "description": "미곡(쌀) 재배면적(계)",
    "keywords": ["쌀", "재배면적", "논", "벼"],
    "source": src("농업·농촌 > Ⅳ. 식량작물 > 미곡 재배면적 및 생산량", 302, "국가데이터처"),
    "series": series(306, 0), "related_ids": ["rice_production", "cultivated_area"]})

# 12 농림수산품 생산자물가 / 13 식료품 소비자물가 / 14 농가교역조건 (p116 인쇄112)
# 컬럼: [PPI총, PPI농림수산품, CPI총, CPI식료품, 농가판매A, 농가구입B, 교역조건]
indicators.append({
    "id": "ppi_agri", "name": "농림수산품 생산자물가지수", "group": "물가·가격", "unit": "지수(2020=100)",
    "frequency": "연간", "is_headline": True, "description": "농림수산품 생산자물가지수(연평균)",
    "keywords": ["생산자물가", "PPI", "물가", "농축산물"],
    "source": src("기본통계 > Ⅴ. 물가 > 물가지수 총괄", 112, "한국은행/국가데이터처"),
    "series": series(116, 1), "related_ids": ["cpi_food", "farm_terms_trade"]})
indicators.append({
    "id": "cpi_food", "name": "식료품 소비자물가지수", "group": "물가·가격", "unit": "지수(2020=100)",
    "frequency": "연간", "is_headline": False, "description": "식료품 소비자물가지수(연평균)",
    "keywords": ["소비자물가", "CPI", "식료품", "물가"],
    "source": src("기본통계 > Ⅴ. 물가 > 물가지수 총괄", 112, "한국은행/국가데이터처"),
    "series": series(116, 3), "related_ids": ["ppi_agri"]})
indicators.append({
    "id": "farm_terms_trade", "name": "농가 교역조건지수", "group": "물가·가격", "unit": "지수(2020=100)",
    "frequency": "연간", "is_headline": False, "description": "농가교역조건지수(판매가격/구입가격×100)",
    "keywords": ["교역조건", "농가판매", "농가구입", "물가"],
    "source": src("기본통계 > Ⅴ. 물가 > 물가지수 총괄", 112, "국가데이터처"),
    "series": series(116, 6), "related_ids": ["ppi_agri", "cpi_food"]})

# 15 가축 사육두수 (p376 인쇄372) breakdown: 한육우 idx0, 젖소 idx2, 돼지 idx4, 닭 idx6
def breakdown_series(pageidx, col):
    return series(pageidx, col)
indicators.append({
    "id": "livestock_heads", "name": "주요 가축 사육마릿수", "group": "축산", "unit": "천마리",
    "frequency": "연간", "is_headline": True, "description": "주요 축종별 사육마릿수(연도말)",
    "keywords": ["가축", "사육", "한우", "젖소", "돼지", "닭", "사육두수"],
    "source": src("농업·농촌 > Ⅵ. 축산 > 가축사육마릿수 및 호수", 372, "국가데이터처 가축동향조사"),
    "breakdown": [
        {"label": "한·육우", "series": breakdown_series(376, 0)},
        {"label": "젖소", "series": breakdown_series(376, 2)},
        {"label": "돼지", "series": breakdown_series(376, 4)},
        {"label": "닭", "series": breakdown_series(376, 6)},
    ],
    "related_ids": ["meat_production"]})

# 21/22/23 수출·수입·무역수지 (p140 인쇄136) — 전치형, 연도 2020~2024
def trade_row(pageidx, label_re):
    yrs = [2020, 2021, 2022, 2023, 2024]
    for ln in PAGES[pageidx - 1].split('\n'):
        if re.search(label_re, ln):
            nums = [t for t in toks(ln) if isinstance(t, (int, float))]
            if len(nums) >= 5:
                s = [{"year": y, "value": nums[i]} for i, y in enumerate(yrs)]
                s[-1]["flag"] = "p"
                return s
    return []
# 수출 농림축산품 (첫 등장), 수입 농림축산품(두번째), 수지(세번째)
def trade_rows_all(pageidx):
    res = []
    for ln in PAGES[pageidx - 1].split('\n'):
        if re.search(r'농림축산품', ln):
            nums = [t for t in toks(ln) if isinstance(t, (int, float))]
            if len(nums) >= 5:
                res.append(nums[:5])
    return res  # [수출, 수입, 수지]
tr = trade_rows_all(140)
yrs = [2020, 2021, 2022, 2023, 2024]
if len(tr) >= 3:
    for idx, (iid, nm, hl, desc) in enumerate([
        ("agri_export", "농림축산물 수출액", True, "농림축산품 수출액(통관)"),
        ("agri_import", "농림축산물 수입액", False, "농림축산품 수입액(통관)"),
        ("agri_trade_balance", "농림축산물 무역수지", False, "농림축산품 무역수지(수출−수입)")]):
        s = [{"year": y, "value": tr[idx][i]} for i, y in enumerate(yrs)]
        s[-1]["flag"] = "p"
        indicators.append({
            "id": iid, "name": nm, "group": "무역", "unit": "백만$",
            "frequency": "연간", "is_headline": hl, "description": desc,
            "keywords": ["무역", "수출", "수입", "무역수지", "농림축산물"],
            "source": src("기본통계 > Ⅵ. 국제수지 및 무역 > 수출입 실적(총괄)", 136,
                          "식품산업정책관 농식품수출진흥과"),
            "series": s, "related_ids": ["agri_export", "agri_import", "agri_trade_balance"]})

groups = [
    {"id": "overview", "name": "농업 한눈에", "order": 1},
    {"id": "food", "name": "식량·자급률", "order": 2},
    {"id": "price", "name": "물가·가격", "order": 3},
    {"id": "livestock", "name": "축산", "order": 4},
    {"id": "trade", "name": "무역", "order": 6},
    {"id": "rural", "name": "농촌·사람", "order": 10},
]

manifest = {
    "meta": {"title": "농림축산식품 주요통계", "edition": 2025, "base_year": 2020,
             "license": "공공누리 제1유형(출처표시)", "source_pdf": "2025 농림축산식품 주요통계.pdf",
             "generated_at": "2026-07-16", "status": "v1 (헤드라인 지표)"},
    "groups": groups,
    "indicators": indicators,
}

out = os.path.join(BASE, "indicators.json")
json.dump(manifest, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("지표 수:", len(indicators))
for ind in indicators:
    if "series" in ind:
        vals = [p for p in ind["series"] if p["value"] is not None]
        last = vals[-1] if vals else None
        print(f'  {ind["id"]:22s} {len(vals):2d}pts  최신 {last}')
    else:
        print(f'  {ind["id"]:22s} breakdown {len(ind["breakdown"])}종')
print("저장:", out)
