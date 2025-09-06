const CACHE_NAME = 'dicpro-cache-v5';
const URLS_TO_CACHE = [
    '/index.html',
    '/static/js/app.js',
    '/static/css/style.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Install the service worker and cache the app shell
self.addEventListener('install', event => {
    // Don't force immediate activation to avoid conflicts
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(URLS_TO_CACHE).catch(err => {
                    console.warn('Failed to cache some resources:', err);
                });
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
        }).then(() => {
            // Only claim clients after cleanup is complete
            return self.clients.claim();
        })
    );
});

// Fetch event handler with improved error handling
self.addEventListener('fetch', event => {
    // Skip non-GET requests and chrome-extension requests
    if (event.request.method !== 'GET' || event.request.url.startsWith('chrome-extension://')) {
        return;
    }

    // For navigation requests, use network-first strategy
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    if (response.ok) {
                        return caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, response.clone());
                            return response;
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, serve cached version
                    return caches.match(event.request).then(cachedResponse => {
                        return cachedResponse || caches.match('/index.html');
                    });
                })
        );
        return;
    }

    // For other requests, use cache-first strategy
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                
                return fetch(event.request).then(fetchResponse => {
                    // Only cache successful responses
                    if (fetchResponse.ok) {
                        return caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, fetchResponse.clone());
                            return fetchResponse;
                        });
                    }
                    return fetchResponse;
                }).catch(error => {
                    console.warn('Fetch failed for:', event.request.url, error);
                    throw error;
                });
            })
    );
});
