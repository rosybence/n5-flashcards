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
const TEF={"開く":"it's open","消える":"it's gone out","曇る":"it's cloudy","咲く":"it's in bloom","閉まる":"it's closed","止まる":"it's stopped","鳴く":"it's crying (an animal)","晴れる":"it's sunny","吹く":"it's blowing (the wind)","降る":"it's raining","鳴る":"it's ringing","沸く":"it's boiling","止む":"it's stopped (raining)","壊れる":"it's broken","揺れる":"it's shaking","落ちる":"it's fallen","決まる":"it's been decided","足りる":"there's enough","無くなる":"it's gone","光る":"it's shining","違う":"it's different","故障する":"it's broken down","残る":"it's left over","増える":"it's increasing","乾く":"it's dry","暮れる":"it's dark","空く":"it's free (empty)","変わる":"it's changed","済む":"it's done","折れる":"it's snapped","見つかる":"it's been found","直る":"it's fixed","続く":"it's continuing","焼ける":"it's burnt","冷える":"it's cold (chilled)","点く":"it's on (a light)","割れる":"it's broken (cracked)","込む":"it's crowded","役に立つ":"it's useful","汚れる":"it's dirty","倒れる":"it's fallen over","合う":"it's right","終わる":"it's finished","着く":"it's arrived","できる":"it's ready","動く":"it's moving","飛ぶ":"it's flying","分かる":"I understand","困る":"I'm in trouble","疲れる":"I'm tired","驚く":"I'm surprised","びっくりする":"I'm surprised","喜ぶ":"I'm delighted","怒る":"I'm angry","心配する":"I'm worried","けがする":"I'm hurt","治る":"I've got better","慣れる":"I'm used to it","太る":"I'm overweight","痩せる":"I'm thin","濡れる":"I'm wet","遅れる":"I'm running late","間に合う":"I'm in time","生きる":"I'm alive","死ぬ":"it's dead","亡くなる":"he has passed away","住む":"I live (somewhere)","勤める":"I work for a company","働く":"I'm working","通う":"I go there regularly","生活する":"I'm living","入院する":"I'm in hospital","眠る":"I'm sleeping","食事する":"I'm having a meal","思う":"I'm thinking","向かう":"I'm on my way","借りる":"I've borrowed it","吸う":"I'm smoking","釣る":"I'm fishing","見える":"I can see it","聞こえる":"I can hear it","負ける":"we're losing","勝つ":"we're winning","けんかする":"they're fighting","別れる":"they've split up","泣く":"she's crying","騒ぐ":"they're making a noise","踏む":"you're stepping on it","盗む":"they're stealing","いじめる":"they're bullying","叱る":"she's scolding","育てる":"I'm bringing up","建てる":"they're building","間違える":"it's wrong","生産する":"they're producing","輸出する":"they're exporting","放送する":"they're broadcasting","要る":"SKIP","生まれる":"SKIP","なる":"SKIP","過ぎる":"SKIP","もらう":"SKIP","くれる":"SKIP","連れる":"SKIP","無くす":"SKIP","落とす":"SKIP","滑る":"SKIP","入学する":"SKIP","退院する":"SKIP","承知する":"SKIP","経験する":"SKIP","かまう":"SKIP"};
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
    // negative and past: polite form is the answer, the plain form (said to friends) is accepted as casual
    const F={pol:[W.pol,R.pol,[]],te:[W.te,R.te,[]],neg:[polNeg(W.pol),polNeg(R.pol),[[W.neg,R.neg,'']]],past:[polPast(W.pol),polPast(R.pol),[[W.past,R.past,'']]]};
    // て-form: a request (please… → 〜てください) or, for verbs that can't be requested, 〜ています with its own English
    const tk=TEF[v.k]??TEF[v.k+'する'];if(tk==='SKIP')delete F.te;
    else if(tk)F.te=[W.te+'います',R.te+'います',[[W.te+'ます',R.te+'ます','']]];
    else F.te=[W.te+'ください',R.te+'ください',[[W.te,R.te,'']]];
    for(const f in F){const [wk,rk,alts]=F[f];
      for(const [a,ar,note] of alts){READ[a]=[ar,kanaRomaji(ar)];if(note)NOTE[a]=note}
      const c={id:'cj:'+(f==='te'?'te2':f)+':'+v.id,k:wk,kana:rk,r:kanaRomaji(rk),en:f==='te'?(tk||'please '+base):conjPrompt(base,past,f,v.k),type:'w',deck:v.deck,jl:[],pic:v.pic,
        alts:alts.map(x=>x[0]),casual:new Set(alts.map(x=>x[0])),conj:f,base:v};
      out.push(c);const gk=f==='te'?'te|'+c.en:base+'|'+f;(byBase[gk]=byBase[gk]||[]).push(c)}
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
