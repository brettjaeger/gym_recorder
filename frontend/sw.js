// Minimal service worker — required for PWA installability.
// No offline caching: the app needs network access to upload and parse images.
self.addEventListener('fetch', () => {});
