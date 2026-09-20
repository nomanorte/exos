---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, tareas, traspasos]
---

# PROTOCOLO — Trabajo y traspasos

## Qué resuelve

Conserva un objetivo único, una siguiente acción visible y una señal de retorno cuando el
trabajo cruza sesiones, agentes o repositorios. Alcanzar un archivo no equivale a enterarse:
todo traspaso declara dónde se deja, cómo se detecta y cómo vuelve el cierre.

## Archivos que usa

- `mi-vida/tareas/PLANTILLA-tarea.md`: contrato de objetivo, responsable y siguiente acción.
- `exos/scripts/crear_tarea.py`: crea sin duplicar objetivos activos.
- `exos/scripts/status.py`: muestra la cola del agente que inicia sesión.
- `exos/scripts/archivar_tareas.py`: retira tareas cerradas sin perder historial.
- `mi-vida/hot.md`: continuidad breve entre sesiones.
- `mi-vida/Triage/`: bandeja temporal de material a clasificar.
- `scripts/mis-encargos.sh`: detecta encargos pendientes en el repositorio web.

## Flujo

1. Consultar `exos/scripts/status.py` al iniciar y trabajar sobre la tarea portadora del
   objetivo; los pasos viven como checkpoints dentro de esa tarea.
2. Crear trabajo nuevo solo con `exos/scripts/crear_tarea.py`; si el objetivo ya existe,
   ampliar la tarea existente.
3. Depositar material sin destino definitivo en `mi-vida/Triage/`, con origen, destino,
   estado y fecha. Procesarlo o retirarlo; la bandeja no es un archivo permanente.
4. Para un cruce de repositorios, dejar un único encargo en el repositorio donde se
   implementa. Debe declarar responsable, autor y tarea que cierra.
5. El receptor detecta el encargo con `scripts/mis-encargos.sh`, implementa sin duplicar el
   contrato y registra evidencia verificable.
6. Cerrar son dos gestos: completar el encargo y marcar el checkpoint de retorno en la
   tarea portadora.
7. Actualizar estado, siguiente acción y fecha. Archivar solo cuando no queda ningún paso;
   si queda una decisión humana, pasar a revisión y escribir la acción exacta.

## Fallos que bloquean

- Hay dos tareas activas para el mismo objetivo.
- El traspaso no declara lugar, mecanismo de detección o señal de retorno.
- El encargo y la tarea mantienen copias divergentes del mismo contrato.
- Un implementador se revisa a sí mismo o el cierre carece de evidencia reciente.
- La tarea figura cerrada con checkpoints pendientes o sin siguiente acción humana visible.
- `mi-vida/Triage/` conserva material sin responsable ni destino.

## Prueba

Ejecutar `python3 exos/scripts/status.py <agente-declarado>` y, en el repositorio web,
`sh scripts/mis-encargos.sh <agente-declarado>`. Para el caso de prueba, comprobar que el
encargo aparece antes de ejecutarlo y desaparece solo después de completar el encargo y el
checkpoint de la tarea. Terminar con `python3 exos/scripts/validar_vault.py`.
