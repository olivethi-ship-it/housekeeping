import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Definir constante DEVICE_OWNER_KEY e carregar deviceOwner
old_store = '''/* ---------- armazenamento (neste aparelho) ---------- */
let store = {person:null, mode:"ind", done:{}, v:2};'''

new_store = '''/* ---------- armazenamento (neste aparelho) ---------- */
const DEVICE_OWNER_KEY = "tarefas_device_owner";
let deviceOwner = localStorage.getItem(DEVICE_OWNER_KEY) || null; // Dono fixo deste aparelho
let store = {person:null, mode:"ind", done:{}, v:2};'''

html = html.replace(old_store, new_store)

# 2. Quando a pessoa clica no seu nome, se o aparelho ainda não tem dono definido, define deviceOwner!
old_set_person = 'c.addEventListener("click", () => { person = p; store.person = p; save(); render(true); });'
new_set_person = '''c.addEventListener("click", () => {
        person = p;
        store.person = p;
        if (!deviceOwner) {
          deviceOwner = p;
          localStorage.setItem(DEVICE_OWNER_KEY, p);
        }
        save();
        render(true);
      });'''

html = html.replace(old_set_person, new_set_person)

# 3. Adicionar no renderTop uma indicação visual e botão de alterar dono do celular
# Vamos ver como está o ppl em renderTop
old_ppl_render = '''    const ppl = el("div", "people"); ppl.setAttribute("role", "group"); ppl.setAttribute("aria-label", "Quem está usando");
    PEOPLE.forEach(p => {
      const c = el("button", "person"); c.type = "button"; c.setAttribute("aria-pressed", String(p === person));
      const dt = el("i", "dot"); dt.style.setProperty("--dot", dotVar(p)); c.append(dt, p);'''

new_ppl_render = '''    const ppl = el("div", "people"); ppl.setAttribute("role", "group"); ppl.setAttribute("aria-label", "Quem está usando");
    PEOPLE.forEach(p => {
      const isOwner = (deviceOwner === p);
      const c = el("button", "person"); c.type = "button"; c.setAttribute("aria-pressed", String(p === person));
      const dt = el("i", "dot"); dt.style.setProperty("--dot", dotVar(p)); 
      c.append(dt, p + (isOwner ? " (Meu)" : ""));'''

html = html.replace(old_ppl_render, new_ppl_render)

# 4. Modificar checkCivilAlertLoop para basear-se EXCLUSIVAMENTE em deviceOwner
old_loop = '''function checkCivilAlertLoop() {
  // 1. Ignora se estiver sob modo silêncio geral/férias ativo
  if (silenceState.active && silenceState.until > Date.now()) return;
  if (Date.now() < snoozeUntil) return;

  // 2. O alerta DEVE aparecer APENAS no celular da pessoa selecionada neste aparelho
  // Se nenhuma pessoa foi escolhida ainda (ex: tela inicial sem morador definido), não apita nem alerta ninguém
  const myPerson = store.person || person;
  if (!myPerson || !PEOPLE.includes(myPerson)) return;

  const d = today;
  const allTasks = tasksOn(d);

  // 3. Filtra ESTRITAMENTE as tarefas da própria pessoa que passaram do horário e não foram feitas por ela
  const myLateTasks = allTasks.filter(t => {
    return t.who.includes(myPerson) && isLate(d, t.quando) && !isDone(myPerson, d, t.name);
  });
    
  if (myLateTasks.length > 0) {
    triggerCivilDefenseAlert(myLateTasks);
  }
}'''

new_loop = '''function checkCivilAlertLoop() {
  // 1. Ignora se estiver sob modo silêncio geral/férias ativo
  if (silenceState.active && silenceState.until > Date.now()) return;
  if (Date.now() < snoozeUntil) return;

  // 2. O alerta TOCA E APARECE APENAS PARA O DONO DESTE CELULAR (deviceOwner)
  // Mesmo se ele estiver navegando e olhando as tarefas da Gigi, Lipe ou Renata, o alarme é SEMPRE dele!
  const myOwner = deviceOwner || store.person || person;
  if (!myOwner || !PEOPLE.includes(myOwner)) return;

  const d = today;
  const allTasks = tasksOn(d);

  // 3. Filtra ESTRITAMENTE as tarefas atrasadas e pendentes do DONO deste aparelho
  const ownerLateTasks = allTasks.filter(t => {
    return t.who.includes(myOwner) && isLate(d, t.quando) && !isDone(myOwner, d, t.name);
  });
    
  if (ownerLateTasks.length > 0) {
    triggerCivilDefenseAlert(ownerLateTasks);
  }
}'''

html = html.replace(old_loop, new_loop)

# 5. Adicionar configuração de "Definir Dono deste Celular" no Dashboard para facilitar se alguém quiser mudar
old_card_actions = '''  const notifyGranted = ("Notification" in window && Notification.permission === "granted");
  const btnReqNotify = el("button", "btn " + (notifyGranted ? "ghost" : ""), notifyGranted ? "🔔 Notificações Ativas ✓" : "🔔 Notificações Obrigatórias (Ativar)");'''

new_card_actions = '''  // Seletor de Dono do Celular
  const ownerBox = el("div", null);
  ownerBox.style.cssText = "display:flex;align-items:center;justify-content:space-between;gap:8px;background:var(--surface-2);padding:10px 14px;border-radius:12px;font-size:0.88rem";
  ownerBox.innerHTML = '<span>Dono deste aparelho: <b>' + (deviceOwner || "Não definido") + '</b></span>';
  const btnChangeOwner = el("button", "btn ghost", "Trocar");
  btnChangeOwner.style.cssText = "padding:4px 10px;font-size:0.8rem";
  btnChangeOwner.addEventListener("click", () => {
    const chosen = prompt("Quem é o dono principal deste celular?\\nDigite exatamente: Renata, Thiago, Giovana ou Felipe", deviceOwner || "Thiago");
    if (chosen && PEOPLE.includes(chosen.trim())) {
      deviceOwner = chosen.trim();
      localStorage.setItem(DEVICE_OWNER_KEY, deviceOwner);
      alert("Aparelho vinculado a " + deviceOwner + "! Os alertas sonoros e vibrações serão apenas das tarefas de " + deviceOwner + ".");
      render(false);
    }
  });
  ownerBox.appendChild(btnChangeOwner);
  cardActions.appendChild(ownerBox);

  const notifyGranted = ("Notification" in window && Notification.permission === "granted");
  const btnReqNotify = el("button", "btn " + (notifyGranted ? "ghost" : ""), notifyGranted ? "🔔 Notificações Ativas ✓" : "🔔 Notificações Obrigatórias (Ativar)");'''

html = html.replace(old_card_actions, new_card_actions)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated public/index.html with decoupled Device Owner & Viewing Person!")
