import sys
def patch(p):
    s=open(p).read()
    if 'id="pocket"' in s: print('already',p); return
    R=[
    ("<span>Start walk mode</span></button>\n  </div>",
     "<span>Start walk mode</span></button>\n    <button class=\"btn\" id=\"pocketBtn\" hidden>Black screen (pocket mode)</button>\n  </div>\n  <div id=\"pocket\" hidden><p id=\"pocketStatus\"></p><p>Hold anywhere for 2 seconds to show the screen</p></div>"),
    (".grace{display:flex;gap:8px}",
     ".grace{display:flex;gap:8px}\n#pocket{position:fixed;inset:0;background:#000;z-index:100;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px;padding-bottom:max(40px,env(safe-area-inset-bottom,0px));touch-action:none;user-select:none;-webkit-user-select:none}\n#pocket p{margin:0;color:#262626;font-size:12px;text-align:center}"),
    ("function status(t){$('wStatus').textContent=t}",
     "function status(t){$('wStatus').textContent=t;const p=$('pocketStatus');if(p)p.textContent=t}\n"
     "// pocket mode: black screen that ignores touches; hold 2 s to exit\n"
     "function pocketOn(){$('pocket').hidden=false;try{document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen().catch(()=>{})}catch(e){}}\n"
     "function pocketOff(){$('pocket').hidden=true;try{document.fullscreenElement&&document.exitFullscreen()}catch(e){}}\n"
     "{let ht;const pk=()=>$('pocket');\n"
     " document.addEventListener('pointerdown',e=>{if(pk().hidden||!pk().contains(e.target))return;e.preventDefault();clearTimeout(ht);ht=setTimeout(pocketOff,2000)},true);\n"
     " ['pointerup','pointercancel','pointerleave'].forEach(t=>document.addEventListener(t,()=>clearTimeout(ht),true));\n"
     " document.addEventListener('click',e=>{if(!pk().hidden&&pk().contains(e.target)){e.preventDefault();e.stopPropagation()}},true)}"),
    ("  $('walkModes').hidden=true;",
     "  $('walkModes').hidden=true;$('pocketBtn').hidden=false;"),
    ("  $('walkModes').hidden=false;",
     "  $('walkModes').hidden=false;$('pocketBtn').hidden=true;pocketOff();"),
    ("$('walkBtn').onclick=()=>walking?stopWalk():startWalk();",
     "$('walkBtn').onclick=()=>walking?stopWalk():startWalk();\n$('pocketBtn').onclick=pocketOn;\n"
     "// if the phone locks, the browser pauses the page: stop cleanly and say why\n"
     "document.addEventListener('visibilitychange',()=>{if(walking&&document.visibilityState==='hidden'){stopWalk();status('Walk mode stopped because the screen locked — use pocket mode instead')}});"),
    ]
    for a,b in R:
        assert a in s,(p,a[:60]); s=s.replace(a,b,1)
    open(p,'w').write(s); print('patched',p)
for p in sys.argv[1:]: patch(p)
