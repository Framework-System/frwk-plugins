# frwk-plugins

Marketplace central de plugins da **Framework System**. Registre uma vez e instale qualquer plugin
da empresa a partir dele — em **Claude Code, GitHub Copilot CLI e Factory Droid**, que leem o mesmo
catálogo. As skills seguem o formato aberto [Agent Skills](https://agentskills.io) e funcionam
também em Codex, Cursor, Gemini CLI, Kimi, pi e outros ~45 agentes.

## Sumário

- [Como funciona](#como-funciona)
- [Instalação](#instalacao)
- [Onde isto foi testado de verdade](#onde-isto-foi-testado-de-verdade)
- [Plugins disponíveis](#plugins-disponiveis)
- [Compatibilidade por agente](#compatibilidade-por-agente)
- [Atualizando](#atualizando)
- [Adicionando um plugin novo](#adicionando-um-plugin-novo)
- [Acesso](#acesso)

## Como funciona

Um plugin da Framework System é uma pasta com três camadas, e nem todo agente consome as três:

- **A skill** (`skills/<nome>/SKILL.md`) — o procedimento em si, no formato aberto Agent Skills.
  Portátil: roda em qualquer agente que leia `SKILL.md`.
- **Os comandos de barra** (`commands/`) — pontos de entrada nomeados por etapa
  (`/discovery-sync:start`, `/selfrepair:scan`). **Específicos do Claude Code.**
- **Os subagentes e hooks** (`agents/`, `hooks/`) — paralelismo e ciclo de vida da sessão.
  **Específicos do Claude Code.**

Fora do Claude Code você não perde o plugin: perde os atalhos. Em vez de `/discovery-sync:start`,
você descreve o que quer e o agente carrega a skill pela descrição dela.

## Instalação

A instalação muda conforme o agente. Se você usa mais de um, instale em cada um separadamente.

> **Repositórios privados.** Todos os repos são privados. Qualquer comando abaixo exige que você já
> esteja autenticado no GitHub (`gh auth login`, credential helper ou chave SSH no `ssh-agent`).
> Sem isso o download falha com erro de autenticação.

### Claude Code

Entrega completa: skills, comandos, subagentes e hooks.

- Registre o marketplace:

  ```bash
  /plugin marketplace add Framework-System/frwk-plugins
  ```

- Instale o que precisar:

  ```bash
  /plugin install equipping-stack-docs@frwk-plugins
  /plugin install legacy-docs@frwk-plugins
  /plugin install qa-handoff@frwk-plugins
  /plugin install oskiller@frwk-plugins
  /plugin install neverstop@frwk-plugins
  /plugin install estimativa-killer@frwk-plugins
  /plugin install discovery-sync@frwk-plugins
  /plugin install flow-genesis-studio@frwk-plugins
  /plugin install screendiscovery@frwk-plugins
  /plugin install drive-transcriber-mcp@frwk-plugins
  /plugin install qa-intake@frwk-plugins
  /plugin install selfrepair@frwk-plugins
  ```

### GitHub Copilot CLI

O Copilot CLI lê o mesmo `marketplace.json` deste repositório. **Testado com o Copilot CLI 1.0.80**:
o marketplace é aceito, os 12 plugins aparecem no `browse`, e a instalação resolve o `source` no
formato `github/repo` sem ajuste nenhum.

- Registre o marketplace:

  ```bash
  copilot plugin marketplace add Framework-System/frwk-plugins
  ```

- Instale um plugin:

  ```bash
  copilot plugin install discovery-sync@frwk-plugins
  ```

### Factory Droid

- Registre o marketplace:

  ```bash
  droid plugin marketplace add https://github.com/Framework-System/frwk-plugins
  ```

- Instale um plugin:

  ```bash
  droid plugin install discovery-sync@frwk-plugins
  ```

### Codex

O Codex também lê um marketplace, mas num arquivo próprio: `.agents/plugins/marketplace.json`
(não o `.claude-plugin/`). Este repositório traz os dois. **Testado com o Codex CLI 0.149.1.**

- Registre o marketplace:

  ```bash
  codex plugin marketplace add https://github.com/Framework-System/frwk-plugins
  ```

- Veja o catálogo e instale:

  ```bash
  codex plugin list
  codex plugin add discovery-sync@frwk-plugins
  ```

- Atualize o catálogo depois:

  ```bash
  codex plugin marketplace upgrade
  ```

### Gemini CLI

Instala **por plugin**, não pelo marketplace. **Testado com o Gemini CLI 0.56.0** — funciona com
repositório privado, usando suas credenciais git.

```bash
gemini extensions install https://github.com/Framework-System/discovery-sync --consent
```

Sem `--consent` o comando trava esperando confirmação interativa.

A extensão injeta o `GEMINI.md`, que inclui a skill inteira no contexto da sessão — é assim que ela
chega ao Gemini.

> **Ruído conhecido.** Nos plugins que têm `agents/`, o Gemini tenta carregá-los como agentes dele e
> falha com `Invalid tool name`, a cada comando. É cosmético: a extensão instala, habilita e a skill
> funciona. A causa é vocabulário de ferramenta — o Gemini usa `read_file`/`glob`, o Claude Code usa
> `Read`/`Glob`, e o campo `tools` do agente só comporta um vocabulário. Testamos converter o formato
> para array YAML (que o Claude Code aceita); resolve a validação estrutural, mas os nomes seguem
> inválidos. Não há correção sem manter dois conjuntos de agentes.

### Cursor, Kimi, Antigravity, OpenCode, pi

Instalam **por plugin**. Cada repositório traz o manifesto do respectivo harness e a seção
**Instalação** com o comando exato.

### GitHub Copilot no editor (VS Code, JetBrains, cloud agent, code review)

O Copilot descobre skills por diretório. Copie a skill para o repositório onde vai trabalhar:

```bash
mkdir -p .agents/skills
cp -R /caminho/para/discovery-sync/skills/discovery-sync .agents/skills/
```

### Qualquer outro agente com suporte a Agent Skills

Copie `skills/<nome>/` do repositório do plugin para o diretório de skills do seu agente — os
caminhos mais comuns são `.agents/skills/` (no repositório) e `~/.agents/skills/` (pessoal).

## Onde isto foi testado de verdade

Nem tudo abaixo é leitura de documentação. Estes três foram instalados e exercitados nesta máquina:

| Agente | Versão testada | Resultado |
|---|---|---|
| **GitHub Copilot CLI** | 1.0.80 | marketplace aceito, 12 plugins no `browse`, 9 instalados. Importa `commands/` como skills (ver aviso de colisão abaixo) |
| **Codex CLI** | 0.149.1 | exigiu `.agents/plugins/marketplace.json`, que foi adicionado. 9 plugins instalados e habilitados |
| **Gemini CLI** | 0.56.0 | instala de repositório privado; a skill chega via `GEMINI.md`. `agents/` gera ruído de validação |

As 10 skills também passam no validador de referência da especificação
([`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref)): **10 válidas, 0 com erro**.

Cursor, Kimi, Antigravity, OpenCode e pi **não foram testados** — os manifestos seguem o formato
documentado de cada um, mas ninguém instalou ainda.

## Plugins disponíveis

| Plugin | O que faz | Acesso | Repositório |
|---|---|---|---|
| **equipping-stack-docs** | Gera skills de documentação locais ao projeto com docs na versão que o projeto usa (inclusive legados), via Context7 | Público | [Framework-System/equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) |
| **legacy-docs** | Documentação profunda e verificada de sistemas legados: pipeline de 5 fases com triage de hot-spots e verificação adversarial (`/legacy-docs:document`) | Restrito | [Framework-System/legacy-documentation-kit](https://github.com/Framework-System/legacy-documentation-kit) |
| **qa-handoff** | Mantém artefatos de QA ao fim de cada demanda em `docs/qaHandoff/`: cenários grounded no código, massa de dados, regressão e matriz de cobertura, com validação em browser real e evidência gravada; cobre front e back, incluindo integração, performance (k6) e confronto com requisitos (`/qa-handoff:scenarios-back-front`) | Restrito | [Framework-System/qa-handoff](https://github.com/Framework-System/qa-handoff) |
| **oskiller** | Migração guiada de uma stack de origem para a arquitetura/stack de destino definida por você, em oito fases com gates: intake → oráculo do legado observado → documentação As-Is (regras RN-* rastreáveis) → gate de decisões DEC-* → assessment de portabilidade → plano em ondas → geração de código → verificação contra dois oráculos externos (`/oskiller:start`) | Restrito | [Framework-System/OSKiller](https://github.com/Framework-System/OSKiller) |
| **neverstop** | Faz sessões longas de codegen (oskiller:execute) sobreviverem ao estouro da janela de contexto, com handoff salvo e recarga automática após /clear | Restrito | [Framework-System/NeverStop](https://github.com/Framework-System/NeverStop) |
| **estimativa-killer** | Estima o esforço agente + humano de uma migração OutSystems até produção; roda após /oskiller:plan e gera cronograma por onda | Restrito | [Framework-System/EstimativaKiller](https://github.com/Framework-System/EstimativaKiller) |
| **discovery-sync** | Do artefato bruto do cliente — pasta local, Google Drive ou board Azure DevOps/Jira já em uso — ao backlog pronto para dev: inventário, quiz adaptativo, Discovery Document com gate de aprovação, Epic/Feature/User Story rastreável e CSV de import gerado para o processo certo do Azure DevOps (Basic/Agile/Scrum/CMMI) (`/discovery-sync:start`) | Restrito | [Framework-System/discovery-sync](https://github.com/Framework-System/discovery-sync) |
| **screendiscovery** | Mapeia exaustivamente uma aplicação web aberta no Chrome — cada tela, aba, menu, modal e estado — entregando screenshots numerados e um `mapeamento_aplicacao.md` que referencia cada imagem (`/screendiscovery:mapear`) | Restrito | [Framework-System/ScreenDiscovery](https://github.com/Framework-System/ScreenDiscovery) |
| **flow-genesis-studio** | Gera protótipos de tela navegáveis e rastreáveis a partir do Discovery Document/backlog do discovery-sync, de texto livre, ou de um protótipo que já existe (Figma via MCP, prints, HTML) — herdando dele paleta e tipografia: blueprint com gate de aprovação, telas HTML clicáveis com craft via interface-design, auditoria em paralelo (uma célula por tela, com comparação visual contra o original) mais passada de escopo cruzado, entrega em ondas acima de 25 telas, e export pro Figma pelo MCP ou via code.to.design (`/flow-genesis-studio:start`) | Restrito | [Framework-System/flow-genesis-studio](https://github.com/Framework-System/flow-genesis-studio) |
| **drive-transcriber-mcp** | Servidor MCP: lê áudios/vídeos de uma pasta do Google Drive, transcreve localmente com faster-whisper (offline, sem custo de API) e sincroniza `.txt`/`.srt` de volta para o Drive | Restrito | [Framework-System/DriveTranscriberMCP](https://github.com/Framework-System/DriveTranscriberMCP) |
| **qa-intake** | Transforma gravações narradas de fluxo (vídeo + transcrição) em casos de teste estruturados, com portão determinístico que impede o modelo de fabricar passos: todo passo cita um timestamp da transcrição e a citação é conferida contra o texto bruto (`/qa-intake:start`) | Restrito | [Framework-System/qa-intake](https://github.com/Framework-System/qa-intake) |
| **selfrepair** | Auto-reparador de bugs de produção: descobre bugs na telemetria que o projeto já usa (Sentry, Datadog, Grafana/Loki, Application Insights via MCP; arquivo de log, saída de container e painel web como fallback), agrupa cross-fonte e ranqueia com decomposição explícita do score, investiga cada bug em paralelo, **conversa com você na busca e na correção**, corrige com teste de regressão vermelho antes do fix e verificação adversarial, e registra em branch dedicada com commits atômicos e PR sob confirmação por degrau (`/selfrepair:start`) | Restrito | [Framework-System/selfrepair](https://github.com/Framework-System/selfrepair) |

**Público** = qualquer pessoa instala. **Restrito** = o repositório do plugin é privado; a instalação exige acesso ao repositório e git autenticado no GitHub (`gh auth login` ou chave SSH). Sem acesso, o clone falha na instalação — o restante da loja continua funcionando normalmente.

> **Dica (clone SSH sem chave):** se a instalação de um plugin restrito falhar com `Permission denied (publickey)`, redirecione o git para HTTPS autenticado:
> ```
> git config --global url."https://github.com/".insteadOf "git@github.com:"
> ```

## Compatibilidade por agente

| Plugin | Versão | Claude Code | Demais agentes | Comandos | Subagentes | Hooks |
|---|---|---|---|---|---|---|
| **equipping-stack-docs** | `1.0.0` | sim | sim | — | — | — |
| **legacy-docs** | `4.2.0` | sim | — | 1 | — | — |
| **qa-handoff** | `1.32.0` | sim | sim | 7 | — | — |
| **oskiller** | `0.4.0` | sim | sim | 9 | 9 | — |
| **neverstop** | `0.2.0` | sim | — | 2 | — | sim |
| **estimativa-killer** | `0.2.0` | sim | sim | 1 | — | — |
| **discovery-sync** | `0.15.0` | sim | sim | 10 | 5 | — |
| **flow-genesis-studio** | `1.1.0` | sim | sim | 7 | 8 | — |
| **screendiscovery** | `0.3.0` | sim | sim | 3 | — | — |
| **drive-transcriber-mcp** | `0.1.1` | sim | — | — | — | — |
| **qa-intake** | `0.3.0` | sim | sim | 5 | 1 | — |
| **selfrepair** | `0.2.0` | sim | sim | 6 | 3 | — |

**Demais agentes = sim** significa que o repositório traz os manifestos de Codex, Cursor, Kimi,
Gemini e pi, todos apontando para a mesma skill — sem cópia duplicada.

### O que o Copilot CLI faz a mais — e o cuidado que isso exige

O Copilot CLI não carrega só a skill: ele também importa os arquivos de `commands/` **como skills
soltas, sem o prefixo do plugin**. Um `/discovery-sync:quiz` vira uma skill chamada `quiz`.

Isso é bom (mais do plugin chega ao Copilot) e é um problema quando você instala vários plugins
nossos, porque **os nomes colidem em silêncio**:

| Nome disputado | Plugins que o usam |
|---|---|
| `status` | discovery-sync, selfrepair, flow-genesis-studio, screendiscovery, oskiller, qa-intake |
| `start` | discovery-sync, selfrepair, flow-genesis-studio, oskiller, qa-intake |
| `ingest` | discovery-sync, qa-intake |
| `review` | discovery-sync, flow-genesis-studio |
| `verify` | flow-genesis-studio, oskiller |

Medido com os 9 plugins instalados: **58 componentes viram 46 nomes únicos — 12 ficam
inacessíveis**, sem aviso. Quem pedir "status" recebe o do discovery-sync, qualquer que fosse a
intenção.

No Claude Code isso não acontece: lá cada comando é prefixado pelo plugin (`/oskiller:status` e
`/qa-intake:status` coexistem). **Se for usar o Copilot CLI, instale só os plugins que você
realmente precisa.**

Os três com **—**:

- **legacy-docs** — não tem `SKILL.md`; toda a lógica está num comando do Claude Code.
- **drive-transcriber-mcp** — é um servidor MCP, não uma skill. MCP é padrão aberto: **já funciona**
  em Codex, Copilot, Cursor e Gemini, bastando registrar o servidor.
- **neverstop** — o valor dele está inteiro nos hooks `PreCompact`/`SessionStart`/`Stop` do Claude
  Code, que não têm equivalente em outros agentes. Portar entregaria uma casca.

## Atualizando

```bash
/plugin marketplace update frwk-plugins
/plugin update
```

> **Rode o primeiro comando manualmente.** O auto-update em background desabilita os credential
> helpers do git, então **não autentica em repositório privado por HTTPS** — que é o caso de todos
> estes. Sem o `marketplace update` manual você continua vendo o catálogo antigo. Alternativa:
> registre o marketplace por SSH, com a chave carregada no `ssh-agent`.

O cache de plugin é indexado pela string de `version`. Todo release muda a versão nos manifests;
sem isso a atualização não chega em quem já instalou.

## Adicionando um plugin novo

1. Crie o repositório na org com `.claude-plugin/plugin.json` e `skills/<nome>/SKILL.md`. Use o
   [equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) como modelo —
   ele traz os manifestos de todos os harnesses.
2. Garanta que a skill passa na [especificação Agent Skills](https://agentskills.io/specification):
   `name` em minúsculas com hífens, igual ao nome da pasta, e `description` com **no máximo 1024
   caracteres**.
3. Adicione a entrada no array `plugins` do
   [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json):

   ```json
   {
     "name": "nome-do-plugin",
     "description": "uma linha sobre o que faz e quando usar",
     "source": { "source": "github", "repo": "Framework-System/nome-do-plugin" },
     "author": { "name": "Seu Nome", "email": "voce@frwk.com.br" }
   }
   ```

4. Dê acesso ao time `ia-frwk-champions` (push) e `symbio-ai` (pull) no repositório novo — a org usa
   `base permission = none`, então sem time atribuído ninguém consegue instalar.
5. Commit e push. Quem já registrou o marketplace passa a ver o plugin novo depois de um
   `/plugin marketplace update frwk-plugins`.

## Acesso

Todos os repositórios são privados. O acesso vem por time, não por pertencer à org:

| Time | Permissão |
|---|---|
| `ia-frwk-champions` | push |
| `symbio-ai` | pull |
| `frwk-acesso-base` | pull |
