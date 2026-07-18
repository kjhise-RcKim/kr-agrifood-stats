# -*- coding: utf-8 -*-
"""원문 PDF → 검색 코퍼스(corpus.json) v3
연도-행 표 + 전치형(연도가 열) 표 모두 라벨링 → RAG 정확도 향상.
PDF쪽 = 인쇄쪽 + 4. 표지·목차(1~24쪽) 제외."""
import json, re, os
pages = json.load(open('/tmp/pages.json', encoding='utf-8'))

def has_kor(s): return bool(re.search(r'[가-힣]', s))
def yconv(y): return 1900 + y if y >= 53 else 2000 + y

MERGES = [('연 도','연도'),('서 류','서류'),('기 타','기타'),('두 류','두류'),
          ('소 계','소계'),('합 계','합계'),('총 계','총계'),('맥 류','맥류'),
          ('잡 곡','잡곡'),('논 벼','논벼'),('밭 벼','밭벼'),('미 곡','미곡')]
def norm_header(line):
    for a, b in MERGES: line = line.replace(a, b)
    return line

def is_num(t):
    c = t.replace(',', '').replace('p', '')
    return bool(re.fullmatch(r'-?\d+(\.\d+)?', c))
def num(t):
    c = t.replace(',', '').replace('p', '')
    return float(c) if '.' in c else int(c)
def valtoks(s):
    out = []
    for t in s.split():
        if t in ('-', '–', '－', '·'): out.append(None)
        elif is_num(t): out.append(num(t))
        else: out.append('X')
    return out

# ── 1) 연도-행 표 라벨링 ──
def label_yearrow(lines):
    header = None
    for l in lines:
        s = norm_header(l.strip())
        if s.startswith('연도'):
            labels = s.split()[1:]
            kor = [t for t in labels if has_kor(t)]
            if len(labels) >= 2 and len(kor) >= max(2, len(labels)//2):
                header = labels; break
    if not header: return []
    out = []
    for l in lines:
        m = re.match(r'^\s*(\d{2})\s+(.*)$', l)
        if not m: continue
        y = int(m.group(1))
        if 25 <= y <= 52: continue
        vals = valtoks(m.group(2))
        if len(vals) != len(header): continue
        parts = [lab + "=" + ("결측" if v is None else ("?" if v == 'X' else str(v)))
                 for lab, v in zip(header, vals)]
        out.append(str(yconv(y)) + "년: " + ", ".join(parts))
    return out

# ── 2) 전치형(연도가 열) 표 라벨링 ──
def trailing_years(line):
    toks = line.split(); yrs = []
    for t in reversed(toks):
        c = t.replace('p', '')
        if re.fullmatch(r'\d{2}', c) and (int(c) <= 24 or int(c) >= 53): yrs.append(c)
        else: break
    return yrs[::-1]

def label_transposed(lines):
    years = None
    for l in lines:
        yrs = trailing_years(l)
        if len(yrs) >= 3:
            years = [yconv(int(t)) for t in yrs]; break
    if not years: return []
    n = len(years); out = []
    for l in lines:
        toks = l.split()
        vi = next((idx for idx, t in enumerate(toks) if is_num(t)), None)
        if vi is None or vi == 0: continue
        label = ''.join(toks[:vi])
        if not has_kor(label): continue
        vals = valtoks(' '.join(toks[vi:]))
        if len(vals) != n: continue
        parts = [str(y) + "년=" + ("결측" if v is None else ("?" if v == 'X' else str(v)))
                 for y, v in zip(years, vals)]
        out.append(label + ": " + ", ".join(parts))
    return out if len(out) >= 2 else []

corpus = []
n_yr = n_tr = 0
for i, txt in enumerate(pages):
    pdfpage = i + 1
    if pdfpage < 25: continue
    printed = pdfpage - 4
    lines = [l.rstrip() for l in txt.split('\n')]
    titles = []
    for l in lines[:8]:
        s = l.strip()
        if not s or re.fullmatch(r'\d{1,3}', s): continue
        ratio = sum(c.isdigit() for c in s) / max(len(s), 1)
        if has_kor(s) and ratio < 0.4: titles.append(s)
        if len(titles) >= 2: break
    title = ' '.join(titles)[:90]
    raw = '\n'.join(l for l in lines if l.strip())
    if not has_kor(raw): continue
    yr = label_yearrow(lines)
    tr = label_transposed(lines) if not yr else []
    if yr: n_yr += 1
    if tr: n_tr += 1
    labeled = yr or tr
    text = raw[:2600]
    if labeled:
        text = ("[표 데이터]\n" + "\n".join(labeled) + "\n\n[원문 텍스트]\n" + raw)[:3800]
    corpus.append({"p": printed, "pdf": pdfpage, "title": title, "text": text})

json.dump(corpus, open('/tmp/corpus.json', 'w', encoding='utf-8'), ensure_ascii=False)
sz = os.path.getsize('/tmp/corpus.json')
print("청크", len(corpus), "개,", sz//1024, "KB | 연도행 라벨", n_yr, "· 전치형 라벨", n_tr)
# 검증: 농림업생산액(p84=PDF88), 일본 자급률(p535=PDF539)
for c in corpus:
    if c['p'] in (84, 535):
        print("--- p." + str(c['p']), c['title'][:30], "---")
        for ln in c['text'].split('\n'):
            if ('농림업' in ln and '=' in ln) or ('식용' in ln and '=' in ln) or ('곡물' in ln and '년=' in ln):
                print("   ", ln[:110]); break
