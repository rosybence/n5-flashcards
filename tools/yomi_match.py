"""Japanese app: judge answers by how they sound (kana reading), not how the phone spelled them,
and treat long-vowel / small-tsu slips as 'close'."""
import sys

JS = r'''
/* ---------- matching by sound: what the phone wrote in kanji, read back as kana ---------- */
let YOMI=null,YMAX=1;
const isKanji=ch=>/[㐀-鿿々〆ヵヶ]/.test(ch);
const isKanaStr=s=>/^[ぁ-ゖー]+$/.test(s);
function loadYomi(){
  fetch('yomi.txt').then(r=>r.ok?r.text():Promise.reject()).then(t=>{
    const m=new Map();
    for(const l of t.split('\n')){if(!l||l[0]==='#')continue;const i=l.indexOf('\t');if(i<0)continue;
      const s=l.slice(0,i);m.set(s,l.slice(i+1).split(','));if(s.length>YMAX)YMAX=s.length}
    // the cards' own spellings (and their alternatives) always count
    const add=(s,r)=>{s=normJa(s);r=normJa(r);if(!s||!r||!isKanaStr(r)||![...s].some(isKanji))return;const a=m.get(s)||[];if(!a.includes(r))m.set(s,[...a,r]);if(s.length>YMAX)YMAX=s.length};
    for(const c of CARDS){if(c.type!=='k'&&c.kana)add(c.k,c.kana);for(const a of c.alts||[])if(READ[a])add(a,READ[a][0])}
    YOMI=m}).catch(()=>{});
}
// can the written text h be read as the kana t?
function canRead(h,t){
  if(!YOMI)return false;const n=h.length,m=t.length,seen=new Set();
  const go=(i,j)=>{if(i===n)return j===m;const key=i*4096+j;if(seen.has(key))return false;seen.add(key);
    const ch=h[i];if(!isKanji(ch)&&t[j]===ch&&go(i+1,j+1))return true;
    for(let L=Math.min(YMAX,n-i);L>=1;L--){const r=YOMI.get(h.substr(i,L));if(r)for(const x of r)if(t.startsWith(x,j)&&go(i+L,j+x.length))return true}
    return false};
  return go(0,0);
}
// all the ways h could be read (capped)
function readingsOf(h,cap=150){
  if(!YOMI)return isKanaStr(h)?[h]:[];
  const n=h.length,R=Array.from({length:n+1},()=>new Set());R[0].add('');
  for(let i=0;i<n;i++){if(!R[i].size)continue;const ch=h[i];let any=false;
    for(const p of R[i]){
      if(!isKanji(ch)){R[i+1].size<cap&&R[i+1].add(p+ch);any=true}
      for(let L=Math.min(YMAX,n-i);L>=1;L--){const r=YOMI.get(h.substr(i,L));if(r){any=true;for(const x of r)if(R[i+L].size<cap)R[i+L].add(p+x)}}
    }
    if(!any)for(const p of R[i])R[i+1].add(p+ch);
  }
  return [...R[n]];
}
// a looser key: long vowels, small っ and ー don't count (おばさん ≈ おばあさん, きて ≈ きって)
const VROW={a:'あかさたなはまやらわがざだばぱぁゃゎ',i:'いきしちにひみりぎじぢびぴぃ',u:'うくすつぬふむゆるぐずづぶぷぅゅ',e:'えけせてねへめれげぜでべぺぇ',o:'おこそとのほもよろをごぞどぼぽぉょ'};
const vowOf=ch=>{for(const v in VROW)if(VROW[v].includes(ch))return v;return ''};
function loose(s){let o='',prev='';for(const ch of s){
  if(ch==='っ'||ch==='ー')continue;
  const pv=vowOf(prev);
  if('あいうえお'.includes(ch)&&pv&&(vowOf(ch)===pv||(ch==='う'&&pv==='o')||(ch==='い'&&pv==='e')))continue;
  o+=ch;prev=ch}return o}
loadYomi();
'''

def patch(p):
    s = open(p).read()
    if 'function canRead' in s: print('already', p); return
    R = [
      ("  const same=(h,t)=>h===t;\n  for(const [exact,pass] of [[true,same],[false,close]])for(const [l,ts] of P)for(let i=0;i<H.length;i++){const t=ts.find(t=>pass(H[i],t));if(t!==undefined){\n"
       "    lastMatch=l===c.k?null:l;lastHit={i,said:heard[i],ans:l===c.k?c.k+(c.kana&&c.kana!==c.k?'（'+c.kana+'）':''):l,ansN:t,exact};return true}}",
       "  const same=(h,t)=>h===t;\n"
       "  // same sound, different spelling (飴 for 雨, 宜しく for よろしく) is still exactly right\n"
       "  let saidR=null;\n"
       "  const sounds=(h,t)=>{if(isKanaStr(t)&&h!==t&&canRead(h,t)){saidR=t;return true}return false};\n"
       "  // close: long vowels / small っ slips, or the answer inside something longer\n"
       "  const soundsClose=(h,t)=>{if(!isKanaStr(t))return false;const rs=readingsOf(h);const lt=loose(t);\n"
       "    const r=rs.find(r=>loose(r)===lt)||rs.find(r=>t.length>1&&r.includes(t))||(t.length>=4?rs.find(r=>sim(r,t)>=.8):null);\n"
       "    if(r){saidR=r;return true}return false};\n"
       "  for(const [exact,pass] of [[true,same],[true,sounds],[false,close],[false,soundsClose]])for(const [l,ts] of P)for(let i=0;i<H.length;i++){saidR=null;const t=ts.find(t=>pass(H[i],t));if(t!==undefined){\n"
       "    lastMatch=l===c.k?null:l;lastHit={i,said:heard[i],saidR:saidR&&saidR!==H[i]?saidR:null,ans:l===c.k?c.k+(c.kana&&c.kana!==c.k?'（'+c.kana+'）':''):l,ansN:t,exact};return true}}"),
      # feedback shows how it was read
      ("  if(h.exact)return{cls:'ok',text:'',html:`Correct — heard “${escH(h.said)}”${extra}${first}`};",
       "  if(h.exact)return{cls:'ok',text:'',html:`Correct — heard “${escH(h.said)}”${h.saidR?' · read as '+escH(h.saidR):''}${extra}${first}`};"),
      ("  const you=en?markDiffEn(h.said,h.ans):markDiffJa(normJa(h.said),h.ansN||normJa(h.ans));",
       "  const you=en?markDiffEn(h.said,h.ans):h.saidR?escH(h.said)+'” · read as “'+markDiffJa(h.saidR,h.ansN||normJa(h.ans)):markDiffJa(normJa(h.said),h.ansN||normJa(h.ans));"),
      ("  const ans=en?markDiffEn(h.ans,h.said):markDiffJa(h.ansN||normJa(h.ans),normJa(h.said))",
       "  const ans=en?markDiffEn(h.ans,h.said):markDiffJa(h.ansN||normJa(h.ans),h.saidR||normJa(h.said))"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b, 1)
    i = s.index('/* ---------- telling you exactly what was accepted ---------- */'); s = s[:i] + JS + s[i:]
    open(p, 'w').write(s); print('patched', p)

for p in sys.argv[1:]: patch(p)
