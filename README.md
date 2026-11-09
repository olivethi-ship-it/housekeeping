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
6. **Alertas com o app fechado (push):**
   - O GitHub Actions (`.github/workflows/alertas.yml`) roda a cada 10 min e avisa quem tem tarefa atrasada, até marcar como feita.
   - Para testar: GitHub → Actions → "Alertas de atraso" → Run workflow → marcar "teste".
   - Ativação, uma vez em cada aparelho (Dashboard → "🔔 Ativar alertas neste aparelho"):
     - **Android:** abrir no Chrome → ⋮ → "Instalar app" (opcional) → ativar alertas → Permitir.
     - **iPhone (iOS 16.4+):** abrir no Safari → Compartilhar → "Adicionar à Tela de Início" → abrir pelo ícone → ativar alertas → Permitir.
     - **Windows:** abrir no Chrome ou Edge → ativar alertas → Permitir. O navegador precisa poder rodar em segundo plano.
   - Som e vibração seguem o perfil do aparelho; no silencioso total, o aviso chega só na tela.
   - Silêncio noturno fixo: nenhum alerta das 22h às 7h.
7. **Painel Admin:**
   - Dashboard → 🔒 Admin → PIN.
   - Associar responsáveis por tarefa, dia e semana do ciclo.
   - Editar, criar e excluir tarefas e moradores, e atribuir celulares.
