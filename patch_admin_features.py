import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# -------------------------------------------------------------
# 1. CORREÇÃO DE MARCAÇÃO DE TAREFAS & TRAVA DE ATRASADAS
# -------------------------------------------------------------
# Ajusta a função askOutOfDay para garantir que o overlay apareça corretamente com display: grid !important
old_ask = '''function askOutOfDay(d, label, action, from){
  const msg = document.getElementById("cf-msg"); msg.textContent = "";
  msg.append("A tarefa ", el("span", "tname", label), " é de " + dayName(d).toLowerCase() + ", e hoje é " + dayName(today).toLowerCase() + ". Quer marcar como feita mesmo assim?");
  cfAction = action; cfReturn = from; cf.hidden = false; document.getElementById("cf-yes").focus();
}
function closeCf(run){ cf.hidden = true; const a = cfAction; cfAction = null; if (run && a) a(); if (cfReturn && document.body.contains(cfReturn)) cfReturn.focus(); }'''

new_ask = '''function askOutOfDay(d, label, action, from){
  const msg = document.getElementById("cf-msg"); msg.textContent = "";
  msg.append("A tarefa ", el("span", "tname", label), " é de " + dayName(d).toLowerCase() + ", e hoje é " + dayName(today).toLowerCase() + ". Quer marcar como feita mesmo assim?");
  cfAction = action; cfReturn = from;
  cf.hidden = false;
  cf.style.setProperty("display", "grid", "important");
  document.getElementById("cf-yes").focus();
}
function closeCf(run){
  cf.hidden = true;
  cf.style.setProperty("display", "none", "important");
  const a = cfAction; cfAction = null;
  if (run && a) a();
  if (cfReturn && document.body.contains(cfReturn)) cfReturn.focus();
}'''

html = html.replace(old_ask, new_ask)

# Adiciona checagem de Admin para tarefas atrasadas na função tap:
old_tap = '''function tap(p, d, name, label, from){
  const k = keyOf(p, d, name);
  const run = () => { if (store.done[k]) { delete store.done[k]; syncTaskToCloud(k, null); } else { store.done[k] = Date.now(); syncTaskToCloud(k, store.done[k]); } save(); render(false); };
  if (!store.done[k] && d.getTime() !== today.getTime()) askOutOfDay(d, label, run, from); else run();
}'''

new_tap = '''function tap(p, d, name, label, from, quando){
  const k = keyOf(p, d, name);
  const isCurrentlyLate = isLate(d, quando);
  
  // Regra: Tarefa atrasada pendente SÓ pode ser liberada/marcada pelo Admin (exige PIN)
  if (!store.done[k] && isCurrentlyLate) {
    if (!isAdminAuthenticated) {
      alert("⚠️ Esta tarefa está ATRASADA! Apenas o Admin pode liberar a conclusão de tarefas atrasadas.");
      openPinModalForAction(() => {
        if (store.done[k]) { delete store.done[k]; syncTaskToCloud(k, null); }
        else { store.done[k] = Date.now(); syncTaskToCloud(k, store.done[k]); }
        save();
        render(false);
      });
      return;
    }
  }

  const run = () => {
    if (store.done[k]) { delete store.done[k]; syncTaskToCloud(k, null); }
    else { store.done[k] = Date.now(); syncTaskToCloud(k, store.done[k]); }
    save();
    render(false);
  };
  
  if (!store.done[k] && d.getTime() !== today.getTime()) {
    askOutOfDay(d, label, run, from);
  } else {
    run();
  }
}'''

html = html.replace(old_tap, new_tap)

# Atualiza chamadas de tap passando t.quando:
html = html.replace('row.addEventListener("click", () => tap(p, d, t.name, label, row));', 'row.addEventListener("click", () => tap(p, d, t.name, label, row, t.quando));')
html = html.replace('b.addEventListener("click", () => tap(p, d, t.name, (CURTO[t.name] || t.name) + " (" + APELIDO[p] + ")", b));', 'b.addEventListener("click", () => tap(p, d, t.name, (CURTO[t.name] || t.name) + " (" + APELIDO[p] + ")", b, t.quando));')

# -------------------------------------------------------------
# 2. PIN MODAL COM AÇÃO CALLBACK (PARA LIBERAR ATRASADA)
# -------------------------------------------------------------
old_pin_action = 'let currentPinInput = "";'
new_pin_action = '''let currentPinInput = "";
let pendingAdminAction = null;

function openPinModalForAction(callback) {
  pendingAdminAction = callback;
  openPinModal();
}'''

html = html.replace(old_pin_action, new_pin_action)

old_verify_pin = '''function verifyPin() {
  if (currentPinInput === adminPin) {
    isAdminAuthenticated = true;
    closePinModal();
    document.getElementById("silence-modal").hidden = false;
    document.getElementById("silence-modal").style.setProperty("display", "grid", "important");
  } else {'''

new_verify_pin = '''function verifyPin() {
  if (currentPinInput === adminPin) {
    isAdminAuthenticated = true;
    closePinModal();
    if (pendingAdminAction) {
      const act = pendingAdminAction;
      pendingAdminAction = null;
      act();
    } else {
      document.getElementById("silence-modal").hidden = false;
      document.getElementById("silence-modal").style.setProperty("display", "grid", "important");
      renderDeviceListInAdmin();
    }
  } else {'''

html = html.replace(old_verify_pin, new_verify_pin)

# -------------------------------------------------------------
# 3. GERENCIAMENTO DE APARELHOS NO ADMIN & TELEMETRIA
# -------------------------------------------------------------
DEVICE_MGMT_JS = '''
/* ---------- Gerenciamento Remoto de Dispositivos pelo Admin ---------- */
const DEVICE_ID_KEY = "tarefas_device_id";
let myDeviceId = localStorage.getItem(DEVICE_ID_KEY);
if (!myDeviceId) {
  myDeviceId = "dev_" + Math.random().toString(36).substr(2, 9);
  localStorage.setItem(DEVICE_ID_KEY, myDeviceId);
}

// Detecta modelo/plataforma amigável do aparelho
function detectDeviceInfo() {
  const ua = navigator.userAgent;
  let model = "Computador / Navegador";
  if (/iPhone/i.test(ua)) model = "iPhone (Apple)";
  else if (/iPad/i.test(ua)) model = "iPad (Apple)";
  else if (/Android/i.test(ua)) {
    const match = ua.match(/Android[^;]+;\\s*([^;)]+)/);
    model = match ? "Android (" + match[1].trim() + ")" : "Celular Android";
  }
  return model;
}

// Registra presença do aparelho no Firebase RTDB
function registerDevicePresence() {
  if (!firebaseDb) return;
  const devRef = firebaseDb.ref("tarefas_casa/devices/" + myDeviceId);
  devRef.update({
    id: myDeviceId,
    model: detectDeviceInfo(),
    owner: deviceOwner || "Não atribuído",
    lastSeen: Date.now()
  });
  
  // Escuta se o Admin atribuiu este celular a um dono remotamente!
  devRef.child("owner").on("value", snap => {
    const assigned = snap.val();
    if (assigned && assigned !== "Não atribuído" && assigned !== deviceOwner) {
      deviceOwner = assigned;
      localStorage.setItem(DEVICE_OWNER_KEY, assigned);
      render(false);
    }
  });
}

// Renderiza a lista de celulares dentro do painel Admin
function renderDeviceListInAdmin() {
  const listEl = document.getElementById("admin-devices-list");
  if (!listEl || !firebaseDb) return;
  listEl.innerHTML = '<div style="font-size:0.85rem;color:var(--muted)">Carregando celulares conectados...</div>';
  
  firebaseDb.ref("tarefas_casa/devices").once("value", snap => {
    listEl.innerHTML = "";
    const devs = snap.val();
    if (!devs) {
      listEl.innerHTML = '<div style="font-size:0.85rem;color:var(--muted)">Nenhum aparelho detectado ainda.</div>';
      return;
    }
    Object.values(devs).forEach(d => {
      const row = el("div", null);
      row.style.cssText = "display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 10px;background:var(--surface-2);border-radius:10px;font-size:0.85rem";
      
      const isMe = (d.id === myDeviceId);
      row.innerHTML = '<div><b>' + d.model + '</b>' + (isMe ? ' <small style="color:var(--ok)">(Este aparelho)</small>' : '') + '<div style="color:var(--muted);font-size:0.78rem">Dono atual: <b style="color:var(--p)">' + (d.owner || "Sem dono") + '</b></div></div>';
      
      const sel = el("select", null);
      sel.style.cssText = "padding:4px 8px;border-radius:8px;border:1px solid var(--line);font-size:0.8rem;background:var(--surface);color:var(--ink)";
      sel.innerHTML = '<option value="">Atribuir...</option>' + PEOPLE.map(p => '<option value="' + p + '" ' + (d.owner === p ? 'selected' : '') + '>' + p + '</option>').join("");
      sel.addEventListener("change", (e) => {
        const newOwner = e.target.value;
        if (newOwner) {
          firebaseDb.ref("tarefas_casa/devices/" + d.id + "/owner").set(newOwner);
          if (isMe) {
            deviceOwner = newOwner;
            localStorage.setItem(DEVICE_OWNER_KEY, newOwner);
            render(false);
          }
          alert("Celular " + d.model + " atribuído com sucesso a " + newOwner + "!");
        }
      });
      
      row.appendChild(sel);
      listEl.appendChild(row);
    });
  });
}
'''

html = html.replace('/* ---------- Gerenciamento Remoto de Dispositivos pelo Admin ---------- */', '')
html = html.replace('// Inicializa a conexão com a nuvem automaticamente', DEVICE_MGMT_JS + '\n// Inicializa a conexão com a nuvem automaticamente')

# Adiciona chamada de registerDevicePresence no listener online
html = html.replace('renderTop();\n    });', 'renderTop(); registerDevicePresence();\n    });')

# -------------------------------------------------------------
# 4. ADICIONA SEÇÃO DE APARELHOS NO MODAL DO ADMIN
# -------------------------------------------------------------
DEVICE_SECTION_HTML = '''
    <hr style="border:0; border-top:1px solid var(--line); margin:6px 0">
    <div style="font-weight:700; font-size:0.95rem; display:flex; justify-content:space-between; align-items:center">
      <span>📱 Celulares Conectados</span>
      <button class="histlink" style="font-size:0.8rem;padding:0" type="button" onclick="renderDeviceListInAdmin()">Atualizar</button>
    </div>
    <div id="admin-devices-list" style="display:grid; gap:6px; max-height:160px; overflow-y:auto"></div>
'''

html = html.replace('<label style="font-weight:700; font-size:0.85rem">Alterar PIN Admin', DEVICE_SECTION_HTML + '\n    <label style="font-weight:700; font-size:0.85rem">Alterar PIN Admin')

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with task unblocking & remote device management!")
