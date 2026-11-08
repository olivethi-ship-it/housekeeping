# ADR 001 — Alertas de atraso por Web Push com agendador no GitHub Actions

Data: 2026-11-07 · Status: aceita

## Contexto
O alerta antigo só funcionava com o app aberto e na tela, porque dependia de um `setInterval` na página. A família usa Android, iPhone e Windows. O requisito é que o responsável seja incomodado enquanto a tarefa estiver atrasada, inclusive com o app fechado.

## Decisão
- O app vira PWA, com `manifest.json` e `sw.js`. Cada aparelho assina Web Push com chave VAPID e grava a assinatura em `tarefas_casa/devices/{id}/push`.
- O workflow `.github/workflows/alertas.yml` roda a cada 10 minutos. O script `scripts/notify.mjs` lê o banco e calcula os atrasos com `scripts/late.mjs`, que usa as mesmas regras do app. Depois envia o push a cada aparelho cujo dono tem tarefa atrasada.
- A notificação repete a cada execução até a tarefa ser marcada, e respeita o Modo Silêncio do Admin.

## Alternativas consideradas
- **App nativo Android com alarme:** fura o modo silencioso, mas não atende iPhone nem Windows e exige instalar APK.
- **Firebase Cloud Functions:** exige o plano Blaze, com cartão.
- **VPS própria:** é pontual, mas é mais um serviço para manter.

## Consequências
- Custo zero. O GitHub pode atrasar execuções agendadas alguns minutos.
- O GitHub desativa workflows agendados em repositório público após 60 dias sem commit. Reativar em Actions, se acontecer.
- Push segue o perfil de som do aparelho. No modo silencioso total, chega só visualmente.
- No iPhone, só funciona com o app adicionado à Tela de Início (iOS 16.4 ou mais novo).
- As regras de atraso existem em dois lugares: `public/index.html` e `scripts/late.mjs`. Mudou uma, mude a outra; os testes cobrem `late.mjs`.
