"""Cards you already know don't use up the daily new-card allowance; higher limits."""
import sys
def patch(p):
    s=open(p).read()
    if 'knewIt' in s: print('already',p);return
    R=[("<option>20</option><option>30</option></select></label>",
        "<option>20</option><option>30</option><option>50</option><option>100</option><option value=\"100000\">No limit</option></select></label>\n    <p class=\"vnote\" style=\"margin:-4px 0 4px\">Words you already know (<b>Know it</b>, or right first time in walk mode) don’t count towards this.</p>"),
       ("['Again','Hard','Good','Easy'].map((n,i)=>`<button data-g=\"${i}\">${n}<small>",
        "['Again','Hard','Good',s?'Easy':'Know it'].map((n,i)=>`<button data-g=\"${i}\">${n}<small>"),
       ("    let ok=true;\n","    let ok=true,knewIt=false;\n"),
       ("      ok=heard!==null&&judgeShow(cur,heard);","      ok=heard!==null&&judgeShow(cur,heard);knewIt=ok&&!st(cur);"),
       ("    grade(cur,ok?2:0);lastId=cur.id;","    grade(cur,ok?(knewIt?3:2):0);lastId=cur.id;"),
    ]
    for a,b in R:
        assert s.count(a)==1,(p,a[:60]);s=s.replace(a,b)
    # only cards you didn't already know count as new for the day
    for a in ("if(!st(c))S.newDone[S.set.dir]++;",):
        assert s.count(a)==1,(p,a);s=s.replace(a,"if(!st(c)&&g<3)S.newDone[S.set.dir]++;")
    open(p,'w').write(s);print('patched',p)
for p in sys.argv[1:]:patch(p)
