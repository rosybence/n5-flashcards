import sys
ALT="(()=>{const o=[...new Set(heard.slice(1).filter(x=>x&&x.trim()&&x!==heard[0]))].slice(0,3);return o.length?' (or “'+o.join('”, “')+'”)':''})()"
for p in sys.argv[1:]:
    s=open(p).read()
    if 'heardAlts' in s: print('already',p);continue
    s=s.replace("function judge(c,heard){","function heardAlts(heard){return "+ALT+"}\nfunction judge(c,heard){",1)
    a="text:'Not quite — heard “'+heard[0]+'”. Try again, or tap Show answer.'"
    assert s.count(a)==1,(p,'mic');s=s.replace(a,"text:'Not quite — heard “'+heard[0]+'”'+heardAlts(heard)+'. Try again, or tap Show answer.'",1)
    b="(ok?'Correct — heard “':'Not quite — heard “')+heard[0]+'”'"
    assert s.count(b)==1,(p,'walk');s=s.replace(b,b+"+(ok?'':heardAlts(heard))",1)
    c="  $('vNote').innerHTML="
    assert s.count(c)==1,(p,'note')
    s=s.replace(c,"  let rec='';try{rec=NAT&&NAT.recognizerName?NAT.recognizerName():''}catch(e){}\n  $('vNote').innerHTML=(rec?'Listening with '+rec+' speech recognition. ':'')+",1)
    open(p,'w').write(s);print('patched',p)
