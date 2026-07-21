# -*- coding: utf-8 -*-
"""전체 지표 추출 → indicators.json (국내 26 + 남북한 4)
원자료: 2025 농림축산식품 주요통계.pdf, PDF페이지 = 인쇄쪽 + 4
외국(일본·대만·중국·OECD) 비교와 일부 지표는 별도 처리(문서 참조)."""
import json, re, os
BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = json.load(open('/tmp/pages.json', encoding='utf-8'))

def toks(line):
    out = []
    for t in line.split():
        if t in ('-', '–', '－'): out.append(None); continue
        c = t.replace(',', '').replace('p', '')
        if re.fullmatch(r'-?\d+(\.\d+)?', c):
            out.append(float(c) if '.' in c else int(c))
        else: out.append('X')
    return out

def yy(y): return 1900 + y if y >= 53 else 2000 + y

def year_rows(pageidx, min_year=53):
    rows = []
    for ln in PAGES[pageidx - 1].split('\n'):
        s = ln.strip()
        m = re.match(r'^(\d{2})\s+(.*)$', s)
        if not m: continue
        y = int(m.group(1))
        if 25 <= y <= 52: continue          # 연도 범위 밖
        vals = toks(m.group(2))
        if any(isinstance(v, (int, float)) for v in vals):
            rows.append((yy(y), vals))
    return rows

def series(pageidx, col, scale=1.0):
    out = []
    for year, vals in year_rows(pageidx):
        v = vals[col] if col < len(vals) else None
        out.append({"year": year, "value": (round(v*scale,3) if scale!=1 else v)
                    if isinstance(v,(int,float)) else None})
    for r in out:
        if r["year"] == 2024 and r["value"] is not None: r["flag"] = "p"
    return out

def ratio_series(pageidx, num_col, den_col, nd=1):
    out = []
    for year, vals in year_rows(pageidx):
        try:
            n, d = vals[num_col], vals[den_col]
            v = round(n/d*100, nd) if isinstance(n,(int,float)) and isinstance(d,(int,float)) and d else None
        except IndexError: v = None
        out.append({"year": year, "value": v})
    for r in out:
        if r["year"] == 2024 and r["value"] is not None: r["flag"] = "p"
    return out

def src(section, page, org):
    return {"publication": "농림축산식품 주요통계 2025", "section": section,
            "page": page, "org": org, "license": "공공누리 출처표시"}

I = []  # indicators
def add(**k): I.append(k)

# ── 농업 총괄 ──
# 농림업 생산액 (p88: 2014~17, p89: 2018~24) — 십억원
def agri_output():
    s = []
    p88 = PAGES[87].split('\n')
    for ln in p88:
        if ('림' in ln and '업' in ln) and not ln.strip().startswith(('품','(')):
            nums = [t for t in toks(ln) if isinstance(t,(int,float))]
            if len(nums) >= 4:
                for i, y in enumerate([2014,2015,2016,2017]): s.append({"year":y,"value":nums[i]})
                break
    p89 = PAGES[88].split('\n')
    for ln in p89:
        nums = [t for t in toks(ln) if isinstance(t,(int,float))]
        # 연도 헤더줄(18~24) 배제: 실제 생산액은 1000 이상
        if len(nums) >= 7 and max(nums) > 1000:
            for i, y in enumerate([2018,2019,2020,2021,2022,2023,2024]): s.append({"year":y,"value":nums[i]})
            break
    if s and s[-1]["year"]==2024: s[-1]["flag"]="p"
    return s
add(id="agri_output_value", name="농림업 생산액", group="농업 총괄", unit="십억원",
    frequency="연간", is_headline=True, description="농림업 생산액(당해년가격)",
    keywords=["생산액","농림업생산액","산출"], source=src("기본통계 > Ⅳ. 국민계정 및 농림업생산액 > 농림업 생산액",84,"농림축산식품부 농림업생산지수"),
    series=agri_output(), related_ids=["farm_income","cultivated_area"])
add(id="cultivated_area", name="경지면적", group="농업 총괄", unit="천ha", frequency="연간",
    is_headline=True, description="전국 경지면적(논+밭)", keywords=["경지","경지면적","논","밭"],
    source=src("기본통계 > Ⅰ. 국토 및 경지 > 경지이용상황",24,"국가데이터처 KOSIS"),
    series=series(28,0), related_ids=["rice_area","agri_output_value"])
add(id="farm_households", name="농가 호수", group="농업 총괄", unit="천호", frequency="연간",
    is_headline=False, description="총 농가 호수", keywords=["농가","농가호수","호수"],
    source=src("기본통계 > Ⅲ. 인구 및 가구 > 경영주 연령별 농가",52,"국가데이터처 농림어업조사"),
    series=series(56,0), related_ids=["farm_population","farmer_aging_rate"])
add(id="farm_population", name="농가 인구", group="농업 총괄", unit="천명", frequency="연간",
    is_headline=True, description="농가에 속한 총 인구", keywords=["농가인구","인구","농촌인구"],
    source=src("기본통계 > Ⅲ. 인구 및 가구 > 연령별·성별 농가인구",62,"국가데이터처 농림어업조사"),
    series=series(66,0), related_ids=["farm_households","farmer_aging_rate"])
add(id="agri_gdp_share", name="농림어업 GDP 비중", group="농업 총괄", unit="%", frequency="연간",
    is_headline=False, description="국내총생산 대비 농림어업 비중(명목)", keywords=["GDP","비중","부가가치","농림어업"],
    source=src("기본통계 > Ⅳ. 국민계정 > 생산구조",76,"한국은행"),
    series=series(80,1), related_ids=["agri_output_value"])
add(id="farm_income", name="농가소득(호당)", group="농업 총괄", unit="천원", frequency="연간",
    is_headline=True, description="농가 1호당 연간 소득(농업+농외+이전+비경상)", keywords=["농가소득","소득","농가경제"],
    source=src("기본통계 > Ⅶ. 농가경제 > 원천별 농가소득",152,"국가데이터처 농가경제조사"),
    series=series(156,0), related_ids=["agri_output_value","farm_population"])

# ── 식량·자급률 ──
add(id="food_self_suff", name="식량자급률", group="식량·자급률", unit="%", frequency="연간",
    is_headline=True, description="식량자급률(사료용 제외, 계)", keywords=["식량자급률","자급률","식량안보"],
    source=src("농업·농촌 > Ⅳ. 식량작물 > 양곡의 자급률(식량)",331,"식량정책관 식량정책과"),
    series=series(335,0), related_ids=["grain_self_suff","rice_production"])
add(id="grain_self_suff", name="곡물자급률", group="식량·자급률", unit="%", frequency="연간",
    is_headline=False, description="곡물자급률(사료용 포함, 계)", keywords=["곡물자급률","자급률","사료"],
    source=src("농업·농촌 > Ⅳ. 식량작물 > 양곡의 자급률(곡물)",330,"식량정책관 식량정책과"),
    series=series(334,0), related_ids=["food_self_suff"])
add(id="rice_production", name="쌀(미곡) 생산량", group="식량·자급률", unit="천t", frequency="연간",
    is_headline=True, description="미곡(쌀) 생산량(계)", keywords=["쌀","미곡","생산량","벼"],
    source=src("농업·농촌 > Ⅳ. 식량작물 > 미곡 재배면적 및 생산량",302,"국가데이터처"),
    series=series(306,1), related_ids=["rice_area","food_self_suff"])
add(id="rice_area", name="쌀 재배면적", group="식량·자급률", unit="천ha", frequency="연간",
    is_headline=False, description="미곡(쌀) 재배면적(계)", keywords=["쌀","재배면적","논"],
    source=src("농업·농촌 > Ⅳ. 식량작물 > 미곡 재배면적 및 생산량",302,"국가데이터처"),
    series=series(306,0), related_ids=["rice_production","cultivated_area"])
add(id="rice_consumption_pc", name="1인당 쌀 소비량", group="식량·자급률", unit="kg", frequency="연간",
    is_headline=False, description="1인당 연간 쌀 소비량", keywords=["쌀소비","1인당","소비량"],
    source=src("농업·농촌 > Ⅳ. 식량작물 > 양곡 1인당 연간소비량",332,"국가데이터처 양곡소비량조사"),
    series=series(336,1), related_ids=["rice_production"])

# ── 물가·가격 (p116) [PPI총,PPI농림수산,CPI총,CPI식료품,판매A,구입B,교역] ──
add(id="ppi_agri", name="농림수산품 생산자물가지수", group="물가·가격", unit="지수(2020=100)",
    frequency="연간", is_headline=True, description="농림수산품 생산자물가지수(연평균)",
    keywords=["생산자물가","PPI","물가"], source=src("기본통계 > Ⅴ. 물가 > 물가지수 총괄",112,"한국은행"),
    series=series(116,1), related_ids=["cpi_food","farm_terms_trade"])
add(id="cpi_food", name="식료품 소비자물가지수", group="물가·가격", unit="지수(2020=100)",
    frequency="연간", is_headline=False, description="식료품 소비자물가지수(연평균)",
    keywords=["소비자물가","CPI","식료품"], source=src("기본통계 > Ⅴ. 물가 > 물가지수 총괄",112,"국가데이터처"),
    series=series(116,3), related_ids=["ppi_agri"])
add(id="farm_terms_trade", name="농가 교역조건지수", group="물가·가격", unit="지수(2020=100)",
    frequency="연간", is_headline=False, description="농가교역조건지수(판매/구입×100)",
    keywords=["교역조건","농가판매","농가구입"], source=src("기본통계 > Ⅴ. 물가 > 물가지수 총괄",112,"국가데이터처"),
    series=series(116,6), related_ids=["ppi_agri","cpi_food"])

# ── 축산 ──
add(id="livestock_heads", name="주요 가축 사육마릿수", group="축산", unit="천마리", frequency="연간",
    is_headline=True, description="주요 축종별 사육마릿수(연도말)", keywords=["가축","사육","한우","젖소","돼지","닭"],
    source=src("농업·농촌 > Ⅵ. 축산 > 가축사육마릿수 및 호수",372,"국가데이터처 가축동향조사"),
    breakdown=[{"label":"한·육우","series":series(376,0)},{"label":"젖소","series":series(376,2)},
               {"label":"돼지","series":series(376,4)},{"label":"닭","series":series(376,6)}],
    related_ids=["meat_production"])
add(id="meat_production", name="축산물(육류) 생산량", group="축산", unit="천t", frequency="연간",
    is_headline=False, description="육류 국내 생산량(계)", keywords=["축산물","육류","생산량","고기"],
    source=src("농업·농촌 > Ⅵ. 축산 > 축산물 수급실적",378,"농림축산식품부"),
    series=series(382,2), related_ids=["livestock_self_suff","livestock_heads"])
add(id="livestock_self_suff", name="축산물(육류) 자급률", group="축산", unit="%", frequency="연간",
    is_headline=False, description="육류 자급률(생산÷수요)", keywords=["자급률","축산물","육류"],
    source=src("농업·농촌 > Ⅵ. 축산 > 축산물 수급실적",378,"농림축산식품부"),
    series=ratio_series(382,2,0), related_ids=["meat_production"])

# ── 채소·과일 ──
add(id="vegetable_production", name="채소류 생산량", group="채소·과일", unit="천t", frequency="연간",
    is_headline=False, description="전국 채소류 생산량", keywords=["채소","생산량","엽채","근채"],
    source=src("농업·농촌 > Ⅴ. 경제작물 > 채소류 생산량",340,"국가데이터처"),
    series=series(344,1), related_ids=["fruit_production"])
add(id="fruit_production", name="과실류 생산량", group="채소·과일", unit="천t", frequency="연간",
    is_headline=False, description="과실류 생산량(계)", keywords=["과일","과실","생산량","사과","배"],
    source=src("농업·농촌 > Ⅴ. 경제작물 > 과실류 생산량",348,"국가데이터처"),
    series=series(352,1), related_ids=["vegetable_production"])

# ── 무역 (p140 전치, 2020~24) ──
def trade():
    res=[]
    for ln in PAGES[139].split('\n'):
        if re.search(r'농림축산품', ln):
            nums=[t for t in toks(ln) if isinstance(t,(int,float))]
            if len(nums)>=5: res.append(nums[:5])
    return res
tr=trade(); yrs=[2020,2021,2022,2023,2024]
if len(tr)>=3:
    for idx,(iid,nm,hl,desc) in enumerate([
        ("agri_export","농림축산물 수출액",True,"농림축산품 수출액(통관)"),
        ("agri_import","농림축산물 수입액",False,"농림축산품 수입액(통관)"),
        ("agri_trade_balance","농림축산물 무역수지",False,"농림축산품 무역수지(수출−수입)")]):
        s=[{"year":y,"value":tr[idx][i]} for i,y in enumerate(yrs)]; s[-1]["flag"]="p"
        add(id=iid,name=nm,group="무역",unit="백만$",frequency="연간",is_headline=hl,description=desc,
            keywords=["무역","수출","수입","무역수지"],
            source=src("기본통계 > Ⅵ. 국제수지 및 무역 > 수출입 실적(총괄)",136,"식품산업정책관 농식품수출진흥과"),
            series=s,related_ids=["agri_export","agri_import","agri_trade_balance"])

# ── 임업 ──
add(id="forest_output", name="임산물 생산액", group="임업", unit="백만원", frequency="연간",
    is_headline=False, description="임산물 생산실적(합계 금액)", keywords=["임산물","임업","생산액"],
    source=src("임업 > Ⅱ. 임산물 생산 및 수급 > 연도별 임산물 생산실적",426,"산림청"),
    series=series(430,0), related_ids=[])

# ── 어업 ──
add(id="fishery_income", name="어가소득(호당)", group="어업", unit="천원", frequency="연간",
    is_headline=False, description="어가 1호당 연간 소득", keywords=["어가","소득","어업"],
    source=src("어업 > Ⅱ. 어가경제 > 어가경제 주요지표",442,"국가데이터처 어가경제조사"),
    series=series(446,0), related_ids=["farm_income"])

# ── 식품산업 ──
add(id="food_industry_size", name="식품산업 시장규모", group="식품산업", unit="백만원", frequency="연간",
    is_headline=False, description="식품산업 시장규모(제조업+음식점·주점업)", keywords=["식품산업","시장규모","외식"],
    source=src("식품 > Ⅰ. 식품산업 현황 > 식품산업 규모",461,"국가데이터처"),
    series=series(465,0), related_ids=[])

# ── 농촌·사람 ──
add(id="farmer_aging_rate", name="경영주 고령화율(65세+)", group="농촌·사람", unit="%", frequency="연간",
    is_headline=True, description="경영주가 65세 이상인 농가 비율", keywords=["고령화","65세","경영주"],
    source=src("기본통계 > Ⅲ. 인구 및 가구 > 경영주 연령별 농가",52,"국가데이터처 농림어업조사"),
    series=ratio_series(56,7,0), related_ids=["farm_population","farm_households"])

# ── 남북한비교 (북한 열) ──
add(id="nk_population", name="북한 인구", group="남북한비교", unit="천명", frequency="연간",
    is_headline=False, description="북한 총인구", keywords=["북한","인구","남북한"],
    source=src("남북한 주요통계 > 인구 > 총인구",560,"통계청 북한통계"),
    series=series(564,2), related_ids=["nk_economy","nk_agriculture"])
add(id="nk_economy", name="북한 명목 GNI", group="남북한비교", unit="십억원", frequency="연간",
    is_headline=False, description="북한 명목 국민총소득(추정)", keywords=["북한","GNI","국민총소득","경제"],
    source=src("남북한 주요통계 > 국민경제 > GNI 및 경제성장률",565,"한국은행 추정"),
    series=series(569,1), related_ids=["nk_population"])
add(id="nk_agriculture", name="북한 농가인구", group="남북한비교", unit="천명", frequency="연간",
    is_headline=False, description="북한 농가인구(추정)", keywords=["북한","농가인구","농업"],
    source=src("남북한 주요통계 > 농림축산업 > 농가인구",568,"통계청 북한통계"),
    series=series(572,2), related_ids=["nk_population"])
add(id="nk_trade", name="북한 무역총액", group="남북한비교", unit="억$", frequency="연간",
    is_headline=False, description="북한 무역총액(추정)", keywords=["북한","무역","교역"],
    source=src("남북한 주요통계 > 무역 > 무역총액",575,"KOTRA/통계청 추정"),
    series=series(579,2), related_ids=["nk_economy"])

groups = [
    {"id":"overview","name":"농업 총괄","order":1},
    {"id":"food","name":"식량·자급률","order":2},
    {"id":"price","name":"물가·가격","order":3},
    {"id":"livestock","name":"축산","order":4},
    {"id":"veg","name":"채소·과일","order":5},
    {"id":"trade","name":"무역","order":6},
    {"id":"forest","name":"임업","order":7},
    {"id":"fishery","name":"어업","order":8},
    {"id":"food_ind","name":"식품산업","order":9},
    {"id":"rural","name":"농촌·사람","order":10},
    {"id":"nk","name":"남북한비교","order":12},
]
manifest = {"meta":{"title":"농림축산식품 주요통계","edition":2025,"base_year":2020,
    "license":"공공누리 제1유형(출처표시)","source_pdf":"2025 농림축산식품 주요통계.pdf",
    "generated_at":"2026-07-16","status":"v2 (국내 26 + 남북한 4)",
    "pending":["meat_consumption_pc(1인당 축산물소비)","timber_self_suff(목재자급률)",
        "fishery_production·return_farming(본서 미수록)","외국비교 japan/taiwan/china/OECD(전치형)"]},
    "groups":groups,"indicators":I}
json.dump(manifest, open(os.path.join(BASE,"indicators.json"),"w",encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("지표 수:", len(I))
for ind in I:
    n = len([p for p in ind.get("series",[]) if p["value"] is not None]) if "series" in ind else -1
    print("  ", ind["id"], (str(n)+"pts") if n>=0 else "breakdown")
