// Speech recognition worker: runs the Vosk engine (vosk-browser, Apache 2.0) off the main thread.
// Messages in: {t:'load',url} {t:'start',id,rate,grammar} {t:'audio',id,data} {t:'stop',id}
// Messages out: {t:'loaded'} {t:'partial',id,text} {t:'result',id,text} {t:'final',id,text} {t:'error',id,error}
importScripts('vosk-wasm.js');
let V = null, model = null, rec = null, recId = null, buf = 0, bufSize = 0;
const words = r => (r && (r.text || r.partial) || '').replace(/\[unk\]/g, '').replace(/\s+/g, ' ').trim();
onmessage = async (e) => {
  const m = e.data;
  try {
    if (m.t === 'load') {
      V = await LoadVosk();
      V.SetLogLevel(-1);
      try { V.FS.mkdir('/vosk'); } catch (_) {}
      V.FS.mount(V.IDBFS, {}, '/vosk');
      await V.syncFilesystem(true);
      const path = '/vosk/' + m.url.replace(/[\W]/g, '_');
      await V.downloadAndExtract(new URL(m.url, self.location.href).toString(), path);
      await V.syncFilesystem(false);
      model = new V.Model(path);
      postMessage({ t: 'loaded' });
    } else if (m.t === 'start') {
      if (rec) { try { rec.delete(); } catch (_) {} rec = null; }
      rec = m.grammar ? new V.Recognizer(model, m.rate, m.grammar) : new V.Recognizer(model, m.rate);
      recId = m.id;
    } else if (m.t === 'audio') {
      if (!rec || m.id !== recId) return;
      const d = m.data, size = d.length * 4;
      if (bufSize !== size) { if (buf) V._free(buf); buf = V._malloc(size); bufSize = size; }
      // browser audio is -1..1; Kaldi expects the int16 range
      const scaled = new Float32Array(d.length);
      for (let i = 0; i < d.length; i++) scaled[i] = d[i] * 32768;
      V.HEAPF32.set(scaled, buf / 4);
      if (rec.AcceptWaveform(buf, d.length)) {
        const text = words(JSON.parse(rec.Result()));
        if (text) postMessage({ t: 'result', id: m.id, text });
      } else {
        const text = words(JSON.parse(rec.PartialResult()));
        if (text) postMessage({ t: 'partial', id: m.id, text });
      }
    } else if (m.t === 'stop') {
      if (!rec || m.id !== recId) return;
      const text = words(JSON.parse(rec.FinalResult()));
      try { rec.delete(); } catch (_) {}
      rec = null; recId = null;
      postMessage({ t: 'final', id: m.id, text });
    }
  } catch (err) {
    postMessage({ t: 'error', id: m.id, error: String((err && err.message) || err) });
  }
};
