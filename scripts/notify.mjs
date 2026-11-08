// Agendador de alertas (GitHub Actions, a cada 10 min): envia push a quem está com tarefa atrasada.
// Variáveis: VAPID_PRIVATE_KEY (segredo), TESTE=true para mandar um aviso de teste a todos os aparelhos.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import webpush from "web-push";
import { defaultsFromHtml, plan } from "./late.mjs";

const DB = process.env.DB_URL || "https://casa-tarefas-ab1f5-default-rtdb.firebaseio.com";
const html = readFileSync(fileURLToPath(new URL("../public/index.html", import.meta.url)), "utf8");
const publicKey = (html.match(/const VAPID_PUBLIC = "([^"]+)"/) || [])[1];
const privateKey = process.env.VAPID_PRIVATE_KEY;
if (!publicKey || !privateKey) { console.error("Faltam chaves VAPID (pública no index.html, privada no segredo)."); process.exit(1); }
webpush.setVapidDetails("https://casa-tarefas-ab1f5.web.app", publicKey, privateKey);

const res = await fetch(DB + "/tarefas_casa.json");
if (!res.ok) { console.error("Falha ao ler o banco:", res.status); process.exit(1); }
const state = (await res.json()) || {};
const now = new Date();

let envios;
if (process.env.TESTE === "true") {
  envios = Object.entries(state.devices || {})
    .filter(([, d]) => d && d.push && d.push.sub)
    .map(([id, d]) => ({ deviceId: id, person: d.owner, sub: d.push.sub, payload: {
      title: "🔔 Teste de alerta", body: "Se você está vendo isto, os alertas de atraso funcionam neste aparelho.", tag: "teste" } }));
} else {
  envios = plan(state, defaultsFromHtml(html), now).map(e => ({ ...e, payload: {
    title: "🚨 " + e.person + ", tarefa atrasada!",
    body: e.tasks.length === 1 ? e.tasks[0] : e.tasks.length + " tarefas atrasadas: " + e.tasks.join(" · "),
    tag: "atraso" } }));
}

let ok = 0, falhas = 0, removidas = 0;
for (const e of envios) {
  try {
    await webpush.sendNotification(e.sub, JSON.stringify(e.payload), { TTL: 600, urgency: "high", topic: e.payload.tag });
    ok++;
  } catch (err) {
    if (err.statusCode === 404 || err.statusCode === 410) {   // assinatura expirada ou cancelada
      await fetch(DB + "/tarefas_casa/devices/" + encodeURIComponent(e.deviceId) + "/push.json", { method: "DELETE" });
      removidas++;
    } else {
      falhas++;
      console.error("Falha ao enviar para aparelho de " + e.person + ":", err.statusCode || err.message);
    }
  }
}
console.log(`${now.toLocaleString("pt-BR")} — envios: ${envios.length}, ok: ${ok}, expiradas removidas: ${removidas}, falhas: ${falhas}`);
if (falhas && !ok) process.exit(1);
