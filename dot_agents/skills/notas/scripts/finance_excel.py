#!/usr/bin/env python3
"""
Generador y sincronizador de libros Excel (.xlsx) y resúmenes en Markdown (.md)
para las notas de finanzas de ~/Notas/finanzas/ (sin dependencias externas, solo stdlib).

Cada mes en `finanzas/YYYY/cuentas/` consta de:
  - `YYYY-MM.xlsx`: Libro Excel con hojas `Resumen`, `Ingresos`, `Gastos`, `Deudas` y `Comida`
    (con fórmulas OOXML nativas evaluadas y tablas Excel, listo para abrir en Neovim con xleak.nvim).
  - `YYYY-MM.md`: Nota Markdown con el resumen ejecutivo del Excel y el desglose del mes.

Y a nivel anual en `finanzas/`:
  - `resumen-anual-YYYY.xlsx`: Libro consolidado anual con hoja `Consolidado` y `Deudas`.
  - `resumen-anual-YYYY.md`: Nota Markdown enlazada al Excel anual y a cada mes.
"""

import os
import re
import sys
import zipfile
import argparse
from datetime import date
from pathlib import Path

VAULT_PATH = Path(os.getenv("NOTAS_VAULT", os.getenv("NOTES_BASE_DIR", os.path.expanduser("~/Notas")))).resolve()
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'

MONTH_NAMES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


# ---------------------------------------------------------------------------
# Escritor OOXML (.xlsx) puro en stdlib
# ---------------------------------------------------------------------------

def col_letter(idx: int) -> str:
    letters = ""
    while idx > 0:
        idx, rest = divmod(idx - 1, 26)
        letters = chr(ord("A") + rest) + letters
    return letters


def xml_escape(text) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_cell(ref: str, value) -> str:
    """
    value:
      - ('s', str)
      - ('n', float|int)
      - ('b', bool)
      - ('f', formula_str, cached_val)
      - str | int | float | bool | None
    """
    if value is None:
        return ""
    if not isinstance(value, tuple):
        if isinstance(value, bool):
            value = ("b", value)
        elif isinstance(value, (int, float)):
            value = ("n", round(float(value), 2))
        else:
            value = ("s", str(value))

    kind = value[0]
    if kind == "s":
        return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{xml_escape(value[1])}</t></is></c>'
    if kind == "n":
        num = round(float(value[1]), 2) if isinstance(value[1], float) else value[1]
        return f'<c r="{ref}"><v>{num}</v></c>'
    if kind == "b":
        return f'<c r="{ref}" t="b"><v>{1 if value[1] else 0}</v></c>'
    if kind == "f":
        _, formula, cached = value
        if cached is not None and isinstance(cached, float):
            cached = round(cached, 2)
        cached_xml = f"<v>{cached}</v>" if cached is not None else ""
        return f'<c r="{ref}"><f>{xml_escape(formula)}</f>{cached_xml}</c>'
    return ""


def build_sheet_xml(rows: list, has_table: bool = False) -> str:
    last_row = max(len(rows), 1)
    last_col = max((len(r) for r in rows), default=1)
    dimension = f"A1:{col_letter(last_col)}{last_row}"
    body = []
    for r_idx, row in enumerate(rows, start=1):
        cells = "".join(
            build_cell(f"{col_letter(c_idx)}{r_idx}", val)
            for c_idx, val in enumerate(row, start=1)
            if val is not None
        )
        body.append(f'<row r="{r_idx}">{cells}</row>')
    table_parts = '<tableParts count="1"><tablePart r:id="rId1"/></tableParts>' if has_table else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<worksheet {NS}><dimension ref="{dimension}"/><sheetData>'
        + "".join(body)
        + f"</sheetData>{table_parts}</worksheet>"
    )


def build_table_xml(table_id: int, name: str, headers: list, num_rows: int) -> str:
    last_col = col_letter(max(len(headers), 1))
    last_row = max(num_rows, 2)
    ref = f"A1:{last_col}{last_row}"
    cols_xml = "".join(
        f'<tableColumn id="{i}" name="{xml_escape(h)}"/>'
        for i, h in enumerate(headers, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<table xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'id="{table_id}" name="{xml_escape(name)}" displayName="{xml_escape(name)}" '
        f'ref="{ref}" totalsRowShown="0">'
        f'<tableColumns count="{len(headers)}">{cols_xml}</tableColumns>'
        "</table>"
    )


def write_xlsx(out_path: Path, sheets: list):
    """
    sheets: list of dicts:
      {
        "name": str,
        "rows": list[list],
        "table_name": Optional[str]
      }
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ct_overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]
    wb_sheets = []
    wb_rels = []
    tables_to_write = []

    for idx, sh in enumerate(sheets, start=1):
        ct_overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        wb_sheets.append(
            f'<sheet name="{xml_escape(sh["name"])}" sheetId="{idx}" r:id="rId{idx}"/>'
        )
        wb_rels.append(
            f'<Relationship Id="rId{idx}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
        if sh.get("table_name") and sh["rows"]:
            t_id = len(tables_to_write) + 1
            ct_overrides.append(
                f'<Override PartName="/xl/tables/table{t_id}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/>'
            )
            headers = [
                (c[1] if isinstance(c, tuple) else str(c))
                for c in sh["rows"][0]
            ]
            tables_to_write.append((idx, t_id, sh["table_name"], headers, len(sh["rows"])))

    ct_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + "".join(ct_overrides)
        + "</Types>"
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    wb_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f"<workbook {NS}><sheets>"
        + "".join(wb_sheets)
        + "</sheets></workbook>"
    )

    wb_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(wb_rels)
        + "</Relationships>"
    )

    table_by_sheet = {s_idx: (t_id, t_name, hdrs, nrows) for (s_idx, t_id, t_name, hdrs, nrows) in tables_to_write}

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", ct_xml)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", wb_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)

        for idx, sh in enumerate(sheets, start=1):
            has_table = idx in table_by_sheet
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", build_sheet_xml(sh["rows"], has_table=has_table))
            if has_table:
                t_id, t_name, hdrs, nrows = table_by_sheet[idx]
                zf.writestr(f"xl/tables/table{t_id}.xml", build_table_xml(t_id, t_name, hdrs, nrows))
                sheet_rels = (
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/table" Target="../tables/table{t_id}.xml"/>'
                    "</Relationships>"
                )
                zf.writestr(f"xl/worksheets/_rels/sheet{idx}.xml.rels", sheet_rels)


# ---------------------------------------------------------------------------
# Parser de notas mensuales Markdown existentes
# ---------------------------------------------------------------------------

def parse_num(val_str: str) -> float:
    raw = str(val_str).strip()
    if "+" in raw:
        parts = [p.strip() for p in raw.split("+") if p.strip()]
        if len(parts) > 1:
            return round(sum(parse_num(p) for p in parts), 2)
    clean = re.sub(r"[`*€+]", "", raw).strip()
    if not clean or clean == "-":
        return 0.0
    # fracciones tipo 14/3
    frac = re.match(r"^(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)$", clean)
    if frac:
        denom = float(frac.group(2))
        return round(float(frac.group(1)) / denom, 2) if denom else 0.0
    clean = clean.replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", clean)
    return round(float(m.group(0)), 2) if m else 0.0


def extract_markdown_tables_by_heading(md_text: str) -> dict:
    """Devuelve { heading_title: [ [cell1, cell2, ...], ... ] }."""
    sections = {}
    current_h = "Raíz"
    for line in md_text.splitlines():
        s = line.strip()
        hm = re.match(r"^#{2,3}\s+(.+)$", s)
        if hm:
            current_h = hm.group(1).strip()
            sections.setdefault(current_h, [])
            continue
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            # saltar separador | :--- | :---: |
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            sections.setdefault(current_h, []).append(cells)
    return sections


def parse_monthly_md(md_path: Path) -> dict:
    """Extrae la estructura financiera de un archivo YYYY-MM.md."""
    text = md_path.read_text(encoding="utf-8")
    tables = extract_markdown_tables_by_heading(text)

    data = {
        "ingresos": [],
        "suscripciones": [],
        "hogar": [],
        "deudas_amigos": [],
        "deudas_entidades": [],
        "deudas_hacienda": [],
        "comida": [],
        "glovo": [],
        "medicacion": [],
        "impuestos": [],
        "resumen": [],
    }

    for heading, rows in tables.items():
        if not rows or len(rows) < 2:
            continue
        body = [r for r in rows[1:] if not any("total" in c.lower() for c in r[:1])]
        h_low = heading.lower()
        if "ingresos" in h_low:
            for r in body:
                if len(r) >= 5:
                    data["ingresos"].append((r[0], parse_num(r[1]), parse_num(r[2]), r[3], r[4]))
        elif "suscripciones" in h_low:
            for r in body:
                if len(r) >= 4:
                    data["suscripciones"].append((r[0], parse_num(r[1]), r[2], r[3]))
        elif "hogar" in h_low:
            for r in body:
                if len(r) >= 4:
                    data["hogar"].append((r[0], parse_num(r[1]), r[2], r[3]))
        elif "amistades" in h_low:
            for r in body:
                if len(r) >= 4:
                    data["deudas_amigos"].append((r[0], parse_num(r[1]), parse_num(r[2]), r[3]))
        elif "prestamistas" in h_low or "entidades" in h_low:
            for r in body:
                if len(r) >= 4:
                    data["deudas_entidades"].append((r[0], parse_num(r[1]), parse_num(r[2]), r[3]))
                elif len(r) == 3:
                    data["deudas_entidades"].append((r[0], parse_num(r[1]), 0.0, r[2]))
        elif "hacienda" in h_low:
            for r in body:
                if len(r) >= 6:
                    data["deudas_hacienda"].append((r[0], parse_num(r[1]), int(parse_num(r[2])), parse_num(r[3]), r[4], r[5]))
        elif "comida semanal" in h_low:
            for r in body:
                if len(r) >= 4:
                    data["comida"].append((r[0], parse_num(r[1]), parse_num(r[2]), parse_num(r[3])))
        elif "glovo" in h_low:
            for r in body:
                if len(r) >= 5:
                    data["glovo"].append((r[0], r[1], parse_num(r[2]), r[3], r[4]))
        elif "medicación" in h_low or "medicacion" in h_low:
            for r in body:
                if len(r) >= 3:
                    data["medicacion"].append((r[0], parse_num(r[1]), r[2]))
        elif "impuestos" in h_low:
            for r in body:
                if len(r) >= 3:
                    data["impuestos"].append((r[0], parse_num(r[1]), r[2]))
        elif "resumen general" in h_low:
            for r in body:
                if len(r) >= 3:
                    data["resumen"].append((r[0], parse_num(r[1]), parse_num(r[2])))

    return data


def default_monthly_data(year: int, month: int) -> dict:
    m_str = f"{month:02d}"
    return {
        "ingresos": [
            ("Facturación / Nómina", 0.0, 0.0, f"01/{m_str}/{year}", "[ ] Pendiente"),
            ("Otros Ingresos", 0.0, 0.0, "-", "[ ] Pendiente"),
        ],
        "suscripciones": [
            ("Suscripción ejemplo", 0.0, f"01/{m_str}/{year}", "[ ] Pendiente"),
        ],
        "hogar": [
            ("Alquiler / Hipoteca", 0.0, f"01/{m_str}/{year}", "[ ] Pendiente"),
            ("Luz", 0.0, f"10/{m_str}/{year}", "[ ] Pendiente"),
            ("Internet", 0.0, f"05/{m_str}/{year}", "[ ] Pendiente"),
            ("Gas / Agua", 0.0, f"15/{m_str}/{year}", "[ ] Pendiente"),
        ],
        "deudas_amigos": [],
        "deudas_entidades": [],
        "deudas_hacienda": [],
        "comida": [
            ("Semana 1", 0.0, 0.0, 0.0),
            ("Semana 2", 0.0, 0.0, 0.0),
            ("Semana 3", 0.0, 0.0, 0.0),
            ("Semana 4", 0.0, 0.0, 0.0),
        ],
        "glovo": [],
        "medicacion": [],
        "impuestos": [],
        "resumen": [],
    }


def compute_totals(data: dict) -> dict:
    ing_prev = round(sum(r[1] for r in data["ingresos"]), 2)
    ing_real = round(sum(r[2] for r in data["ingresos"]), 2)

    susc_prev = round(sum(r[1] for r in data["suscripciones"]), 2)
    hogar_prev = round(sum(r[1] for r in data["hogar"]), 2)
    amigos_prev = round(sum(r[1] for r in data["deudas_amigos"]), 2)
    ent_prev = round(sum(r[1] for r in data["deudas_entidades"]), 2)
    hac_prev = round(sum(r[1] for r in data["deudas_hacienda"]), 2)
    deudas_prev = round(amigos_prev + ent_prev + hac_prev, 2)
    comida_prev = round(sum(r[1] for r in data["comida"]), 2)
    comida_real_sem = round(sum(r[2] for r in data["comida"]), 2)
    med_prev = round(sum(r[1] for r in data["medicacion"]), 2)
    imp_prev = round(sum(r[1] for r in data["impuestos"]), 2)

    # Si había tabla de resumen en el MD, respetamos sus importes reales por bloque
    res_map = {}
    for label, prev_v, real_v in data.get("resumen", []):
        low = label.lower()
        if "suscrip" in low:
            res_map["suscripciones"] = real_v
        elif "hogar" in low:
            res_map["hogar"] = real_v
        elif "deuda" in low:
            res_map["deudas"] = real_v
        elif "comida" in low:
            res_map["comida"] = real_v
        elif "medicac" in low or "salud" in low:
            res_map["medicacion"] = real_v
        elif "impuesto" in low or "autónomo" in low or "autonomo" in low:
            res_map["impuestos"] = real_v

    susc_real = res_map.get("suscripciones", round(sum(r[1] for r in data["suscripciones"] if "[x]" in r[3].lower()), 2))
    hogar_real = res_map.get("hogar", round(sum(r[1] for r in data["hogar"] if "[x]" in r[3].lower()), 2))
    deudas_real = res_map.get(
        "deudas",
        round(
            sum(r[1] for r in data["deudas_amigos"] if "[x]" in r[3].lower())
            + sum(r[1] for r in data["deudas_entidades"] if "[x]" in r[3].lower())
            + sum(r[1] for r in data["deudas_hacienda"] if "[x]" in r[5].lower()),
            2,
        ),
    )
    comida_real = res_map.get("comida", comida_real_sem)
    med_real = res_map.get("medicacion", round(sum(r[1] for r in data["medicacion"] if "[x]" in r[2].lower()), 2))
    imp_real = res_map.get("impuestos", round(sum(r[1] for r in data["impuestos"] if "[x]" in r[2].lower()), 2))

    gastos_prev = round(susc_prev + hogar_prev + deudas_prev + comida_prev + med_prev + imp_prev, 2)
    gastos_real = round(susc_real + hogar_real + deudas_real + comida_real + med_real + imp_real, 2)

    deuda_restante = round(
        sum(r[2] for r in data["deudas_amigos"])
        + sum(r[2] for r in data["deudas_entidades"])
        + sum(r[1] * r[2] for r in data["deudas_hacienda"]),
        2,
    )

    return {
        "ingresos_prev": ing_prev,
        "ingresos_real": ing_real,
        "suscripciones_prev": susc_prev,
        "suscripciones_real": susc_real,
        "hogar_prev": hogar_prev,
        "hogar_real": hogar_real,
        "deudas_amigos_prev": amigos_prev,
        "deudas_entidades_prev": ent_prev,
        "deudas_hacienda_prev": hac_prev,
        "deudas_prev": deudas_prev,
        "deudas_real": deudas_real,
        "deuda_restante": deuda_restante,
        "comida_prev": comida_prev,
        "comida_real": comida_real,
        "medicacion_prev": med_prev,
        "medicacion_real": med_real,
        "impuestos_prev": imp_prev,
        "impuestos_real": imp_real,
        "gastos_prev": gastos_prev,
        "gastos_real": gastos_real,
        "balance_prev": round(ing_prev - gastos_prev, 2),
        "balance_real": round(ing_real - gastos_real, 2),
    }


def generate_monthly_xlsx(xlsx_path: Path, data: dict) -> dict:
    totals = compute_totals(data)

    # Hoja 1: Resumen (TablaResumen)
    resumen_rows = [
        ["Bloque", "Previsto (€)", "Real (€)", "Diferencia (€)", "% s/Previsto"],
        [
            "1. Ingresos",
            totals["ingresos_prev"],
            totals["ingresos_real"],
            ("f", "C2-B2", round(totals["ingresos_real"] - totals["ingresos_prev"], 2)),
            100.0 if totals["ingresos_prev"] == 0 else round(totals["ingresos_real"] / totals["ingresos_prev"] * 100, 1),
        ],
        [
            "2. Suscripciones",
            totals["suscripciones_prev"],
            totals["suscripciones_real"],
            ("f", "B3-C3", round(totals["suscripciones_prev"] - totals["suscripciones_real"], 2)),
            round(totals["suscripciones_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "3. Hogar",
            totals["hogar_prev"],
            totals["hogar_real"],
            ("f", "B4-C4", round(totals["hogar_prev"] - totals["hogar_real"], 2)),
            round(totals["hogar_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "4. Deudas y Financiaciones",
            totals["deudas_prev"],
            totals["deudas_real"],
            ("f", "B5-C5", round(totals["deudas_prev"] - totals["deudas_real"], 2)),
            round(totals["deudas_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "5. Comida Semanal",
            totals["comida_prev"],
            totals["comida_real"],
            ("f", "B6-C6", round(totals["comida_prev"] - totals["comida_real"], 2)),
            round(totals["comida_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "6. Medicación y Salud",
            totals["medicacion_prev"],
            totals["medicacion_real"],
            ("f", "B7-C7", round(totals["medicacion_prev"] - totals["medicacion_real"], 2)),
            round(totals["medicacion_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "7. Impuestos y Autónomos",
            totals["impuestos_prev"],
            totals["impuestos_real"],
            ("f", "B8-C8", round(totals["impuestos_prev"] - totals["impuestos_real"], 2)),
            round(totals["impuestos_prev"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0,
        ],
        [
            "TOTAL GASTOS",
            ("f", "SUM(B3:B8)", totals["gastos_prev"]),
            ("f", "SUM(C3:C8)", totals["gastos_real"]),
            ("f", "B9-C9", round(totals["gastos_prev"] - totals["gastos_real"], 2)),
            100.0,
        ],
        [
            "BALANCE NETO",
            ("f", "B2-B9", totals["balance_prev"]),
            ("f", "C2-C9", totals["balance_real"]),
            ("f", "C10-B10", round(totals["balance_real"] - totals["balance_prev"], 2)),
            0.0,
        ],
    ]

    # Hoja 2: Gastos Fijos (Suscripciones + Hogar + Medicación + Impuestos)
    gastos_rows = [["Categoría", "Concepto", "Previsto (€)", "Vencimiento", "Estado"]]
    for s_name, s_price, s_date, s_st in data["suscripciones"]:
        gastos_rows.append(["Suscripciones", s_name, s_price, s_date, s_st])
    for h_name, h_price, h_date, h_st in data["hogar"]:
        gastos_rows.append(["Hogar", h_name, h_price, h_date, h_st])
    for m_name, m_price, m_st in data["medicacion"]:
        gastos_rows.append(["Salud", m_name, m_price, "Mensual", m_st])
    for i_name, i_price, i_st in data["impuestos"]:
        gastos_rows.append(["Impuestos", i_name, i_price, "Mensual", i_st])
    last_g = len(gastos_rows)
    total_fijos = round(totals["suscripciones_prev"] + totals["hogar_prev"] + totals["medicacion_prev"] + totals["impuestos_prev"], 2)
    gastos_rows.append(["TOTAL FIJOS", "", ("f", f"SUM(C2:C{last_g})", total_fijos), "", ""])

    # Hoja 3: Deudas
    deudas_rows = [["Tipo", "Acreedor / Modelo", "Cuota Mes (€)", "Deuda Restante (€)", "Turnos", "Estado"]]
    for a_name, a_cuota, a_rest, a_st in data["deudas_amigos"]:
        deudas_rows.append(["Amistades", a_name, a_cuota, a_rest, "-", a_st])
    for e_name, e_cuota, e_rest, e_st in data["deudas_entidades"]:
        deudas_rows.append(["Entidades", e_name, e_cuota, e_rest, "-", e_st])
    for h_mod, h_cuota, h_turnos, h_ini, h_fecha, h_st in data["deudas_hacienda"]:
        deudas_rows.append(["Hacienda", f"{h_mod} ({h_fecha})", h_cuota, round(h_cuota * h_turnos, 2), h_turnos, h_st])
    last_d = len(deudas_rows)
    deudas_rows.append([
        "TOTAL DEUDAS",
        "",
        ("f", f"SUM(C2:C{last_d})", totals["deudas_prev"]),
        ("f", f"SUM(D2:D{last_d})", totals["deuda_restante"]),
        "",
        "",
    ])

    # Hoja 4: Comida y Pedidos
    comida_rows = [["Semana / Pedido", "Presupuesto (€)", "Real Gastado (€)", "Diferencia (€)", "Detalle / Recibo"]]
    for idx, (sem, pres, real_g, _) in enumerate(data["comida"], start=2):
        comida_rows.append([
            sem,
            pres,
            real_g,
            ("f", f"B{idx}-C{idx}", round(pres - real_g, 2)),
            "Presupuesto semanal",
        ])
    last_c = len(comida_rows)
    comida_rows.append([
        "TOTAL COMIDA",
        ("f", f"SUM(B2:B{last_c})", totals["comida_prev"]),
        ("f", f"SUM(C2:C{last_c})", totals["comida_real"]),
        ("f", f"B{last_c+1}-C{last_c+1}", round(totals["comida_prev"] - totals["comida_real"], 2)),
        "",
    ])
    for fac, f_date, imp, rec, st in data.get("glovo", []):
        comida_rows.append([f"Glovo {f_date}", 0.0, imp, -imp, f"{fac} ({st})"])

    # Hoja 5: Ingresos
    ingresos_rows = [["Origen / Concepto", "Previsto (€)", "Real (€)", "Fecha Cobro", "Estado"]]
    for o_name, o_prev, o_real, o_date, o_st in data["ingresos"]:
        ingresos_rows.append([o_name, o_prev, o_real, o_date, o_st])
    last_i = len(ingresos_rows)
    ingresos_rows.append([
        "TOTAL INGRESOS",
        ("f", f"SUM(B2:B{last_i})", totals["ingresos_prev"]),
        ("f", f"SUM(C2:C{last_i})", totals["ingresos_real"]),
        "",
        "",
    ])

    sheets = [
        {"name": "Resumen", "rows": resumen_rows, "table_name": "TablaResumen"},
        {"name": "Gastos", "rows": gastos_rows, "table_name": "TablaGastos"},
        {"name": "Deudas", "rows": deudas_rows, "table_name": "TablaDeudas"},
        {"name": "Comida", "rows": comida_rows, "table_name": "TablaComida"},
        {"name": "Ingresos", "rows": ingresos_rows, "table_name": "TablaIngresos"},
    ]
    write_xlsx(xlsx_path, sheets)
    return totals


def build_excel_callout_for_monthly_md(year: int, month: int, totals: dict) -> str:
    ym = f"{year}-{month:02d}"
    rel_xlsx = f"finanzas/{year}/cuentas/{ym}.xlsx"
    pct_ejec = round(totals["gastos_real"] / totals["gastos_prev"] * 100, 1) if totals["gastos_prev"] else 0.0
    diff_gasto = round(totals["gastos_prev"] - totals["gastos_real"], 2)
    sign = "+" if diff_gasto >= 0 else ""
    return (
        f"<!-- EXCEL-SUMMARY:START -->\n"
        f"> [!TIP] 📊 **Libro Excel Vinculado (`xleak.nvim`)**\n"
        f"> - **Archivo Excel**: [[{rel_xlsx}|{ym}.xlsx]] *(abrir en Neovim: `:Xleak open {rel_xlsx}`)*\n"
        f"> - **Hojas del libro**: `Resumen` · `Gastos` · `Deudas` · `Comida` · `Ingresos`\n"
        f">\n"
        f"> | Indicador Excel (`Resumen`) | Previsto (€) | Real (€) | Desviación (€) | Ejecución |\n"
        f"> | :--- | :---: | :---: | :---: | :---: |\n"
        f"> | **Ingresos Totales** | {totals['ingresos_prev']:.2f} | {totals['ingresos_real']:.2f} | {totals['ingresos_real'] - totals['ingresos_prev']:+.2f} | - |\n"
        f"> | **Gastos Totales** | {totals['gastos_prev']:.2f} | {totals['gastos_real']:.2f} | {sign}{diff_gasto:.2f} | {pct_ejec:.1f}% |\n"
        f"> | **Deuda Viva Restante** | - | {totals['deuda_restante']:.2f} | - | Cuota: {totals['deudas_prev']:.2f} € |\n"
        f"> | **Balance Neto** | **{totals['balance_prev']:.2f}** | **{totals['balance_real']:.2f}** | **{totals['balance_real'] - totals['balance_prev']:+.2f}** | |\n"
        f"<!-- EXCEL-SUMMARY:END -->"
    )


def inject_excel_into_monthly_md(md_path: Path, year: int, month: int, totals: dict):
    ym = f"{year}-{month:02d}"
    rel_xlsx = f"finanzas/{year}/cuentas/{ym}.xlsx"
    content = md_path.read_text(encoding="utf-8")

    # 1. Asegurar `excel:` en el frontmatter YAML
    fm_match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)(.*)$", content, re.DOTALL)
    if fm_match:
        fm_head, fm_body, fm_tail, body = fm_match.groups()
        if "excel:" not in fm_body:
            fm_body = fm_body.rstrip() + f'\nexcel: "{rel_xlsx}"'
        else:
            fm_body = re.sub(r'^excel:.*$', f'excel: "{rel_xlsx}"', fm_body, flags=re.MULTILINE)
    else:
        body = content
        fm_head, fm_body, fm_tail = "", "", ""

    callout = build_excel_callout_for_monthly_md(year, month, totals)

    # 2. Insertar o actualizar el bloque EXCEL-SUMMARY justo después del callout de Navegación
    if "<!-- EXCEL-SUMMARY:START -->" in body:
        body = re.sub(
            r"<!-- EXCEL-SUMMARY:START -->.*?<!-- EXCEL-SUMMARY:END -->",
            callout,
            body,
            flags=re.DOTALL,
        )
    else:
        nav_pattern = re.compile(r"(> \[!INFO\] \*\*Navegación\*\*\r?\n> .*?\r?\n)", re.DOTALL)
        if nav_pattern.search(body):
            body = nav_pattern.sub(rf"\1\n{callout}\n", body, count=1)
        else:
            body = callout + "\n\n" + body

    new_content = f"{fm_head}{fm_body}{fm_tail}{body}" if fm_head else body
    md_path.write_text(new_content, encoding="utf-8")


def create_monthly_md_from_template(md_path: Path, year: int, month: int) -> Path:
    ym = f"{year}-{month:02d}"
    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)

    tpl_path = VAULT_PATH / "templates" / "plantilla-cuentas-mes.md"
    if tpl_path.is_file():
        tpl = tpl_path.read_text(encoding="utf-8")
        rendered = (
            tpl.replace("{{date}}", ym)
            .replace("{{year}}", str(year))
            .replace("{{month}}", f"{month:02d}")
            .replace("{{prev_year}}", str(prev_y))
            .replace("{{prev_month_file}}", f"{prev_y}-{prev_m:02d}")
            .replace("{{next_year}}", str(next_y))
            .replace("{{next_month_file}}", f"{next_y}-{next_m:02d}")
        )
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(rendered, encoding="utf-8")
    return md_path


def sync_month(year: int, month: int, create_if_missing: bool = False) -> dict:
    cuentas_dir = VAULT_PATH / "finanzas" / str(year) / "cuentas"
    cuentas_dir.mkdir(parents=True, exist_ok=True)
    ym = f"{year}-{month:02d}"
    md_path = cuentas_dir / f"{ym}.md"
    xlsx_path = cuentas_dir / f"{ym}.xlsx"

    if not md_path.is_file():
        if not create_if_missing:
            raise FileNotFoundError(f"No existe la nota mensual {md_path}")
        create_monthly_md_from_template(md_path, year, month)

    data = parse_monthly_md(md_path)
    if not any(data[k] for k in ("suscripciones", "hogar", "comida")):
        data = default_monthly_data(year, month)

    totals = generate_monthly_xlsx(xlsx_path, data)
    inject_excel_into_monthly_md(md_path, year, month, totals)
    return {
        "year": year,
        "month": month,
        "md_path": str(md_path),
        "xlsx_path": str(xlsx_path),
        "totals": totals,
    }


def sync_annual(year: int) -> dict:
    cuentas_dir = VAULT_PATH / "finanzas" / str(year) / "cuentas"
    annual_md = VAULT_PATH / "finanzas" / f"resumen-anual-{year}.md"
    annual_xlsx = VAULT_PATH / "finanzas" / f"resumen-anual-{year}.xlsx"

    consolidado_rows = [[
        "Mes", "Ingresos (€)", "Suscrip. (€)", "Hogar (€)", "Deudas (€)",
        "Comida (€)", "Salud (€)", "Impuestos (€)", "Total Gastos (€)", "Balance (€)", "Estado"
    ]]

    sum_cols = {k: 0.0 for k in ("ing", "susc", "hog", "deu", "com", "sal", "imp", "gas", "bal")}
    month_records = {}

    for m in range(1, 13):
        m_name = MONTH_NAMES_ES[m]
        ym = f"{year}-{m:02d}"
        md_file = cuentas_dir / f"{ym}.md"
        r_idx = m + 1
        if md_file.is_file():
            data = parse_monthly_md(md_file)
            tot = compute_totals(data)
            month_records[m] = tot
            ing = tot["ingresos_real"]
            susc = tot["suscripciones_prev"]
            hog = tot["hogar_prev"]
            deu = tot["deudas_prev"]
            com = tot["comida_prev"]
            sal = tot["medicacion_prev"]
            imp = tot["impuestos_prev"]
            gas = round(susc + hog + deu + com + sal + imp, 2)
            bal = round(ing - gas, 2)
            estado = "En curso"
        else:
            ing = susc = hog = deu = com = sal = imp = gas = bal = 0.0
            estado = "Sin abrir"

        sum_cols["ing"] += ing
        sum_cols["susc"] += susc
        sum_cols["hog"] += hog
        sum_cols["deu"] += deu
        sum_cols["com"] += com
        sum_cols["sal"] += sal
        sum_cols["imp"] += imp
        sum_cols["gas"] += gas
        sum_cols["bal"] += bal

        consolidado_rows.append([
            m_name,
            ing,
            susc,
            hog,
            deu,
            com,
            sal,
            imp,
            ("f", f"SUM(C{r_idx}:H{r_idx})", gas),
            ("f", f"B{r_idx}-I{r_idx}", bal),
            estado,
        ])

    consolidado_rows.append([
        "TOTAL ANUAL",
        ("f", "SUM(B2:B13)", round(sum_cols["ing"], 2)),
        ("f", "SUM(C2:C13)", round(sum_cols["susc"], 2)),
        ("f", "SUM(D2:D13)", round(sum_cols["hog"], 2)),
        ("f", "SUM(E2:E13)", round(sum_cols["deu"], 2)),
        ("f", "SUM(F2:F13)", round(sum_cols["com"], 2)),
        ("f", "SUM(G2:G13)", round(sum_cols["sal"], 2)),
        ("f", "SUM(H2:H13)", round(sum_cols["imp"], 2)),
        ("f", "SUM(I2:I13)", round(sum_cols["gas"], 2)),
        ("f", "SUM(J2:J13)", round(sum_cols["bal"], 2)),
        "Consolidado",
    ])

    write_xlsx(
        annual_xlsx,
        [{"name": "Consolidado", "rows": consolidado_rows, "table_name": "TablaAnual"}],
    )

    # Actualizar resumen-anual-YYYY.md si existe
    if annual_md.is_file():
        rel_xlsx = f"finanzas/resumen-anual-{year}.xlsx"
        content = annual_md.read_text(encoding="utf-8")
        fm_match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)(.*)$", content, re.DOTALL)
        if fm_match:
            fm_head, fm_body, fm_tail, body = fm_match.groups()
            if "excel:" not in fm_body:
                fm_body = fm_body.rstrip() + f'\nexcel: "{rel_xlsx}"'
            else:
                fm_body = re.sub(r'^excel:.*$', f'excel: "{rel_xlsx}"', fm_body, flags=re.MULTILINE)
        else:
            body = content
            fm_head = fm_body = fm_tail = ""

        callout = (
            f"<!-- EXCEL-SUMMARY:START -->\n"
            f"> [!TIP] 📊 **Libro Excel Consolidado Anual (`xleak.nvim`)**\n"
            f"> - **Archivo Excel**: [[{rel_xlsx}|resumen-anual-{year}.xlsx]] *(abrir en Neovim: `:Xleak open {rel_xlsx}`)*\n"
            f"> - **Meses contabilizados**: `{len(month_records)}/12` · **Gasto anual previsto acumulado**: `{sum_cols['gas']:.2f} €` · **Balance acumulado**: `{sum_cols['bal']:.2f} €`\n"
            f"<!-- EXCEL-SUMMARY:END -->"
        )

        # Reconstruir la tabla Markdown anual con todos los meses existentes
        table_lines = [
            "| Mes | Ingresos (€) | Suscrip. (€) | Hogar (€) | Deudas (€) | Comida (€) | Salud (€) | Impuestos (€) | Total Gastos (€) | Balance (€) | Nota / Excel |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]
        for m in range(1, 13):
            m_name = MONTH_NAMES_ES[m]
            ym = f"{year}-{m:02d}"
            if m in month_records:
                t = month_records[m]
                ing = t["ingresos_real"]
                susc = t["suscripciones_prev"]
                hog = t["hogar_prev"]
                deu = t["deudas_prev"]
                com = t["comida_prev"]
                sal = t["medicacion_prev"]
                imp = t["impuestos_prev"]
                gas = t["gastos_prev"]
                bal = round(ing - gas, 2)
                links_cell = f"[[finanzas/{year}/cuentas/{ym}\\|MD]] · [[finanzas/{year}/cuentas/{ym}.xlsx\\|XLSX]]"
                table_lines.append(
                    f"| **{m_name}** | {ing:.2f} | {susc:.2f} | {hog:.2f} | {deu:.2f} | {com:.2f} | {sal:.2f} | {imp:.2f} | **{gas:.2f}** | **{bal:.2f}** | {links_cell} |"
                )
            else:
                table_lines.append(
                    f"| {m_name} | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | - |"
                )
        table_lines.append(
            f"| **TOTAL ANUAL** | **{sum_cols['ing']:.2f}** | **{sum_cols['susc']:.2f}** | **{sum_cols['hog']:.2f}** | **{sum_cols['deu']:.2f}** | **{sum_cols['com']:.2f}** | **{sum_cols['sal']:.2f}** | **{sum_cols['imp']:.2f}** | **{sum_cols['gas']:.2f}** | **{sum_cols['bal']:.2f}** | 🏁 |"
        )

        new_body = (
            f"# 📈 Resumen Financiero Anual {year}\n\n"
            f"> [!SUMMARY] **Consolidado de Finanzas Personales**\n\n"
            f"{callout}\n\n"
            + "\n".join(table_lines)
            + "\n"
        )
        # Asegurar que links del frontmatter incluyan todos los meses existentes
        for m in sorted(month_records.keys()):
            ym = f"{year}-{m:02d}"
            link_str = f"[[finanzas/{year}/cuentas/{ym}|Cuentas {ym}]]"
            if link_str not in fm_body:
                fm_body = fm_body.rstrip() + f'\n  - "{link_str}"'

        annual_md.write_text(f"{fm_head}{fm_body}{fm_tail}\n{new_body}", encoding="utf-8")

    return {
        "year": year,
        "md_path": str(annual_md),
        "xlsx_path": str(annual_xlsx),
        "months_synced": sorted(month_records.keys()),
        "total_gastos": round(sum_cols["gas"], 2),
    }


def sync_deudas() -> dict | None:
    deudas_md = VAULT_PATH / "finanzas" / "deudas-actuales.md"
    if not deudas_md.is_file():
        return None
    deudas_xlsx = VAULT_PATH / "finanzas" / "deudas-actuales.xlsx"
    text = deudas_md.read_text(encoding="utf-8")
    tables = extract_markdown_tables_by_heading(text)

    rows = [["Categoría", "Acreedor", "Importe Restante (€)"]]
    total = 0.0
    subtotals = {}
    for heading, t_rows in tables.items():
        for r in t_rows[1:]:
            if len(r) >= 2 and "subtotal" not in r[0].lower():
                raw_val = str(r[1]).strip()
                imp = parse_num(raw_val)
                total += imp
                subtotals[heading] = round(subtotals.get(heading, 0.0) + imp, 2)
                parts = [p.strip() for p in raw_val.split("+") if p.strip()] if "+" in raw_val else []
                if len(parts) > 1:
                    formula_terms = [
                        f"{int(v)}" if (v := parse_num(p)).is_integer() else f"{v:.2f}"
                        for p in parts
                    ]
                    cell_val = ("f", "+".join(formula_terms), imp)
                else:
                    cell_val = imp
                rows.append([heading, r[0], cell_val])
    last_r = len(rows)
    rows.append(["TOTAL DEUDA", "", ("f", f"SUM(C2:C{last_r})", round(total, 2))])

    write_xlsx(deudas_xlsx, [{"name": "Deudas", "rows": rows, "table_name": "TablaDeudasActuales"}])

    rel_xlsx = "finanzas/deudas-actuales.xlsx"
    fm_match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)(.*)$", text, re.DOTALL)
    if fm_match:
        fm_head, fm_body, fm_tail, body = fm_match.groups()
        if "excel:" not in fm_body:
            fm_body = fm_body.rstrip() + f'\nexcel: "{rel_xlsx}"'
        if "total_deuda:" in fm_body:
            fm_body = re.sub(r"^total_deuda:.*$", f"total_deuda: {total:.2f}", fm_body, flags=re.MULTILINE)
        sub_str = " · ".join(f"**{k}**: `{v:.2f} €`" for k, v in subtotals.items())
        sub_line = f"> - **Desglose por bloque**: {sub_str}\n" if sub_str else ""
        callout = (
            f"<!-- EXCEL-SUMMARY:START -->\n"
            f"> [!TIP] 📊 **Libro Excel Vinculado (`xleak.nvim`)**\n"
            f"> - **Archivo Excel**: [[{rel_xlsx}|deudas-actuales.xlsx]] *(abrir en Neovim: `:Xleak open {rel_xlsx}`)*\n"
            f"{sub_line}"
            f"> - **Deuda Total Consolidada**: `{total:.2f} €`\n"
            f"<!-- EXCEL-SUMMARY:END -->"
        )
        if "<!-- EXCEL-SUMMARY:START -->" in body:
            body = re.sub(
                r"<!-- EXCEL-SUMMARY:START -->.*?<!-- EXCEL-SUMMARY:END -->",
                callout,
                body,
                flags=re.DOTALL,
            )
        else:
            body = re.sub(r"(# .+\r?\n)", rf"\1\n{callout}\n", body, count=1)
        deudas_md.write_text(f"{fm_head}{fm_body}{fm_tail}{body}", encoding="utf-8")

    return {"md_path": str(deudas_md), "xlsx_path": str(deudas_xlsx), "total": round(total, 2)}


def sync_all(year: int | None = None) -> list:
    fin_dir = VAULT_PATH / "finanzas"
    results = []
    years = [year] if year else sorted(
        int(p.name) for p in fin_dir.iterdir() if p.is_dir() and p.name.isdigit()
    )
    for y in years:
        cuentas_dir = fin_dir / str(y) / "cuentas"
        if cuentas_dir.is_dir():
            for md_file in sorted(cuentas_dir.glob(f"{y}-*.md")):
                m_match = re.match(rf"^{y}-(\d{{2}})\.md$", md_file.name)
                if m_match:
                    m = int(m_match.group(1))
                    results.append(sync_month(y, m, create_if_missing=False))
        results.append(sync_annual(y))
    d_res = sync_deudas()
    if d_res:
        results.append(d_res)
    return results


def main():
    parser = argparse.ArgumentParser(description="Genera y sincroniza los Excel (.xlsx) y resúmenes (.md) de finanzas")
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_sync = sub.add_parser("sync", help="Sincroniza todas las notas de finanzas o un mes concreto")
    p_sync.add_argument("--year", type=int, default=None, help="Año (ej. 2026)")
    p_sync.add_argument("--month", type=int, default=None, help="Mes (1-12)")
    p_sync.add_argument("--create", action="store_true", help="Crear la nota mensual si no existe")

    args = parser.parse_args()
    if args.cmd == "sync" and args.month:
        y = args.year or date.today().year
        res = sync_month(y, args.month, create_if_missing=args.create)
        sync_annual(y)
        print(f"Sincronizado {y}-{args.month:02d}:")
        print(f"  MD:   {res['md_path']}")
        print(f"  XLSX: {res['xlsx_path']}")
    else:
        results = sync_all(getattr(args, "year", None))
        for r in results:
            print(f"OK  {r.get('xlsx_path')}  <-  {r.get('md_path')}")


if __name__ == "__main__":
    main()
