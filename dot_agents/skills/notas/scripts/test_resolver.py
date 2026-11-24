#!/usr/bin/env python3
"""
Unit tests for resolve_note.py
"""

import unittest
from datetime import date, timedelta
from resolve_note import resolve_date_expression, resolve_entity, classify_note_topic, parse_frontmatter, extract_tasks_from_markdown

class TestResolveNote(unittest.TestCase):
    def setUp(self):
        self.base_date = date(2026, 10, 1) # Thursday

    def test_date_expressions(self):
        self.assertEqual(resolve_date_expression("hoy", self.base_date), date(2026, 10, 1))
        self.assertEqual(resolve_date_expression("ayer", self.base_date), date(2026, 9, 30))
        self.assertEqual(resolve_date_expression("anteayer", self.base_date), date(2026, 9, 29))
        self.assertEqual(resolve_date_expression("mañana", self.base_date), date(2026, 10, 2))
        self.assertEqual(resolve_date_expression("pasado mañana", self.base_date), date(2026, 10, 3))
        self.assertEqual(resolve_date_expression("2026-09-15", self.base_date), date(2026, 9, 15))
        self.assertEqual(resolve_date_expression("15/09/2026", self.base_date), date(2026, 9, 15))
        self.assertEqual(resolve_date_expression("14 de septiembre", self.base_date), date(2026, 9, 14))

    def test_daily_entity_resolution(self):
        res = resolve_entity("nota diaria")
        self.assertEqual(res["type"], "daily_note")
        self.assertIn("journal", res["path"])

        res_ayer = resolve_entity("nota de ayer")
        self.assertEqual(res_ayer["type"], "daily_note")
        self.assertIn("journal", res_ayer["path"])

    def test_finance_entity_resolution(self):
        res = resolve_entity("cuentas de septiembre")
        self.assertEqual(res["type"], "finance_monthly")
        self.assertEqual(res["month"], 9)
        self.assertIn("finanzas", res["path"])

        res_annual = resolve_entity("resumen anual 2026")
        self.assertEqual(res_annual["type"], "finance_annual")
        self.assertEqual(res_annual["year"], 2026)

        res_recibos = resolve_entity("recibos 2026")
        self.assertEqual(res_recibos["type"], "finance_recibos")
        self.assertIn("recibos", res_recibos["path"])

        res_facturas = resolve_entity("facturas emitidas")
        self.assertEqual(res_facturas["type"], "finance_facturas")
        self.assertIn("facturas", res_facturas["path"])

    def test_classify(self):
        daily = classify_note_topic("Bitácora del día")
        self.assertEqual(daily["type"], "daily_note")

        finance = classify_note_topic("Gastos e ingresos de diciembre")
        self.assertEqual(finance["type"], "finance")
        self.assertIn("12.md", finance["filename"])

        project = classify_note_topic("Proyecto web-app fase 3")
        self.assertEqual(project["type"], "project")

        zettel = classify_note_topic("Arquitectura de microservicios en Go")
        self.assertEqual(zettel["type"], "zettelkasten")

    def test_extract_tasks_with_postponed(self):
        sample = """
## TODO
### Casa / Personal
- [ ] Comprar pan
- [x] Limpiar cocina
- [>] Ir al dentista ⏳ pospuesto a [[2026-10-02]]
"""
        tasks = extract_tasks_from_markdown(sample)
        self.assertEqual(len(tasks), 3)
        self.assertFalse(tasks[0]["completed"])
        self.assertFalse(tasks[0]["postponed"])
        self.assertTrue(tasks[1]["completed"])
        self.assertFalse(tasks[1]["postponed"])
        self.assertFalse(tasks[2]["completed"])
        self.assertTrue(tasks[2]["postponed"])

if __name__ == "__main__":
    unittest.main()
