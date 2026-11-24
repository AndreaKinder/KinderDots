#!/usr/bin/env python3
"""Valida una skill contra las reglas de skill-architect. Sin dependencias externas."""

import re
import sys
from pathlib import Path


def parse_frontmatter(text):
    """Extrae y valida el frontmatter YAML basico de SKILL.md.

    Soporta pares clave-valor y listas con '-'. No soporta YAML complejo.
    Devuelve (dict_parsed, error_str).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "falta apertura '---' del frontmatter"

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "falta cierre '---' del frontmatter"

    fm_lines = lines[1:end]
    parsed = {}
    key = None
    values = []

    for line in fm_lines:
        stripped = line.rstrip()
        if not stripped.strip():
            continue

        key_match = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", stripped)
        if key_match:
            if key is not None:
                parsed[key] = values
            key = key_match.group(1)
            rest = key_match.group(2).strip()
            values = [rest] if rest else []
            continue

        list_match = re.match(r"^\s+-\s+(.*)$", stripped)
        if list_match and key is not None:
            values.append(("list", list_match.group(1).strip()))
            continue

        if key is not None:
            values.append(stripped.strip())

    if key is not None:
        parsed[key] = values

    return parsed, None


def find_links(text):
    """Devuelve una lista de destinos de enlaces Markdown.

    Ignora bloques de codigo delimitados por triple backtick.
    """
    clean = re.sub(r"```[\s\S]*?```", "", text)
    return re.findall(r"\]\(([^)]+)\)", clean)


def main(skill_path):
    base = Path(skill_path)
    skill_md = base / "SKILL.md"

    if not skill_md.exists():
        print(f"ERROR: no existe {skill_md}", file=sys.stderr)
        return 1

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) > 119:
        print(f"ERROR: SKILL.md tiene {len(lines)} lineas (max 119)", file=sys.stderr)
        return 1
    print(f"OK: SKILL.md tiene {len(lines)} lineas")

    fm, err = parse_frontmatter(text)
    if err:
        print(f"ERROR: frontmatter invalido: {err}", file=sys.stderr)
        return 1
    if not fm:
        print("ERROR: frontmatter vacio", file=sys.stderr)
        return 1

    for required in ("name", "description"):
        if required not in fm:
            print(f"ERROR: frontmatter falta '{required}'", file=sys.stderr)
            return 1
    print("OK: frontmatter YAML basico valido")

    broken = []
    for link in find_links(text):
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = base / link
        if not target.exists():
            broken.append(link)
    if broken:
        print(f"ERROR: enlaces rotos en SKILL.md: {broken}", file=sys.stderr)
        return 1
    print("OK: todos los enlaces relativos existen")

    refs_dir = base / "references"
    nested = []
    if refs_dir.exists():
        for ref in refs_dir.rglob("*.md"):
            ref_text = ref.read_text(encoding="utf-8")
            for link in find_links(ref_text):
                if link.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                if "references/" in link:
                    nested.append((str(ref.relative_to(base)), link))
    if nested:
        print("ERROR: enlaces anidados en references/:", file=sys.stderr)
        for ref, link in nested:
            print(f"  {ref} -> {link}", file=sys.stderr)
        return 1
    print("OK: no hay enlaces anidados en references/")

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <ruta_skill>", file=sys.stderr)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
