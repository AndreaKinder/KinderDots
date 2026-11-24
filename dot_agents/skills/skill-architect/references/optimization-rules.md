# Reglas de optimizacion para skills

## Frontmatter

- Campos obligatorios: `name`, `description`.
- `description`: maximo 3 lineas.
  - Linea 1: accion principal y tecnologia.
  - Linea 2: archivos, herramientas o extensiones involucradas.
  - Linea 3: condiciones de exclusion (`No usar para: ...`).
- Prohibido lenguaje generico: "ayuda con", "gestiona", "facilita".

## Estructura

- `SKILL.md` ≤ 120 lineas.
- Tabla de enrutamiento con rutas relativas directas a `references/`.
- Cada `references/*.md` resuelve una tarea sin apuntar a otro `references/`.
- `scripts/` contiene solo utilidades deterministas (linters, generadores).
- `assets/` contiene plantillas listas para copiar.

## Estilo

- Verbos en imperativo directo.
- Oraciones cortas. Un concepto por linea.
- Usa ejemplos few-shot binarios: `// CORRECTO` / `// INCORRECTO`.
- Cero duplicacion: si una regla esta en `references/`, `SKILL.md` solo la enruta.

## Ejemplos

### Descripcion del frontmatter

```yaml
// CORRECTO
description: |
  Configura Nginx virtual hosts y SSL con Certbot.
  Archivos: nginx.conf, sites-available/*, systemd timers.
  No usar para: Apache, Caddy, frontend frameworks.

// INCORRECTO
description: |
  Esta skill te ayuda a gestionar servidores web. Puede
  usarse para muchas cosas relacionadas con la web y es util.
```

### Enlaces en SKILL.md

```markdown
// CORRECTO
[Ver reglas de shell](references/shell.md)

// INCORRECTO
Para mas detalles, consulta la seccion avanzada mas abajo.
```

### Instrucciones en references/

```markdown
// CORRECTO
Valida la sintaxis con `nginx -t`. Reinicia con `systemctl restart nginx`.

// INCORRECTO
Es importante que el agente valide la configuracion antes de reiniciar
el servidor, ya que un error podria causar problemas graves.
```

### Diseno para modelos locales

```markdown
// CORRECTO
1. Lee el archivo de configuracion.
2. Aplica el cambio exacto solicitado.
3. Ejecuta el comando de validacion.

// INCORRECTO
Primero, piensa en la mejor forma de abordar el problema. Luego,
considera las implicaciones del cambio antes de modificar nada.
```
