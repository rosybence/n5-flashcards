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
# common place names (IPADIC keeps these in files skipped above)
for s_, r_ in {'日本':'にほん,にっぽん','東京':'とうきょう','大阪':'おおさか','京都':'きょうと','新宿':'しんじゅく','渋谷':'しぶや','横浜':'よこはま',
  '名古屋':'なごや','北海道':'ほっかいどう','沖縄':'おきなわ','九州':'きゅうしゅう','広島':'ひろしま','奈良':'なら','神戸':'こうべ','札幌':'さっぽろ',
  '福岡':'ふくおか','英国':'えいこく','米国':'べいこく','中国':'ちゅうごく','韓国':'かんこく','上野':'うえの','池袋':'いけぶくろ','銀座':'ぎんざ',
  '浅草':'あさくさ','秋葉原':'あきはばら','品川':'しながわ','富士山':'ふじさん','田中':'たなか','山田':'やまだ','花子':'はなこ','鈴木':'すずき'}.items():
    for r in r_.split(','): tab[s_].add(r)
with open(out, 'w', encoding='utf-8') as fo:
    fo.write('# kanji spelling<TAB>readings — from IPADIC (mecab-ipadic, BSD-style licence, see NOTICE in that project)\n')
    for s in sorted(tab):
        fo.write(s + '\t' + ','.join(sorted(tab[s])) + '\n')
print('surfaces', len(tab), 'bytes', os.path.getsize(out))
