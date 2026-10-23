import sys
for p in sys.argv[1:]:
    s=open(p).read()
    R=[("feedback={cls:'ok',text:(triedWrong?'Got it on another try — heard “':'Correct — heard “')+heard[0]",
        "feedback={cls:'ok',text:'Correct — heard “'+heard[0]"),
       ("  suggest=triedWrong?0:2;doReveal();","  suggest=2;doReveal();")]
    if 'app.html' in p and 'function phonEs' not in s:
        R.append(("  const close=(h,t)=>h===t||(t.length>3&&","  const close=(h,t)=>phonMatch(h,t)||h===t||(t.length>3&&"))
        R.append(("function judge(c,heard){","""// Spanish sounds phones often mix up: b/v, ll/y, z/c/s, silent h, qu/k, g/j
function phonEs(s){return s.replace(/\\s+/g,'').replace(/ch/g,'§').replace(/h/g,'').replace(/§/g,'ch').replace(/v/g,'b').replace(/ll/g,'y').replace(/y$/,'i')
  .replace(/z/g,'s').replace(/c([ei])/g,'s$1').replace(/qu/g,'k').replace(/c/g,'k').replace(/g([ei])/g,'j$1').replace(/gu([ei])/g,'g$1').replace(/(.)\\1+/g,'$1')}
function phonMatch(h,t){const a=phonEs(h),b=phonEs(t);return a===b||(b.length>=5&&sim(a,b)>=.82)}
function judge(c,heard){"""))
    for a,b in R:
        assert s.count(a)==1,(p,a[:60]);s=s.replace(a,b,1)
    open(p,'w').write(s);print('patched',p)
