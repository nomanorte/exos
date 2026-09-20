# EXOS

### Tu sistema operativo personal para trabajar con agentes de IA — en tu carpeta, sin depender de nadie.

Tus ideas, tus reglas y tu memoria viven en una carpeta que es **tuya**: la mueves, la copias
o la abandonas cuando quieras. Ningún SaaS de por medio.

![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-2e7d32?style=flat-square)
![Sin código](https://img.shields.io/badge/💡-sin%20saber%20programar-1565c0?style=flat-square)

---

## El problema

Trabajas con un agente de IA y pasa siempre lo mismo:

- **Cada sesión empieza de cero.** Le explicas otra vez lo que ya decidisteis ayer.
- **Lo que decidiste no está en ninguna parte.** Está en un chat que se perdió, y a la
  siguiente vuelve a proponerte lo que ya descartaste.
- **Rompe lo que funcionaba.** Toca un archivo que no debía y nadie se entera hasta que algo
  falla.
- **Tu información está repartida** entre veinte aplicaciones que no se hablan, y ninguna es
  tuya del todo.

No es que el agente sea malo. **Es que no tiene dónde apoyarse.**

## Qué hace EXOS

Le da ese sitio. Es una carpeta con reglas, memoria y comprobaciones para trabajar con
agentes que lean sus instrucciones. Las protecciones locales requieren activación al instalar.

- 🧠 **Se acuerda.** Lo que decides queda escrito en archivos, no en un chat.
- 🛡️ **No rompe lo que funciona.** Hay zonas protegidas que un agente no puede tocar solo.
- 🔑 **Tus secretos, fuera de los archivos.** Nada que se comparta lleva una clave dentro.
- 🔁 **Archivos portables.** Las instrucciones son Markdown; cada herramienta debe leerlas
  y respetarlas para que el recorrido funcione.
- 📋 **Sabe qué te toca.** Tareas que no se duplican y un parte de en qué andabas.
- ✅ **Se comprueba solo.** Ver «[Lo que se vigila a sí mismo](#lo-que-se-vigila-a-sí-mismo)».

## Instalar

### Opción A — con tu agente (recomendado, no necesitas saber programar)

Descarga una versión desde [Releases](https://github.com/nomanorte/exos/releases), ábrela con tu agente —Claude Code, Codex o el que uses— y escríbele
esto, tal cual:

```
inicia recorrido
```

Él comprueba qué te falta, te enseña el mapa y te pregunta por tu proyecto. De una cosa cada
vez.

> **¿Te contesta como un asistente cualquiera**, sin comprobar nada? Entonces no ha leído sus
> instrucciones, y **no es culpa tuya**. Escríbele:
> ```
> lee los archivos AGENTS.md y CLAUDE.md de este proyecto y haz lo que dicen
> ```

> **¿Y los guardianes, los enciende alguien?** Sí: **lo hace él**, en el primer paso del
> recorrido, y te lo dice cuando lo haya hecho. Tú no tienes que ejecutar nada.
>
> Vienen apagados en cada copia nueva —es cómo funciona git, no un olvido— y si nadie los
> enciende **no falla nada**: sencillamente no existirían, y nadie te lo diría. Por eso es lo
> primero que hace.

### Opción B — a mano (si ya programas)

```bash
bash exos/scripts/bootstrap.sh
```

Es lo mismo que hace él por ti en la Opción A: enciende los guardianes.

## Qué hay dentro

Tres carpetas, y de ahí sale todo:

| Carpeta | Qué es | ¿La editas tú? |
|---|---|---|
| **`exos/`** | El sistema: reglas, guardianes, scripts | **No.** Se actualiza junto con las instrucciones raíz |
| **`modulos/`** | Los programas que añadas | Solo añadiendo o quitando carpetas |
| **`mi-vida/`** | Lo tuyo: tareas, decisiones, tu registro | **Sí. Es tuya** |

**Lo tuyo vive en `mi-vida/` y en los módulos que añadas.** Las versiones nuevas de EXOS
incluyen `exos/`, `AGENTS.md`, `CLAUDE.md` y los guardianes de `.github/workflows/`.
Actualizar solo `exos/` deja reglas y código de versiones distintas. Consulta
[`DISTRIBUCION.md`](DISTRIBUCION.md) antes de incorporar una versión a tu proyecto.

> **¿Qué es un «programa» y por qué `modulos/` está vacío?**
>
> **No es nada que instales en tu ordenador.** No hay `.exe` ni `.dmg` ni nada que abrir: un
> programa aquí es **una carpeta con instrucciones** que le enseña a tu agente a hacer algo
> concreto y bien. La copias dentro de `modulos/`, se lo dices, y ya sabe hacerlo.
>
> Ejemplos de lo que puede hacer un programa: **tener siempre listo tu CV** adaptado a cada
> oferta · **montar y publicar la web** de tu negocio · **conseguir clientes** con contenido.
>
> **Empieza vacía a propósito**, y tu sistema funciona igual si nunca añades ninguno. Cada
> programa puede tener su propio repositorio y sus propias condiciones de acceso. No forma
> parte de este repositorio público hasta que se incorpore expresamente.

| Archivo | Para qué |
|---|---|
| [`MAPA — De qué va cada carpeta.html`](MAPA%20—%20De%20qué%20va%20cada%20carpeta.html) | Medio minuto, el primer día |
| [`AGENTS.md`](AGENTS.md) · [`CLAUDE.md`](CLAUDE.md) | **Para tu agente, no para ti.** Sus reglas |
| [`exos/CONGELADO.md`](exos/CONGELADO.md) | Lo que ningún agente cambia sin tu sí |
| [`mi-vida/hot.md`](mi-vida/hot.md) | En qué andabas. Lo mantiene él |

## Lo que se vigila a sí mismo

Esto no es una promesa: son comprobaciones que corren solas antes de cada guardado.

| Guardián | Qué impide |
|---|---|
| **Secretos** | Que una clave entre en un archivo que se comparte |
| **Zonas congeladas** | Que se cambie una regla sin tu sí explícito |
| **Registro** | Que un trabajo se cierre sin quedar anotado |
| **Referencias** | Que un documento cite un archivo que no existe |
| **Estructura** | Que aparezca una carpeta que rompa el reparto de arriba |

Si uno falla, el guardado **se para y te dice por qué**. No avisa después: impide antes.

## Dos reglas que no cambian

**Ninguna contraseña ni clave se escribe dentro de un archivo de este proyecto.** Nunca. Un
archivo se comparte, se sube sin querer y acaba en un zip — y un secreto filtrado no se
desfiltra, solo se cambia, y siempre tarde. Para eso está `_secrets/`, excluida de git desde
el primer día.

**Las reglas del sistema no las cambia un agente por su cuenta.** Están en
`exos/CONGELADO.md` y tocarlas exige tu sí y dejarlo escrito. Cambiar una regla cambia el
comportamiento de todos tus agentes a la vez: es una decisión tuya, no una edición más.

Y cuando te lo proponga, **tiene que dártelo masticado**. Nunca un «¿cambio esta regla?» a
secas, porque eso te devuelve a ti el trabajo de averiguar qué está en juego. Las tres cosas,
siempre:

| | Qué tiene que decirte |
|---|---|
| **Contexto** | Qué hace hoy esa regla y por qué existe |
| **Consecuencia** | Qué cambia si dices que sí — **y qué pasa si no se toca** |
| **Recomendación** | Cuál elegiría él **y por qué**, con la pega dicha, no escondida |

Si no puede escribirte las tres, es que no lo ha investigado. Pídeselas antes de decidir.

## Licencia

Apache 2.0. Ver [`LICENSE`](LICENSE).

## Colaborar y avisar de problemas

Las propuestas y los errores se reciben mediante [Issues](https://github.com/nomanorte/exos/issues) y Pull Requests.
Lee [`CONTRIBUTING.md`](CONTRIBUTING.md) antes de enviar cambios. Para una vulnerabilidad
o una posible filtración, **no abras un Issue público**: sigue [`SECURITY.md`](SECURITY.md).
`main` puede evolucionar entre versiones; una versión publicada se identifica por su tag
y sus notas de release, no por el último commit.
