---
name: stack-portable
description: Empaqueta un objetivo, sus fuentes y un checkpoint para continuar trabajo en otro modelo, herramienta o sesión sin depender de sintaxis propietaria.
estado: activo
safe_fail: solo-lectura
safe-fail: solo-lectura
dependencias: []
---

# Preparar un paquete portable

## Entrada

- Objetivo o tarea portadora.
- Fuentes verificadas necesarias para ejecutarla.
- Estado actual y restricciones de acceso.

## Flujo

1. Leer el objetivo y localizar sus fuentes de verdad. No convertir borradores o supuestos en hechos.
2. Extraer solo el contexto necesario; omitir secretos, datos personales y material ajeno al objetivo.
3. Separar instrucciones, fuentes y estado para que el receptor pueda distinguir obligación de evidencia.
4. Redactar un paquete sin nombres de proveedor, comandos exclusivos de una interfaz ni identidad inyectada.
5. Cerrar con un checkpoint que declare qué está hecho, qué falta, cómo se verifica y cuál es la siguiente acción.

## Salida

```markdown
# OBJETIVO
[resultado observable]

# RESTRICCIONES
[límites y decisiones ya tomadas]

# FUENTES
## [fuente y estado]
[contenido necesario]

# CHECKPOINT
- Hecho:
- Pendiente:
- Verificación:
- Siguiente acción:
```

## Safe-fail

La skill es de solo lectura. Si una fuente falta o no es fiable, declararlo en el paquete; no completarla por inferencia ni modificar el repositorio de origen.
