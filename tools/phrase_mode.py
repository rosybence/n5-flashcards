"""Spanish app: Automatic phrase mode.
A short word the phone keeps mishearing switches to an example phrase containing it (sticky per card);
the phrase is judged by finding the word in what you said."""
import sys

JS = r'''
/* ---------- phrase mode: answer a word card with an example phrase ---------- */
const plainPh=s=>s.replace(/[\[\]]/g,'');
const markPh=s=>escH(s).replace(/\[(.*?)\]/g,'<b class="tw">$1</b>');
function phraseOn(c){if(!c||!c.ph||S.set.dir!=='ej'||c.type!=='w')return false;
  const m=S.set.phraseMode||'auto';return m==='always'||(m==='auto'&&!!(S.phr||{})[c.id])}
function setPhrase(c,on){S.phr=S.phr||{};S.miss=S.miss||{};if(on)S.phr[c.id]=1;else{delete S.phr[c.id];S.miss[c.id]=0}save()}
function noteMiss(c){S.miss=S.miss||{};S.miss[c.id]=(S.miss[c.id]||0)+1;save();return S.miss[c.id]}
function canSwitch(c){return c&&c.ph&&S.set.dir==='ej'&&c.type==='w'&&(S.set.phraseMode||'auto')==='auto'&&!phraseOn(c)}
const phWords=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9ñ ]+/g,' ').split(/\s+/).filter(Boolean);
function wordHit(h,t){return h===t||phonEs(h)===phonEs(t)||(S.set.check!=='strict'&&softNear(phonEs(h),phonEs(t)))}
// right if the card's word is in what you said and most of the phrase is there too
function judgePhrase(c,heard){
  const exp=phWords(plainPh(c.ph[0])),tgt=phWords((c.ph[0].match(/\[(.*?)\]/)||['',''])[1]);
  return heard.some(h=>{const H=phWords(h);if(!H.length)return false;
    const hasT=tgt.every(t=>H.some(w=>wordHit(w,t)));
    const found=exp.filter(e=>H.some(w=>wordHit(w,e))).length;
    return hasT&&(found/exp.length>=.5||H.length<=tgt.length+1)});
}
'''

def patch(p):
    s = open(p).read()
    if 'function judgePhrase' in s: print('already', p); return
    R = [
      # card builder keeps the phrase
      ("function build(rows,type,deck){return rows.map(([es,en,esA,enA,pic])=>{",
       "function build(rows,type,deck){return rows.map(([es,en,esA,enA,pic,ph])=>{"),
      ("return{id:deck+':'+es+'|'+en,es,en,type,deck,pic:pic||'',esA:strip(esA),enA:strip(enA),",
       "return{id:deck+':'+es+'|'+en,es,en,type,deck,pic:pic||'',ph:ph||null,esA:strip(esA),enA:strip(enA),"),
      # prompt / answer audio
      ("const promptOf=c=>S.set.dir==='je'?[esSay(c),'es-ES']:[enSay(c),'en-GB'];",
       "const promptOf=c=>S.set.dir==='je'?[esSay(c),'es-ES']:phraseOn(c)?[plainPh(c.ph[1]),'en-GB']:[enSay(c),'en-GB'];"),
      ("const answerOf=c=>S.set.dir==='je'?[enSay(c),'en-GB']:[altShown&&c===cur?",
       "const answerOf=c=>S.set.dir==='je'?[enSay(c),'en-GB']:phraseOn(c)?[plainPh(c.ph[0]),'es-ES']:[altShown&&c===cur?"),
      # judging
      ("function judge(c,heard){\n  lastLenient=false;\n  if(!heard||!heard.length)return false;",
       "function judge(c,heard){\n  lastLenient=false;\n  if(!heard||!heard.length)return false;\n  if(phraseOn(c)){lastMatch=null;return judgePhrase(c,heard)}"),
      # front of card
      ("  const front=S.set.dir==='je'?`<div class=\"es${long?' long':''}\">${esHtml(cur.es)}</div>`:`<div class=\"en-front\">${escH(cur.en)}</div>`;",
       "  const ph=phraseOn(cur);\n  const front=S.set.dir==='je'?`<div class=\"es${long?' long':''}\">${esHtml(cur.es)}</div>`:ph?`<div class=\"en-front ph\"><span>${markPh(cur.ph[1])}</span><span class=\"phnote\">Say the whole phrase in Spanish</span>${(S.set.phraseMode||'auto')==='auto'?'<button class=\"phsingle\" id=\"phSingle\">Try the single word instead</button>':''}</div>`:`<div class=\"en-front\">${escH(cur.en)}</div>`;"),
      ("${cur.type==='p'?' · Phrase':''} · ${LEVELS[cur.deck]}</span>",
       "${cur.type==='p'?' · Phrase':''}${ph?' · In a phrase':''} · ${LEVELS[cur.deck]}</span>"),
      # answer side
      ("`<div class=\"es${long?' long':''}\">${esHtml(altShown||cur.es)}</div>`}${altsHtml()}</div>`;",
       "(ph?`<div class=\"es long phans\">${markPh(cur.ph[0])}</div><div class=\"phword\">${esHtml(cur.es)} · ${escH(cur.en)}</div>`:`<div class=\"es${long?' long':''}\">${esHtml(altShown||cur.es)}</div>`)}${altsHtml()}</div>`;"),
      # Speak button: two misses on a short word -> phrase
      ("  if(!heard.length||!heard.some(x=>x&&x.trim())){feedback={cls:'no',text:'Didn’t catch that. Tap Speak to try again.'};return render()}",
       "  if(!heard.length||!heard.some(x=>x&&x.trim())){if(phMaybeSwitch())return;feedback={cls:'no',text:'Didn’t catch that. Tap Speak to try again.'};return render()}"),
      ("  if(!ok){triedWrong=true;feedback=",
       "  if(!ok&&phMaybeSwitch())return;\n  if(ok&&!phraseOn(cur)&&S.miss)S.miss[cur.id]=0;\n  if(!ok){triedWrong=true;feedback="),
      # walk mode: a miss on a short word gets one more go as a phrase
      ("      ok=heard!==null&&judgeShow(cur,heard);tone(ok);heardFeedback(ok,heard);",
       """      ok=heard!==null&&judgeShow(cur,heard);
      if(!ok&&heard!==null&&canSwitch(cur)){
        setPhrase(cur,true);render();status('Let’s try it in a phrase');
        await speak('Try it in a phrase.','en-GB');if(!walking)break;
        await speak(plainPh(cur.ph[1]),'en-GB');if(!walking)break;
        status('Your turn — say the whole phrase in Spanish');
        const h2=await listen(al,(S.set.gap+3)*1000,h=>{if(h){feedback={cls:'info',text:'Heard: '+h};render()}});
        if(!walking)break;
        ok=h2!==null&&judgeShow(cur,h2);heardFeedback(ok,h2&&h2.length?h2:heard);
        if(!ok)setPhrase(cur,false),noteMiss(cur);
      }
      tone(ok);if(!feedback||feedback.cls==='info')heardFeedback(ok,heard);"""),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b, 1)
    # speak-button helper + "try the single word" link
    helper = r'''
let phShowMiss=0,phShowId=null;
// on the Speak button: second miss on a short word in this showing switches the card to its phrase
function phMaybeSwitch(){
  if(phShowId!==cur.id){phShowId=cur.id;phShowMiss=0}
  if(!canSwitch(cur))return false;
  phShowMiss++;noteMiss(cur);
  if(phShowMiss<2)return false;
  setPhrase(cur,true);triedWrong=false;
  feedback={cls:'info',text:'Your phone keeps mishearing this word, so try it in a phrase. Tap Speak and say the whole phrase.'};render();
  const pr=promptOf(cur);if(+S.set.auto)speak(pr[0],pr[1]);
  return true;
}
document.addEventListener('click',e=>{if(e.target.closest('#phSingle')){setPhrase(cur,false);phShowMiss=0;feedback=null;render();
  const pr=promptOf(cur);if(+S.set.auto)speak(pr[0],pr[1])}});
'''
    i = s.index('/* ---------- answer checking ---------- */'); s = s[:i] + JS + helper + s[i:]
    # setting
    a = '    <label>Answer checking'
    assert s.count(a) == 1
    s = s.replace(a, '    <label>Phrase help <select id="sPhrase"><option value="auto">Automatic</option><option value="always">Always phrases</option><option value="off">Off</option></select></label>\n' + a, 1)
    a = "$('sCheck').value=S.set.check||'lenient';"
    assert s.count(a) == 1
    s = s.replace(a, "$('sPhrase').value=S.set.phraseMode||'auto';$('sPhrase').onchange=()=>{S.set.phraseMode=$('sPhrase').value;save();render()};\n" + a, 1)
    css = '''
.en-front.ph{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:clamp(22px,6.5vw,30px)}
.tw{color:var(--accent);font-weight:700}
.phnote{font-size:13px;color:var(--muted);font-weight:400}
.phsingle{font-size:12.5px;color:var(--muted);text-decoration:underline;text-underline-offset:3px;padding:4px}
.phans{font-weight:500}
.phans .tw{font-weight:700}
.phword{font-size:14px;color:var(--muted)}
'''
    i = s.index('</style>'); s = s[:i] + css + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
