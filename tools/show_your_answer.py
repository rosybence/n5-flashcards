"""When an alternative answer is accepted, show and say that answer as the main one; the card's own answer moves to Other answers."""
import sys
JP = [
 ("  const T=[c.k,c.kana,...c.alts,...c.alts.map(x=>READ[x]&&READ[x][0]).filter(Boolean)].map(normJa);\n  return heard.some(h=>{h=normJa(h);return T.some(t=>h===t||(t.length>1&&h.includes(t))||sim(h,t)>=(t.length>8?.7:.75))});",
  """  // find which answer you gave: exact matches first, then close ones; the card's own answer wins ties
  const P=[[c.k,[c.k,c.kana]],...c.alts.map(a=>[a,[a,READ[a]&&READ[a][0]].filter(Boolean)])].map(([l,ts])=>[l,ts.map(normJa)]);
  const H=heard.map(normJa);lastMatch=null;
  const close=(h,t)=>h===t||(t.length>1&&h.includes(t))||sim(h,t)>=(t.length>8?.7:.75);
  for(const pass of [(h,t)=>h===t,close])for(const [l,ts] of P)if(H.some(h=>ts.some(t=>pass(h,t)))){lastMatch=l===c.k?null:l;return true}
  return false;"""),
 ("const answerOf=c=>c.type==='k'?[c.kana,'ja-JP']:S.set.dir==='je'?[enSay(c),'en-GB']:[c.kana,'ja-JP'];",
  "const answerOf=c=>c.type==='k'?[c.kana,'ja-JP']:S.set.dir==='je'?[enSay(c),'en-GB']:[altShown&&c===cur?(READ[altShown]&&READ[altShown][0]||altShown):c.kana,'ja-JP'];"),
 ("`<div class=\"jp\">${ruby(cur)}</div>",
  "`<div class=\"jp\">${ruby(shownCard())}</div>"),
 ("function altsHtml(){",
  """function shownCard(){if(!altShown||S.set.dir!=='ej')return cur;const r=READ[altShown]||['',''];return{...cur,k:altShown,kana:r[0]||altShown,r:r[1]||''}}
// with your own answer shown, the card's answer joins the other answers
function altsHtml(){
  if(!altShown||S.set.dir!=='ej')return altsHtmlBase();
  const keep=cur;READ[keep.k]=READ[keep.k]||[keep.k!==keep.kana?keep.kana:'',keep.r];
  cur={...keep,k:altShown,kana:(READ[altShown]&&READ[altShown][0])||altShown,alts:[keep.k,...keep.alts.filter(x=>x!==altShown)]};
  try{return altsHtmlBase()}finally{cur=keep}
}
function altsHtmlBase(){"""),
]
ES = [
 ("  const T=esTargets(c);\n  return heard.some(h=>{h=normEs(h);return T.some(t=>h===t||(t.length>3&&(' '+h+' ').includes(' '+t+' '))||(t.length>6&&sim(h,t)>=(t.length>12?.75:.8))||overlap(h,t)>=.8)});",
  """  // find which answer you gave: exact matches first, then close ones; the card's own answer wins ties
  const P=[[c.es,[c.es,...c.enA.filter(x=>/^\\d+$/.test(x))]],...c.esA.map(a=>[a,[a]])].map(([l,ts])=>[l,ts.map(normEs).filter(Boolean)]);
  const H=heard.map(normEs);lastMatch=null;
  const close=(h,t)=>h===t||(t.length>3&&(' '+h+' ').includes(' '+t+' '))||(t.length>6&&sim(h,t)>=(t.length>12?.75:.8))||overlap(h,t)>=.8;
  for(const pass of [(h,t)=>h===t,close])for(const [l,ts] of P)if(H.some(h=>ts.some(t=>pass(h,t)))){lastMatch=l===c.es?null:l;return true}
  return false;"""),
 ("const answerOf=c=>S.set.dir==='je'?[enSay(c),'en-GB']:[esSay(c),'es-ES'];",
  "const answerOf=c=>S.set.dir==='je'?[enSay(c),'en-GB']:[altShown&&c===cur?altShown.replace(/…/g,''):esSay(c),'es-ES'];"),
 ("`<div class=\"es${long?' long':''}\">${esHtml(cur.es)}</div>`}${altsHtml()}",
  "`<div class=\"es${long?' long':''}\">${esHtml(altShown||cur.es)}</div>`}${altsHtml()}"),
 ("  const xs=(es?cur.esA:", "  const xs=(es?(altShown?[cur.es,...cur.esA.filter(x=>x!==altShown)]:cur.esA):"),
 ("function resetCard(){revealed=false;", "function resetCard(){altShown=null;revealed=false;"),
]
COMMON = [
 ("function judge(c,heard){", "let lastMatch=null,altShown=null;\nfunction judgeShow(c,heard){const ok=judge(c,heard);altShown=ok&&S.set.dir==='ej'?lastMatch:null;return ok}\nfunction judge(c,heard){"),
 ("const ok=judge(cur,heard);tone(ok);", "const ok=judgeShow(cur,heard);tone(ok);"),
 ("ok=heard!==null&&judge(cur,heard);", "ok=heard!==null&&judgeShow(cur,heard);"),
]
for p in sys.argv[1:]:
    s=open(p).read()
    if 'judgeShow' in s: print('already',p);continue
    for a,b in COMMON+(JP if 'n5-flashcards' in p else ES):
        assert s.count(a)==1,(p,a[:70]);s=s.replace(a,b,1)
    if 'n5-flashcards' in p:
        n=s.count("feedback=null;suggest=null;showAlts=false;")
        s=s.replace("feedback=null;suggest=null;showAlts=false;","feedback=null;suggest=null;showAlts=false;altShown=null;")
        print('resets',n)
    open(p,'w').write(s);print('patched',p)
