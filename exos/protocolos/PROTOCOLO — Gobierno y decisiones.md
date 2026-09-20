---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, gobierno, decisiones]
---

# PROTOCOLO — Gobierno y decisiones

## Qué resuelve

Mantiene una jerarquía de fuentes entendible y evita que un cambio irreversible nazca de
una suposición. Los agentes ejecutan y recomiendan; la persona propietaria del proyecto
decide el alcance, el dinero, la publicación, los permisos y cualquier punto de no retorno.

## Archivos que usa

- `AGENTS.md`: reglas globales y orden de autoridad.
- `CLAUDE.md`: ritual de apertura, trabajo y cierre de sesión.
- `exos/ESTANDARES.md`: formatos, estados y ubicación de cada artefacto.
- `exos/CONGELADO.md`: zonas estables que no cambian sin autorización visible.
- `mi-vida/decisions/PLANTILLA-decision.md`: registro de decisiones con consecuencias.
- `mi-vida/hot.md`: estado breve que cambia lo que hay que hacer ahora.

## Flujo

1. Leer primero `AGENTS.md`, después `CLAUDE.md` y las fuentes específicas del trabajo.
2. Ante una contradicción, aplicar la fuente de mayor autoridad y registrar la
   discrepancia; una conversación no sustituye una fuente versionada.
3. Clasificar el cambio por reversibilidad y radio de impacto.
4. Si afecta a permisos, dinero, publicación, datos, arquitectura o varias áreas,
   preparar un breve con impacto, alternativas, reversibilidad, recomendación y piloto.
5. Esperar la decisión explícita de la persona propietaria antes de cruzar el punto de no
   retorno.
6. Registrar la decisión con la plantilla, ejecutar el cambio mínimo y reconciliar las
   fuentes que hayan quedado desfasadas.
7. Dejar en `mi-vida/hot.md` solo el estado que condiciona la siguiente sesión.

## Fallos que bloquean

- La contradicción entre dos fuentes sigue sin resolverse.
- Falta autorización humana para una acción irreversible o externa.
- Un cambio con consecuencias no tiene registro de decisión.
- Se pretende modificar una zona congelada sin desbloqueo consciente y trazable.
- La salida afirma estar verificada sin mostrar la prueba reciente.

## Prueba

Ejecutar `python3 exos/scripts/validar_vault.py`. Para una decisión transversal,
comprobar además que existe un documento basado en
`mi-vida/decisions/PLANTILLA-decision.md`, que identifica a la persona que aprobó el
cambio y que las rutas afectadas coinciden con el alcance declarado.
