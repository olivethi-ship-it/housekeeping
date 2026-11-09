Em execução por: ninguém

# Retomada do Projeto — housekeeping

## Estado atual (2026-11-06)
- **Versão:** v1.4.0 em produção: https://casa-tarefas-ab1f5.web.app
- **Pasta oficial:** `C:\Users\thiag\housekeeping`. A pasta `homework` é antiga e não deve receber trabalho.
- **Repositório:** https://github.com/olivethi-ship-it/housekeeping (público), branch `main`.
- **Código:** `public/index.html` é o app inteiro. `tests/smoke.mjs` roda no predeploy e bloqueia o deploy se falhar.

## O que mudou nesta sessão
- Produção estava quebrada: marcadores de conflito impediam o script principal de compilar.
- Marcações vindas da nuvem agora são decodificadas e aparecem na tela.
- Removidos `public/app.js` (quebrado e sem uso) e o refresh de 5 min, que impedia o alerta de 10 min.
- Alerta checa 5 s após abrir o app; HTML publicado com `Cache-Control: no-cache`.
- Admin (v1.3.0): corrigido o salvamento de `custom_config`, que falhava por chaves com `/` em `tempo`. Isso afetava editar, criar e excluir tarefas e moradores.
- Admin (v1.3.0): nova seção "Associar Tarefas às Pessoas", por dia e por semana do ciclo. O modal passou a se chamar Painel Admin.
- O primeiro salvamento real grava `custom_config` e passa a valer para todos os aparelhos. Conferir no uso real.
- v1.4.0: alertas push com o app fechado (ADR 001). Arquivos: `public/sw.js`, `public/manifest.json`, `scripts/late.mjs`, `scripts/notify.mjs` e `.github/workflows/alertas.yml`. A chave privada está no segredo `VAPID_PRIVATE_KEY` do repositório; a pública fica em `index.html`. Passo a passo de ativação no README.
- v1.4.0: o aparelho sem dono não sobrescreve mais o dono atribuído pelo Admin. Trocar o dono agora grava na nuvem.
- Não testado em aparelho real: o painel do Claude não roda service worker. Validar com Actions → Run workflow → "teste".

- v1.4.1 (2026-11-09): silêncio noturno fixo das 22h às 7h, no push (`isQuietHour` em `scripts/late.mjs`) e no alerta do app aberto.

## Problema aberto (2026-11-09): push não chega
- Só 1 aparelho tem inscrição push (`dev_zf0m`, Thiago, Android). Renata (`dev_2ak5`) e os demais nunca tocaram em "Ativar alertas".
- O cron do GitHub é "melhor esforço": rodou a cada 3 a 7 horas, não a cada 10 min. Precisa de um disparador externo (ex.: cron-job.org chamando `workflow_dispatch`), a decidir com o Thiago.

## Pendências (dívida técnica)
1. **Segurança, prioridade alta:** o Realtime Database aceita leitura sem login e o app não tem autenticação; logo, a escrita também é aberta. `admin_pin` fica nesse banco, então o PIN é só uma barreira de tela. Resolver exige Firebase Auth (ex.: anônimo) e regras versionadas.
2. Repositório público contém o PIN padrão no código e no README. Trocar o PIN pelo Admin e avaliar tornar o repositório privado.
3. Branch remota `master` tem histórico sem relação com a `main`. Decidir se apaga.
4. Scripts `patch_*.py`, `update_ui.py` e `fix_firebase_auto.py` são descartáveis de sessões antigas. Decidir se remove.
5. `homework` tem alteração não commitada em `public/index.html`. Conferir antes de arquivar a pasta.
6. Ao renomear tarefa no Admin, marcações antigas dela deixam de aparecer, porque a chave usa o nome.
7. Melhorar a consulta de histórico, se fizer falta.
8. Workflow agendado é pausado pelo GitHub após 60 dias sem commit. Reativar em Actions, se parar.
9. As regras de atraso estão duplicadas em `index.html` e `scripts/late.mjs` (ver ADR 001).
