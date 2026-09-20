#!/usr/bin/env python3
"""doctor.py — ¿tiene este ordenador lo que hace falta para trabajar aquí?

POR QUÉ EXISTE. Una persona recibió su sistema completo, con su repositorio y su editor
con IA, y **no pudo trabajar**: le faltaban piezas que nadie le había dicho que hacían
falta. No fallaba con un mensaje claro; fallaba con errores que no dicen lo que pasa.
Hizo falta que alguien se sentara con ella a instalarlo a mano.

Eso es lo que este archivo sustituye. **Lo ejecuta el agente, nunca la persona.**

── LA DISTINCIÓN QUE IMPORTA ────────────────────────────────────────────────────
No todo se arregla igual, y mezclarlo es lo que convierte esto en una tarde perdida:

  · ARREGLABLE   — el agente lo instala y sigue. La persona no se entera.
  · PIDE CLAVE   — hace falta la contraseña del ordenador. Se pide UNA vez, explicando
                   qué se va a instalar y por qué. Nunca se pide "por si acaso".
  · SOLO AVISO   — no bloquea nada hoy. Se anota y se saca cuando estorbe.

Un doctor que lo marca todo como urgente se ignora igual que uno que no avisa de nada.

Uso:
    python3 exos/scripts/doctor.py            # mira y cuenta
    python3 exos/scripts/doctor.py --json     # para el agente
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def activar_hooks(raiz: Path = RAIZ) -> bool:
    """Activa los guardianes versionados solo para este repositorio.

    Es idempotente y deliberadamente no toca la configuración global de git. Tampoco
    configura el repositorio padre si el directorio recibido no es su propia raíz.
    """
    raiz = raiz.resolve()
    pre_commit = raiz / "exos/githooks" / "pre-commit"
    if not pre_commit.is_file() or shutil.which("git") is None:
        return False
    try:
        encontrado = subprocess.run(
            ["git", "-C", str(raiz), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if encontrado.returncode != 0 or Path(encontrado.stdout.strip()).resolve() != raiz:
            return False
        activado = subprocess.run(
            ["git", "-C", str(raiz), "config", "--local", "core.hooksPath", "exos/githooks"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return activado.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def version(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else None
    except Exception:
        return None


def numero_mayor(v: str | None) -> int:
    """De «v22.3.1» saca 22. Devuelve 0 si no se puede leer."""
    if not v:
        return 0
    for trozo in v.replace("v", " ").replace(".", " ").split():
        if trozo.isdigit():
            return int(trozo)
    return 0


def revisar() -> list[dict]:
    """Cada entrada: qué es, si está, qué bloquea, y cómo se arregla."""
    r = []

    # ── git ───────────────────────────────────────────────────────────────────
    r.append({
        "pieza": "git",
        "para_que": "guardar tu trabajo y poder volver atrás",
        "ok": shutil.which("git") is not None,
        "bloquea": "todo",
        "arreglo": "pide_clave",
        "como": "En macOS: `xcode-select --install`. Abre una ventana del sistema y "
                "pide confirmación. Son unos minutos y se hace una sola vez.",
    })

    hooks_activos = activar_hooks()
    r.append({
        "pieza": "guardianes al guardar",
        "para_que": "que cada commit ejecute las comprobaciones del repositorio",
        "ok": hooks_activos,
        "bloquea": "los guardianes",
        "arreglo": "arreglable",
        "como": "El doctor activa `exos/githooks` en la configuración local de este "
                "repositorio. No cambia la configuración global del ordenador.",
    })

    # ── la web NO va en EXOS (18-sep-2026) ────────────────────────────────────
    # Este doctor comprobaba node, npm, la carpeta hermana `web/` y sus dependencias,
    # y salía ROJO en un EXOS recién instalado por no encontrar una web que ya no viaja.
    # El primer contacto con el producto era un diagnóstico en rojo por algo que no
    # falta: eso enseña a ignorar al doctor, que es justo lo contrario de su función.
    # Construir webs es el programa `crear-web`, y su doctor viaja con él.

    # ── python ────────────────────────────────────────────────────────────────
    r.append({
        "pieza": "python3",
        "para_que": "los guardianes y los scripts de tu cerebro",
        "ok": sys.version_info >= (3, 9),
        "detalle": f"{sys.version_info.major}.{sys.version_info.minor}",
        "bloquea": "los guardianes",
        "arreglo": "arreglable",
        "como": "Si estás leyendo esto, python funciona: lo ha ejecutado él.",
    })

    return r


def main() -> int:
    piezas = revisar()
    faltan = [p for p in piezas if not p["ok"]]

    if "--json" in sys.argv:
        print(json.dumps({
            "todo_bien": not faltan,
            "bloquea_todo": [p["pieza"] for p in faltan if p["bloquea"] == "todo"],
            "piezas": piezas,
        }, ensure_ascii=False, indent=2))
        return 0

    print("\n🩺 ¿Tiene este ordenador lo que hace falta?\n")
    for p in piezas:
        marca = "✓" if p["ok"] else "⛔"
        extra = f"  ({p['detalle']})" if p.get("detalle") else ""
        print(f"  {marca} {p['pieza']:<24} {p['para_que']}{extra}")

    if not faltan:
        print("\n✅ Todo listo. No hay nada que instalar.\n")
        return 0

    print(f"\n⛔ Faltan {len(faltan)}:\n")
    for p in faltan:
        clave = " · HACE FALTA LA CONTRASEÑA DEL ORDENADOR" if p["arreglo"] == "pide_clave" else ""
        print(f"  · {p['pieza']} — bloquea {p['bloquea']}{clave}")
        print(f"    {p['como']}\n")

    # Código 1 solo si impide trabajar HOY. Que falte node cuando aún no se ha llegado a
    # la web no es una urgencia, y tratarlo como tal enseña a ignorar los avisos.
    return 1 if any(p["bloquea"] == "todo" for p in faltan) else 0


if __name__ == "__main__":
    sys.exit(main())
