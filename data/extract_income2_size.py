# -*- coding: utf-8 -*-
"""농가소득 2단계: 경지규모별 농가소득 (p.156+157, 두 쪽 매트릭스)
  p.156 왼쪽: 연도 | 농가소득 0.5미만 0.5~1.0 1.0~1.5
  p.157 오른쪽(연도없음): 1.5~2.0 2.0~3.0 3.0~5.0 5.0~7.0 7.0~10.0 10.0이상
  두 쪽 23행(1970~2024) 인덱스 정렬. 단위 천원. '-'는 결측(대규모 구간 초기연도).
실행: python3 data/extract_income2_size.py
"""
import json, re, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '2025 농림축산식품 주요통계.pdf')


def page(printed):
    return subprocess.run(['pdftotext', '-layout', '-f', str(printed + 4), '-l', str(printed + 4), PDF, '-'],
                          capture_output=True, text=True).stdout


def yy(y):
    return 1900 + y if y >= 53 else 2000 + y


def toN(t):
    c = t.replace(',', '')
    return int(c) if re.fullmatch(r'-?\d+', c) else (float(c) if re.fullmatch(r'-?\d+\.\d+', c) else None)


left = []   # (year, [계, 0.5미만, 0.5~1.0, 1.0~1.5])
for ln in page(156).split('\n'):
    if not re.match(r'^\s*\d{2}\s', ln):
        continue
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 5 or not all(re.fullmatch(r'-?[\d,]+(\.\d+)?|-', t) for t in toks):
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    left.append((yy(y), [toN(t) for t in toks[1:]]))

right = []  # [1.5~2.0, 2.0~3.0, 3.0~5.0, 5.0~7.0, 7.0~10.0, 10.0이상]
for ln in page(157).split('\n'):
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 6 or not all(re.fullmatch(r'-?[\d,]+(\.\d+)?|-', t) for t in toks):
        continue
    right.append([toN(t) for t in toks])

assert len(left) == len(right) == 23, "행수 불일치 L=%d R=%d" % (len(left), len(right))

LABELS = ["0.5ha 미만", "0.5~1.0ha", "1.0~1.5ha", "1.5~2.0ha", "2.0~3.0ha",
          "3.0~5.0ha", "5.0~7.0ha", "7.0~10.0ha", "10.0ha 이상"]


def ser_total():
    return [{"year": y, "value": lv[0]} for y, lv in left]


def ser_item(k):
    """k: 0..8 규모구간 인덱스. 0~2는 왼쪽(lv[1..3]), 3~8은 오른쪽(right[i][0..5])"""
    out = []
    for i, (y, lv) in enumerate(left):
        v = lv[1 + k] if k < 3 else right[i][k - 3]
        out.append({"year": y, "value": v})
    return out


ind = {
    "id": "farm_income_by_size", "name": "경지규모별 농가소득", "group": "농가경제", "unit": "천원",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "경지규모별 농가 1호당 소득. 계(농가소득 평균) + 규모 구간별(0.5ha 미만~10ha 이상)",
    "keywords": ["농가소득", "경지규모", "규모", "대농", "소농"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "기본통계 Ⅶ.농가경제 3.경지규모별 농가소득",
               "page": 156, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser_total(), "series_label": "전체 평균",
    "breakdown": [{"label": LABELS[k], "series": ser_item(k)} for k in range(9)],
    "related_ids": ["farm_income", "farm_income_source", "farm_income_by_type"],
    "tip": "경지규모(농가가 부치는 땅의 넓이)별 농가 1호당 연간 소득입니다(천원). "
           "계는 전체 농가 평균입니다. 3.0ha 이상 큰 규모 구간은 표본이 적어 초기 연도에는 집계되지 않아 결측입니다. (p.156~157)"
}

json.dump(ind, open('/tmp/income2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 경지규모별 농가소득 (천원) — 2024 ===")
li = 22
print("계(평균) %s" % format(left[li][1][0], ','))
for k in range(9):
    v = ser_item(k)[li]["value"]
    print("   · %-11s %s" % (LABELS[k], format(v, ',') if v is not None else '-'))
