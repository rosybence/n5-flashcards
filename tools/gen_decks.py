"""Build the extra decks (full N5, N4, hiragana, katakana) from the open JLPT word list
(github.com/jamsinclair/open-anki-jlpt-decks, MIT licence) and print JS data blocks."""
import csv, re, json, sys
SRC = '/tmp/claude-0/src/open-anki-jlpt-decks/src/'

# ---------- kana -> Hepburn romaji ----------
B = dict(zip("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん",
  "a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa o n".split()))
B.update(dict(zip("がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉゔ",
  "ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe po a i u e o vu".split())))
Y = {'ゃ':'a','ゅ':'u','ょ':'o'}
YB = {'き':'ky','ぎ':'gy','し':'sh','じ':'j','ち':'ch','ぢ':'j','に':'ny','ひ':'hy','び':'by','ぴ':'py','み':'my','り':'ry'}
SMALL_EXT = {'ふぁ':'fa','ふぃ':'fi','ふぇ':'fe','ふぉ':'fo','てぃ':'ti','でぃ':'di','うぃ':'wi','うぇ':'we','うぉ':'wo','しぇ':'she','じぇ':'je','ちぇ':'che','ゔぁ':'va'}
def k2h(s): return ''.join(chr(ord(c)-0x60) if 'ァ'<=c<='ヶ' else c for c in s)
def romaji(kana, verb=False):
    h = k2h(kana); out = []; i = 0
    while i < len(h):
        c = h[i]; n = h[i+1] if i+1 < len(h) else ''
        if c+n in SMALL_EXT: out.append(SMALL_EXT[c+n]); i += 2; continue
        if n in Y and c in YB: out.append(YB[c]+Y[n]); i += 2; continue
        if c == 'っ':
            nxt = romaji(h[i+1:i+3])[:2] if i+1 < len(h) else ''
            out.append('t' if nxt.startswith('ch') else (nxt[:1] if nxt else '')); i += 1; continue
        if c == 'ー':
            if out and out[-1][-1] in 'aiueo': out[-1] = out[-1][:-1] + 'āīūēō'['aiueo'.index(out[-1][-1])]
            i += 1; continue
        if c == 'ん':
            out.append("n'" if n and n in 'あいうえおやゆよ' else 'n'); i += 1; continue
        out.append(B.get(c, c)); i += 1
    if len(h) > 1 and h.endswith('は') and h != 'はは': out[-1] = 'wa'
    r = ''.join(out)
    tail = ''
    if verb and r.endswith('u') and len(r) > 1 and r[-2] in 'aiueo':  # keep -ou / -uu verb endings
        tail = 'u'; r = r[:-1]
    for a, b in (('aa','ā'),('uu','ū'),('oo','ō'),('ou','ō'),('ee','ē')):
        r = r.replace(a, b)
    return r + tail

# ---------- English ----------
def senses(m):
    m = m.replace('--', ' ').strip()
    parts, depth, cur = [], 0, ''
    for ch in m:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if ch in ';,' and depth == 0: parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur)
    out = []
    for p in parts:
        p = re.sub(r'\s+', ' ', p.replace('|', '/')).strip(' .')
        if p and p not in out: out.append(p)
    return out

def clean_jp(s): return re.sub(r'^[～〜]|\s*\((する|〜を|~を)\)\s*|\s*\(〜を\)\s*', '', s).replace('～', '').replace('〜', '').strip()

def load(fname, existing):
    rows = []
    for x in csv.DictReader(open(SRC + fname)):
        exprs = [clean_jp(e) for e in x['expression'].split(';')]
        reads = [clean_jp(e) for e in x['reading'].split(';')]
        exprs = [re.sub(r'\s*\(.*?\)', '', e).strip() for e in exprs if e.strip()]
        reads = [re.sub(r'\s*\(.*?\)', '', e).strip() for e in reads if e.strip()]
        if not reads: reads = exprs[:]
        if not exprs: exprs = reads[:]
        if x['expression'] == 'いただく': exprs, reads = ['頂く'], ['いただく']
        k, kana = exprs[0], reads[0]
        if re.search(r'[一-鿿]', kana): kana, k = k, kana
        if k in existing or (k == kana and kana in existing): continue
        existing.add(k)
        sn = senses(x['meaning'])
        verb = sn[0].lower().startswith('to ')
        en = '; '.join(sn[:3]).replace('`', "'")
        alts = [s for s in sn[3:]] + [e for e in exprs[1:] + reads[1:] if e not in (k, kana)]
        alts = [a.replace(',', ' ').replace('`', "'") for a in alts if a]
        rows.append('|'.join([k, kana, romaji(kana, verb), en, ','.join(alts)]).rstrip('|'))
    return rows

def jlpt_map():
    m = {}
    for f in ('n5.csv', 'n4.csv'):
        for x in csv.DictReader(open(SRC + f)):
            sn = [a.replace(',', ' ').replace('`', "'") for a in senses(x['meaning'])]
            for e in x['expression'].split(';') + x['reading'].split(';'):
                e = re.sub(r'\s*\(.*?\)', '', clean_jp(e)).strip()
                if e and e not in m: m[e] = sn
    return m

page = open('/home/claude/n5-flashcards.html').read()
existing = set()
for name in ('RAW', 'RAW_P'):
    for l in re.search(r'const %s=`(.*?)`;' % name, page, re.S).group(1).split('\n'):
        existing.add(l.split('|')[0])
n5 = load('n5.csv', existing)
n4 = load('n4.csv', existing)

# ---------- kana decks ----------
G = "あいうえお かきくけこ さしすせそ たちつてと なにぬねの はひふへほ まみむめも やゆよ らりるれろ わをん".replace(' ', '')
D = "がぎぐげご ざじずぜぞ だぢづでど ばびぶべぼ ぱぴぷぺぽ".replace(' ', '')
YO = [a+b for a in 'きぎしじちにひびみりぴ' for b in 'ゃゅょ']
def kana_rows(kata):
    rows = []
    for ch in list(G) + list(D) + YO:
        k = ''.join(chr(ord(c)+0x60) for c in ch) if kata else ch
        r = romaji(ch)
        if ch == 'を': r = 'wo'
        if ch == 'ぢ': r = 'ji (di)'
        if ch == 'づ': r = 'zu (du)'
        other = ''.join(chr(ord(c)+0x60) for c in ch) if not kata else ch
        rows.append('|'.join([k, k, r, r, other]))
    return rows
hira, kata = kana_rows(False), kana_rows(True)
JM = jlpt_map()
cur_jl = {}
for name in ('RAW', 'RAW_P'):
    for l in re.search(r'const %s=`(.*?)`;' % name, page, re.S).group(1).split('\n'):
        f = l.split('|')
        for key in (f[0], f[1]):
            if key in JM: cur_jl[f[0]] = JM[key]; break
out = {'JL': cur_jl, 'N5X': n5, 'N4': n4, 'HIRA': hira, 'KATA': kata}
json.dump(out, open('/tmp/claude-0/decks.json', 'w'), ensure_ascii=False)
for k, v in out.items(): print(k, len(v), list(v)[:3] if isinstance(v, dict) else v[:3])
