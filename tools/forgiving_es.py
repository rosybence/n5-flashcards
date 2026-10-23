import sys
p=sys.argv[1];s=open(p).read()
R=[
("function phonMatch(h,t){const a=phonEs(h),b=phonEs(t);return a===b||(b.length>=5&&sim(a,b)>=.82)}",
"""// Forgiving mode: Spanish consonants between vowels are soft, so phones often swap b/d/g/l/r/y or drop a d
let lastLenient=false;
const SOFT='bdglry';
function softNear(a,b){
  if(b.length<4)return false;
  if(a.length===b.length){let d=0,ok=true;for(let i=0;i<a.length;i++)if(a[i]!==b[i]){d++;if(!(SOFT.includes(a[i])&&SOFT.includes(b[i])))ok=false}return d===1&&ok}
  if(Math.abs(a.length-b.length)===1){const [l,sh]=a.length>b.length?[a,b]:[b,a];
    for(let i=0;i<l.length;i++)if('dbg'.includes(l[i])&&l.slice(0,i)+l.slice(i+1)===sh)return true}
  return false}
function phonMatch(h,t){const a=phonEs(h),b=phonEs(t);if(a===b||(b.length>=5&&sim(a,b)>=.82))return true;
  if(S.set.check!=='strict'&&softNear(a,b)){lastLenient=true;return true}return false}"""),
("function judge(c,heard){\n  if(!heard||!heard.length)return false;","function judge(c,heard){\n  lastLenient=false;\n  if(!heard||!heard.length)return false;"),
("    <label>New cards per day","    <label>Answer checking <select id=\"sCheck\"><option value=\"lenient\">Forgiving</option><option value=\"strict\">Strict</option></select></label>\n    <label>New cards per day"),
("$('sTypes').value=S.set.types;","$('sCheck').value=S.set.check||'lenient';$('sCheck').onchange=()=>{S.set.check=$('sCheck').value;save()};\n$('sTypes').value=S.set.types;"),
]
for a,b in R:
    assert s.count(a)==1,a[:60];s=s.replace(a,b,1)
n=s.count("+(casualHit(cur,heard)?' · casual form':'')")
s=s.replace("+(casualHit(cur,heard)?' · casual form':'')","+(casualHit(cur,heard)?' · casual form':'')+(ok&&lastLenient?' · close enough':'')")
s=s.replace("feedback={cls:'ok',text:'Correct — heard “'+heard[0]+'”'+(casualHit(cur,heard)?' · casual form':'')+(ok&&lastLenient","feedback={cls:'ok',text:'Correct — heard “'+heard[0]+'”'+(casualHit(cur,heard)?' · casual form':'')+(lastLenient")
open(p,'w').write(s);print('ok',n)
