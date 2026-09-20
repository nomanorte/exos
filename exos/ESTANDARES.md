# ESTANDARES — Formatos y naming del cerebro

> Doctrina de formatos. La cambia solo el humano. Todo `.md` nuevo la cumple.

## Frontmatter mínimo de cualquier documento

```yaml
---
tipo: conocimiento | protocolo | proyecto | tarea | plantilla | propuesta | captura | decision
estado: activo | borrador | en-revision | archivo
fecha: AAAA-MM-DD
tags: [dos, o, tres]
---
```

## Tareas (`mi-vida/tareas/TASK-NNN-slug.md`)

```yaml
---
id: TASK-NNN
tipo: tarea
estado: pendiente | en-curso | en-revision | bloqueada | completada
asignado: humano | <agente>
prioridad: absoluta | alta | media | baja
creado: AAAA-MM-DD
actualizado: AAAA-MM-DD          # SIEMPRE al día en cada commit que la toque
next_action: "el paso exacto siguiente; si es del humano: 'humano: …'"
fecha_limite: AAAA-MM-DD          # la da el humano; nunca relativa ("mañana" NO)
---
```

- IDs secuenciales: `ls` del directorio antes de crear (regla anti-colisión).
- El **criterio de cierre** está en `AGENTS.md` y lo aplica el agente al actualizar la tarea.

## Experimentos (si usas laboratorio: `mi-vida/<tu-cajón>/EXP-NNN-slug/`)

`estado: semilla → definicion → ejecucion → extraccion → producto` (o `pausado`).
`ejecucion` exige diario de campo VIVO; preparar docs es `definicion`.

## Decisiones (`mi-vida/decisions/`)

Nombre: `_DECISION — AAAA-MM-DD — Titulo corto.md`. Frontmatter: fecha,
contexto, opciones, decision. Cuerpo: consecuencias y qué supersede.

## Sesiones (`mi-vida/sesiones/`)

Nombre: `AAAA-MM-DD-<agente>-<tema>.md`. Se escribe INCREMENTALMENTE durante la
sesión, por bloques.

## Naming general
- Documentos de sistema: `TIPO — Titulo.md` (`CONOCIMIENTO — …`, `PROTOCOLO — …`, `SPEC — …`, `PLAN — …`).
- Carpetas numeradas: `NN-Nombre-Con-Guiones`.
- Fechas SIEMPRE absolutas.

## §6 Mapa de propagación (auditoría de consistencia)
Cuando cambies algo estructural, revisa en cadena: este archivo → `AGENTS.md` →
`CLAUDE.md` → READMEs de zona → plantillas → tareas activas que lo referencien.
No dejes documentos apuntando a lo viejo.
