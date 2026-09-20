---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, pilotos, integraciones]
---

# PROTOCOLO — Pilotos e integraciones

## Qué resuelve

Permite probar herramientas e integraciones sin convertir una hipótesis en infraestructura
permanente. La capacidad se conserva mediante un contrato portable; el proveedor es un
adaptador reemplazable. Un conector da acceso, pero no sustituye autorización ni aislamiento.

## Archivos que usa

- `mi-vida/tareas/PLANTILLA-tarea.md`: hipótesis, responsable y criterio de salida del piloto.
- `mi-vida/decisions/PLANTILLA-decision.md`: adopción, rechazo o retirada con consecuencias.
- `mi-vida/onboarding-estado.yaml`: capacidades y elecciones ya declaradas por el proyecto.
- `docs/INTEGRACIONES.md`: contratos de integración del repositorio web.
- `docs/ARQUITECTURA.md`: adaptadores y compromisos técnicos vigentes.
- `exos/scripts/auditar_secretos.py`: comprobación previa de credenciales.

## Flujo

1. Partir de una fricción observada y de la fase real del proyecto, no de una herramienta
   interesante. Definir qué trabajo desaparece si el piloto funciona.
2. Escribir en la tarea la hipótesis, alcance mínimo, datos de prueba, coste temporal,
   criterio de éxito, criterio de abandono, salida y fecha de revisión.
3. Comparar alternativas, reutilizar primero servicios disponibles y preferir una prueba
   reversible. La persona propietaria decide altas, dinero, permisos y producción.
4. Integrar contra un contrato propio descrito en `docs/INTEGRACIONES.md`. Configuración,
   autenticación y proveedor quedan detrás de un adaptador.
5. Si se usa un protocolo de conectividad entre modelos y herramientas, fijar versión,
   exponer el perímetro mínimo y mantener la autorización fuera del conector. Un pasillo no
   es una cerradura.
6. Ejecutar el conector en un entorno aislado, con un directorio de trabajo dedicado como
   único ámbito escribible. Montar las zonas sensibles y el resto del sistema en solo lectura;
   no entregar acceso de escritura a todo el repositorio por comodidad.
7. Ejecutar primero de forma manual, observar entradas, salidas y fallos, y pedir revisión
   independiente antes de automatizar.
8. Registrar adopción, rechazo o nueva iteración. Si se abandona, retirar credenciales,
   permisos, disparadores y configuración; conservar solo el aprendizaje reusable.

## Fallos que bloquean

- No existe fricción observada, criterio de éxito o plan de retirada.
- El piloto exige datos reales cuando bastan datos ficticios.
- La integración acopla la lógica del proyecto a un proveedor.
- Un conector se presenta como control de permisos.
- El piloto no está aislado o puede escribir fuera de su directorio de trabajo; las zonas
  sensibles no están montadas en solo lectura.
- Las credenciales aparecen en archivos, comandos documentados o resultados.
- Se automatiza antes de una pasada manual y una revisión independiente.

## Prueba

Ejecutar el piloto en un entorno temporal aislado con credenciales simuladas o de alcance
mínimo. Dejar escribible solo su directorio de trabajo y montar las zonas sensibles en solo
lectura; un intento de escritura fuera del perímetro debe fallar. Forzar éxito, fallo de
autenticación y retirada del proveedor. La prueba pasa si el contrato de
`docs/INTEGRACIONES.md` mantiene la misma interfaz, no quedan archivos secretos y
`python3 exos/scripts/auditar_secretos.py` termina sin revelar valores.
