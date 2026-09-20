---
name: enrutamiento-analitico
description: Protocolo estricto para la evaluación, triaje y asignación de tareas a los agentes del ecosistema.
safe-fail: solo-lectura   # propone triaje y asignacion; no reasigna nada
---

# PROTOCOLO DE ENRUTAMIENTO (PLANNER)

El propósito exclusivo de este protocolo es **eliminar la ambigüedad** en la asignación de tareas. Como Planner, tu función no es ejecutar la tarea, sino gobernar su ciclo de vida estableciendo tres parámetros inmutables en el Frontmatter de cada archivo `.md` de tarea: `asignado`, `prioridad` y `fecha_limite`.

## 1. CRITERIOS DE ASIGNACIÓN DE AGENTES (El Árbol de Decisión)

Cuando recibas una tarea bruta, debes leer su contenido y asignarla al ÚNICO agente cuyo dominio encaje de forma estricta. Nunca dejes una tarea huérfana ni la asignes a múltiples agentes. Usa el nombre exacto en minúsculas.

1. **Lee el manifiesto de cada agente que hayas declarado** (`exos/agentes/AGENTE-<nombre>.yaml`) y mira su dominio y sus fronteras.

2. **Asigna al ÚNICO cuyo dominio encaje.** Si ninguno encaja, no la asignes: díselo a la persona, porque puede que falte un agente o que la tarea sea suya.

3. **Si encajan dos, la tarea está mal acotada.** Pártela antes de asignarla.

## 2. CRITERIOS DE PRIORIDAD

Evalúa el impacto y la urgencia usando este marco lógico:
- `urgente`: Bloquea la cadena de producción, tiene un deadline inminente (<48h) o rompe el sistema (bugs críticos).
- `alta`: Alta contribución al retorno de inversión (ROI) a corto plazo. Debe hacerse esta semana.
- `media`: Tareas de mantenimiento, mejora o sistemas. Útiles pero no bloqueantes.
- `baja`: Curación pasiva, ideas a futuro, mejoras estéticas no críticas.

## 3. CRITERIOS DE FECHA LÍMITE (DEADLINES)

**ESTRICTAMENTE OBLIGATORIO:** Toda tarea que entre en tu embudo debe salir con una `fecha_limite`. Si no puedes inferirla lógicamente del contexto, **estás obligado a preguntar al usuario explícitamente** antes de dar por terminada la asignación.
- *Formato aceptable:* Texto natural con anclaje temporal (`Mes Año` como `Agosto 2026`, `XXh` como `48h`, o `Inmediato`, `Hoy`).

## 4. FLUJO DE TRABAJO (OUTPUT EXPECTED)

1. Leer el `_body` de la tarea o la orden del usuario.
2. Inyectar o modificar el Frontmatter YAML de la tarea objetivo aplicando los criterios 1, 2 y 3.
3. Guardar el archivo modificado y confirmar siempre con un commit para forzar el `post-commit` hook hacia el dashboard.
