# Distribución y actualizaciones de EXOS

## Qué repositorio manda

Este repositorio contiene el código distribuible de EXOS. El repositorio público `exos`
es la fuente de verdad de lo publicado: cada versión oficial, sus notas y su historial de releases. El cerebro donde se
incubó conserva la fábrica, el criterio y los aprendizajes, pero no sustituye el historial
del producto. Los programas especializados pueden vivir en repositorios independientes;
no se incluyen ni se prometen aquí.

## Qué se instala y qué es personal

Una versión de EXOS es un **tag** con notas de release. Quien lo usa puede copiarla a un
proyecto personal privado, que tendrá su propio historial. El repositorio público no recibe
datos personales. No se recomienda usar el clon público como proyecto personal ni hacer
`git pull` desde él sobre `mi-vida/`.

Al actualizar un proyecto personal, el agente propone una rama y un Pull Request en **ese
proyecto privado**. Compara la versión instalada con el nuevo tag y traslada, revisando
las diferencias, estos componentes del sistema:

- `exos/`, `AGENTS.md`, `CLAUDE.md` y `.github/workflows/`;
- archivos de raíz del producto que hayan cambiado y sean relevantes para el proyecto.

No reemplaza `mi-vida/`, `modulos/`, `_secrets/` ni archivos personales añadidos. El
`mi-vida/` de este repositorio es solo una **semilla** para una instalación nueva. No se
vuelve a copiar en una actualización. Antes de integrar el PR se ejecutan los guardianes
y se revisan los cambios de doctrina con la persona dueña del proyecto. No hay
actualizaciones automáticas ni `push` directo al proyecto personal.

## Cómo evoluciona el repositorio público

**Este repositorio se actualiza solo por releases oficiales.** Cada versión es un tag con
notas de compatibilidad y migración, y reúne una **tanda** de cambios ya probados en conjunto.
Entre versiones `main` no recibe cambios sueltos.

Issues y Pull Requests permanecen abiertos para errores, propuestas y contribuciones: se leen,
se responden y, si procede, se integran en la **siguiente release**, no en el momento. No se
fuerza un calendario. La única excepción es un fallo de seguridad o una fuga de datos, que
sale como release de parche (`v1.0.1`) sin esperar a la tanda.

Los usuarios instalan un tag publicado, nunca un commit de `main`. La versión que entra por
release llega a `main` por Pull Request, con las comprobaciones exigidas.

`main` debe tener una regla de protección: Pull Request obligatorio, comprobaciones
requeridas y conversaciones resueltas. No se debe confundir la CI verde con una
protección de rama activa.

La automatización llamada «Centinela de main» está destinada a **copias personales**:
rescata cambios que fallen en un repo privado sin protección de rama. Nunca debe reescribir
`main` de `nomanorte/exos`.
