# -*- coding: utf-8 -*-
"""원문 PDF → 페이지 단위 검색 코퍼스(corpus.json) v2: 연도-행 표 라벨링"""
import json, re, os
pages = json.load(open('/tmp/pages.json', encoding='utf-8'))

def has_kor(s): return bool(re.search(r'[가-힣]', s))

MERGES = [('연 도','연도'),('서 류','서류'),('기 타','기타'),('두 류','두류'),
          ('소 계','소계'),('합 계','합계'),('총 계','총계'),('맥 류','맥류'),
          ('잡 곡','잡곡'),('논 벼','논벼'),('밭 벼','밭벼'),('미 곡','미곡')]

def norm_header(line):
    for a, b in MERGES: line = line.replace(a, b)
    return line

def valtoks(s):
    out = []
    for t in s.split():
        if t in ('-', '–', '－', '·'): out.append(None); continue
        c = t.replace(',', '').replace('p', '')
        out.append(float(c) if re.fullmatch(r'-?\d+(\.\d+)?', c) else 'X')
    return out

def label_table(lines):
    header_labels = None
    for l in lines:
        s = norm_header(l.strip())
        if s.startswith('연도'):
            labels = s.split()[1:]
            koreanish = [t for t in labels if has_kor(t)]
            if len(labels) >= 2 and len(koreanish) >= max(2, len(labels)//2):
                header_labels = labels
                break
    if not header_labels:
        return []
    out = []
    for l in lines:
        m = re.match(r'^\s*(\d{2})\s+(.*)$', l)
        if not m: continue
        y = int(m.group(1))
        if 25 <= y <= 52: continue
        year = 1900 + y if y >= 53 else 2000 + y
        vals = valtoks(m.group(2))
        if len(vals) != len(header_labels):
            continue
        parts = []
        for lab, v in zip(header_labels, vals):
            if v is None: parts.append(lab + "=결측")
            elif v == 'X': parts.append(lab + "=?")
            else: parts.append(lab + "=" + str(v))
        out.append(str(year) + "년: " + ", ".join(parts))
    return out

corpus = []
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
    labeled = label_table(lines)
    text = raw[:2600]
    if labeled:
        text = ("[표 데이터]\n" + "\n".join(labeled) + "\n\n[원문 텍스트]\n" + raw)[:3600]
    corpus.append({"p": printed, "pdf": pdfpage, "title": title, "text": text})

json.dump(corpus, open('/tmp/corpus.json', 'w', encoding='utf-8'), ensure_ascii=False)
sz = os.path.getsize('/tmp/corpus.json')
n_lab = sum(1 for c in corpus if '[표 데이터]' in c['text'])
print("청크", len(corpus), "개,", sz//1024, "KB, 라벨링된 표", n_lab, "개")
for c in corpus:
    if c['p'] == 332:
        for ln in c['text'].split('\n'):
            if ln.startswith('2023년') or ln.startswith('2024년'):
                print("  검증 p332:", ln[:90])
