import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Transformar const ROWS, PEOPLE, CODE, APELIDO, TEMPO em let para permitir reatribuição dinâmica
html = html.replace('const ROWS = [', 'let ROWS = [', 1)
html = html.replace('const PEOPLE = ["Renata","Thiago","Giovana","Felipe"];', 'let PEOPLE = ["Renata","Thiago","Giovana","Felipe"];', 1)
html = html.replace('const CODE = {"Rê":"Renata","Thi":"Thiago","Gigi":"Giovana","Lipe":"Felipe"};', 'let CODE = {"Rê":"Renata","Thi":"Thiago","Gigi":"Giovana","Lipe":"Felipe"};', 1)
html = html.replace('const APELIDO = {Renata:"Rê", Thiago:"Thi", Giovana:"Gigi", Felipe:"Lipe"};', 'let APELIDO = {Renata:"Rê", Thiago:"Thi", Giovana:"Gigi", Felipe:"Lipe"};', 1)
html = html.replace('const TEMPO = {', 'let TEMPO = {', 1)

# 2. Código de sincronização e persistência de tarefas e pessoas dinâmicas no Firebase
CRUD_MANAGEMENT_JS = '''
/* ---------- Gerenciamento Dinâmico de Tarefas e Pessoas ---------- */
function syncCustomDataToFirebase() {
  if (!firebaseDb) return;
  firebaseDb.ref("tarefas_casa/custom_config").set({
    rows: ROWS,
    people: PEOPLE,
    tempo: TEMPO,
    code: CODE,
    apelido: APELIDO
  });
}

function listenCustomDataFromFirebase() {
  if (!firebaseDb) return;
  firebaseDb.ref("tarefas_casa/custom_config").on("value", snap => {
    const data = snap.val();
    if (data && typeof data === "object") {
      if (Array.isArray(data.rows)) ROWS = data.rows;
      if (Array.isArray(data.people)) PEOPLE = data.people;
      if (data.tempo && typeof data.tempo === "object") TEMPO = data.tempo;
      if (data.code && typeof data.code === "object") CODE = data.code;
      if (data.apelido && typeof data.apelido === "object") APELIDO = data.apelido;
      render(false);
    }
  });
}

// Renderiza lista de pessoas no painel Admin
function renderPeopleManagerInAdmin() {
  const container = document.getElementById("admin-people-list");
  if (!container) return;
  container.innerHTML = "";
  
  PEOPLE.forEach(p => {
    const item = el("div", null);
    item.style.cssText = "display:flex;align-items:center;justify-content:space-between;padding:6px 10px;background:var(--surface-2);border-radius:8px;font-size:0.85rem";
    
    const info = el("div", null);
    const dt = el("i", "dot"); dt.style.setProperty("--dot", dotVar(p));
    info.append(dt, " " + p + " (Apelido: " + (APELIDO[p] || p) + ")");
    
    const btnDel = el("button", "histlink", "Remover");
    btnDel.style.cssText = "color:var(--late);font-size:0.75rem;padding:2px 6px";
    btnDel.addEventListener("click", () => {
      if (PEOPLE.length <= 1) {
        alert("Deve haver pelo menos 1 morador na casa.");
        return;
      }
      if (confirm("Deseja realmente remover " + p + " da escala da casa?")) {
        PEOPLE = PEOPLE.filter(x => x !== p);
        delete APELIDO[p];
        syncCustomDataToFirebase();
        renderPeopleManagerInAdmin();
        render(false);
      }
    });
    
    item.append(info, btnDel);
    container.appendChild(item);
  });
}

function addNewPersonPrompt() {
  const name = prompt("Nome do novo morador (ex: Lucas):");
  if (!name || !name.trim()) return;
  const cleanName = name.trim();
  if (PEOPLE.includes(cleanName)) {
    alert("Este morador já está cadastrado!");
    return;
  }
  const ap = prompt("Apelido curto para os botões (ex: Lu):", cleanName.slice(0, 3));
  PEOPLE.push(cleanName);
  const cleanAp = (ap && ap.trim()) ? ap.trim() : cleanName.slice(0, 3);
  APELIDO[cleanName] = cleanAp;
  CODE[cleanAp] = cleanName;
  syncCustomDataToFirebase();
  renderPeopleManagerInAdmin();
  render(false);
  alert("Morador " + cleanName + " adicionado com sucesso!");
}

// Renderiza gerenciador de tarefas no painel Admin
function renderTasksManagerInAdmin() {
  const container = document.getElementById("admin-tasks-list");
  if (!container) return;
  container.innerHTML = "";
  
  // Agrupa tarefas distintas
  const uniqueTasks = [];
  const seen = new Set();
  ROWS.forEach(r => {
    if (!seen.has(r[1])) {
      seen.add(r[1]);
      uniqueTasks.push({ name: r[1], day: r[0], slot: r[2], time: tempoOf(r[1]) });
    }
  });

  uniqueTasks.forEach(t => {
    const row = el("div", null);
    row.style.cssText = "display:flex;align-items:center;justify-content:space-between;gap:6px;padding:8px 10px;background:var(--surface-2);border-radius:10px;font-size:0.82rem";
    
    const details = el("div", null);
    details.style.cssText = "flex:1;min-width:0";
    details.innerHTML = '<div style="font-weight:700;line-height:1.2;margin-bottom:2px">' + t.name + '</div>'
      + '<span style="color:var(--muted);font-size:0.75rem">' + t.day + ' · ' + t.slot + ' · ⏱ ' + t.time + 'min</span>';
    
    const actions = el("div", null);
    actions.style.cssText = "display:flex;gap:4px;flex-shrink:0";
    
    const btnEdit = el("button", "histlink", "Editar");
    btnEdit.style.cssText = "font-size:0.75rem;padding:2px 4px";
    btnEdit.addEventListener("click", () => editTaskPrompt(t.name));

    const btnDel = el("button", "histlink", "Excluir");
    btnDel.style.cssText = "color:var(--late);font-size:0.75rem;padding:2px 4px";
    btnDel.addEventListener("click", () => {
      if (confirm("Deseja realmente excluir a tarefa: \\"" + t.name + "\\" de todos os dias da escala?")) {
        ROWS = ROWS.filter(r => r[1] !== t.name);
        delete TEMPO[t.name];
        syncCustomDataToFirebase();
        renderTasksManagerInAdmin();
        render(false);
      }
    });

    actions.append(btnEdit, btnDel);
    row.append(details, actions);
    container.appendChild(row);
  });
}

function editTaskPrompt(taskName) {
  const curTime = tempoOf(taskName);
  const newTime = prompt("Tempo estimado em minutos para \\"" + taskName + "\\":", curTime);
  if (newTime && !isNaN(parseInt(newTime))) {
    TEMPO[taskName] = parseInt(newTime);
  }
  const newName = prompt("Novo nome para a tarefa (deixe igual para não mudar):", taskName);
  if (newName && newName.trim() && newName.trim() !== taskName) {
    const finalName = newName.trim();
    ROWS.forEach(r => { if (r[1] === taskName) r[1] = finalName; });
    TEMPO[finalName] = TEMPO[taskName];
    delete TEMPO[taskName];
  }
  syncCustomDataToFirebase();
  renderTasksManagerInAdmin();
  render(false);
}

function addNewTaskPrompt() {
  const name = prompt("Nome da nova tarefa:");
  if (!name || !name.trim()) return;
  const finalName = name.trim();
  
  const day = prompt("Qual dia da semana? (Seg, Ter, Qua, Qui, Sex, Sáb ou Dom):", "Seg");
  const validDay = DIAS.includes(day) ? day : "Seg";

  const slot = prompt("Período? (Manhã, Tarde, Noite ou -):", "Manhã");
  const validSlot = ["Manhã","Tarde","Noite","-"].includes(slot) ? slot : "Manhã";

  const timeStr = prompt("Tempo estimado em minutos (ex: 15, 30, 45):", "20");
  const finalTime = parseInt(timeStr) || 20;

  const resp = prompt("Quem é o responsável? Digite o apelido (ex: " + Object.keys(CODE).join(", ") + ", ou Rê e Thi, ou Todos):", APELIDO[PEOPLE[0]] || "Todos");
  const finalResp = resp && resp.trim() ? resp.trim() : "Todos";

  // Adiciona a tarefa na escala das 4 semanas
  ROWS.push([validDay, finalName, validSlot, [finalResp, finalResp, finalResp, finalResp]]);
  TEMPO[finalName] = finalTime;

  syncCustomDataToFirebase();
  renderTasksManagerInAdmin();
  render(false);
  alert("Tarefa \\"" + finalName + "\\" criada e sincronizada com sucesso!");
}
'''

html = html.replace('// Inicializa a conexão com a nuvem automaticamente', CRUD_MANAGEMENT_JS + '\n// Inicializa a conexão com a nuvem automaticamente')

# Adiciona listenCustomDataFromFirebase dentro de initFirebase
html = html.replace('renderTop(); registerDevicePresence();\n    });', 'renderTop(); registerDevicePresence(); listenCustomDataFromFirebase();\n    });')

# Atualiza verifyPin para renderizar o gerenciador de tarefas e pessoas no Admin
html = html.replace('renderDeviceListInAdmin();\n    }', 'renderDeviceListInAdmin(); renderPeopleManagerInAdmin(); renderTasksManagerInAdmin();\n    }')

# 3. Adiciona a seção de Pessoas e Tarefas dentro do modal do Admin (silence-modal)
ADMIN_CRUD_HTML = '''
    <!-- Seção de Pessoas -->
    <hr style="border:0; border-top:1px solid var(--line); margin:6px 0">
    <div style="font-weight:700; font-size:0.95rem; display:flex; justify-content:space-between; align-items:center">
      <span>👥 Pessoas na Escala</span>
      <button class="histlink" style="font-size:0.8rem;padding:0;color:var(--p)" type="button" onclick="addNewPersonPrompt()">+ Adicionar Pessoa</button>
    </div>
    <div id="admin-people-list" style="display:grid; gap:6px; max-height:120px; overflow-y:auto"></div>

    <!-- Seção de Tarefas -->
    <hr style="border:0; border-top:1px solid var(--line); margin:6px 0">
    <div style="font-weight:700; font-size:0.95rem; display:flex; justify-content:space-between; align-items:center">
      <span>📋 Tarefas da Casa</span>
      <button class="histlink" style="font-size:0.8rem;padding:0;color:var(--p)" type="button" onclick="addNewTaskPrompt()">+ Nova Tarefa</button>
    </div>
    <div id="admin-tasks-list" style="display:grid; gap:6px; max-height:220px; overflow-y:auto"></div>
'''

html = html.replace('<div id="admin-devices-list" style="display:grid; gap:6px; max-height:160px; overflow-y:auto"></div>', '<div id="admin-devices-list" style="display:grid; gap:6px; max-height:160px; overflow-y:auto"></div>' + ADMIN_CRUD_HTML)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved public/index.html with full People & Task CRUD!")
