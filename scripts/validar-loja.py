#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida a consistencia interna da loja frwk-plugins.

A loja publica DOIS catalogos do mesmo conjunto de plugins:

  .claude-plugin/marketplace.json   lido por Claude Code, Copilot CLI, Cursor e Factory Droid
  .agents/plugins/marketplace.json  lido pelo Codex

Sao dois arquivos porque cada familia de agente procura um caminho diferente — mas descrevem a
MESMA loja. Divergencia entre eles significa que dois usuarios em agentes diferentes veem lojas
diferentes, e ninguem percebe: cada um so enxerga o proprio catalogo.

Checa:
  1. JSON valido nos dois catalogos.
  2. Mesmo conjunto de plugins nos dois.
  3. Description identica entre os dois, para cada plugin.
  4. O source dos dois aponta para o mesmo repositorio (formatos diferem por design:
     github/repo no .claude-plugin, URL git no .agents — o alvo e que deve ser o mesmo).
  5. Toda entrada do catalogo tem linha de install no README, e vice-versa.

O que este script NAO cobre: comparar a description da loja com o plugin.json de cada plugin.
Isso exige ler 11 repositorios privados, que o GITHUB_TOKEN da loja nao alcanca — essa regra e
cobrada no CI de CADA PLUGIN (validar-plugin.py --loja), que enxerga a loja publica.

Uso: python scripts/validar-loja.py [--repo CAMINHO]
Sai com 1 se qualquer checagem falhar.
"""

import argparse
import json
import re
import sys
from pathlib import Path

erros: list[str] = []


def erro(msg: str) -> None:
    erros.append(msg)


def repo_de(source) -> str:
    """Normaliza o alvo de um campo source para owner/repo, qualquer que seja o formato."""
    if not isinstance(source, dict):
        return str(source)
    if source.get("source") == "github":
        return source.get("repo", "")
    url = source.get("url", "")
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    return m.group(1) if m else url


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="caminho do checkout da loja")
    args = ap.parse_args()
    raiz = Path(args.repo).resolve()

    catalogos = {}
    for rel in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        p = raiz / rel
        if not p.is_file():
            erro(f"{rel}: nao existe")
            continue
        try:
            catalogos[rel] = {e["name"]: e for e in
                              json.loads(p.read_text(encoding="utf-8")).get("plugins", [])}
        except Exception as e:
            erro(f"{rel}: {e}")

    if len(catalogos) == 2:
        (rel_a, a), (rel_b, b) = catalogos.items()
        so_a, so_b = set(a) - set(b), set(b) - set(a)
        for n in sorted(so_a):
            erro(f"`{n}` esta em {rel_a} mas falta em {rel_b}")
        for n in sorted(so_b):
            erro(f"`{n}` esta em {rel_b} mas falta em {rel_a}")
        for n in sorted(set(a) & set(b)):
            if a[n].get("description", "").strip() != b[n].get("description", "").strip():
                erro(f"`{n}`: description diverge entre os dois catalogos — usuarios em agentes "
                     "diferentes veem lojas diferentes")
            ra, rb = repo_de(a[n].get("source")), repo_de(b[n].get("source"))
            if ra.lower() != rb.lower():
                erro(f"`{n}`: source aponta para repositorios diferentes ({ra} vs {rb})")

    readme = raiz / "README.md"
    if readme.is_file() and catalogos:
        texto = readme.read_text(encoding="utf-8")
        install = set(re.findall(r"/plugin install ([a-z0-9-]+)@frwk-plugins", texto))
        nomes = set(next(iter(catalogos.values())))
        for n in sorted(nomes - install):
            erro(f"`{n}` esta no catalogo mas nao tem linha de install no README")
        for n in sorted(install - nomes):
            erro(f"README tem linha de install para `{n}`, que nao esta no catalogo")

    n_plugins = len(next(iter(catalogos.values()))) if catalogos else 0
    print(f"loja: {n_plugins} plugins em {len(catalogos)} catalogo(s)")
    if erros:
        for e in erros:
            print(f"  ERRO   {e}")
        print(f"\n{len(erros)} erro(s).", file=sys.stderr)
        return 1
    print("  ok     catalogos consistentes entre si e com o README")
    return 0


if __name__ == "__main__":
    sys.exit(main())
