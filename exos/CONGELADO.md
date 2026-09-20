---
tipo: instrucciones
estado: activo
fecha: 2026-07-30
tags: [doctrina, guardian, congelado, seguridad]
---

# Zonas congeladas del cerebro

**Estos archivos NO los edita un agente por su cuenta.** Son la doctrina: las reglas, las
fronteras entre agentes, los estándares y el protocolo de sesión. Cambiar cualquiera de
ellos cambia el comportamiento de **todos** los agentes a la vez, así que es una decisión
de la persona, no una edición más.

## Por qué existe este archivo

La norma de `AGENTS.md` dice desde hace semanas que *«la doctrina la cambia solo la persona:
los agentes proponen, nunca aplican»*. Estaba escrita **dentro del propio archivo que
protegía**, y cualquier agente podía editarlo sin que nada lo impidiera. Era una cerradura
dibujada en la puerta.

La persona, 2026-07-30: *«debe ser una regla categórica, no algo que un agente se pueda saltar
o no leer o no considerar»*. Así que dejó de ser una norma escrita y pasó a ser un
candado que se comprueba solo.

## Procedimiento para tocar algo de aquí

1. **Propón el cambio a la persona y espera su sí explícito en la conversación.**
2. Commitea con el desbloqueo consciente: `UNLOCK=1 git commit ...`
3. **Registra la decisión** en `mi-vida/decisions/` con la fecha, qué cambia y por qué.

Sin el paso 1 no hay paso 2. El desbloqueo no es un trámite: es la marca de que un humano
decidió.

<!-- ZONAS-CONGELADAS -->
```
AGENTS.md
CLAUDE.md
exos/CONGELADO.md
exos/ESTANDARES.md
exos/scripts/validar_vault.py
exos/scripts/guardian_archivos.py
exos/scripts/guardian_doctrina.py
exos/scripts/crear_tarea.py
exos/scripts/aplicar_perfiles.py
exos/perfiles-agentes.yaml
exos/githooks/pre-commit
exos/githooks/post-commit
```
<!-- /ZONAS-CONGELADAS -->

> **06-sep-2026 · Se retiró de esta lista `exos/agentes/FRONTERAS — Dominios de agentes.md`.**
> Estaba declarado como zona congelada y **no existe en la entrega**: el producto viaja con un
> agente de ejemplo, no con el reparto de dominios de otro sistema. Un candado que protege un
> archivo inexistente no protege nada, y enseña a no fiarse de la lista.
>
> Las fronteras siguen siendo doctrina y siguen protegidas: viven en `AGENTS.md` —que sí está
> aquí— y en la ficha de cada agente.

## Por qué los scripts del guardián también están congelados

Porque si no, la forma más fácil de saltarse un candado es quitarlo. Un agente al que le
molesta una comprobación puede borrarla en una línea y seguir como si nada. Congelándolos,
quitar un candado cuesta exactamente lo mismo que cambiar una regla: el sí de la persona y una
decisión registrada.
