"""Walk mode: keep listening for the whole answer time; never reveal early because the recognizer gave up."""
import sys
for p in sys.argv[1:]:
    s=open(p).read()
    if 'listenGen' in s: print('already',p); continue
    R=[
     ("function listen(lang,ms,onHeard){return NAT?listenNative(lang,ms,onHeard):listenWeb(lang,ms,onHeard)}",
      """// keep listening until the answer time is up: phone recognizers often stop after a second or two of silence
let listenGen=0;
function abortListening(){listenGen++;try{curRec&&curRec.abort()}catch(e){}}
async function listen(lang,ms,onHeard){
  const gen=++listenGen,until=Date.now()+ms;
  await new Promise(r=>setTimeout(r,250));
  while(gen===listenGen){
    const left=until-Date.now();if(left<700)return [];
    const h=await (NAT?listenNative:listenWeb)(lang,left,onHeard);
    if(h===null)return null;
    if(gen!==listenGen||h.some(x=>x&&x.trim()))return h;
    await new Promise(r=>setTimeout(r,200));
  }
  return [];
}"""),
     ("error:c=>{if(c==='not-allowed'){","error:c=>{if(c==='not-allowed'||c==='unavailable'){"),
    ]
    for a,b in R:
        assert s.count(a)==1,(p,a[:50]);s=s.replace(a,b,1)
    # every early stop goes through abortListening so the loop above ends
    n=s.count("try{curRec&&curRec.abort()}catch(e){}")
    s=s.replace("try{curRec&&curRec.abort()}catch(e){}","abortListening();")
    s=s.replace("function abortListening(){listenGen++;abortListening();}","function abortListening(){listenGen++;try{curRec&&curRec.abort()}catch(e){}}")
    # mic unavailable mid-walk: give the normal thinking pause instead of revealing at once
    a="      if(!walking)break;\n      ok=heard!==null&&judge(cur,heard);"
    assert s.count(a)==1,(p,'walk')
    s=s.replace(a,"      if(!walking)break;\n      if(heard===null){for(let t=S.set.gap;t>0&&walking;t--){status('Think of the answer… '+t);await wait(1000)}if(!walking)break}\n      ok=heard!==null&&judge(cur,heard);",1)
    open(p,'w').write(s);print('patched',p,n)
