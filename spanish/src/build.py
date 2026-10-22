"""Build the Spanish app: data/*.txt -> DATA JSON inside app.html -> n5-flashcards/spanish/index.html (+ artifact copy)."""
import json, re, os
D = '/home/claude/spanish/data/'
def rows(fname):
    out = []
    for l in open(D + fname, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l.strip() or l.startswith('#'): continue
        f = l.split('|')
        while len(f) < 5: f.append('')
        if len(f) == 6:  # "…|enAlts|pic|extraEnglish" written by mistake: fold extra into English alts
            f[3] = ','.join(x for x in (f[3], f[5]) if x); f = f[:5]
        es, en, esA, enA, pic = [x.strip() for x in f[:5]]
        sp = lambda s: [x.strip() for x in s.split(',') if x.strip()]
        out.append([es, en, sp(esA), sp(enA), pic])
    return out
seen_es, seen = {}, set()
DATA = {}
for lvl in ('a1', 'a2', 'b1'):
    for kind in ('w', 'p'):
        keep = []
        for r in rows(f'{lvl}_{"words" if kind=="w" else "phrases"}.txt'):
            es = r[0].lower()
            if (es, r[1]) in seen or (es in seen_es and seen_es[es] != lvl): continue
            seen.add((es, r[1])); seen_es.setdefault(es, lvl); keep.append(r)
        DATA[lvl + kind] = keep
        print(lvl, kind, len(keep))
js = 'const DATA=' + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')) + ';'
page = open('/home/claude/spanish/app.html', encoding='utf-8').read().replace('/*DATA*/', js)
open('/home/claude/spanish/es-flashcards.html', 'w', encoding='utf-8').write(page)
head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0F1613">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Español">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
tail = '''
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}))</script>
</body>
</html>
'''
os.makedirs('/home/claude/n5-flashcards/spanish', exist_ok=True)
open('/home/claude/n5-flashcards/spanish/index.html', 'w', encoding='utf-8').write(head + page + tail)
print('total', sum(len(v) for v in DATA.values()))
