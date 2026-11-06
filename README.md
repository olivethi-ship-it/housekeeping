---
name: tarefas-casa
description: Aplicativo PWA de gestão de tarefas domésticas da família do Thiago com sincronização Firebase em tempo real
type: project
---

# Tarefas da Casa

Aplicativo mobile-first / PWA para gestão das tarefas domésticas da família.

- **URL de Produção (Hosting):** https://casa-tarefas-ab1f5.web.app
- **Firebase Console:** https://console.firebase.google.com/project/casa-tarefas-ab1f5/overview
- **Realtime Database:** `https://casa-tarefas-ab1f5-default-rtdb.firebaseio.com/`

## Funcionalidades Principais
1. **Sincronização em Tempo Real (Firebase RTDB):**
   - Qualquer aparelho (iPhone no Safari ou Android no Chrome) sincroniza instantaneamente ao marcar uma tarefa.
2. **Alertas da Defesa Civil Doméstica:**
   - Pop-up com efeito de alarme, som estridente (Web Audio API) e vibração a cada 10 min para tarefas atrasadas.
3. **Dashboard Semanal com %:**
   - Cumprimento geral da casa e individual por morador (Renata, Thiago, Giovana, Felipe).
4. **Tempos Sugeridos e Totalizadores:**
   - Cada tarefa possui minutos estimados (ex: ⏱ 15min, ⏱ 45min).
   - Cabeçalhos de dia e placar mostram total de horas/minutos feitas vs planejadas.
5. **Acesso dos Pais / Modo Silêncio e Férias:**
   - Protegido por PIN de 4 dígitos (padrão inicial: `1234`).
   - Os filhos não têm acesso e não conseguem silenciar os alertas.
   - Pais podem pausar alertas por 2h, 4h, fim do dia ou semanas (férias/viagens).
6. **Painel Admin:**
   - Dashboard → 🔒 Admin → PIN.
   - Associar responsáveis por tarefa, dia e semana do ciclo.
   - Editar, criar e excluir tarefas e moradores, e atribuir celulares.
