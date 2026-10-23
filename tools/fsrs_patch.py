"""Switch both apps to FSRS-6 scheduling (with the classic SM-2 kept as an option), log every review."""
import sys
CORE = open('/home/claude/tools/fsrs_core.js').read()

GLUE = r'''
const dayNo=ts=>Math.floor((ts-new Date(ts).getTimezoneOffset()*60000)/DAY);   // local calendar day
// memory state; cards studied before FSRS start from their SM-2 interval and ease
function fState(cs){
  if(cs&&cs.fs>0)return{s:cs.fs,d:cs.fd};
  if(cs&&!cs.learning&&cs.ivl>0)return{s:Math.max(cs.ivl,0.1),d:fClamp(5+(2.5-(cs.ease||2.5))*4,1,10)};
  return null;
}
function scheduleFSRS(prev,g,now){
  const G=g+1,ret=+S.set.retention||0.9;
  const cs=prev?{...prev}:{ivl:0,ease:2.5,reps:0,lapses:0,step:0,learning:true};
  const st0=fState(prev);
  const last=prev&&(prev.last||(prev.due&&prev.ivl?prev.due-prev.ivl*DAY:0));
  const t=st0&&last?Math.max(0,dayNo(now)-dayNo(last)):0;
  const st=fNextState(st0,t,G);
  cs.fs=st.s;cs.fd=st.d;cs.last=now;cs.reps=(cs.reps||0)+1;cs.ease=cs.ease||2.5;
  if(cs.learning){
    // learning steps (1 min, 10 min) as before, then FSRS takes over
    if(G===1){cs.step=0;cs.due=now+STEPS[0]*MIN}
    else if(G===2){cs.due=now+Math.round(STEPS[Math.min(cs.step,STEPS.length-1)]*1.5)*MIN}
    else if(G===3){cs.step++;if(cs.step>=STEPS.length){cs.learning=false;cs.ivl=fIvl(st.s,ret);cs.due=now+cs.ivl*DAY}else cs.due=now+STEPS[cs.step]*MIN}
    else{cs.learning=false;const good=fIvl(fNextState(st0,t,3).s,ret);cs.ivl=Math.max(fIvl(st.s,ret),good+1);cs.due=now+cs.ivl*DAY}
  }else if(G===1){cs.lapses=(cs.lapses||0)+1;cs.learning=true;cs.step=1;cs.ivl=fIvl(st.s,ret);cs.due=now+STEPS[1]*MIN}
  else{
    // Hard < Good < Easy, at least a day apart (as in the reference scheduler)
    const iv=[2,3,4].map(x=>fIvl(fNextState(st0,t,x).s,ret));
    const a=Math.min(iv[0],36500),b=Math.min(Math.max(iv[1],a+1),36500),c=Math.min(Math.max(iv[2],b+1),36500);
    cs.ivl=[a,b,c][G-2];cs.due=now+cs.ivl*DAY;
  }
  return cs;
}
function schedule(cs,g,now){return S.set.algo==='sm2'?scheduleSM2(cs,g,now):scheduleFSRS(cs,g,now)}
'''

SETTINGS = ('    <label>Scheduling <select id="sAlgo"><option value="fsrs">FSRS (recommended)</option><option value="sm2">Classic (SM-2)</option></select></label>\n'
            '    <label>Target memory <select id="sRet"><option value="0.85">85% · fewer reviews</option><option value="0.9">90%</option><option value="0.95">95% · more reviews</option></select></label>\n')

def patch(p):
    s = open(p).read()
    if 'scheduleFSRS' in s: print('already', p); return
    R = [
      ("function schedule(cs,g,now){", "function scheduleSM2(cs,g,now){"),
      ("gradeBase(c,g);logReview(g,isNew)}",
       "gradeBase(c,g);logReview(g,isNew);(S.revlog=S.revlog||[]).push([ck(c),Date.now(),g]);if(S.revlog.length>20000)S.revlog.splice(0,S.revlog.length-20000);save()}"),
      ("    <label>New cards per day", SETTINGS + "    <label>New cards per day"),
      ("$('setBtn').onclick=",
       "$('sAlgo').value=S.set.algo==='sm2'?'sm2':'fsrs';$('sAlgo').onchange=()=>{S.set.algo=$('sAlgo').value;save();render()};\n"
       "$('sRet').value=String(S.set.retention||0.9);$('sRet').onchange=()=>{S.set.retention=+$('sRet').value;save();render()};\n$('setBtn').onclick="),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:60]); s = s.replace(a, b, 1)
    i = s.index('function scheduleSM2(cs,g,now){'); s = s[:i] + CORE + GLUE + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
