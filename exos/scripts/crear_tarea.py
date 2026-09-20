#!/usr/bin/env python3
"""crear_tarea.py — la ÚNICA vía para crear una tarea.

El estándar, y es más simple de lo que suele estar escrito:

  · **Una tarea = un objetivo dentro de un área.** Si dos tareas empujan el mismo
    objetivo en la misma área, son la misma aunque produzcan cosas distintas.
  · **Nunca se parte en varias tareas. Siempre una con pasos.** Sus palabras:
    «Búsqueda de trabajo: currículum en varios formatos, pipelines, fuentes de mi vida
    laboral, plataformas, procesos, carta de motivación, la web /cv, el CV descargable…
    pero todo es el mismo objetivo-tarea con distintos checkpoints a cubrir.»
  · **Los pasos son casillas en el cuerpo**, no un campo de estado que mantener.
  · **Si se solapa, se bloquea y se fusiona.** No se avisa: se impide.

Por qué existe este script: la La norma prohibía las tareas duplicadas por escrito desde
hacía semanas, y los agentes la saltaron igual. Hubo que arreglar 26 a
mano. Una regla que se puede comprobar no se escribe: se construye.

Uso:
    crear_tarea.py --auditar
        Enseña qué tareas vivas se solapan según el estándar. No toca nada.

    crear_tarea.py --titulo "..." --area sistema --objetivo "..." \
                   --asignado humano --siguiente "humano: ..."
        Crea la tarea. Si detecta solapamiento, NO crea nada y te dice a cuál añadir.

    crear_tarea.py --anadir-a TASK-026 --paso "Carta de motivación adaptada por oferta"
        Añade un checkpoint a una tarea existente. Es lo que hay que hacer casi siempre.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()
TAREAS = VAULT / "mi-vida" / "tareas"

VIVAS = {"pendiente", "en-curso", "en-revision", "bloqueada"}

# Quién puede llevar una tarea: tú, o cualquiera de los agentes que hayas declarado.
# desfasadas a la vez (auditoría 2026-08-06): los sandboxes desaparecieron el 02-ago al
# convertirse en skills, e `humano` ES la persona (CLAUDE.md, «no hay orquestador»). Resultado:
# no había forma de asignarle una tarea a ninguno de los seis agentes del roster, y todo
# acababa en `humano` aunque el trabajo no fuera suyo.
# El roster se lee del sitio donde vive, no se copia aquí: un enum a mano vuelve a
# desfasarse en cuanto nazca un agente.
AGENTES_DIR = VAULT / "exos/agentes"


def _roster() -> set:
    nombres = set()
    for y in AGENTES_DIR.rglob("AGENTE-*.yaml"):
        n = y.stem.replace("AGENTE-", "")
        if n != "plantilla":
            nombres.add(n)
    return nombres


ASIGNADO_OK = {"humano"} | _roster()

# Cupos por especie (PROPUESTA — Taxonomía de tareas, 2026-08-15). Antes había UN tope
# de 40 sobre todo lo vivo, y el 15-ago bloqueó el sistema: de las 47 abiertas solo 1
# era archivable. Lo que llenaba el cupo eran 26 intenciones aparcadas y 9 decisiones
# esperando a ti — ninguna de las dos cosas es trabajo en curso.
#
# `pendiente` NO lleva cupo a propósito: es backlog, y capar el backlog es lo que rompió
# el sistema. Se ordena y caduca (revisar_al_abrir.py), no se capa.
# `bloqueada` queda fuera: está parada por causa externa, no ocupa a nadie.
CUPOS = {
    "en-curso": 5,      # WIP real: no más trabajo del que se pueda revisar de verdad
    "en-revision": 7,   # tu bandeja
}


def conteo_por_estado(tareas: list[dict]) -> dict[str, int]:
    """Cuántas tareas hay en cada estado. Devuelve 0 para los que no aparecen."""
    conteo = {e: 0 for e in VIVAS}
    for t in tareas:
        estado = t.get("estado", "")
        if estado in conteo:
            conteo[estado] += 1
    return conteo

# Umbral de solapamiento, sobre COINCIDENCIA (intersección / la más corta de las dos),
# no sobre Jaccard. Motivo, encontrado probándolo: las tareas viejas no declaran
# `objetivo:`, así que se compara un objetivo largo contra un título corto. Jaccard
# castiga esa asimetría y dejaba pasar duplicados evidentes — «carta de motivación por
# oferta» no chocaba con «búsqueda de empleo». La coincidencia mide lo que importa:
# cuánto de la tarea PEQUEÑA está contenido en la otra.
# Calibrado contra las 22 vivas del 30-jul: a 0.40 emparejaba cosas sin relación.
UMBRAL = 0.55

VACIAS = {
    "de", "del", "la", "el", "los", "las", "y", "o", "en", "para", "por", "con", "a",
    "un", "una", "que", "se", "su", "sus", "al", "lo", "es", "sin", "sobre", "tarea",
    "hacer", "crear", "montar", "definir", "revisar", "the", "of", "task",
}


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def palabras(*textos: str) -> set[str]:
    bruto = " ".join(t or "" for t in textos)
    tokens = re.findall(r"[a-z0-9]{3,}", sin_tildes(bruto).lower())
    # Fuera los identificadores: "task" y los números salen en TODAS las tareas (vienen
    # del nombre del archivo) y diluían la coincidencia hasta dejar pasar duplicados
    # evidentes. Son etiqueta, no significado.
    return {t for t in tokens if t not in VACIAS and not t.isdigit()}


def area_normal(dominio: str) -> str:
    """`3-negocio`, `03-negocio/web`, `negocio` → `negocio`. El área es el área."""
    d = sin_tildes(str(dominio or "")).lower().strip()
    d = re.sub(r"^\d+[-_ ]*", "", d)          # fuera el número de orden
    d = re.split(r"[/\\]", d)[0].strip()      # fuera el subdominio
    return d or "sin-area"


def frontmatter(texto: str) -> dict:
    if not texto.startswith("---"):
        return {}
    fin = texto.find("\n---", 3)
    if fin == -1:
        return {}
    fm = {}
    for linea in texto[3:fin].splitlines():
        if ":" in linea and not linea.startswith((" ", "-", "#")):
            k, v = linea.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def cargar(solo_vivas: bool = True) -> list[dict]:
    out = []
    for p in sorted(TAREAS.glob("TASK-*.md")):
        texto = p.read_text(encoding="utf-8", errors="ignore")
        fm = frontmatter(texto)
        if solo_vivas and fm.get("estado") not in VIVAS:
            continue
        titulo = ""
        m = re.search(r"^#\s+(.+)$", texto, re.M)
        if m:
            titulo = m.group(1)
        out.append({
            "ruta": p,
            "id": fm.get("id", p.stem[:8]),
            "titulo": titulo,
            "area": area_normal(fm.get("dominio", "")),
            "objetivo": fm.get("objetivo", ""),
            "estado": fm.get("estado", ""),
            "actualizado": fm.get("actualizado", ""),
            "palabras": palabras(titulo, fm.get("objetivo", ""), p.stem),
        })
    return out


def parecido(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def choques(area: str, pals: set[str], tareas: list[dict], excluir: str = "") -> list[tuple]:
    """Mismo objetivo Y misma área — el criterio que eligió la persona."""
    res = []
    for t in tareas:
        if t["id"] == excluir or t["area"] != area:
            continue
        s = parecido(pals, t["palabras"])
        if s >= UMBRAL:
            res.append((s, t))
    return sorted(res, key=lambda x: -x[0])


# ─── acciones ────────────────────────────────────────────────────────────────

def auditar() -> int:
    tareas = cargar()
    print(f"📋 {len(tareas)} tareas vivas · criterio: mismo objetivo + misma área\n")
    vistos, grupos = set(), []
    for t in tareas:
        if t["id"] in vistos:
            continue
        familia = [t] + [o for _, o in choques(t["area"], t["palabras"], tareas, t["id"])]
        if len(familia) > 1:
            for f in familia:
                vistos.add(f["id"])
            grupos.append(familia)

    if not grupos:
        print("✅ Ninguna se solapa. Nada que fusionar.")
        return 0

    print(f"⚠️  {len(grupos)} grupo(s) que según el estándar deberían ser UNA tarea:\n")
    for i, g in enumerate(grupos, 1):
        print(f"  Grupo {i} · área «{g[0]['area']}»")
        for t in g:
            print(f"    · {t['id']:<9} {t['titulo'][:66]}")
        print(f"    → quedarse con {g[0]['id']} y pasar el resto a checkpoints suyos\n")
    print("Fusionar es decisión de la persona: este comando no toca nada.")
    return 0


def anadir(task_id: str, paso: str) -> int:
    cands = list(TAREAS.glob(f"{task_id}*.md"))
    if not cands:
        print(f"⛔ No encuentro {task_id}", file=sys.stderr)
        return 1
    p = cands[0]
    texto = p.read_text(encoding="utf-8")

    linea = f"- [ ] {paso}"
    if "## Pasos" in texto:
        texto = re.sub(r"(## Pasos\n)", rf"\1{linea}\n", texto, count=1)
    else:
        texto = texto.rstrip() + f"\n\n## Pasos\n{linea}\n"

    texto = re.sub(r"^actualizado:.*$", f"actualizado: {date.today()}", texto, count=1, flags=re.M)
    p.write_text(texto, encoding="utf-8")
    print(f"✅ Checkpoint añadido a {task_id}: {paso}")
    print(f"   {p.relative_to(VAULT)}")
    return 0


def crear(args) -> int:
    tareas = cargar()
    area = area_normal(args.area)
    pals = palabras(args.titulo, args.objetivo)

    choque = choques(area, pals, tareas)
    if choque:
        print("\n⛔ NO SE CREA: esto es el mismo objetivo en la misma área.\n")
        print("   Estándar de la persona (30-jul): una tarea = un objetivo. Nunca se parte;")
        print("   siempre es una tarea con pasos.\n")
        for s, t in choque[:4]:
            print(f"   · {t['id']:<9} {t['titulo'][:64]}   ({int(s*100)}% de coincidencia)")
        sugerida = choque[0][1]["id"]
        print(f"\n   Añádelo como checkpoint de la que ya existe:")
        print(f'   crear_tarea.py --anadir-a {sugerida} --paso "{args.titulo}"')
        return 1

    if args.asignado not in ASIGNADO_OK:
        print(f"⛔ 'asignado' debe ser uno de: {' · '.join(sorted(ASIGNADO_OK))}", file=sys.stderr)
        return 1

    # Crear una tarea NO se bloquea: nace en `pendiente`, que es backlog libre. El cupo
    # que importa es el de `en-curso`, y ese se comprueba en el pre-commit
    # (validar_vault.py) porque pasar a en-curso se hace editando el frontmatter, no
    # llamando a este script.
    conteo = conteo_por_estado(tareas)
    for estado, tope in CUPOS.items():
        if conteo[estado] >= tope:
            print(f"⚠️  Aviso: {conteo[estado]} tarea(s) en `{estado}` (cupo {tope}).")
            if estado == "en-revision":
                print("   Es la bandeja de la persona: enséñasela antes de darle más trabajo.")
            else:
                print("   No empieces trabajo nuevo hasta cerrar algo de lo que hay en curso.")

    # rglob, no glob: los IDs cerrados viven en _cerradas/AAAA-MM/ y siguen contando.
    # Con glob a secas, archivar la TASK-001 dejaría el 001 libre y el siguiente que se
    # creara pisaría su nombre en los enlaces del histórico.
    usados = {int(m.group(1)) for p in TAREAS.rglob("TASK-*.md")
              if (m := re.match(r"TASK-(\d+)", p.name))}
    nid = max(usados, default=0) + 1
    slug = re.sub(r"[^a-z0-9]+", "-", sin_tildes(args.titulo).lower()).strip("-")[:52]
    ruta = TAREAS / f"TASK-{nid:03d}-{slug}.md"

    pasos = "".join(f"- [ ] {p}\n" for p in (args.paso or [])) or "- [ ] (primer paso)\n"

    ruta.write_text(f"""---
id: TASK-{nid:03d}
tipo: tarea
estado: pendiente
asignado: {args.asignado}
prioridad: {args.prioridad}
dominio: {args.area}
objetivo: {args.objetivo}
creado: {date.today()}
actualizado: {date.today()}
next_action: "{args.siguiente}"
creado_por: crear_tarea
tags: [{args.tags}]
---

# TASK-{nid:03d} — {args.titulo}

## Objetivo

{args.objetivo}

## Pasos

{pasos}""", encoding="utf-8")

    print(f"✅ Creada TASK-{nid:03d} · {ruta.relative_to(VAULT)}")
    print("   Todo lo que surja de este objetivo va aquí como checkpoint, no como tarea nueva.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--auditar", action="store_true")
    ap.add_argument("--anadir-a", dest="anadir_a")
    ap.add_argument("--paso", action="append")
    ap.add_argument("--titulo")
    ap.add_argument("--area")
    ap.add_argument("--objetivo")
    ap.add_argument("--asignado", default="humano")
    ap.add_argument("--prioridad", default="media")
    ap.add_argument("--siguiente", default="")
    ap.add_argument("--tags", default="")
    a = ap.parse_args()

    if a.auditar:
        return auditar()
    if a.anadir_a:
        if not a.paso:
            print("⛔ Falta --paso", file=sys.stderr)
            return 1
        return anadir(a.anadir_a, a.paso[0])
    if a.titulo:
        for campo in ("area", "objetivo", "siguiente"):
            if not getattr(a, campo):
                print(f"⛔ Falta --{campo}", file=sys.stderr)
                return 1
        return crear(a)

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
