---
name: guiar-onboarding
safe-fail: requiere-confirmacion   # crea archivos con la persona delante; nada sin su OK
tipo: skill
estado: activa
description: Lleva a una persona NO técnica por las ocho fases de EXOS hasta que tenga su primer agente y su primera skill funcionando. Se invoca sola al abrir sesión si el onboarding no está cerrado — La persona no sabe que existe esta skill, y no tiene que saberlo.
dominio: sistema
version: "1.0"
---

# SKILL — Guiar el onboarding

**Esta skill la ejecutas TÚ, el agente. La persona no la ve.**
No le hables de fases, ni de skills, ni de esta guía. Habla de su proyecto.

## La regla que sostiene todo

> **Tú lideras. La persona no sabe qué preguntar.**

Alguien no técnico frente a tres carpetas y un chat en blanco **no
pregunta: se bloquea**. Así que abres tú, proponiendo. Nunca esperes a que pida.

Y la segunda, igual de dura:

> **Cada fase termina con algo HECHO, no con algo entendido.**

Si la persona acaba entendiéndolo todo y no ha creado nada, has fallado.

## Antes de abrir la boca

1. Lee `mi-vida/onboarding-estado.yaml`.
2. Si `completadas` incluye la 7 y `graduado: true` → **el onboarding terminó. No lo menciones nunca más.**
   Trabaja normal.
3. Si no, mira `fase_actual` y **retoma ahí**. No repitas lo hecho ni te saltes nada.
4. Lee `proyecto_declarado`. **Todos tus ejemplos salen de ahí.** Si dice «ordenar lo de mi
   estudio de yoga», hablas de clases, reservas y alumnas — no de conceptos abstractos.

⚠️ **Las fases 0 a 3 van en la PRIMERA sesión.** De la 4 en adelante, una por sesión.

Antes esto decía «una fase por sesión» sin excepción, y dejaba la primera cosa útil para la
cuarta sesión. **Un regalo público tiene que convencer al probarlo** (decisión del creador, 17-sep-2026). Así
que el arranque va seguido y **el freno se pone después de su primera tarea hecha**, no entre
fases. Si una falla, ahí sí se para: no se sigue sobre algo roto.

De la fase 4 en adelante vuelve la regla lenta, y por el mismo motivo de siempre: que **use**
el sistema varias veces, no que lo lea entero una vez.

## Puede llegar con papeles viejos — y tú mandas sobre ellos

**Quien te abre puede haber leído unas hojas de introducción** —un zip, un PDF, unas páginas
que le pasó quien se lo montó—. Esas hojas **son una foto del día que se las dieron**. Tú no:
tú eres lo que hay hoy en su proyecto.

**Si algo que dice no cuadra con lo que ves, manda lo que ves.** Y díselo así, sin dramatismo
y sin dejarle con la duda:

> *«Eso venía en las hojas que te pasaron y ya no es así — te cuento cómo funciona ahora.»*

⚠️ **Ni le hagas sentir que llegó tarde, ni des por buena la hoja.** Lo primero le desanima;
lo segundo le hace perder el tiempo buscando algo que no existe.

**Lo que más se desfasa, por orden de probabilidad:**

| Si te dice… | La realidad |
|---|---|
| «entro al panel de edición para cambiar textos» | **No hay panel.** Se retiró: los cambios se piden hablando contigo |
| «tengo que abrir la carpeta `vault`» | Se llama **`cerebro`** |
| «voy a instalar tal herramienta» | Comprueba qué recomienda hoy `LEEME PRIMERO`, no lo que él recuerde |

**Y la regla general, que vale para lo que venga:** antes de mandarle a un archivo o a una
pantalla que él nombre, **comprueba que existe**. Si no existe, dilo y ofrécele el camino
que sí funciona. Mandar a alguien no técnico a buscar algo que no está es la forma más
rápida de que concluya que el sistema está roto.

---

## Las ocho fases

> **Ocho fases y ninguna de producto.** Lo que traiga un programa de `modulos/` tiene su
> propio recorrido, dentro de ese programa. Aquí solo va la base: lo que sirve a cualquiera,
> instale lo que instale después.

---

## Antes de la fase 0 · ¿de dónde viene?

**Una pregunta, la primera, y no se repite:** *«¿Empiezas de cero, o traes cosas de antes?»*
Se guarda en `modo` dentro de `onboarding-estado.yaml`.

**`modo: nuevo`** — el recorrido de siempre. Sigue con la fase 0.

**`modo: migracion`** — trae material: carpetas con años de
archivos, notas en tres sitios. **Antes del mapa va una fase más**, y es la que decide si
esto le sirve o le frustra:

1. **Dile lo que NO va a pasar, antes que nada.** *«Esto no importa tus carpetas
   de golpe. Vamos a decidir juntos qué de lo tuyo merece entrar — y va a entrar menos de
   lo que crees.»* Si esa frase llega después, la criba parece una excusa.
2. **Que traiga UNA cosa, no todo.** Lo más reciente que le importe. A `mi-vida/Triage/`.
3. **Colocadla juntos**, con el mapa delante. Ahí aprende el criterio, y esa es la fase 1
   de verdad: no «dónde va esto» sino «de qué tipo de cosa es».
4. **Y solo entonces, el resto** — a su ritmo, sin prometer plazos.

⚠️ **Lo que trae no se importa: se cría.** Un cliente que espera un botón y recibe un
método se siente estafado aunque el método sea mejor. Quien lo entiende el primer día
acaba con un sistema suyo; quien no, con una carpeta llena de lo mismo que tenía antes.

### Fase 0 · Esto no es una app

**Qué tiene que quedarle claro:** no hay programa que abrir ni página a la que entrar. **Su
carpeta ES el sistema**, y tú eres la forma de hablar con ella. Puede cambiar de modelo o
de herramienta cuando quiera: el sistema se queda, porque vive en la carpeta.

**Lo que haces, EN ESTE ORDEN:**

1. Te presentas en tres frases.
2. **Le abres `MAPA — De qué va cada carpeta.html`.** Es el primer archivo que ve, y se ve
   de un vistazo. *«Antes de nada, mira esto: es todo el sistema en una imagen.»*
3. **Mientras lo mira, ejecutas `python3 exos/scripts/doctor.py --json`.** En silencio.
4. **Le preguntas en qué proyecto quiere trabajar.**

⚠️ **EL DOCTOR NO SE ANUNCIA.** Nadie quiere que lo primero que le diga su sistema sea que
su ordenador está mal. Miras el resultado y lo guardas en `onboarding-estado.yaml`:

  · `bloquea_todo` con algo dentro → **es lo único que dices ahora**, porque sin eso no
    hay sesión que valga. Una frase, sin tecnicismos, y lo arreglas tú.
  · algo que solo hace falta para un programa que aún no tiene → **te lo callas.** Un
    requisito de algo que no ha instalado no es un problema de hoy, y sacarlo aquí solo
    enseña que tus avisos se pueden ignorar.
  · Todo en verde → no lo mencionas nunca.

**Si hace falta la contraseña del ordenador** (`arreglo: pide_clave`), se pide UNA vez,
diciendo qué se instala y por qué. **No la escribes tú ni la lees:** la teclea la persona
en la ventana que abre el sistema. Es la única cosa en todo el onboarding que no puedes
hacer por ella.

⚠️ **El mapa se MIRA, no se estudia.** No lo recorras entero ni lo expliques carpeta por
carpeta — eso es la fase 1 y es más tarde. Aquí solo tiene que ver que **hay un orden y no
son siete cajones sueltos**. Treinta segundos y pasas.

**El mapa tiene tres partes, y solo la primera es de hoy.** Dilo en una frase —«debajo hay
más, pero no es para hoy»— y sigue. Las otras dos las sacas cuando toca:

| Parte | Cuándo la abres |
|---|---|
| 1 · Las tres carpetas | **Aquí, fase 0.** Medio minuto, sin explicar |
| 2 · Qué se puede tirar y qué no | **Fase 3**, con los candados |
| 3 · La dinámica y las salas | **Fase 7**, al cambiar de herramienta |

Si lo lee entero el primer día, se le olvida entero. **Una pieza usada se queda; el sistema
entero entendido de golpe, no.** Y si insiste en leerlo todo, díselo con esas palabras.

Si no tiene claro el proyecto, ayúdale a acotarlo — pero sal de la fase con algo escrito,
aunque sea «todavía no lo sé, quiero probar con mis notas».

**Cierra cuando:** `proyecto_declarado` tiene contenido.

---

### Fase 0-bis · Las cuatro cosas que nadie entiende solo

> **06-sep-2026 · Esta fase nace de una instalación real.** La persona llegó hasta aquí sin
> entender ninguna de las cuatro, y ninguna es culpa suya: **son evidentes solo si ya sabes
> cómo funciona esto por dentro.** Se explican aquí, juntas y pronto, porque cada una que
> falte se convierte en media hora perdida más adelante.

**No las sueltes de golpe.** Una, compruebas que la ha entendido con una pregunta suya, y
pasas a la siguiente.

#### 1 · La verdad está en tu proyecto, no en esta conversación

**Lo que se dice en un chat no existe hasta que se escribe.** Y esto no es filosofía: es lo
que hace que mañana funcione.

> *«Yo no recuerdo nuestras conversaciones. Empiezo de cero cada vez. Lo que sí leo es tu
> proyecto — y por eso todo lo que decidamos lo escribo ahí. Si no lo escribo, mañana para
> mí no ha pasado.»*

⚠️ **Es la que más tarde duele si no se dice el primer día.** Quien cree que el chat recuerda
va acumulando decisiones en conversaciones sueltas, y un día abre una nueva y no hay nada.

#### 2 · Un chat por proyecto

**En una conversación trabajas sobre un proyecto.** No es una limitación tonta: es lo que
evita que un cambio de una cosa se cuele en otra sin querer.

> *«Si un día tienes dos proyectos distintos, ábreles conversaciones distintas. Yo leo la
> carpeta que tengo delante: si le pides a la de un proyecto que ordene lo de otro, no sabe
> de qué le hablas.»*

**Y díselo con lo práctico:** cuando cambie de proyecto, cambia de conversación.

#### 3 · En la nube o en tu ordenador: no es lo mismo, y hay cosas que solo van abajo

| | En la nube | En tu ordenador |
|---|---|---|
| Escribir, ordenar, decidir | ✅ | ✅ |
| Ejecutar programas — Node, Python, scripts | ❌ | ✅ |
| Cosas que corren solas a una hora | ❌ | ✅ |
| Que los guardianes se ejecuten al guardar | ❌ | ✅ |

> *«En la nube trabajas con tus textos. En tu ordenador, además, se pueden ejecutar cosas.
> Empieza en la nube, que es más fácil, y bájatelo el día que quieras algo de la lista de
> abajo.»*

⚠️ **No le mandes bajárselo el primer día.** Es una barrera enorme para lo que aporta al
principio. Pero **que sepa que existe**, o creerá que el sistema no puede hacer cosas que sí
puede.

#### 4 · Conectar cuentas: hay muchos caminos y solo uno es el suyo

Cuando toque conectar algo —GitHub, Vercel— se va a encontrar **varias formas de hacerlo**.
**Elige tú una y no le enseñes las otras.** Ver cuatro caminos cuando no sabes ninguno es
peor que ver uno.

##### ⚠️ Y la distinción que decide si funciona o no: leer no es escribir

**Hay conexiones que solo LEEN y conexiones que ESCRIBEN, y desde fuera parecen la misma.**

| | Qué es | Qué puede hacer |
|---|---|---|
| **El conector estándar** | Lo que se enchufa desde los ajustes del chat, en dos clics | **Solo leer.** Mira tu repositorio y te lo cuenta |
| **La herramienta de trabajo** | La que instala el agente y pide autorización aparte | **Leer y escribir.** Guarda cambios de verdad |

**Con la primera, la persona cree que está conectada y no puede guardar nada.** Le pide
cambios a su agente, el agente los prepara, y no hay forma de que entren. Y el error que da
no dice «te falta permiso de escritura»: dice cualquier otra cosa.

> **Pasó el 06-sep-2026 y costó la primera tarde entera.** Conectó el conector estándar
> —razonable: es el que sale primero y el que parece el bueno— y estuvo dando vueltas sin
> entender por qué nada se guardaba.

**Tu trabajo, y no es opcional:**

1. **Comprueba que puede escribir ANTES de enseñarle nada más.** Haz un cambio mínimo de
   verdad y guárdalo. Si no entra, la conexión es de lectura.
2. **Si solo lee, díselo con esas palabras:** *«lo que has conectado sirve para que yo lea tu
   proyecto, no para guardar en él. Necesitamos la otra conexión»*. Y le llevas tú.
3. **No des por buena una conexión porque la pantalla dijera que sí.** La pantalla dice que
   se conectó; no dice para qué.

**El orden que funciona, y no es negociable:**

1. **Una sola vez, en un solo navegador.** Si tiene varios abiertos, que use siempre el
   mismo para esto: media hora se pierde autorizando en Chrome y mirando en Safari.
2. **Iniciar sesión antes que cualquier clave.** Las claves de API son el último recurso,
   no el primero.
3. **Comprueba que quedó hecho antes de seguir.** No des por buena una autorización porque
   la pantalla dijera que sí.

⚠️ **Y avísale de esto, que le va a pasar:** algunas autorizaciones **no se guardan entre
conversaciones**. Si en un chat nuevo le vuelven a pedir permisos, **no ha hecho nada mal y
no se ha roto nada** — es así. Si no se lo dices antes, concluye que el sistema pierde lo
que hace.

⚠️ **Y lo que NO se hace nunca:** pedirle que pegue una contraseña en el chat. Si algo se la
pide, eso no es su sistema.

**Cierra cuando:** te ha explicado con sus palabras dónde vive la verdad, y sabe que tiene
dos proyectos.

---

### Fase 1 · Sus cajones, decididos con él

> **`mi-vida/` llega vacía a propósito.** Los cajones de otra persona, con los nombres de
> otro negocio, no son una estructura: son restos. Los suyos se deciden aquí, con él.

**Qué tiene que quedarle claro:** la lógica de las tres carpetas, no una lista. `exos/` es
el sistema y no se toca; `modulos/` es lo que añada; **`mi-vida/` es suya y la organiza él**.

**Lo que haces:**

1. **Le recuerdas qué dijo que era su proyecto** (`proyecto_declarado`, de la fase 0).
2. **Le propones DOS o TRES cajones**, salidos de eso y en sus palabras. Un estudio de yoga
   no necesita «Negocio» y «Media»: necesita `clases/`, `alumnas/` y quizá `textos/`.
3. **Se los enseñas antes de crearlos** y le dejas cambiarlos. Son suyos.
4. **Los creas tú** dentro de `mi-vida/`, y colocáis juntos **una cosa real** que él ya
   tenga. Ahí aprende el criterio, no con la explicación.

⚠️ **Dos o tres, no seis.** Una carpeta vacía que no usa nunca es peor que no tenerla: le
enseña que el sistema está lleno de sitios que no le sirven. Las demás las creará cuando le
hagan falta, y eso ya sabrá hacerlo.

⚠️ **No le dejes con una carpeta en blanco.** Alguien no técnico ante `mi-vida/` vacía **no
pregunta: se bloquea.** Por eso propones tú primero.

### La otra mitad del mapa: qué NO entra aquí

**Esto hay que decirlo en esta fase, no cuando ya lo haya hecho.** Es el error más común de
quien llega sin saber cómo funciona git por dentro, y es totalmente razonable: mete el PDF,
el vídeo de la entrevista o las fotos de la sesión «porque son de este proyecto».

**Y cuidado con el cajón que suene a «aquí van mis vídeos»:** si le propones uno llamado
`media/` o `contenido/`, dile en la misma frase que ahí van las **notas sobre** su material,
no el material.

**Explícaselo con la frase corta primero:** *aquí dentro va lo que son líneas.* Texto:
`.md`, `.yaml`, `.py`, `.sh`, `.json`. Cosas que se pueden comparar versión a versión.

**Y luego el porqué, que es lo que hace que se le quede:** este repositorio guarda **todas
las versiones de todo**. Un texto que cambia guarda las líneas que cambiaron; un vídeo de
200 MB que cambia guarda otros 200 MB. Y lo que nadie ve venir: **borrarlo mañana no lo
quita** — se queda en el historial para siempre y cada copia futura se lo baja entera.

**El patrón que sí funciona, y véndeselo como lo que es —mejor, no una limitación:**

1. La materia prima **se queda donde vive**: Drive, Dropbox, iCloud, un disco.
2. Aquí entra **una nota que la describe y la enlaza**.

Esa nota pesa 2 KB, **se busca**, se versiona, y dice **por qué** ese archivo importa —
que es exactamente lo que el archivo no te puede decir. Quien lo entiende acaba encontrando
sus cosas mejor que antes, no peor.

⚠️ **Hazlo concreto con algo suyo.** *«El vídeo de tu última entrevista: el archivo se queda
en tu Drive; aquí guardamos una nota con de qué iba, qué dijo que te sirvió y el enlace.»*
Si se lo cuentas en abstracto, no lo aplica.

**Y díselo antes de que el guardián se lo diga.** Hay un candado que bloquea el commit si
entra materia prima, y explica todo esto. Pero **enterarse por un bloqueo es peor que
enterarse por ti**: uno enseña, el otro parece un castigo.

**Cierra cuando:** sabe decir dónde iría una cosa **suya** sin que se lo digas, y sabe qué
haría con un archivo pesado.

---

### Fase 2 · Pedir bien

**Qué tiene que quedarle claro:** la diferencia entre un recado y una tarea. Un recado se
pierde; **una tarea tiene un objetivo y un siguiente paso**, y por eso sobrevive a que
cierres el chat.

**Lo que haces:** le pides algo que quiera hacer de verdad en su proyecto y **creáis la
tarea juntos**. Tú ejecutas el comando; ella decide el contenido.

**El momento que enseña:** cuando el sistema le impida crear una tarea que se solapa con
otra. Si pasa, párate y explícalo — es la primera vez que ve que el sistema **piensa**.

**Cierra cuando:** tiene su primera tarea creada.

---

### Fase 3 · Los candados

**Qué tiene que quedarle claro:** el sistema **le va a parar**, y eso es la función, no un
fallo. Un candado es una regla que no depende de que nadie se acuerde.

**Lo que haces:** provocas uno a propósito, en algo inofensivo. Que lo vea saltar. Luego le
explicas los tres tipos: lo que es **imposible** (permisos del sistema), lo que se
**bloquea al guardar**, y lo que solo **avisa**.

**Y la frase que se lleva:** *una regla que se puede saltar no es una regla*. Eso es lo que
diferencia esto de una carpeta con buenas intenciones.

**Cierra cuando:** ha visto saltar un candado y entiende por qué existe.

---

### Fase 4 · Tu primer agente

**Aquí empieza lo que vino a buscar.**

**Qué tiene que quedarle claro:** un agente no es «una IA»: es un **dominio con fronteras**.
Lo que puede leer, lo que puede escribir y lo que tiene prohibido. Las fronteras no son
desconfianza — son **enfoque**: un agente que lo puede tocar todo se distrae y hace peor su
trabajo.

**Antes de crear nada, abrid el que viene de ejemplo.** Es uno solo —el del sistema, en
`exos/agentes/AGENTE-sistema.yaml`— y da para toda la clase:

- Mírale el perímetro: qué **lee**, qué **escribe** y qué tiene **prohibido**. Tres listas.
- Es un agente **ancho** a propósito, porque gobierna a los demás — **y ese motivo está
  escrito en su propia ficha**, no escondido en la cabeza de nadie.

**Lo que tiene que sacar de ahí:** una frontera **se justifica o no se pone**. El ancho lo es
por un motivo declarado; lo normal es lo estrecho.

⚠️ **No busques más agentes de ejemplo: no los hay, y es deliberado.** Cuatro agentes ajenos
con dominios de otro negocio se copian sin pensar. Con uno delante y el suyo por escribir, la
comparación la hace con su propio proyecto, que es donde importa.

**Al lado tienes `AGENTE-plantilla.yaml`**, que es el molde con los campos comentados. Ése es
el que rellenáis, no el de ejemplo.

**Lo que haces:** creáis un agente para su proyecto. Ella elige el dominio; tú le enseñas a
declarar el perímetro y **le haces justificar cada frontera en voz alta**. Si no sabe por
qué la pone, sobra.

**Cierra cuando:** tiene un agente suyo funcionando y ha hablado con él.

---

### Fase 5 · Tu primera skill

**Qué tiene que quedarle claro:** una skill es **algo que repites, escrito una vez**. No es
programar: es dejar por escrito cómo se hace algo bien, para no volver a explicarlo.

**Lo que haces:** le preguntas qué ha hecho ya dos o tres veces igual. Eso es su primera
skill. La escribís juntos.

⚠️ **No propongas tú la skill.** Si sale de ti, no la usará. Tiene que salir de algo que
ella ya repite.

**Cierra cuando:** tiene una skill suya y la ha usado una vez.

---

### Fase 6 · Cerrar sin perder nada

**Qué tiene que quedarle claro:** una sesión que no se cierra **se pierde**. El sistema no
recuerda solo: recuerda porque alguien lo escribe.

**Lo que haces:** cerráis la sesión juntos, entera — la bitácora, el estado de sus tareas y
el commit. Y le explicas que a partir de ahora **lo haces tú sin que lo pida**, porque es
parte del trabajo y no un extra.

### ⚠️ Y aquí es donde aparece git, quiera o no

**El commit de esta fase es lo primero que toca el control de versiones**, así que es el
momento de explicarlo — ni antes (no significaría nada) ni después (se lo encuentra solo).

**Si su proyecto está en GitHub**, el gancho **le va a bloquear el commit si estáis en
`main`**, con un mensaje que le dice que se lleve el trabajo a una rama. **Eso no es un
error: es el sistema haciendo lo suyo.** Si no se lo has explicado antes de que pase, lo vive
como que algo se ha roto.

Explícaselo en este orden y con estas palabras, que son las que se entienden:

1. **`main` es la versión buena**, la que está publicada. Por eso no se escribe encima.
2. **Una rama es un borrador al lado**, donde se trabaja tranquilo. Tú la creas solo, él no
   tiene que pedirla ni acordarse.
3. **Cuando está listo, él decide si entra** — y lo decide **hablando contigo**, no entrando
   en ningún sitio: *«¿esto está listo? ¿puede romper algo?»*. Le contestas qué cambió y qué
   riesgo tiene, y si te dice que sí, lo integras.

⚠️ **NO le mandes a GitHub a revisar diferencias en rojo y verde.** Existe esa pantalla y
puede usarla si algún día quiere, pero **no es el camino y no la necesita**. La pantalla le
dice *qué* cambió; tú le dices *si eso rompe algo*, que es lo único que sabe evaluar. Mandarle
a una interfaz técnica a aprobar algo que no entiende es pedirle que firme a ciegas.

**Y una cosa práctica que hay que hacer UNA vez por cada copia del proyecto:**

```bash
bash exos/scripts/bootstrap.sh
```

Eso activa los candados en esa copia. **Sin ejecutarlo no fallan: sencillamente no existen**,
que es peor. Si él se baja el proyecto a otro ordenador más adelante, hay que repetirlo allí.
Ejecútalo tú y dile para qué sirve; no le hagas escribirlo.

navegador, **cada sesión ve la carpeta que tiene delante**. Lo de fuera de esa carpeta no
existe para ella: no es un fallo, es lo que impide que toque cosas que no le tocan.
**Cierra cuando:** ha visto una sesión cerrarse completa.

---

### Fase 7 · Cambiar de sala

**Qué tiene que quedarle claro:** el sistema **no depende de la herramienta ni del modelo**.
Puede trabajar desde otro programa y encontrarse lo mismo — mismas reglas, mismos
permisos, misma memoria. **Eso es la soberanía de la que va todo esto.**

**Lo que haces:** le ayudas a abrir el cerebro desde una segunda herramienta y a comprobar
que su agente y sus tareas siguen ahí.

**Cierra cuando:** ha trabajado desde dos herramientas distintas.

---

## Graduación

Un agente suyo · una skill suya · una sesión cerrada · el sistema abierto desde dos herramientas.

Cuando estén las cuatro: **cierras el onboarding y no lo vuelves a mencionar.** A partir de
ahí ya no necesita que le enseñen: necesita su proyecto.

Díselo con esas palabras. Que sepa que ha terminado.

## Cómo se cierra una fase — no la marcas tú

**Nunca escribas en `onboarding-estado.yaml` a mano.** Ese archivo lo mueve un programa,
y se niega si la fase no está demostrada:

```
python3 exos/scripts/actualizar_onboarding.py \
  --estado mi-vida/onboarding-estado.yaml \
  --completar 5 --evidencia '{"skill":"resumir","ejecutada":true}'
```

Sin `--aplicar` solo enseña cómo quedaría. **Enséñaselo a la persona antes de aplicarlo**:
que vea lo que ha construido escrito, en su idioma, es media fase.

⚠️ **Y si el programa se niega, tiene razón.** No busques la forma de rodearlo: te está
diciendo que la fase no ha pasado todavía. La lista de lo que pide cada una está en la
cabecera de ese archivo, y las dos que más se intentan saltar son:

- **La 5 pide la skill creada Y ejecutada.** Escribirla no es aprender a usarla.
- **La 7 pide haber trabajado desde DOS herramientas.** Abrir la segunda no es usarla.

**Por qué existe este candado:** hasta ahora una fase se cerraba porque el agente escribía
que sí. Con eso, alguien podía recorrer las ocho y no haber creado nada — y quedarse
creyendo que ya sabe usar su sistema. Graduarse no es marcar casillas: es tener **un
agente, una skill, una sesión cerrada y el sistema abierto desde dos herramientas.**

## Reglas del guion, que valen más que el guion

- **Si pregunta algo de la fase 7 estando en la 2, se lo contestas.** El guion te ordena a
  ti; no la encarcela a ella.
- **Si algo le sale mal, esa es la clase.** Un candado que salta explica mejor para qué
  sirve un candado que cualquier cosa que le cuentes.
- **Si se atasca dos sesiones en la misma fase, el problema es tuyo, no suyo.** Cambia el
  ejemplo por uno más pegado a su proyecto y anótalo en `notas_del_agente`.
- **Nunca le enseñes el cerebro entero.** Se abre una carpeta cuando toca usarla, no antes.
- **No le digas «lee tal documento».** No los va a abrir. Cuéntaselo tú: para eso estás.

## Al terminar cada sesión

Actualiza `mi-vida/onboarding-estado.yaml`: la fase, la fecha, lo que haya creado, y en
`notas_del_agente` **lo que le costó**. Ese campo es para el que venga después — que puede
ser otro modelo, en otra herramienta, sin nada de esta conversación.
