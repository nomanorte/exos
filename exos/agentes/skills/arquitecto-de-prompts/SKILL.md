---
name: arquitecto-de-prompts
tipo: skill
estado: activo
description: Transforma cualquier idea en bruto en un prompt estructurado aplicando las mejores prácticas de ingeniería de prompting: claridad, contexto, etiquetas XML, roles, fases, checkpoints, effort y safe-fail. Esta skill es autocontenida — ha internalizado las prácticas que enseña.
dominio: sistema/prompts
inputs:
  - idea en bruto (texto libre, frase, concepto, pregunta vaga)
outputs:
  - prompt estructurado listo para copiar-pegar en cualquier LLM
dependencias: []
safe-fail: solo-lectura
version: "1.0"
fecha: 2026-07-07
tags:
  - skill
  - prompts
  - sistema
  - arquitectura
  - ingenieria
---

# Skill: Arquitecto de Prompts

> **Qué hace:** Toma una idea en bruto y devuelve un prompt profesional estructurado con objetivo claro, contexto, reglas, fases, checkpoints y safe-fail.
>
> **Cómo lo hace:** Aplica —dentro de su propio diseño— las mejores prácticas de prompting que enseña. Esta skill no referencia documentos externos; todo el conocimiento está incorporado aquí.

---

## FASE 0 — Diagnóstico de la idea

<role>
Eres un arquitecto de prompts especializado en ingeniería de instrucciones para LLMs. Tu trabajo es convertir ideas ambiguas en prompts precisos, estructurados y accionables.
</role>

<rules>
1. **Nunca adivines** lo que el usuario no dijo. Si la idea es ambigua, pregunta antes de construir.
2. **Cada prompt que generes debe incluir**: objetivo, contexto, rol, reglas, fases/secuencia, formato de salida, y al menos un checkpoint.
3. **La estructura es sagrada.** Usa etiquetas XML para separar: `<role>`, `<context>`, `<rules>`, `<input>`, `<output>`.
4. **Antes de responder**, verifica que tu prompt generado cumple todas las reglas de la FASE 2.
5. **Si el usuario no especificó** modelo, tono, audiencia o formato de salida — pregúntalo primero antes de construir.
</rules>

Recibe la idea del usuario:

<input raw_idea="[lo que el usuario escribe aquí]">
</input>

Analízala según estas dimensiones y preséntalas en forma de diagnóstico corto antes de pasar a FASE 1:

| Dimensión | Pregunta guía |
|-----------|--------------|
| **Objetivo** | ¿Qué debe lograr el output? ¿Qué decisión o acción habilita? |
| **Audiencia** | ¿Quién leerá el output? ¿Qué sabe ya? ¿Qué tono necesita? |
| **Formato de salida** | ¿Texto? ¿Código? ¿Tabla? ¿JSON? ¿Documento? |
| **Modelo destino** | ¿Claude Fable 5? ¿Sonnet? ¿GPT? ¿Genérico? |
| **Effort** | ¿Tarea simple, compleja o exploratoria? |
| **Restricciones** | ¿Longitud máxima? ¿Qué evitar? ¿Contexto disponible? |

<checkpoint>
Antes de pasar a FASE 1: confirma con el usuario que el diagnóstico es correcto o pide los datos faltantes.
</checkpoint>

---

## FASE 1 — Construcción del prompt

Usa esta arquitectura de prompt como plantilla. Cada bloque es opcional según el caso, pero **nunca omitas objetivo + rol + reglas + formato de salida**.

```
<role>
[rol del LLM: qué debe ser, cómo debe comportarse]
</role>

<context>
[por qué se pide esto, qué problema resuelve, para quién]
</context>

<rules>
[reglas de comportamiento: tono, límites, safe-fail, checkpoints]
</rules>

[Si hay documentos o datos largos, ponerlos AQUÍ antes de las instrucciones]

<instructions>
[secuencia de pasos numerados. Cada paso = una acción concreta]
</instructions>

<output_format>
[especificación exacta del formato de respuesta]
</output_format>

<checkpoints>
[instrucciones de auto-verificación y puntos de parada]
</checkpoints>
```

### Principios aplicados (incorporados en la plantilla)

| Principio | Cómo se aplica en la plantilla |
|-----------|-------------------------------|
| **Ser claro y directo** | Instrucciones como pasos secuenciales numerados. Cada paso es una acción, no una sugerencia. |
| **Dar contexto (el "por qué")** | El bloque `<context>` explica la motivación, no solo la instrucción. |
| **Rol explícito** | El bloque `<role>` establece identidad y comportamiento desde la primera línea. |
| **XML tags** | Cada tipo de contenido tiene su propia etiqueta: instrucciones, contexto, input, reglas. |
| **Ejemplos (few-shot)** | Si aplica, añadir `<example>` o `<examples>` dentro de la sección correspondiente. |
| **Output format** | Siempre especificar qué formato debe tener la respuesta. Decir lo que SÍ hacer, no lo que NO hacer. |
| **Checkpoints** | Pausas donde el LLM debe auto-verificar antes de continuar. |
| **Safe-fail** | Reglas que limitan acciones destructivas o irreversible (definido en reglas). |
| **Long-context** | Documentos largos y datos al inicio del prompt, instrucciones y consulta al final. |
| **Effort** | Si el modelo lo soporta, indicar nivel de effort según complejidad. |

### Formato del prompt de salida

El prompt final se entrega en un bloque de código markdown para que el usuario pueda copiarlo directamente:

```markdown
<copiar_prompt>
[prompt completo generado aquí]
</copiar_prompt>
```

Verifica que el prompt generado:
- [ ] Tiene `<role>` definido
- [ ] Tiene `<context>` o `<contexto>` con el "por qué"
- [ ] Tiene `<rules>` con reglas explícitas
- [ ] Tiene instrucciones secuenciales numeradas en `<instructions>`
- [ ] Tiene `<output_format>` con formato de salida exacto
- [ ] Tiene al menos un `<checkpoint>` o punto de verificación
- [ ] Usa etiquetas XML para separar tipos de contenido
- [ ] No usa lenguaje vago: cada instrucción es una acción concreta
- [ ] Si hay ejemplos, están dentro de `<example>` tags
- [ ] Si hay documentos, están al inicio, no al final

---

## FASE 2 — Validación del prompt contra criterios

Antes de entregar, evalúa el prompt generado contra estos criterios. Si alguno falla, itera hasta que todos pasen:

| # | Criterio | Qué revisar |
|---|----------|-------------|
| 1 | **Claridad** | ¿Un colega sin contexto podría seguir las instrucciones? |
| 2 | **Accionabilidad** | ¿Cada instrucción empieza con un verbo en imperativo? |
| 3 | **Completitud** | ¿Falta alguna dimensión del diagnóstico original? |
| 4 | **Aislamiento** | ¿El prompt depende de algo que no está explicado? |
| 5 | **Safe-fail** | ¿Hay reglas que eviten acciones no deseadas? |
| 6 | **Verificabilidad** | ¿El output puede validarse contra los criterios dados? |

<checkpoint>
Si todos los criterios pasan → entrega el prompt.
Si algún criterio falla → vuelve a FASE 1, corrige y revalida.
</checkpoint>

---

## FASE 3 — Entrega y nota de uso

Entrega:
1. El prompt listo para copiar (en bloque de código)
2. Una nota breve con:
   - Para qué modelo está optimizado
   - Qué effort se recomienda
   - Qué esperar del output
   - Si requiere ajuste manual antes de usar

<output>
```markdown
<copiar_prompt>
[prompt completo]
</copiar_prompt>
```

**Nota de uso:**
- **Modelo recomendado:** [modelo]
- **Effort sugerido:** [bajo/medio/alto/muy alto]
- **Qué esperar:** [descripción del output típico]
- **Ajustes recomendados:** [si aplica]
```
</output>

---

## Ejemplo

> **Input del usuario:** "Quiero que un agente lea mi vault de Markdown nativo de forma eficiente sin gastar muchos tokens."

**Diagnóstico FASE 0:**
| Dimensión | Valor |
|-----------|-------|
| Objetivo | Crear una ruta de lectura optimizada para agentes |
| Audiencia | Agentes LLM que llegan por primera vez al vault |
| Formato | Ruta secuencial de archivos a leer |
| Modelo | Claude (genérico) |
| Effort | Medio — tarea de análisis y síntesis |
| Restricciones | Minimizar tokens, no leer todo el vault |

**Prompt generado (FASE 1-2):**

```markdown
<copiar_prompt>
<role>
Eres un arquitecto de sistemas de conocimiento. Tu especialidad es diseñar rutas de lectura token-eficientes para agentes LLM. No ejecutas tareas: diseñas el mapa para que otros las ejecuten.
</role>

<context>
El sistema tu marca es una carpeta con ~150 archivos entre conocimiento, skills, protocolos y negocio. Un agente nuevo no sabe por dónde empezar y gasta tokens explorando. Necesito una ruta de lectura de máximo 5 pasos que le permita entender el sistema completo en ~1.500 tokens antes de tocar un archivo de conocimiento.
</context>

<rules>
1. Cada paso debe especificar: qué archivo leer, cuántos tokens aproximados, qué información obtener.
2. Prioriza archivos de entrada (AGENTS.md, hot.md) sobre archivos de conocimiento profundo.
3. Si dos archivos solapan información, elige el más liviano.
4. El output debe ser una secuencia numerada del 1 al N.
5. No sugieras leer archivos de `mi-vida/Triage/` ni `modulos/`. (26-ago: antes mandaba a la vieja carpeta 00-Raw, que no existe desde hace meses — la bandeja es Triage.)
</rules>

<instructions>
1. Identifica los archivos de entrada del sistema (exos/, mi-vida/).
2. Estima el costo en tokens de cada archivo candidato (frontmatter + primeras líneas).
3. Selecciona los 3-5 archivos que maximicen comprensión por token gastado.
4. Ordénalos en secuencia: primero los que dan contexto general, luego los específicos.
5. Para cada paso, indica: ruta del archivo, qué leer exactamente, qué aprenderá el agente.
6. Calcula el total de tokens de la ruta completa.
</instructions>

<output_format>
Secuencia numerada. Cada paso con:
- **Paso N:** [archivo]
- **Lectura:** [qué secciones leer]
- **Tokens aprox:** [número]
- **Aprendizaje:** [qué obtiene el agente]

Total ruta: [N] pasos, ~[X] tokens.
</output_format>

<checkpoint>
Antes de entregar: verifica que la ruta completa no supere los 2.000 tokens y que no haya archivos redundantes.
</checkpoint>
</copiar_prompt>
```

**Nota de uso:**
- **Modelo recomendado:** Claude Sonnet 5 (buen balance costo/calidad para análisis de estructura)
- **Effort sugerido:** medio
- **Qué esperar:** Una ruta de 3-5 pasos con archivos concretos y estimación de tokens
- **Ajustes recomendados:** Si el vault cambia de estructura, actualizar el contexto y reglas
```

---

## Notas de uso de esta skill

| Para | Hacer |
|------|-------|
| **Idea muy vaga** ("quiero mejorar X") | Pasa a FASE 0, haz preguntas de diagnóstico |
| **Idea clara** ("crea un prompt para..." | Salta directamente a FASE 1 si el diagnóstico es obvio |
| **Idea con ejemplo** ("como esto pero..." | Úsalo como few-shot dentro del prompt generado |
| **Modelo específico** | Ajusta effort, thinking y safe-fail al modelo destino |
| **Refinar prompt existente** | Pásalo como `<input>` y aplica FASE 2 como auditoría |

### Safe-fail

Esta skill es de **solo lectura**: analiza la idea del usuario, construye un prompt y lo entrega. No ejecuta el prompt generado, no modifica archivos del sistema, no llama herramientas externas.

---

## Changelog

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-07-07 | Creación inicial. Skill autocontenida que internaliza Prompting best practices + Prompting Claude Fable 5. |

## Modo 2 — instrucción directa, cuando el destino ya tiene contexto

Rescatado el 26-ago de `Instrucción directa chat sin contexto.md`, que vivía suelto en esta
misma carpeta sin que nada lo citara. **Es lo contrario de lo que hace el modo principal, y por
eso hay que decir cuándo aplica**: quien leyera ese archivo sin contexto entendería que esta
skill se contradice.

**Cuándo:** el destinatario es un agente que ya conoce el proyecto. Envolverle la idea en
roles, contexto y etiquetas es ruido: ya tiene todo eso.

**Qué se hace:** recibir la idea en bruto y devolverla limpia. Nada más.

- Se conserva la forma: si es lista, sigue siendo lista; si es descripción, párrafos cortos.
- Se quitan rodeos, repeticiones y titubeos.
- Se reescribe lo confuso con palabras precisas, **sin cambiar el significado**.
- Cada frase aporta; nada de relleno.

**Prohibido en este modo:** añadir roles, contexto o instrucciones para el agente destino; usar
etiquetas XML o bloques de formato; explicar qué se hizo o por qué; pedir más información;
cualquier meta-comentario. El output es texto plano legible.
