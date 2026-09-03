const CACHE_NAME = 'qr-offline-dynamic';
const ASSETS = [
  '/offline',
  '/static/icon.png',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://unpkg.com/html5-qrcode',
  'https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME && key.startsWith('qr-offline-')) {
          return caches.delete(key);
        }
      }));
    })
  );
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  if (e.request.mode === 'navigate' || e.request.url.includes('/offline')) {
    e.respondWith(
      fetch(e.request).then((response) => {
        // Dynamically update cache with the newest version for offline use!
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, responseClone));
        return response;
      }).catch(() => {
        // 100% Offline fallback
        return caches.match(e.request);
      })
    );
  } else {
    e.respondWith(
      caches.match(e.request).then((cachedResponse) => {
        return cachedResponse || fetch(e.request);
      })
    );
  }
});
