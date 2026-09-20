---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, skills, portabilidad]
---

# PROTOCOLO — Skills y portabilidad

## Qué resuelve

Convierte una capacidad repetible en instrucciones encontrables, seguras y transferibles
entre herramientas. La skill pertenece a un dominio o al núcleo compartido; no crea una
identidad nueva ni depende de memoria privada de un modelo.

## Archivos que usa

- `exos/agentes/skills/`: capacidades compartidas instaladas en la plantilla.
- `exos/agentes/skills/enrutamiento-analitico/SKILL.md`: selección de la capacidad adecuada.
- `exos/agentes/skills/arquitecto-de-prompts/SKILL.md`: preparación de instrucciones ejecutables.
- `exos/agentes/AGENTE-plantilla.yaml`: propietario y perímetro de las skills de dominio.
- `mi-vida/tareas/PLANTILLA-tarea.md`: objetivo, fuentes, restricciones y checkpoint portable.

## Flujo

1. Buscar primero en `exos/agentes/skills/` y en las skills del dominio declarado. Si
   una capacidad existente cubre el objetivo, ampliarla en vez de duplicarla.
2. Crear una skill solo a partir de un flujo ejecutado y documentado. Su SKILL.md declara
   nombre, descripción, disparadores, entradas, pasos, salidas, dependencias y safe-fail.
3. Sin safe-fail explícito, tratarla como solo lectura. Dinero, publicación, permisos,
   borrado y escrituras externas siempre vuelven a la persona propietaria.
4. Mantener rutas relativas, formatos abiertos y parámetros neutrales. Una marca de
   herramienta puede aparecer como adaptador opcional, nunca como requisito oculto.
5. Para cambiar de modelo, empaquetar objetivo, fuentes necesarias, restricciones,
   decisiones vigentes, estado y criterio de aceptación. No inyectar biografía ni datos
   que el trabajo no necesita.
6. El modelo receptor devuelve resultado, evidencia, incertidumbres y siguiente
   checkpoint; el sistema de archivos conserva el estado, no el historial del chat.

## Fallos que bloquean

- La skill duplica una capacidad ya existente o no tiene propietario.
- Falta SKILL.md, descripción, safe-fail, entrada o salida verificable.
- El paquete depende de una ruta personal, un proveedor obligatorio o contexto no incluido.
- Se transfieren secretos, datos privados o una identidad irrelevante para el objetivo.
- El receptor no puede saber qué significa terminar ni dónde devolver el resultado.

## Prueba

Elegir una tarea basada en `mi-vida/tareas/PLANTILLA-tarea.md`, enrutarla con
`exos/agentes/skills/enrutamiento-analitico/SKILL.md` y entregar el paquete a una
segunda herramienta sin contexto previo. La prueba pasa si esa herramienta identifica el
objetivo, las fuentes, las restricciones y el checkpoint sin pedir una ruta privada ni una
marca concreta.
