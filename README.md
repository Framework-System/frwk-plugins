# frwk-plugins

Marketplace central de plugins Claude Code da **Framework System**. Registre uma vez e instale qualquer plugin da empresa a partir dele.

## Uso

```
/plugin marketplace add Framework-System/frwk-plugins
```

Depois instale o que precisar:

```
/plugin install equipping-stack-docs@frwk-plugins
/plugin install oskiller@frwk-plugins
/plugin install neverstop@frwk-plugins
/plugin install estimativa-killer@frwk-plugins
```

> **Repos privados + clone SSH:** se a instalação falhar com `Permission denied (publickey)`, seu git está tentando SSH sem chave configurada. Ou configure uma chave SSH no GitHub, ou redirecione para HTTPS autenticado (via `gh auth login`) com:
> ```
> git config --global url."https://github.com/".insteadOf "git@github.com:"
> ```

## Plugins disponíveis

| Plugin | O que faz | Repositório |
|---|---|---|
| **equipping-stack-docs** | Gera skills de documentação locais ao projeto com docs na versão que o projeto usa (inclusive legados), via Context7 | [Framework-System/equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) |
| **oskiller** | Migração guiada de apps OutSystems para a stack de destino, em fases: análise → blueprint/plano → geração de código → verificação | [felipehorta/OSKiller](https://github.com/felipehorta/OSKiller) |
| **neverstop** | Faz sessões longas de codegen (oskiller:execute) sobreviverem ao estouro da janela de contexto, com handoff salvo e recarga automática após /clear | [felipehorta/NeverStop](https://github.com/felipehorta/NeverStop) |
| **estimativa-killer** | Estima o esforço agente + humano de uma migração OutSystems até produção; roda após /oskiller:plan e gera cronograma por onda | [felipehorta/EstimativaKiller](https://github.com/felipehorta/EstimativaKiller) |

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
