"""Spanish app: say which of the phone's guesses was accepted, and when an answer was only
accepted as 'close', show what you said next to the real answer with the differences marked."""
import sys

def patch(p):
    s = open(p).read()
    if 'lastHit' in s: print('already', p); return
    R = [
      # --- remember which guess matched, against which answer, and whether it was exact ---
      ("function judge(c,heard){\n  lastLenient=false;\n  if(!heard||!heard.length)return false;",
       "let lastHit=null;\nfunction judge(c,heard){\n  lastLenient=false;lastHit=null;\n  if(!heard||!heard.length)return false;"),
      ("  if(S.set.dir==='je'){const T=enTargets(c);return heard.some(h=>{h=normEn(h);return T.some(t=>h===t||(' '+h+' ').includes(' '+t+' ')||sim(h,t)>=.8||overlap(h,t)>=.75)})}",
       "  if(S.set.dir==='je'){const T=enTargets(c);const disp=[...c.en.split(';').map(x=>x.trim()),c.en,...c.enA];\n"
       "    for(const exact of [true,false])for(let i=0;i<heard.length;i++){const h=normEn(heard[i]);\n"
       "      for(let j=0;j<T.length;j++){const t=T[j];if(exact?(h===t||(' '+h+' ').includes(' '+t+' ')):(sim(h,t)>=.8||overlap(h,t)>=.75)){lastHit={i,said:heard[i],ans:disp[j]||c.en,exact};return true}}}\n"
       "    return false}"),
      ("  for(const pass of [(h,t)=>h===t,close])for(const [l,ts] of P)if(H.some(h=>ts.some(t=>pass(h,t)))){lastMatch=l===c.es?null:l;return true}",
       "  // same sound, different spelling (b/v, ll/y…) still counts as exact\n"
       "  const same=(h,t)=>h===t||phonEs(h)===phonEs(t)||(t.length>=2&&(' '+h+' ').includes(' '+t+' '));\n"
       "  for(const [exact,pass] of [[true,same],[false,close]])for(const [l,ts] of P)for(let i=0;i<H.length;i++)if(ts.some(t=>pass(H[i],t))){\n"
       "    lastMatch=l===c.es?null:l;lastHit={i,said:heard[i],ans:l,exact:exact&&!lastLenient};return true}"),
      # phrase judging
      ("  return heard.some(h=>{const H=phWords(h);if(!H.length)return false;",
       "  return heard.some((h,i)=>{const H=phWords(h);if(!H.length)return false;"),
      ("    return hasT&&(!rest.length||found/rest.length>=.5||H.length<=tgt.length+1)});\n}",
       "    const ok=hasT&&(!rest.length||found/rest.length>=.5||H.length<=tgt.length+1);\n"
       "    if(ok)lastHit={i,said:h,ans:plainPh(c.ph[0]),exact:phWords(h).join(' ')===exp.join(' ')};\n"
       "    return ok});\n}"),
      # --- feedback can carry markup ---
      ("fb.className='feedback '+feedback.cls;fb.textContent=feedback.text}",
       "fb.className='feedback '+feedback.cls;if(feedback.html)fb.innerHTML=feedback.html;else fb.textContent=feedback.text}"),
      # Speak button
      ("  feedback={cls:'ok',text:'Correct — heard “'+heard[0]+'”'+(casualHit(cur,heard)?' · casual form':'')+(lastLenient?' · close enough':'')};",
       "  feedback=okFeedback(heard);"),
      # walk mode / shared helper
      ("function heardFeedback(ok,heard){lastHeard=heard&&heard[0]||'';\n  feedback=heard&&heard.length?{",
       "function heardFeedback(ok,heard){lastHeard=heard&&heard[0]||'';\n  if(ok&&heard&&heard.length){feedback=okFeedback(heard);return}\n  feedback=heard&&heard.length?{"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b, 1)
    helper = r'''
/* ---------- telling you exactly what was accepted ---------- */
// words of a that aren't in b get marked
function markDiff(a,b,norm){const B=new Set(b.split(/\s+/).map(norm).filter(Boolean));
  return a.split(/\s+/).map(w=>{const n=norm(w);return n&&!B.has(n)?'<b class="dw">'+escH(w)+'</b>':escH(w)}).join(' ')}
function okFeedback(heard){
  const h=lastHit||{i:0,said:heard[0],ans:'',exact:true};
  const extra=(casualHit(cur,heard)?' · casual form':'');
  const first=h.i>0&&heard[0]&&heard[0]!==h.said?`<span class="fbsub">The phone’s first guess was “${escH(heard[0])}”, but another guess matched.</span>`:'';
  lastHeard=h.said;
  if(h.exact)return{cls:'ok',text:'',html:`Correct — heard “${escH(h.said)}”${extra}${first}`};
  const n=S.set.dir==='je'?normEn:normEs;
  return{cls:'close',text:'',html:`<b>Accepted as close</b> — not an exact match${extra}`+
    `<span class="fbcmp"><span class="fbl">You said</span> “${markDiff(h.said,h.ans,n)}”</span>`+
    `<span class="fbcmp"><span class="fbl">Answer</span> “${markDiff(h.ans,h.said,n)}”</span>${first}`+
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
