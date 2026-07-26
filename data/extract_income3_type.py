# -*- coding: utf-8 -*-
"""농가소득 3단계: 영농형태별 농가소득 (p.160+161, 두 쪽 매트릭스)
  p.160 왼쪽: 연도 | 농가소득 논벼 과수 채소
  p.161 오른쪽(연도없음): 특작 화훼 전작 축산 기타
  두 쪽 18행(1995~2024) 인덱스 정렬. 단위 천원. '-'는 결측.
실행: python3 data/extract_income3_type.py
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


left = []   # (year, [계, 논벼, 과수, 채소])
for ln in page(160).split('\n'):
    if not re.match(r'^\s*\d{2}\s', ln):
        continue
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 5 or not all(re.fullmatch(r'-?[\d,]+(\.\d+)?|-', t) for t in toks):
        continue
    y = int(toks[0])
    if 25 <= y <= 52:
        continue
    left.append((yy(y), [toN(t) for t in toks[1:]]))

right = []  # [특작, 화훼, 전작, 축산, 기타]
for ln in page(161).split('\n'):
    toks = [t for t in ln.split() if not re.search(r'[가-힣]', t)]
    if len(toks) != 5 or not all(re.fullmatch(r'-?[\d,]+(\.\d+)?|-', t) for t in toks):
        continue
    right.append([toN(t) for t in toks])

assert len(left) == len(right) == 18, "행수 불일치 L=%d R=%d" % (len(left), len(right))

LABELS = ["논벼", "과수", "채소", "특작", "화훼", "전작", "축산", "기타"]


def ser_total():
    return [{"year": y, "value": lv[0]} for y, lv in left]


def ser_item(k):
    """k: 0논벼 1과수 2채소 (왼쪽 lv[1..3]) / 3특작 4화훼 5전작 6축산 7기타 (오른쪽)"""
    out = []
    for i, (y, lv) in enumerate(left):
        v = lv[1 + k] if k < 3 else right[i][k - 3]
        out.append({"year": y, "value": v})
    return out


ind = {
    "id": "farm_income_by_type", "name": "영농형태별 농가소득", "group": "농가경제", "unit": "천원",
    "frequency": "연간", "is_headline": False, "brief_weight": 1,
    "description": "영농형태별 농가 1호당 소득. 계(전체 평균) + 형태별(논벼·과수·채소·특작·화훼·전작·축산·기타)",
    "keywords": ["농가소득", "영농형태", "논벼", "과수", "채소", "축산"],
    "source": {"publication": "농림축산식품 주요통계 2025",
               "section": "기본통계 Ⅶ.농가경제 5.영농형태별 농가소득",
               "page": 160, "org": "농림축산식품부", "license": "공공누리 제1유형(출처표시)"},
    "series": ser_total(), "series_label": "전체 평균",
    "breakdown": [{"label": LABELS[k], "series": ser_item(k)} for k in range(8)],
    "related_ids": ["farm_income", "farm_income_source", "farm_income_by_size"],
    "tip": "주로 어떤 농사를 짓는지(영농형태)별 농가 1호당 연간 소득입니다(천원). "
           "계는 전체 농가 평균이며, 원자료에 1995년부터 집계돼 그 이전은 없습니다. (p.160~161)"
}

json.dump(ind, open('/tmp/income3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print("=== 영농형태별 농가소득 (천원) — 2024 ===")
li = 17
print("계(평균) %s" % format(left[li][1][0], ','))
for k in range(8):
    v = ser_item(k)[li]["value"]
    print("   · %-4s %s" % (LABELS[k], format(v, ',') if v is not None else '-'))
