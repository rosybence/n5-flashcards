"""Japanese app: say which of the phone's guesses was accepted; show close (non-exact) matches
next to the answer with the differences marked; digits count as the number."""
import sys

def patch(p):
    s = open(p).read()
    if 'lastHit' in s: print('already', p); return
    R = [
      ("function normJa(s){return s.replace(",
       "const JDIG={'0':'零','1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九','10':'十'};\n"
       "function normJa(s){return s.replace(/[０-９]/g,d=>String.fromCharCode(d.charCodeAt(0)-0xFEE0)).replace(/\\d+/g,d=>JDIG[d]||d).replace("),
      ("function judge(c,heard){\n  if(!heard||!heard.length)return false;\n  if(c.type==='k'){const T=[c.k,...c.alts].map(normJa),R=normEn(c.r.replace(/\\(.*?\\)/g,''));return heard.some(h=>T.includes(normJa(h))||normEn(h)===R)}",
       "let lastHit=null;\nfunction judge(c,heard){\n  lastHit=null;\n  if(!heard||!heard.length)return false;\n"
       "  if(c.type==='k'){const T=[c.k,...c.alts].map(normJa),R=normEn(c.r.replace(/\\(.*?\\)/g,''));\n"
       "    for(let i=0;i<heard.length;i++)if(T.includes(normJa(heard[i]))||normEn(heard[i])===R){lastHit={i,said:heard[i],ans:c.k,exact:true};return true}return false}"),
      ("    const T=[...c.en.split(';'),c.en,...c.alts,...c.jl].map(normEn).filter(Boolean);\n"
       "    return heard.some(h=>{h=normEn(h);return T.some(t=>h===t||(' '+h+' ').includes(' '+t+' ')||sim(h,t)>=.8||overlap(h,t)>=.75)});",
       "    const D=[...c.en.split(';').map(x=>x.trim()),c.en,...c.alts,...c.jl].filter(x=>normEn(x));const T=D.map(normEn);\n"
       "    for(const exact of [true,false])for(let i=0;i<heard.length;i++){const h=normEn(heard[i]);\n"
       "      for(let j=0;j<T.length;j++){const t=T[j];if(exact?(h===t||(' '+h+' ').includes(' '+t+' ')):(sim(h,t)>=.8||overlap(h,t)>=.75)){lastHit={i,said:heard[i],ans:D[j],exact};return true}}}\n"
       "    return false;"),
      ("  for(const pass of [(h,t)=>h===t,close])for(const [l,ts] of P)if(H.some(h=>ts.some(t=>pass(h,t)))){lastMatch=l===c.k?null:l;return true}",
       "  // saying the answer inside a longer sentence still counts as exact\n"
       "  const same=(h,t)=>h===t||(t.length>1&&h.includes(t));\n"
       "  for(const [exact,pass] of [[true,same],[false,close]])for(const [l,ts] of P)for(let i=0;i<H.length;i++){const t=ts.find(t=>pass(H[i],t));if(t!==undefined){\n"
       "    lastMatch=l===c.k?null:l;lastHit={i,said:heard[i],ans:l===c.k?c.k+(c.kana&&c.kana!==c.k?'（'+c.kana+'）':''):l,ansN:t,exact};return true}}"),
      ("fb.className='feedback '+feedback.cls;fb.textContent=feedback.text}",
       "fb.className='feedback '+feedback.cls;if(feedback.html)fb.innerHTML=feedback.html;else fb.textContent=feedback.text}"),
      ("  feedback={cls:'ok',text:'Correct — heard “'+heard[0]+'”'+(casualHit(cur,heard)?' · casual form':'')};",
       "  feedback=okFeedback(heard);"),
      ("      lastHeard=heard&&heard[0]||'';feedback=heard&&heard.length?{cls:ok?'ok':'no',",
       "      lastHeard=heard&&heard[0]||'';feedback=ok&&heard&&heard.length?okFeedback(heard):heard&&heard.length?{cls:ok?'ok':'no',"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b, 1)
    helper = r'''
/* ---------- telling you exactly what was accepted ---------- */
function markDiffEn(a,b){const B=new Set(b.split(/\s+/).map(normEn).filter(Boolean));
  return a.split(/\s+/).map(w=>{const n=normEn(w);return n&&!B.has(n)?'<b class="dw">'+escH(w)+'</b>':escH(w)}).join(' ')}
// Japanese has no spaces: mark the characters that aren't shared (longest common subsequence)
function markDiffJa(a,b){const A=[...a],B=[...b],n=A.length,m=B.length,L=Array.from({length:n+1},()=>new Array(m+1).fill(0));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L[i][j]=A[i]===B[j]?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
  const keep=new Set();let i=0,j=0;while(i<n&&j<m){if(A[i]===B[j]){keep.add(i);i++;j++}else if(L[i+1][j]>=L[i][j+1])i++;else j++}
  return A.map((ch,k)=>keep.has(k)?escH(ch):'<b class="dw">'+escH(ch)+'</b>').join('')}
function okFeedback(heard){
  const h=lastHit||{i:0,said:heard[0],ans:'',exact:true};
  const extra=(casualHit(cur,heard)?' · casual form':'');
  const first=h.i>0&&heard[0]&&heard[0]!==h.said?`<span class="fbsub">The phone’s first guess was “${escH(heard[0])}”, but another guess matched.</span>`:'';
  lastHeard=h.said;
  if(h.exact)return{cls:'ok',text:'',html:`Correct — heard “${escH(h.said)}”${extra}${first}`};
  const en=S.set.dir==='je'&&cur.type!=='k';
  const you=en?markDiffEn(h.said,h.ans):markDiffJa(normJa(h.said),h.ansN||normJa(h.ans));
  const ans=en?markDiffEn(h.ans,h.said):escH(h.ans);
  return{cls:'close',text:'',html:`<b>Accepted as close</b> — not an exact match${extra}`+
    `<span class="fbcmp"><span class="fbl">You said</span> “${you}”</span>`+
    `<span class="fbcmp"><span class="fbl">Answer</span> “${ans}”</span>${first}`+
    `<span class="fbsub">If the difference matters, tap “I got it wrong”.</span>`};
}
'''
    i = s.index('/* ---------- rendering ---------- */'); s = s[:i] + helper + s[i:]
    css = '''
.feedback.close{background:var(--accent-soft);color:var(--ink);text-align:left}
.feedback .fbcmp{display:block;margin-top:4px}
.feedback .fbl{display:inline-block;min-width:68px;font-size:12px;color:var(--muted)}
.feedback .dw{color:var(--bad);font-weight:700;text-decoration:underline;text-underline-offset:3px}
.feedback .fbsub{display:block;margin-top:5px;font-size:12.5px;color:var(--muted)}
'''
    i = s.index('</style>'); s = s[:i] + css + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
