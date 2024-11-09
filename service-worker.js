// service-worker.js
const CACHE_NAME = 'jyf0214-blog-cache-v1';
const urlsToCache = [
  '/',
  '/favicon.ico',
  '/manifest.json',
  '/src/main.ts',
  // 添加其他静态资源路径
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