// ============================================
// M.A TECH — Service Worker (PWA)
// ============================================

const CACHE_NAME = 'matech-v1';
const URLS_PARA_CACHE = [
    '/static/style.css',
    '/static/app-mobile.css',
    '/static/app.js',
    '/static/app-mobile.js',
    '/static/help.js',
    '/static/favicon.svg',
];

// Instala e faz cache dos arquivos estáticos
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(URLS_PARA_CACHE).catch(() => {});
        })
    );
    self.skipWaiting();
});

// Ativa e limpa cache antigo
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((names) => {
            return Promise.all(
                names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n))
            );
        })
    );
    self.clients.claim();
});

// Fetch — rede primeiro, cache fallback
self.addEventListener('fetch', (event) => {
    const req = event.request;

    // Só GET
    if (req.method !== 'GET') return;

    // Só pra recursos estáticos
    if (!req.url.includes('/static/')) return;

    event.respondWith(
        fetch(req).then((res) => {
            // Atualiza cache
            const resClone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
            return res;
        }).catch(() => {
            return caches.match(req);
        })
    );
});