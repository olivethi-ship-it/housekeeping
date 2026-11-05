# homework — Regras para Agentes e LLMs

Leia este arquivo antes de iniciar qualquer trabalho. Ele é conciso e define o fluxo para qualquer LLM (Antigravity, Claude Code, etc.) trabalhar sem estourar limites de contexto ou tokens.

## 1. O que é o Projeto
Aplicativo web mobile-first / PWA para gestão de tarefas domésticas da família:
- **Produção (Hosting):** https://casa-tarefas-ab1f5.web.app
- **Firebase Database:** `https://casa-tarefas-ab1f5-default-rtdb.firebaseio.com/`
- **Código Principal:** `public/index.html` (aplicativo autocontido com CSS, HTML e JS).

## 2. Trava de Execução
Antes de começar, verifique a primeira linha de `docs/retomada.md` (`Em execução por:`).
- Se estiver com o nome de outro agente/sessão, não altere nada e avise o usuário.
- Se estiver `ninguém`, altere para seu identificador e data antes de iniciar.
- Ao terminar ou pausar, volte para `ninguém`.

## 3. Seleção de Modelos & Controle de Custos (REGRA OBRIGATÓRIA)
- **Modelos Rápidos / Baratos (Padrão):**
  - Use modelos eficientes e de menor custo (ex: `flash`, `flash_lite`, GPT mini/oss) para tarefas rotineiras, correções pontuais de CSS/JS, consultas e atualizações de documentação.
- **Modelos Caros / Pesados (Opus, Pro):**
  - **PROIBIDO** acionar subagentes ou mudar para modelos caros sem pedir autorização explícita do Thiago antes.
  - Para demandas simples a intermediárias, resolva com o modelo padrão de menor custo.

## 4. Economia de Tokens (O que ler e o que NÃO ler)
- **Leia SOMENTE:**
  1. `AGENTS.md` (este arquivo)
  2. `docs/retomada.md` (estado atual e próxima ação)
  3. A seção específica do `public/index.html` que for modificar (via range de linhas).
- **NÃO leia:**
  - Pastas de scratch ou arquivos gerados em sessões anteriores.
  - O arquivo `index.html` inteiro repetidas vezes a cada turno.

## 5. Deploy e Publicação
- Para publicar alterações no ar:
  ```powershell
  cd C:\Users\thiag\homework
  npx firebase-tools deploy --only hosting
  ```
