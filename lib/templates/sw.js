const CACHE_NAME = 'gps-tracker-v2';
const ASSETS = [
  'https://your-domain.cloudflare/',
  'https://your-domain.cloudflare/index.html',
  'https://your-domain.cloudflare/manifest.json',
  'https://api.mapbox.com/mapbox-gl-js/v2.13.0/mapbox-gl.js',
  'https://api.mapbox.com/mapbox-gl-js/v2.13.0/mapbox-gl.css',
  'https://your-domain.cloudflare/icons/icon-192x192.png',
  'https://your-domain.cloudflare/icons/icon-512x512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/get_coordinates')) {
    // Non cacheare le richieste di dati in tempo reale
    return fetch(event.request);
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        return cachedResponse || fetch(event.request)
          .then(response => {
            return caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, response.clone());
              return response;
            });
          });
      })
  );
});