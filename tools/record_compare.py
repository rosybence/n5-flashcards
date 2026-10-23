"""Record & compare: record your answer, then hear it next to the native audio and mark yourself."""
import sys

HTML = '''    <div class="mark" id="mark"></div>
    <div class="rc" id="rcRow">
      <button class="btn" id="rcBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/></svg><span>Record &amp; compare</span></button>
      <button class="btn" id="rcMine" hidden>▶ Mine</button>
      <button class="btn" id="rcNative" hidden>▶ Native</button>
    </div>'''

CSS = '''
.rc{display:flex;gap:8px}
.rc .btn{padding:11px 8px;font-size:14px}
.rc #rcBtn{flex:1.6}
.rc #rcBtn.recording{background:var(--bad);border-color:var(--bad);color:var(--surface)}
'''

JS = r'''
/* ---------- record & compare: hear yourself next to the native audio ---------- */
let rcUrl=null,rcBusy=false,rcCard=null,rcStop=null;
function rcReset(){if(rcUrl){URL.revokeObjectURL(rcUrl);rcUrl=null}rcCard=cur&&cur.id;$('rcMine').hidden=true;$('rcNative').hidden=true;
  $('rcBtn').classList.remove('recording');$('rcBtn').lastChild.textContent='Record & compare'}
function rcPlay(url){return new Promise(res=>{const a=new Audio(url);a.onended=res;a.onerror=res;a.play().catch(res)})}
async function rcNativePlay(){const [t,l]=answerOf(cur);await speak(t,l)}
async function rcRecord(){
  if(rcStop){rcStop();return}
  if(rcBusy||!cur)return;
  if(!(navigator.mediaDevices&&window.MediaRecorder)){feedback={cls:'no',text:'Recording isn’t supported in this browser.'};return render()}
  rcBusy=true;const b=$('rcBtn');
  try{
    try{speechSynthesis.cancel()}catch(e){}try{NAT&&NAT.stopSpeaking()}catch(e){}
    const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
    const mr=new MediaRecorder(stream),chunks=[];
    mr.ondataavailable=e=>{if(e.data&&e.data.size)chunks.push(e.data)};
    const stopped=new Promise(r=>mr.onstop=r);
    mr.start();b.classList.add('recording');b.lastChild.textContent='Recording… tap to stop';
    const auto=setTimeout(()=>rcStop&&rcStop(),5000);
    rcStop=()=>{clearTimeout(auto);rcStop=null;if(mr.state!=='inactive')mr.stop()};
    await stopped;stream.getTracks().forEach(t=>t.stop());b.classList.remove('recording');
    if(rcUrl)URL.revokeObjectURL(rcUrl);
    rcUrl=URL.createObjectURL(new Blob(chunks,{type:mr.mimeType||'audio/webm'}));
    b.lastChild.textContent='Playing yours…';await rcPlay(rcUrl);
    await new Promise(r=>setTimeout(r,350));
    b.lastChild.textContent='Playing native…';await rcNativePlay();
    $('rcMine').hidden=false;$('rcNative').hidden=false;b.lastChild.textContent='Record again';
  }catch(e){
    b.classList.remove('recording');b.lastChild.textContent='Record & compare';
    feedback={cls:'no',text:'Couldn’t record: the microphone isn’t available. Check the app’s microphone permission.'};render();
  }finally{rcBusy=false;rcStop=null}
}
$('rcBtn').onclick=rcRecord;
$('rcMine').onclick=()=>{if(rcUrl)rcPlay(rcUrl)};
$('rcNative').onclick=rcNativePlay;
window.__rcReady=true;rcReset();
'''

def patch(p):
    s = open(p).read()
    if 'id="rcBtn"' in s: print('already', p); return
    a = '    <div class="mark" id="mark"></div>'
    assert s.count(a) == 1; s = s.replace(a, HTML, 1)
    # new card -> reset the recording
    a = 'function render(){'
    assert s.count(a) == 1; s = s.replace(a, 'function render(){\n  if(window.__rcReady&&(cur&&cur.id)!==rcCard)rcReset();', 1)
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]
    i = s.rindex('</script>'); s = s[:i] + JS + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
