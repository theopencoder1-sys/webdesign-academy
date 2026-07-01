const CACHE_NAME = 'webdesign-academy-v1';
const ASSETS = [
    '/',
    '/courses/',
    '/courses/html5-full/',
    '/playground/',
    '/static/css/custom-theme.css',
    '/static/css/responsive.css',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
