---
tipo: protocolo
estado: activo
version: "1.0"
fecha: 2026-08-10
tags: [sistema, seguridad, calidad]
---

# PROTOCOLO — Seguridad y reglas comprobables

## Qué resuelve

Evita depender de que una persona o un agente recuerden reglas mecánicas. Lo detectable se
convierte en comprobador; lo evitable se elimina del perímetro; solo el criterio permanece
como prosa. Los secretos nunca viven en archivos versionados.

## Archivos que usa

- `exos/scripts/rotar_secreto.sh`: incorpora valores al gestor de credenciales sin escribirlos en el cerebro.
- `exos/scripts/secrets_loader.py`: carga valores durante el proceso que los necesita.
- `exos/scripts/auditar_secretos.py`: informa de nombres y ausencias sin imprimir valores.
- `exos/scripts/guardian_archivos.py`: detecta material sensible o basura peligrosa.
- `exos/scripts/guardian_doctrina.py`: comprueba reglas estructurales.
- `exos/scripts/validar_vault.py`: puerta de consistencia general.
- `exos/githooks/pre-commit`: bloquea antes de registrar una entrega insegura.

## Flujo

1. Ante una norma nueva, preguntar si puede hacerse imposible o detectarse con código.
2. Si puede hacerse imposible, sacar el dato o la capacidad peligrosa del repositorio. Si
   puede detectarse, implementar una sola comprobación reutilizada por la puerta de commit.
3. Mantener en archivos solo nombres de variables y ejemplos inertes. Los valores se
   obtienen del entorno del proceso o de un gestor de credenciales mediante adaptador.
4. Probar el comprobador contra un caso peligroso, uno normal y uno ya resuelto. Después
   provocar el bloqueo en el punto real de entrega.
5. Eliminar reglas duplicadas que el comprobador ya sustituye; una fuente mecánica y una
   explicación breve son suficientes.
6. La persona propietaria decide cualquier ampliación de permisos, acceso a credenciales o
   excepción. Un bypass nunca puede ser silencioso.

## Fallos que bloquean

- Aparece un valor secreto, una sesión o un dato privado dentro del repositorio.
- La norma es mecánica pero solo existe como recordatorio escrito.
- El comprobador no se ha visto fallar contra el caso que afirma bloquear.
- Hay dos listas de patrones que pueden divergir.
- Una excepción evita el guardián sin autorización ni rastro.
- La salida revela valores durante la auditoría.

## Prueba

Ejecutar `python3 exos/scripts/auditar_secretos.py` y
`python3 exos/scripts/validar_vault.py`. A continuación, en una copia temporal, crear
un secreto ficticio inequívoco e intentar registrarlo: `exos/githooks/pre-commit` debe
bloquearlo. Retirar el caso y repetir con un archivo normal: la puerta debe quedar verde.
