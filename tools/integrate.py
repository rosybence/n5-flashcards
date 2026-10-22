import json, re
p='/home/claude/n5-flashcards.html'; s=open(p).read()
d=json.load(open('/tmp/claude-0/decks.json'))
def blk(name, rows):
    body='\n'.join(rows).replace('\\','\\\\').replace('`',"'").replace('${','$ {')
    return 'const %s=`%s`;\n' % (name, body)
data=blk('RAW_N5X',d['N5X'])+blk('RAW_N4',d['N4'])+blk('RAW_HIRA',d['HIRA'])+blk('RAW_KATA',d['KATA'])+'const JL='+json.dumps(d['JL'],ensure_ascii=False)+';\n'
# replace any previous generated data
s=re.sub(r'const RAW_N5X=`.*?`;\nconst RAW_N4=`.*?`;\nconst RAW_HIRA=`.*?`;\nconst RAW_KATA=`.*?`;\nconst JL=.*?;\n','',s,flags=re.S)
s=s.replace('const READ=',data+'const READ=',1)
R=[
("const parse=(raw,type)=>raw.trim().split('\\n').map(l=>{const [k,kana,r,en,alts,pic]=l.split('|');const al=alts?alts.split(',').filter(Boolean):[];return{id:k+'/'+kana,k,kana,r,en,type,pic:pic||PICS[k]||'',alts:al.map(a=>a.replace(/^~/,'')),casual:new Set(al.filter(a=>a[0]==='~').map(a=>a.slice(1)))}});",
 """const parse=(raw,type,deck,imported)=>raw.trim().split('\\n').map(l=>{const [k,kana,r,en,alts,pic]=l.split('|');const al=alts?alts.split(',').filter(Boolean):[];
  const clean=al.map(a=>a.replace(/^~/,''));
  // JLPT-list meanings (preferred translations): imported words take them straight from the list
  const jl=type==='k'?[]:imported?[...en.split(';').map(x=>x.trim()),...clean.filter(x=>!/[^\\x00-\\x7F]/.test(x))]:(JL[k]||[]);
  return{id:(type==='k'?'kana:':'')+k+'/'+kana,k,kana,r,en,type,deck,jl,pic:pic||PICS[k]||'',alts:clean,casual:new Set(al.filter(a=>a[0]==='~').map(a=>a.slice(1)))}});"""),
("const WORDS=parse(RAW,'w'),PHRASES=parse(RAW_P,'p');",
 "const WORDS=parse(RAW,'w','n5').concat(parse(RAW_N5X,'w','n5',true)),PHRASES=parse(RAW_P,'p','n5');\nconst N4=parse(RAW_N4,'w','n4',true),HIRA=parse(RAW_HIRA,'k','hira'),KATA=parse(RAW_KATA,'k','kata');"),
("const pool=()=>S.set.types==='words'?WORDS:S.set.types==='phrases'?PHRASES:CARDS;",
 """CARDS.push(...N4,...HIRA,...KATA);
const DECKS={hira:'Hiragana',kata:'Katakana',n5:'N5',n4:'N4'};
let _pk='',_pool=[];
const pool=()=>{const key=S.set.decks.join()+'/'+S.set.types;if(key!==_pk){_pk=key;_pool=CARDS.filter(c=>S.set.decks.includes(c.deck)&&(c.deck!=='n5'||S.set.types==='both'||(S.set.types==='words')===(c.type==='w')))}return _pool};
const isKana=c=>c.type==='k';"""),
("auto:1,types:'both'}","auto:1,types:'both',decks:['n5']}"),
("  if(S.newDone[S.set.dir]<S.set.newPerDay){const n=pool().find(c=>!st(c)&&c.id!==lastId);if(n)return n}",
 """  if(S.newDone[S.set.dir]<S.set.newPerDay){
    // take new cards from the chosen decks in turn
    const ds=S.set.decks;
    for(let i=0;i<ds.length;i++){const dk=ds[(S.newDone[S.set.dir]+i)%ds.length];const n=pool().find(c=>c.deck===dk&&!st(c)&&c.id!==lastId);if(n)return n}
  }"""),
("const promptOf=c=>S.set.dir==='je'?[c.kana,'ja-JP']:[enSay(c),'en-GB'];\nconst answerOf=c=>S.set.dir==='je'?[enSay(c),'en-GB']:[c.kana,'ja-JP'];",
 "const promptOf=c=>c.type==='k'?null:S.set.dir==='je'?[c.kana,'ja-JP']:[enSay(c),'en-GB'];\nconst answerOf=c=>c.type==='k'?[c.kana,'ja-JP']:S.set.dir==='je'?[enSay(c),'en-GB']:[c.kana,'ja-JP'];"),
("function judge(c,heard){\n  if(!heard||!heard.length)return false;\n  if(S.set.dir==='je'){\n    const T=[...c.en.split(';'),c.en,...c.alts].map(normEn).filter(Boolean);",
 """function judge(c,heard){
  if(!heard||!heard.length)return false;
  if(c.type==='k'){const T=[c.k,...c.alts].map(normJa),R=normEn(c.r.replace(/\\(.*?\\)/g,''));return heard.some(h=>T.includes(normJa(h))||normEn(h)===R)}
  if(S.set.dir==='je'){
    const T=[...c.en.split(';'),c.en,...c.alts,...c.jl].map(normEn).filter(Boolean);"""),
("function ruby(c){\n","function ruby(c){\n  if(c.type==='k')return escH(c.k);\n"),
("  if(cur&&+S.set.auto&&!walking&&userActed){const [t,l]=promptOf(cur);speak(t,l)}}",
 "  const pr=cur&&promptOf(cur);if(pr&&+S.set.auto&&!walking&&userActed)speak(pr[0],pr[1])}"),
("$('play').onclick=()=>{if(!cur)return;const [t,l]=revealed?answerOf(cur):promptOf(cur);speak(t,l)};",
 "$('play').onclick=()=>{if(!cur)return;const x=revealed?answerOf(cur):promptOf(cur);if(x)speak(x[0],x[1])};"),
("    const [pt,pl]=promptOf(cur);const [,al]=answerOf(cur);\n    status('Listen…');await speak(pt,pl);if(!walking)break;",
 "    const pr=promptOf(cur);const [,al]=answerOf(cur);\n    if(pr){status('Listen…');await speak(pr[0],pr[1])}else{status('Read the card…');await wait(700)}if(!walking)break;"),
("${cur.type==='p'?' · Phrase':''}</span>","${cur.type==='p'?' · Phrase':''} · ${DECKS[cur.deck]}</span>"),
# Other answers with JLPT group first
("  const a=cur.alts.filter(x=>!(READ[x]&&!READ[x][0]&&kanaOf.has(x)));if(!a.length)return '';\n  if(!showAlts)return `<button class=\"alts-btn\" id=\"altsBtn\" aria-expanded=\"false\">Other answers · ${a.length}</button>`;\n  const ja=a.filter(x=>/[^\\x00-\\x7F]/.test(x)),en=a.filter(x=>!/[^\\x00-\\x7F]/.test(x)).map(x=>x.replace(/\\bi\\b/g,'I'));",
 """  const shown=new Set(cur.en.split(';').map(normEn));
  const jl=cur.jl.filter(x=>!shown.has(normEn(x)));const jlN=new Set([...cur.jl.map(normEn)]);
  const a=cur.alts.filter(x=>!(READ[x]&&!READ[x][0]&&kanaOf.has(x))&&!jlN.has(normEn(x))||/[^\\x00-\\x7F]/.test(x)&&!(READ[x]&&!READ[x][0]&&kanaOf.has(x)));
  const total=a.length+jl.length;if(!total)return '';
  if(!showAlts)return `<button class="alts-btn" id="altsBtn" aria-expanded="false">Other answers · ${total}</button>`;
  const ja=a.filter(x=>/[^\\x00-\\x7F]/.test(x)),en=a.filter(x=>!/[^\\x00-\\x7F]/.test(x)).map(x=>x.replace(/\\bi\\b/g,'I'));"""),
("return `<button class=\"alts-btn\" id=\"altsBtn\" aria-expanded=\"true\">Hide other answers</button><div class=\"alts\">${grp('Japanese',ja,'jpc')}${grp('English',en,'')}</div>`;",
 "return `<button class=\"alts-btn\" id=\"altsBtn\" aria-expanded=\"true\">Hide other answers</button><div class=\"alts\">${grp('JLPT list · preferred',jl,'jlpt')}${grp('Japanese',ja,'jpc')}${grp(jl.length?'Other English':'English',en,'')}</div>`;"),
("const c=cur.casual.has(x)||cur.casual.has(x.replace(/\\bI\\b/g,'i'));","const c=cls!=='jlpt'&&(cur.casual.has(x)||cur.casual.has(x.replace(/\\bI\\b/g,'i')));"),
(".chip.jpc{",".chip.jlpt{background:var(--accent);color:var(--surface);font-weight:500}\n.chip.jpc{"),
# deck picker UI
('<div class="brand"><b>日本語</b><span>JLPT N5</span></div>','<div class="brand"><b>日本語</b><span id="brandSub">JLPT N5</span></div>'),
('  <div class="seg" role="group" aria-label="Direction">','''  <div class="decks" role="group" aria-label="Decks">
    <button data-deck="hira" aria-pressed="false"><b>あ</b>Hiragana</button>
    <button data-deck="kata" aria-pressed="false"><b>ア</b>Katakana</button>
    <button data-deck="n5" aria-pressed="true"><b>N5</b>Words</button>
    <button data-deck="n4" aria-pressed="false"><b>N4</b>Words</button>
  </div>
  <div class="seg" role="group" aria-label="Direction">'''),
('<label>Study <select id="sTypes">','<label>N5 cards <select id="sTypes">'),
(".seg{",""".decks{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.decks button{display:flex;flex-direction:column;align-items:center;gap:1px;padding:7px 2px;border-radius:12px;border:1px solid var(--line);background:var(--surface);font-size:11.5px;color:var(--muted)}
.decks b{font-family:var(--jp);font-size:18px;font-weight:700;color:var(--ink);line-height:1.2}
.decks button[aria-pressed="true"]{border-color:var(--accent);background:var(--accent-soft);color:var(--accent)}
.decks button[aria-pressed="true"] b{color:var(--accent)}
.seg{"""),
("  $('dJE').setAttribute('aria-pressed',S.set.dir==='je');","""  document.querySelectorAll('[data-deck]').forEach(b=>b.setAttribute('aria-pressed',S.set.decks.includes(b.dataset.deck)));
  $('brandSub').textContent=['hira','kata','n5','n4'].filter(d=>S.set.decks.includes(d)).map(d=>({hira:'あ',kata:'ア',n5:'N5',n4:'N4'})[d]).join(' · ');
  $('dJE').setAttribute('aria-pressed',S.set.dir==='je');"""),
("$('dJE').onclick=","""document.querySelector('.decks').onclick=e=>{const b=e.target.closest('[data-deck]');if(!b)return;const d=b.dataset.deck;
  const on=S.set.decks.includes(d);if(on&&S.set.decks.length===1)return;
  S.set.decks=on?S.set.decks.filter(x=>x!==d):[...S.set.decks,d];save();if(walking)stopWalk();lastId=null;show()};
$('dJE').onclick="""),
]
for a,b in R:
    assert a in s, a[:90]
    s=s.replace(a,b,1)
# kana cards: label English side as the sound
s=s.replace("const dir=S.set.dir==='je'?'Japanese → English':'English → Japanese';","const dir=S.set.dir==='je'?'Japanese → English':'English → Japanese';",1)
open(p,'w').write(s)
print('ok',len(s))
