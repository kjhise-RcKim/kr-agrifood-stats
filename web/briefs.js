/* ══════════════════════════════════════════════════════════════
   브리프 정의 — 주제별로 관련 지표를 모아 한 화면에 놓는다.

   ▸ 새 브리프 추가법: 아래 배열에 항목 하나만 늘리면 된다. 코드 수정 불필요.
   ▸ src 형식:  [지표id]            → 그 지표의 계(전체) 시계열
                [지표id, '품목명']   → 그 지표의 품목별(breakdown) 시계열
   ▸ axis: 'y'(왼쪽) / 'y2'(오른쪽). 단위가 같으면 둘 다 'y'로 두고 y2를 비운다.
   ▸ page: 근거 원문 인쇄 쪽번호.  ind: '지표 자세히 보기'로 연결할 지표 id.

   ⚠️ 원칙(변경 금지): 해석·주장 문장을 넣지 않는다.
      제목·설명은 사실 서술로만 쓴다.
      ○ "1인당 밀 소비량과 밀 자급률"
      ✕ "소비는 늘고 자급률은 떨어진 54년"
   ══════════════════════════════════════════════════════════════ */
window.BRIEFS = [
{
  id: 'wheat', icon: '🌾', name: '우리밀 브리프', short: '우리밀',
  desc: '원자료에 실린 밀 관련 수치를 한 화면에 모았습니다.',
  kpis: [
    { label: '밀 자급률 (식량자급률 기준)', src: ['food_self_suff', '밀'], unit: '%' },
    { label: '밀 재배면적',       src: ['food_crop_area', '밀'],       unit: '천ha' },
    { label: '밀 생산량',         src: ['food_crop_production', '밀'], unit: '천t' },
    { label: '1인당 밀 소비량',    src: ['rice_consumption_pc', '밀'],  unit: 'kg' }
  ],
  charts: [
    { title: '1인당 밀 소비량과 밀 자급률', cap: '왼쪽 축 kg · 오른쪽 축 %',
      page: 332, ind: 'rice_consumption_pc', y1: 'kg', y2: '%',
      series: [
        { label: '1인당 밀 소비량 (kg)', src: ['rice_consumption_pc', '밀'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '밀 자급률 (%)',       src: ['food_self_suff', '밀'],      color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '밀 재배면적과 생산량', cap: '왼쪽 축 천ha · 오른쪽 축 천t',
      page: 296, ind: 'food_crop_production', y1: '천ha', y2: '천t',
      series: [
        { label: '재배면적 (천ha)', src: ['food_crop_area', '밀'],       color: '#38d39f', fill: true, axis: 'y' },
        { label: '생산량 (천t)',    src: ['food_crop_production', '밀'], color: '#ff6b6b', axis: 'y2' }
      ] },
    { title: '1인당 소비량: 쌀과 밀', cap: 'kg',
      page: 332, ind: 'rice_consumption_pc', y1: 'kg',
      series: [
        { label: '쌀 (kg)', src: ['rice_consumption_pc', '쌀'], color: '__TOTAL__', axis: 'y' },
        { label: '밀 (kg)', src: ['rice_consumption_pc', '밀'], color: '#ffb84d', fill: true, axis: 'y' }
      ] }
  ]
},
{
  id: 'security', icon: '🛡️', name: '식량안보 브리프', short: '식량안보',
  desc: '자급률·경지·소비·농가 구조에 관한 수치를 한 화면에 모았습니다.',
  kpis: [
    { label: '식량자급률 (사료용 제외)', src: ['food_self_suff'],      unit: '%' },
    { label: '곡물자급률 (사료용 포함)', src: ['grain_self_suff'],     unit: '%' },
    { label: '경지면적',                src: ['cultivated_area'],     unit: '천ha' },
    { label: '1인당 양곡 소비량',        src: ['rice_consumption_pc'], unit: 'kg' }
  ],
  charts: [
    { title: '식량자급률과 곡물자급률', cap: '% · 두 선의 차이는 사료용 곡물의 포함 여부에서 생깁니다',
      page: 331, ind: 'food_self_suff', y1: '%',
      series: [
        { label: '식량자급률 (사료용 제외, %)', src: ['food_self_suff'],  color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '곡물자급률 (사료용 포함, %)', src: ['grain_self_suff'], color: '#ffb84d', axis: 'y' }
      ] },
    { title: '1인당 양곡 소비량과 식량자급률', cap: '왼쪽 축 kg · 오른쪽 축 %',
      page: 332, ind: 'rice_consumption_pc', y1: 'kg', y2: '%',
      series: [
        { label: '1인당 양곡 소비량 (kg)', src: ['rice_consumption_pc'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '식량자급률 (%)',        src: ['food_self_suff'],      color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '경지면적과 농림업 생산액', cap: '왼쪽 축 천ha · 오른쪽 축 십억원',
      page: 24, ind: 'cultivated_area', y1: '천ha', y2: '십억원',
      series: [
        { label: '경지면적 (천ha)',    src: ['cultivated_area'],   color: '#38d39f', fill: true, axis: 'y' },
        { label: '농림업 생산액 (십억원)', src: ['agri_output_value'], color: '#ff6b6b', axis: 'y2' }
      ] },
    { title: '농가 인구와 경영주 고령화율', cap: '왼쪽 축 천명 · 오른쪽 축 %',
      page: 62, ind: 'farm_population', y1: '천명', y2: '%',
      series: [
        { label: '농가 인구 (천명)',        src: ['farm_population'],   color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '경영주 고령화율 (%)',      src: ['farmer_aging_rate'], color: '#ff6b6b', axis: 'y2' }
      ] }
  ]
},
{
  id: 'rice', icon: '🍚', name: '쌀 수급 브리프', short: '쌀 수급',
  desc: '쌀의 자급률·재배면적·생산량·1인당 소비량과 수급실적(생산·소비·재고·도입)을 한 화면에 모았습니다.',
  kpis: [
    { label: '쌀 자급률 (식량자급률 기준)', src: ['food_self_suff', '쌀'],      unit: '%' },
    { label: '쌀 재배면적',       src: ['food_crop_area', '쌀'],       unit: '천ha' },
    { label: '쌀 생산량',         src: ['food_crop_production', '쌀'], unit: '천t' },
    { label: '1인당 쌀 소비량',    src: ['rice_consumption_pc', '쌀'],  unit: 'kg' }
  ],
  charts: [
    { title: '1인당 쌀 소비량과 쌀 자급률', cap: '왼쪽 축 kg · 오른쪽 축 %',
      page: 332, ind: 'rice_consumption_pc', y1: 'kg', y2: '%',
      series: [
        { label: '1인당 쌀 소비량 (kg)', src: ['rice_consumption_pc', '쌀'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '쌀 자급률 (%)',       src: ['food_self_suff', '쌀'],      color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '쌀 재배면적과 생산량', cap: '왼쪽 축 천ha · 오른쪽 축 천t',
      page: 296, ind: 'food_crop_area', y1: '천ha', y2: '천t',
      series: [
        { label: '재배면적 (천ha)', src: ['food_crop_area', '쌀'],       color: '#38d39f', fill: true, axis: 'y' },
        { label: '생산량 (천t)',    src: ['food_crop_production', '쌀'], color: '#ff6b6b', axis: 'y2' }
      ] },
    { title: '식량작물 생산량 중 쌀', cap: '천t · 계는 식량작물 전체(정곡 기준)입니다',
      page: 296, ind: 'food_crop_production', y1: '천t',
      series: [
        { label: '식량작물 계 (천t)', src: ['food_crop_production'],      color: '__TOTAL__', axis: 'y' },
        { label: '쌀 (천t)',         src: ['food_crop_production', '쌀'], color: '#ffb84d', fill: true, axis: 'y' }
      ] },
    { title: '쌀 생산량과 소비량', cap: '천t · 양곡년도(전년 11.1~당년 10.31) 기준',
      page: 307, ind: 'rice_supply_demand', y1: '천t',
      series: [
        { label: '생산 (천t)', src: ['rice_supply_demand', '생산'], color: '#38d39f', fill: true, axis: 'y' },
        { label: '소비 (천t)', src: ['rice_supply_demand', '소비'], color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '연말재고와 쌀 자급률', cap: '왼쪽 축 천t · 오른쪽 축 % · 양곡년도 기준',
      page: 307, ind: 'rice_supply_demand', y1: '천t', y2: '%',
      series: [
        { label: '연말재고 (천t)', src: ['rice_supply_demand', '연말재고'], color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '자급률 (%)',     src: ['rice_self_suff_grainyear'],       color: '#ffb84d', axis: 'y2' }
      ] },
    { title: '쌀 도입(수입)량과 이월량', cap: '천t · 도입은 수입량, 이월은 전년도에서 넘어온 재고',
      page: 307, ind: 'rice_supply_demand', y1: '천t',
      series: [
        { label: '도입 (천t)', src: ['rice_supply_demand', '도입'], color: '#ff6b6b', fill: true, axis: 'y' },
        { label: '이월 (천t)', src: ['rice_supply_demand', '이월'], color: '#3fa7ff', axis: 'y' }
      ] }
  ]
},
{
  id: 'livestock', icon: '🐄', name: '축산 브리프', short: '축산',
  desc: '육류 생산량·자급률과 가축 사육마릿수를 한 화면에 모았습니다.',
  kpis: [
    { label: '축산물(육류) 생산량', src: ['meat_production'],           unit: '천t' },
    { label: '축산물(육류) 자급률', src: ['livestock_self_suff'],       unit: '%' },
    { label: '돼지 사육마릿수',     src: ['livestock_heads', '돼지'],    unit: '천마리' },
    { label: '닭 사육마릿수',       src: ['livestock_heads', '닭'],      unit: '천마리' }
  ],
  charts: [
    { title: '육류 생산량과 자급률', cap: '왼쪽 축 천t · 오른쪽 축 % · 2020년부터 쇠고기·돼지고기 생산량 산출 기준이 바뀌었습니다',
      page: 378, ind: 'meat_production', y1: '천t', y2: '%',
      series: [
        { label: '육류 생산량 (천t)', src: ['meat_production'],     color: '#ff6b6b', fill: true, axis: 'y' },
        { label: '육류 자급률 (%)',   src: ['livestock_self_suff'], color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '가축 사육마릿수', cap: '왼쪽 축 천마리(한·육우·젖소·돼지) · 오른쪽 축 천마리(닭)',
      page: 372, ind: 'livestock_heads', y1: '천마리', y2: '천마리 (닭)',
      series: [
        { label: '한·육우', src: ['livestock_heads', '한·육우'], color: '#ff6b6b', axis: 'y' },
        { label: '젖소',   src: ['livestock_heads', '젖소'],   color: '#38d39f', axis: 'y' },
        { label: '돼지',   src: ['livestock_heads', '돼지'],   color: '#ffb84d', axis: 'y' },
        { label: '닭',     src: ['livestock_heads', '닭'],     color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '육류 자급률과 곡물자급률', cap: '% · 곡물자급률에는 가축이 먹는 사료용 곡물이 포함됩니다',
      page: 378, ind: 'livestock_self_suff', y1: '%',
      series: [
        { label: '육류 자급률 (%)',   src: ['livestock_self_suff'], color: '#ff6b6b', fill: true, axis: 'y' },
        { label: '곡물자급률 (%)',    src: ['grain_self_suff'],     color: '#3fa7ff', axis: 'y' }
      ] }
  ]
},
{
  id: 'trade', icon: '🌏', name: '무역 브리프', short: '무역',
  desc: '농림축산물 수출액·수입액·무역수지를 한 화면에 모았습니다. 원자료에 실린 기간은 2020년 이후입니다.',
  kpis: [
    { label: '농림축산물 수출액', src: ['agri_export'],        unit: '백만$' },
    { label: '농림축산물 수입액', src: ['agri_import'],        unit: '백만$' },
    { label: '농림축산물 무역수지', src: ['agri_trade_balance'], unit: '백만$' }
  ],
  charts: [
    { title: '농림축산물 수출액과 수입액', cap: '백만$ · 관세청 통관기준, 면세점 수출액 제외',
      page: 136, ind: 'agri_export', y1: '백만$', type: 'bar',
      series: [
        { label: '수출액 (백만$)', src: ['agri_export'], color: '#38d39f', axis: 'y' },
        { label: '수입액 (백만$)', src: ['agri_import'], color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '농림축산물 무역수지', cap: '백만$ · 수출액에서 수입액을 뺀 값입니다',
      page: 136, ind: 'agri_trade_balance', y1: '백만$', type: 'bar',
      series: [
        { label: '무역수지 (백만$)', src: ['agri_trade_balance'], color: '#3fa7ff', axis: 'y' }
      ] }
  ]
},
{
  id: 'othercrops', icon: '🌱', name: '잡곡·콩 브리프', short: '잡곡·콩',
  desc: '쌀·밀을 뺀 나머지 식량작물(보리쌀·콩·옥수수·서류)의 수치를 한 화면에 모았습니다.',
  kpis: [
    { label: '콩 자급률',    src: ['food_self_suff', '콩'],    unit: '%' },
    { label: '보리쌀 자급률', src: ['food_self_suff', '보리쌀'], unit: '%' },
    { label: '옥수수 자급률', src: ['food_self_suff', '옥수수'], unit: '%' },
    { label: '서류 자급률',   src: ['food_self_suff', '서류'],   unit: '%' }
  ],
  charts: [
    { title: '품목별 자급률', cap: '% · 식량자급률(사료용 제외) 기준',
      page: 331, ind: 'food_self_suff', y1: '%',
      series: [
        { label: '보리쌀', src: ['food_self_suff', '보리쌀'], color: '#ffb84d', axis: 'y' },
        { label: '콩',     src: ['food_self_suff', '콩'],     color: '#38d39f', axis: 'y' },
        { label: '옥수수', src: ['food_self_suff', '옥수수'], color: '#3fa7ff', axis: 'y' },
        { label: '서류',   src: ['food_self_suff', '서류'],   color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '품목별 재배면적', cap: '천ha',
      page: 296, ind: 'food_crop_area', y1: '천ha',
      series: [
        { label: '보리쌀', src: ['food_crop_area', '보리쌀'], color: '#ffb84d', axis: 'y' },
        { label: '콩',     src: ['food_crop_area', '콩'],     color: '#38d39f', axis: 'y' },
        { label: '옥수수', src: ['food_crop_area', '옥수수'], color: '#3fa7ff', axis: 'y' },
        { label: '서류',   src: ['food_crop_area', '서류'],   color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '품목별 1인당 소비량', cap: 'kg · 양곡년도 기준',
      page: 332, ind: 'rice_consumption_pc', y1: 'kg',
      series: [
        { label: '보리쌀', src: ['rice_consumption_pc', '보리쌀'], color: '#ffb84d', axis: 'y' },
        { label: '콩',     src: ['rice_consumption_pc', '콩'],     color: '#38d39f', axis: 'y' },
        { label: '옥수수', src: ['rice_consumption_pc', '옥수수'], color: '#3fa7ff', axis: 'y' },
        { label: '서류',   src: ['rice_consumption_pc', '서류'],   color: '#ff6b6b', axis: 'y' }
      ] }
  ]
},
{
  id: 'farmecon', icon: '💰', name: '농가경제 브리프', short: '농가경제',
  desc: '농가소득과 농가가 마주하는 가격 여건을 한 화면에 모았습니다.',
  kpis: [
    { label: '농가소득 (호당)',   src: ['farm_income'],       unit: '천원' },
    { label: '농가 교역조건지수',  src: ['farm_terms_trade'],  unit: '지수' },
    { label: '농림수산품 생산자물가', src: ['ppi_agri'],        unit: '지수' },
    { label: '식료품 소비자물가',   src: ['cpi_food'],          unit: '지수' }
  ],
  charts: [
    { title: '농가소득과 농가 교역조건지수', cap: '왼쪽 축 천원 · 오른쪽 축 지수(2020=100) · 교역조건은 2005년부터',
      page: 152, ind: 'farm_income', y1: '천원', y2: '지수',
      series: [
        { label: '농가소득 (천원)',   src: ['farm_income'],      color: '#38d39f', fill: true, axis: 'y' },
        { label: '농가 교역조건지수', src: ['farm_terms_trade'], color: '#ff6b6b', axis: 'y2' }
      ] },
    { title: '생산자물가와 소비자물가', cap: '지수(2020=100) · 생산자물가는 농어민이 파는 단계, 소비자물가는 사는 단계',
      page: 112, ind: 'ppi_agri', y1: '지수',
      series: [
        { label: '농림수산품 생산자물가지수', src: ['ppi_agri'], color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '식료품 소비자물가지수',    src: ['cpi_food'], color: '#ffb84d', axis: 'y' }
      ] },
    { title: '농가소득과 어가소득', cap: '천원 · 호당 · 어가소득은 2003년부터',
      page: 152, ind: 'farm_income', y1: '천원',
      series: [
        { label: '농가소득 (천원)', src: ['farm_income'],    color: '#38d39f', fill: true, axis: 'y' },
        { label: '어가소득 (천원)', src: ['fishery_income'], color: '#3fa7ff', axis: 'y' }
      ] }
  ]
},
{
  id: 'ruralpop', icon: '👥', name: '농촌 인구구조 브리프', short: '농촌 인구',
  desc: '농가 호수·인구와 고령화, 농림어업의 경제 비중을 한 화면에 모았습니다.',
  kpis: [
    { label: '농가 호수',        src: ['farm_households'],   unit: '천호' },
    { label: '농가 인구',        src: ['farm_population'],   unit: '천명' },
    { label: '경영주 고령화율',   src: ['farmer_aging_rate'], unit: '%' },
    { label: '농림어업 GDP 비중', src: ['agri_gdp_share'],    unit: '%' }
  ],
  charts: [
    { title: '농가 호수와 농가 인구', cap: '왼쪽 축 천호 · 오른쪽 축 천명',
      page: 62, ind: 'farm_population', y1: '천호', y2: '천명',
      series: [
        { label: '농가 호수 (천호)', src: ['farm_households'], color: '#38d39f', fill: true, axis: 'y' },
        { label: '농가 인구 (천명)', src: ['farm_population'], color: '#3fa7ff', axis: 'y2' }
      ] },
    { title: '경영주 고령화율과 농림어업 GDP 비중', cap: '% · 고령화율은 농가 경영주(대표자) 기준',
      page: 52, ind: 'farmer_aging_rate', y1: '%',
      series: [
        { label: '경영주 고령화율 (%)',   src: ['farmer_aging_rate'], color: '#ff6b6b', fill: true, axis: 'y' },
        { label: '농림어업 GDP 비중 (%)', src: ['agri_gdp_share'],    color: '#3fa7ff', axis: 'y' }
      ] },
    { title: '농가 인구와 경지면적', cap: '왼쪽 축 천명 · 오른쪽 축 천ha',
      page: 24, ind: 'cultivated_area', y1: '천명', y2: '천ha',
      series: [
        { label: '농가 인구 (천명)', src: ['farm_population'], color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '경지면적 (천ha)',  src: ['cultivated_area'], color: '#38d39f', axis: 'y2' }
      ] }
  ]
},
{
  id: 'worldgrain', icon: '🌍', name: '세계 곡물 생산 브리프', short: '세계 곡물',
  desc: 'FAO 통계 기준 주요국의 밀·옥수수·콩 생산량을 한 화면에 모았습니다. 원문 표에 한국은 포함돼 있지 않습니다.',
  kpis: [
    { label: '미국 밀 생산량',    src: ['world_wheat_production', '미국'],     unit: '백만t' },
    { label: '미국 옥수수 생산량', src: ['world_maize_production', '미국'],     unit: '백만t' },
    { label: '미국 콩 생산량',    src: ['world_soybean_production', '미국'],   unit: '백만t' },
    { label: '한국 밀 생산량',    src: ['food_crop_production', '밀'],         unit: '천t' }
  ],
  charts: [
    { title: '주요국 밀 생산량', cap: '백만t · FAO통계 기준',
      page: 320, ind: 'world_wheat_production', y1: '백만t',
      series: [
        { label: '캐나다',     src: ['world_wheat_production', '캐나다'],     color: '#ff6b6b', axis: 'y' },
        { label: '미국',       src: ['world_wheat_production', '미국'],       color: '#3fa7ff', axis: 'y' },
        { label: '프랑스',     src: ['world_wheat_production', '프랑스'],     color: '#38d39f', axis: 'y' },
        { label: '아르헨티나', src: ['world_wheat_production', '아르헨티나'], color: '#ffb84d', axis: 'y' },
        { label: '호주',       src: ['world_wheat_production', '호주'],       color: '#c78bff', axis: 'y' }
      ] },
    { title: '주요국 옥수수 생산량', cap: '백만t · FAO통계 기준',
      page: 326, ind: 'world_maize_production', y1: '백만t',
      series: [
        { label: '미국',       src: ['world_maize_production', '미국'],       color: '#3fa7ff', axis: 'y' },
        { label: '브라질',     src: ['world_maize_production', '브라질'],     color: '#38d39f', axis: 'y' },
        { label: '아르헨티나', src: ['world_maize_production', '아르헨티나'], color: '#ffb84d', axis: 'y' },
        { label: '인도',       src: ['world_maize_production', '인도'],       color: '#ff6b6b', axis: 'y' },
        { label: '프랑스',     src: ['world_maize_production', '프랑스'],     color: '#c78bff', axis: 'y' }
      ] },
    { title: '주요국 콩(대두) 생산량', cap: '백만t · FAO통계 기준',
      page: 327, ind: 'world_soybean_production', y1: '백만t',
      series: [
        { label: '미국',       src: ['world_soybean_production', '미국'],       color: '#3fa7ff', axis: 'y' },
        { label: '아르헨티나', src: ['world_soybean_production', '아르헨티나'], color: '#ffb84d', axis: 'y' },
        { label: '인도',       src: ['world_soybean_production', '인도'],       color: '#ff6b6b', axis: 'y' },
        { label: '인도네시아', src: ['world_soybean_production', '인도네시아'], color: '#38d39f', axis: 'y' }
      ] },
    { title: '한국의 밀 생산량', cap: '천t · 위 그래프들과 단위가 다릅니다(백만t 아님)',
      page: 296, ind: 'food_crop_production', y1: '천t',
      series: [
        { label: '한국 밀 생산량 (천t)', src: ['food_crop_production', '밀'], color: '#ffb84d', fill: true, axis: 'y' }
      ] }
  ]
},
{
  id: 'nutrition', icon: '🍱', name: '국민 영양 브리프', short: '국민 영양',
  desc: '국민 한 사람이 하루에 공급받는 열량과 그 공급원, 단백질·지방질 공급량을 한 화면에 모았습니다.',
  kpis: [
    { label: '1인 1일당 공급에너지', src: ['energy_supply_pc'],           unit: 'kcal' },
    { label: '곡류에서 오는 열량',    src: ['energy_supply_pc', '곡류'],   unit: 'kcal' },
    { label: '쌀에서 오는 열량',      src: ['energy_supply_pc', '쌀'],     unit: 'kcal' },
    { label: '밀가루에서 오는 열량',   src: ['energy_supply_pc', '밀가루'], unit: 'kcal' }
  ],
  charts: [
    { title: '1인 1일당 공급에너지와 곡류', cap: 'kcal · 계는 모든 식품군의 합이며 곡류는 그중 일부입니다',
      page: 494, ind: 'energy_supply_pc', y1: 'kcal',
      series: [
        { label: '계 (kcal)',  src: ['energy_supply_pc'],         color: '__TOTAL__', axis: 'y' },
        { label: '곡류 (kcal)', src: ['energy_supply_pc', '곡류'], color: '#ffb84d', fill: true, axis: 'y' }
      ] },
    { title: '곡류 안에서: 쌀과 밀가루', cap: 'kcal · 곡류에는 쌀·밀가루·보리·기타가 포함됩니다',
      page: 494, ind: 'energy_supply_pc', y1: 'kcal',
      series: [
        { label: '쌀 (kcal)',   src: ['energy_supply_pc', '쌀'],    color: '__TOTAL__', axis: 'y' },
        { label: '밀가루 (kcal)', src: ['energy_supply_pc', '밀가루'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '보리 (kcal)',  src: ['energy_supply_pc', '보리'],  color: '#38d39f', axis: 'y' }
      ] },
    { title: '단백질과 지방질 공급량', cap: 'g · 1인 1일당 · 2015년부터 식품성분표 개정으로 기준이 바뀌었습니다',
      page: 493, ind: 'nutrient_supply_pc', y1: 'g',
      series: [
        { label: '단백질 (g)', src: ['nutrient_supply_pc'],         color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '지방질 (g)', src: ['nutrient_supply_pc', '지방질'], color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '설탕류·두류·서류에서 오는 열량', cap: 'kcal · 1인 1일당',
      page: 494, ind: 'energy_supply_pc', y1: 'kcal',
      series: [
        { label: '설탕류 (kcal)', src: ['energy_supply_pc', '설탕류'], color: '#ffb84d', axis: 'y' },
        { label: '두류 (kcal)',   src: ['energy_supply_pc', '두류'],   color: '#38d39f', axis: 'y' },
        { label: '서류 (kcal)',   src: ['energy_supply_pc', '서류'],   color: '#ff6b6b', axis: 'y' }
      ] }
  ]
},
{
  id: 'cropecon', icon: '🌾', name: '작물 생산비·소득 브리프', short: '생산비·소득',
  desc: '논벼·겉보리·쌀보리·콩의 10a(300평)당 총수입·생산비·소득·순수익을 한 화면에 모았습니다. 물가를 반영하지 않은 그해 금액입니다.',
  kpis: [
    { label: '논벼 10a당 소득',   src: ['crop_income_10a', '논벼'],   unit: '원' },
    { label: '콩 10a당 소득',     src: ['crop_income_10a', '콩'],     unit: '원' },
    { label: '겉보리 10a당 소득',  src: ['crop_income_10a', '겉보리'], unit: '원' },
    { label: '쌀보리 10a당 소득',  src: ['crop_income_10a', '쌀보리'], unit: '원' }
  ],
  charts: [
    { title: '작물별 10a당 소득', cap: '원/10a · 소득 = 총수입 − 경영비 · 콩은 2014년부터',
      page: 180, ind: 'crop_income_10a', y1: '원/10a',
      series: [
        { label: '논벼',   src: ['crop_income_10a', '논벼'],   color: '__TOTAL__', axis: 'y' },
        { label: '콩',     src: ['crop_income_10a', '콩'],     color: '#38d39f', axis: 'y' },
        { label: '겉보리', src: ['crop_income_10a', '겉보리'], color: '#ffb84d', axis: 'y' },
        { label: '쌀보리', src: ['crop_income_10a', '쌀보리'], color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '작물별 10a당 순수익', cap: '원/10a · 순수익 = 총수입 − 생산비 · 자기 노동비와 토지용역비까지 뺀 값이라 음수가 될 수 있습니다',
      page: 180, ind: 'crop_netprofit_10a', y1: '원/10a',
      series: [
        { label: '논벼',   src: ['crop_netprofit_10a', '논벼'],   color: '__TOTAL__', axis: 'y' },
        { label: '콩',     src: ['crop_netprofit_10a', '콩'],     color: '#38d39f', axis: 'y' },
        { label: '겉보리', src: ['crop_netprofit_10a', '겉보리'], color: '#ffb84d', axis: 'y' },
        { label: '쌀보리', src: ['crop_netprofit_10a', '쌀보리'], color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '논벼: 총수입과 생산비', cap: '원/10a',
      page: 180, ind: 'crop_revenue_10a', y1: '원/10a',
      series: [
        { label: '총수입', src: ['crop_revenue_10a', '논벼'], color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '생산비', src: ['crop_cost_10a', '논벼'],    color: '#ff6b6b', axis: 'y' }
      ] },
    { title: '겉보리: 총수입과 생산비', cap: '원/10a',
      page: 181, ind: 'crop_revenue_10a', y1: '원/10a',
      series: [
        { label: '총수입', src: ['crop_revenue_10a', '겉보리'], color: '#3fa7ff', fill: true, axis: 'y' },
        { label: '생산비', src: ['crop_cost_10a', '겉보리'],    color: '#ff6b6b', axis: 'y' }
      ] }
  ]
},
{
  id: 'korjpn', icon: '🇯🇵', name: '한일 비교 브리프', short: '한일 비교',
  desc: '한국과 일본의 자급률·1인당 소비량을 나란히 놓았습니다. 두 나라의 조사 주체와 산출 방식이 달라 단순 비교에는 주의가 필요합니다.',
  kpis: [
    { label: '한국 밀 자급률',   src: ['food_self_suff', '밀'],       unit: '%' },
    { label: '일본 밀 자급률',   src: ['japan_agri', '밀(소맥)'],      unit: '%' },
    { label: '한국 곡물자급률',  src: ['grain_self_suff'],            unit: '%' },
    { label: '일본 곡물자급률',  src: ['japan_agri'],                 unit: '%' }
  ],
  charts: [
    { title: '밀 자급률: 한국과 일본', cap: '% · 한국은 식량자급률 기준, 일본은 농림수산성 기준',
      page: 535, ind: 'japan_agri', y1: '%',
      series: [
        { label: '한국 (%)', src: ['food_self_suff', '밀'],  color: '#ffb84d', fill: true, axis: 'y' },
        { label: '일본 (%)', src: ['japan_agri', '밀(소맥)'], color: '#3fa7ff', axis: 'y' }
      ] },
    { title: '곡물자급률: 한국과 일본', cap: '% · 둘 다 사료용을 포함한 기준',
      page: 535, ind: 'japan_agri', y1: '%',
      series: [
        { label: '한국 (%)', src: ['grain_self_suff'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '일본 (%)', src: ['japan_agri'],      color: '#3fa7ff', axis: 'y' }
      ] },
    { title: '쌀 자급률: 한국과 일본', cap: '%',
      page: 535, ind: 'japan_agri', y1: '%',
      series: [
        { label: '한국 (%)', src: ['food_self_suff', '쌀'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '일본 (%)', src: ['japan_agri', '쌀'],     color: '#3fa7ff', axis: 'y' }
      ] },
    { title: '1인당 쌀 소비량: 한국과 일본', cap: 'kg · 한국은 양곡년도 기준, 일본은 연간 기준',
      page: 534, ind: 'japan_consumption_pc', y1: 'kg',
      series: [
        { label: '한국 (kg)', src: ['rice_consumption_pc', '쌀'], color: '#ffb84d', fill: true, axis: 'y' },
        { label: '일본 (kg)', src: ['japan_consumption_pc'],      color: '#3fa7ff', axis: 'y' }
      ] },
    { title: '1인당 밀 소비량: 한국과 일본', cap: 'kg',
      page: 534, ind: 'japan_consumption_pc', y1: 'kg',
      series: [
        { label: '한국 (kg)', src: ['rice_consumption_pc', '밀'],   color: '#ffb84d', fill: true, axis: 'y' },
        { label: '일본 (kg)', src: ['japan_consumption_pc', '밀'],  color: '#3fa7ff', axis: 'y' }
      ] }
  ]
}
];
