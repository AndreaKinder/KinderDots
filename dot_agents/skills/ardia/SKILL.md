---
name: ardia
description: |
  Opera el navegador Ardia del usuario (tabs, logins, cookies) via shell con `ardia browse` y `ardia call`.
  Herramientas: ardia CLI, agent-browser, batch, script, notes.
  No usar para: tareas donde no importen logins del usuario, scraping sin pagina abierta, acciones destructivas sin confirmar.
allowed-tools: Bash(ardia:*)
---

# Ardia

`ardia browse` ejecuta comandos de agent-browser en el navegador Ardia del usuario, con sus tabs y logins.

## Reglas globales

1. Cada llamada relee toda la salida anterior: haz el maximo por llamada, imprime el minimo.
2. Trabaja en la tab del usuario cuando la peticion sea sobre su pagina.
3. Pregunta antes de pasos no solicitados: enviar, publicar, comprar, borrar.
4. No toques cookies, passwords ni storage salvo que te lo pidan.
5. Cada valor debe provenir de la salida de esta sesion; nunca retypes filas ni rellenes huecos de memoria.

## Enrutamiento

Carga un archivo de `references/` solo si la tarea lo requiere (para acciones basicas basta este `SKILL.md`).

| Tarea | Archivo |
| --- | --- |
| Start, lectura y acciones basicas | Este SKILL.md |
| Bucles y scripts | [references/script.md](references/script.md) |
| Flujos guardados | [references/flows.md](references/flows.md) |
| Automatizacion avanzada (tabs, eventos, hooks) | [references/automation.md](references/automation.md) |
| Notas de sitio y userscripts | [references/userscripts.md](references/userscripts.md) |
| Configuracion y temas | [references/config.md](references/config.md) |
| Reportes diarios | [references/daily-reports.md](references/daily-reports.md) |
| Troubleshooting y referencias rapidas | [references/troubleshooting.md](references/troubleshooting.md) |
| Metodos, ayuda y DevTools | [references/look-it-up.md](references/look-it-up.md) |
| Validar esta skill | [scripts/lint_skill.py](scripts/lint_skill.py) |

## Start

```sh
ardia browse open <url> --read
ardia browse batch "tab active" "snapshot -i"
```

## Read

- Texto de la pagina: `ardia browse read` o `read -s <sel>`.
- Multiples paginas: `read <url> <url> …` o `read --links /p/ -s table.specs`.
- Datos embebidos: `read --data`, `network requests --reload --type xhr,fetch`.
- Listas largas: `read --scroll` o `-s <list> --match <text>`.

## Act

```sh
ardia browse batch --bail <<'EOF'
click @e10
fill @e11 "Ana Ruiz"
select @e12 Clients
click @e30
notes append "Add contact: Group defaults to Personal; Save contact saves"
EOF
```

- Agrupa todos los pasos posibles en un `batch`.
- `fill` tipos, fechas, tiempos, colores y rangos; `select` maneja dropdowns.
- `open <url>` mueve a background tab; `tab t<N>` vuelve.

## Loops

Para pasos repetitivos usa `script`:

```sh
ardia browse script <<'EOF'
const rows = [];
for (const url of await page.links('/p/')) {
  await page.goto(url);
  rows.push({ name: await page.text('h1'), price: await page.text('.price') });
}
return rows;
EOF
```

- API: `page.goto/click/fill/select/press/text(sel)/links(pat)/snapshot('-i')`, `read(urls)`, `browse('cmd', …)`.
- Guarda datos con `--out <file>`. No retypes datos en codigo.

## Finish

- Verifica el total, cada pagina, tab, categoria y `Load more`.
- Responde en la forma solicitada; los archivos que nombres deben existir.
- Marca `unverified` lo que no provenga de la salida.

## Memory

`ardia notes` guarda una nota corta por sitio.

- Escribe en la ultima accion (`notes append "…"`).
- Incluye ubicaciones, formatos, defaults y pitfalls. Nunca secrets ni datos personales.
