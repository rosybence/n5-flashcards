"""Let the web apps use the Android app's native voice + speech recognition when running inside it."""
import sys
ADAPTER = r'''/* ---------- native Android app bridge (used only inside the installed Android app) ---------- */
const NAT=window.NativeApp||null;
let _nid=0;const _ntts={},_nsr={};
window.__nativeTtsDone=id=>{const f=_ntts[id];if(f){delete _ntts[id];f()}};
window.__nativeSr=(id,kind,data)=>{const h=_nsr[id];if(h)h[kind](data)};
function speakNative(text,lang){return new Promise(res=>{const id='t'+(++_nid);_ntts[id]=res;
  NAT.speak(text,lang,lang.startsWith('en')?1:+S.set.rate,id);setTimeout(()=>window.__nativeTtsDone(id),4000+text.length*300)})}
function listenNative(lang,ms,onHeard){return new Promise(res=>{
  const id='r'+(++_nid);let interim='',done=false,t;
  const fin=v=>{if(done)return;done=true;clearTimeout(t);delete _nsr[id];curRec=null;res(v)};
  _nsr[id]={partial:x=>{if(x){interim=x;onHeard&&onHeard(x)}},result:a=>fin(a&&a.length?a:interim?[interim]:[]),
    error:c=>{if(c==='not-allowed'){micBlocked=true;showMicNote();fin(null)}else fin(interim?[interim]:[])}};
  curRec={abort(){try{NAT.abortListening()}catch(e){}fin(interim?[interim]:[])}};
  t=setTimeout(()=>{try{NAT.stopListening()}catch(e){}t=setTimeout(()=>fin(interim?[interim]:[]),2000)},ms);
  NAT.listen(lang,id)})}
'''
R = [
 ("/* ---------- speech out ---------- */", ADAPTER + "/* ---------- speech out ---------- */"),
 ("function speak(text,lang){return new Promise(res=>{", "function speak(text,lang){return NAT?speakNative(text,lang):speakWeb(text,lang)}\nfunction speakWeb(text,lang){return new Promise(res=>{"),
 ("function listen(lang,ms,onHeard){return new Promise(res=>{", "function listen(lang,ms,onHeard){return NAT?listenNative(lang,ms,onHeard):listenWeb(lang,ms,onHeard)}\nfunction listenWeb(lang,ms,onHeard){return new Promise(res=>{"),
 ("let micBlocked=!SR,curRec=null;", "let micBlocked=NAT?!NAT.srAvailable():!SR,curRec=null;"),
 ("walking=false;try{speechSynthesis.cancel()}catch(e){}", "walking=false;try{NAT?(NAT.stopSpeaking(),NAT.keepAwake(false)):speechSynthesis.cancel()}catch(e){}"),
 ("walking=true;userActed=true;", "walking=true;userActed=true;try{NAT&&NAT.keepAwake(true)}catch(e){}"),
 ("function pocketOn(){", "function pocketOn(){try{NAT&&NAT.immersive(true)}catch(e){}"),
 ("function pocketOff(){", "function pocketOff(){try{NAT&&NAT.immersive(false)}catch(e){}"),
]
for p in sys.argv[1:]:
    s = open(p).read()
    if 'const NAT=window.NativeApp' in s: print('already', p); continue
    for a, b in R:
        assert s.count(a) == 1, (p, a); s = s.replace(a, b, 1)
    open(p, 'w').write(s); print('patched', p)
