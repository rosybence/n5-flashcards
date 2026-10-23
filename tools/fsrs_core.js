/* ---------- FSRS-6 spaced repetition (ported from open-spaced-repetition/ts-fsrs, MIT) ---------- */
const FW=[0.212,1.2931,2.3065,8.2956,6.4133,0.8334,3.0194,0.001,1.8722,0.1666,0.796,1.4835,0.0614,0.2629,1.6483,0.6014,1.8729,0.5425,0.0912,0.0658,0.1542];
const F_DECAY=-FW[20],F_FACTOR=Math.round((Math.exp(Math.log(0.9)/F_DECAY)-1)*1e8)/1e8;
const fClamp=(x,a,b)=>Math.min(Math.max(x,a),b);
const fRound=x=>Math.round(x*1e8)/1e8;
const fRetr=(t,s)=>fRound(Math.pow(1+F_FACTOR*t/s,F_DECAY));
const fInitS=g=>fClamp(FW[g-1],0.001,36500);
const fInitD=g=>fRound(FW[4]-Math.exp((g-1)*FW[5])+1);
function fNextD(d,g){const nd=d+fRound((-FW[6]*(g-3))*(10-d)/9);return fClamp(fRound(FW[7]*fInitD(4)+(1-FW[7])*nd),1,10)}
function fRecallS(d,s,r,g){return fRound(fClamp(s*(1+Math.exp(FW[8])*(11-d)*Math.pow(s,-FW[9])*(Math.exp((1-r)*FW[10])-1)*(g===2?FW[15]:1)*(g===4?FW[16]:1)),0.001,36500))}
function fForgetS(d,s,r){const sf=fRound(fClamp(FW[11]*Math.pow(d,-FW[12])*(Math.pow(s+1,FW[13])-1)*Math.exp((1-r)*FW[14]),0.001,36500));
  return fClamp(fRound(s/Math.exp(FW[17]*FW[18])),0.001,sf)}
function fShortS(s,g){let k=Math.pow(s,-FW[19])*Math.exp(FW[17]*(g-3+FW[18]));if(g>=2)k=Math.max(k,1);return fRound(fClamp(s*k,0.001,36500))}
// memory state after a review t days after the previous one, grade g (1 Again .. 4 Easy)
function fNextState(st,t,g){
  if(!st)return{s:fInitS(g),d:fClamp(fInitD(g),1,10)};
  const r=fRetr(t,st.s);let s;
  if(t===0)s=fShortS(st.s,g);else if(g===1)s=fForgetS(st.d,st.s,r);else s=fRecallS(st.d,st.s,r,g);
  return{s,d:fNextD(st.d,g)};
}
const fIvl=(s,ret)=>Math.max(Math.round((s/F_FACTOR)*(Math.pow(ret,1/F_DECAY)-1)),1);
