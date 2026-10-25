"""Japanese app: verb cards show how the verb conjugates (polite, て-form, negative, past), plus the example
sentence when there is one. Open on new cards; behind a 'Conjugation' button on reviews."""
import sys

JS = r'''
/* ---------- verb conjugation on verb cards ---------- */
// う-verbs that end in -iru/-eru (they look like る-verbs but aren't)
const GODAN_RU=new Set(['かえる:帰る','はいる:入る','いる:要る','きる:切る','しる:知る','はしる:走る','すべる:滑る','しゃべる:喋る','へる:減る','かぎる:限る','ける:蹴る','にぎる:握る','まいる:参る','てる:照る','ちる:散る','あせる:焦る','ねる:練る']);
const HONORIFIC=new Set(['くださる','いらっしゃる','おっしゃる','なさる']);
const isVerb=c=>c.type==='w'&&!/ます$/.test(c.kana)&&(/する$/.test(c.kana)||HONORIFIC.has(c.kana)||/^to /i.test(c.en.replace(/^\([^)]*\)\s*/,''))&&/[うくぐすつぬぶむる]$/.test(c.kana));
const A={う:'わ',く:'か',ぐ:'が',す:'さ',つ:'た',ぬ:'な',ぶ:'ば',む:'ま',る:'ら'},I={う:'い',く:'き',ぐ:'ぎ',す:'し',つ:'ち',ぬ:'に',ぶ:'び',む:'み',る:'り'};
const TE={う:'って',つ:'って',る:'って',む:'んで',ぶ:'んで',ぬ:'んで',く:'いて',ぐ:'いで',す:'して'};
// forms for one spelling (kanji or kana) of the verb; base = dictionary form, kana = its reading
function conjOf(base,kana,k){
  const stem=n=>base.slice(0,base.length-n);
  if(/する$/.test(kana)){const b=stem(2);return{pol:b+'します',te:b+'して',neg:b+'しない',past:b+'した'}}
  if(kana==='くる'){const b=base==='くる'?'':base.slice(0,-1);return base==='くる'?{pol:'きます',te:'きて',neg:'こない',past:'きた'}:{pol:b+'ます',te:b+'て',neg:b+'ない',past:b+'た'}}
  if(HONORIFIC.has(kana)){const b=stem(1);return{pol:b+'います',te:b+'って',neg:b+'らない',past:b+'った'}}  // くださる → くださいます
  const last=kana.slice(-1);
  const ichidan=last==='る'&&/[いきしちにひみりぎじぢびぴえけせてねへめれげぜでべぺ]る$/.test(kana)&&!GODAN_RU.has(kana+':'+k);
  if(ichidan){const b=stem(1);return{pol:b+'ます',te:b+'て',neg:b+'ない',past:b+'た'}}
  const b=stem(1),te=(kana==='いく'?'って':TE[last]);
  return{pol:b+I[last]+'ます',te:b+te,neg:(kana==='ある'?'':b)+(kana==='ある'?'ない':A[last]+'ない'),past:b+te.replace('て','た').replace('で','だ')};
}
function conjHtml(c,open){
  if(!isVerb(c))return '';
  let k=c.k,kana=c.kana;if(/する$/.test(kana)&&!/する$/.test(k))k+='する';
  const W=conjOf(k,kana,c.k),R=conjOf(kana,kana,c.k);
  const mode=S.set.ruby,rd=x=>mode==='romaji'?kanaRomaji(x):mode==='kana'?x:'';
  const row=(lbl,f)=>{const r=rd(R[f]);return `<tr><th>${lbl}</th><td><span class="cjw">${escH(W[f])}</span>${r&&(mode==='romaji'||W[f]!==R[f])?`<span class="cjr">${escH(r)}</span>`:''}</td></tr>`};
  const ex=c.ph&&!phraseOn(c)?`<div class="cjex">${markPh(c.ph[0])}<span>${escH(plainPh(c.ph[2]))}</span></div>`:'';
  if(!open)return `<button class="cjbtn" id="cjBtn">Conjugation ▸</button>`;
  return `<div class="conj"><table>${row('polite','pol')}${row('て-form','te')}${row('negative','neg')}${row('past','past')}</table>${ex}</div>`;
}
let showConj=false;
document.addEventListener('click',e=>{if(e.target.closest('#cjBtn')){showConj=true;render()}});
'''

def patch(p):
    s = open(p).read()
    if 'function conjHtml' in s: print('already', p); return
    R = [
      # fix typo card
      ("\n落る|おちる|ochiru|to fall; to drop", "\n落ちる|おちる|ochiru|to fall; to drop"),
      # render: on the answer side, after the alternatives
      ("`<div class=\"jp\">${ruby(shownCard())}</div>${cur.type==='k'&&S.set.ruby==='romaji'?`<div class=\"kana\">${cur.r}</div>`:''}`}${altsHtml()}</div>`;",
       "`<div class=\"jp\">${ruby(shownCard())}</div>${cur.type==='k'&&S.set.ruby==='romaji'?`<div class=\"kana\">${cur.r}</div>`:''}`}${altsHtml()}${conjHtml(cur,isNew||showConj)}</div>`;"),
      # reset per card
      ("function show(){triedWrong=false;cur=nextCard();revealed=false;", "function show(){triedWrong=false;showConj=false;cur=nextCard();revealed=false;"),
      ("    cur=nextCard();revealed=false;feedback=null;suggest=null;showAlts=false;", "    cur=nextCard();showConj=false;revealed=false;feedback=null;suggest=null;showAlts=false;"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:80]); s = s.replace(a, b, 1)
    i = s.index('/* ---------- telling you exactly what was accepted ---------- */'); s = s[:i] + JS + s[i:]
    css = '''
.conj{margin:12px auto 0;max-width:320px;text-align:left}
.conj table{width:100%;border-collapse:collapse;font-size:15px}
.conj th{font-weight:500;color:var(--muted);font-size:12.5px;padding:3px 10px 3px 0;white-space:nowrap;vertical-align:top}
.conj td{padding:3px 0}
.cjw{font-family:var(--jp,inherit);font-size:17px}
.cjr{display:block;font-size:12px;color:var(--muted)}
.cjex{margin-top:10px;font-size:16px;text-align:center}
.cjex span{display:block;font-size:13px;color:var(--muted);margin-top:2px}
.cjbtn{margin-top:10px;font-size:13px;color:var(--muted);text-decoration:underline;text-underline-offset:3px;padding:4px}
'''
    i = s.index('</style>'); s = s[:i] + css + s[i:]
    open(p, 'w').write(s); print('patched', p)

patch(sys.argv[1])
