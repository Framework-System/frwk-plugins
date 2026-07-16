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
/plugin install oskiller@frwk-plugins
/plugin install neverstop@frwk-plugins
/plugin install estimativa-killer@frwk-plugins
```

## Plugins disponíveis

| Plugin | O que faz | Acesso | Repositório |
|---|---|---|---|
| **equipping-stack-docs** | Gera skills de documentação locais ao projeto com docs na versão que o projeto usa (inclusive legados), via Context7 | Público | [Framework-System/equipping-stack-docs](https://github.com/Framework-System/equipping-stack-docs) |
| **legacy-docs** | Documentação profunda e verificada de sistemas legados: pipeline de 5 fases com triage de hot-spots e verificação adversarial (`/legacy-docs:document`) | Restrito | [Framework-System/legacy-documentation-kit](https://github.com/Framework-System/legacy-documentation-kit) |
| **oskiller** | Migração guiada de apps OutSystems para a stack de destino, em fases: análise → blueprint/plano → geração de código → verificação | Restrito | [felipehorta/OSKiller](https://github.com/felipehorta/OSKiller) |
| **neverstop** | Faz sessões longas de codegen (oskiller:execute) sobreviverem ao estouro da janela de contexto, com handoff salvo e recarga automática após /clear | Restrito | [felipehorta/NeverStop](https://github.com/felipehorta/NeverStop) |
| **estimativa-killer** | Estima o esforço agente + humano de uma migração OutSystems até produção; roda após /oskiller:plan e gera cronograma por onda | Restrito | [felipehorta/EstimativaKiller](https://github.com/felipehorta/EstimativaKiller) |

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
