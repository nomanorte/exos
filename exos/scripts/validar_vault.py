#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EL GUARDIÁN de tu cerebro — comprueba que el estado que lees es el estado real.

Es una HERRAMIENTA, no un agente: existe, tiene una función y no lleva criterio propio.

Es DETERMINISTA a propósito. Comprobar nombres, enumerados y contratos es trabajo de un
validador, no de un modelo de lenguaje: no se inventa nada, cuesta cero y tarda un segundo.
**El guardián juzga la FORMA; la calidad la juzgas tú.** No hay programa que juzgue calidad.

POR QUÉ EXISTE. Las reglas escritas en un documento se incumplen sin que nadie se entere —
un identificador repetido, un estado que no existe, un «ya está guardado» que era falso. Y
no se enteran porque nada las comprueba. Esto las convierte en comprobaciones: se ejecutan
solas al guardar, y hasta que no salen en verde no entra nada al historial.

Cuando añadas reglas tuyas, añádelas aquí. Una regla que hay que recordar no es una regla.

Uso:
    python3 exos/scripts/validar_vault.py          # informe completo
    python3 exos/scripts/validar_vault.py --breve  # solo errores

Salida: 0 si todo está bien o solo hay avisos · 1 si hay ERRORES.
"""

import os
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _raiz import raiz_vault, raiz_web  # noqa: E402

VAULT = raiz_vault()
TAREAS = VAULT / "mi-vida/tareas"
AGENTES = VAULT / "exos/agentes"

# ── Enums oficiales (fuente: exos/ESTANDARES.md) ──────────────────
# 'archivo' entra el 2026-07-30: La persona y un agente hicieron una pasada conjunta de
# limpieza y necesitaban marcar tareas que ya no atan a nadie sin borrarlas ni fingir
# que están completadas. Una tarea en 'archivo' no sale en el parte ni cuenta como
# trabajo vivo. (Lo decidió la persona; los agentes no tocan este conjunto por su cuenta.)
ESTADO_TAREA = {"pendiente", "en-curso", "en-revision", "bloqueada", "completada", "archivo"}
# Quién puede llevar una tarea: tú, o cualquiera de los agentes que hayas declarado.
# desfasadas a la vez (06-ago): los sandboxes de aquel esquema desaparecieron al volverse skills, e
# Se lee de donde viven los agentes, para que no se desfase al crear uno nuevo.
# roster. Se lee de donde vive, para que no vuelva a desfasarse al nacer uno nuevo.
ASIGNADO = {"humano"} | {
    y.stem.replace("AGENTE-", "")
    for y in (VAULT / "exos/agentes").rglob("AGENTE-*.yaml")
    if y.stem != "AGENTE-plantilla"
}
PRIORIDAD = {"urgente", "alta", "media", "baja"}
CAMPOS_TAREA = ["id", "tipo", "estado", "asignado", "prioridad",
                "dominio", "creado", "actualizado"]

# Contrato de las piezas que corren solas
FASE = {"idle", "corriendo", "esperando-input", "output-listo", "bloqueado", "pausado"}
# 'manual' entra el 2026-07-31 por instrucción de la persona: «los pipelines deberíamos
# eliminarlos todos, ponerlos en estado manual para cada agente, y no declararlos
# pipelines hasta que no se valide todo el flujo conmigo».
# Una pieza en `manual` NO es un pipeline: es un procedimiento que lanza un agente
# cuando la persona se lo pide. No corre sola, no cuenta como automatización y no puede
# presumir de estarlo. Volver a otra etapa exige que él haya validado el flujo entero.
ETAPA = {"manual", "en-construccion", "test-interno", "rodaje-api", "produccion-auto"}
CAMPOS_STATUS = ["fase", "etapa", "agente", "detalle", "updated"]

errores, avisos = [], []


def err(donde, msg, arreglo=""):
    errores.append((donde, msg, arreglo))


def avi(donde, msg, arreglo=""):
    avisos.append((donde, msg, arreglo))


def frontmatter(path):
    try:
        t = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not t.startswith("---"):
        return {}
    fin = t.find("\n---", 3)
    if fin == -1:
        return {}
    fm = {}
    for linea in t[3:fin].splitlines():
        m = re.match(r"^([\w-]+):\s*(.*)$", linea)
        if m:
            v = m.group(2)
            # Un comentario en línea (`cierra: TASK-026  # la tarea…`) formaba parte del
            # valor y rompía la comparación en silencio. 30-jul.
            if " #" in v:
                v = v.split(" #", 1)[0]
            fm[m.group(1)] = v.strip().strip('"').strip("'")
    return fm


# ── 1. TAREAS ────────────────────────────────────────────────────────────────

def validar_tareas():
    vistos = {}
    for f in sorted(TAREAS.glob("TASK-*.md")):
        m = re.match(r"(TASK-\d+)", f.name)
        if not m:
            continue
        tid = m.group(1)
        vistos.setdefault(tid, []).append(f.name)

        fm = frontmatter(f)
        nombre = f.name

        faltan = [c for c in CAMPOS_TAREA if c not in fm]
        if faltan:
            err(nombre, f"faltan campos obligatorios: {', '.join(faltan)}",
                "añádelos al frontmatter")

        if fm.get("id") and fm["id"] != tid:
            err(nombre, f"el id del frontmatter ({fm['id']}) no coincide con el "
                        f"nombre del archivo ({tid})", "corrige uno de los dos")

        e = fm.get("estado")
        if e and e not in ESTADO_TAREA:
            err(nombre, f"estado inválido: '{e}'",
                f"usa uno de: {' · '.join(sorted(ESTADO_TAREA))}")

        a = fm.get("asignado")
        if a and a not in ASIGNADO:
            err(nombre, f"asignado inválido: '{a}'",
                f"vale 'humano' o un agente del roster: {' · '.join(sorted(ASIGNADO))}")

        p = fm.get("prioridad")
        if p == "normal":
            avi(nombre, "prioridad 'normal' está deprecada", "usa 'media'")
        elif p and p not in PRIORIDAD:
            err(nombre, f"prioridad inválida: '{p}'",
                f"usa: {' · '.join(sorted(PRIORIDAD))}")

        # Una tarea sin dueño y sin próximo paso es una nota, no una tarea: nadie sabe
        # a quién le toca ni qué es lo siguiente, y acaba resolviéndolo la persona a mano una
        # por una. Se comprueba aquí en vez de dejarlo escrito como norma, porque una
        # norma que un agente puede no leer no es una norma (y una norma que un agente puede no leer no es una norma).
        viva = e not in ("completada", "archivo")

        if viva and not a:
            err(nombre, "tarea viva sin 'asignado'",
                f"di de quién es: {' · '.join(sorted(ASIGNADO))}")

        if viva and not fm.get("next_action"):
            err(nombre, "tarea viva sin 'next_action'",
                "una frase con el siguiente paso concreto y quién lo da")

    for tid, files in vistos.items():
        if len(files) > 1:
            err(tid, f"ID DUPLICADO en {len(files)} archivos: {', '.join(files)}",
                "renumera uno al siguiente ID libre: con el mismo identificador dos veces, "
                "cualquier enlace apunta a las dos")


# ── 1-bis. CUPOS POR ESPECIE ─────────────────────────────────────────────────
# Los números viven en crear_tarea.py y se importan: dos copias del mismo tope se
# desfasan, y ya pasó con el enum de `asignado`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
# crear_tarea.py NO es inerte de importar: a nivel de módulo calcula ASIGNADO_OK
# recorriendo exos/agentes/ con rglob (I/O de disco). Si eso falla — un YAML corrupto,
# un permiso denegado — un `import` a pelo tumba el módulo entero, y como este
# validador corre en el pre-commit, nadie podría commitear nada, sin que el
# traceback explique por qué. Se captura y se convierte en un error legible del
# propio guardián en vez de una excepción que se lo lleve por delante.
try:
    from crear_tarea import CUPOS, conteo_por_estado  # noqa: E402
except Exception as _e:
    CUPOS = None
    conteo_por_estado = None
    err("cupos", f"no se pudo importar crear_tarea.py: {_e}",
        "el guardián no puede comprobar los cupos por especie · revisa exos/agentes/ "
        "(YAML corrupto o permiso denegado) y vuelve a correr el validador")


def revisar_cupos(conteo):
    """Separado de validar_cupos() para poder probarlo sin tocar el disco."""
    if CUPOS is None:
        return          # el import falló y ya quedó registrado como error arriba
    # Los dos umbrales son intencionalmente distintos, no un descuido:
    # `en-curso` es WIP duro — llegar EXACTO al cupo es lo esperado, así que solo
    # pasarse (`>`) es error. `en-revision` es una bandeja de la persona que conviene
    # avisar ANTES de que desborde, así que llegar AL cupo (`>=`) ya dispara el aviso.
    for estado, tope in CUPOS.items():
        n = conteo.get(estado, 0)
        if estado == "en-curso" and n > tope:
            err("cupos", f"{n} tareas en `en-curso` y el cupo son {tope}",
                "pasa las que no estés tocando hoy a `pendiente`. El cupo es el WIP "
                "real: no se empieza trabajo nuevo sin cerrar el que hay")
        elif estado == "en-revision" and n >= tope:
            avi("cupos", f"{n} tareas esperando a la persona (cupo {tope})",
                "enséñale la bandeja antes de darle más trabajo: "
                "python3 exos/scripts/revisar_al_abrir.py --parte")


def validar_cupos():
    if conteo_por_estado is None:
        return          # el import falló y ya quedó registrado como error arriba
    tareas = [{"estado": frontmatter(f).get("estado", "")}
              for f in sorted(TAREAS.glob("TASK-*.md"))]
    revisar_cupos(conteo_por_estado(tareas))


# ── 2. (hueco a propósito) ───────────────────────────────────────────────────
# 16-ago-2026 · Aquí había un bloque validando `06-Pipelines/`: una carpeta que
# el cerebro de origen ya había disuelto y que este producto nunca ha tenido. Comprobaba un
# contrato inexistente, en un sitio inexistente, para nadie. Se retira entero.
#
# Si algún día montas una zona con reglas propias, este es su sitio: una función que
# recorre lo tuyo y llama a `err()` cuando algo incumple. Copia la forma de las de al lado
# y añádela abajo, a la lista que se ejecuta.

# ── 2-bis. REFERENCIAS MUERTAS EN LA DOCTRINA  ─────────────────────

# Los documentos que MANDAN. Si uno de estos nombra una pieza que ya no existe,
# la doctrina esta mintiendo y algun agente la va a obedecer.
# 15-ago-2026 · Esta lista sale VACIADA. La de casa nombraba dos documentos que no
# viajan en el producto y el validador daba dos errores rojos sobre archivos que el
# cliente nunca tuvo — o sea, el sistema estrenándose acusándose a sí mismo. Aquí van
# solo los que se entregan. Cuando escribas doctrina propia, añádela: esta lista es lo
# que impide que un documento que MANDA siga citando una pieza que ya borraste.
DOCTRINA = [
    "AGENTS.md",
    "CLAUDE.md",
    "exos/ESTANDARES.md",
    "mi-vida/hot.md",
]


def validar_referencias_doctrina():
    """Caza referencias a piezas que ya no existen.

    Origen (19-jul): la la regla delegaba el juicio de calidad en el 'ejemplo',
    archivado ese mismo dia. Lo pillo un agente de casualidad. Esto lo convierte en
    freno: es exactamente el tipo de contradiccion que un script SI puede ver.
    """
    # 06-ago: ya no hay sandboxes vivos — 06-Pipelines se disolvio y los 21 estan en
    # archive/sandboxes-2026-07/. La regla sigue en pie: la doctrina no puede mandar
    # sobre un muerto, y ahora TODOS lo estan.
    vivos_sb = set()
    SB_ARCHIVO = VAULT / "archive" / "sandboxes-2026-07"
    archivados = {d.name[:2]: d.name for d in SB_ARCHIVO.iterdir()
                  if d.is_dir() and re.match(r"^\d{2}-", d.name)} if SB_ARCHIVO.is_dir() else {}
    # rglob: desde el 06-ago las cerradas viven en _cerradas/AAAA-MM/ conservando su
    # nombre. Citar una tarea archivada NO es una referencia rota — el documento sigue
    # ahí y el wikilink resuelve igual. Con glob a secas, archivar 55 tareas habría
    # convertido media doctrina en "error" de golpe.
    tareas_vivas = {p.name[:8] for p in TAREAS.rglob("TASK-*.md")}
    agentes_vivos = {p.stem.replace("AGENTE-", "")
                     for p in AGENTES.rglob("AGENTE-*.yaml")
                     if "plantilla" not in p.stem}

    # Las TAREAS VIVAS tambien mandan: una tarea abierta que pide trabajar sobre una
    # pieza archivada sale en el parte de la persona como trabajo pendiente que no existe.
    # (19-jul: TASK-114 seguia pidiendo "crear el sandbox 16" horas despues de archivarlo.)
    for t in sorted(TAREAS.glob("TASK-*.md")):
        txt = t.read_text(encoding="utf-8")
        m = re.search(r"^estado:\s*(\S+)", txt, re.M)
        if m and m.group(1) in ("completada", "bloqueada"):
            continue
        muertos = set()
        for linea in txt.splitlines():
            if re.search(r"archivad|cerrada|obsolet|ya no", linea, re.I):
                continue
            muertos |= {n for n in re.findall(r"[Ss]andbox (\d{2})", linea)
                        if n not in vivos_sb and n in archivados}
        for num in sorted(muertos):
            err(t.name, f"tarea ABIERTA sobre el Sandbox {num}, archivado",
                "sale en el parte de la persona como trabajo pendiente que ya no "
                "existe: ciérrala o reencamínala")

    for rel in DOCTRINA:
        doc = VAULT / rel
        if not doc.exists():
            err(rel, "documento de doctrina que no existe",
                "alguien lo movio o lo borro: la lista DOCTRINA de el guardián apunta al vacio")
            continue
        texto = doc.read_text(encoding="utf-8")
        corto = doc.name

        # Una mencion HISTORICA es legitima ("el 16, que quedo archivado"): lo que
        # esta prohibido es MANDAR sobre un muerto. Convencion: si citas una pieza
        # muerta, en la misma linea tiene que constar que lo esta.
        difunto = re.compile(r"archivad|derogad|jubilad|obsolet|ya no |nunca se ejecut|"
                             r"correcci[oó]n", re.I)

        for linea in texto.splitlines():
            for num in set(re.findall(r"[Ss]andbox (\d{2})", linea)):
                if num in vivos_sb or difunto.search(linea):
                    continue
                if num in archivados:
                    err(corto, f"manda sobre el Sandbox {num}, ARCHIVADO ({archivados[num]})",
                        "reescribe la regla, o di en la misma linea que esta archivado "
                        "si es una nota historica")
                else:
                    err(corto, f"cita el Sandbox {num}, que no existe",
                        "ni activo ni archivado")

        # TASK-NNN citadas que ya no estan
        for t in set(re.findall(r"TASK-\d{3}", texto)):
            if t not in tareas_vivas:
                err(corto, f"cita {t}, que no existe en mi-vida/tareas/",
                    "renombrada o borrada: corrige la referencia")

        # scripts citados por ruta
        for s in set(re.findall(r"exos/scripts/[\w\-]+\.py", texto)):
            if not (VAULT / s).exists():
                err(corto, f"cita el script '{s}', que no existe",
                    "una regla que manda ejecutar algo inexistente no se puede cumplir")

        # nombres de agente en minuscula dentro de listas de roster
        for a in set(re.findall(r"`(agente-ejemplo|agente-media|agente-negocio|agente-web|agente-sistema|orbit|agente-biblioteca|"
                                r"planner|curador|productor|operador)`", texto)):
            if a not in agentes_vivos and a not in ("planner", "curador", "productor",
                                                    "operador"):
                err(corto, f"cita al agente '{a}', que ya no tiene manifiesto",
                    "roster desincronizado con la doctrina")


def validar_contexto_manifiestos():
    """Cada ruta de 'contexto_arranque' de un manifiesto tiene que existir.

    Origen (19-jul): Agente-negocio arrancaba con una ruta al embudo que se habia movido a
    10-Tu Segunda Marca/01-Embudo/. Lo cazo el propio agente de pasada. Esto lo hace
    determinista: un manifiesto que manda leer un archivo inexistente arranca ciego.
    """
    for man in AGENTES.rglob("AGENTE-*.yaml"):
        if "plantilla" in man.stem:
            continue
        en_ctx = False
        for linea in man.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\s*contexto_arranque:", linea):
                en_ctx = True
                continue
            if en_ctx:
                m = re.match(r"^\s*-\s*(.+?)\s*$", linea)
                if not m:                       # se acabo la lista
                    if linea.strip() and not linea.startswith(" "):
                        en_ctx = False
                    continue
                ruta = m.group(1)
                ruta = re.sub(r"\s+#.*$", "", ruta)   # quita comentario en linea
                ruta = ruta.strip().strip('"').strip("'")
                if ruta.startswith("~") or ruta.startswith("/"):
                    continue                    # ruta externa (repo web): no la juzgamos
                if not (VAULT / ruta).exists():
                    err(man.stem, f"contexto_arranque apunta a '{ruta}', que no existe",
                        "el agente arranca sin ese contexto: corrige la ruta en el manifiesto")


# Utilidades genéricas: son de todos, no se listan como propiedad .
SKILLS_VENDATED = {
                   "json-canvas", "excalidraw-diagram-skill", "superpowers", "defuddle"}


def validar_propiedad_skills():
    """Recuerda: cada skill (salvo vendored/deprecated) tiene UN agente dueño en su
    manifiesto. Una skill sin dueño no la mejora nadie y no puede ascender a sandbox."""
    # skills reales: SOLO las de primer nivel de cada dominio. NO las anidadas dentro
    # de subagentes (exos/agentes/<dom>/subagentes/*/skills) ni dentro de vendored
    # (superpowers/skills) — esas pertenecen al subagente o al paquete, no al dominio.
    reales = {}
    for dom in ("negocio", "media", "biblioteca", "_Meta"):
        sd = AGENTES / dom / "skills"
        if not sd.is_dir():
            continue
        for s in sd.iterdir():
            if s.is_dir() and not s.name.startswith("_"):
                skmd = s / "SKILL.md"
                if skmd.exists() and re.search(r"[Rr]eemplazada|[Dd]eprecad|[Rr]etirad",
                                               skmd.read_text(encoding="utf-8")[:400]):
                    continue
                reales.setdefault(s.name, []).append(dom)

    # skills declaradas en cada manifiesto
    declaradas = {}
    for man in AGENTES.rglob("AGENTE-*.yaml"):
        if "plantilla" in man.stem:
            continue
        ag = man.stem.replace("AGENTE-", "")
        en = False
        for linea in man.read_text(encoding="utf-8").splitlines():
            if re.match(r"^skills:", linea):
                en = True
                continue
            if en:
                m = re.match(r"^\s+-\s+([\w\-]+)", linea)
                if m:
                    declaradas.setdefault(m.group(1), []).append(ag)
                elif linea.strip() and not linea.startswith((" ", "#")):
                    en = False

    for nombre in sorted(reales):
        if nombre in SKILLS_VENDATED:
            continue
        duenos = declaradas.get(nombre, [])
        if not duenos:
            err("skills", f"'{nombre}' no tiene dueño en ningún manifiesto",
                "cada skill se lista en el skills: de su agente, o no la mejora nadie")
        elif len(duenos) > 1:
            err("skills", f"'{nombre}' tiene {len(duenos)} dueños: {', '.join(duenos)}",
                "una skill, un responsable")



def validar_hot():
    """hot.md tiene un limite propio (~500 tokens). Un hot.md gigante = corrupcion.

    Origen (21-jul): un `str.replace("", nuevo)` de agente-sistema —el find fallo y devolvio
    cadena vacia— inserto el texto entre CADA caracter: 8.049 copias, 6,9 MB, cabecera
    destruida. Se commiteo sin que nada saltara.
    """
    hot = VAULT / "mi-vida/hot.md"
    if not hot.exists():
        err("hot.md", "no existe", "es la memoria de trabajo: sin el, ningun agente arranca")
        return
    t = hot.read_text(encoding="utf-8")
    n = len(t.splitlines())
    # Saltar frontmatter YAML si existe (añadido 02-ago-2026: hot.md adopto el estándar)
    body = t
    if t.startswith("---"):
        parts = t.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].lstrip()
    if n > 200:
        err("hot.md", f"{n} lineas ({len(t)//1024} KB) — deberia rondar las 120",
            "senal de corrupcion o de falta de poda: restaura con `git show <commit>:mi-vida/hot.md`")
    if not body.startswith("# Contexto Caliente"):
        err("hot.md", "no empieza por su cabecera '# Contexto Caliente'",
            "alguien lo trunco o lo sobrescribio")


# ── 3. ROSTER CONGELADO ──────────────────────────────────────────────────────

def validar_roster():
    """Avisa si el roster crece. No lo impide: lo hace VISIBLE."""
    agentes = sorted(p.stem.replace("AGENTE-", "")
                     for p in AGENTES.rglob("AGENTE-*.yaml")
                     if "plantilla" not in p.stem)
    sandboxes = []
    docs = sum(1 for _ in VAULT.rglob("*.md")
               if ".git" not in str(_) and ".obsidian" not in str(_))
    # Una pieza en `manual` NO es un pipeline. El parte no puede
    # llamarlas pipelines: presumir de automatización que no existe fue el fallo que
    # destapó el radar en julio.
    manuales = 0
    for d in []:
        sj = d / "status.json"
        if d.is_dir() and sj.exists():
            try:
                if json.loads(sj.read_text(encoding="utf-8")).get("etapa") == "manual":
                    manuales += 1
            except (ValueError, OSError):
                pass
    autom = len(sandboxes) - manuales
    print(f"\n📋 ROSTER: {len(agentes)} agentes · {autom} pipelines · "
          f"{manuales} procedimientos manuales · {docs} documentos")
    print(f"   agentes: {', '.join(agentes)}")
    if docs > 2100:
        avi("documentos", f"{docs} .md en el cerebro",
            "crear exige jubilar: ¿qué se puede archivar? "
            "Un documento que ya no cambia lo que alguien hace es sedimento.")
    if len(sandboxes) > 12:
        avi("roster", f"{len(sandboxes)} pipelines activos",
            "cada uno es una pieza mas que su agente debe mantener viva. "
            "¿Alguno se puede jubilar, fusionar o volver skill manual?")


# ── 4. PROTECCIÓN DE FUENTES DE VERDAD ───────────────────────────────────────

def validar_modificacion_yamls():
    """Aviso al tocar un YAML marcado `veridico: true`. Avisa; ya no bloquea.

    ── Por qué cambió el 2026-07-30 (auditoría de agente-negocio, confirmada en el código) ──
    La versión anterior tenía tres defectos y entre los tres provocaron **19 commits
    con `--no-verify`** en dos días, 13 de ellos de un solo agente:

    1. **No había forma de cumplirlo.** Su propio mensaje de error decía «si la persona lo
       autorizó, usa --no-verify». Un candado cuya única salida es la llave maestra no
       es un candado: es un cartel.
    2. **Miraba el árbol de trabajo, no lo que ibas a guardar** (`git diff HEAD`). Un
       `cv.yaml` a medio editar bloqueaba commits que no lo tocaban, de otros agentes.
    3. **El precio del salto era desproporcionado, y esto es lo grave:** `--no-verify`
       no apaga este check, los apaga TODOS — el escáner de secretos, el guardián de
       archivos peligrosos, la doctrina congelada y el registro incremental. Un candado
       de bajo valor obligaba a apagar los de alto valor. El día que alguien tuviera una
       credencial en el diff con un YAML sucio, el escáner de secretos no habría corrido.

    Ahora: **solo mira lo que vas a commitear**, y **avisa en vez de bloquear**. La
    protección real de esos archivos no es prohibir la edición —se editan a diario— sino
    que las fechas salgan de la cronología validada, y eso es un invariante que se
    comprueba, no una puerta que se cierra. Pendiente de construir ese check.
    """
    try:
        # SOLO lo staged. Que un archivo abierto por otro agente bloquee tu commit es
        # el fallo que hizo que todo el mundo se acostumbrara a saltarse el guardián.
        salida = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=M"],
            cwd=VAULT, stderr=subprocess.DEVNULL).decode("utf-8")
        for yml in [f for f in salida.splitlines() if f.endswith((".yaml", ".yml"))]:
            path = VAULT / yml
            if path.exists() and "veridico: true" in path.read_text(encoding="utf-8").lower():
                avi(yml, "tocas una fuente marcada como verídica",
                    "comprueba que las fechas siguen saliendo de "
                    "Cronologia-Factica-Validada.yaml · ningún agente las inventa")
    except Exception:
        pass


# ── informe ──────────────────────────────────────────────────────────────────

# ── CARPETAS RAÍZ ────────────────────────────────────────────────────────────
# la regla ("no inventes carpetas raíz") era prosa. Ahora es esto.
CARPETAS_RAIZ = {
    "exos",      # el sistema. No lo editas; se reemplaza entero
    "modulos",   # los programas que añades
    "mi-vida",   # lo tuyo, y lo que sobrevive a reemplazar exos/
    "_secrets", "archive",
}


def validar_carpetas_raiz():
    for p in sorted(VAULT.iterdir()):
        if not p.is_dir() or p.name.startswith("."):
            continue
        if p.name not in CARPETAS_RAIZ:
            err(p.name, "carpeta raíz que no está en la lista oficial",
                "muévela dentro de una de las oficiales, o pídele a la persona que la añada "
                "(es doctrina: exos/CONGELADO.md)")



def avisar_scripts_sin_dueno():
    """Un .py que no aparece en ningún cron, skill ni manifiesto no lo mantiene nadie.

    El 06-ago había 49 scripts repartidos en cinco sitios y NADIE los revisaba: el validador
    contaba agentes, skills y documentos, pero no scripts. Salieron tanteos («scratch_cf»),
    migraciones de un solo uso ya ejecutadas, y uno —feedback_diario.py— apuntando a una
    ruta que no existía desde hacía semanas. Ninguno daba error: simplemente nadie los
    llamaba. Misma medicina que ya funciona con las skills sin dueño.
    """
    scripts = {p.name for p in (VAULT / "exos" / "scripts").glob("*.py")}
    if not scripts:
        return

    # Dónde puede estar declarado: crons, skills, manifiestos, protocolos, otros scripts.
    #
    # 16-ago-2026 · Aquí había dos agujeros que hacían que el sistema se acusara a sí
    # mismo el primer día, y los dos son del mismo tipo — mirar solo donde miraba el cerebro
    # de origen:
    #   · No se leía la RAÍZ, donde viven `CLAUDE.md` y `AGENTS.md`. Y ahí es justo donde
    #     se declara el ritual de apertura: `revisar_al_abrir.py` salía huérfano estando
    #     nombrado en el documento que más manda.
    #   · Un script solo lo declaraban archivos de FUERA de `scripts/`. Pero un módulo
    #     como `_raiz.py` lo importan sus vecinos, no un cron — y ser importado por ocho
    #     scripts es tener ocho dueños, no ninguno.
    menciones = set()
    archivos = list((VAULT).glob("*.md")) + list((VAULT).glob("*.json"))
    for zona in ("exos", "exos", "exos/agentes", "exos/githooks"):
        if (VAULT / zona).is_dir():
            archivos += list((VAULT / zona).rglob("*"))
    for f in archivos:
        if not f.is_file() or f.suffix not in (".md", ".yaml", ".sh", ".py", ".json", ""):
            continue
        try:
            texto = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for s in scripts:
            if s != f.name and s in texto:   # nadie se declara a sí mismo
                menciones.add(s)
    # El prefijo lo pone `programar_autoguardado.py` al crear la tarea programada.
    for plist in (Path.home() / "Library" / "LaunchAgents").glob("com.exos.*.plist"):
        try:
            texto = plist.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for s in scripts:
            if s in texto:
                menciones.add(s)

    huerfanos = sorted(scripts - menciones)
    if huerfanos:
        avi("scripts", f"{len(huerfanos)} sin dueño: no los llama ningún cron, skill ni manifiesto",
            f"{' · '.join(huerfanos[:6])}{' …' if len(huerfanos) > 6 else ''} → "
            "o se declara quién los usa, o se retiran: un script que nadie llama no lo mantiene nadie")


def avisar_sedimento():
    """Las tres formas en que el cerebro se vuelve a llenar de ruido solo (06-ago-2026).

    Las tres son de la misma familia: cosas que ya terminaron y siguen ocupando el sitio
    de las que no. Ninguna rompe nada, y por eso nadie las miraba: 55 de 92 tareas estaban
    cerradas dentro de la carpeta activa, y en `Triage/` había notas de hace tres semanas
    marcadas como urgentes. Aquí solo se cuenta y se avisa — nada se mueve solo.
    """
    hoy = dt.date.today()

    def dias(valor):
        try:
            return (hoy - dt.date.fromisoformat(str(valor)[:10])).days
        except (ValueError, TypeError):
            return None

    # 1 · tareas cerradas que siguen en la carpeta activa
    tareas_dir = VAULT / "mi-vida" / "tareas"
    cerradas, abiertas = [], []
    for p in tareas_dir.glob("TASK-*.md"):
        fm = frontmatter(p) or {}
        estado = fm.get("estado", "")
        if estado in ("completada", "archivo"):
            d = dias(fm.get("actualizado") or fm.get("creado"))
            if d is None or d >= 7:
                cerradas.append(p.name)
        elif estado in ("pendiente", "en-curso", "en-revision", "bloqueada"):
            abiertas.append(p.name)
    if cerradas:
        avi("tareas", f"{len(cerradas)} cerrada(s) hace más de 7 días siguen en la carpeta activa",
            "python3 exos/scripts/archivar_tareas.py · van a _cerradas/AAAA-MM/ "
            "conservando su ID, así que los enlaces del histórico no se rompen")

    # 2 · el cupo global de 40 se retiró el 15-ago con la taxonomía por
    #     especie: capar TODO lo vivo bloqueó el sistema con 26 intenciones aparcadas y
    #     9 decisiones esperando a la persona, ninguna archivable. Lo que se vigila ahora es
    #     el WIP y la bandeja, en validar_cupos(). Este aviso se queda fuera a propósito
    #     —y no como olvido— porque su remedio («crear_tarea.py ya lo impide») dejó de
    #     ser cierto: crear ya no se bloquea.

    # 3 · el foco es UNO. Un campo que se puede poner a diez cosas no elige nada: es
    #     exactamente lo que le paso a `prioridad` (4 urgentes y 19 altas de 36 tareas).
    focos = [p.name for p in tareas_dir.glob("TASK-*.md")
             if (frontmatter(p) or {}).get("foco") == "hoy"]
    if len(focos) > 1:
        avi("foco", f"{len(focos)} tareas marcadas `foco: hoy` — el foco es UNO",
            f"{' · '.join(focos)} → elige una y quita el campo a las demas")

    # 4 · triage estancado. Una bandeja que nadie vacía deja de ser una bandeja.
    viejas = []
    for p in (VAULT / "mi-vida" / "Triage").rglob("*.md"):
        d = dias((frontmatter(p) or {}).get("fecha"))
        if d is None or d >= 7:
            viejas.append(p.name)
    if viejas:
        avi("triage", f"{len(viejas)} nota(s) llevan más de 7 días sin procesar",
            "o se convierte en tarea, o se archiva, o se borra · lo que lleva tres semanas "
            "en una bandeja no era urgente")


def validar_safe_fail_skills():
    """Recuerda: toda skill declara su safe-fail antes de poder ejecutar acciones.

    TRINQUETE, no purga. Al montar esto (30-jul) faltaba en 30 de 48 skills. Convertirlo
    en error habría bloqueado todos los commits hasta arreglar 30 archivos — o sea, habría
    empujado a todo el mundo al --no-verify, que es justo cómo muere un sistema de
    candados. Así que: aquí solo cuenta, y `guardian_doctrina.py` BLOQUEA las skills que
    se toquen. Lo viejo se arregla cuando se pase por ahí; lo nuevo no puede nacer mal.
    """
    faltan = []
    for skill in VAULT.glob("exos/agentes/**/skills/*/SKILL.md"):
        rel = str(skill.relative_to(VAULT))
        if any(v in rel for v in SKILLS_VENDATED):
            continue
        if "safe-fail" not in (frontmatter(skill) or {}):
            faltan.append(rel)
    if faltan:
        avi("skills", f"{len(faltan)} sin 'safe-fail' declarado (deuda, se arregla al tocarlas)",
            "sin safe-fail una skill es de solo lectura · las que se editen ya lo exigen")


def avisar_traspasos_sin_cerrar():
    """Un encargo completado cuya tarea nadie actualizó = el que encargó no se enteró.

    `PROTOCOLO — Traspaso entre agentes y repos` §4: cerrar un encargo son DOS gestos —
    marcarlo completado y marcar su checkpoint en la tarea que declara `cierra:`. Si solo
    se hace el primero, el trabajo está hecho y nadie lo sabe. Es la otra mitad del fallo
    del 30-jul: entonces el encargo no llegaba; esto evita que tampoco vuelva.
    """
    docs = raiz_web() / "docs"          # raiz_web() ya honra NOMA_WEB
    if not docs.exists():
        return
    for f in sorted(docs.glob("ENCARGO*.md")):
        fm = frontmatter(f)
        if fm.get("estado") not in ("completado", "cerrado"):
            continue
        tid = fm.get("cierra")
        if not tid:
            avi(f.name[:44], "encargo completado sin declarar a qué tarea pertenece",
                "añádele `cierra: TASK-NNN` para que el cierre sea trazable")
            continue
        cand = list(TAREAS.glob(f"{tid}*.md"))
        if not cand:
            avi(f.name[:44], f"encargo completado que dice cerrar {tid}, y esa tarea no existe")
            continue
        cuerpo = cand[0].read_text(encoding="utf-8", errors="ignore")
        if "- [ ]" in cuerpo and "- [x]" not in cuerpo:
            avi(tid, f"«{f.name[:38]}» está completado y {tid} no tiene ningún paso marcado",
                "cerrar un traspaso son dos gestos: el encargo Y el checkpoint")


def avisar_deriva_perfiles():
    """¿`perfiles-agentes.yaml` sigue diciendo la verdad?

    Existe por el fallo del 30-jul: el archivo declaraba que agente-web alcanzaba una carpeta
    que en realidad tenía negada, la persona se fio para dejarle un encargo y planificó mal.
    Una declaración que puede desviarse en silencio es una regla que hay que recordar.
    """
    if not (Path.home() / ".gemini" / "config" / "projects").exists():
        return                      # otra máquina o CI: no hay nada que comparar
    try:
        r = subprocess.run(
            [sys.executable, str(VAULT / "exos/scripts/aplicar_perfiles.py"), "--verificar"],
            capture_output=True, text=True, cwd=str(VAULT), timeout=25,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if r.returncode != 0:
        lineas = r.stdout.splitlines()
        contradicciones = sum(1 for l in lineas if "contradicción" in l or "NEGADO" in l)
        sin_aplicar = sum(1 for l in lineas if "declarado y no aplicado" in l)

        # 16-ago-2026 · Antes se sumaban las tres cosas y salía «22 desajustes» el primer
        # día. Pero no son lo mismo, y confundirlas convierte el estreno en un reproche:
        #   · «declarado y no aplicado» a secas = **todavía no lo has aplicado**. Es el
        #     estado normal de un sistema recién instalado, no un fallo.
        #   · una contradicción = se aplicó y ahora dice una cosa distinta. ESO sí importa,
        #     porque los agentes planifican leyendo el archivo, no la herramienta.
        if contradicciones:
            avi("perfiles", f"{contradicciones} contradicción(es) entre lo declarado y lo aplicado",
                "los agentes planifican con ese archivo · detalle: "
                "aplicar_perfiles.py --verificar")
        elif sin_aplicar:
            avi("perfiles", "los permisos están declarados pero aún no aplicados",
                "es lo normal recién instalado · para activarlos: "
                "aplicar_perfiles.py --herramienta <la tuya> --aplicar")


def contar_marcadores_guardian(lineas):
    """Cuenta UNLOCK=1 y --no-verify leyendo el CAMPO 2 (marcador), no la línea entera.

    Separado de avisar_saltos_guardian() para poder probarlo sin tocar disco. El
    formato del log es `fecha hora | marcador | sha | asunto`: el asunto es texto
    libre y en este cerebro habla constantemente de los propios guardianes ("feat
    (guardian): ... UNLOCK con ADR"), así que buscar la subcadena en la línea
    entera cuenta commits dos veces cuando el asunto menciona el otro marcador.
    Ya pasó una vez (15-ago): un dato mal agregado así se propagó a doctrina.
    Líneas malformadas (menos de 2 campos) no cuentan en ninguna bolsa y no rompen
    el validador.
    """
    n_unlock = n_noverify = 0
    for l in lineas:
        partes = l.split("|")
        if len(partes) < 2:
            continue
        marcador = partes[1].strip()
        if "UNLOCK=1" in marcador:
            n_unlock += 1
        elif "no-verify" in marcador:
            n_noverify += 1
    return n_unlock, n_noverify


def avisar_saltos_guardian():
    """Un candado que se salta en silencio deja de ser un candado.

    Vale igual para reescribir los permisos de un programa: se puede hacer con la
    autorización de la persona, pero no puede pasar sin que él se entere al día siguiente.
    """
    log_perf = VAULT / "exos" / "logs" / "perfiles-aplicados.log"
    if log_perf.exists():
        n = len([l for l in log_perf.read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith(" ")])
        if n:
            avi("perfiles", f"{n} vez/veces se han reescrito los permisos de una herramienta",
                "desde perfiles-agentes.yaml · detalle en exos/logs/perfiles-aplicados.log")

    log = VAULT / "exos" / "logs" / "saltos-guardian.log"
    if not log.exists():
        return
    try:
        lineas = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    except OSError:
        return
    if not lineas:
        return
    # UNLOCK=1 y --no-verify no son lo mismo: un UNLOCK es un desbloqueo con permiso
    # explícito y el gancho se ejecuta igual (queda registrado aquí mismo); solo
    # --no-verify esquiva el gancho entero. Juntarlos bajo "se han saltado el
    # guardián" es falso para los UNLOCK, y ese dato mal agregado ya indujo una vez
    # a un agente a escribir un número incorrecto en un documento de doctrina (15-ago).
    n_unlock, n_noverify = contar_marcadores_guardian(lineas)
    recientes = lineas[-5:]
    avi("guardián",
        f"{len(lineas)} commit(s) con el guardián desbloqueado: "
        f"{n_unlock} con UNLOCK=1 (permiso explícito, el gancho corrió igual) · "
        f"{n_noverify} con --no-verify (salto real del gancho)",
        "últimos: " + " · ".join(l.split("|")[1].strip() + " " + l.split("|")[3].strip()[:40]
                                 for l in recientes if l.count("|") >= 3))


def main():
    breve = "--breve" in sys.argv
    validar_carpetas_raiz()
    validar_safe_fail_skills()
    validar_tareas()
    validar_cupos()                  # cupos por especie (propuesta 15-ago)
    validar_referencias_doctrina()   # lo que MANDA no puede citar algo que ya no existe
    validar_contexto_manifiestos()   # cada ruta de arranque de un agente existe
    validar_propiedad_skills()       # cada skill tiene un agente dueño, o no la mejora nadie
    validar_hot()                    # hot.md integro (21-jul: se corrompio en silencio)
    validar_modificacion_yamls()     # impide modificar YAMLs verídicos sin permiso
    if not breve:
        validar_roster()
        avisar_saltos_guardian()     # los atajos existen, pero no en silencio
        avisar_deriva_perfiles()     # lo declarado tiene que ser lo aplicado
        avisar_traspasos_sin_cerrar()  # un encargo cerrado que nadie devolvió
        avisar_sedimento()             # lo que terminó y sigue ocupando sitio (06-ago)
        avisar_scripts_sin_dueno()     # un .py que nadie llama no lo mantiene nadie (06-ago)

    if errores:
        print(f"\n❌ {len(errores)} ERRORES (rompen la trazabilidad de tu sistema)\n")
        for donde, msg, arreglo in errores:
            print(f"  · {donde}: {msg}")
            if arreglo:
                print(f"      → {arreglo}")

    if avisos and not breve:
        print(f"\n⚠️  {len(avisos)} avisos (no rompen nada, conviene mirarlos)\n")
        for donde, msg, arreglo in avisos:
            print(f"  · {donde}: {msg}")
            if arreglo:
                print(f"      → {arreglo}")

    if not errores:
        print(f"\n✅ Estado válido. Tu sistema cuenta la verdad."
              + (f" ({len(avisos)} avisos)" if avisos else ""))
        return 0
    print(f"\n   Arréglalo y vuelve a pasar el validador. "
          f"Nada de esto lo tiene que cazar la persona a mano.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
