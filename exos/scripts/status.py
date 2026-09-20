#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EL PARTE DE LA PERSONA — lo primero que ve al abrir cualquier sesión.

Enseña lo que te toca a ti y lo que espera a otro, en vez de un muro de tareas
para agentes. Pero el contacto de la persona con la realidad **es el chat**: no abre
carpetas, no usa Markdown nativo, y el móvil lo usa como cajón de captura, no como canal
de decisiones. Así que el estado tiene que aparecer donde él está, sin pedirlo.

Reglas de presentación (importan tanto como el dato):
- **Cero identificadores.** La persona no quiere ver TASK-119: quiere "rebalanceo de
  relaciones".
- **Ordenado por lo que DESBLOQUEA**, no por prioridad declarada.
- **Cada línea termina en algo que hacer.**
- **Una pantalla.** Si no cabe, el fallo es de priorización, no de resumen.

Uso:  python3 exos/scripts/status.py
"""

import json
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
TAREAS = VAULT / "mi-vida/tareas"
ESTADOS_AUTOMATICOS = VAULT / "exos/pipelines"


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
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def nombre(f):
    """'TASK-046-radar-tendencias.md' → 'radar tendencias'."""
    return f.stem.split("-", 2)[-1].replace("-", " ")


def recortar(txt, n=110):
    txt = " ".join(txt.split())
    return txt if len(txt) <= n else txt[: n - 1] + "…"


REPO_WEB = VAULT.parent / "web"


def programas_instalados():
    """Qué programas hay en `modulos/` y qué sabe hacer cada uno.

    18-sep-2026 · `modulos/` existía y no la leía nadie: podías dejar una carpeta dentro y
    ningún agente se enteraba. Un programa que el sistema no ve es un programa que no
    tienes.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import modulos as _m
        filas = []
        for x in _m.instalados():
            marca = "🤖" if x["datos"].get("tipo") == "agente" else "📄"
            filas.append(f"{marca} {x['nombre']} — {x['datos'].get('que_es', '¿?')}")
            for f in x["fallos"]:
                filas.append(f"   ⛔ {f}")
        return filas
    except Exception:
        return []


def encargos_web(agente=None):
    # 18-sep-2026 · La web es OPCIONAL: EXOS ya no la lleva —construir webs es un programa
    # aparte—, así que aquí puede no haber repositorio hermano. Enseñar un apartado sobre un
    # repositorio que nunca has tenido es ruido, y el ruido enseña a no leer el parte.
    if not REPO_WEB.is_dir():
        return []

    """Encargos abiertos del repositorio web, para que el parte sea de los DOS repos.

    El trabajo de un agente no cabe en un solo sitio: la tarea de fondo vive en el cerebro
    y lo que se implementa vive en la web. El 30-jul un encargo estuvo esperando sin que
    nadie lo viera porque el parte solo miraba aquí. `PROTOCOLO — Traspaso entre agentes
    y repos` §2.
    """
    carpeta = REPO_WEB / "docs"
    if not carpeta.exists():
        return []
    out = []
    for f in sorted(carpeta.glob("ENCARGO*.md")):
        fm = frontmatter(f)
        if fm.get("estado") in ("completado", "cerrado", "archivo"):
            continue
        quien = (fm.get("asignado") or "sin asignar").lower()
        if agente and quien != agente:
            continue
        titulo = ""
        for linea in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            if linea.startswith("# "):
                titulo = linea[2:].strip()
                break
        cierra = fm.get("cierra")
        out.append(f"  · {titulo or f.name}"
                   f"\n      para {quien} · lo pidió {fm.get('autor', '?')}"
                   f"{' · cierra ' + cierra if cierra else ''}"
                   f"\n      tu-proyecto/web/docs/{f.name}")
    return out


def el_foco():
    """Enseña la única tarea marcada como foco, si existe."""
    for f in TAREAS.glob("TASK-*.md"):
        fm = frontmatter(f)
        if fm.get("foco") == "hoy" and fm.get("estado") not in ("completada", "archivo"):
            print("\n" + "━" * 64)
            print(f"  🎯 HOY:  {nombre(f)}")
            if fm.get("next_action"):
                print(f"     {recortar(fm['next_action'], 100)}")
            print("━" * 64)
            return


def la_mas_vieja():
    """Enseña la tarea que más tiempo lleva esperando una acción humana."""
    import datetime as dt

    hoy = dt.date.today()
    peor = None
    for f in TAREAS.glob("TASK-*.md"):
        fm = frontmatter(f)
        if fm.get("estado") in ("completada", "archivo"):
            continue
        if not str(fm.get("next_action", "")).startswith("humano"):
            continue
        try:
            dias = (hoy - dt.date.fromisoformat(str(fm.get("actualizado", ""))[:10])).days
        except (ValueError, TypeError):
            continue
        if peor is None or dias > peor[0]:
            peor = (dias, nombre(f), fm.get("next_action", ""))
    if peor and peor[0] >= 7:
        print(f"\n⏳ LO QUE MÁS LLEVA ESPERANDO  ({peor[0]} días)")
        print(f"  · {peor[1]}")
        print(f"    → {recortar(peor[2], 100)}")


def termometro():
    """Cuenta el estado que existe en esta copia, sin asumir carpetas privadas."""
    tareas = [frontmatter(f) for f in TAREAS.glob("TASK-*.md")]
    abiertas = sum(1 for fm in tareas if fm.get("estado") not in ("completada", "archivo"))
    cerradas = len(tareas) - abiertas
    print(f"\n🌡️  TAREAS ABIERTAS {abiertas}  ·  CERRADAS {cerradas}")


def main():
    agente_filtro = sys.argv[1].lower() if len(sys.argv) > 1 else None
    
    tareas = {}
    for f in sorted(TAREAS.glob("TASK-*.md")):
        m = re.match(r"(TASK-\d+)", f.name)
        if m:
            tareas[m.group(1)] = (f, frontmatter(f))


    # cuántas tareas destraba cada una (grafo de dependencias)
    destraba = {tid: 0 for tid in tareas}
    for tid, (f, fm) in tareas.items():
        if fm.get("estado") == "completada":
            continue
        for dep in re.findall(r"TASK-\d+", fm.get("depende_de", "")):
            if dep in destraba:
                destraba[dep] += 1

    solo_tu, con_agente, revision, atascado = [], [], [], []
    for tid, (f, fm) in tareas.items():
        # Comprobar tags y agente para el filtro
        tiene_agente = False
        if agente_filtro:
            if agente_filtro in fm.get("tags", "").lower():
                tiene_agente = True
            elif agente_filtro == fm.get("agente", "").lower():
                tiene_agente = True
            
            if not tiene_agente:
                continue
                
        est, asig = fm.get("estado", ""), fm.get("asignado", "")
        if est == "completada":
            continue
        n = destraba.get(tid, 0)
        # La prioridad pesa por encima de cuántas destraba. El 06-ago se marcó una tarea
        # como `urgente` y quedó la tercera de una lista de 24: el campo existía y no lo
        # miraba nadie. Una prioridad que no cambia el orden no es una prioridad.
        urgente = fm.get("prioridad", "") == "urgente"
        if urgente:
            n += 100
        cabeza = ("  🔴 " if urgente else "  · ") + nombre(f) + (f"   🔓 destraba {destraba.get(tid, 0)}" if destraba.get(tid, 0) else "")
        paso = fm.get("next_action", "")
        linea = cabeza + (f"\n      → {recortar(paso)}" if paso else "")
        if est == "en-revision":
            revision.append((n, linea))
        elif est == "bloqueada":
            dep = fm.get("depende_de", "").strip(" []")
            atascado.append((n, cabeza + (f"\n      → espera a: {dep}" if dep else "")))
        elif asig in ("humano", "tu", "contigo") and est in ("pendiente", "en-curso"):
            # 'contigo' NO es un agente: eres tu, en sesion con uno. Estas tareas
            # tambien le necesitan. Antes se filtraban y 36 tareas eran invisibles
            # para el: creia que no le tocaban y en realidad esperaban por el.
            destino = solo_tu if asig in ("humano", "tu") else con_agente
            destino.append((n, cabeza + (f"\n      → {recortar(paso)}" if paso else "")))

    for g in (solo_tu, con_agente, revision, atascado):
        g.sort(key=lambda x: -x[0])

    # pipelines que dejaron algo esperando, y los que están vivos
    esperando, corriendo = [], []
    directorios_estado = ESTADOS_AUTOMATICOS.iterdir() if ESTADOS_AUTOMATICOS.is_dir() else ()
    for d in sorted(directorios_estado):
        sj = d / "status.json"
        if not d.is_dir() or not sj.exists():
            continue
        try:
            s = json.loads(sj.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if agente_filtro and s.get("agente", "").lower() != agente_filtro:
            continue
        bonito = d.name.split("-", 1)[-1].replace("-", " ").lower()
        if s.get("fase") == "output-listo":
            esperando.append(f"  · {bonito} (de {s.get('agente','?')})"
                             f"\n      → {recortar(s.get('detalle',''))}")
        elif s.get("fase") not in ("idle", None):
            corriendo.append(f"  · {bonito}: {s.get('fase')}")

    # Escaneo de Bandeja Soberana (Borradores de agente-biblioteca)
    borradores = []
    BORRADORES_DIR = VAULT / "mi-vida/_borradores"
    if BORRADORES_DIR.exists():
        for b in sorted(BORRADORES_DIR.glob("*.md")):
            fm_b = frontmatter(b)
            if fm_b.get("estado") == "en-revision":
                if agente_filtro and agente_filtro != "agente-biblioteca":
                    continue
                borradores.append(f"  · {b.name}\n      → Abre este archivo para validarlo o dejar [!FEEDBACK]")

    print("\n╔" + "═" * 62 + "╗")
    if agente_filtro:
        print(f"║  TU PARTE CON {agente_filtro.upper()}" + " " * (47 - len(agente_filtro)) + "║")
    else:
        print("║  TU PARTE (GLOBAL)" + " " * 43 + "║")
    print("╚" + "═" * 62 + "╝")
    el_foco()

    def bloque(titulo, items, vacio=None, tope=6):
        if not items:
            if vacio:
                print(f"\n{titulo}\n  {vacio}")
            return
        print(f"\n{titulo}  ({len(items)})")
        for it in items[:tope]:
            print(it)
        if len(items) > tope:
            print(f"  …y {len(items) - tope} más")

    bloque("👤 SOLO TÚ  (offline, sin abrir sesión)",
           [l for _, l in solo_tu], "nada pendiente ✅")
    bloque("🤝 CONTIGO + UN AGENTE  (hay que sentarse)",
           [l for _, l in con_agente], tope=5)
    
    # NUEVO: Bloque exclusivo para la Bandeja Soberana de agente-biblioteca
    bloque("📥 BORRADORES ESPERANDO TU FEEDBACK (Bandeja agente-biblioteca)", borradores)
    
    # Encargos del OTRO repositorio. Van aquí porque el trabajo de un agente no cabe
    # en un solo sitio: la tarea de fondo vive en el cerebro y lo que se implementa vive
    # en la web. Si el parte solo mira el cerebro, un encargo puede quedarse semanas sin
    # que nadie lo vea — que es exactamente lo que pasó el 30-jul.
    bloque("📦 TUS PROGRAMAS", programas_instalados())
    bloque("🌐 ENCARGOS EN EL REPO WEB", encargos_web(agente_filtro))

    bloque("📤 ESPERANDO TU REVISIÓN  (un pipeline ya lo dejó hecho)", esperando)
    bloque("👁️ ESPERAN TU OK", [l for _, l in revision], tope=5)
    bloque("⛔ ATASCADO", [l for _, l in atascado], tope=4)
    bloque("🏭 CORRIENDO AHORA", corriendo, "todo en reposo")

    la_mas_vieja()
    termometro()

    print("\n" + "─" * 64)
    print("  Decisiones vigentes y horizonte: mi-vida/hot.md")
    print("  Qué hay en cada carpeta: MAPA — De qué va cada carpeta.html")
    print("─" * 64 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
