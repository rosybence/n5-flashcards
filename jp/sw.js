// Network first so updates arrive; cached copy when offline (e.g. on a walk with no signal).
// Only handles files inside this app's own folder, so the two apps never mix.
const CACHE = 'jp-v1';
const FILES = ['./', './index.html', './app.webmanifest', './icon2-192.png', './icon2-512.png'];
const SCOPE = self.registration.scope;
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('jp-') && k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || !e.request.url.startsWith(SCOPE)) return;
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  }).catch(() => caches.match(e.request).then(m => m || (e.request.mode === 'navigate' ? caches.match(SCOPE + 'index.html') : undefined))));
});
