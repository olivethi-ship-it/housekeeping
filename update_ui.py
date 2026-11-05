import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Renomear "Acesso dos Pais" para "Admin"
html = html.replace('<h3 style="margin:0; font-family:var(--f-display)">Acesso dos Pais</h3>', '<h3 style="margin:0; font-family:var(--f-display)">Admin</h3>')
html = html.replace('p style="margin:0; color:var(--muted); font-size:0.88rem">Digite a senha de 4 dígitos para gerenciar o modo silêncio e configurações.', 'p style="margin:0; color:var(--muted); font-size:0.88rem">Digite a senha de 4 dígitos para acessar o painel de administração.')
html = html.replace('isAdminAuthenticated ? "🔓 Pais (Admin)" : "🔒 Acesso dos Pais"', 'isAdminAuthenticated ? "🔓 Admin" : "🔒 Admin"')
html = html.replace('⚙️ Painel de Controle dos Pais', '⚙️ Painel Admin')
html = html.replace('Alterar PIN dos Pais', 'Alterar PIN Admin')

# 2. Tornar notificação obrigatória: solicitar logo no primeiro toque na tela e verificar se já concedida
# Vamos adicionar uma rotina que requisita permissão no primeiro toque (exigência do iOS/Android)
notification_enforce = '''
// Solicitação OBRIGATÓRIA de notificações ao carregar ou no primeiro toque
function ensureNotificationPermission() {
  if ("Notification" in window) {
    if (Notification.permission === "default") {
      Notification.requestPermission().then(perm => {
        if (perm === "denied") {
          console.warn("Notificações bloqueadas pelo usuário.");
        }
      });
    }
  }
}
window.addEventListener("DOMContentLoaded", ensureNotificationPermission);
window.addEventListener("click", () => {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }
}, { passive: true });
'''

html = html.replace('initFirebase();', notification_enforce + '\ninitFirebase();')

# No botão do Dashboard, mostrar status obrigatório ativo
old_notify_btn = '''  const btnReqNotify = el("button", "btn", "🔔 Ativar Notificações no Celular");
  btnReqNotify.type = "button";
  btnReqNotify.addEventListener("click", () => {
    if ("Notification" in window) {
      Notification.requestPermission().then(perm => {
        alert("Status das Notificações: " + perm);
      });
    } else {
      alert("Notificações não são suportadas neste navegador diretamente.");
    }
  });'''

new_notify_btn = '''  const notifyGranted = ("Notification" in window && Notification.permission === "granted");
  const btnReqNotify = el("button", "btn " + (notifyGranted ? "ghost" : ""), notifyGranted ? "🔔 Notificações Ativas ✓" : "🔔 Notificações Obrigatórias (Ativar)");
  btnReqNotify.type = "button";
  btnReqNotify.addEventListener("click", () => {
    if ("Notification" in window) {
      Notification.requestPermission().then(perm => {
        if (perm === "granted") alert("Notificações ativadas com sucesso!");
        else alert("Atenção: As notificações são obrigatórias para os alertas. Ative nas permissões do seu navegador.");
        render(false);
      });
    } else {
      alert("Navegador sem suporte a Web Notifications.");
    }
  });'''

html = html.replace(old_notify_btn, new_notify_btn)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML updated with Admin name and Mandatory notifications!")
