"""Add a progress/stats screen and progress backup/restore to an app page (Japanese or Spanish)."""
import sys

HEADER_BTN = '''<button class="iconbtn" id="statsBtn" aria-label="Progress and stats"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M5 20V11M12 20V5M19 20v-6"/></svg></button>
    <button class="iconbtn" id="setBtn"'''

STATS_SECTION = '''  </header>

  <section id="stats" hidden aria-label="Your progress">
    <div class="st-head"><button class="iconbtn" id="statsBack" aria-label="Back to cards"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 18l-6-6 6-6"/></svg></button><h2>Your progress</h2></div>
    <div class="seg" role="group" aria-label="Direction"><button id="stJE" aria-pressed="true"></button><button id="stEJ" aria-pressed="false"></button></div>
    <div class="tiles">
      <div class="tile"><b id="stStreak">0</b><span>day streak</span></div>
      <div class="tile"><b id="stWeek">0</b><span>reviews this week</span></div>
      <div class="tile"><b id="stAcc">–</b><span>right this week</span></div>
      <div class="tile"><b id="stKnown">0</b><span>cards learned</span></div>
    </div>
    <div class="panel">
      <h3>Last 14 days</h3>
      <div class="bars" id="stBars" role="list"></div>
      <p class="cap" id="stBarInfo">Tap a day to see the details.</p>
    </div>
    <div class="panel">
      <h3>Cards by level</h3>
      <div class="legend"><span><i class="sw s-new"></i>New</span><span><i class="sw s-learn"></i>Learning</span><span><i class="sw s-known"></i>Known</span><span><i class="sw s-master"></i>Mastered</span></div>
      <div id="stDecks"></div>
      <p class="cap">Known: answered right and spaced out to a day or more. Mastered: next review is 3 weeks or more away.</p>
    </div>
    <div class="panel">
      <h3>Coming up</h3>
      <div class="due" id="stDue"></div>
    </div>
    <div class="panel">
      <h3>Trickiest cards</h3>
      <ol class="tricky" id="stTricky"></ol>
    </div>
  </section>'''

BACKUP_HTML = '''    <div class="backup">
      <span class="blabel">Progress backup</span>
      <div class="vr"><button class="test" id="bkSave">Save backup file</button><button class="test" id="bkRestore">Restore from file</button></div>
      <input type="file" id="bkFile" accept=".json,application/json,text/plain" hidden>
      <button class="btn primary" id="bkConfirm" hidden>Replace my progress with this backup</button>
      <p class="vnote" id="bkNote">Save your progress as a file, then restore it after reinstalling, on a new phone, or in the other version of the app.</p>
    </div>
    <button class="danger" id="reset">Reset all progress</button>'''

CSS = '''
/* ---------- stats screen ---------- */
.app.stats-open > :not(header):not(#stats){display:none!important}
#stats{display:flex;flex-direction:column;gap:14px}
#stats[hidden]{display:none}
.st-head{display:flex;align-items:center;gap:10px}
.st-head h2{margin:0;font-size:20px}
.tiles{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:2px}
.tile b{font-size:28px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.1}
.tile span{font-size:12.5px;color:var(--muted)}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:10px}
.panel h3{margin:0;font-size:14px;font-weight:600}
.cap{margin:0;font-size:12.5px;color:var(--muted)}
.bars{display:grid;grid-template-columns:repeat(14,1fr);gap:4px;align-items:end;height:120px;border-bottom:1px solid var(--line)}
.bars button{height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:stretch;padding:0;border-radius:4px 4px 0 0}
.bars .b{display:block;background:color-mix(in oklab,var(--accent) 55%,var(--surface));border-radius:4px 4px 0 0;min-height:0}
.bars .b.zero{height:2px!important;background:var(--line)}
.bars button.today .b{background:var(--accent)}
.bars button[aria-pressed="true"] .b{outline:2px solid var(--ink);outline-offset:1px}
.days{display:grid;grid-template-columns:repeat(14,1fr);gap:4px;font-size:10.5px;color:var(--muted);text-align:center;margin-top:-4px}
.legend{display:flex;flex-wrap:wrap;gap:10px;font-size:12px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:5px}
.sw{width:10px;height:10px;border-radius:3px;display:inline-block}
.s-new{background:var(--line)}
.s-learn{background:color-mix(in oklab,var(--accent) 30%,var(--surface))}
.s-known{background:color-mix(in oklab,var(--accent) 62%,var(--surface))}
.s-master{background:var(--accent)}
.drow{display:grid;gap:5px}
.drow .top{display:flex;justify-content:space-between;gap:8px;font-size:13.5px}
.drow .top span{color:var(--muted);font-variant-numeric:tabular-nums}
.pstack{display:flex;gap:2px;height:12px;background:var(--surface)}
.pstack i{display:block;height:100%;min-width:0}
.pstack i:first-child{border-radius:4px 0 0 4px}.pstack i:last-child{border-radius:0 4px 4px 0}.pstack i:only-child{border-radius:4px}
#stDecks{display:grid;gap:12px}
.due{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}
.due b{display:block;font-size:22px;font-weight:600;font-variant-numeric:tabular-nums}
.due span{font-size:12px;color:var(--muted)}
.tricky{margin:0;padding-left:20px;display:grid;gap:6px;font-size:14px}
.tricky .w{font-weight:600}
.tricky .m{color:var(--muted)}
.backup{display:grid;gap:8px;font-size:14px}
.backup .vr .test{flex:1}
'''

JS = r'''
/* ---------- progress log, stats screen and backup ---------- */
const DECKNAMES=typeof DECKS!=='undefined'?DECKS:LEVELS;
const APPNAME=KEY.startsWith('n5')?'nihongo':'espanol';
function dayKey(d){return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate()}
function logReview(g,isNew){
  S.log=S.log||{};const k=today();const e=S.log[k]||(S.log[k]={r:0,c:0,n:0});
  e.r++;if(g>=1)e.c++;if(isNew)e.n++;
  const cut=new Date(Date.now()-150*DAY);
  for(const key of Object.keys(S.log)){const [y,m,d]=key.split('-').map(Number);if(new Date(y,m-1,d)<cut)delete S.log[key]}
  save();
}
let statsDir=S.set.dir;
const cardById=new Map(CARDS.map(c=>[c.id,c]));
function stateOf(c,dir){return S.cards[dir+':'+c.id]}
function bucket(s){if(!s)return 'new';if(s.learning)return 'learn';return s.ivl>=21?'master':'known'}
function renderStats(){
  const log=S.log||{},dir=statsDir,now=Date.now();
  $('stJE').textContent=$('dJE').textContent;$('stEJ').textContent=$('dEJ').textContent;
  $('stJE').setAttribute('aria-pressed',dir==='je');$('stEJ').setAttribute('aria-pressed',dir==='ej');
  // last 14 days
  const days=[];for(let i=13;i>=0;i--){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()-i);const e=log[dayKey(d)]||{r:0,c:0,n:0};days.push({d,...e})}
  const max=Math.max(1,...days.map(x=>x.r));
  $('stBars').innerHTML=days.map((x,i)=>`<button role="listitem" data-i="${i}" class="${i===13?'today':''}" aria-label="${x.d.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'short'})}: ${x.r} reviews"><span class="b${x.r?'':' zero'}" style="height:${(x.r/max*100).toFixed(1)}%"></span></button>`).join('');
  let dl=$('stDays');if(!dl){dl=document.createElement('div');dl.id='stDays';dl.className='days';$('stBars').after(dl)}
  dl.innerHTML=days.map((x,i)=>`<span>${i===13?'Today':x.d.toLocaleDateString('en-GB',{weekday:'narrow'})}</span>`).join('').replace('<span>Today</span>','<span>•</span>');
  $('stBars').onclick=e=>{const b=e.target.closest('[data-i]');if(!b)return;const x=days[+b.dataset.i];
    document.querySelectorAll('#stBars button').forEach(q=>q.setAttribute('aria-pressed',q===b));
    const label=+b.dataset.i===13?'Today':x.d.toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'});
    $('stBarInfo').textContent=x.r?`${label}: ${x.r} reviews · ${x.c} right (${Math.round(x.c/x.r*100)}%) · ${x.n} new cards`:`${label}: no reviews`};
  $('stBarInfo').textContent=days.some(x=>x.r)?'Tap a day to see the details. Today is the darker bar.':'No reviews yet. Study some cards and your history appears here.';
  // streak and week
  let streak=0;for(let i=0;i<400;i++){const d=new Date();d.setDate(d.getDate()-i);const e=log[dayKey(d)];if(e&&e.r)streak++;else if(i>0)break}
  const wk=days.slice(7);const r=wk.reduce((a,x)=>a+x.r,0),c=wk.reduce((a,x)=>a+x.c,0);
  $('stStreak').textContent=streak;$('stWeek').textContent=r;$('stAcc').textContent=r?Math.round(c/r*100)+'%':'–';
  // cards by level
  let learned=0;const rows=[];
  for(const [dk,name] of Object.entries(DECKNAMES)){
    const cs=CARDS.filter(x=>x.deck===dk);if(!cs.length)continue;
    const n={new:0,learn:0,known:0,master:0};for(const x of cs)n[bucket(stateOf(x,dir))]++;
    learned+=n.known+n.master;
    const seg=['learn','known','master','new'].filter(k=>n[k]).map(k=>`<i class="s-${k}" style="flex:${n[k]}" title="${n[k]} ${k}"></i>`).join('');
    rows.push(`<div class="drow"><div class="top"><b>${name}</b><span>${n.known+n.master} of ${cs.length} learned${n.learn?` · ${n.learn} learning`:''}</span></div><div class="pstack">${seg}</div></div>`);
  }
  $('stDecks').innerHTML=rows.join('');$('stKnown').textContent=learned;
  // coming up
  const end=new Date();end.setHours(23,59,59,999);const t1=end.getTime()+DAY,t7=end.getTime()+7*DAY;
  let dueNow=0,tom=0,week=0;
  for(const [k,s] of Object.entries(S.cards)){if(!k.startsWith(dir+':'))continue;if(s.due<=now)dueNow++;else if(s.due<=t1)tom++;if(s.due>now&&s.due<=t7)week++}
  $('stDue').innerHTML=`<div><b>${dueNow}</b><span>due now</span></div><div><b>${tom}</b><span>tomorrow</span></div><div><b>${week}</b><span>next 7 days</span></div>`;
  // trickiest
  const tricky=Object.entries(S.cards).filter(([k,s])=>k.startsWith(dir+':')&&s.lapses>0).sort((a,b)=>b[1].lapses-a[1].lapses).slice(0,5)
    .map(([k,s])=>{const card=cardById.get(k.slice(3));return card?`<li><span class="w">${escH(card.k||card.es)}</span> <span class="m">· ${escH(card.en)} · missed ${s.lapses}×</span></li>`:''}).join('');
  $('stTricky').innerHTML=tricky||'<li class="m" style="list-style:none;margin-left:-20px">Nothing yet. Cards you forget after learning them show up here.</li>';
}
function openStats(){if(walking)stopWalk();statsDir=S.set.dir;$('settings').hidden=true;$('setBtn').setAttribute('aria-expanded',false);
  document.querySelector('.app').classList.add('stats-open');$('stats').hidden=false;renderStats();window.scrollTo(0,0)}
function closeStats(){document.querySelector('.app').classList.remove('stats-open');$('stats').hidden=true;render()}
$('statsBtn').onclick=()=>$('stats').hidden?openStats():closeStats();
$('statsBack').onclick=closeStats;
$('stJE').onclick=()=>{statsDir='je';renderStats()};$('stEJ').onclick=()=>{statsDir='ej';renderStats()};

/* backup */
function bkNote(t){$('bkNote').textContent=t}
window.__nativeSaved=ok=>{if(ok){S.lastBackup=Date.now();save()}bkNote(ok?'Backup saved.':'Backup not saved.')};
$('bkSave').onclick=()=>{
  const data=JSON.stringify({app:KEY,version:1,exported:new Date().toISOString(),data:S});
  const d=new Date(),name=`${APPNAME}-progress-${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}.json`;
  if(NAT&&NAT.saveFile){NAT.saveFile(name,data);bkNote('Choose where to save the backup…');return}
  try{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type:'application/json'}));a.download=name;document.body.appendChild(a);a.click();
    setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},2000);S.lastBackup=Date.now();save();bkNote(`Saved ${name} to your Downloads folder.`)}
  catch(e){bkNote('This browser couldn’t save the file.')}
};
let bkPending=null;
$('bkRestore').onclick=()=>{$('bkFile').value='';$('bkFile').click()};
$('bkFile').onchange=()=>{
  const f=$('bkFile').files[0];if(!f)return;const rd=new FileReader();
  rd.onload=()=>{bkPending=null;$('bkConfirm').hidden=true;
    let o;try{o=JSON.parse(rd.result)}catch(e){return bkNote('That file isn’t a progress backup.')}
    if(!o||!o.data||typeof o.data.cards!=='object')return bkNote('That file isn’t a progress backup.');
    if(o.app!==KEY)return bkNote(`That backup is from the ${o.app&&o.app.startsWith('n5')?'Japanese':'Spanish'} app. Restore it there instead.`);
    const n=Object.keys(o.data.cards).length,when=o.exported?new Date(o.exported).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}):'an unknown date';
    bkPending=o.data;$('bkConfirm').hidden=false;bkNote(`Backup from ${when} with ${n} studied cards. Restoring replaces your current progress.`)};
  rd.onerror=()=>bkNote('Couldn’t read that file.');rd.readAsText(f);
};
$('bkConfirm').onclick=()=>{if(!bkPending)return;S={...S,...bkPending,set:{...S.set,...(bkPending.set||{})}};save();bkNote('Progress restored.');setTimeout(()=>location.reload(),600)};
'''

def patch(p):
    s = open(p).read()
    if 'id="statsBtn"' in s: print('already', p); return
    R = [
        ('<button class="iconbtn" id="setBtn"', HEADER_BTN),
        ('    <button class="danger" id="reset">Reset all progress</button>', BACKUP_HTML),
        ('function grade(c,g){', 'function grade(c,g){const isNew=!st(c);gradeBase(c,g);logReview(g,isNew)}\nfunction gradeBase(c,g){'),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a); s = s.replace(a, b, 1)
    # stats section right after the header
    i = s.index('  </header>'); s = s[:i] + STATS_SECTION + s[i + len('  </header>'):]
    # header now has two icon buttons: group them
    s = s.replace('<button class="iconbtn" id="statsBtn"', '<div class="hbtns"><button class="iconbtn" id="statsBtn"', 1)
    j = s.index('id="setBtn"'); k = s.index('</button>', j) + len('</button>')
    s = s[:k] + '</div>' + s[k:]
    i = s.index('</style>'); s = s[:i] + CSS + '.hbtns{display:flex;gap:6px}\n' + s[i:]
    i = s.rindex('</script>'); s = s[:i] + JS + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
