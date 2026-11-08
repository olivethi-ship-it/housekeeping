// Service worker: recebe os alertas de atraso mesmo com o app fechado.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { body: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.title || "🚨 Tarefa atrasada", {
    body: d.body || "Você tem tarefas atrasadas. Abra o app e marque o que já fez.",
    tag: d.tag || "atraso",
    renotify: true,               // toca e vibra de novo mesmo substituindo o aviso anterior
    requireInteraction: true,     // fica na tela até ser tocado
    vibrate: [500, 200, 500, 200, 900],
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    data: { url: d.url || "/" }
  }));
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || "/";
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(wins => {
    for (const w of wins) if ("focus" in w) return w.focus();
    return self.clients.openWindow(url);
  }));
});
