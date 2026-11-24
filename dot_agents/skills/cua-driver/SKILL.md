---
name: cua-driver
description: |
  Opera aplicaciones GUI nativas en macOS, Windows y Linux via cua-driver CLI o MCP.
  Herramientas: cua-driver, snapshots, element_token, run_steps, verify_state.
  No usar para: APIs de aplicacion cuando el usuario pide GUI-only, escaladas no autorizadas, instalar software solo para hacer una receta funcionar.
version: 0.38.0
metadata:
  openclaw:
    requires:
      bins:
        - cua-driver
    homepage: https://cua.ai/docs/cua-driver
---

# cua-driver

Opera un objetivo exacto, observalo de forma precisa, actua por elemento y verifica el postcondicion del usuario en checkpoints.

**Carga SOLO el archivo de `references/` necesario para tu tarea y SO** (en Linux no leas `MACOS.md` ni `WINDOWS.md`).

## Reglas globales

1. Selecciona el objetivo exacto en cada accion.
2. Observa antes de actuar y verifica el resultado en checkpoints.
3. Usa los tokens devueltos, nunca indices inventados.
4. No infieras pixeles de una imagen ausente o de una ventana diferente.
5. Manten un solo controlador para un escritorio compartido.
6. Los prompts de permisos del usuario/sistema le pertenecen al usuario; solo aprueba los de Cua Driver en macOS si el propietario lo autorizo explicitamente.

## Enrutamiento

| Tarea | Archivo |
| --- | --- |
| Bucle eficiente: observar, actuar, verificar | [references/WORKFLOW.md](references/WORKFLOW.md) |
| Instalacion, CLI/MCP, sesiones, autorizacion | [references/RUNTIME.md](references/RUNTIME.md) |
| Guia de macOS | [references/MACOS.md](references/MACOS.md) |
| Guia de Linux | [references/LINUX.md](references/LINUX.md) |
| Guia de Windows | [references/WINDOWS.md](references/WINDOWS.md) |
| Automatizacion de navegador | [references/BROWSER.md](references/BROWSER.md) |
| Grabacion de sesiones | [references/RECORDING.md](references/RECORDING.md) |
| Parseo de regiones visuales | [references/VISUAL.md](references/VISUAL.md) |
| Integracion host-app embebida | [references/EMBEDDING.md](references/EMBEDDING.md) |
| Instalacion y lectura recomendada | [references/README.md](references/README.md) |

## Failure map rapido

| Sintoma | Siguiente paso |
| --- | --- |
| Binario missing, daemon mismatch, tool desconocida | RUNTIME.md preflight |
| Token stale o ventana ambigua | Refresca list_windows / get_window_state |
| Arbol grande, truncado o lecturas repetidas | WORKFLOW.md observacion con limites |
| background_unavailable | No es un stop: actua por element_token |
| Pagina web en navegador | BROWSER.md |
| Cualquier refusal o unverifiable | WORKFLOW.md refusals-and-hints |

## Continuacion de actividad reciente

Cuando `history_status` y `history_query` esten disponibles y el usuario pida continuar, reanudar o recordar trabajo previo de Cua, llama a `history_status` primero. Si el historial es saludable, haz una `history_query` acotada. Trata los metadatos solo como pista y verifica el estado actual.
