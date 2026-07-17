# -*- coding: utf-8 -*-
"""원문 PDF → 페이지 단위 검색 코퍼스(corpus.json) 생성
챗봇 RAG용. 각 청크 = 한 페이지 {p:인쇄쪽, pdf:PDF쪽, title:표제목, text:본문}
PDF쪽 = 인쇄쪽 + 4. 표지·목차(1~24쪽) 제외.
"""
import json, re, os
BASE = os.path.dirname(os.path.abspath(__file__))
pages = json.load(open('/tmp/pages.json', encoding='utf-8'))

def has_kor(s): return bool(re.search(r'[가-힣]', s))

corpus = []
for i, txt in enumerate(pages):
    pdfpage = i + 1
    if pdfpage < 25:            # 표지·이용안내·목차 제외
        continue
    printed = pdfpage - 4
    lines = [l.rstrip() for l in txt.split('\n')]
    # 제목 후보: 상단에서 한글 포함 & 숫자비율 낮은 줄 1~2개
    titles = []
    for l in lines[:8]:
        s = l.strip()
        if not s or re.fullmatch(r'\d{1,3}', s):
            continue
        ratio = sum(c.isdigit() for c in s) / max(len(s), 1)
        if has_kor(s) and ratio < 0.4:
            titles.append(s)
        if len(titles) >= 2:
            break
    title = ' '.join(titles)[:90]
    body = '\n'.join(l for l in lines if l.strip())[:2600]
    if not has_kor(body):
        continue
    corpus.append({"p": printed, "pdf": pdfpage, "title": title, "text": body})

json.dump(corpus, open('/tmp/corpus.json', 'w', encoding='utf-8'), ensure_ascii=False)
sz = os.path.getsize('/tmp/corpus.json')
print(f"코퍼스 청크: {len(corpus)}개, 크기 {sz//1024}KB")
# 샘플 검증: '1인당' 또는 '소비량' 들어간 페이지
hits = [c for c in corpus if '1인당' in c['text'] and '소비' in c['text']][:5]
for c in hits:
    print(f"  p.{c['p']} | {c['title'][:40]}")
