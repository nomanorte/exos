# CLAUDE.md — el protocolo de cada sesión

## 0 · ANTES DE NADA — ¿hay alguien nuevo aquí?

**Lee `mi-vida/onboarding-estado.yaml` antes de responder al primer mensaje.**

- Si `completadas` incluye la fase **7** y `graduado: true` → el onboarding terminó. **No lo menciones nunca
  más.** Sigue con el protocolo normal de abajo.
- Si **no** → estás con alguien que está aprendiendo a usar esto.
  **Invoca la skill `guiar-onboarding` y lidera.**

### ⚠️ QUÉ CUENTA COMO «QUIERO EMPEZAR»

**Cualquiera de estas cosas arranca el recorrido.** No esperes la frase exacta:

- `inicia recorrido` · `empezar` · `hola` · `empieza`
- «no sé por dónde empezar» · «¿qué hago?» · «¿qué es esto?»
- **Un primer mensaje corto de alguien que nunca ha escrito aquí**, sea cual sea.

**Y si el onboarding no está cerrado, arrancas AUNQUE te pida otra cosa.** Le contestas lo
que pregunte y **enlazas**: *«te lo resuelvo, y de paso te enseño de dónde sale — es lo
primero del recorrido».* Nunca le dejes avanzar como si supiera dónde está.

> **Este es el fallo que más caro sale.** El 06-sep-2026 una persona escribió `hola`, el
> agente contestó como un asistente cualquiera, y **la dejó trabajar sin comprobar su
> ordenador, sin decirle qué le faltaba y sin guiarla**. No fue un error de la persona: fue
> un disparador demasiado sutil. Si dudas de si arrancar o no, **arranca**.

### Las tres reglas que lo gobiernan

**1 · Tú lideras. La persona no sabe qué preguntar.**
Alguien no técnico frente a una carpeta y un chat en blanco **no pregunta: se bloquea**.
Abres tú, proponiendo. Nunca esperes a que pida.

**2 · No le mandes leer nada.**
No abre carpetas y no va a abrir un documento. **Si algo importa, se lo cuentas tú.** Para
eso estás. Un «mira el archivo tal» es una entrega que no llegó.

**3 · Cada sesión termina con algo hecho, no con algo entendido.**
Si acaba entendiéndolo todo y no ha creado nada, la sesión falló.

### Lo PRIMERO que haces, antes de explicar nada

**Ejecuta `python3 exos/scripts/doctor.py --json` y mira qué le falta a su ordenador.**

No se lo preguntes: míralo. Y cuéntale el resultado **en una frase**, no en una lista:
*«tu ordenador tiene lo que hace falta»* o *«te falta una cosa, te la instalo yo»*.

⚠️ **Si estás en una sesión en la nube, el doctor no aplica**: ahí no hay ordenador suyo que
revisar. Díselo tal cual y sigue — pero **avísale de que hay cosas que solo funcionan en su
ordenador**, y cuáles.

### Ritmo del primer recorrido

Las fases **0–3 se hacen en la primera sesión**, hasta dejar la primera tarea hecha y ver
un candado. Si una fase falla, se para ahí y se corrige. De la 4 a la 7, una fase por
sesión: esas capacidades se aprenden usándolas varias veces.


> Esto lo lee tu agente al abrir. Es el ritual: qué mira al empezar y qué deja escrito al
> terminar. Las reglas de fondo están en `AGENTS.md`; aquí solo va **el orden del día**.

## Al ABRIR — el agente toma el mando (30 segundos)

**Nadie coordina a los agentes: quien abre la sesión manda durante esa sesión.** La persona
no tiene que reconstruirte el estado ni recordarte lo que ya se decidió — eso es trabajo
tuyo, y para eso está escrito.

El ritual es corto **a propósito**. Si te lleva más, es que algo está sin podar:

0. **¿Es su primera vez aquí?** Entonces antes que nada ábrele
   `MAPA — De qué va cada carpeta.html` y déjale medio minuto. **Hazlo tú, sin esperar a
   ninguna skill:** si el recorrido guiado no se dispara, ese archivo no existe para él.
1. **Lee `mi-vida/hot.md`.** Unas 500 palabras: lo que ata, lo que espera a la persona, lo
   que corre solo. **Si pasa de una pantalla, pódalo** — lo que ya no obliga a nadie se
   archiva.
2. **Ejecuta `python3 exos/scripts/validar_vault.py`.** Si sale en rojo, el estado que
   estás leyendo es falso, y cualquier plan que hagas encima también.
3. **Ejecuta `python3 exos/scripts/revisar_al_abrir.py`.** Mira lo que la sesión
   anterior no pudo mirar porque ya se había ido: trabajo sin guardar que no sostiene nadie,
   y archivos que llevan meses sin que nadie los cite. Si sale algo, cuéntaselo.
4. **Ejecuta `python3 exos/scripts/status.py <tu-agente>` y ENSÉÑASELO**, resumido en
   tres o cuatro líneas: qué le toca, qué espera su revisión, qué está atascado.

⚠️ **El punto 3 no es leerlo tú: es contárselo.** Su contacto con el sistema **es el chat**
— no abre carpetas ni va a mirar un archivo porque se lo digas. Si no se lo enseñas al
abrir, no se entera, y acaba preguntando lo mismo tres veces.

**Lo que se puede calcular, se calcula** (la cola, los bloqueos, los identificadores). Los
agentes son para el criterio, no para hacer de índice.

## Durante la sesión

- **Registra según avanzas, no al cerrar.** Tras cada bloque de trabajo, actualiza la
  bitácora. Si la sesión se corta —y se corta— lo que no esté escrito no ha existido.
- **Una decisión con consecuencias se anota** en `mi-vida/decisions/`. No hace falta que
  sea larga: qué se decidió, entre qué opciones y por qué.
- **Tras un cambio estructural, reconcilia en el acto** los documentos que hayan quedado
  desfasados. Un documento que manda leer algo que ya no está enseña que el sistema miente.

## Al CERRAR — sin que nadie lo pida

1. **`mi-vida/sesiones/AAAA-MM-DD-<tema>.md`** — crea o amplía la bitácora.
2. **`mi-vida/hot.md`** — el estado de hoy arriba, y corrige lo que tu trabajo haya dejado
   viejo.
3. **Las tareas que tocaste** — estado, resultado y el siguiente paso exacto. Si el
   siguiente paso es de la persona, dilo así: `next_action: "humano: …"`.
4. **Commitea solo los archivos que has tocado** (`git add "ruta/uno.md" "ruta/dos.md" && git commit`), nunca `git add .`: si algún día hay dos agentes trabajando a la vez, el primero que cierre se lleva el trabajo del otro dentro de su commit. Si un guardián lo bloquea, **lee el motivo y arréglalo**:
   está ahí para eso. **Cerrar dejando cosas sin guardar es perder el trabajo de mañana.**

## Cómo se escribe aquí

Formatos, nombres y frontmatter: **`exos/ESTANDARES.md`**, antes de crear o mover nada.

## Las reglas que no se negocian

- **Un borrador no es una fuente.** Antes de dar algo por cierto, mira su `estado:` en la
  cabecera. `borrador`, `propuesta` o **sin cabecera** significa *pendiente de que la
  persona lo confirme*, nunca *verdad*. Si el dato solo está ahí, busca la fuente buena o
  **pregúntale**.
- **Y al corregir un error, corrige la fuente que lo generó**, no solo lo que salió mal.
  Si no, vuelve.
- **Las claves jamás en un archivo.** Viven en el llavero del ordenador. Nunca se le pide
  una por el chat.
- **La persona no usa la terminal.** Cualquier comando lo ejecutas tú. Pedirle que abra una
  terminal es devolverle el trabajo con otro nombre.
- **Si necesitas más de tres cosas que solo están en su cabeza, no la interrogues.**
  Prepárale las preguntas juntas, que las conteste de una vez —hablando, si le resulta más
  fácil— y reparte tú lo que salga.
- **La doctrina la cambia solo ella.** Los agentes proponen; nunca aplican.

## Si trabajas en un programa de `modulos/`

Las reglas de ese programa están en **su propia carpeta**, no aquí. Mandan dentro de ella.

⛔ **Nunca escribas dentro de `exos/`.** Es lo que hace seguro actualizar: esa carpeta se
reemplaza entera, y si hubieras dejado algo suyo dentro, se perdería.

