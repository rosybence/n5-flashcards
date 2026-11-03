"""Japanese app: separate conjugation cards (polite, て-form, negative, past) for each verb, prompted by English.
They unlock once the verb itself has been learned. The conjugation table stays only behind its button.
Usage: python3 conj_cards_jp.py <app.html> <verb_english.txt>"""
import sys, json

def patch(p, ven_path):
    s = open(p).read()
    if 'function makeConjCards' in s: print('already', p); return
    VEN = {}
    for l in open(ven_path, encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        k, base, past = (l.rstrip('\n').split('|') + ['', ''])[:3]
        if base != 'SKIP': VEN[k] = [base, past]
    JS = r'''
/* ---------- conjugation cards: one form of a verb per card, unlocked once you know the verb ---------- */
const VEN=''' + json.dumps(VEN, ensure_ascii=False, separators=(',', ':')) + r''';
const CONJ_LABEL={pol:'polite',te:'て-form',neg:'negative',past:'past'};
const IT_VERBS=new Set(['開く','消える','曇る','咲く','閉まる','止まる','鳴く','晴れる','吹く','降る','鳴る','沸く','聞こえる','止む','壊れる','揺れる','落ちる','決まる','足りる','無くなる','光る','残る','増える','乾く','暮れる','空く','変わる','済む','見える','折れる','見つかる','直る','続く','焼ける','冷える','点く','割れる','込む','役に立つ','違う','故障']);
// English 3rd person for "it …": go→goes, carry→carries, rain→rains
const third=w=>w==='have'?'has':w==='do'?'does':w==='go'?'goes':/(s|sh|ch|x|z|o)$/.test(w)?w+'es':/[^aeiou]y$/.test(w)?w.slice(0,-1)+'ies':w+'s';
function conjPrompt(base,past,f,k){
  const it=IT_VERBS.has(k)||IT_VERBS.has(k.replace(/する$/,'')),they=k==='くれる',be=/^be /.test(base),able=base==='be able to';
  const subj=it?'it':they?'they':'I';
  const [w0,...rest]=base.split(' '),tail=rest.length?' '+rest.join(' '):'';
  if(f==='te')return (able?'can':base)+' and… (て-form)';
  if(f==='pol'){if(able)return 'I can (polite)';if(be)return (it?'it is':'I am')+' '+base.slice(3)+' (polite)';
    return subj+' '+(it?third(w0)+tail:base)+' (polite)'}
  if(f==='neg'){if(able)return "I can't";if(be)return (it?"it isn't":"I'm not")+' '+base.slice(3);
    return subj+' '+(it?"doesn't":"don't")+' '+base}
  return subj+' '+(be&&!it?past:past)}
function makeConjCards(){
  const out=[],byBase={};
  for(const v of CARDS){const en=isVerb(v)&&(VEN[v.k]||VEN[v.k+'する']);if(!en)continue;
    const [base,past]=en;let k=v.k;if(/する$/.test(v.kana)&&!/する$/.test(k))k+='する';
    const W=conjOf(k,v.kana,v.k),R=conjOf(v.kana,v.kana,v.k);
    const polNeg=s=>s.replace(/ます$/,'ません'),polPast=s=>s.replace(/ます$/,'ました');
    const F={pol:[W.pol,R.pol,[]],te:[W.te,R.te,[]],neg:[W.neg,R.neg,[[polNeg(W.pol),polNeg(R.pol),'polite']]],past:[W.past,R.past,[[polPast(W.pol),polPast(R.pol),'polite']]]};
    for(const f in F){const [wk,rk,alts]=F[f];
      for(const [a,ar,note] of alts){READ[a]=[ar,kanaRomaji(ar)];if(note)NOTE[a]=note}
      const c={id:'cj:'+f+':'+v.id,k:wk,kana:rk,r:kanaRomaji(rk),en:conjPrompt(base,past,f,v.k),type:'w',deck:v.deck,jl:[],pic:v.pic,
        alts:alts.map(x=>x[0]),casual:new Set(),conj:f,base:v};
      out.push(c);(byBase[base+'|'+f]=byBase[base+'|'+f]||[]).push(c)}
  }
  // verbs that share an English meaning (出る / 出かける "go out") accept each other's forms
  for(const g of Object.values(byBase))if(g.length>1)for(const c of g)for(const o of g)if(o!==c){
    for(const x of [o.k,...o.alts])if(!c.alts.includes(x)&&x!==c.k){c.alts.push(x);if(!READ[x])READ[x]=[o.kana,o.r]}}
  // place each verb's cards straight after the verb, so they come up soon after you've learned it
  for(const c of out.slice().reverse()){const i=CARDS.indexOf(c.base);CARDS.splice(i+1,0,c)}
  return out.length;
}
const CONJ_COUNT=makeConjCards();
const conjUnlocked=c=>!c.conj||(()=>{const s=st(c.base);return !!s&&!s.learning})();
'''
    R = [
      ("const isVerb=c=>c.type==='w'&&!/ます$/.test(c.kana)&&", "const isVerb=c=>c.type==='w'&&!c.conj&&!/ます$/.test(c.kana)&&"),
      ("const n=pool().find(c=>c.deck===dk&&!st(c)&&c.id!==lastId&&sk(c));if(n)return n}",
       "const n=pool().find(c=>c.deck===dk&&!st(c)&&c.id!==lastId&&sk(c)&&conjUnlocked(c));if(n)return n}"),
      # tag: show it's a conjugation card, level of its verb
      ("${cur.type==='p'?' · Phrase':''}${ph?' · In a sentence':''} · ${cur.type==='k'?DECKS[cur.deck]:(JW[cur.k]||JW[cur.kana])?'JLPT '+(JW[cur.k]||JW[cur.kana]):'Extra'}",
       "${cur.type==='p'?' · Phrase':''}${ph?' · In a sentence':''}${cur.conj?' · '+CONJ_LABEL[cur.conj]+' of '+escH(cur.base.k):''} · ${cur.type==='k'?DECKS[cur.deck]:(()=>{const b=cur.conj?cur.base:cur,l=JW[b.k]||JW[b.kana];return l?'JLPT '+l:'Extra'})()}"),
      # table only behind its button
      ("${conjHtml(cur,isNew||showConj)}", "${conjHtml(cur,showConj)}"),
      # stats: words per level without conjugations; conjugations as their own row
      ("    const cs=CARDS.filter(x=>x.deck===dk);if(!cs.length)continue;", "    const cs=CARDS.filter(x=>x.deck===dk&&!x.conj);if(!cs.length)continue;"),
      ("  $('stDecks').innerHTML=rows.join('');",
       "  {const cs=CARDS.filter(x=>x.conj&&S.set.decks.includes(x.deck));if(cs.length){const n={new:0,learn:0,known:0,master:0};for(const x of cs)n[bucket(stateOf(x,dir))]++;\n"
       "    const seg=['learn','known','master','new'].filter(k=>n[k]).map(k=>`<i class=\"s-${k}\" style=\"flex:${n[k]}\" title=\"${n[k]} ${k}\"></i>`).join('');\n"
       "    rows.push(`<div class=\"drow\"><div class=\"top\"><b>Verb forms</b><span>${n.known+n.master} of ${cs.length} learned${n.learn?` · ${n.learn} learning`:''}</span></div><div class=\"pstack\">${seg}</div></div>`)}}\n"
       "  $('stDecks').innerHTML=rows.join('');"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:80]); s = s.replace(a, b, 1)
    # after the verb-conjugation helpers
    i = s.index('/* ---------- telling you exactly what was accepted ---------- */'); s = s[:i] + JS + s[i:]
    open(p, 'w').write(s); print('patched', p, len(VEN), 'verbs')

patch(sys.argv[1], sys.argv[2])
