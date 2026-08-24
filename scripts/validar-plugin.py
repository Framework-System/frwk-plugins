#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida um repositorio de plugin da Framework System contra as regras da loja.

As regras existem porque cada uma corresponde a um defeito que ja chegou em producao:

1. VERSAO SOBE QUANDO O CONTEUDO MUDA
   O cache de plugin do Claude Code e indexado pela string de `version`. Publicar commits sem
   subir a versao nao propaga nada: quem ja instalou fica com a copia antiga para sempre. Cinco
   plugins ficaram meses assim.

2. VERSAO CONSISTENTE ENTRE OS MANIFESTOS
   Um repo multi-harness tem a versao em ate 7 arquivos. A doc do Claude Code avisa que o valor do
   `plugin.json` sempre vence, entao um manifesto desatualizado mascara a versao sem avisar.

3. SKILL VALIDA NA SPEC AGENT SKILLS
   `description` tem limite de 1024 caracteres e `name` precisa casar com o diretorio. Uma skill
   com 1150 caracteres foi publicada e seria recusada por validador estrito.

4. DESCRIPTION ATIVA POR LINGUAGEM NATURAL
   Uma description que so diz "use quando o usuario rodar /plugin:comando" nunca dispara fora do
   Claude Code, onde comando de barra nao existe: a skill fica instalada e inerte.

5. JSON VALIDO EM TODO MANIFESTO
   Manifesto quebrado derruba o carregamento do plugin inteiro, as vezes da loja inteira.

6. COMANDO CITADO NO README EXISTE
   O README da loja apontava para `/qa-handoff:update`, comando que nunca existiu.

7. DESCRIPTION SINCRONIZADA COM A LOJA (so com --loja)
   A entrada do plugin nos catalogos da loja repete verbatim a description do plugin.json.
   Quatro entradas da loja ficaram meses descrevendo versoes antigas — quem instala pelo
   marketplace decidia com base em texto defasado. Ao mudar a description aqui, atualize a
   entrada correspondente em frwk-plugins ANTES de mergear este PR.

Uso:
    python scripts/validar-plugin.py [--repo CAMINHO] [--base REF] [--loja CAMINHO]

`--base` liga a regra 1: compara com essa ref do git (ex.: `origin/main`) e cobra o bump se o
conteudo do plugin mudou. Sem ela, a regra 1 e pulada.

Sai com codigo 1 se qualquer regra falhar.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LIMITE_DESCRIPTION = 1024
DIRS_CONTEUDO = ["skills", "commands", "agents", "templates", "references", "scripts", "hooks"]
MANIFESTOS_VERSAO = [
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".kimi-plugin/plugin.json",
    "gemini-extension.json",
    "package.json",
]

erros: list[str] = []
avisos: list[str] = []


def erro(regra: str, msg: str) -> None:
    erros.append(f"[{regra}] {msg}")


def aviso(regra: str, msg: str) -> None:
    avisos.append(f"[{regra}] {msg}")


def ler_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        erro("json-valido", f"{p}: {e}")
        return None


def frontmatter(caminho: Path):
    """Extrai o mapa do frontmatter YAML de um SKILL.md, sem depender de PyYAML."""
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None, texto
    corpo = m.group(1)
    campos = {}
    for chave in re.findall(r"^([\w-]+):", corpo, re.M):
        dm = re.search(rf"^{re.escape(chave)}:\s*(.*?)(?=^\w[\w-]*:|\Z)", corpo, re.M | re.S)
        if dm:
            campos[chave] = dm.group(1).strip().strip('"').strip("'")
    return campos, texto


def regra_json_valido(raiz: Path) -> list[Path]:
    achados = []
    for rel in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                ".agents/plugins/marketplace.json"] + MANIFESTOS_VERSAO:
        p = raiz / rel
        if p.is_file():
            achados.append(p)
            ler_json(p)
    return achados


def regra_versao_consistente(raiz: Path, pj: dict) -> None:
    alvo = pj.get("version")
    if not alvo:
        erro("versao-consistente", ".claude-plugin/plugin.json sem campo `version`")
        return
    mk = raiz / ".claude-plugin/marketplace.json"
    if mk.is_file():
        d = ler_json(mk) or {}
        for e in d.get("plugins", []):
            if "version" in e and e["version"] != alvo:
                erro("versao-consistente",
                     f".claude-plugin/marketplace.json: entrada `{e.get('name')}` em "
                     f"{e['version']}, plugin.json em {alvo}")
    for rel in MANIFESTOS_VERSAO:
        p = raiz / rel
        if not p.is_file():
            continue
        d = ler_json(p) or {}
        if d.get("version") and d["version"] != alvo:
            erro("versao-consistente", f"{rel}: {d['version']}, plugin.json em {alvo}")


def regra_skills(raiz: Path) -> None:
    dir_skills = raiz / "skills"
    if not dir_skills.is_dir():
        aviso("skill-spec", "sem diretorio skills/ — plugin nao portavel para outros agentes")
        return
    for sk in sorted(dir_skills.iterdir()):
        arq = sk / "SKILL.md"
        if not sk.is_dir() or not arq.is_file():
            continue
        campos, _ = frontmatter(arq)
        if campos is None:
            erro("skill-spec", f"{arq}: sem frontmatter YAML")
            continue
        nome = campos.get("name", "")
        desc = campos.get("description", "")

        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome) or len(nome) > 64:
            erro("skill-spec", f"{arq}: `name: {nome!r}` invalido — use minusculas, digitos e "
                               "hifens simples, ate 64 caracteres")
        if nome != sk.name:
            erro("skill-spec", f"{arq}: `name: {nome}` difere do diretorio `{sk.name}` — a spec "
                               "exige que sejam iguais")
        if not desc:
            erro("skill-spec", f"{arq}: `description` vazia")
        elif len(desc) > LIMITE_DESCRIPTION:
            erro("skill-spec", f"{arq}: description com {len(desc)} caracteres, limite da spec e "
                               f"{LIMITE_DESCRIPTION}")

        # regra 4: gatilho de ativacao nao pode depender de comando de barra.
        # O que importa nao e a description inteira, e a CLAUSULA DE GATILHO — o trecho que diz
        # *quando* usar, antes da primeira pontuacao forte. O resto descreve o que a skill faz, e
        # descricao de comportamento nao ativa skill nenhuma.
        # Skill que declara `compatibility` restrita ao Claude Code nao precisa ativar por
        # linguagem natural: ela nunca vai ser instalada em outro agente. `compatibility` e campo
        # da propria spec Agent Skills, nao invencao nossa.
        so_claude = re.search(r"claude\s*code", campos.get("compatibility", ""), re.I)

        if desc and not so_claude:
            # Mascara os comandos ANTES de procurar o fim da clausula: o `:` de
            # `/plugin:comando` seria lido como pontuacao e truncaria o gatilho no meio.
            CMD = "\x00CMD\x00"
            mascarado = re.sub(r"/[a-z0-9-]+:[a-z0-9-]+", CMD, desc)
            m_gat = re.match(r"^\s*Use\s+(?:when|quando)\b(.*?)(?:[—.:;]|$)", mascarado,
                             re.I | re.S)
            if m_gat:
                gatilho = m_gat.group(1)
                if CMD in gatilho:
                    restante = gatilho.replace(CMD, "")
                    # sobra so conectivo? entao o unico gatilho e o comando de barra
                    palavras = [p for p in re.findall(r"[\w'-]+", restante)
                                if p.lower() not in {
                                    "the", "user", "runs", "run", "o", "usuario", "usuário",
                                    "rodar", "roda", "executar", "or", "and", "ou", "e", "a", "as",
                                    "os", "quando", "when", "use"}]
                    if len(palavras) < 4:
                        legivel = gatilho.replace(CMD, "/<comando>").strip()[:70]
                        erro("ativacao-natural",
                             f"{arq}: a clausula de gatilho da description depende apenas de "
                             f"comando de barra ({legivel}...). Comando de barra so "
                             "existe no Claude Code — nos demais agentes a skill fica instalada e "
                             "inerte. Reescreva abrindo com gatilho em linguagem natural.")
                    else:
                        aviso("ativacao-natural",
                              f"{arq}: a clausula de gatilho cita comando de barra. Confira se o "
                              "gatilho em linguagem natural basta fora do Claude Code.")


def regra_readme_comandos(raiz: Path, pj: dict) -> None:
    readme = raiz / "README.md"
    if not readme.is_file():
        aviso("readme-comandos", "sem README.md")
        return
    texto = readme.read_text(encoding="utf-8")
    nome = pj.get("name", "")
    for ref in sorted(set(re.findall(rf"`/{re.escape(nome)}:([a-z0-9-]+)`", texto))):
        if not (raiz / "commands" / f"{ref}.md").is_file():
            erro("readme-comandos",
                 f"README cita `/{nome}:{ref}`, mas commands/{ref}.md nao existe")


def regra_loja_sincronizada(raiz: Path, pj: dict, loja: Path) -> None:
    """A entrada deste plugin nos catalogos da loja repete verbatim a description do plugin.json."""
    nome = pj.get("name", "")
    desc = pj.get("description", "").strip()
    achou = False
    for rel in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        cat = loja / rel
        if not cat.is_file():
            continue
        try:
            d = json.loads(cat.read_text(encoding="utf-8"))
        except Exception as e:
            erro("loja-sincronizada", f"{cat}: {e}")
            continue
        for e_ in d.get("plugins", []):
            if e_.get("name") != nome:
                continue
            achou = True
            if e_.get("description", "").strip() != desc:
                erro("loja-sincronizada",
                     f"a entrada `{nome}` em {rel} da loja tem description diferente da deste "
                     "plugin.json. Quem instala pelo marketplace decide com base nesse texto — "
                     "atualize a entrada na loja (frwk-plugins) antes de mergear este PR.")
    if not achou:
        aviso("loja-sincronizada",
              f"plugin `{nome}` nao esta em nenhum catalogo da loja — se e um plugin novo, "
              "adicione a entrada em frwk-plugins depois deste merge.")


def conteudo_mudou(raiz: Path, base: str) -> list[str]:
    try:
        r = subprocess.run(["git", "-C", str(raiz), "diff", "--name-only", f"{base}...HEAD"],
                           capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        aviso("versao-bump", f"nao consegui comparar com `{base}`: {e}")
        return []
    mudados = [l for l in r.stdout.splitlines() if l.strip()]
    return [f for f in mudados
            if any(f.startswith(d + "/") for d in DIRS_CONTEUDO) or f == "README.md"]


def regra_versao_bump(raiz: Path, pj: dict, base: str) -> None:
    relevantes = conteudo_mudou(raiz, base)
    if not relevantes:
        return
    try:
        antigo = subprocess.run(
            ["git", "-C", str(raiz), "show", f"{base}:.claude-plugin/plugin.json"],
            capture_output=True, text=True, check=True).stdout
        v_antiga = json.loads(antigo).get("version")
    except Exception:
        return  # plugin.json novo: nao ha versao anterior para comparar
    if v_antiga == pj.get("version"):
        amostra = ", ".join(relevantes[:4]) + ("..." if len(relevantes) > 4 else "")
        erro("versao-bump",
             f"conteudo do plugin mudou ({len(relevantes)} arquivo(s): {amostra}) mas a versao "
             f"continua {v_antiga}. O cache e indexado pela versao: sem bump, a mudanca nao chega "
             "em quem ja instalou.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="caminho do repositorio do plugin")
    ap.add_argument("--base", help="ref do git para comparar (liga a regra de bump)")
    ap.add_argument("--loja", help="caminho de um checkout do frwk-plugins (liga a regra de "
                                   "sincronia da description com a loja)")
    args = ap.parse_args()

    raiz = Path(args.repo).resolve()
    pj_path = raiz / ".claude-plugin/plugin.json"
    if not pj_path.is_file():
        print(f"nao e um repositorio de plugin: {pj_path} nao existe", file=sys.stderr)
        return 1

    regra_json_valido(raiz)
    pj = ler_json(pj_path)
    if pj is None:
        print("\n".join(erros), file=sys.stderr)
        return 1

    regra_versao_consistente(raiz, pj)
    regra_skills(raiz)
    regra_readme_comandos(raiz, pj)
    if args.loja:
        regra_loja_sincronizada(raiz, pj, Path(args.loja).resolve())
    if args.base:
        regra_versao_bump(raiz, pj, args.base)

    nome = pj.get("name", raiz.name)
    print(f"plugin: {nome} v{pj.get('version')}")
    for a in avisos:
        print(f"  aviso  {a}")
    if erros:
        for e in erros:
            print(f"  ERRO   {e}")
        print(f"\n{len(erros)} erro(s). Regras em scripts/validar-plugin.py.", file=sys.stderr)
        return 1
    print(f"  ok     todas as regras passaram ({len(avisos)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
