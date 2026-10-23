"""Build jp/yomi.txt: kanji spelling -> kana readings, from the IPADIC dictionary (mecab-ipadic CSVs, EUC-JP).
Lets the Japanese app check whether what the phone wrote (in kanji) *sounds* like the answer.
Usage: python3 build_yomi.py /path/to/mecab-ipadic /path/to/out/yomi.txt"""
import glob, re, sys, collections, os
src, out = sys.argv[1], sys.argv[2]
SKIP = {'Noun.name.csv', 'Noun.org.csv', 'Noun.place.csv', 'Noun.proper.csv', 'Symbol.csv'}
K = re.compile(r'[㐀-鿿々〆ヵヶ]')
hira = lambda s: ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
tab = collections.defaultdict(set)
for f in glob.glob(os.path.join(src, '*.csv')):
    if os.path.basename(f) in SKIP: continue
    for l in open(f, encoding='euc-jp', errors='ignore'):
        c = l.rstrip('\n').split(',')
        if len(c) < 12: continue
        s, rd = c[0], c[11]
        if not K.search(s) or rd == '*' or len(s) > 8: continue
        tab[s].add(hira(rd))
with open(out, 'w', encoding='utf-8') as fo:
    fo.write('# kanji spelling<TAB>readings — from IPADIC (mecab-ipadic, BSD-style licence, see NOTICE in that project)\n')
    for s in sorted(tab):
        fo.write(s + '\t' + ','.join(sorted(tab[s])) + '\n')
print('surfaces', len(tab), 'bytes', os.path.getsize(out))
