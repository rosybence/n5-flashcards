import sys,re
NOTE=r"""let micErr='';
function showMicNote(){const n=$('micNote');n.hidden=false;
  let msg;
  if(!SR&&!NAT)msg='<strong>This browser can’t listen.</strong> Use Chrome (Android) or Safari (iPhone) to answer by voice. You can still study by tapping.';
  else if(micErr==='audio-capture')msg='<strong>The microphone is busy.</strong> Another app may be using it (for example the Android version of this app, a call or a voice recorder). Close it, then tap Try again.';
  else if(micErr==='network')msg='<strong>Speech recognition needs internet.</strong> Check your signal, then tap Try again.';
  else if(NAT)msg='<strong>The app isn’t allowed to use the microphone.</strong> Go to phone Settings → Apps → this app → Permissions → Microphone → Allow, then tap Try again.';
  else msg='<strong>Chrome isn’t allowed to use the microphone on this page.</strong> Tap the icon left of the web address → Permissions → Microphone → Allow. Also check phone Settings → Apps → Chrome → Permissions → Microphone. Then tap Try again.';
  n.innerHTML=msg+'<div class="row" style="margin-top:8px"><button class="btn" id="micRetry">Try again</button></div>';
  $('micRetry').onclick=()=>{micBlocked=false;micErr='';n.hidden=true;render()};
  render()}
"""
for p in sys.argv[1:]:
    s=open(p).read()
    if 'let micErr' in s: print('already',p);continue
    i=s.index('function showMicNote(){');j=s.index("render()}\n",i)+len("render()}\n")
    s=s[:i]+NOTE+s[j:]
    a="rec.onerror=e=>{if(/not-allowed|service-not-allowed|audio-capture/.test(e.error)){micBlocked=true;"
    assert s.count(a)==1,p
    s=s.replace(a,"rec.onerror=e=>{if(e.error==='network'){micErr='network'}if(/not-allowed|service-not-allowed|audio-capture/.test(e.error)){micErr=e.error;micBlocked=true;",1)
    open(p,'w').write(s);print('patched',p)
