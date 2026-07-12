# frwk-plugins

Marketplace central de plugins Claude Code da **Framework System**. Registre uma vez e instale qualquer plugin da empresa a partir dele.

## Uso

```
/plugin marketplace add Framework-System/frwk-plugins
```

Depois instale o que precisar:

```
/plugin install equipping-stack-docs@frwk-plugins
```

## Plugins disponíveis

| Plugin | O que faz | Repositório |
|---|---|---|
| **equipping-stack-docs** | Gera skills de documentação locais ao projeto com docs na versão que o projeto usa (inclusive legados), via Context7 | [Framework-System/equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) |

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
