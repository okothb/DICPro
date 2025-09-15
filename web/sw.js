'''const CACHE_NAME = 'dicpro-cache-v3';
const URLS_TO_CACHE = [
    '/app.html',
    '/static/js/app.js?v=final-fix',
    '/static/css/app.css?v=final-fix',
    '/manifest.json?v=final-fix',
    '/static/css/all.min.css',
    '/cleanup.html',
    '/static/js/cleaner.js',
    '/static/js/landing.js',
    '/static/css/style.css',
    '/static/css/landing.css',
    '/index.html',
    '/static/js/hash-generator.js'
];

// Helper to convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// Helper to open IndexedDB for storing hashes
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('dicpro-hashes-db', 1);
        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('hashes')) {
                db.createObjectStore('hashes', { keyPath: 'original_hash' });
            }
        };
        request.onsuccess = event => resolve(event.target.result);
        request.onerror = event => reject(event.target.error);
    });
}

// Helper to get all hashes from IndexedDB
async function getAllHashes() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['hashes'], 'readonly');
        const store = transaction.objectStore('hashes');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = (event) => reject('Error getting hashes: ' + event.target.error);
    });
}

// Helper to clear all hashes from IndexedDB
async function clearAllHashes() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['hashes'], 'readwrite');
        const store = transaction.objectStore('hashes');
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = (event) => reject('Error clearing hashes: ' + event.target.error);
    });
}

// Function to sync locally stored hashes with the backend
async function syncHashesWithBackend() {
    console.log('Attempting to sync local hashes with the backend...');
    const hashes = await getAllHashes();

    if (hashes.length === 0) {
        console.log('No local hashes to sync.');
        return; // Nothing to do
    }

    try {
        const response = await fetch('/api/sync-hashes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ hashes }),
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('Successfully synced hashes with the backend.');
                await clearAllHashes();
                console.log('Local hash store cleared after successful sync.');
            } else {
                console.error('Backend failed to sync hashes:', data.error || 'Unknown error');
            }
        } else {
            console.error('Failed to sync hashes. Server responded with status:', response.status);
        }
    } catch (error) {
        console.error('Error during hash synchronization fetch:', error);
    }
}

// Listen for messages from the client to trigger sync
self.addEventListener('message', event => {
    if (event.data && event.data.action === 'syncHashes') {
        console.log('Service Worker received "syncHashes" message from client.');
        event.waitUntil(syncHashesWithBackend());
    }
});

// Install the service worker and cache the app shell
self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(URLS_TO_CACHE))
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
    return self.clients.claim();
});

// Intercept fetch requests
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // For API calls, use a network-first strategy.
    // If the network fails, fall back to the offline handlers.
    if (url.pathname.startsWith('/api/')) {
        // We don't want to intercept the sync call itself, which is initiated by the SW.
        // Let it go to the network. If it fails, the sync function will handle it.
        if (url.pathname === '/api/sync-hashes') {
            return;
        }

        event.respondWith(
            fetch(event.request.clone()).catch(async () => {
                console.log(`Network request for ${url.pathname} failed. Falling back to offline handler.`);

                // --- OFFLINE FALLBACK LOGIC ---
                if (url.pathname === '/api/protect' && event.request.method === 'POST') {
                    return (async () => {
                        try {
                            const formData = await event.request.formData();
                            const file = formData.get('file');
                            const original_hash = formData.get('original_hash');
                            const secretData = formData.get('secretData');
                            const isEncrypted = formData.get('encryptPayload') === 'on';

                            const db = await openDB();
                            const tx = db.transaction('hashes', 'readwrite');
                            await tx.objectStore('hashes').put({
                                original_hash: original_hash,
                                fileName: file.name,
                                protection_date: new Date().toISOString(),
                                secretData: secretData,
                                isEncrypted: isEncrypted
                            });
                            await tx.done;

                            const fileBuffer = await file.arrayBuffer();
                            const protected_file_data = arrayBufferToBase64(fileBuffer);

                            return new Response(JSON.stringify({
                                success: true,
                                message: 'Document protected locally (offline).',
                                original_file: file.name,
                                original_hash: original_hash,
                                protected_hash: original_hash,
                                protection_date: new Date().toISOString(),
                                protected_file_data: protected_file_data,
                                protected_filename: `protected_${file.name}`
                            }), { headers: { 'Content-Type': 'application/json' } });
                        } catch (error) {
                            return new Response(JSON.stringify({ success: false, error: `Service Worker Error: ${error.message}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
                        }
                    })();
                } else if (url.pathname === '/api/verify' && event.request.method === 'POST') {
                    return (async () => {
                        try {
                            const formData = await event.request.formData();
                            const file = formData.get('file');
                            const current_hash = formData.get('current_hash');

                            const db = await openDB();
                            const storedRecord = await db.transaction('hashes', 'readonly').objectStore('hashes').get(current_hash);

                            if (storedRecord) {
                                return new Response(JSON.stringify({
                                    success: true,
                                    is_verified: true,
                                    message: 'Document is VERIFIED (offline).',
                                    current_hash: current_hash,
                                    original_hash: storedRecord.original_hash,
                                    protection_date: storedRecord.protection_date,
                                    original_file: storedRecord.fileName
                                }), { headers: { 'Content-Type': 'application/json' } });
                            } else {
                                return new Response(JSON.stringify({
                                    success: true,
                                    is_verified: false,
                                    message: 'Document is UNKNOWN or has been TAMPERED with (offline).',
                                    current_hash: current_hash,
                                }), { headers: { 'Content-Type': 'application/json' } });
                            }
                        } catch (error) {
                            return new Response(JSON.stringify({ success: false, error: `Service Worker Error: ${error.message}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
                        }
                    })();
                } else if (url.pathname === '/api/extract' && event.request.method === 'POST') {
                    return (async () => {
                        try {
                            const formData = await event.request.formData();
                            const current_hash = formData.get('current_hash');

                            const db = await openDB();
                            const storedRecord = await db.transaction('hashes', 'readonly').objectStore('hashes').get(current_hash);

                            if (storedRecord) {
                                return new Response(JSON.stringify({
                                    success: true,
                                    message: storedRecord.secretData ? 'Secret data extracted successfully (offline).' : 'No secret data embedded in this document.',
                                    secret_data: storedRecord.secretData || null,
                                    is_encrypted: storedRecord.isEncrypted,
                                    original_file: storedRecord.fileName
                                }), { headers: { 'Content-Type': 'application/json' } });
                            } else {
                                return new Response(JSON.stringify({ success: false, error: 'Document not recognized or tampered with (offline).' }), { status: 404, headers: { 'Content-Type': 'application/json' } });
                            }
                        } catch (error) {
                            return new Response(JSON.stringify({ success: false, error: `Service Worker Error: ${error.message}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
                        }
                    })();
                } else if (url.pathname === '/api/batch-protect' && event.request.method === 'POST') {
                    return (async () => {
                        try {
                            const formData = await event.request.formData();
                            const files = formData.getAll('files');
                            const original_hashes = formData.getAll('original_hashes');
                            const secretData = formData.get('secret_data');
                            const isEncrypted = formData.get('encrypt_payload') === 'on';

                            const db = await openDB();
                            const tx = db.transaction('hashes', 'readwrite');
                            const store = tx.objectStore('hashes');
                            const results = [];

                            for (let i = 0; i < files.length; i++) {
                                const file = files[i];
                                const original_hash = original_hashes[i];

                                await store.put({
                                    original_hash: original_hash,
                                    fileName: file.name,
                                    protection_date: new Date().toISOString(),
                                    secretData: secretData,
                                    isEncrypted: isEncrypted
                                });

                                const fileBuffer = await file.arrayBuffer();
                                const protected_file_data = arrayBufferToBase64(fileBuffer);

                                results.push({
                                    status: 'success',
                                    file: file.name,
                                    is_verified: true,
                                    current_hash: original_hash,
                                    stored_hash: original_hash,
                                    protected_file_data: protected_file_data,
                                    protected_filename: `protected_${file.name}`
                                });
                            }

                            await tx.done;

                            return new Response(JSON.stringify({
                                success: true,
                                message: 'Batch protection completed locally (offline).',
                                results: results
                            }), { headers: { 'Content-Type': 'application/json' } });

                        } catch (error) {
                            return new Response(JSON.stringify({ success: false, error: `Service Worker Batch Protect Error: ${error.message}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
                        }
                    })();
                } else if (url.pathname === '/api/batch-verify' && event.request.method === 'POST') {
                    return (async () => {
                        try {
                            const formData = await event.request.formData();
                            const files = formData.getAll('files');
                            const current_hashes = formData.getAll('current_hashes');

                            const db = await openDB();
                            const tx = db.transaction('hashes', 'readonly');
                            const store = tx.objectStore('hashes');
                            const results = [];

                            for (let i = 0; i < files.length; i++) {
                                const file = files[i];
                                const current_hash = current_hashes[i];
                                const storedRecord = await store.get(current_hash);

                                if (storedRecord) {
                                    results.push({
                                        status: 'success',
                                        file: file.name,
                                        is_verified: true,
                                        message: 'Document is VERIFIED (offline).',
                                        current_hash: current_hash,
                                        stored_hash: storedRecord.original_hash
                                    });
                                } else {
                                    results.push({
                                        status: 'success',
                                        file: file.name,
                                        is_verified: false,
                                        message: 'Document is UNKNOWN or has been TAMPERED with (offline).',
                                        current_hash: current_hash,
                                        stored_hash: 'N/A'
                                    });
                                }
                            }

                            return new Response(JSON.stringify({
                                success: true,
                                message: 'Batch verification completed locally (offline).',
                                results: results
                            }), { headers: { 'Content-Type': 'application/json' } });

                        } catch (error) {
                            return new Response(JSON.stringify({ success: false, error: `Service Worker Batch Verify Error: ${error.message}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
                        }
                    })();
                } else {
                    return new Response(JSON.stringify({ error: 'API endpoint not supported offline' }), { status: 404, headers: { 'Content-Type': 'application/json' } });
                }
            })
        );
        return;
    }

    // Network-first strategy for navigation and critical scripts
    if (event.request.mode === 'navigate' || event.request.url.includes('app.js') || event.request.url.includes('manifest.json')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Cache-first strategy for other assets
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
''