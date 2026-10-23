"""Spanish app: on-phone speech recognition (Vosk) that is told the expected answer plus similar-sounding decoys."""
import sys

JS = r'''
/* ---------- on-phone speech recognition (Vosk, told the expected answer) ---------- */
const VK={state:'idle',worker:null,loading:null,cb:{},seq:0};
const VK_SHORT=['tu','tú','su','sus','tus','te','se','de','ya','yo','lo','la','le','el','en','un','mi','me','no','sí','si','todo','toda','tal','tan','que','qué'];
function vkWanted(){return S.set.vosk!=='off'&&typeof WebAssembly==='object'&&typeof Worker==='function'&&!!(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia)}
function vkUsable(){return vkWanted()&&VK.state!=='failed'}
function vkStatusText(){
  if(!vkWanted())return S.set.vosk==='off'?'Using your phone’s recognizer for Spanish.':'On-phone recognition isn’t supported here, so your phone’s recognizer is used.';
  return {idle:'On-phone Spanish recognition downloads its speech data (34 MB) the first time you speak.',loading:'Downloading Spanish speech data (34 MB, first time only)…',ready:'On-phone Spanish recognition is ready.',failed:'On-phone recognition couldn’t start, so your phone’s recognizer is used for now.'}[VK.state]}
function vkStatus(){const el=$('vkNote');if(el)el.textContent=vkStatusText()}
function vkLoad(){
  if(VK.state==='ready')return Promise.resolve();
  if(VK.loading)return VK.loading;
  VK.state='loading';vkStatus();
  VK.loading=new Promise((res,rej)=>{
    let w;try{w=new Worker('vosk/worker.js')}catch(e){return rej(e)}
    VK.worker=w;const to=setTimeout(()=>rej(new Error('timed out')),240000);
    w.onmessage=e=>{const m=e.data;
      if(m.t==='loaded'){clearTimeout(to);VK.state='ready';vkStatus();res()}
      else if(m.t==='error'&&!m.id){clearTimeout(to);rej(new Error(m.error))}
      else{const c=VK.cb[m.id];c&&c(m)}};
    w.onerror=e=>{clearTimeout(to);rej(new Error(e.message||'worker error'))};
    w.postMessage({t:'load',url:'es-small.tar.gz'});
  });
  VK.loading.catch(()=>{VK.state='failed';VK.loading=null;try{VK.worker&&VK.worker.terminate()}catch(e){}VK.worker=null;vkStatus()});
  return VK.loading;
}
function phraseES(s){return s.toLowerCase().replace(/[¿¡?!.,;:…"“”()]/g,' ').replace(/\s+/g,' ').trim()}
let vkIndex=null;
function vkDecoys(c){
  if(!vkIndex){vkIndex=[];for(const x of CARDS)for(const p of [x.es,...x.esA]){const q=phraseES(p).replace(/^(el|la|los|las|un|una)\s+/,'');if(q)vkIndex.push([q,phonEs(q)])}}
  const own=new Set([c.es,...c.esA].map(p=>phraseES(p).replace(/^(el|la|los|las|un|una)\s+/,'')));
  const target=phonEs(phraseES(c.es).replace(/^(el|la|los|las|un|una)\s+/,''));
  const scored=[];const seen=new Set();
  for(const [q,ph] of vkIndex){if(own.has(q)||seen.has(q))continue;seen.add(q);const sc=sim(ph,target);if(sc>=.5)scored.push([sc,q])}
  scored.sort((a,b)=>b[0]-a[0]);
  const out=scored.slice(0,6).map(x=>x[1]);
  if(target.length<=3)for(const w of VK_SHORT)if(!own.has(w))out.push(w);
  return out;
}
function vkGrammar(c){
  const set=new Set();
  const add=x=>{x=phraseES(x);if(!x)return;set.add(x);const m=x.match(/^(el|la|los|las|un|una)\s+(.+)$/);if(m)set.add(m[2])};
  [c.es,...c.esA].forEach(add);vkDecoys(c).forEach(add);
  return JSON.stringify([...set,'[unk]']);
}
async function listenVosk(c,ms,onHeard){
  const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true,channelCount:1}});
  const AC=window.AudioContext||window.webkitAudioContext;const ac=new AC();try{await ac.resume()}catch(e){}
  const src=ac.createMediaStreamSource(stream),node=ac.createScriptProcessor(4096,1,1);
  const id='v'+(++VK.seq);let partial='';const results=[];
  return new Promise(res=>{
    let done=false,t;
    const cleanup=()=>{try{node.disconnect();src.disconnect()}catch(e){}stream.getTracks().forEach(x=>x.stop());try{ac.close()}catch(e){}};
    const fin=()=>{if(done)return;done=true;clearTimeout(t);cleanup();
      const give=extra=>{delete VK.cb[id];const all=[...results,extra].filter(Boolean);res(all.length?all:(partial?[partial]:[]))};
      VK.cb[id]=m=>{if(m.t==='final')give(m.text)};
      VK.worker.postMessage({t:'stop',id});
      setTimeout(()=>{if(VK.cb[id])give('')},1500)};
    VK.cb[id]=m=>{if(m.t==='partial'){partial=m.text;onHeard&&onHeard(m.text)}else if(m.t==='result'){results.push(m.text);onHeard&&onHeard(m.text);fin()}};
    VK.worker.postMessage({t:'start',id,rate:ac.sampleRate,grammar:vkGrammar(c)});
    node.onaudioprocess=e=>{if(!done)VK.worker.postMessage({t:'audio',id,data:new Float32Array(e.inputBuffer.getChannelData(0))})};
    src.connect(node);node.connect(ac.destination);
    curRec={abort(){fin()}};
    t=setTimeout(fin,ms);
  });
}
'''

def patch(p):
    s = open(p).read()
    if 'const VK=' in s: print('already', p); return
    R = [
      ("async function listen(lang,ms,onHeard){\n  const gen=++listenGen,until=Date.now()+ms;\n  await new Promise(r=>setTimeout(r,250));\n  while(gen===listenGen){\n    const left=until-Date.now();if(left<700)return [];\n    const h=await (NAT?listenNative:listenWeb)(lang,left,onHeard);",
       """async function listen(lang,ms,onHeard){
  const gen=++listenGen;
  // Spanish answers: on-phone recognition that knows the expected answer (falls back to the phone's recognizer)
  let useVk=lang.startsWith('es')&&!!cur&&vkUsable();
  if(useVk&&VK.state!=='ready'){
    const prev=feedback;feedback={cls:'info',text:'Getting Spanish speech recognition ready (first time only: 34 MB)…'};render();
    try{await vkLoad()}catch(e){useVk=false}
    feedback=prev;render();if(gen!==listenGen)return [];
  }
  const until=Date.now()+ms;
  await new Promise(r=>setTimeout(r,250));
  while(gen===listenGen){
    const left=until-Date.now();if(left<700)return [];
    let h;
    if(useVk){try{h=await listenVosk(cur,left,onHeard)}catch(e){VK.state='failed';vkStatus();useVk=false;continue}}
    else h=await (NAT?listenNative:listenWeb)(lang,left,onHeard);"""),
      ('    <label>Answer checking',
       '    <label>Spanish speech recognition <select id="sVosk"><option value="on">On-phone (best for single words)</option><option value="off">Phone’s recognizer</option></select></label>\n    <p class="vnote" id="vkNote"></p>\n    <label>Answer checking'),
      ("$('sCheck').value=S.set.check||'lenient';",
       "$('sVosk').value=S.set.vosk==='off'?'off':'on';$('sVosk').onchange=()=>{S.set.vosk=$('sVosk').value;if(S.set.vosk!=='off'&&VK.state==='failed')VK.state='idle';save();vkStatus()};vkStatus();\n$('sCheck').value=S.set.check||'lenient';"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:60]); s = s.replace(a, b, 1)
    i = s.index('/* ---------- answer checking ---------- */'); s = s[:i] + JS + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
