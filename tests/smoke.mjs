// Barreira de regressão: roda sem dependências (node tests/smoke.mjs) e no predeploy do Firebase.
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const pub = join(dirname(fileURLToPath(import.meta.url)), "..", "public");
const html = readFileSync(join(pub, "index.html"), "utf8");
const falhas = [];
const check = (ok, msg) => { if (!ok) falhas.push(msg); };

// 1. Nenhum marcador de conflito de merge
check(!/^(<{7}|={7}|>{7})/m.test(html), "index.html contém marcador de conflito de merge");

// 2. Todo <script> inline precisa compilar
const inline = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
check(inline.length > 0, "nenhum script inline encontrado");
inline.forEach((code, i) => {
  try { new vm.Script(code, { filename: `inline-${i}.js` }); }
  catch (e) { check(false, `script inline #${i} não compila: ${e.message}`); }
});

// 3. Todo script local referenciado precisa existir
for (const m of html.matchAll(/<script[^>]*\bsrc="(?!https?:)([^"]+)"/g)) {
  check(existsSync(join(pub, m[1])), `script referenciado não existe: ${m[1]}`);
}

// 4. A sincronização é uma só e devolve as chaves ao formato usado por isDone
const all = inline.join("\n");
check((all.match(/function syncTaskToCloud\(/g) || []).length === 1, "syncTaskToCloud deve ter uma única definição");
check(/\bcloudKey\(/.test(all) && /\blocalKey\(/.test(all), "faltam cloudKey/localKey para ida e volta da chave");

// 5. Ida e volta da chave do Firebase, com os caracteres reais das tarefas
const sandbox = {};
const src = all.match(/const cloudKey = [^\n]+\nconst localKey = [^\n]+/);
check(src, "cloudKey/localKey não encontrados em duas linhas seguidas");
if (src) {
  vm.runInNewContext(`${src[0].replace(/const /g, "var ")}`, sandbox);
  const k = "Renata|2026-11-06|Passear com a Pretinha, colocar comida e água (manhã/almoço)";
  const c = sandbox.cloudKey(k);
  check(!/[.#$/[\]]/.test(c), "chave da nuvem contém caractere proibido pelo Firebase");
  check(sandbox.localKey(c) === k, "cloudKey/localKey não fazem ida e volta");
  check(sandbox.localKey(k) === k, "localKey deve preservar chave já decodificada");
}

// 6. custom_config não pode ter chave proibida: TEMPO usa nomes de tarefa como chave
check(/const encodeTempo = [^\n]+\nconst decodeTempo = [^\n]+/.test(all), "faltam encodeTempo/decodeTempo");
const tempoSrc = all.match(/const encodeTempo = [^\n]+\nconst decodeTempo = [^\n]+/);
if (src && tempoSrc) {
  const sb = {};
  vm.runInNewContext(`${src[0]}\n${tempoSrc[0]}`.replace(/const /g, "var "), sb);
  const tempo = { "Passear (manhã/almoço)": 30, "Lavar a louça": 25 };
  const enc = JSON.parse(JSON.stringify(sb.encodeTempo(tempo)));
  check(Object.keys(enc).every(k => !/[.#$/[\]]/.test(k)), "tempo codificado ainda tem chave proibida pelo Firebase");
  check(JSON.stringify(JSON.parse(JSON.stringify(sb.decodeTempo(enc)))) === JSON.stringify(tempo), "encodeTempo/decodeTempo não fazem ida e volta");
}

// 7. Admin tem a tela de associação de responsáveis por semana
check(html.includes('id="admin-assign-list"'), "falta a lista de associação no Admin");
check(/function renderAssignInAdmin\(/.test(all), "falta renderAssignInAdmin");

// 8. PWA com push: manifest, service worker, ícones e chave pública VAPID
check(/<link rel="manifest" href="\/manifest\.json">/.test(html), "falta o link do manifest");
for (const f of ["manifest.json", "sw.js", "icon-192.png", "icon-512.png"]) check(existsSync(join(pub, f)), `falta public/${f}`);
if (existsSync(join(pub, "manifest.json"))) {
  const mf = JSON.parse(readFileSync(join(pub, "manifest.json"), "utf8"));
  check(mf.display === "standalone" && mf.icons?.length >= 2, "manifest precisa de display standalone e 2 ícones");
}
if (existsSync(join(pub, "sw.js"))) {
  const sw = readFileSync(join(pub, "sw.js"), "utf8");
  try { new vm.Script(sw); } catch (e) { check(false, "sw.js não compila: " + e.message); }
  check(/addEventListener\("push"/.test(sw) && /notificationclick/.test(sw), "sw.js precisa tratar push e notificationclick");
}
check(/const VAPID_PUBLIC = "[A-Za-z0-9_-]{80,}";/.test(all), "falta a chave pública VAPID");
check(!/new Notification\(/.test(all), "new Notification() falha no Android; use registration.showNotification");

if (falhas.length) { console.error("FALHOU:\n- " + falhas.join("\n- ")); process.exit(1); }
console.log("OK: smoke test passou");
