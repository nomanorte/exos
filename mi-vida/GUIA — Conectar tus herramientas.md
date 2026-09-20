---
tipo: conocimiento
estado: activo
fecha: 2026-08-19
tags: [integraciones, herramientas, negocio, soberania]
---

# GUÍA — Conectar tus herramientas

> Esta guía es la parte de negocio. El **cómo** técnico —pilotos, adaptadores, aislamiento,
> registro— vive en `exos/protocolos/PROTOCOLO — Pilotos e integraciones.md`, y en
> `../web/docs/INTEGRACIONES.md` si lo que conectas toca tu web. Aquí solo se decide **qué
> conectar, cuándo, y qué ganas**.

## El problema que resuelve

Tus herramientas no se hablan entre ellas. Hablan contigo, una por una.

El motor de reservas sabe quién viene. El correo sabe qué le prometiste. La hoja de precios
sabe cuánto vale. Ninguna de las tres sabe lo que saben las otras, así que **el puente eres
tú**: copiando de una a otra, acordándote de lo que dijiste, y corrigiendo cuando algo sale
con el dato viejo.

Añadir una herramienta más no arregla eso. Añade una isla más.

Lo que cambia con un cerebro en medio es el sentido de las flechas: **las herramientas dejan
de hablar contigo y empiezan a leer del mismo sitio.** Tu criterio —precios, políticas, qué
se puede prometer y qué no— se escribe una vez, aquí, y cualquier agente lo consulta antes
de tocar nada.

```
ANTES                          DESPUÉS
reservas ──┐                   reservas ──┐
correo   ──┼──► TÚ             correo   ──┼──► TU CEREBRO ──► tú decides
precios  ──┤   (el puente)     precios  ──┤   (la fuente)
redes    ──┘                   redes    ──┘
```

## Las tres preguntas antes de conectar nada

Contéstalas en voz alta. Si alguna falla, todavía no toca.

1. **¿Qué trabajo desaparece de mi semana si esto funciona?** Si no sabes nombrarlo en una
   frase, no es una integración: es curiosidad.
2. **¿La cuenta va a estar a mi nombre?** Si el alta la hace otro con su correo, no estás
   conectando una herramienta: estás alquilándola.
3. **¿Puedo apagarlo y seguir operando?** Todo lo que conectas es algo más que mantener,
   que puede caerse y que algún día subirá de precio.

## Qué conectar, y qué gana el cerebro con ello

| Lo que quieres | Qué conectas | Qué gana el cerebro | Cuándo compensa de verdad |
|---|---|---|---|
| **Que te escriban** | Tu correo a la vista, o Resend con tu dominio | Los mensajes entran con contexto: quién escribe y sobre qué oferta | Cuando recibas tantos que necesites clasificarlos. Antes no |
| **Escribir como el negocio** | Tu dominio + tu proveedor de correo | Cada respuesta sale con tu tono y tus políticas ya escritas, no improvisadas | Cuando el correo sea tu cara ante clientes |
| **Cobrar o agendar** | Tu pasarela, tu calendario | Deja de haber dos versiones de «qué se puede reservar y a qué precio» | Cuando tengas a quién cobrar |
| **Reservas y disponibilidad** | Tu motor o tu PMS, tal cual está | El agente consulta el estado real antes de prometer nada | Cuando alguien que no seas tú tenga que contestar |
| **Atención por chat** | El canal que ya uses | Responde con tus precios y tus límites, no con lo que sepa internet | Cuando las mismas cinco preguntas te coman la mañana |
| **Guardar datos propios** | Tu base de datos | Un solo sitio con el estado real, en vez de cuatro copias | **Casi nunca.** Tus textos ya viven como archivos aquí |

**Lee la última columna antes que las otras dos.** La mitad del valor de esta guía es la
lista de cosas que hoy no te hacen falta.

## Las cuatro reglas que hacen que conectar no te cueste la soberanía

1. **La cuenta es tuya.** Cada servicio se abre con tu correo, desde tu ordenador. Quien
   tiene la cuenta tiene el servicio, y recuperar algo que está a nombre de otro va de pedir
   favores.
2. **La clave nunca dentro de un archivo.** Va al llavero de tu ordenador o a la
   configuración del sitio donde publicas. Un archivo se comparte, se sube sin querer y se
   copia en un zip — y un secreto filtrado no se desfiltra: solo se rota, y siempre tarde.
3. **Detrás de un adaptador.** El proveedor se elige por lo que hace, no por lo que cuesta
   cambiarlo. Si mañana sube de precio, se sustituye la pieza y no el sistema.
4. **Queda escrito.** Dos líneas en `mi-vida/decisions/`: qué encendiste y por qué. Dentro
   de seis meses no vas a acordarte de por qué existe esa cuenta.

## El orden que funciona

No es el orden de lo más llamativo. Es el orden de lo que da valor antes.

1. **Primero el cerebro, sin conectar nada.** Tu oferta, tus políticas y tu tono escritos.
   Sin esto, cualquier cosa que conectes hereda tu desorden y lo multiplica.
2. **Después la web**, que es lo que ve el mundo. Nace estática a propósito: no se cae por
   un servicio ajeno y no cuesta dinero.
3. **Después el correo**, cuando el volumen lo pida.
4. **Y al final lo que atiende o cobra**, que es lo que más riesgo tiene y lo que más se
   beneficia de que las tres capas anteriores ya estén escritas.

> **La trampa habitual es empezar por el 4.** Un chat que atiende sin que existan el 1 y el
> 2 promete cosas que no puedes cumplir — y el que da la cara eres tú.

## Lo que no se conecta

- **Nada que exija subir datos de tus clientes a un sitio que no controlas.** La regla corta:
  si no lo publicarías, no lo pegues en algo que no es tuyo.
- **Nada que solo se pueda apagar cancelando y perdiendo el histórico.** Eso no es una
  integración, es una mudanza con billete de ida.
- **Nada «por si acaso».** Cada conexión se justifica con la pregunta 1 o no se pone.

## Dónde queda registrado

| Qué | Dónde |
|---|---|
| La hipótesis y el criterio de abandono | `mi-vida/tareas/` |
| La decisión de adoptar, rechazar o retirar | `mi-vida/decisions/` |
| El contrato técnico, si toca la web | `../web/docs/INTEGRACIONES.md` |
| Qué capacidades ya declaró el proyecto | `mi-vida/onboarding-estado.yaml` |

Si conectas algo y no aparece en ninguna de esas cuatro filas, para el sistema no ha
ocurrido — y dentro de seis meses tampoco habrá ocurrido para ti.
