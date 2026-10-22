import sys,re
NEW=r"""$('mic').onclick=async()=>{
  if(!cur||revealed||micBlocked)return;
  const b=$('mic');
  if(b.classList.contains('listening')){abortListening();return}   // tap again to stop
  b.classList.add('listening');b.lastChild.textContent='Listening…';
  feedback={cls:'info',text:'Listening… say your answer'};render();b.classList.add('listening');
  const [,lang]=answerOf(cur);
  const heard=await listen(lang,7000,h=>{if(h){feedback={cls:'info',text:'Heard: '+h};render();b.classList.add('listening')}});
  b.classList.remove('listening');b.lastChild.textContent='Speak';
  if(heard===null){feedback=null;return render()}
  if(!heard.length||!heard.some(x=>x&&x.trim())){feedback={cls:'no',text:'Didn’t catch that. Tap Speak to try again.'};return render()}
  const ok=judge(cur,heard);tone(ok);lastHeard=heard[0];
  if(!ok){triedWrong=true;feedback={cls:'no',text:'Not quite — heard “'+heard[0]+'”. Try again, or tap Show answer.'};return render()}
  feedback={cls:'ok',text:(triedWrong?'Got it on another try — heard “':'Correct — heard “')+heard[0]+'”'+(casualHit(cur,heard)?' · casual form':'')};
  suggest=triedWrong?0:2;doReveal();
};
"""
for p in sys.argv[1:]:
    s=open(p).read()
    if 'let triedWrong' in s: print('already',p);continue
    i=s.index("$('mic').onclick=async()=>{");j=s.index("\n};\n",i)+4
    s=s[:i]+NEW+s[j:]
    for a,b2 in (("function show(){","let triedWrong=false;\nfunction show(){triedWrong=false;"),
                 ("$('reveal').onclick=()=>{if(cur&&!revealed){suggest=null;doReveal()}};","$('reveal').onclick=()=>{if(cur&&!revealed){if(triedWrong)suggest=0;else suggest=null;abortListening();doReveal()}};")):
        assert s.count(a)==1,(p,a);s=s.replace(a,b2,1)
    open(p,'w').write(s);print('patched',p)
