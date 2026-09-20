#!/usr/bin/env python3
"""actualizar_onboarding.py — el onboarding avanza con pruebas, no con afirmaciones.

EL PROBLEMA QUE RESUELVE. Hasta ahora una fase se daba por cerrada porque el agente
escribía en el archivo de estado que lo estaba. Eso convierte el progreso en una opinión:
basta un agente optimista —o uno con prisa por terminar— para que alguien «se gradúe» sin
haber creado un solo agente ni ejecutado una sola skill. Y quien recibe ese vault cree que
ya sabe usarlo.

LA REGLA. **Cada fase declara qué evidencia la cierra.** Sin esa evidencia concreta, la
fase no se marca. El agente no escribe el estado a mano: llama aquí, y esto se niega.

  fase 0  el proyecto declarado, con palabras suyas
  fase 1  ha colocado algo suyo donde toca
  fase 2  existe una tarea de verdad
  fase 3  ha VISTO saltar un candado (no que le hayan contado que existen)
  fase 4  tiene un agente suyo
  fase 5  una skill suya **y ejecutada** — crearla no es aprender a usarla
  fase 6  una sesión cerrada entera
  fase 7  ha trabajado desde DOS herramientas distintas

⚠️ Y LA GRADUACIÓN NO ES HABER MARCADO LAS OCHO FASES. Es haber creado las cuatro cosas:
un agente, una skill, una sesión cerrada y el sistema abierto desde dos herramientas. Se
puede recorrer el guion entero y no haber construido nada; eso no es graduarse, es asistir.

Uso:
    actualizar_onboarding.py --estado PATH --completar 5 --evidencia '{"skill":"resumir","ejecutada":true}'
    ...y añade --aplicar para escribirlo. Sin él solo enseña el estado que quedaría.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


class EvidenciaInsuficiente(Exception):
    """La fase pide algo que no está demostrado. No se marca."""


# ── Qué cierra cada fase ─────────────────────────────────────────────────────
# Cada regla recibe la evidencia y el estado, y devuelve None si vale o el motivo si no.
# Se escriben como funciones y no como una lista de claves porque varias fases piden
# **dos cosas a la vez** (crear y usar), que es justo donde estaba el agujero.

def _texto(ev, clave):
    v = ev.get(clave)
    return isinstance(v, str) and v.strip() != ""


def _cierto(ev, clave):
    return ev.get(clave) is True


REGLAS = {
    0: lambda ev, e: None if _texto(ev, "proyecto")
    else "falta `proyecto`: la fase 0 cierra cuando dice en qué quiere trabajar",
    1: lambda ev, e: None if _cierto(ev, "ubicacion_correcta")
    else "falta `ubicacion_correcta`: tiene que haber colocado algo suyo donde toca",
    2: lambda ev, e: None if _texto(ev, "tarea")
    else "falta `tarea`: el identificador de la tarea que ha creado",
    3: lambda ev, e: None if _texto(ev, "candado_visto")
    else "falta `candado_visto`: qué candado le saltó. Contarlo no cuenta; verlo, sí",
    4: lambda ev, e: None if _texto(ev, "agente")
    else "falta `agente`: el nombre del agente que ha creado",
    5: lambda ev, e: None if (_texto(ev, "skill") and _cierto(ev, "ejecutada"))
    else "la fase 5 pide `skill` Y `ejecutada`: crearla no es aprender a usarla",
    6: lambda ev, e: None if _cierto(ev, "sesion_cerrada")
    else "falta `sesion_cerrada`: una sesión cerrada entera, con su bitácora",
    # 18-sep-2026 · La 7 era «su web arrancada». La web dejó de viajar en EXOS —es el
    # programa `crear-web`, aparte— y un alumno sin web no podía graduarse NUNCA, porque la
    # graduación se la exigía. La antigua 8 pasa a ser la 7 y el recorrido son ocho fases.
    7: lambda ev, e: None if _texto(ev, "herramienta")
    else "falta `herramienta`: desde cuál ha trabajado esta vez",
}

TOTAL_FASES = 8


def cargar_estado(path: Path) -> dict:
    """Lee el estado. `safe_load` a propósito: un YAML puede ejecutar código."""
    datos = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(datos, dict):
        raise ValueError(f"{path} no contiene un estado de onboarding válido")
    datos.setdefault("fase_actual", 0)
    datos.setdefault("completadas", [])
    datos.setdefault("creado_hasta_ahora", {})
    datos["creado_hasta_ahora"].setdefault("agentes", [])
    datos["creado_hasta_ahora"].setdefault("skills", [])
    datos["creado_hasta_ahora"].setdefault("herramientas", [])
    datos["creado_hasta_ahora"].setdefault("sesiones_cerradas", 0)
    datos["creado_hasta_ahora"].setdefault("web_arrancada", False)
    return datos


def _graduado(creado: dict, quiere_web: bool = True) -> bool:
    """Las pruebas de verdad. Marcar ocho casillas no es haber construido nada.

    Son CUATRO: un agente, una skill, una sesión cerrada y el sistema abierto desde dos
    herramientas distintas. Ninguna se puede dar por buena sin evidencia.
    entera igual.
    """
    base = bool(creado.get("agentes")
                and creado.get("skills")
                and creado.get("sesiones_cerradas", 0) >= 1)
    return base and (creado.get("web_arrancada", False) if quiere_web else True)


def completar_fase(estado: dict, fase: int, evidencia: dict) -> dict:
    import copy
    e = copy.deepcopy(estado)
    e.setdefault("completadas", [])
    creado = e.setdefault("creado_hasta_ahora", {})
    for k, v in (("agentes", []), ("skills", []), ("herramientas", []),
                 ("sesiones_cerradas", 0), ("web_arrancada", False)):
        creado.setdefault(k, v)

    if fase not in REGLAS:
        raise EvidenciaInsuficiente(f"la fase {fase} no existe (hay de 0 a 7)")

    # ── No se salta ninguna. Aprender esto es acumulativo: la fase 5 no significa nada
    #    para quien no ha pasado por la 4, y marcarla igual deja un hueco invisible.
    faltan = [f for f in range(fase) if f not in e["completadas"]]
    if faltan:
        raise EvidenciaInsuficiente(
            f"no se puede cerrar la fase {fase}: faltan por hacer {faltan}")

    motivo = REGLAS[fase](evidencia, e)
    if motivo:
        raise EvidenciaInsuficiente(motivo)

    # ── Acumular lo CREADO, que es lo que de verdad cuenta
    if fase == 4:
        if evidencia["agente"] not in creado["agentes"]:
            creado["agentes"].append(evidencia["agente"])
    elif fase == 5:
        if evidencia["skill"] not in creado["skills"]:
            creado["skills"].append(evidencia["skill"])
    elif fase == 6:
        creado["sesiones_cerradas"] = creado.get("sesiones_cerradas", 0) + 1
    elif fase == 7:
        h = evidencia["herramienta"]
        if h not in creado["herramientas"]:
            creado["herramientas"].append(h)
        # Portabilidad = haberlo hecho en DOS salas. Con una sola no es un fallo del
        # cliente, pero sí una fase abierta — y hay que decirlo en voz alta: devolver el
        # estado sin más dejaría al agente creyendo que la cerró.
        if len(creado["herramientas"]) < 2:
            raise EvidenciaInsuficiente(
                f"la fase 7 pide DOS herramientas distintas y solo hay "
                f"{creado['herramientas']}. Ábrelo desde otra y vuelve.")
        if not _graduado(creado, False):
            raise EvidenciaInsuficiente(
                "no gradúa: faltan un agente, una skill o una sesión cerrada")

    if fase == 0 and _texto(evidencia, "proyecto"):
        e["proyecto_declarado"] = evidencia["proyecto"]

    if fase not in e["completadas"]:
        e["completadas"].append(fase)
    e["completadas"] = sorted(set(e["completadas"]))
    e["fase_actual"] = min(fase + 1, TOTAL_FASES - 1)
    e["graduado"] = (fase == 7 and _graduado(creado, False)
                     and len(creado["herramientas"]) >= 2)
    return e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estado", required=True, type=Path)
    ap.add_argument("--completar", required=True, type=int)
    ap.add_argument("--evidencia", required=True, help="JSON con lo que demuestra la fase")
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe. Sin esto solo enseña qué quedaría.")
    a = ap.parse_args()

    try:
        estado = cargar_estado(a.estado)
        evidencia = json.loads(a.evidencia)
        nuevo = completar_fase(estado, a.completar, evidencia)
    except EvidenciaInsuficiente as exc:
        print(f"⛔ Evidencia insuficiente para la fase {a.completar}:\n   {exc}")
        print("\n   No es burocracia: la fase existe para que haga algo, no para marcarla.")
        return 1
    except Exception as exc:
        print(f"⛔ No se pudo leer el estado: {exc}")
        return 1

    salida = yaml.safe_dump(nuevo, allow_unicode=True, sort_keys=False)
    if not a.aplicar:
        print("· SIMULACRO — así quedaría el estado (no se ha escrito nada):\n")
        print(salida)
        return 0

    a.estado.write_text(salida, encoding="utf-8")
    print(f"✓ fase {a.completar} cerrada · siguiente: {nuevo['fase_actual']}")
    if nuevo.get("graduado"):
        print("\n🎓 Graduado: un agente, una skill, una sesión cerrada y dos herramientas.")
        print("   A partir de aquí el onboarding NO se vuelve a mencionar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
