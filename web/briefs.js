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
}
];
