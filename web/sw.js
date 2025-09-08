const CACHE_NAME = 'dicpro-cache-final-fix';
const URLS_TO_CACHE = [
    '/app.html',
    '/static/js/app.js?v=final-fix',
    '/static/css/app.css?v=final-fix',
    '/manifest.json?v=final-fix',
    '/static/css/all.min.css'
];

// Install the service worker and cache the app shell
self.addEventListener('install', event => {
    self.skipWaiting(); // Force the new service worker to activate immediately
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(URLS_TO_CACHE);
            })
    );
});

// Activate event to clean up old caches
self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim(); // Take control of all clients immediately
});

// Network-first strategy for navigation and critical scripts
self.addEventListener('fetch', event => {
    // For HTML and the main app script, always go to the network first.
    if (event.request.mode === 'navigate' || event.request.url.includes('app.js') || event.request.url.includes('manifest.json')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // If the network request is successful, cache it and return it
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                })
                .catch(() => {
                    // If the network fails, serve the cached version
                    return caches.match(event.request);
                })
        );
        return;
    }

    // For other requests (CSS, fonts, etc.), use a cache-first strategy
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request).then(fetchResponse => {
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                });
            })
    );
});
