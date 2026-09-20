#!/usr/bin/env python3
"""guardian_doctrina.py — la doctrina no se toca sin que la persona lo haya dicho.

Dos candados en uno:

1. ZONAS CONGELADAS. Los archivos listados en `exos/CONGELADO.md` (reglas, fronteras,
   estándares, protocolo de sesión y los propios scripts del guardián) no se pueden
   commitear sin `UNLOCK=1`. La norma estaba escrita desde hacía semanas — dentro
   del archivo que pretendía proteger. Era una cerradura dibujada en la puerta.

2. FRASES PROHIBIDAS. Hay afirmaciones sobre la persona que se han colado tres veces, por tres
   agentes distintos, hasta llegar a documentos publicables. No dependen de criterio: o
   está la frase o no está. Así que se comprueban, y su prosa deja de hacer falta.

Uso:  python3 guardian_doctrina.py --staged
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
CONGELADO = VAULT / "exos" / "CONGELADO.md"

# ─── frases que no pueden entrar ─────────────────────────────────────────────
# Cada entrada: (patrón, por qué está mal, qué escribir en su lugar)
# Solo cosas objetivas. Nada que dependa de interpretar el tono.

PROHIBIDO_SIEMPRE = [
    # ⚠️ VACÍA A PROPÓSITO — aquí van TUS frases prohibidas.
    #
    # Qué poner: afirmaciones sobre ti o sobre tu proyecto que no quieres ver escritas
    # NUNCA, en ningún documento. Cosas que alguien dio por buenas una vez y que, si no se
    # cortan, se copian a otro documento y a la tercera ya son «lo que dice el sistema».
    #
    # Por qué existe este candado y no una nota: una regla que hay que recordar no es una
    # regla. Esto lo comprueba al guardar, que es el único momento en que sale barato.
    (
        r"\bcambia esto por una frase tuya\b",
        "Explica aquí por qué está mal.",
        "y aquí qué se escribe en su lugar.",
    ),
]

PROHIBIDO_EN_CANDIDATURA = [
    # Igual que arriba, pero solo en documentos de candidatura (CV, cartas, perfiles).
    # Hay cosas que valen en un sitio y no valen en otro. Déjalo vacío si no lo necesitas.
]

# Y dónde se aplican esas reglas: prefijos de ruta, tal cual, uno por línea. Vacía
# significa «en ningún sitio», que es lo correcto mientras la lista de arriba esté vacía.
# 15-ago-2026: esta constante se había quedado fuera al vaciar el guardián, pero su uso
# seguía abajo. Resultado: `NameError` en el primer commit de la propia doctrina, o sea el guardián
# de la doctrina reventando justo cuando estrena el sistema.
RUTAS_CANDIDATURA = (
    # "mi-vida/<tu-cajón>/",
)

# Archivos que hablan DE las reglas: ahí las frases aparecen citadas a propósito.
# Faltaba CLAUDE.md, y se vio el 2026-08-02: bloqueó un commit por la frase de los
# «20 años en el sector»… que aparece dentro de la propia norma que la prohíbe, precedida de un ⛔
# y seguida de la forma correcta. El guardián estaba impidiendo guardar el documento que
# declara la prohibición. Mismo caso que los workflows: **los que vigilan no se vigilan a
# sí mismos**, y quien enuncia la regla tampoco.
EXENTOS = (
    "AGENTS.md",
    "CLAUDE.md",
    "exos/CONGELADO.md",
    "mi-vida/hot.md",
    "mi-vida/hot-historial",
    "exos/scripts/guardian_doctrina.py",
    "mi-vida/sesiones/",
    "mi-vida/decisions/",
    "mi-vida/tareas/",
    "_recursos_previos/",
    # `archive/` es histórico muerto por definición (ESTANDARES §carpetas): no se enlaza
    # desde documentos activos y nadie lo reutiliza. Guardar la MALA salida del radar es
    # justamente la prueba de por qué se paró — y sin esta exención, archivar un error
    # queda bloqueado por el propio error. La regla real no es «que la frase no exista»:
    # es «que no salga de aquí».
    "/archive/",
)

EXT_TEXTO = {".md", ".yaml", ".yml", ".txt", ".tsx", ".ts", ".json"}



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


def staged() -> list[str]:
    r = subprocess.run(
        _args_diff("ACMR"),
        capture_output=True, text=True, cwd=VAULT,
    )
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def zonas_congeladas() -> list[str]:
    if not CONGELADO.exists():
        return []
    txt = CONGELADO.read_text(encoding="utf-8")
    m = re.search(r"<!-- ZONAS-CONGELADAS -->(.*?)<!-- /ZONAS-CONGELADAS -->", txt, re.S)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines()
            if l.strip() and not l.strip().startswith("```")]


def exento(ruta: str) -> bool:
    return any(e in ruta for e in EXENTOS)


def main() -> int:
    if "--staged" not in sys.argv:
        print("Uso: guardian_doctrina.py --staged", file=sys.stderr)
        return 2

    archivos = staged()
    fallos = 0

    # ── 1 · zonas congeladas ────────────────────────────────────────────────
    # El commit inicial no cambia doctrina: la ESTRENA. Sin esta salvedad, el primer
    # `git commit` del sistema recién instalado se bloquea entero —todos los archivos
    # congelados aparecen como nuevos— y lo primero que aprende quien lo estrena es a
    # escribir `UNLOCK=1`. Un candado que obliga a saltárselo el día uno ya no es un
    # candado. Se detectó el 15-ago-2026 en la primera entrega real.
    hay_historial = subprocess.run(
        ["git", "rev-parse", "--verify", "-q", "HEAD"],
        capture_output=True, text=True, cwd=VAULT,
    ).returncode == 0

    congeladas = zonas_congeladas() if hay_historial else []
    tocadas = [f for f in archivos if f in congeladas]

    if tocadas and os.environ.get("UNLOCK") != "1":
        print("\n✖ BLOQUEADO: intentas cambiar DOCTRINA (exos/CONGELADO.md):")
        for f in tocadas:
            print(f"  · {f}")
        print("\n  Esto cambia el comportamiento de todos los agentes a la vez.")
        print("  Procedimiento: pídeselo a la persona y espera su sí → UNLOCK=1 git commit …")
        print("  → y registra la decisión en mi-vida/decisions/")
        fallos += 1
    elif tocadas:
        print("⚠ Desbloqueo consciente (UNLOCK=1) de doctrina:")
        for f in tocadas:
            print(f"  · {f}")
        print("  Recuerda dejar la decisión escrita en mi-vida/decisions/")

    # ── 2 · las tareas solo nacen por crear_tarea.py ────────────────────────
    # El estándar: una tarea = un objetivo dentro de un área, y nunca
    # se parte en varias. Si se pudiera crear una tarea escribiendo un archivo a mano,
    # el detector de solapamiento sería decorativo — que es exactamente lo que le pasó a
    # la la norma durante semanas.
    nuevas = subprocess.run(
        _args_diff("A"),
        capture_output=True, text=True, cwd=VAULT,
    ).stdout.split()

    for ruta in nuevas:
        if not re.match(r"mi-vida/tareas/TASK-\d+", ruta):
            continue
        p = VAULT / ruta
        if p.exists() and "creado_por: crear_tarea" not in p.read_text(encoding="utf-8", errors="ignore")[:1200]:
            print(f"\n✖ BLOQUEADO: {ruta} se ha creado a mano.")
            print("  Las tareas se crean SOLO con crear_tarea.py, que comprueba antes si")
            print("  ya existe una con el mismo objetivo en la misma área.")
            print("\n  python3 exos/scripts/crear_tarea.py \\")
            print('      --titulo "…" --area <área> --objetivo "…" \\')
            print('      --asignado humano --siguiente "humano: …"')
            print("\n  Y casi siempre lo correcto es esto otro:")
            print('  crear_tarea.py --anadir-a TASK-NNN --paso "…"')
            fallos += 1

    # ── 2-bis · si tocas el CV, sus fechas siguen saliendo de la cronología ──
    # Sustituye a la vieja prohibición de tocar `cv.yaml`, que no tenía forma de
    # cumplirse y empujó a 19 commits con --no-verify (apagando de paso el escáner de
    # secretos). La regla real nunca fue «no lo toques»: era «ningún agente inventa
    # fechas». Eso sí se comprueba, y se puede pasar.
    # 06-ago: esto comprobaba `EXP-001-Trabajo-Remoto/cv.yaml`. Al disolver el laboratorio
    # el CV pasó a `01-CV-y-Empleo/` y el candado dejó de saltar EN SILENCIO — seguía
    # ejecutándose y no protegía nada. Se compara solo por el nombre del archivo para que
    # sobreviva a la próxima mudanza.
    if any(r.endswith("/cv.yaml") or r.endswith("cv.yaml") for r in archivos):
        r = subprocess.run(
            [sys.executable, str(VAULT / "exos/scripts/verificar_fechas_cv.py"), "--breve"],
            capture_output=True, text=True, cwd=VAULT,
        )
        if r.returncode != 0:
            print("\n✖ BLOQUEADO: hay fechas en el CV sin respaldo en la cronología validada.")
            print(r.stdout.strip())
            fallos += 1

    # ── 3 · trinquete del safe-fail ─────────────────────────────────────────
    # Solo sobre lo que se toca. Lo viejo es deuda contada por validar_vault; lo que
    # pasa por aquí ya no puede nacer sin declarar su safe-fail (la norma).
    # Una skill que se MUDA no es una skill que NACE. El 06-ago, al reorganizar
    # las skills en una carpeta por agente, git registró 31 skills como archivos nuevos
    # (cambiaron de ruta y de contenido a la vez, así que no las detectó como renombrados)
    # y el trinquete bloqueó el commit entero. Bloquear una reorganización empuja al
    # --no-verify, que es justo como mueren estos candados. Se compara contra HEAD: si el
    # nombre de la skill ya existía en el árbol, es deuda vieja —la cuenta validar_vault—
    # y no un nacimiento.
    ya_existian = set()
    try:
        previo = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "exos/agentes/"],
                                capture_output=True, text=True, cwd=VAULT).stdout
        ya_existian = {l.split("/")[-2] for l in previo.splitlines() if l.endswith("SKILL.md")}
    except Exception:
        pass

    for ruta in archivos:
        if not ruta.endswith("SKILL.md"):
            continue
        p = VAULT / ruta
        if not p.exists():
            continue
        if ruta.split("/")[-2] in ya_existian:
            continue
        cabecera = p.read_text(encoding="utf-8", errors="ignore")[:2000]
        if "safe-fail" not in cabecera:
            print(f"\n✖ BLOQUEADO: {ruta} no declara 'safe-fail'.")
            print("  Sin safe-fail una skill es de solo lectura, y eso no se comprobaba.")
            print("  Añade al frontmatter: solo-lectura · requiere-confirmacion ·")
            print("  no-enviar · no-ejecutar · alcance")
            fallos += 1

    # ── 4 · frases prohibidas ───────────────────────────────────────────────
    for ruta in archivos:
        if exento(ruta) or Path(ruta).suffix not in EXT_TEXTO:
            continue
        p = VAULT / ruta
        if not p.exists():
            continue
        try:
            texto = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        reglas = list(PROHIBIDO_SIEMPRE)
        if any(ruta.startswith(c) for c in RUTAS_CANDIDATURA):
            reglas += PROHIBIDO_EN_CANDIDATURA

        for patron, motivo, alternativa in reglas:
            for m in re.finditer(patron, texto, re.I):
                linea = texto[: m.start()].count("\n") + 1
                print(f"\n✖ BLOQUEADO: frase prohibida en {ruta}:{linea}")
                print(f"  «{m.group(0).strip()}»")
                print(f"  {motivo}")
                print(f"  → escribe: {alternativa}")
                fallos += 1
                break  # una por regla y archivo, no inundes

    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
