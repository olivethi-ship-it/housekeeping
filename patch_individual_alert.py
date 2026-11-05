import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\thiag\homework\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Substituir checkCivilAlertLoop para alertar APENAS o dono do celular e APENAS as tarefas dele
old_loop = '''function checkCivilAlertLoop() {
  // Ignora se estiver sob silêncio geral/férias ativado pelos pais
  if (silenceState.active && silenceState.until > Date.now()) return;
  if (Date.now() < snoozeUntil) return;
  const d = today;
  const allTasks = tasksOn(d);
  // Se estiver com pessoa selecionada no modo individual, alerta só dela; senão, alerta de todos
  const targetTasks = mode === "ind" && person
    ? allTasks.filter(t => t.who.includes(person) && isLate(d, t.quando) && !isDone(person, d, t.name))
    : allTasks.filter(t => isLate(d, t.quando) && t.who.some(p => !isDone(p, d, t.name)));
    
  if (targetTasks.length > 0) {
    triggerCivilDefenseAlert(targetTasks);
  }
}'''

new_loop = '''function checkCivilAlertLoop() {
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

html = html.replace(old_loop, new_loop)

# No teste de alerta do Dashboard, também testar com a pessoa do aparelho
old_test = '''    triggerCivilDefenseAlert([
      { name: "Passear com a Pretinha (Teste de Alerta)", who: ["Thiago"], quando: "Manhã" }
    ]);'''

new_test = '''    const myP = store.person || person || "Thiago";
    triggerCivilDefenseAlert([
      { name: "Passear com a Pretinha (Teste de Alerta)", who: [myP], quando: "Manhã" }
    ]);'''

html = html.replace(old_test, new_test)

with open(r'C:\Users\thiag\homework\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated checkCivilAlertLoop to alert strictly individual tasks!")
