import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defaultsFromHtml, configFrom, keyOf, lateByPerson, plan, isQuietHour } from "../scripts/late.mjs";

const html = readFileSync(fileURLToPath(new URL("../public/index.html", import.meta.url)), "utf8");
const defaults = defaultsFromHtml(html);
const cfg = configFrom(null, defaults);
const at = (y, m, d, h, min = 0) => new Date(y, m - 1, d, h, min);
const sub = { endpoint: "https://push.example/x", keys: { p256dh: "a", auth: "b" } };

test("lê a escala padrão do index.html", () => {
  assert.equal(defaults.rows.length > 50, true);
  assert.deepEqual(defaults.people, ["Renata", "Thiago", "Giovana", "Felipe"]);
  assert.equal(defaults.code["Thi"], "Thiago");
});

test("sexta 13h: tarefas da manhã atrasadas, da tarde ainda não", () => {
  const late = lateByPerson(cfg, {}, at(2026, 11, 6, 13));
  assert.deepEqual(late.Renata.sort(), ["Passear com a Pretinha, colocar comida e água (manhã/almoço)", "Preparar o almoço"]);
  assert.deepEqual(late.Thiago, ["Retirar a louça da máquina e do escorredor e guardar"]);
  assert.equal(late.Giovana, undefined);
});

test("tarefa marcada como feita (chave codificada da nuvem) não alerta", () => {
  const k = keyOf("Thiago", at(2026, 11, 6, 0), "Retirar a louça da máquina e do escorredor e guardar");
  const done = { [encodeURIComponent(k).replace(/\./g, "%2E")]: 1 };
  assert.equal(lateByPerson(cfg, done, at(2026, 11, 6, 13)).Thiago, undefined);
});

test("até 2h da madrugada ainda conta como o dia anterior", () => {
  const late = lateByPerson(cfg, {}, at(2026, 11, 7, 1));
  assert.ok(late.Thiago.includes("Lavar a louça, limpar a pia e a mesa do almoço"));
});

test("compras usam o texto individual na chave", () => {
  assert.equal(keyOf("Renata", at(2026, 11, 5, 0), "Compras de mercado"), "Renata|2026-11-05|Compras de mercado (junto com o Thiago)");
});

test("antes do início do ciclo não há tarefas", () => {
  assert.deepEqual(lateByPerson(cfg, {}, at(2026, 10, 10, 20)), {});
});

test("configuração da nuvem substitui a escala e decodifica as chaves", () => {
  const rows = defaults.rows.map(r => r[0] === "Sex" && r[1] === "Preparar o almoço" ? [r[0], r[1], r[2], ["Gigi", "Gigi", "Gigi", "Gigi"]] : r);
  const cloud = configFrom({ rows, people: defaults.people, code: { "Gigi": "Giovana", "R%C3%AA": "Renata", "Thi": "Thiago", "Lipe": "Felipe" } }, defaults);
  const late = lateByPerson(cloud, {}, at(2026, 11, 6, 13));
  assert.deepEqual(late.Giovana, ["Preparar o almoço"]);
  assert.deepEqual(late.Renata, ["Passear com a Pretinha, colocar comida e água (manhã/almoço)"]);
});

test("plano envia só para aparelhos com push e dono atrasado", () => {
  const state = {
    done: {},
    devices: {
      a: { id: "a", owner: "Thiago", push: { sub } },
      b: { id: "b", owner: "Giovana", push: { sub } },
      c: { id: "c", owner: "Renata" },
      d: { id: "d", owner: "Não atribuído", push: { sub } }
    }
  };
  const p = plan(state, defaults, at(2026, 11, 6, 13));
  assert.deepEqual(p.map(x => [x.deviceId, x.person, x.tasks.length]), [["a", "Thiago", 1]]);
  assert.deepEqual(p[0].sub, sub);
});

test("silêncio noturno: das 22h às 7h não envia; fora disso envia", () => {
  const devices = { a: { id: "a", owner: "Thiago", push: { sub } } };
  assert.equal(isQuietHour(at(2026, 11, 6, 21, 59)), false);
  assert.equal(isQuietHour(at(2026, 11, 6, 22, 0)), true);
  assert.equal(isQuietHour(at(2026, 11, 7, 6, 59)), true);
  assert.equal(isQuietHour(at(2026, 11, 7, 7, 0)), false);
  assert.equal(plan({ devices }, defaults, at(2026, 11, 6, 22, 30)).length, 0);
  assert.equal(plan({ devices }, defaults, at(2026, 11, 6, 21, 30)).length, 1);
});

test("modo silêncio ativo não envia nada; vencido volta a enviar", () => {
  const now = at(2026, 11, 6, 13);
  const devices = { a: { id: "a", owner: "Thiago", push: { sub } } };
  assert.equal(plan({ devices, silence: { active: true, until: now.getTime() + 60000 } }, defaults, now).length, 0);
  assert.equal(plan({ devices, silence: { active: true, until: now.getTime() - 60000 } }, defaults, now).length, 1);
});
