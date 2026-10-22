"""Add a voice picker (target language + English) with Test buttons to an app's settings."""
import sys
CFG = {
  'n5-flashcards.html': dict(pre='ja', tag='ja-JP', name='Japanese', sample='こんにちは。今日も日本語を練習しましょう。'),
  'app.html': dict(pre='es', tag='es-ES', name='Spanish', sample='Hola, ¿qué tal? Vamos a practicar español juntos.'),
}
def patch(p):
    c = CFG[p.split('/')[-1]]
    s = open(p).read()
    if 'id="sVoiceT"' in s: print('already', p); return
    html = f'''    <div class="voicerow"><label for="sVoiceT">{c['name']} voice</label><div class="vr"><select id="sVoiceT"></select><button class="test" data-test="t">▶ Test</button></div></div>
    <div class="voicerow"><label for="sVoiceE">English voice</label><div class="vr"><select id="sVoiceE"></select><button class="test" data-test="e">▶ Test</button></div></div>
    <p class="vnote" id="vNote"></p>
    <button class="danger" id="reset">Reset all progress</button>'''
    js = f'''
/* ---------- voice picker ---------- */
const TL='{c['pre']}',TTAG='{c['tag']}',TSAMPLE='{c['sample']}',ESAMPLE='Hello! Let’s practise together.';
function voiceList(pre){{
  if(NAT){{try{{return JSON.parse(NAT.voices(pre))}}catch(e){{return[]}}}}
  const L=v=>v.lang.replace('_','-').toLowerCase();
  return voices.filter(v=>L(v).startsWith(pre)).sort((a,b)=>(b.localService===false)-(a.localService===false)||a.name.localeCompare(b.name))
    .map(v=>({{name:v.name,label:v.name.replace(/^(Microsoft|Google)\\s+/,'')+' ('+v.lang+')'+(v.localService===false?' · online':'')}}))}}
function fillVoices(){{
  S.set.voice=S.set.voice||{{}};
  for(const [id,pre] of [['sVoiceT',TL],['sVoiceE','en']]){{
    const el=$(id),list=voiceList(pre),cur=S.set.voice[pre]||'';
    el.innerHTML='<option value="">Automatic</option>'+list.map(v=>`<option value="${{escH(v.name).replace(/"/g,'&quot;')}}">${{escH(v.label)}}</option>`).join('');
    el.value=list.some(v=>v.name===cur)?cur:'';
    el.onchange=()=>{{S.set.voice[pre]=el.value;save();speak(pre==='en'?ESAMPLE:TSAMPLE,pre==='en'?'en-GB':TTAG)}};
  }}
  const n=voiceList(TL).length;
  $('vNote').innerHTML=(n?'':'No {c['name']} voices found on this phone. ')+'Voices sound robotic? Install <b>Speech Services by Google</b>, then in phone Settings → General management → Language and input → Text-to-speech output, choose it and download the {c['name']} and English voices.';
}}
document.querySelectorAll('[data-test]').forEach(b=>b.onclick=()=>{{userActed=true;const t=b.dataset.test==='t';speak(t?TSAMPLE:ESAMPLE,t?TTAG:'en-GB')}});
window.__nativeTtsReady=()=>{{try{{fillVoices()}}catch(e){{}}}};
if('speechSynthesis' in window)speechSynthesis.addEventListener('voiceschanged',()=>{{try{{fillVoices()}}catch(e){{}}}});
fillVoices();
'''
    R = [
      ('    <button class="danger" id="reset">Reset all progress</button>', html),
      ('.danger{', '.voicerow{display:grid;gap:6px;font-size:14px}\n.vr{display:flex;gap:8px}\n.vr select{flex:1;min-width:0}\n.test{padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--bg);font-weight:500;white-space:nowrap}\n.vnote{margin:0;font-size:12.5px;color:var(--muted)}\n.vnote b{color:var(--ink);font-weight:600}\n.danger{'),
      ("function pickVoice(lang){const L=lang.toLowerCase();", "function pickVoice(lang){const want=(S.set.voice||{})[lang.slice(0,2).toLowerCase()];if(want){const w=voices.find(v=>v.name===want);if(w)return w}\n  const L=lang.toLowerCase();"),
      ("NAT.speak(text,lang,lang.startsWith('en')?1:+S.set.rate,id);", "NAT.speak(text,lang,lang.startsWith('en')?1:+S.set.rate,id,(S.set.voice||{})[lang.slice(0,2).toLowerCase()]||'');"),
      ("$('setBtn').onclick=()=>{const s=$('settings');s.hidden=!s.hidden;", "$('setBtn').onclick=()=>{const s=$('settings');s.hidden=!s.hidden;if(!s.hidden)fillVoices();"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:60]); s = s.replace(a, b, 1)
    i = s.rindex('</script>'); s = s[:i] + js + s[i:]
    open(p, 'w').write(s); print('patched', p)
for p in sys.argv[1:]: patch(p)
