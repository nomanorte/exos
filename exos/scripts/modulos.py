#!/usr/bin/env python3
"""modulos.py — encima de EXOS cabe cualquier cosa, y EXOS reacciona.

## Lo que pidió la persona (18-sep-2026)

> *«EXOS debería ser flexible y que se le pueda meter modularmente cualquier cosa. Eso es lo
> importante, lo demás lo descubrimos sobre la marcha. Si son módulos, programas, agentes o
> skills, eso es lo de menos. Y que la estructura esté preparada para que cualquier cosa que
> se ponga **haya una reacción activa** para gestionarlo y detectarlo.»*

Dos exigencias, y la segunda es la que manda:

1. **Cabe cualquier cosa.** Nadie tiene que declarar de qué tipo es. Una carpeta con
   documentos, una con skills, una a medias: todas valen.
2. **Reacciona sola.** No basta con contestar si alguien pregunta — eso es un catálogo, y un
   catálogo que nadie abre no existe. Lo que se suelte ahí **aparece en el parte de apertura**
   sin que nadie lo pida.

## Cómo lo hace: mira, no pregunta

No hay esquema que cumplir. Se deduce de lo que hay dentro:

    ¿tiene `skills/` con algo?      → sabe hacer cosas
    ¿tiene documentos?              → trae material
    ¿tiene `MODULO.yaml`?           → además lo cuenta él mismo (opcional)

`MODULO.yaml` **no es obligatorio nunca**. Solo sirve para que digas en tus palabras qué es
algo, y para declarar fronteras si va a escribir — que es lo único que de verdad importa
cuando algo escribe en tu carpeta.

Uso:
    modulos.py                 # qué hay encima de EXOS y qué se deduce de cada cosa
    modulos.py --novedades     # solo lo que ha aparecido o cambiado desde la última vez
    modulos.py --estricto      # al empaquetar: exige que lo que escriba tenga fronteras
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _raiz import raiz_vault
except ImportError:                      # fuera de una entrega (tests)
    def raiz_vault() -> Path:            # type: ignore[misc]
        return Path.cwd()

DOCS = {".md", ".txt", ".html", ".pdf", ".yaml", ".yml", ".json", ".csv"}


def carpeta_modulos() -> Path:
    return raiz_vault() / "modulos"


def memoria() -> Path:
    """Lo que ya se había visto. Vive en `mi-vida/` porque es estado de la persona."""
    return raiz_vault() / "mi-vida" / ".modulos-vistos.json"


def _mirar(c: Path) -> dict:
    """Qué se deduce de una carpeta, sin pedirle que declare nada."""
    skills = sorted(p.name for p in (c / "skills").iterdir()
                    if p.is_dir()) if (c / "skills").is_dir() else []
    docs = [p for p in c.rglob("*")
            if p.is_file() and p.suffix.lower() in DOCS and "skills" not in p.parts]
    datos = {}
    f = c / "MODULO.yaml"
    if f.exists():
        try:
            datos = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if not isinstance(datos, dict):
                datos = {}
        except yaml.YAMLError:
            datos = {"_yaml_roto": True}

    puede = []
    if skills:
        puede.append(f"{len(skills)} skill(s): {', '.join(skills[:4])}")
    if docs:
        puede.append(f"{len(docs)} documento(s)")

    avisos = []
    if datos.get("_yaml_roto"):
        avisos.append("su `MODULO.yaml` no es YAML válido: se ignora")
    # Lo ÚNICO que se exige, y solo a quien escribe: sin fronteras, instalar algo es
    # darle tu carpeta entera.
    if datos.get("escribe") and not datos.get("prohibido"):
        avisos.append("declara `escribe` y no `prohibido`: dile también qué NO puede tocar")
    if skills and not datos.get("escribe"):
        avisos.append("tiene skills y no declara `escribe`: no se sabe dónde puede escribir")

    return {"nombre": c.name, "ruta": c, "skills": skills, "docs": len(docs),
            "datos": datos, "puede": puede, "avisos": avisos,
            "descrito": bool(datos.get("que_es"))}


def instalados() -> list[dict]:
    raiz = carpeta_modulos()
    if not raiz.is_dir():
        return []
    return [_mirar(c) for c in sorted(raiz.iterdir())
            if c.is_dir() and not c.name.startswith((".", "_"))]


def _huella(m: dict) -> str:
    return f"{len(m['skills'])}s{m['docs']}d{'+' if m['descrito'] else '-'}"


def novedades() -> list[str]:
    """Lo que ha aparecido o cambiado desde la última vez. Esta es la reacción activa."""
    mods = instalados()
    ahora = {m["nombre"]: _huella(m) for m in mods}
    antes = {}
    f = memoria()
    if f.exists():
        try:
            antes = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            antes = {}

    lineas = []
    for m in mods:
        n = m["nombre"]
        if n not in antes:
            que = " · ".join(m["puede"]) or "todavía vacía"
            lineas.append(f"✨ «{n}» es nuevo aquí — {que}")
            if not m["descrito"]:
                lineas.append(f"     dile qué es y lo anoto: un `MODULO.yaml` con `que_es:`")
        elif antes[n] != ahora[n]:
            lineas.append(f"🔄 «{n}» ha cambiado — {' · '.join(m['puede']) or 'vacía'}")
        for a in m["avisos"]:
            lineas.append(f"     ⚠️ {n}: {a}")
    for n in antes:
        if n not in ahora:
            lineas.append(f"🗑️ «{n}» ya no está")

    if lineas:
        try:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(ahora, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass
    return lineas


def _imprimir(mods: list[dict]) -> None:
    if not mods:
        print("\n📦 Encima de EXOS no hay nada todavía.\n")
        print("   `modulos/` admite lo que quieras dejar ahí: una carpeta con documentos,")
        print("   un programa entero o algo a medias. No hay formato que cumplir.\n")
        return
    print(f"\n📦 {len(mods)} cosa(s) encima de EXOS\n")
    for m in mods:
        print(f"  ● {m['nombre']}")
        if m["datos"].get("que_es"):
            print(f"      {m['datos']['que_es']}")
        elif m["puede"]:
            print(f"      sin describir · se ve: {' · '.join(m['puede'])}")
        else:
            print("      vacía")
        for a in m["avisos"]:
            print(f"      ⚠️ {a}")
        print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--novedades", action="store_true",
                    help="solo lo aparecido o cambiado desde la última vez")
    ap.add_argument("--estricto", action="store_true",
                    help="al empaquetar: exige fronteras a lo que escriba")
    a = ap.parse_args(argv)

    if a.novedades:
        for l in novedades():
            print(l)
        return 0

    mods = instalados()
    if a.estricto:
        graves = [(m["nombre"], x) for m in mods for x in m["avisos"]]
        if graves:
            print(f"⛔ {len(graves)} aviso(s) que no se entregan así:\n")
            for n, x in graves:
                print(f"  · {n}: {x}")
            return 1
        print(f"✓ modulos: {len(mods)} cosa(s), ninguna escribe sin fronteras")
        return 0

    _imprimir(mods)
    return 0
if __name__ == "__main__":
    sys.exit(main())
