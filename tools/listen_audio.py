"""Both apps:
- 'Hear again' button once a card is flipped (plays the Spanish/Japanese again)
- Listen-only walk mode doesn't count as correct: heard cards keep their schedule (skipped for the rest of
  the walk); saying 'I was wrong' still marks them wrong
- Listen-only: the Spanish/Japanese is repeated (2 extra times)
- Speech no longer clipped at the start: wake the audio output with near-silence before speaking"""
import sys

def patch(p, lang):
    s = open(p).read()
    if 'hearAgain' in s: print('already', p); return
    say_in = "'Your turn — say it '+(al.startsWith('es')?'in Spanish':'in English')" if lang == 'es' else "'Your turn — say it '+(al.startsWith('ja')?'in Japanese':'in English')"
    R = [
      # --- hear again button ---
      ('    <div class="rc" id="rcRow">\n',
       '    <div class="rc" id="rcRow">\n      <button class="btn" id="hearAgain"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span>Hear again</span></button>\n'),
      ("$('flip').onclick=()=>{suggest=suggest===0?2:0;render()};",
       "$('flip').onclick=()=>{suggest=suggest===0?2:0;render()};\n"
       "// the Spanish/Japanese side, whichever way round the card is\n"
       "function targetAudio(c){const a=answerOf(c),p=promptOf(c);return [a,p].find(x=>x&&x[1]&&!x[1].startsWith('en'))||a}\n"
       "$('hearAgain').onclick=()=>{if(!cur)return;const [t,l]=targetAudio(cur);speak(t,l)};"),
      # --- listen-only: no 'correct', skip for the rest of the walk, repeat the word ---
      ("function nextCard(){\n  rollDay();const now=Date.now();",
       "let walkSkip=new Set();\nfunction nextCard(){\n  rollDay();const now=Date.now();const sk=c=>!(walking&&walkSkip.has(c.id));"),
      ("  const due=pool().filter(c=>{const s=st(c);return s&&s.due<=now});",
       "  const due=pool().filter(c=>{const s=st(c);return s&&s.due<=now&&sk(c)});"),
      ("  if(S.newDone[S.set.dir]<S.set.newPerDay){",
       "  if(S.newDone[S.set.dir]+(walking?walkNew:0)<S.set.newPerDay){"),
      ("const n=pool().find(c=>c.deck===dk&&!st(c)&&c.id!==lastId);if(n)return n}",
       "const n=pool().find(c=>c.deck===dk&&!st(c)&&c.id!==lastId&&sk(c));if(n)return n}"),
      ("  const ahead=pool().filter(c=>{const s=st(c);return s&&s.learning&&s.due<=now+20*MIN});",
       "  const ahead=pool().filter(c=>{const s=st(c);return s&&s.learning&&s.due<=now+20*MIN&&sk(c)});"),
      ("      status('Answer');await doReveal();if(!walking)break;\n    }else{",
       "      status('Answer');await doReveal();if(!walking)break;\n"
       "      // hear the Spanish/Japanese a couple more times\n"
       "      {const [t,l]=targetAudio(cur);for(let r=0;r<2&&walking;r++){await wait(900);if(!walking)break;status('Again…');await speak(t,l)}}\n"
       "      if(!walking)break;\n    }else{"),
      ("    grade(cur,ok?(knewIt?3:2):0);lastId=cur.id;await wait(400);",
       "    if(S.set.walkMode==='listen'||micBlocked){\n"
       "      // just listening isn't an answer: keep the card's schedule unless you said you got it wrong\n"
       "      if(!ok)grade(cur,0);else{if(!st(cur))walkNew++;walkSkip.add(cur.id)}\n"
       "    }else grade(cur,ok?(knewIt?3:2):0);\n"
       "    lastId=cur.id;await wait(400);"),
      ("async function startWalk(){\n  walking=true;",
       "let walkNew=0;\nasync function startWalk(){\n  walkSkip=new Set();walkNew=0;\n  walking=true;"),
      ("'Say <b>“say it again”</b> to hear it again, <b>“I was wrong”</b> if you missed it, or <b>“next card”</b>. Say nothing and it counts as right.'",
       "'Say <b>“say it again”</b> to hear it again, <b>“I was wrong”</b> if you missed it, or <b>“next card”</b>.','Just listening doesn’t count as a correct answer: the card keeps its schedule. Say “I was wrong” and it comes back soon.'"),
    ]
    for a, b in R:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b, 1)
    # --- wake the audio output so the start of a word isn't cut off ---
    a = "function speak(text,lang){return NAT?speakNative(text,lang):speakWeb(text,lang)}"
    assert s.count(a) == 1, p
    s = s.replace(a, r"""// phones put the speaker/Bluetooth to sleep between sounds, which clips the start of the next word:
// keep it awake with an inaudible tone while speaking, and give it a moment after a quiet spell
let _ka=null,_kaT=null,_lastSpoke=0;
function audioAwake(){try{actx=actx||new (window.AudioContext||window.webkitAudioContext)();if(actx.state==='suspended')actx.resume();
  if(!_ka){const o=actx.createOscillator(),g=actx.createGain();o.frequency.value=30;g.gain.value=0.0006;o.connect(g).connect(actx.destination);o.start();_ka=o}
  clearTimeout(_kaT);_kaT=setTimeout(()=>{try{_ka&&_ka.stop()}catch(e){}_ka=null},walking?600000:15000)}catch(e){}}
function speak(text,lang){const cold=Date.now()-_lastSpoke>3000||!_ka;audioAwake();
  return (cold?wait(lang.startsWith('en')?150:350):Promise.resolve()).then(()=>NAT?speakNative(text,lang):speakWeb(text,lang)).then(v=>{_lastSpoke=Date.now();audioAwake();return v})}""", 1)
    if 'let actx' not in s and 'actx=' not in s.split('function audioAwake')[0]:
        print('note: actx declared?', p)
    open(p, 'w').write(s); print('patched', p)

patch('/home/claude/spanish/app.html', 'es')
patch('/home/claude/n5-flashcards.html', 'ja')
