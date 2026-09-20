#!/usr/bin/env python3
"""revisar_al_abrir.py — lo que nadie comprueba porque el que debía ya se fue.

POR QUÉ EXISTE, y es el motivo de fondo de dos problemas que llevaban meses volviendo:

**1 · El cierre de sesión no se puede obligar.** El guardián del registro vive en el
`pre-commit`, así que **solo comprueba a quien se acerca a la puerta**. Una sesión que se
queda sin tokens, que se cierra o que se cae **nunca ejecuta `git commit`** — y nada la
comprueba jamás. El 11-ago la web se quedó un día entera con trabajo sin guardar y solo
salió a la luz porque la puerta de EXOS se negó a certificar una entrega.

  ⇒ El cierre depende de que el agente sobreviva. **La apertura, no.** Por eso esto se
    ejecuta al ABRIR: no evita que una sesión muera a medias, pero convierte un problema
    invisible durante días en lo primero que ve el siguiente. Es el máximo que se puede.

**2 · Todos los guardianes comprueban que las cosas estén BIEN; ninguno, que sirvan.**
El de referencias caza enlaces rotos; el validador, formatos; el catálogo, archivos sin
clasificar dentro de sus zonas. Ninguno se pregunta *«¿esto sigue haciendo algo?»* — y así
es como se acumula ruido sin que salte nada. El 12-ago quedó un archivo inútil en el cerebro
y **ningún guardián dijo nada**, porque ninguno tenía esa pregunta.

  ⇒ El valor de un documento es criterio y no se automatiza. **Sus síntomas sí**: nadie lo
    enlaza, nadie lo toca en meses, sigue en borrador desde hace medio año, tiene tres
    líneas. Eso es una consulta, no una opinión. **Esto no borra nada**: pone delante una
    lista corta con su motivo, y decides tú.

**3 · Una fuente única no sirve de nada si nadie regenera lo que cuelga de ella.**
El 13-ago se descubrió que las cuatro salidas del CV en inglés llevaban **seis días** sin
rehacerse: `cv.yaml` se editó el 11 y solo se regeneró el español. A los dos PDF ingleses
les faltaba el perfil reescrito y **todos los nombres de empresa de dos etapas** — dieciséis
años de trayectoria sin una empresa citada, que en un ATS es lo que descarta. Nadie lo vio
porque **ningún guardián comparaba fechas**: el validador mira formatos, el de referencias
mira enlaces, y una salida vieja está perfectamente bien formada.

  ⇒ Salió a la luz de casualidad, cruzando dos CV para otra cosa. Eso no es un método.
    Comparar la fecha de una fuente con la de sus salidas **sí es una consulta**, así que
    se hace aquí. Lo versionado se mide por fecha de commit —un `git clone` iguala todos
    los `mtime`, y el aviso desaparecería justo en la máquina donde más falta haría— y lo
    que está fuera de git, por `mtime`. **Cada pareja con el mismo reloj**: mezclarlos
    inventaba desfases de horas que no existían.

Uso:
    revisar_al_abrir.py                 # el parte, para enseñárselo a la persona
    revisar_al_abrir.py --podar         # solo los candidatos a poda, en detalle
    revisar_al_abrir.py --salidas       # solo la comprobación fuente → salidas
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault, raiz_web, hay_web  # noqa: E402

VAULT = raiz_vault()
# 18-sep-2026 · La web es OPCIONAL: EXOS ya no la lleva —construir webs es un programa
# aparte—. Vigilar un repositorio que no existe llena el parte de avisos sobre nada, y el
# ruido es exactamente cómo se enseña a no leerlo.
REPOS = [("cerebro", VAULT)]
if hay_web():
    REPOS.append(("web", raiz_web()))

# Horas a partir de las cuales un cambio sin guardar deja de ser «estoy trabajando» y pasa
# a ser «alguien se fue». Cuatro es una sesión larga; más que eso, ya no hay nadie.
HORAS_HUERFANO = 4

# Un documento sin tocar en tres meses que además no enlaza nadie es candidato. Menos
# tiempo daría falsos positivos con lo que es estable a propósito —una doctrina buena no
# se toca— y por eso hace falta que SE CUMPLAN LAS DOS cosas, no una.
DIAS_QUIETO = 90
LINEAS_MINIMAS = 6
ESTADOS_TIBIOS = ("semilla", "borrador", "propuesta", "en-pruebas")

SALTAR = {".git", "node_modules", ".next", "_Vendored", ".worktrees", "archive",
          "sesiones", "tareas", "decisions", "generados", "Triage"}

# ── El parte para la persona ───────────────────────────────────────────────────────
# CLAUDE.md paso 4 ya ordena enseñárselo, EN MAYÚSCULAS, y no se cumple: su queja del
# 15-ago fue literal, «nunca nadie me dice lo que hay pendiente». Una orden en prosa no
# es un mecanismo. Esto lo imprime ya formateado para pegar en el chat, de modo que
# enseñárselo cueste menos que redactarlo a mano.
DIAS_ENTRE_REVISIONES = 7
MARCA_FRIAS = VAULT / "exos" / "logs" / "ultima-revision-frias.txt"


def toca_revisar_frias(hoy, marca) -> bool:
    """¿Han pasado ya 7 días desde la última vez que se le enseñó la lista?"""
    try:
        ultima = dt.date.fromisoformat(marca.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return True          # sin marca fiable, se enseña
    return (hoy - ultima).days >= DIAS_ENTRE_REVISIONES


def sellar_revision_frias(hoy, marca) -> None:
    marca.parent.mkdir(parents=True, exist_ok=True)
    marca.write_text(hoy.isoformat(), encoding="utf-8")


def bandeja() -> list:
    """Lo que espera una decisión de la persona, con su next_action tal cual."""
    tareas = VAULT / "mi-vida" / "tareas"
    out = []
    for p in sorted(tareas.glob("TASK-*.md")):
        texto = p.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"^estado:\s*en-revision\s*$", texto, re.M):
            continue
        m = re.search(r'^next_action:\s*"?(.+?)"?\s*$', texto, re.M)
        accion = m.group(1) if m else "(sin next_action)"
        out.append((p.stem[:40], accion))
    return out


def parte() -> list:
    """El texto que el agente pega en el chat. Sin adornos: se lee en el móvil."""
    import archivar_tareas

    hoy = dt.date.today()
    lineas = []

    pendientes = bandeja()
    if pendientes:
        lineas.append(f"**Tu bandeja — {len(pendientes)} esperan una decisión tuya:**")
        for nombre, accion in pendientes:
            lineas.append(f"· `{nombre}` — {accion[:150]}")
        lineas.append("")

    if toca_revisar_frias(hoy, MARCA_FRIAS):
        frias = archivar_tareas.frias(hoy)
        if frias:
            lineas.append(f"**{len(frias)} tareas frías** (backlog sin tocar en 30+ días). "
                          f"Dime cuáles archivo:")
            for i, (p, dias) in enumerate(frias, 1):
                lineas.append(f"{i}. `{p.stem[:48]}` — {dias} días")
            lineas.append("")
            lineas.append("_Archivar no borra: se mueve a `_cerradas/` conservando el ID._")

    if not lineas:
        return ["✓ Nada espera tu decisión y no hay tareas frías."]
    return lineas


# ── Fuentes únicas y lo que cuelga de ellas ───────────────────────────────────
# Para añadir una fábrica nueva: una entrada más. `fuente` siempre es del cerebro;
# cada salida lleva su repo delante porque algunas viven en el de la web.
# La `orden` se imprime tal cual: tiene que poder copiarse y pegarse.
FABRICAS = [
    # ⚠️ VACÍA A PROPÓSITO — aquí van TUS cadenas de «fuente → salidas».
    #
    # 16-ago-2026 · Aquí venían dos cadenas del cerebro de origen: el CV de una persona y su
    # identidad de marca, con sus nombres de archivo y sus carpetas. Al sustituir el nombre
    # propio, las rutas quedaban con un sustantivo común en mitad de un nombre de archivo:
    # no filtran nada y **no significan nada**. Un texto personal anonimizado es peor que
    # uno personal, porque pasa los filtros y sigue sin tener sentido. Se van enteras.
    #
    # QUÉ PONER AQUÍ. Cualquier cosa tuya que se GENERE a partir de otra: un PDF que sale
    # de un YAML, unos textos que salen de un documento maestro, una imagen que sale de una
    # plantilla. Declararla aquí hace que el sistema te avise cuando la fuente cambió y la
    # salida se quedó vieja — que es el error que nadie ve, porque nada falla: simplemente
    # estás enseñando una versión antigua.
    #
    # La forma, con un ejemplo comentado:
    #
    # {
    #     "que": "Tarifas",
    #     "fuente": "mi-vida/ejemplo.yaml",
    #     "orden": "python3 exos/scripts/generar_tarifas.py",   # copiable tal cual
    #     "salidas": [
    #         ("cerebro", "mi-vida/EJEMPLO.md"),
    #         ("web",   "public/tarifas.json"),
    #     ],
    # },
]


def _git(repo: Path, *args) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, timeout=30)
        return r.stdout
    except Exception:
        return ""


def encima_de_exos() -> list[str]:
    """Lo que ha aparecido encima de EXOS desde la última vez.

    18-sep-2026 · la persona: «que la estructura esté preparada para que cualquier cosa que se
    ponga haya una REACCIÓN ACTIVA para gestionarlo y detectarlo». Un catálogo que hay que
    abrir no es una reacción: es un cajón. Esto salta solo, aquí, sin que nadie pregunte.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import modulos as _m
        return _m.novedades()
    except Exception:
        return []


def sin_guardar() -> list[str]:
    """Trabajo que alguien dejó a medias y ya no sostiene nadie."""
    avisos = []
    ahora = time.time()
    for nombre, repo in REPOS:
        if not (repo / ".git").exists():
            continue
        estado = [l for l in _git(repo, "status", "--porcelain").splitlines() if l.strip()]
        if not estado:
            continue

        # La antigüedad se mide por el archivo modificado más RECIENTE: si alguien está
        # trabajando ahora mismo, eso es de hace un minuto y no se avisa.
        reciente = 0.0
        for linea in estado:
            ruta = repo / linea[3:].strip().strip('"')
            try:
                reciente = max(reciente, ruta.stat().st_mtime)
            except OSError:
                # Un archivo BORRADO no se puede fechar: ya no está. Se usa la fecha de su
                # carpeta, que sí cambia al borrar dentro. Sin esto, un borrado recién
                # hecho se anunciaba como «hace 42 días» — el script mintiendo sobre su
                # propio trabajo, que es la peor clase de falso positivo.
                try:
                    reciente = max(reciente, ruta.parent.stat().st_mtime)
                except OSError:
                    continue
        horas = (ahora - reciente) / 3600 if reciente else 0

        if horas >= HORAS_HUERFANO:
            cuando = f"{horas/24:.0f} días" if horas >= 48 else f"{horas:.0f} horas"
            avisos.append(
                f"⛔ {nombre}: {len(estado)} archivo(s) sin guardar, el último tocado hace "
                f"{cuando}.\n"
                f"     Nadie lo sostiene: la sesión que lo hizo ya cerró. **Cualquier "
                f"`git checkout` lo borraría** —\n"
                f"     y si son borrados, los resucitaría. Guárdalo o pregunta de quién es "
                f"ANTES de tocar nada."
            )
    return avisos


def _repo(nombre: str) -> Path:
    return dict(REPOS)[nombre]


# Margen antes de considerar que una salida se ha quedado atrás. No es holgura
# gratuita: la misma regeneración se comitea en el cerebro y en la web a horas
# distintas, y sin margen eso se anunciaba como desfase cada día. Lo que esto
# busca son días de retraso, no minutos.
HORAS_MARGEN = 12


def _fecha(repo: Path, rel: str, base: str) -> float | None:
    """Cuándo se actualizó ese archivo. `None` si no existe.

    `base` decide con qué reloj se mide, y no es un detalle: comparar una fecha
    de commit con un `mtime` es comparar dos cosas distintas, y así salían
    desfases de mentira. Se mide igual a los dos lados de cada pareja.

    · `commit` — para lo versionado. Un `git clone` pone la misma hora a todo el
      árbol, así que el mtime ahí no distingue nada. Si el archivo está tocado
      sin comitear, manda el árbol sobre el historial.
    · `mtime`  — para lo que está fuera de git (los binarios de `render/`), donde
      es lo único que hay.
    """
    ruta = repo / rel
    if not ruta.exists():
        return None
    if base == "mtime":
        return ruta.stat().st_mtime
    salida = _git(repo, "log", "-1", "--format=%ct", "--", rel).strip()
    commit = float(salida) if salida else 0.0
    sucio = bool(_git(repo, "status", "--porcelain", "--", rel).strip())
    if not commit or sucio:
        return max(commit, ruta.stat().st_mtime)
    return commit


def _versionado(repo: Path, rel: str) -> bool:
    return bool(_git(repo, "ls-files", "--", rel).strip())


def salidas_desfasadas() -> list[str]:
    """Fuentes que se tocaron después que lo que se genera desde ellas."""
    avisos = []
    cerebro = _repo("cerebro")
    margen = HORAS_MARGEN * 3600

    for fab in FABRICAS:
        viejas = []
        for repo_nombre, rel in fab["salidas"]:
            repo = _repo(repo_nombre)
            if not (repo / ".git").exists() and repo_nombre != "cerebro":
                continue                  # ese repo no está en esta máquina

            # Cada pareja se mide con el mismo reloj: si la salida no está en git,
            # la fuente también se mide por mtime.
            base = "commit" if _versionado(repo, rel) else "mtime"
            t_fuente = _fecha(cerebro, fab["fuente"], base)
            if t_fuente is None:
                break                     # la fuente se movió: no es asunto de esto

            t = _fecha(repo, rel, base)
            if t is None:
                viejas.append((repo_nombre, rel, "no existe"))
            elif t_fuente - t > margen:
                dias = round((t_fuente - t) / 86400)
                plural = "día" if dias == 1 else "días"
                viejas.append((repo_nombre, rel, f"{dias} {plural} por detrás"))

        if viejas:
            avisos.append(
                f"🕗 {fab['que']}: la fuente `{fab['fuente']}` es más nueva que "
                f"{len(viejas)} de sus {len(fab['salidas'])} salidas.\n"
                + "\n".join(f"     · {r} ({n}) — {m}" for n, r, m in viejas)
                + f"\n     Se arregla ejecutándolo:\n     {fab['orden']}"
            )
    return avisos


def _enlazados(raiz: Path) -> set[str]:
    """Nombres de archivo citados por alguien. Basta el nombre: si se cita, se usa."""
    citados: set[str] = set()
    patron = re.compile(r"[\[\(`]([^\]\)`\n]{4,120})[\]\)`]")
    for f in raiz.rglob("*.md"):
        if SALTAR & set(f.relative_to(raiz).parts):
            continue
        try:
            texto = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in patron.finditer(texto):
            citados.add(Path(m.group(1).strip()).name)
    return citados


def candidatos_a_poda(raiz: Path, detalle: bool = False) -> list[str]:
    """Síntomas, no juicios. La decisión sigue siendo de la persona."""
    citados = _enlazados(raiz)
    ahora = time.time()
    hallazgos: list[tuple[str, str]] = []

    for f in raiz.rglob("*.md"):
        rel = f.relative_to(raiz)
        if SALTAR & set(rel.parts):
            continue
        try:
            texto = f.read_text(encoding="utf-8", errors="ignore")
            lineas = [l for l in texto.splitlines() if l.strip()]
        except OSError:
            continue

        if f.name in citados:
            continue                      # alguien lo cita: no es huérfano

        dias = (ahora - f.stat().st_mtime) / 86400
        estado = re.search(r"^estado:\s*(\S+)", texto, re.M)
        estado = estado.group(1) if estado else ""

        motivo = None
        if len(lineas) <= LINEAS_MINIMAS:
            motivo = f"{len(lineas)} líneas y nadie lo cita"
        elif estado in ESTADOS_TIBIOS and dias >= DIAS_QUIETO:
            motivo = f"en `{estado}` desde hace {dias/30:.0f} meses, sin que nadie lo cite"
        elif dias >= DIAS_QUIETO * 2:
            motivo = f"{dias/30:.0f} meses sin tocarse y sin que nadie lo cite"

        if motivo:
            hallazgos.append((str(rel), motivo))

    hallazgos.sort()
    if not hallazgos:
        return []
    if detalle:
        return [f"· {r}\n     {m}" for r, m in hallazgos]

    # En el parte de apertura solo van los tres primeros: una lista larga se ignora, y
    # entonces habríamos construido otro guardián que nadie lee.
    salida = [f"🧹 {len(hallazgos)} candidato(s) a poda. Los tres primeros:"]
    salida += [f"     · {r} — {m}" for r, m in hallazgos[:3]]
    if len(hallazgos) > 3:
        salida.append("     Lista entera: `revisar_al_abrir.py --podar`")
    return salida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--podar", action="store_true", help="solo la lista de poda, entera")
    ap.add_argument("--salidas", action="store_true", help="solo la comprobación fuente → salidas")
    ap.add_argument("--parte", action="store_true",
                    help="el parte pegable en el chat: bandeja de la persona y tareas frías")
    a = ap.parse_args()

    if a.parte:
        for linea in parte():
            print(linea)
        sellar_revision_frias(dt.date.today(), MARCA_FRIAS)
        return 0

    if a.salidas:
        desfase = salidas_desfasadas()
        if not desfase:
            print("✓ Todas las salidas están al día con su fuente.")
            return 0
        print("\n🕗 SALIDAS DESFASADAS\n")
        for x in desfase:
            print("  " + x + "\n")
        return 0

    if a.podar:
        lista = candidatos_a_poda(VAULT, detalle=True)
        print(f"\n🧹 CANDIDATOS A PODA — {len(lista)}\n")
        for x in lista:
            print("  " + x)
        print("\n  Esto NO borra nada. Son síntomas: nadie los cita, llevan meses quietos\n"
              "  o están casi vacíos. Decide tú, archivo a archivo.\n")
        return 0

    nuevo_encima = encima_de_exos()
    huerfanos = sin_guardar()
    desfase = salidas_desfasadas()
    poda = candidatos_a_poda(VAULT)

    # Va PRIMERO y en su propio bloque: es lo único de este parte que la persona acaba de
    # hacer a propósito. Enterrarlo entre avisos de mantenimiento sería no reaccionar.
    if nuevo_encima:
        print("\n📦 ENCIMA DE EXOS — algo nuevo desde la última vez\n")
        for x in nuevo_encima:
            print("  " + x)
        print()

    if not huerfanos and not desfase and not poda:
        if not nuevo_encima:
            print("✓ Nada sin guardar, nada desfasado y nada que podar.")
        return 0

    print("\n🔎 AL ABRIR — lo que nadie comprobó porque la sesión anterior ya se había ido\n")
    for x in huerfanos:
        print("  " + x + "\n")
    for x in desfase:
        print("  " + x + "\n")
    for x in poda:
        print("  " + x)
    print()
    # Código 0 siempre: esto INFORMA al abrir, no bloquea. Un aviso que impide trabajar
    # se desactiva el segundo día, y entonces deja de avisar para siempre.
    return 0


if __name__ == "__main__":
    sys.exit(main())
