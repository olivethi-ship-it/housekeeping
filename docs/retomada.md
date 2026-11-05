---
name: Atualização de Tarefas Casa
description: Registro das correções finais, deploy e próximos passos
type: project
---

## Última atualização (2026-11-05)
- Correção da funcionalidade de marcação de tarefas (campo `concluida` agora persiste no Realtime Database e a UI atualiza corretamente).
- A lógica de destaque `is‑late` foi ajustada para permanecer apenas visualmente quando a tarefa ainda não está concluída, mas continua contabilizada como atrasada para ranking e relatórios.
- Deploy concluído com sucesso para o Firebase Hosting.
- URL ativa: https://casa-tarefas-ab1f5.web.app

### Próximos passos
- Monitorar feedback de usuários sobre a nova marcação.
- Eventual aprimoramento da página de histórico (`associate.html`).
- Atualizar documentação de desenvolvedor se houver novas funcionalidades.
