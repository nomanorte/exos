---
fecha: 2026-09-24
contexto: crear_tarea.py --anadir-a añadía otra casilla idéntica al repetir una llamada, incluso si la primera ya estaba completada, y modificaba la fecha de actualización sin trabajo nuevo. Un agente que reintenta tras un corte lo provoca.
opciones:
  - Dejarlo como estaba y avisar en la documentación.
  - Reconocer la misma casilla (pendiente o completada) y no escribir nada.
decision: Reconocer la casilla ya presente y no escribir el archivo. Decidido por el mantenedor para la release v1.1.
---

# _DECISION — 2026-09-24 — Reintentar un checkpoint no lo duplica

## Consecuencias
`exos/scripts/crear_tarea.py` (zona congelada) cambia: un checkpoint con el mismo texto que otro ya presente
—pendiente o completado— produce un aviso y no modifica la tarea. Un checkpoint distinto se añade como siempre.
La comparación es exacta: no se infiere que dos redacciones distintas sean lo mismo. Sale en la release v1.1.
