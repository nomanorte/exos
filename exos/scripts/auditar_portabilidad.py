#!/usr/bin/env python3
"""auditar_portabilidad.py — ¿qué te funciona solo en una herramienta, y te importa?

EL PROBLEMA QUE RESUELVE. Tu sistema promete que puedes cambiar de herramienta y
encontrarte lo mismo — las mismas reglas, las mismas skills, la misma memoria. Esa promesa
tiene un enemigo silencioso: **lo que instalas DENTRO de un programa**. Un plugin de tu
editor, una skill suelta de tu agente — funcionan de maravilla… en ese programa. Cambias
de herramienta y desaparecen, sin mensaje, y no sabes por qué «ahí no va».

Esto lo hace visible. Separa lo instalado fuera del cerebro en tres bandejas, y solo una es
deuda:

  ⚡ POTENTE   — te empodera Y está declarada con su «extracción»: qué haces cuando esa
               capacidad no está. Dependencia consciente, perfectamente legítima.
  💤 SIN JUICIO — instalada y nunca decidida. La bandeja que importa: cada una es la
               pregunta «¿me empodera o es ruido?» sin contestar.
  🗑  RUIDO    — decidida como inservible. Candidata a desinstalar: una skill inútil
               instalada no es neutra — ocupa contexto y confunde a tus agentes.

El juicio es TUYO y vive en `exos/portabilidad.yaml` — este script jamás decide, solo
enseña la foto. Sin ese archivo todo sale «sin juicio», que es la verdad.

El objetivo no es cero instaladas: es CERO SIN DECIDIR.

Uso:
    python3 exos/scripts/auditar_portabilidad.py            # el parte
    python3 exos/scripts/auditar_portabilidad.py --json     # para otros scripts
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()
HOME = Path.home()
JUICIO = VAULT / "exos" / "portabilidad.yaml"

# Dónde guarda cada herramienta lo que se le instala. Añadir una herramienta = una línea.
# Se registra TODO lo que aparezca; el juicio (potente/ruido) es de la persona, no de esta lista.
FUENTES = {
    "claude-code": [
        (HOME / ".claude" / "skills", "skill suelta"),
        (HOME / ".claude" / "plugins" / "cache", "plugin"),
    ],
    "codex": [(HOME / ".codex" / "skills", "skill suelta")],
    "gemini": [(HOME / ".gemini" / "config" / "skills", "skill suelta")],
    "cursor": [(HOME / ".cursor" / "skills", "skill suelta")],
    "opencode": [(HOME / ".opencode" / "skills", "skill suelta")],
}


def skills_del_vault() -> set[str]:
    """Las portables: viajan con la carpeta y funcionan en cualquier herramienta."""
    return {p.parent.name for p in (VAULT / "exos/agentes").rglob("SKILL.md")}


def instaladas() -> list[dict]:
    """Todo lo que vive dentro de un programa y no del cerebro."""
    filas = []
    for herramienta, rutas in FUENTES.items():
        for base, tipo in rutas:
            if not base.is_dir():
                continue
            if tipo == "plugin":
                # cache/<marketplace>/<plugin>/<version>/skills/<skill>
                for mercado in sorted(base.iterdir()):
                    if not mercado.is_dir():
                        continue
                    for plugin in sorted(mercado.iterdir()):
                        if not plugin.is_dir():
                            continue
                        # Solo la versión más reciente: la caché guarda las viejas y
                        # contarlas duplica cada skill sin aportar nada.
                        versiones = sorted((d for d in plugin.iterdir() if d.is_dir()),
                                           key=lambda d: d.stat().st_mtime)[-1:]
                        for version in versiones:
                            sk = version / "skills"
                            for s in sorted(sk.iterdir()) if sk.is_dir() else []:
                                if s.is_dir():
                                    filas.append({
                                        "nombre": s.name,
                                        "herramienta": herramienta,
                                        "origen": f"plugin {plugin.name} {version.name}",
                                    })
            else:
                for s in sorted(base.iterdir()):
                    if s.is_dir() and not s.name.startswith("."):
                        filas.append({
                            "nombre": s.name,
                            "herramienta": herramienta,
                            "origen": tipo,
                        })
    return filas


def cargar_juicio() -> dict:
    """El veredicto de la persona por nombre de skill. Vacío si aún no existe el archivo."""
    if not JUICIO.exists():
        return {}
    import yaml
    datos = yaml.safe_load(JUICIO.read_text(encoding="utf-8")) or {}
    return datos.get("skills", {}) or {}


def clasificar(filas: list[dict], juicio: dict, cerebro: set[str]) -> dict:
    bandejas = {"potente": [], "sin_juicio": [], "ruido": [], "duplicada": []}
    for f in filas:
        v = juicio.get(f["nombre"], {})
        veredicto = v.get("veredicto", "")
        if f["nombre"] in cerebro:
            # Existe dentro Y fuera: dos versiones del mismo nombre acaban desfasadas.
            bandejas["duplicada"].append(f)
        elif veredicto == "potente":
            f["extraccion"] = v.get("extraccion", "")
            bandejas["potente"].append(f)
        elif veredicto == "ruido":
            bandejas["ruido"].append(f)
        else:
            bandejas["sin_juicio"].append(f)
    return bandejas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cerebro = skills_del_vault()
    filas = instaladas()
    bandejas = clasificar(filas, cargar_juicio(), cerebro)

    if a.json:
        print(json.dumps({"cerebro": len(cerebro), **{k: v for k, v in bandejas.items()}},
                         ensure_ascii=False, indent=2))
        return 0

    print(f"\n🧭 PORTABILIDAD — lo instalado en programas vs lo que viaja contigo\n")
    print(f"   en el cerebro (portables): {len(cerebro)}")
    print(f"   instaladas en programas: {len(filas)}\n")

    if bandejas["potente"]:
        print(f"⚡ POTENTES y declaradas — dependencia consciente: {len(bandejas['potente'])}")
        for f in bandejas["potente"]:
            ext = f" · extracción: {f['extraccion']}" if f.get("extraccion") else " · ⚠️ SIN extracción declarada"
            print(f"   · {f['nombre']}  ({f['herramienta']}, {f['origen']}){ext}")
        print()

    if bandejas["sin_juicio"]:
        print(f"💤 SIN JUICIO — nadie ha decidido si valen: {len(bandejas['sin_juicio'])}")
        print(f"   Cada una es la pregunta «¿me empodera o es ruido?» sin contestar.")
        print(f"   Se contesta en exos/portabilidad.yaml, no aquí.")
        for f in bandejas["sin_juicio"]:
            print(f"   · {f['nombre']}  ({f['herramienta']}, {f['origen']})")
        print()

    if bandejas["duplicada"]:
        print(f"⚠️  DUPLICADAS — misma skill dentro y fuera del cerebro: {len(bandejas['duplicada'])}")
        print(f"   Dos copias del mismo nombre se desfasan sin avisar. Se queda la del cerebro.")
        for f in bandejas["duplicada"]:
            print(f"   · {f['nombre']}  ({f['herramienta']}, {f['origen']})")
        print()

    if bandejas["ruido"]:
        print(f"🗑  RUIDO declarado — candidatas a desinstalar: {len(bandejas['ruido'])}")
        for f in bandejas["ruido"]:
            print(f"   · {f['nombre']}  ({f['herramienta']})")
        print()

    sin = len(bandejas["sin_juicio"])
    if sin:
        print(f"→ El número que importa: {sin} sin juicio. El objetivo no es cero instaladas —")
        print(f"  es cero SIN DECIDIR. Una dependencia consciente con extracción escrita es")
        print(f"  legítima; una que nadie ha mirado es la que te sorprende en otra herramienta.")
    else:
        print("✅ Cero sin juicio: toda dependencia es consciente y tiene su extracción.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
