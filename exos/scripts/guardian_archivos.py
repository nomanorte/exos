#!/usr/bin/env python3
"""guardian_archivos.py — detecta archivos peligrosos para versionar, en el acto.

Nació el 2026-07-29: un `git add .` estuvo a punto de subir al repositorio dos archivos
de cookies de sesión y un entorno virtual entero. Ninguna regla escrita lo habría evitado:
el agente que creó las cookies estaba a cuarenta pasos de haber leído nada sobre .gitignore.

Doctrina: **toda regla que se pueda convertir en comprobación, deja de ser una regla.**
Este script es esa conversión. Se usa en dos momentos:

  --hook      Desde un hook PostToolUse de Claude Code. Lee el JSON del hook por stdin y
              avisa EN EL ACTO, justo después de que un agente cree o edite el archivo.
  --staged    Desde el pre-commit de git. Revisa lo que está a punto de entrar al commit.
              Salida distinta de 0 = bloquear el commit.
  <rutas>     Comprobación manual de rutas sueltas.

Un archivo solo se marca si es peligroso **y** git NO lo está ignorando ya. Si ya está en
.gitignore, silencio: el problema está resuelto y avisar sería ruido.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# 15-ago-2026: antes `.parent.parent.parent` — la misma atadura que `parents[2]`,
# escrita de otra forma. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()

# ── Peligroso por lo que ES (el nombre basta) ────────────────────────────────
# Un archivo de cookies no contiene ningún patrón de clave de API: es peligroso
# por su naturaleza, no por su contenido. Por eso esta lista existe aparte.
PATRONES_NOMBRE = [
    (r"cookies?\.txt$",              "cookies de sesión (equivalen a estar logueado)"),
    (r"\.cookies$",                  "cookies de sesión"),
    (r"\.pem$",                      "certificado o clave privada"),
    (r"\.key$",                      "clave privada"),
    (r"\.p12$|\.pfx$|\.keystore$",   "almacén de certificados"),
    (r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$", "clave SSH privada"),
    (r"(^|/)\.netrc$",               "credenciales de red en texto plano"),
    (r"(^|/)\.env($|\.)",            "variables de entorno con secretos"),
    (r"service[-_]account.*\.json$", "credenciales de servicio de Google"),
    (r"credentials?\.json$",         "credenciales"),
    (r"\.sql$|\.dump$|\.sqlite3?$",  "volcado de base de datos (puede llevar datos de leads)"),
    (r"(^|/)\.DS_Store$",            "basura de macOS"),
]

# ── Peligroso por dónde VIVE (carpetas que nunca se versionan) ───────────────
PATRONES_RUTA = [
    (r"(^|/)\.venv/|(^|/)venv/",  "entorno virtual de Python (miles de archivos regenerables)"),
    (r"(^|/)node_modules/",       "dependencias de Node (regenerables)"),
    (r"(^|/)__pycache__/",        "caché de Python"),
    (r"(^|/)\.next/",             "build de Next.js"),
    (r"(^|/)_secrets/",           "directorio de secretos (crítico)"),
    (r"(^|/)(datos|clientes|leads)/","datos personales o de clientes (crítico)"),
]

# ── MATERIA PRIMA: no es peligrosa, es que aquí no cabe ──────────────────────
# 06-sep-2026 · Faltaba, y es el error más común de quien llega sin saber cómo
# funciona git por dentro: mete el PDF, el vídeo o las fotos «porque son de este
# proyecto». Es razonable, y sale caro.
#
# POR QUÉ. Git guarda TODAS las versiones de TODO. Un archivo de texto que cambia
# guarda las líneas que cambiaron; un vídeo de 200 MB que cambia guarda otros
# 200 MB. Y aquí está lo que no se ve venir: **borrarlo después no lo quita**. Se
# queda en el historial para siempre, y cada copia futura del proyecto se lo baja
# entero. Un repositorio así tarda minutos en clonarse y no hay vuelta atrás
# sencilla.
#
# QUÉ SÍ VA AQUÍ: lo que son líneas — .md, .yaml, .py, .sh, .json, .ts. Cosas que
# se pueden comparar versión a versión, que es de lo que va todo esto.
#
# QUÉ HACE LA GENTE QUE LO TIENE RESUELTO: la materia prima vive fuera (Drive,
# Dropbox, iCloud, un disco) y aquí entra **una nota que la describe y la enlaza**.
# La nota pesa 2 KB, se busca, se versiona y explica POR QUÉ ese archivo importa —
# que es justo lo que un vídeo no te puede decir.
PATRONES_MATERIA_PRIMA = [
    (r"\.(mov|mp4|avi|mkv|webm|m4v)$",     "vídeo"),
    (r"\.(wav|mp3|m4a|aac|flac|aiff?)$",   "audio"),
    (r"\.pdf$",                            "PDF"),
    (r"\.(psd|ai|sketch|fig|xd|indd)$",    "archivo de diseño"),
    (r"\.(zip|rar|7z|tar|gz|dmg|iso)$",    "comprimido o imagen de disco"),
    (r"\.(raw|cr2|nef|arw|dng|heic|tiff?)$", "foto sin procesar"),
    (r"\.(docx?|xlsx?|pptx?|pages|numbers|keynote)$", "documento de ofimática"),
]

# Lo que no cae por extensión, cae por peso. Así una captura de 40 KB entra sin
# molestar y un PNG de 12 MB no. El límite es generoso a propósito: no se trata de
# perseguir kilobytes, sino de parar lo que va a doler dentro de un año.
LIMITE_PESO = 5 * 1024 * 1024

# ── Peligroso por lo que DICE dentro ─────────────────────────────────────────
PATRONES_CONTENIDO = [
    (r"sk_live_[A-Za-z0-9]{10,}",            "clave de Stripe en vivo"),
    (r"rk_live_|whsec_[A-Za-z0-9]{10,}",     "credencial de Stripe"),
    (r"\bntn_[A-Za-z0-9]{20,}",              "token de integración de Notion"),
    (r"\bre_[A-Za-z0-9]{20,}",               "clave de Resend"),
    (r"postgres(ql)?://[^\s:]+:[^\s@]+@",    "cadena de conexión con contraseña"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----",  "clave privada"),
    (r"\bAKIA[0-9A-Z]{16}\b",                "clave de acceso de AWS"),
    (r"\bghp_[A-Za-z0-9]{30,}",              "token de GitHub"),
    (r"\b[0-9]{8,10}:AA[A-Za-z0-9_-]{30,}",  "token de bot de mensajería"),
]

MAX_SNIFF = 512 * 1024  # no leemos archivos enormes buscando patrones

# ── Los que vigilan no se vigilan a sí mismos ────────────────────────────────
# Un detector de secretos contiene los patrones como texto, así que se marcaría
# solo. Pasó a los 3 minutos de escribir este script (2026-07-29).
EXENTOS = [
    r"guardian_archivos\.py$",
    r"(^|/)(?:[.]githooks|exos/githooks)/",
    r"(^|/)\.git/hooks/",
    r"hooks-pre-commit",
    r"(^|/)PROTOCOLO — Permisos de agentes\.md$",
    # Los flujos de GitHub llevan los mismos patrones de detección como texto: son
    # el guardián en el servidor. Gitignorarlos sería absurdo — dejarían de correr.
    r"(^|/)\.github/workflows/",
    r"guardian-public-json\.sh$",
    # Mismo caso que los dos de arriba, y ya van cinco en este sistema: **quien enuncia
    # la regla no puede ser víctima de ella.** Un verificador de exportación lleva dentro,
    # por definición, la lista de lo que busca — y esa lista dispara a este guardián.
    # Antes de añadir nada aquí: comprueba que el archivo DECLARA la prohibición en vez
    # de infringirla. Si no la declara, no es este caso y no se exime.
    r"verificar-export\.sh$",
    r"verificar_plantilla\.py$",
]


def ya_ignorado(ruta):
    """True si git ya está ignorando esta ruta. Si ya está resuelto, no avisamos."""
    try:
        r = subprocess.run(
            ["git", "check-ignore", "-q", str(ruta)],
            cwd=str(ruta.parent if ruta.parent.exists() else VAULT),
            capture_output=True, timeout=5,
        )
        return r.returncode == 0
    except Exception:
        return False


def en_repo(ruta):
    """True si la ruta está dentro de un repositorio git (si no, no hay nada que filtrar)."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(ruta.parent if ruta.parent.exists() else VAULT),
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() == "true"
    except Exception:
        return False


def analizar(ruta_str, mirar_contenido=True):
    """Devuelve (motivo, sugerencia_gitignore) si es peligroso; (None, None) si no."""
    ruta = Path(ruta_str)
    rel = str(ruta)

    for patron in EXENTOS:
        if re.search(patron, rel):
            return None, None

    # Un `.env.example` es una PLANTILLA: existe para decir qué variables hacen falta, y
    # por convención se versiona — si no viaja, quien clona el repo no sabe qué rellenar.
    # Pero se comprueba, no se confía: pasa solo si TODAS sus claves están vacías. Con un
    # valor dentro vuelve a ser un .env y se bloquea igual. (06-ago-2026: el guardián lo
    # bloqueaba a ciegas por el patrón `.env.`, y llevaba versionado desde el commit
    # inicial sin que nadie lo hubiera mirado.)
    if re.search(r"(^|/)\.env\.(example|sample|template)$", rel):
        try:
            for linea in (VAULT / ruta).read_text(encoding="utf-8", errors="ignore").splitlines():
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if "=" in linea and linea.split("=", 1)[1].strip():
                    return "plantilla .env CON UN VALOR DENTRO (deja de ser plantilla)", f"{rel}"
        except OSError:
            return "plantilla .env que no se puede leer para comprobarla", f"{rel}"
        return None, None

    for patron, motivo in PATRONES_RUTA:
        if re.search(patron, rel):
            carpeta = re.search(patron, rel).group(0).strip("/")
            return motivo, f"{carpeta}/"

    for patron, motivo in PATRONES_NOMBRE:
        if re.search(patron, rel, re.IGNORECASE):
            sufijo = ruta.suffix
            sugerencia = f"*{sufijo}" if sufijo else ruta.name
            if "cookie" in ruta.name.lower():
                sugerencia = "*cookies.txt"
            return motivo, sugerencia

    # ── Materia prima: no es peligro, es que no cabe ────────────────────────
    for patron, que_es in PATRONES_MATERIA_PRIMA:
        if re.search(patron, str(ruta), re.IGNORECASE):
            return f"MATERIA_PRIMA::{que_es}", f"*{ruta.suffix}"
    if ruta.is_file():
        try:
            peso = ruta.stat().st_size
            if peso > LIMITE_PESO:
                return f"MATERIA_PRIMA::archivo de {peso // (1024*1024)} MB", f"*{ruta.suffix}"
        except Exception:
            pass

    if mirar_contenido and ruta.is_file():
        try:
            if ruta.stat().st_size <= MAX_SNIFF:
                texto = ruta.read_text(encoding="utf-8", errors="ignore")
                for patron, motivo in PATRONES_CONTENIDO:
                    if re.search(patron, texto):
                        return f"contiene lo que parece {motivo}", ruta.name
        except Exception:
            pass

    return None, None


def modo_hook():
    """Lee el JSON del hook por stdin. Avisa sin bloquear: el agente decide y actúa."""
    try:
        datos = json.load(sys.stdin)
    except Exception:
        return 0

    ruta_str = (datos.get("tool_input") or {}).get("file_path") \
        or (datos.get("tool_response") or {}).get("filePath")
    if not ruta_str:
        return 0

    ruta = Path(ruta_str)
    if not en_repo(ruta):
        return 0

    # Un tarro de sesión no se arregla con .gitignore: hay que SACARLO del repositorio.
    # Gitignorar protege de git, no del agente que lee la carpeta — por eso este caso
    # avisa AUNQUE git ya lo ignore. Regla §4-bis de PROTOCOLO — Permisos de agentes.
    es_sesion = bool(re.search(r"cookies?\.txt$|\.cookies$|(^|/)\.netrc$", str(ruta_str),
                               re.IGNORECASE))
    if not es_sesion and ya_ignorado(ruta):
        return 0

    motivo, sugerencia = analizar(ruta_str)
    if not motivo:
        return 0
    if es_sesion:
        destino = "~/.config/noma/sesiones/"
        aviso = (f"⚠️ '{ruta.name}' es una sesión iniciada (equivale a la contraseña de "
                 f"la persona). No basta con gitignorarlo: tiene que vivir en {destino}")
        contexto = (
            f"GUARDIÁN DE SESIONES: acabas de escribir '{ruta_str}'. Una cookie de sesión es "
            f"una credencial —quien la tenga entra como la persona, sin contraseña ni segundo "
            f"factor— y NO puede vivir dentro de un repositorio, ni siquiera gitignorada: "
            f"gitignorar protege de git, no del agente que lee la carpeta. "
            f"Muévela a {destino} (carpeta 700, archivo 600), apunta ahí el script que la "
            f"usa, y díselo a la persona en una línea. Reglas completas: "
            f"exos/protocolos/PROTOCOLO — Permisos de agentes §4-bis."
        )
    else:
        aviso = (f"⚠️ '{ruta.name}' es {motivo} y NO está en .gitignore. "
                 f"Se subiría al repositorio en el próximo `git add .`")
        contexto = (
            f"GUARDIÁN DE ARCHIVOS: acabas de escribir '{ruta_str}', que es {motivo}, "
            f"y git NO lo está ignorando. Antes de seguir, añade '{sugerencia}' al "
            f".gitignore del repositorio correspondiente y díselo a la persona en una línea. "
            f"No lo dejes para el commit: para entonces ya se te habrá olvidado."
        )

    print(json.dumps({
        "systemMessage": aviso,
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": contexto},
    }))
    return 0



def modo_staged():
    """Revisa lo que está a punto de entrar en el commit. Devuelve 1 si hay que bloquear."""
    # --diff-filter=d EXCLUYE los borrados. Sin esto, el guardián bloqueaba el commit que
    # SACA un .env del índice — que es exactamente lo que él mismo recomienda hacer. Se vio
    # el 06-ago al mover una carpeta de agente: git lista las dos caras del renombrado, y la
    # cara del borrado hacía saltar la alarma. Un candado que impide cerrarlo no es un
    # candado: es un bucle.
    r = subprocess.run(_args_diff("d"),
                       capture_output=True, text=True)
    archivos = [f for f in r.stdout.splitlines() if f.strip()]
    hallazgos = []
    for f in archivos:
        motivo, sugerencia = analizar(f)
        if motivo:
            hallazgos.append((f, motivo, sugerencia))

    if not hallazgos:
        return 0

    materia = [(f, m.split("::", 1)[1], s) for f, m, s in hallazgos if m.startswith("MATERIA_PRIMA::")]
    peligro = [(f, m, s) for f, m, s in hallazgos if not m.startswith("MATERIA_PRIMA::")]

    if peligro:
        print("⛔ COMMIT BLOQUEADO — archivos que no deberían entrar al repositorio:")
        for f, motivo, sugerencia in peligro:
            print(f"  · {f}")
            print(f"      {motivo}")
            print(f"      → añade '{sugerencia}' al .gitignore y saca el archivo con:")
            print(f"        git rm --cached '{f}'")
        print("")
        print("  El archivo NO se borra del disco: solo deja de versionarse.")

    if materia:
        print("")
        print("⛔ COMMIT BLOQUEADO — esto es materia prima, y aquí no va:")
        for f, que_es, _ in materia:
            print(f"  · {f}   ({que_es})")
        print("")
        print("  POR QUÉ. Este repositorio guarda TODAS las versiones de TODO. Un texto")
        print("  que cambia guarda las líneas que cambiaron; un vídeo que cambia guarda")
        print("  el vídeo entero otra vez. Y borrarlo mañana NO lo quita: se queda en el")
        print("  historial para siempre, y cada copia futura se lo baja.")
        print("")
        print("  QUÉ HACER, y es mejor de lo que parece:")
        print("    1. Deja el archivo donde vive (Drive, Dropbox, iCloud, un disco).")
        print("    2. Guarda aquí una NOTA que lo describa y lo enlace.")
        print("")
        print("  Esa nota pesa 2 KB, se busca, se versiona, y dice POR QUÉ ese archivo")
        print("  importa — que es justo lo que el archivo no te puede decir.")
        print("")
        print("  Aquí dentro va lo que son líneas: .md, .yaml, .py, .sh, .json.")

    print("")
    print("  (si de verdad hace falta subirlo: git commit --no-verify)")
    return 1



def _args_diff(filtro: str) -> list[str]:
    """Qué archivos mirar: el índice en local, un rango de commits en GitHub.

    El mismo guardián tiene que valer en los dos sitios. En tu portátil compara
    contra lo que vas a commitear; en el servidor, contra la base de la propuesta.
    Uso en CI:  guardian_x.py --staged --desde origin/main
    """
    import sys as _s
    if "--desde" in _s.argv:
        base = _s.argv[_s.argv.index("--desde") + 1]
        return ["git", "diff", "--name-only", f"--diff-filter={filtro}", f"{base}...HEAD"]
    return ["git", "diff", "--cached", "--name-only", f"--diff-filter={filtro}"]


def main():
    args = sys.argv[1:]
    if args and args[0] == "--hook":
        return modo_hook()
    if args and args[0] == "--staged":
        return modo_staged()
    if args:
        salida = 0
        for a in args:
            motivo, sugerencia = analizar(a)
            if motivo:
                print(f"⚠️  {a}: {motivo} → .gitignore: '{sugerencia}'")
                salida = 1
            else:
                print(f"✅ {a}: sin problema")
        return salida
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
