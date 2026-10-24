"""Japanese app: Automatic phrase mode (ported from the Spanish app).
A short word the phone keeps mishearing switches to a short example sentence containing it (sticky per card).
The sentence is judged by sound: the word must be in what you said, and most of the sentence too.
Usage: python3 phrase_mode_jp.py <app.html> <phj.json>"""
import sys, json

def patch(p, phj):
    s = open(p).read()
    if 'function judgePhraseJa' in s: print('already', p); return
    data = json.dumps(json.load(open(phj)), ensure_ascii=False, separators=(',', ':'))
    JS = r'''
/* ---------- phrase mode: answer a short word card with an example sentence ---------- */
// PHJ[card] = [sentence with [target], target as said (kana), English with [word], reading with spaces]
const PHJ=''' + data + r''';
for(const c of CARDS)if(c.type==='w'&&PHJ[c.k])c.ph=PHJ[c.k];
const plainPh=s=>s.replace(/[\[\]]/g,'');
const markPh=s=>escH(s).replace(/\[(.*?)\]/g,'<b class="tw">$1</b>');
function phraseOn(c){if(!c||!c.ph||S.set.dir!=='ej'||c.type!=='w')return false;
  const m=S.set.phraseMode||'auto';return m==='always'||(m==='auto'&&!!(S.phr||{})[c.id])}
function setPhrase(c,on){S.phr=S.phr||{};S.miss=S.miss||{};if(on)S.phr[c.id]=1;else{delete S.phr[c.id];S.miss[c.id]=0}save()}
function noteMiss(c){S.miss=S.miss||{};S.miss[c.id]=(S.miss[c.id]||0)+1;save();return S.miss[c.id]}
function canSwitch(c){return c&&c.ph&&S.set.dir==='ej'&&c.type==='w'&&(S.set.phraseMode||'auto')==='auto'&&!phraseOn(c)}
// right if the card's word is in what you said (by sound) and most of the sentence is there too
function judgePhraseJa(c,heard){
  const [ja,tr,,full]=c.ph,t=normJa(tr),F=normJa(full),tw=normJa((ja.match(/\[(.*?)\]/)||['',''])[1]);
  let best=null;
  for(let i=0;i<heard.length;i++){const hn=normJa(heard[i]||'');if(!hn)continue;
    const rs=readingsOf(hn);if(isKanaStr(hn)&&!rs.includes(hn))rs.push(hn);
    const hasT=hn.includes(tw)||rs.some(r=>r.includes(t)||loose(r).includes(loose(t)));
    if(!hasT)continue;
    let r0=rs[0]||hn,sc=0;for(const r of rs){const v=Math.max(sim(r,F),sim(loose(r),loose(F)));if(v>sc){sc=v;r0=r}}
    const exact=rs.includes(F);
    if(exact||sc>=.6||hn===tw||rs.some(r=>r===t)){best={i,said:heard[i],saidR:r0!==hn?r0:null,ans:plainPh(ja),ansN:F,exact};break}
  }
  lastHit=best;return !!best;
}
// kana -> romaji (Hepburn with long-vowel macrons); words separated by spaces, lone は/へ/を are particles
const ROMA={'きゃ':'kya','きゅ':'kyu','きょ':'kyo','しゃ':'sha','しゅ':'shu','しょ':'sho','ちゃ':'cha','ちゅ':'chu','ちょ':'cho','にゃ':'nya','にゅ':'nyu','にょ':'nyo','ひゃ':'hya','ひゅ':'hyu','ひょ':'hyo','みゃ':'mya','みゅ':'myu','みょ':'myo','りゃ':'rya','りゅ':'ryu','りょ':'ryo','ぎゃ':'gya','ぎゅ':'gyu','ぎょ':'gyo','じゃ':'ja','じゅ':'ju','じょ':'jo','びゃ':'bya','びゅ':'byu','びょ':'byo','ぴゃ':'pya','ぴゅ':'pyu','ぴょ':'pyo',
 'あ':'a','い':'i','う':'u','え':'e','お':'o','か':'ka','き':'ki','く':'ku','け':'ke','こ':'ko','さ':'sa','し':'shi','す':'su','せ':'se','そ':'so','た':'ta','ち':'chi','つ':'tsu','て':'te','と':'to','な':'na','に':'ni','ぬ':'nu','ね':'ne','の':'no','は':'ha','ひ':'hi','ふ':'fu','へ':'he','ほ':'ho','ま':'ma','み':'mi','む':'mu','め':'me','も':'mo','や':'ya','ゆ':'yu','よ':'yo','ら':'ra','り':'ri','る':'ru','れ':'re','ろ':'ro','わ':'wa','を':'o','ん':'n',
 'が':'ga','ぎ':'gi','ぐ':'gu','げ':'ge','ご':'go','ざ':'za','じ':'ji','ず':'zu','ぜ':'ze','ぞ':'zo','だ':'da','ぢ':'ji','づ':'zu','で':'de','ど':'do','ば':'ba','び':'bi','ぶ':'bu','べ':'be','ぼ':'bo','ぱ':'pa','ぴ':'pi','ぷ':'pu','ぺ':'pe','ぽ':'po','ぁ':'a','ぃ':'i','ぅ':'u','ぇ':'e','ぉ':'o'};
function kanaRomaji(s){return s.split(' ').map(w=>{if(w==='は')return 'wa';if(w==='へ')return 'e';if(w==='を')return 'o';
  w=w.replace(/[ァ-ヶ]/g,ch=>String.fromCharCode(ch.charCodeAt(0)-0x60));let o='',dbl=false;
  for(let i=0;i<w.length;i++){const two=ROMA[w.slice(i,i+2)];let r=two||ROMA[w[i]];if(two)i++;
    if(w[i]==='っ'){dbl=true;continue}if(w[i]==='ー'){o=o.replace(/([aeiou])$/,m=>({a:'ā',e:'ē',i:'ī',o:'ō',u:'ū'})[m]);continue}
    if(!r){o+=w[i];continue}if(dbl){r=(r.startsWith('ch')?'t':r[0])+r;dbl=false}
    if(o.endsWith('n')&&w[i-1]==='ん'&&/^[aeiouy]/.test(r))o+="'";
    o+=r}
  return o.replace(/ou/g,'ō').replace(/oo/g,'ō').replace(/uu/g,'ū').replace(/aa/g,'ā')}).join(' ')}
function phRuby(c){const [ja,,,full]=c.ph;const mode=S.set.ruby;const rt=mode==='romaji'?kanaRomaji(full):mode==='kana'?full:'';
  return `<span class="stack">${rt?`<span class="rt">${escH(rt)}</span>`:''}<span>${markPh(ja)}</span></span>`}
let phShowMiss=0,phShowId=null;
// on the Speak button: second miss on a short word in this showing switches the card to its sentence
function phMaybeSwitch(){
  if(phShowId!==cur.id){phShowId=cur.id;phShowMiss=0}
  if(!canSwitch(cur))return false;
  phShowMiss++;noteMiss(cur);
  if(phShowMiss<2)return false;
  setPhrase(cur,true);triedWrong=false;
  feedback={cls:'info',text:'Your phone keeps mishearing this word, so try it in a sentence. Tap Speak and say the whole sentence.'};render();
  const pr=promptOf(cur);if(+S.set.auto)speak(pr[0],pr[1]);
  return true;
}
document.addEventListener('click',e=>{if(e.target.closest('#phSingle')){setPhrase(cur,false);phShowMiss=0;feedback=null;render();
  const pr=promptOf(cur);if(+S.set.auto)speak(pr[0],pr[1])}});
'''
    R = [
      # audio: English sentence as the prompt, Japanese sentence (written form) as the answer
      ("const promptOf=c=>c.type==='k'?null:S.set.dir==='je'?[jaSay(c),'ja-JP']:[enSay(c),'en-GB'];",
       "const promptOf=c=>c.type==='k'?null:S.set.dir==='je'?[jaSay(c),'ja-JP']:phraseOn(c)?[plainPh(c.ph[2]),'en-GB']:[enSay(c),'en-GB'];"),
      ("const answerOf=c=>c.type==='k'?[c.kana,'ja-JP']:S.set.dir==='je'?[enSay(c),'en-GB']:[altShown",
       "const answerOf=c=>c.type==='k'?[c.kana,'ja-JP']:S.set.dir==='je'?[enSay(c),'en-GB']:phraseOn(c)?[plainPh(c.ph[0]),'ja-JP']:[altShown"),
      # judging
      ("  if(S.set.dir==='je'){\n    const D=",
       "  if(phraseOn(c)){lastMatch=null;return judgePhraseJa(c,heard)}\n  if(S.set.dir==='je'){\n    const D="),
      # front / back
      ("  const front=S.set.dir==='je'?`<div class=\"jp${long?' long':''}\">${ruby(cur)}</div>`:`<div class=\"en-front\">${cur.en}</div>`;",
       "  const ph=phraseOn(cur);\n  const front=S.set.dir==='je'?`<div class=\"jp${long?' long':''}\">${ruby(cur)}</div>`:ph?`<div class=\"en-front ph\"><span>${markPh(cur.ph[2])}</span><span class=\"phnote\">Say the whole sentence in Japanese</span>${(S.set.phraseMode||'auto')==='auto'?'<button class=\"phsingle\" id=\"phSingle\">Try the single word instead</button>':''}</div>`:`<div class=\"en-front\">${cur.en}</div>`;"),
      ("${cur.type==='p'?' · Phrase':''} · ${cur.type==='k'?DECKS[cur.deck]",
       "${cur.type==='p'?' · Phrase':''}${ph?' · In a sentence':''} · ${cur.type==='k'?DECKS[cur.deck]"),
      ("      `<div class=\"jp\">${ruby(shownCard())}</div>",
       "      ph?`<div class=\"jp phans\">${phRuby(cur)}</div><div class=\"phword\">${escH(cur.k)}${cur.k!==cur.kana?'（'+escH(cur.kana)+'）':''} · ${escH(cur.en)}</div>`:`<div class=\"jp\">${ruby(shownCard())}</div>"),
      # Speak button
      ("  if(!heard.length||!heard.some(x=>x&&x.trim())){feedback={cls:'no',text:'Didn’t catch that. Tap Speak to try again.'};return render()}",
       "  if(!heard.length||!heard.some(x=>x&&x.trim())){if(phMaybeSwitch())return;feedback={cls:'no',text:'Didn’t catch that. Tap Speak to try again.'};return render()}"),
      ("  if(!ok){triedWrong=true;feedback=",
       "  if(!ok&&phMaybeSwitch())return;\n  if(ok&&!phraseOn(cur)&&S.miss)S.miss[cur.id]=0;\n  if(!ok){triedWrong=true;feedback="),
      # walk mode: a miss on a short word gets one more go as a sentence
      ("      const heard=await listen(al,S.set.gap*1000,h=>{if(h){feedback={cls:'info',text:'Heard: '+h};render()}});\n      if(!walking)break;\n      if(heard===null){",
       "      let heard=await listen(al,S.set.gap*1000,h=>{if(h){feedback={cls:'info',text:'Heard: '+h};render()}});\n      if(!walking)break;\n      if(heard===null){"),
      ("      ok=heard!==null&&judgeShow(cur,heard);knewIt=ok&&!st(cur);tone(ok);",
       "      ok=heard!==null&&judgeShow(cur,heard);knewIt=ok&&!st(cur);\n"
       "      if(!ok&&heard!==null&&canSwitch(cur)){\n"
       "        setPhrase(cur,true);render();status('Let’s try it in a sentence');\n"
       "        await speak('Try it in a sentence.','en-GB');if(!walking)break;\n"
       "        await speak(plainPh(cur.ph[2]),'en-GB');if(!walking)break;\n"
       "        status('Your turn — say the whole sentence in Japanese');\n"
       "        const h2=await listen(al,(S.set.gap+3)*1000,h=>{if(h){feedback={cls:'info',text:'Heard: '+h};render()}});\n"
       "        if(!walking)break;\n"
       "        ok=h2!==null&&judgeShow(cur,h2);if(h2&&h2.length)heard=h2;knewIt=false;\n"
       "        if(!ok)setPhrase(cur,false),noteMiss(cur);\n"
       "      }\n"
       "      tone(ok);"),
      # setting
      ('    <label>Reading above kanji',
       '    <label>Phrase help <select id="sPhrase"><option value="auto">Automatic</option><option value="always">Always sentences</option><option value="off">Off</option></select></label>\n    <label>Reading above kanji'),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:80]); s = s.replace(a, b, 1)
    a = "bind('sRuby','ruby');"
    assert s.count(a) == 1
    s = s.replace(a, "$('sPhrase').value=S.set.phraseMode||'auto';$('sPhrase').onchange=()=>{S.set.phraseMode=$('sPhrase').value;save();render()};\n" + a, 1)
    i = s.index('/* ---------- telling you exactly what was accepted ---------- */'); s = s[:i] + JS + s[i:]
    css = '''
.en-front.ph{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:clamp(22px,6.5vw,30px)}
.tw{color:var(--accent);font-weight:700}
.phnote{font-size:13px;color:var(--muted);font-weight:400}
.phsingle{font-size:12.5px;color:var(--muted);text-decoration:underline;text-underline-offset:3px;padding:4px}
.phans{font-size:clamp(24px,7vw,34px)!important}
.phword{font-size:14px;color:var(--muted);margin-top:4px}
'''
    i = s.index('</style>'); s = s[:i] + css + s[i:]
    open(p, 'w').write(s); print('patched', p)

patch(sys.argv[1], sys.argv[2])
