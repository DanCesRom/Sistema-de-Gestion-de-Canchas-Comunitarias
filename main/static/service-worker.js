const CACHE_NAME = 'your-app-cache-v1';
const urlsToCache = [
    '/',
    '/static/manifest.webmanifest',
    '/static/icons/reserva_logo.jpeg',
    // Add other routes or assets to cache here
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
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
