// Regras de atraso usadas pelo agendador (GitHub Actions).
// ATENÇÃO: espelham as funções de public/index.html (tasksOn, indText, keyOf, isLate, houseDay).
// Mudou uma regra lá, mude aqui; tests/late.test.mjs cobre este arquivo.

const DAY = 86400000;
const CYCLE0 = new Date(2026, 9, 19);   // segunda, 19/10/2026 (fuso do processo: TZ=America/Sao_Paulo no workflow)
const GRACE_H = 2;
const DEADLINE = { "Manhã": 12, "Tarde": 18, "Noite": 24 + GRACE_H, "-": 24 + GRACE_H };
const DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const iso = d => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
const diaOf = d => DIAS[(d.getDay() + 6) % 7];
const mondayOf = d => addDays(d, -((d.getDay() + 6) % 7));
const weekIdx = d => Math.floor(Math.round((mondayOf(d) - CYCLE0) / DAY) / 7);
const localKey = k => { try { return decodeURIComponent(k); } catch { return k; } };
const decodeMap = m => Object.fromEntries(Object.entries(m || {}).map(([k, v]) => [localKey(k), v]));

export function houseDay(now) {
  const n = new Date(now.getTime() - GRACE_H * 3600000);
  n.setHours(0, 0, 0, 0);
  return n;
}

/** Escala padrão embutida no index.html (usada enquanto não houver custom_config na nuvem). */
export function defaultsFromHtml(html) {
  const grab = name => {
    const m = html.match(new RegExp("^let " + name + " = (.+?);\\s*(//.*)?$", "m"));
    if (!m) throw new Error("Não achei " + name + " no index.html");
    return JSON.parse(m[1]);
  };
  return { rows: grab("ROWS"), people: grab("PEOPLE"), code: grab("CODE") };
}

export function configFrom(cloud, defaults) {
  const c = cloud && typeof cloud === "object" ? cloud : {};
  return {
    rows: Array.isArray(c.rows) ? c.rows : defaults.rows,
    people: Array.isArray(c.people) ? c.people : defaults.people,
    code: c.code && typeof c.code === "object" ? decodeMap(c.code) : defaults.code
  };
}

export function tasksOn(cfg, d) {
  const w = weekIdx(d); if (w < 0) return [];
  const c = ((w % 4) + 4) % 4, dia = diaOf(d), out = [];
  cfg.rows.forEach(r => {
    if (!r || r[0] !== dia) return;
    const code = (r[3] || [])[c]; if (!code || code === "—") return;
    const who = (code === "Rê e Thi" ? ["Renata", "Thiago"] : code === "Todos" ? cfg.people.slice() : [cfg.code[code]])
      .filter(p => cfg.people.includes(p));
    if (who.length) out.push({ name: r[1], quando: r[2], who });
  });
  return out;
}

const indText = (p, name) => (name === "Compras de frutas e legumes" || name === "Compras de mercado")
  ? name + (p === "Renata" ? " (junto com o Thiago)" : " (junto com a Renata)") : name;
export const keyOf = (p, d, name) => p + "|" + iso(d) + "|" + indText(p, name);
const isLate = (d, quando, now) => now.getTime() > d.getTime() + DEADLINE[quando] * 3600000;

/** { pessoa: [nomes das tarefas atrasadas e não feitas hoje] } */
export function lateByPerson(cfg, cloudDone, now) {
  const done = decodeMap(cloudDone);
  const d = houseDay(now), out = {};
  tasksOn(cfg, d).forEach(t => {
    if (!(t.quando in DEADLINE) || !isLate(d, t.quando, now)) return;
    t.who.forEach(p => { if (!done[keyOf(p, d, t.name)]) (out[p] = out[p] || []).push(t.name); });
  });
  return out;
}

/** Lista de envios: [{deviceId, person, tasks, sub}] */
export function plan(state, defaults, now) {
  const s = state || {};
  if (s.silence && s.silence.active && s.silence.until > now.getTime()) return [];
  const late = lateByPerson(configFrom(s.custom_config, defaults), s.done, now);
  return Object.entries(s.devices || {})
    .filter(([, dev]) => dev && dev.push && dev.push.sub && late[dev.owner])
    .map(([id, dev]) => ({ deviceId: id, person: dev.owner, tasks: late[dev.owner], sub: dev.push.sub }));
}
