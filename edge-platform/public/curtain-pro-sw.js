// ACRO CURTAIN PRO 오프라인 지원 — 네트워크 우선, 끊기면 마지막으로 받은 화면을 보여 준다.
// 사이트 루트에 두지만 범위는 /curtain-pro 로 한정 (엣지컴퍼니 홈페이지 다른 페이지에는 관여하지 않음)
const CACHE = 'acro-curtain-pro-v1';
const PAGE = '/curtain-pro';
const PRECACHE = [PAGE, '/curtain-pro/manifest.webmanifest', '/curtain-pro/icon-192.png', '/curtain-pro/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).catch(() => undefined));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('acro-curtain-pro-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith('/curtain-pro')) return;
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match(PAGE))),
  );
});
