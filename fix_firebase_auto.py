import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Chamar initFirebase() ANTES de render(true)
# Localizamos onde initFirebase() é definido e onde render(true) é chamado
# Vamos mover a chamada de initFirebase() para antes do render(true)

old_first_render = 'render(true);\n\n\n/* ==========================================================================\n   SINCRONIZAÇÃO EM TEMPO REAL (FIREBASE REALTIME DB / LOCAL FALLBACK)'
new_first_render = '/* ==========================================================================\n   SINCRONIZAÇÃO EM TEMPO REAL (FIREBASE REALTIME DB / LOCAL FALLBACK)'

html = html.replace(old_first_render, new_first_render, 1)

# E no final do bloco do Firebase ou logo antes do primeiro render:
# Colocamos initFirebase() e em seguida render(true)
old_end_fb = '    console.warn("Aviso Firebase:", err);\n  }\n}'
new_end_fb = '''    console.warn("Aviso Firebase:", err);
  }
}

// Inicializa a conexão com a nuvem automaticamente antes de renderizar a interface
initFirebase();
render(true);'''

html = html.replace(old_end_fb, new_end_fb, 1)

# Remove a chamada duplicada do final do arquivo
html = html.replace('initFirebase();\nsetInterval(checkCivilAlertLoop, 600000);', 'setInterval(checkCivilAlertLoop, 600000);', 1)

# 2. Tornar o badge puramente informativo: não abrir modal de configuração desnecessário se já estiver conectado
old_badge = '''  const syncBtn = el("button", "sync-badge " + (firebaseDb ? "online" : "local"));
  syncBtn.type = "button";
  syncBtn.innerHTML = "<i></i> " + (firebaseDb ? "Online" : "Conectar Nuvem");
  syncBtn.addEventListener("click", () => openSyncModal());'''

new_badge = '''  const syncBtn = el("div", "sync-badge " + (firebaseDb ? "online" : "local"));
  syncBtn.innerHTML = "<i></i> " + (firebaseDb ? "Online" : "Conectando...");'''

html = html.replace(old_badge, new_badge, 1)

# 3. No listener de conexão do Firebase, forçar re-render do topo quando o banco conectar
old_listener = '    // Escuta tarefas feitas\n    firebaseDb.ref("tarefas_casa/done").on("value", snapshot => {'
new_listener = '''    // Atualiza status online no badge
    firebaseDb.ref(".info/connected").on("value", snap => {
      renderTop();
    });

    // Escuta tarefas feitas
    firebaseDb.ref("tarefas_casa/done").on("value", snapshot => {'''

html = html.replace(old_listener, new_listener, 1)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated public/index.html with auto-connecting Firebase!")
