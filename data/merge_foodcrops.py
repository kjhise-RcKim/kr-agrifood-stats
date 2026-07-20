# -*- coding: utf-8 -*-
"""식량작물 생산량·재배면적(품목별) 지표 추가 + 기존 쌀 단독 지표 2개 제거"""
import json
BASE="/sessions/eager-charming-feynman/mnt/kr-agrifood-stats/data"
fc=json.load(open('/tmp/foodcrops.json',encoding='utf-8'))
d=json.load(open(BASE+'/indicators.json',encoding='utf-8'))

def src(section,page):
    return {"publication":"농림축산식품 주요통계 2025","section":section,"page":page,
            "org":"국가데이터처 농작물생산조사","license":"공공누리 출처표시"}

NOTE=("계는 원문의 식량작물 전체(정곡 기준)로, 표시된 6품목 합계와 정확히 일치하지 않습니다"
      "(서류는 생서 기준, 기타 잡곡 등 포함). 보리쌀=겉보리+쌀보리+맥주보리, 서류=감자+고구마.")

prod={
 "id":"food_crop_production","name":"식량작물 생산량","group":"식량·자급률","unit":"천t",
 "frequency":"연간","is_headline":True,
 "description":"식량작물 생산량 — 계 + 품목별(쌀·보리쌀·밀·옥수수·콩·서류). "+NOTE,
 "keywords":["생산량","식량작물","쌀","미곡","보리쌀","보리","밀","옥수수","콩","서류","감자","고구마"],
 "source":src("농업·농촌 > Ⅳ. 식량작물 > 총괄·맥류·서류/두류/잡곡 생산량",296),
 "series":fc["prod_total"],
 "breakdown":[{"label":n,"series":s} for n,s in fc["prod_items"]],
 "related_ids":["food_crop_area","food_self_suff","cultivated_area"]}

area={
 "id":"food_crop_area","name":"식량작물 재배면적","group":"식량·자급률","unit":"천ha",
 "frequency":"연간","is_headline":False,
 "description":"식량작물 재배면적 — 계 + 품목별(쌀·보리쌀·밀·옥수수·콩·서류). "+NOTE,
 "keywords":["재배면적","면적","식량작물","쌀","미곡","보리쌀","보리","밀","옥수수","콩","서류","감자","고구마"],
 "source":src("농업·농촌 > Ⅳ. 식량작물 > 총괄·맥류·서류/두류/잡곡 재배면적",296),
 "series":fc["area_total"],
 "breakdown":[{"label":n,"series":s} for n,s in fc["area_items"]],
 "related_ids":["food_crop_production","cultivated_area","food_self_suff"]}

# 1) 기존 쌀 단독 지표 제거
REMOVE={"rice_production","rice_area"}
kept=[i for i in d["indicators"] if i["id"] not in REMOVE]
removed=[i["id"] for i in d["indicators"] if i["id"] in REMOVE]

# 2) 신규 지표 삽입 (곡물자급률 뒤에 위치)
pos=next((k for k,i in enumerate(kept) if i["id"]=="grain_self_suff"), len(kept)-1)+1
kept[pos:pos]=[prod,area]

# 3) 사라진 id를 참조하는 related_ids 정리
for i in kept:
    rid=i.get("related_ids")
    if not rid: continue
    new=[]
    for r in rid:
        if r=="rice_production": new.append("food_crop_production")
        elif r=="rice_area": new.append("food_crop_area")
        else: new.append(r)
    i["related_ids"]=list(dict.fromkeys(new))

d["indicators"]=kept
d["meta"]["status"]="v6 (식량작물 생산량·재배면적 품목별 추가, 쌀 단독지표 흡수)"
json.dump(d, open('/tmp/indicators.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)

print("제거:",removed)
print("추가: food_crop_production, food_crop_area")
print("총 지표:",len(kept))
print("잔여 rice_ 참조:",[ (i['id'],r) for i in kept for r in i.get('related_ids',[]) if r.startswith('rice_')])
