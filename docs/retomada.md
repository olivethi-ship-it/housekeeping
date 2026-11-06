Em execução por: ninguém

# Retomada do Projeto — housekeeping

## Estado atual (2026-11-06)
- **Versão:** v1.2.1 em produção: https://casa-tarefas-ab1f5.web.app
- **Pasta oficial:** `C:\Users\thiag\housekeeping`. A pasta `homework` é antiga e não deve receber trabalho.
- **Repositório:** https://github.com/olivethi-ship-it/housekeeping (público), branch `main`.
- **Código:** `public/index.html` é o app inteiro. `tests/smoke.mjs` roda no predeploy e bloqueia o deploy se falhar.

## O que mudou nesta sessão
- Produção estava quebrada: marcadores de conflito impediam o script principal de compilar.
- Marcações vindas da nuvem agora são decodificadas e aparecem na tela.
- Removidos `public/app.js` (quebrado e sem uso) e o refresh de 5 min, que impedia o alerta de 10 min.
- Alerta checa 5 s após abrir o app; HTML publicado com `Cache-Control: no-cache`.

## Pendências (dívida técnica)
1. **Segurança, prioridade alta:** o Realtime Database aceita leitura sem login e o app não tem autenticação; logo, a escrita também é aberta. `admin_pin` fica nesse banco, então o PIN é só uma barreira de tela. Resolver exige Firebase Auth (ex.: anônimo) e regras versionadas.
2. Repositório público contém o PIN padrão no código e no README. Trocar o PIN pelo Admin e avaliar tornar o repositório privado.
3. Branch remota `master` tem histórico sem relação com a `main`. Decidir se apaga.
4. Scripts `patch_*.py`, `update_ui.py` e `fix_firebase_auto.py` são descartáveis de sessões antigas. Decidir se remove.
5. `homework` tem alteração não commitada em `public/index.html`. Conferir antes de arquivar a pasta.
6. Ao renomear tarefa no Admin, marcações antigas dela deixam de aparecer, porque a chave usa o nome.
7. Melhorar a consulta de histórico, se fizer falta. Não existe `associate.html` no projeto.
