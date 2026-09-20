---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, agentes, permisos]
---

# PROTOCOLO — Agentes y permisos

## Qué resuelve

Separa responsabilidad, acceso y capacidad para que varios agentes colaboren sin pisarse.
El perímetro documentado orienta el trabajo; la seguridad real se apoya en el aislamiento,
la ausencia de secretos en los repositorios y la aprobación humana de permisos sensibles.

## Archivos que usa

- `exos/agentes/AGENTE-plantilla.yaml`: molde de un dominio con misión y fronteras.
- `exos/perfiles-agentes.yaml`: fuente única del acceso declarado.
- `exos/scripts/aplicar_perfiles.py`: traduce los perfiles a herramientas compatibles.
- `exos/scripts/validar_vault.py`: valida forma, roster y referencias del cerebro.
- `AGENTS.md`: autoridad, reglas de escalado y límites comunes.

## Flujo

1. Crear un agente solo cuando exista un dominio real que necesite propietario; una tarea,
   una skill o un script no son agentes.
2. Partir de `exos/agentes/AGENTE-plantilla.yaml` y declarar misión, lectura, escritura,
   prohibiciones, entradas, salidas y escalado.
3. Añadir su perímetro a `exos/perfiles-agentes.yaml` sin duplicar la misión.
4. Mantener tres zonas: núcleo compartido de lectura, dominio propio de escritura y zona
   común de coordinación. Denegar dominios ajenos y material sensible.
5. Simular la traducción con `exos/scripts/aplicar_perfiles.py` antes de aplicarla.
6. La persona propietaria aprueba cualquier ampliación de permisos, acceso externo o
   creación de un agente. La aplicación mecánica puede delegarse después de esa decisión.
7. Validar el cerebro y comprobar con una operación inocua que el dominio puede escribir
   donde debe y falla fuera de su carril.

## Fallos que bloquean

- El nuevo agente no tiene dominio o responsabilidad diferenciada.
- El manifiesto y `exos/perfiles-agentes.yaml` se contradicen.
- El perfil permite secretos, rutas ajenas o una raíz más amplia de la necesaria.
- Se amplía un permiso sin decisión de la persona propietaria.
- La herramienta no puede imponer el límite y esa limitación se presenta como seguridad.

## Prueba

Ejecutar primero una simulación con
`python3 exos/scripts/aplicar_perfiles.py --herramienta <adaptador-disponible>` y después
`python3 exos/scripts/validar_vault.py`. La revisión debe mostrar el mismo dominio en el
manifiesto y en el perfil, sin ampliar rutas no declaradas.
