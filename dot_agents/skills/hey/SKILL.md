---
name: hey
description: |
  Interactua con HEY mediante el HEY CLI: email, contactos, calendario, tareas, habitos, time tracking y journal.
  Herramientas: hey CLI, --json, --jq, OAuth keyring.
  No usar para: otros servicios de email, automatizacion sin aprobacion del usuario, ejecutar hey auth login desatendido.
version: 1.0.0
invocable: true
argument-hint: "[command] [args...]"
---

# /hey - HEY Email Workflow Command

CLI for HEY: mailboxes, labels, collections, email threads, contacts, replies, compose, calendars, todos, habits, time tracking, and journal entries.

Usa el CLI instalado como referencia de comandos. Esta skill solo contiene reglas transversales; el catalogo oficial esta en la ayuda del binario.

## Reglas globales

1. Lee la ayuda del comando antes de ejecutar: `hey <group> <subcommand> --agent --help`.
2. Usa `--json`/`--jq` para output estructurado. Nunca pipes a `jq` externo.
3. No ejecutes `hey auth login` desatendido; solo para recuperacion interactiva.
4. No ejecutes `hey config trust-local` sin aprobacion explicita del usuario.
5. Nunca reenvies un mensaje con estado `not_delivered`.
6. Confirma las mutaciones de IDs; HEY no reporta IDs que no coincidan.

## Enrutamiento

Carga solo el archivo de `references/` necesario para la tarea actual.

| Tarea | Archivo |
| --- | --- |
| Discovery y lectura de ayuda de comandos | [references/discovery.md](references/discovery.md) |
| Output estructurado, IDs y paginacion | [references/output-and-ids.md](references/output-and-ids.md) |
| Enviar emails, drafts y bulk-reply | [references/sending.md](references/sending.md) |
| Escribir contenido Markdown/HTML y notas | [references/writing.md](references/writing.md) |
| Autenticacion, keyring y errores de auth | [references/authentication.md](references/authentication.md) |
