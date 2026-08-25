self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // This is a minimal Service Worker.
  // It just passes the requests to the network since we require an online database connection.
  // Having this file is enough to trick the browser into showing the "Install App" prompt!
  e.respondWith(fetch(e.request));
});
