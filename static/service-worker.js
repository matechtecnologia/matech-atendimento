// M.A Tech — Service Worker desativado
// Não cacheia nada, só deixa o app "instalável"
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then(names => Promise.all(names.map(n => caches.delete(n))))
        .then(() => self.clients.claim())
    );
});
self.addEventListener('fetch', () => { /* sem cache */ });
