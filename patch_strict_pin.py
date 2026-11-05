import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remover persistência de autenticação do PIN no localStorage
old_auth_cache = '''try {
  const cachedAuth = JSON.parse(localStorage.getItem(PIN_STORAGE_KEY) || "null");
  if (cachedAuth && cachedAuth.expires > Date.now()) {
    isAdminAuthenticated = true;
  }
} catch(e) {}'''

new_auth_cache = '''// Sessão de admin NÃO persiste: exige digitação do PIN a CADA acesso
localStorage.removeItem(PIN_STORAGE_KEY);
isAdminAuthenticated = false;'''

html = html.replace(old_auth_cache, new_auth_cache)

# 2. Na verificação do PIN: abre o modal do painel temporariamente, mas fecha e desautentica ao sair
old_verify = '''function verifyPin() {
  if (currentPinInput === adminPin) {
    isAdminAuthenticated = true;
    localStorage.setItem(PIN_STORAGE_KEY, JSON.stringify({
      auth: true,
      expires: Date.now() + 30 * 86400000 // 30 dias
    }));
    closePinModal();
    openSilenceModal();
    render(false);
  } else {
    alert("PIN incorreto!");
    currentPinInput = "";
    updatePinDots();
  }
}'''

new_verify = '''function verifyPin() {
  if (currentPinInput === adminPin) {
    isAdminAuthenticated = true;
    closePinModal();
    document.getElementById("silence-modal").hidden = false;
    document.getElementById("silence-modal").style.setProperty("display", "grid", "important");
  } else {
    alert("PIN incorreto!");
    currentPinInput = "";
    updatePinDots();
  }
}'''

html = html.replace(old_verify, new_verify)

# 3. Sempre que fechar o modal Admin (silence-modal), revogar o acesso imediatamente!
old_close_silence = '''function closeSilenceModal() {
  document.getElementById("silence-modal").hidden = true;
}'''

new_close_silence = '''function closeSilenceModal() {
  const elSil = document.getElementById("silence-modal");
  if (elSil) {
    elSil.hidden = true;
    elSil.style.setProperty("display", "none", "important");
  }
  // Revoga autenticação imediatamente: próximo clique exigirá PIN novamente
  isAdminAuthenticated = false;
  currentPinInput = "";
  render(false);
}'''

html = html.replace(old_close_silence, new_close_silence)

# 4. No botão do Dashboard: sempre abre o modal do PIN para pedir a senha
old_lock_click = '''  lockBtn.addEventListener("click", () => {
    if (isAdminAuthenticated) openSilenceModal();
    else openPinModal();
  });'''

new_lock_click = '''  lockBtn.addEventListener("click", () => {
    openPinModal();
  });'''

html = html.replace(old_lock_click, new_lock_click)

# E manter o texto do botão sempre com o cadeado fechado "🔒 Admin"
html = html.replace('const lockBtn = el("button", "admin-badge-lock", isAdminAuthenticated ? "🔓 Admin" : "🔒 Admin");', 'const lockBtn = el("button", "admin-badge-lock", "🔒 Admin");')

# 5. Ao salvar o PIN, atualizar adminPin e fechar revogando acesso
old_change_pin = '''    localStorage.setItem("tarefas_admin_pin_val", np);
    alert("PIN de Admin alterado com sucesso para " + np);
    document.getElementById("new-pin-input").value = "";
    closeSilenceModal();'''

new_change_pin = '''    localStorage.setItem("tarefas_admin_pin_val", np);
    alert("PIN de Admin alterado com sucesso para " + np + "! Na próxima vez que abrir o Admin, use a nova senha.");
    document.getElementById("new-pin-input").value = "";
    closeSilenceModal();'''

html = html.replace(old_change_pin, new_change_pin)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated public/index.html with strict per-access PIN verification!")
