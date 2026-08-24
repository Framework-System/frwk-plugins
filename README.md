# frwk-plugins

Marketplace central de plugins Claude Code da **Framework System**. Registre uma vez e instale qualquer plugin da empresa a partir dele.

## Uso

```
/plugin marketplace add Framework-System/frwk-plugins
```

Depois instale o que precisar:

```
/plugin install equipping-stack-docs@frwk-plugins
/plugin install legacy-docs@frwk-plugins
/plugin install qa-handoff@frwk-plugins
/plugin install oskiller@frwk-plugins
/plugin install neverstop@frwk-plugins
/plugin install estimativa-killer@frwk-plugins
/plugin install discovery-sync@frwk-plugins
/plugin install screendiscovery@frwk-plugins
/plugin install flow-genesis-studio@frwk-plugins
/plugin install drive-transcriber-mcp@frwk-plugins
/plugin install qa-intake@frwk-plugins
/plugin install selfrepair@frwk-plugins
```

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

## Adicionando um plugin novo

1. Crie o repositório do plugin na org com `.claude-plugin/plugin.json` e `skills/` (use o [equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) como modelo de estrutura mínima).
2. Adicione uma entrada no array `plugins` do [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) deste repo:

```json
{
  "name": "nome-do-plugin",
  "description": "uma linha sobre o que faz",
  "source": { "source": "github", "repo": "Framework-System/nome-do-plugin" },
  "author": { "name": "Seu Nome", "email": "voce@frwk.com.br" }
}
```

3. Commit e push — quem já registrou o marketplace passa a ver o plugin novo.
