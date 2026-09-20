#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""archivar_tareas.py — saca de la carpeta activa lo que ya está cerrado.

Por qué existe (auditoría del 2026-08-06): había 92 tareas y **55 estaban cerradas**
—34 `completada` y 21 `archivo`— viviendo en la misma carpeta que las vivas. Nadie va a
leer 92 archivos antes de crear el 93, así que se duplicaba trabajo. Y el problema nunca
fue el número del ID: el último era el 171 con solo 92 archivos, porque el contador cuenta
creaciones, no tareas. Lo que molesta es abrir la carpeta y no poder mirarla.

La regla que lo arregla no es una norma escrita: es este script + el aviso del guardián.
Ya se demostró que archivar «cuando toque» no ocurre nunca.

**El ID no se toca.** Una tarea archivada conserva su nombre de archivo, así que los
wikilinks del histórico siguen resolviendo y `crear_tarea.py` sigue viendo su número como
usado (lee con `rglob`). Archivar no libera un ID: lo congela.

Uso:
    python3 exos/scripts/archivar_tareas.py           # enseña qué movería
    python3 exos/scripts/archivar_tareas.py --aplicar # lo mueve
"""

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()
TAREAS = VAULT / "mi-vida" / "tareas"
CERRADAS = {"completada", "archivo"}
DIAS_DE_GRACIA = 7  # una tarea recién cerrada sigue a la vista una semana


def campo(texto: str, nombre: str) -> str:
    m = re.search(rf"^{nombre}:\s*(.+)$", texto, re.M)
    return m.group(1).split(" #")[0].strip().strip('"').strip("'") if m else ""


# Una tarea de backlog que lleva 30 días sin que nadie la toque no está aparcada: está
# muerta y ocupando sitio. 30 días es un mes natural — por debajo salían falsos positivos
# con lo que espera a una fecha concreta.
DIAS_FRIA = 30

# Solo enfrían las que no dependen de nadie ahora mismo. `en-curso` la lleva un agente;
# `en-revision` espera a la persona, y que él tarde no la convierte en basura: eso es un
# problema de bandeja, no de caducidad.
ESTADOS_FRIABLES = {"pendiente", "bloqueada"}


def frias(hoy: dt.date) -> list:
    """Tareas de backlog sin tocar desde hace DIAS_FRIA. Detecta; no toca nada."""
    out = []
    for p in sorted(TAREAS.glob("TASK-*.md")):
        texto = p.read_text(encoding="utf-8", errors="ignore")
        if campo(texto, "estado") not in ESTADOS_FRIABLES:
            continue
        fecha = campo(texto, "actualizado") or campo(texto, "creado")
        try:
            dias = (hoy - dt.date.fromisoformat(fecha[:10])).days
        except (ValueError, TypeError):
            continue          # sin fecha fiable no se acusa a nadie de estar frío
        if dias >= DIAS_FRIA:
            out.append((p, dias))
    return sorted(out, key=lambda x: -x[1])


def archivar_una(ruta: Path) -> Path:
    """Mueve una tarea fría a _cerradas/ marcándola. El ID no se toca: se congela.

    Se marca `estado: archivo` y no `completada` porque no se completó nada — fingir lo
    contrario ensuciaría cualquier recuento futuro de trabajo hecho.
    """
    texto = ruta.read_text(encoding="utf-8")
    hoy = dt.date.today()
    texto = re.sub(r"^estado:.*$", "estado: archivo", texto, count=1, flags=re.M)
    if not re.search(r"^estado: archivo\s*$", texto, re.M):
        # La tarea no tenía línea `estado:` (frontmatter incompleto o ausente): el
        # re.sub de arriba no tuvo nada que sustituir. archivar_una() es interfaz
        # pública — no solo la alimenta `--frias` — así que no podemos asumir que
        # siempre hay un `estado:` que reemplazar. Si no lo hay, se inserta a mano
        # para que ninguna tarea archivada quede sin marcar (H3).
        if texto.startswith("---\n"):
            texto = "---\nestado: archivo\n" + texto[len("---\n"):]
        else:
            texto = "estado: archivo\n" + texto
    if re.search(r"^actualizado:", texto, re.M):
        texto = re.sub(r"^actualizado:.*$", f"actualizado: {hoy}", texto, count=1, flags=re.M)
    texto = re.sub(r"^next_action:.*$",
                   f'next_action: "caducada por inactividad ({hoy}) — resucítala moviéndola '
                   f'de vuelta a mi-vida/tareas/ y devolviéndole su estado"',
                   texto, count=1, flags=re.M)
    if "caducada por inactividad" not in texto:
        # La tarea no tenía next_action: se deja constancia igual, en el cuerpo.
        texto = texto.rstrip() + (
            f"\n\n> [!note] Archivada el {hoy}: caducada por inactividad.\n"
            f"> Resucítala moviéndola de vuelta a `mi-vida/tareas/`.\n")

    destino_dir = TAREAS / "_cerradas" / hoy.strftime("%Y-%m")
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / ruta.name
    if destino.exists():
        # No hay otra copia de esta tarea en ningún sitio: el vault no tiene remoto.
        # Sobrescribir en silencio (H1) sería destruir sin aviso una tarea que quizás
        # se resucitó a mano y volvió a enfriarse el mismo mes. El criterio del vault
        # es que archivar nunca destruye, así que fallamos con un mensaje claro en vez
        # de inventar un sufijo: un sufijo automático crearía dos "TASK-XXX" a la vez
        # en _cerradas/, justo la ambigüedad de ID que este script existe para evitar.
        # Quien archiva decide a mano qué hacer con el choque, no el script por él.
        raise FileExistsError(
            f"ya existe {destino} — no se sobrescribe. Resuelve el choque a mano "
            f"(revisa si es la misma tarea resucitada y vuelta a enfriar) antes de "
            f"volver a archivar {ruta.name}.")
    destino.write_text(texto, encoding="utf-8")
    try:
        ruta.unlink()
    except OSError:
        # El movimiento no puede quedar a medias (H2): si no se puede borrar el
        # origen, deshacemos la escritura en destino para que la tarea siga
        # existiendo en un único sitio — vivo en origen, tal y como estaba — en vez
        # de quedar archivada y viva a la vez (dos verdades para el mismo ID).
        destino.unlink(missing_ok=True)
        raise
    return destino


def main() -> int:
    aplicar = "--aplicar" in sys.argv
    if "--frias" in sys.argv:
        lista = frias(dt.date.today())
        if not lista:
            print("✅ Ninguna tarea de backlog lleva más de 30 días sin tocarse.")
            return 0
        print(f"\n🧊 {len(lista)} tarea(s) frías — backlog sin tocar en {DIAS_FRIA}+ días\n")
        for i, (p, dias) in enumerate(lista, 1):
            print(f"  {i:>2}. {p.stem[:56]:<56} {dias}d")
        ids = [a for a in sys.argv[1:] if a.startswith("TASK-")]
        if not (aplicar and ids):
            print("\n  Esto NO archiva nada. Dile a la persona los números que quiere archivar y")
            print("  ejecuta: archivar_tareas.py --frias --aplicar TASK-XXX TASK-YYY\n")
            return 0

        movidas = 0
        vistos = set()
        for p, _dias in lista:
            # Emparejar por el componente ID completo (TASK-<número>), no por
            # startswith crudo (H4): "TASK-01" con startswith casaría a la vez con
            # TASK-01-algo.md y TASK-010-x.md y archivaría las dos sin avisar.
            m = re.match(r"^(TASK-\d+)(?=[-.]|$)", p.name)
            id_tarea = m.group(1) if m else None
            if id_tarea in ids:
                vistos.add(id_tarea)
                destino = archivar_una(p)
                print(f"  → {p.name} archivada en {destino.parent.name}/")
                movidas += 1
        # Un ID que la persona escribió mal, o que ya no está frío, no debe fallar en
        # silencio (H5): si se queda creyendo que archivó algo que no casó con
        # ninguna tarea fría, la carpeta activa miente sobre lo que hay vivo.
        no_encontrados = [i for i in ids if i not in vistos]
        if no_encontrados:
            print(f"\n⚠️  {len(no_encontrados)} ID(s) no casaron con ninguna tarea "
                  f"fría de la lista de arriba — no se archivó nada con ese ID: "
                  f"{', '.join(no_encontrados)}")
        print(f"\n✅ {movidas} archivada(s) por decisión de la persona. "
              f"Los IDs siguen ocupados: archivar no libera un número.\n")
        return 0
    hoy = dt.date.today()
    mover = []

    for p in sorted(TAREAS.glob("TASK-*.md")):
        texto = p.read_text(encoding="utf-8", errors="ignore")
        if campo(texto, "estado") not in CERRADAS:
            continue
        fecha = campo(texto, "actualizado") or campo(texto, "creado")
        try:
            d = (hoy - dt.date.fromisoformat(fecha[:10])).days
            periodo = fecha[:7]
        except (ValueError, TypeError):
            d, periodo = 999, "sin-fecha"   # sin fecha fiable, se archiva igual
        if d >= DIAS_DE_GRACIA:
            mover.append((p, periodo, d))

    if not mover:
        print("✅ Nada que archivar: la carpeta activa solo tiene tareas vivas.")
        return 0

    for p, periodo, d in mover:
        destino = TAREAS / "_cerradas" / periodo
        print(f"  {'→' if aplicar else '·'} {p.name[:52]:<52} cerrada hace {d}d → _cerradas/{periodo}/")
        if aplicar:
            destino.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(destino / p.name))

    vivas = len(list(TAREAS.glob("TASK-*.md"))) - (0 if aplicar else len(mover))
    if aplicar:
        print(f"\n✅ {len(mover)} archivada(s). Quedan {vivas} en la carpeta activa.")
        print("   Los IDs siguen ocupados: archivar no libera un número.")
    else:
        print(f"\n{len(mover)} se archivarían · quedarían {vivas} abiertas.")
        print("   Ejecuta con --aplicar para moverlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
