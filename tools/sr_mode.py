import sys
for p in sys.argv[1:]:
    s=open(p).read()
    if 'id="sSrMode"' in s: print('already',p);continue
    R=[("  NAT.listen(lang,id)})}","  if(NAT.listenWith)NAT.listenWith(lang,id,S.set.srMode==='search'?'search':'chrome');else NAT.listen(lang,id)})}"),
       ("    <label>New cards per day",'    <label id="srModeRow" hidden>Speech recognition <select id="sSrMode"><option value="chrome">Like Chrome</option><option value="search">Short words (voice search)</option></select></label>\n    <label>New cards per day'),
       ("$('setBtn').onclick=","$('srModeRow').hidden=!(NAT&&NAT.listenWith);$('sSrMode').value=S.set.srMode==='search'?'search':'chrome';$('sSrMode').onchange=()=>{S.set.srMode=$('sSrMode').value;save()};\n$('setBtn').onclick=")]
    for a,b in R:
        assert s.count(a)==1,(p,a[:50]);s=s.replace(a,b,1)
    open(p,'w').write(s);print('patched',p)
