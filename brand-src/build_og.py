# -*- coding: utf-8 -*-
import cairosvg

INK="#101713"; PANEL="#19221C"; BORDER="rgba(255,255,255,0.07)"
PAPER="#F7F8F5"; MUTED="#94A099"
WHEAT="#C9962E"; WSOFT="#E8C87A"; GREEN="#1B6B4A"; ACCENT="#4FB286"; BLUE="#4A7FB5"
SERIF="Noto Serif CJK KR"; SANS="Noto Sans CJK KR"

# 실제 밀 자급률 시계열 (food_self_suff · 밀)
wheat=[(1970,15.9),(1975,5.8),(1980,4.8),(1985,0.5),(1990,0.05),(1995,0.47),
(2000,0.1),(2005,0.4),(2010,1.7),(2011,1.9),(2012,1.7),(2013,0.9),(2014,1.1),
(2015,1.2),(2016,1.8),(2017,1.7),(2018,1.2),(2019,0.7),(2020,0.8),(2021,1.1),
(2022,1.3),(2023,2.0),(2024,1.5)]

# ---- 라인 차트 좌표 (패널 P1) ----
PX,PY,PW,PH=64,436,624,164
x0,x1=PX+26,PX+PW-22
y0,yb=PY+52,PY+PH-26      # y0=val16(top), yb=val0(bottom)
vmax=16.0
def sx(yr): return x0+(yr-1970)/54.0*(x1-x0)
def sy(v):  return yb-(min(v,vmax)/vmax)*(yb-y0)
line=" ".join(("M" if i==0 else "L")+f"{sx(yr):.1f},{sy(v):.1f}" for i,(yr,v) in enumerate(wheat))
area=f"M{sx(wheat[0][0]):.1f},{yb:.1f} "+" ".join(f"L{sx(yr):.1f},{sy(v):.1f}" for yr,v in wheat)+f" L{sx(wheat[-1][0]):.1f},{yb:.1f} Z"
dots="".join(f'<circle cx="{sx(yr):.1f}" cy="{sy(v):.1f}" r="3.4" fill="{WHEAT}"/>' for yr,v in [wheat[0],wheat[-1]])

# 밀 이삭 마크 (상세형) — translate/scale
def mark(cx,cy,s):
    return (f'<g transform="translate({cx} {cy}) scale({s}) translate(-12 -12)" stroke-linecap="round">'
    f'<path d="M12 21V8" stroke="{WHEAT}" stroke-width="1.8"/>'
    f'<path d="M12 8c0-2.5 1.8-4.5 4-5-0 2.5-1.8 4.5-4 5Z" fill="{WHEAT}"/>'
    f'<path d="M12 8c0-2.5-1.8-4.5-4-5 0 2.5 1.8 4.5 4 5Z" fill="{GREEN}"/>'
    f'<path d="M12 13c0-2.2 1.6-4 3.6-4.4 0 2.2-1.6 4-3.6 4.4Z" fill="{WHEAT}"/>'
    f'<path d="M12 13c0-2.2-1.6-4-3.6-4.4 0 2.2 1.6 4 3.6 4.4Z" fill="{GREEN}"/>'
    f'<path d="M12 17.5c0-1.9 1.4-3.5 3.1-3.9 0 1.9-1.4 3.5-3.1 3.9Z" fill="{WHEAT}"/>'
    f'<path d="M12 17.5c0-1.9-1.4-3.5-3.1-3.9 0 1.9 1.4 3.5 3.1 3.9Z" fill="{GREEN}"/></g>')

# KPI 패널 P2
KX,KY,KW,KH=712,436,424,164
kpis=[("식량자급률","47.9","%"),("1인당 쌀 소비","55.8","kg"),("수록 지표","56","개")]
krows=""
for i,(lab,num,suf) in enumerate(kpis):
    ry=KY+40+i*40
    krows+=(f'<text x="{KX+26}" y="{ry}" font-family="{SANS}" font-size="19" fill="{MUTED}">{lab}</text>'
            f'<text x="{KX+KW-24}" y="{ry}" font-family="{SANS}" font-weight="700" font-size="27" fill="{PAPER}" text-anchor="end">'
            f'<tspan fill="{WHEAT}">{num}</tspan> <tspan font-size="16" fill="{MUTED}">{suf}</tspan></text>')

svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs>
 <radialGradient id="g1" cx="50%" cy="112%" r="62%"><stop offset="0%" stop-color="{WHEAT}" stop-opacity="0.16"/><stop offset="60%" stop-color="{WHEAT}" stop-opacity="0"/></radialGradient>
 <radialGradient id="g2" cx="84%" cy="-8%" r="60%"><stop offset="0%" stop-color="{GREEN}" stop-opacity="0.30"/><stop offset="62%" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
 <linearGradient id="wf" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{WHEAT}" stop-opacity="0.28"/><stop offset="100%" stop-color="{WHEAT}" stop-opacity="0"/></linearGradient>
</defs>
<rect width="1200" height="630" fill="{INK}"/>
<rect width="1200" height="630" fill="url(#g1)"/>
<rect width="1200" height="630" fill="url(#g2)"/>

<!-- 헤더 -->
{mark(86,64,1.7)}
<text x="118" y="72" font-family="{SANS}" font-weight="600" font-size="25" fill="{PAPER}">농식품 주요통계 대시보드</text>
<text x="1136" y="70" font-family="{SANS}" font-size="17" fill="{MUTED}" text-anchor="end">공공누리 제1유형 · 출처표시</text>

<!-- 히어로 타이틀 -->
<rect x="64" y="150" width="7" height="168" rx="3" fill="{WHEAT}"/>
<text x="92" y="212" font-family="{SERIF}" font-weight="700" font-size="70" fill="{PAPER}">우리 농업, 지금</text>
<text x="92" y="292" font-family="{SERIF}" font-weight="700" font-size="70" fill="{PAPER}">어떤 <tspan fill="{WSOFT}">모습</tspan>일까요?</text>

<!-- 서브 -->
<text x="94" y="344" font-family="{SANS}" font-size="24" fill="{MUTED}">농림축산식품부 『농림축산식품 주요통계 2025』 · 581쪽</text>
<text x="94" y="380" font-family="{SANS}" font-size="24" fill="{MUTED}">숫자는 원자료 그대로 · 대시보드 · 검색 · AI 분석</text>
<text x="94" y="416" font-family="{SANS}" font-weight="600" font-size="24" fill="{ACCENT}">kr-agrifood-stats.vercel.app</text>

<!-- 패널1: 밀 자급률 라인 -->
<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
<text x="{PX+26}" y="{PY+32}" font-family="{SANS}" font-weight="600" font-size="18" fill="{PAPER}">밀 자급률 · 1970 → 2024</text>
<text x="{PX+PW-24}" y="{PY+32}" font-family="{SANS}" font-size="15" fill="{MUTED}" text-anchor="end">%</text>
<path d="{area}" fill="url(#wf)"/>
<path d="{line}" fill="none" stroke="{WHEAT}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>
{dots}
<text x="{sx(1970):.0f}" y="{yb+18:.0f}" font-family="{SANS}" font-size="14" fill="{MUTED}">15.9%</text>
<text x="{sx(2024):.0f}" y="{sy(1.5)-12:.0f}" font-family="{SANS}" font-size="14" fill="{WSOFT}" text-anchor="end">1.5%</text>

<!-- 패널2: KPI -->
<rect x="{KX}" y="{KY}" width="{KW}" height="{KH}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
{krows}
<text x="{KX+26}" y="{KY+KH-18}" font-family="{SANS}" font-size="14" fill="{MUTED}">원문 581쪽 · 공공 데이터</text>
<text x="{KX+KW-24}" y="{KY+KH-18}" font-family="{SANS}" font-size="14" fill="{MUTED}" text-anchor="end">2024년 기준 (잠정 포함)</text>
</svg>'''

open("/tmp/og.svg","w",encoding="utf-8").write(svg)
cairosvg.svg2png(url="/tmp/og.svg", write_to="/tmp/og_new.png", output_width=1200, output_height=630)
print("OG rendered")
