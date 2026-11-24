#!/usr/bin/env python3
"""
CLI & Helper Library to identify, resolve, manage, and create notes in ~/Notas.
Adheres strictly to the vault architecture and rules defined in AGENTS.md.
"""

import sys
import os
import re
import json
import time
import argparse
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

VAULT_PATH = Path(os.path.expanduser("~/Notas")).resolve()

SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12
}

SPANISH_WEEKDAYS = {
    "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
}


def parse_frontmatter(content: str):
    """Extract YAML frontmatter and markdown body from note content."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    yaml_text = match.group(1)
    body = match.group(2)
    meta = {}
    if yaml:
        try:
            meta = yaml.safe_load(yaml_text) or {}
        except Exception:
            pass
    if not meta:
        # Fallback simple parser supporting lists, nulls, and key-values
        current_list_key = None
        for line in yaml_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("- ") and current_list_key:
                val = stripped[2:].strip().strip('"\'')
                if not isinstance(meta.get(current_list_key), list):
                    meta[current_list_key] = []
                meta[current_list_key].append(val)
            elif ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val_raw = val.strip()
                val_clean = val_raw.strip('"\'')
                if val_raw in ('""', "''"):
                    meta[key] = ""
                    current_list_key = None
                elif val_clean == "[]":
                    meta[key] = []
                    current_list_key = key
                elif val_raw == "" or val_clean == "null":
                    meta[key] = None
                    current_list_key = key
                else:
                    try:
                        if "." in val_clean:
                            meta[key] = float(val_clean)
                        else:
                            meta[key] = int(val_clean)
                    except ValueError:
                        meta[key] = val_clean
                    current_list_key = None
            else:
                current_list_key = None
    return meta, body


def dump_frontmatter(meta: dict, body: str) -> str:
    """Combine metadata and body into standard frontmatter format."""
    if yaml:
        yaml_text = yaml.dump(meta, sort_keys=False, allow_unicode=True).strip()
    else:
        lines = []
        for k, v in meta.items():
            if isinstance(v, list):
                if not v:
                    lines.append(f"{k}: []")
                else:
                    lines.append(f"{k}:")
                    for item in v:
                        lines.append(f"  - {json.dumps(item) if isinstance(item, str) else item}")
            elif v is None:
                lines.append(f"{k}:")
            elif isinstance(v, (int, float)):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {json.dumps(v) if isinstance(v, str) else v}")
        yaml_text = "\n".join(lines)
    return f"---\n{yaml_text}\n---\n\n{body.lstrip()}"


def resolve_date_expression(expr: str, base_date: date = None) -> date:
    """Parse relative or absolute date expressions in Spanish/English."""
    if base_date is None:
        base_date = date.today()

    norm = expr.strip().lower()

    # Exact ISO date: YYYY-MM-DD
    iso_match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", norm)
    if iso_match:
        y, m, d = map(int, iso_match.groups())
        return date(y, m, d)

    # European date: DD/MM/YYYY or DD-MM-YYYY
    eu_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", norm)
    if eu_match:
        d, m, y = map(int, eu_match.groups())
        return date(y, m, d)

    # Relative days
    if norm in ["hoy", "today", "ahora", "current", "nota de hoy", "nota diaria", "diario", "journal", "bitacora", "bitácora"]:
        return base_date
    if norm in ["ayer", "yesterday", "nota de ayer"]:
        return base_date - timedelta(days=1)
    if norm in ["anteayer", "antes de ayer", "antier"]:
        return base_date - timedelta(days=2)
    if norm in ["mañana", "manana", "tomorrow", "nota de mañana", "nota de manana"]:
        return base_date + timedelta(days=1)
    if norm in ["pasado mañana", "pasado manana"]:
        return base_date + timedelta(days=2)

    # Patterns like "hace X días"
    days_ago = re.search(r"hace\s+(\d+)\s+d[ií]as?", norm)
    if days_ago:
        return base_date - timedelta(days=int(days_ago.group(1)))

    # Patterns like "en X días"
    days_in = re.search(r"en\s+(\d+)\s+d[ií]as?", norm)
    if days_in:
        return base_date + timedelta(days=int(days_in.group(1)))

    # Weekdays (e.g. "el lunes", "el lunes pasado", "el viernes que viene")
    for name, wd in SPANISH_WEEKDAYS.items():
        if name in norm:
            current_wd = base_date.weekday()
            if "pasado" in norm or "anterior" in norm:
                diff = (current_wd - wd) % 7
                if diff == 0:
                    diff = 7
                return base_date - timedelta(days=diff)
            elif "que viene" in norm or "proximo" in norm or "próximo" in norm:
                diff = (wd - current_wd) % 7
                if diff == 0:
                    diff = 7
                return base_date + timedelta(days=diff)
            else:
                # Default to nearest past or today
                diff = (current_wd - wd) % 7
                return base_date - timedelta(days=diff)

    # Date with Spanish month: "14 de septiembre", "1 de octubre 2026"
    month_match = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)(?:\s+(?:de\s+)?(\d{4}))?", norm)
    if month_match:
        d = int(month_match.group(1))
        m_str = month_match.group(2)
        y = int(month_match.group(3)) if month_match.group(3) else base_date.year
        if m_str in SPANISH_MONTHS:
            return date(y, SPANISH_MONTHS[m_str], d)

    return base_date


def resolve_entity(query: str) -> dict:
    """
    Intelligently identify what note or vault resource a query refers to.
    Returns entity type, candidate file path, whether it exists, and metadata.
    """
    q = query.strip().lower()

    # 1. DAILY NOTES (Journal / Bitácora)
    daily_keywords = ["nota diaria", "diaria", "diario", "journal", "bitacora", "bitácora", "hoy", "ayer", "mañana", "manana", "daily", "daily-note"]
    is_daily = any(k in q for k in daily_keywords) or any(d in q for d in SPANISH_WEEKDAYS) or re.search(r"\b\d{4}-\d{2}-\d{2}\b", q)

    # Check for finance indicators that might conflict
    is_finance = any(k in q for k in ["finanzas", "cuentas", "gastos", "gasto", "balance", "resumen anual", "recibo", "recibos", "recivo", "recivos", "factura", "facturas", "ticket", "tickets"])

    if is_finance:
        year_match = re.search(r"\b(20\d\d)\b", q)
        year = int(year_match.group(1)) if year_match else date.today().year

        # Check recibos (gastos)
        if any(k in q for k in ["recibo", "recibos", "recivo", "recivos", "ticket", "tickets"]):
            path = VAULT_PATH / "finanzas" / str(year) / "recibos"
            return {
                "type": "finance_recibos",
                "name": f"Recibos {year}",
                "path": str(path),
                "exists": path.is_dir(),
                "year": year
            }

        # Check facturas (emitidas)
        if any(k in q for k in ["factura", "facturas"]):
            path = VAULT_PATH / "finanzas" / str(year) / "facturas"
            return {
                "type": "finance_facturas",
                "name": f"Facturas {year}",
                "path": str(path),
                "exists": path.is_dir(),
                "year": year
            }

        # Check annual summary
        if "resumen anual" in q or "anual" in q:
            path = VAULT_PATH / "finanzas" / f"resumen-anual-{year}.md"
            excel_path = VAULT_PATH / "finanzas" / f"resumen-anual-{year}.xlsx"
            return {
                "type": "finance_annual",
                "name": f"Resumen Anual {year}",
                "path": str(path),
                "excel_path": str(excel_path),
                "exists": path.is_file(),
                "excel_exists": excel_path.is_file(),
                "year": year
            }

        # Monthly finance
        target_date = date.today()
        month_match = re.search(r"\b(20\d\d)-(\d{2})\b", q)
        if month_match:
            year, month = int(month_match.group(1)), int(month_match.group(2))
        else:
            # Check month names
            found_month = None
            for m_name, m_num in SPANISH_MONTHS.items():
                if m_name in q:
                    found_month = m_num
                    break
            month = found_month if found_month else date.today().month

        # In this vault, accounts are organized in finanzas/YYYY/cuentas/YYYY-MM.md
        path_cuentas = VAULT_PATH / "finanzas" / str(year) / "cuentas" / f"{year}-{month:02d}.md"
        path_legacy = VAULT_PATH / "finanzas" / str(year) / "Cuentas" / f"{year}-{month:02d}.md"
        path_direct = VAULT_PATH / "finanzas" / str(year) / f"{year}-{month:02d}.md"
        path = path_cuentas if path_cuentas.is_file() else (path_legacy if path_legacy.is_file() else (path_direct if path_direct.is_file() else path_cuentas))
        excel_path = VAULT_PATH / "finanzas" / str(year) / "cuentas" / f"{year}-{month:02d}.xlsx"

        return {
            "type": "finance_monthly",
            "name": f"Cuentas {year}-{month:02d}",
            "path": str(path),
            "excel_path": str(excel_path),
            "exists": path.is_file(),
            "excel_exists": excel_path.is_file(),
            "year": year,
            "month": month
        }

    if is_daily:
        target_date = resolve_date_expression(q)
        date_str = target_date.strftime("%Y-%m-%d")
        path = VAULT_PATH / "journal" / f"{date_str}.md"
        result = {
            "type": "daily_note",
            "name": f"Nota Diaria {date_str}",
            "date": date_str,
            "path": str(path),
            "exists": path.is_file()
        }
        if path.is_file():
            meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            result["metadata"] = meta
            # Extract events
            events = meta.get("events", [])
            if isinstance(events, str):
                events = [events] if events else []
            result["events"] = events
            # Extract tasks
            tasks = extract_tasks_from_markdown(body)
            result["tasks_summary"] = {
                "total": len(tasks),
                "pending": sum(1 for t in tasks if not t["completed"] and not t.get("postponed")),
                "completed": sum(1 for t in tasks if t["completed"]),
                "postponed": sum(1 for t in tasks if t.get("postponed"))
            }
        return result

    # 2. PROJECTS
    if "proyecto" in q or "project" in q:
        projects_dir = VAULT_PATH / "projects"
        if projects_dir.is_dir():
            for p in projects_dir.iterdir():
                if p.is_dir() and not p.name.startswith("."):
                    if p.name.lower() in q or any(word in p.name.lower() for word in q.split() if len(word) > 3):
                        readme = p / "README.md"
                        return {
                            "type": "project",
                            "name": p.name,
                            "path": str(p),
                            "readme": str(readme) if readme.is_file() else None,
                            "exists": True
                        }

    # 3. ZETTELKASTEN / GENERAL SEARCH
    zettel_dir = VAULT_PATH / "zettelkasten"
    if zettel_dir.is_dir():
        # Match by filename
        clean_q = re.sub(r"[^\w\s-]", "", q).strip()
        candidates = []
        for f in zettel_dir.glob("*.md"):
            name = f.stem.lower()
            if clean_q in name:
                candidates.append(f)
            else:
                # Check aliases in frontmatter
                try:
                    meta, _ = parse_frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
                    aliases = [str(a).lower() for a in meta.get("aliases", [])]
                    if any(clean_q in a for a in aliases):
                        candidates.append(f)
                except Exception:
                    pass

        if candidates:
            best = candidates[0]
            meta, _ = parse_frontmatter(best.read_text(encoding="utf-8", errors="ignore"))
            return {
                "type": "zettelkasten",
                "name": best.stem,
                "path": str(best),
                "exists": True,
                "metadata": meta
            }

    # Default fallback: check if it's a date or treat as zettelkasten query
    target_date = resolve_date_expression(q)
    date_str = target_date.strftime("%Y-%m-%d")
    daily_path = VAULT_PATH / "journal" / f"{date_str}.md"
    if daily_path.is_file():
        return {
            "type": "daily_note",
            "name": f"Nota Diaria {date_str}",
            "date": date_str,
            "path": str(daily_path),
            "exists": True
        }

    return {
        "type": "unknown",
        "query": query,
        "vault_path": str(VAULT_PATH),
        "exists": False
    }


def extract_tasks_from_markdown(content: str) -> list:
    """Extract markdown checkbox tasks with their section headers."""
    tasks = []
    current_section = "General"
    for line in content.splitlines():
        line_clean = line.strip()
        header_match = re.match(r"^(#{1,4})\s+(.+)$", line_clean)
        if header_match:
            current_section = header_match.group(2).strip()
            continue

        task_match = re.match(r"^-\s*\[([ xX>])\]\s*(.*)$", line_clean)
        if task_match:
            marker = task_match.group(1)
            is_done = marker.lower() == "x"
            is_postponed = marker == ">"
            task_text = task_match.group(2).strip()
            if task_text:
                tasks.append({
                    "task": task_text,
                    "completed": is_done,
                    "postponed": is_postponed,
                    "section": current_section,
                    "raw": line
                })
    return tasks


def get_or_create_daily_note(date_val: date) -> tuple[Path, bool]:
    """
    Ensure the daily note exists for date_val.
    If not, create it from templates/plantilla-diaria.md.
    Returns (path, created).
    """
    date_str = date_val.strftime("%Y-%m-%d")
    journal_dir = VAULT_PATH / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    note_path = journal_dir / f"{date_str}.md"

    if note_path.is_file():
        return note_path, False

    # Create from template
    template_path = VAULT_PATH / "templates" / "plantilla-diaria.md"
    if template_path.is_file():
        template_text = template_path.read_text(encoding="utf-8")
        content = template_text.replace("{ { date } }", date_str).replace("{{date}}", date_str)
    else:
        # Fallback standard daily structure adhering to AGENTS.md
        content = f"""---
id: {date_str}
description: ""
events: []
weight:
aliases:
  - "{date_str}"
tags:
  - daily-notes
---

# {date_str}

## TODO

### Trabajo

- [ ] 

### Casa / Personal

- [ ] 
"""
    note_path.write_text(content, encoding="utf-8")
    return note_path, True


def add_task_to_daily_note(date_val: date, task_text: str, category: str = "Casa / Personal") -> bool:
    """
    Add a task checkbox '- [ ] <task_text>' under the specified category in the daily note.
    Creates the note or section if it doesn't already exist.
    """
    note_path, _ = get_or_create_daily_note(date_val)
    content = note_path.read_text(encoding="utf-8")

    category_header = f"### {category}"
    task_line = f"- [ ] {task_text}"

    # Check if category header exists
    if category_header in content:
        # Insert right below the category header
        pattern = re.compile(rf"({re.escape(category_header)}\r?\n)")
        new_content = pattern.sub(rf"\1\n{task_line}\n", content, count=1)
    elif "## TODO" in content:
        # Category doesn't exist, append category and task under ## TODO
        pattern = re.compile(r"(## TODO\r?\n)")
        new_content = pattern.sub(rf"\1\n{category_header}\n\n{task_line}\n", content, count=1)
    else:
        # Append ## TODO, category, and task
        new_content = content.rstrip() + f"\n\n## TODO\n\n{category_header}\n\n{task_line}\n"

    # Clean double empty lines
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)
    note_path.write_text(new_content, encoding="utf-8")
    return True


def postpone_task_in_daily_note(from_date: date, to_date: date, task_query: str, target_category: str = None) -> tuple[bool, str]:
    """
    Postpone a task from from_date's daily note to to_date's daily note.
    - Marks task as '- [>] <task> ⏳ pospuesto a [[YYYY-MM-DD]]' in from_date note.
    - Ensures to_date daily note exists and adds '- [>] <task> ⏳ pospuesto desde [[YYYY-MM-DD]]'.
    """
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")

    from_path = VAULT_PATH / "journal" / f"{from_date_str}.md"
    if not from_path.is_file():
        return False, f"La nota diaria de origen ({from_date_str}) no existe en {from_path}."

    content = from_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    target_idx = -1
    detected_category = target_category or "Casa / Personal"
    cleaned_task = None
    current_section = "General"

    query_lower = task_query.strip().lower()

    for idx, line in enumerate(lines):
        line_clean = line.strip()
        h_match = re.match(r"^(#{1,4})\s+(.+)$", line_clean)
        if h_match:
            current_section = h_match.group(2).strip()
            continue

        t_match = re.match(r"^(\s*-\s*\[)([ xX>])(\]\s*)(.*)$", line)
        if t_match:
            task_body = t_match.group(4).strip()
            if query_lower in task_body.lower():
                target_idx = idx
                cleaned_task = re.sub(r"\s*⏳\s*pospuesto\s+(?:a|desde)\s+\[\[.*?\]\]", "", task_body).strip()
                if not target_category and current_section not in ["TODO", "General"]:
                    detected_category = current_section
                break

    if target_idx == -1 or not cleaned_task:
        return False, f"No se encontró ninguna tarea que coincida con '{task_query}' en {from_date_str}."

    # Update origin line
    indent_match = re.match(r"^(\s*-\s*)", lines[target_idx])
    indent_prefix = indent_match.group(1) if indent_match else "- "
    lines[target_idx] = f"{indent_prefix}[>] {cleaned_task} ⏳ pospuesto a [[{to_date_str}]]"
    from_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Add to destination note
    to_note_path, _ = get_or_create_daily_note(to_date)
    to_content = to_note_path.read_text(encoding="utf-8")

    category_header = f"### {detected_category}"
    to_task_line = f"- [>] {cleaned_task} ⏳ pospuesto desde [[{from_date_str}]]"

    if category_header in to_content:
        pattern = re.compile(rf"({re.escape(category_header)}\r?\n)")
        new_to_content = pattern.sub(rf"\1\n{to_task_line}\n", to_content, count=1)
    elif "## TODO" in to_content:
        pattern = re.compile(r"(## TODO\r?\n)")
        new_to_content = pattern.sub(rf"\1\n{category_header}\n\n{to_task_line}\n", to_content, count=1)
    else:
        new_to_content = to_content.rstrip() + f"\n\n## TODO\n\n{category_header}\n\n{to_task_line}\n"

    new_to_content = re.sub(r"\n{3,}", "\n\n", new_to_content)
    to_note_path.write_text(new_to_content, encoding="utf-8")

    return True, f"Tarea pospuesta de {from_date_str} a {to_date_str} [{detected_category}]: {cleaned_task}"


def add_event_to_daily_note(date_val: date, event_text: str) -> bool:
    """Add an event to the events list in YAML frontmatter of the daily note."""
    note_path, _ = get_or_create_daily_note(date_val)
    content = note_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    events = meta.get("events", [])
    if isinstance(events, str):
        events = [events] if events else []
    elif events is None:
        events = []

    if event_text not in events:
        events.append(event_text)
    meta["events"] = events

    new_content = dump_frontmatter(meta, body)
    note_path.write_text(new_content, encoding="utf-8")
    return True


def set_weight_daily_note(date_val: date, weight_val) -> bool:
    """Set or update the weight in the YAML frontmatter of the daily note."""
    note_path, _ = get_or_create_daily_note(date_val)
    content = note_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    if weight_val is None or weight_val == "":
        meta["weight"] = None
    else:
        try:
            num = float(weight_val)
            meta["weight"] = int(num) if num.is_integer() else num
        except (ValueError, TypeError):
            meta["weight"] = weight_val

    new_content = dump_frontmatter(meta, body)
    note_path.write_text(new_content, encoding="utf-8")
    return True


def classify_note_topic(topic: str) -> dict:
    """
    Classify what type of note should be created and where, according to AGENTS.md rules.
    """
    t = topic.lower().strip()
    timestamp = str(int(time.time()))

    if any(k in t for k in ["diario", "hoy", "ayer", "mañana", "journal", "bitacora", "bitácora", "tarea diaria"]):
        today_str = date.today().strftime("%Y-%m-%d")
        return {
            "type": "daily_note",
            "directory": "journal/",
            "filename": f"{today_str}.md",
            "template": "templates/plantilla-diaria.md",
            "tags": ["daily-notes"],
            "rule": "Bitácora diaria en journal/YYYY-MM-DD.md"
        }

    if any(k in t for k in ["factura", "facturas", "facturación", "facturacion"]):
        today = date.today()
        return {
            "type": "finance_facturas",
            "directory": f"finanzas/{today.year}/facturas/",
            "filename": f"factura-{timestamp}.pdf",
            "tags": ["finanzas", "finanzas/facturas"],
            "rule": "Facturas emitidas organizadas en finanzas/YYYY/facturas/"
        }

    if any(k in t for k in ["recibo", "recibos", "recivo", "recivos", "ticket", "tickets", "justificante"]):
        today = date.today()
        return {
            "type": "finance_recibos",
            "directory": f"finanzas/{today.year}/recibos/",
            "filename": f"recibo-{timestamp}.pdf",
            "tags": ["finanzas", "finanzas/recibos"],
            "rule": "Recibos y justificantes de gastos organizados en finanzas/YYYY/recibos/"
        }

    if any(k in t for k in ["finanzas", "gasto", "gastos", "cuenta", "cuentas", "presupuesto", "hacienda", "ingreso"]):
        today = date.today()
        target_month = today.month
        for m_name, m_num in SPANISH_MONTHS.items():
            if m_name in t:
                target_month = m_num
                break
        return {
            "type": "finance",
            "directory": f"finanzas/{today.year}/cuentas/",
            "filename": f"{today.year}-{target_month:02d}.md",
            "excel": f"{today.year}-{target_month:02d}.xlsx",
            "template": "templates/plantilla-cuentas-mes.md",
            "tags": ["finanzas", "finanzas/mensual"],
            "rule": "Gestión financiera organizada en finanzas/YYYY/cuentas/YYYY-MM.md + YYYY-MM.xlsx"
        }

    if any(k in t for k in ["proyecto", "desarrollo", "sistema"]):
        # Extract slug
        slug = re.sub(r"[^\w\s-]", "", t).replace(" ", "-").strip("-")
        return {
            "type": "project",
            "directory": f"projects/{slug}/docs/",
            "filename": f"{slug}.md",
            "tags": ["project", slug],
            "rule": "Proyectos en projects/<nombre-proyecto>/ con docs/, fases/, backups/"
        }

    # Default: Zettelkasten atomic note
    slug = re.sub(r"[^\w\s-]", "", t).replace(" ", "-").strip("-")
    acronym = "".join([w[0].upper() for w in re.findall(r"\w+", t)[:4]])
    if not acronym or len(acronym) < 2:
        acronym = "NOTE"
    filename = f"{timestamp}-{slug[:30]}.md" if slug else f"{timestamp}-{acronym}.md"

    return {
        "type": "zettelkasten",
        "directory": "zettelkasten/",
        "filename": filename,
        "template": "templates/plantilla-nota.md",
        "tags": ["conocimiento", "atomico"],
        "rule": "Notas genéricas y conocimiento atómico en zettelkasten/<TIMESTAMP>-<SLUG/ACRONIMO>.md"
    }


def semantic_search(term: str, limit: int = 20) -> list:
    """Delegate to the embedding index (notes_index.py) for hybrid semantic search."""
    script = Path(__file__).resolve().parent / "notes_index.py"
    if not script.is_file():
        return []
    try:
        out = subprocess.run(
            [sys.executable, str(script), "find", term, "-k", str(limit), "--json"],
            capture_output=True, text=True, timeout=180,
        )
        if out.returncode != 0:
            return []
        items = json.loads(out.stdout)
        return [
            {
                "relative_path": it["path"],
                "path": it["full_path"],
                "filename": Path(it["path"]).name,
                "score": it.get("score"),
                "match": "semantic",
            }
            for it in items
        ]
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser(description="Notas Vault Helper & Entity Resolver")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Resolve command
    res_parser = subparsers.add_parser("resolve", help="Resolve human phrase like 'nota diaria' to vault entity")
    res_parser.add_argument("query", help="Phrase to resolve, e.g. 'nota diaria', 'ayer', 'cuentas de septiembre'")
    res_parser.add_argument("--json", action="store_true", help="Print structured JSON output")

    # 2. Daily note subcommands
    daily_parser = subparsers.add_parser("daily", help="Manage daily notes")
    daily_sub = daily_parser.add_subparsers(dest="daily_command", required=True)

    # daily get
    d_get = daily_sub.add_parser("get", help="Get daily note details")
    d_get.add_argument("--date", default="hoy", help="Date: 'hoy', 'ayer', 'mañana', 'YYYY-MM-DD'")
    d_get.add_argument("--json", action="store_true")

    # daily create
    d_create = daily_sub.add_parser("create", help="Create daily note if missing")
    d_create.add_argument("--date", default="hoy", help="Date: 'hoy', 'ayer', 'mañana', 'YYYY-MM-DD'")

    # daily add-task
    d_task = daily_sub.add_parser("add-task", help="Add a task to the daily note")
    d_task.add_argument("task", help="Task description")
    d_task.add_argument("--category", default="Casa / Personal", help="Category: 'Casa / Personal', 'Trabajo', 'Social'")
    d_task.add_argument("--date", default="hoy", help="Date expression")

    # daily postpone-task
    d_postpone = daily_sub.add_parser("postpone-task", help="Postpone a task from one daily note to another")
    d_postpone.add_argument("task", help="Task description or substring to match")
    d_postpone.add_argument("--to", required=True, help="Destination date ('mañana', 'YYYY-MM-DD', etc.)")
    d_postpone.add_argument("--date", default="hoy", help="Source date (default: 'hoy')")
    d_postpone.add_argument("--category", default=None, help="Target category (inherits from source if omitted)")

    # daily add-event
    d_event = daily_sub.add_parser("add-event", help="Add an event to daily note frontmatter")
    d_event.add_argument("event", help="Event description")
    d_event.add_argument("--date", default="hoy", help="Date expression")

    # daily set-weight
    d_weight = daily_sub.add_parser("set-weight", help="Set body weight in daily note frontmatter")
    d_weight.add_argument("weight", help="Weight value (e.g. 78.5)")
    d_weight.add_argument("--date", default="hoy", help="Date expression")

    # 3. Classify command
    class_parser = subparsers.add_parser("classify", help="Determine category and target path for a note")
    class_parser.add_argument("topic", help="Topic or title of the note")
    class_parser.add_argument("--json", action="store_true")

    # 4. Search command
    search_parser = subparsers.add_parser("search", help="Search vault notes")
    search_parser.add_argument("term", help="Search term")
    search_parser.add_argument("--json", action="store_true")

    # 5. Finance command (Excel + Markdown summary sync)
    fin_parser = subparsers.add_parser("finance", help="Manage finance notes and their paired Excel (.xlsx) workbooks")
    fin_sub = fin_parser.add_subparsers(dest="finance_command", required=True)
    f_sync = fin_sub.add_parser("sync", help="Generate/update paired .xlsx and Markdown summary callouts")
    f_sync.add_argument("--year", type=int, default=None, help="Year (e.g. 2026)")
    f_sync.add_argument("--month", type=int, default=None, help="Month (1-12)")
    f_sync.add_argument("--create", action="store_true", help="Create monthly note from template if missing")

    args = parser.parse_args()

    if args.command == "resolve":
        res = resolve_entity(args.query)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"Tipo: {res.get('type')}")
            print(f"Nombre: {res.get('name')}")
            print(f"Ruta: {res.get('path')}")
            if res.get("excel_path"):
                print(f"Excel: {res.get('excel_path')} ({'Sí' if res.get('excel_exists') else 'No'})")
            print(f"Existe: {'Sí' if res.get('exists') else 'No'}")
            if "events" in res and res["events"]:
                print(f"Eventos: {', '.join(res['events'])}")
            if "tasks_summary" in res:
                ts = res["tasks_summary"]
                print(f"Tareas: {ts['total']} (Pendientes: {ts['pending']}, Completadas: {ts['completed']})")

    elif args.command == "daily":
        d_val = resolve_date_expression(args.date)
        if args.daily_command == "get":
            date_str = d_val.strftime("%Y-%m-%d")
            path = VAULT_PATH / "journal" / f"{date_str}.md"
            if not path.is_file():
                res = {"exists": False, "date": date_str, "path": str(path)}
            else:
                meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
                tasks = extract_tasks_from_markdown(body)
                res = {
                    "exists": True,
                    "date": date_str,
                    "path": str(path),
                    "metadata": meta,
                    "events": meta.get("events", []),
                    "tasks": tasks
                }
            if args.json:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            else:
                if not res["exists"]:
                    print(f"Nota diaria {date_str} NO existe en {path}")
                else:
                    print(f"📅 Nota Diaria: {date_str}")
                    print(f"📂 Ruta: {path}")
                    if res.get("events"):
                        print(f"📌 Eventos:")
                        for ev in res["events"]:
                            print(f"   - {ev}")
                    if meta.get("weight") is not None:
                        print(f"⚖️ Peso: {meta['weight']} kg")
                    print(f"✅ Tareas ({len(res['tasks'])}):")
                    for t in res["tasks"]:
                        if t.get("completed"):
                            status = "[x]"
                        elif t.get("postponed"):
                            status = "[>]"
                        else:
                            status = "[ ]"
                        print(f"   {status} ({t['section']}) {t['task']}")

        elif args.daily_command == "create":
            path, created = get_or_create_daily_note(d_val)
            print(f"{'Creada' if created else 'Ya existía'}: {path}")

        elif args.daily_command == "add-task":
            add_task_to_daily_note(d_val, args.task, args.category)
            date_str = d_val.strftime("%Y-%m-%d")
            print(f"Tarea añadida a la nota diaria {date_str} [{args.category}]: {args.task}")

        elif args.daily_command == "postpone-task":
            to_val = resolve_date_expression(args.to, base_date=d_val)
            ok, msg = postpone_task_in_daily_note(d_val, to_val, args.task, args.category)
            if ok:
                print(f"✅ {msg}")
            else:
                print(f"❌ Error: {msg}", file=sys.stderr)
                sys.exit(1)

        elif args.daily_command == "add-event":
            add_event_to_daily_note(d_val, args.event)
            date_str = d_val.strftime("%Y-%m-%d")
            print(f"Evento añadido a la nota diaria {date_str}: {args.event}")

        elif args.daily_command == "set-weight":
            set_weight_daily_note(d_val, args.weight)
            date_str = d_val.strftime("%Y-%m-%d")
            print(f"Peso registrado en la nota diaria {date_str}: {args.weight} kg")

    elif args.command == "classify":
        res = classify_note_topic(args.topic)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"Categoría: {res['type']}")
            print(f"Directorio: {res['directory']}")
            print(f"Archivo sugerido: {res['filename']}")
            print(f"Regla: {res['rule']}")

    elif args.command == "search":
        term = args.term.lower()
        results = []
        for md_file in VAULT_PATH.glob("**/*.md"):
            if ".trash" in md_file.parts or ".obsidian" in md_file.parts:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                if term in md_file.name.lower() or term in content.lower():
                    rel = md_file.relative_to(VAULT_PATH)
                    results.append({
                        "relative_path": str(rel),
                        "path": str(md_file),
                        "filename": md_file.name
                    })
            except Exception:
                pass

        if len(results) < 3:
            seen = {r["relative_path"] for r in results}
            for r in results:
                r["match"] = "lexical"
            for sem in semantic_search(args.term):
                if sem["relative_path"] not in seen:
                    seen.add(sem["relative_path"])
                    results.append(sem)

        if args.json:
            print(json.dumps(results[:20], indent=2, ensure_ascii=False))
        else:
            print(f"Encontradas {len(results)} notas (mostrando hasta 20):")
            for r in results[:20]:
                tag = " [sem]" if r.get("match") == "semantic" else ""
                print(f" - {r['relative_path']}{tag}")

    elif args.command == "finance":
        fin_script = Path(__file__).resolve().parent / "finance_excel.py"
        cmd = [sys.executable, str(fin_script), "sync"]
        if args.year:
            cmd += ["--year", str(args.year)]
        if args.month:
            cmd += ["--month", str(args.month)]
        if args.create:
            cmd.append("--create")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
