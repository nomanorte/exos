#!/usr/bin/env python3
"""programar_autoguardado.py — deja el autoguardado funcionando en TU ordenador.

POR QUÉ EXISTE. `autoguardado.sh` no corre por existir: alguien tiene que decirle al
ordenador que lo lance cada X minutos. Y esa parte es distinta en cada sistema —launchd en
Mac, cron en Linux, el Programador de tareas en Windows—, con lo cual acaba sin hacerse.
Un script que nadie programa es un archivo muerto que además da falsa sensación de red.

Esto lo programa. Y si tu sistema no lo permite desde aquí, te dice exactamente qué hacer
en vez de fallar.

Uso:
    python3 exos/scripts/programar_autoguardado.py            # enseña qué haría
    python3 exos/scripts/programar_autoguardado.py --aplicar
    python3 exos/scripts/programar_autoguardado.py --quitar
    ...y --cada 15 para cambiar los minutos (por defecto, 10).
"""
from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()
SCRIPT = VAULT / "exos" / "scripts" / "autoguardado.sh"
ETIQUETA = "com.exos.autoguardado"


def _plist(cada: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{ETIQUETA}</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>{SCRIPT}</string></array>
  <key>StartInterval</key><integer>{cada * 60}</integer>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
"""


def mac(cada: int, aplicar: bool, quitar: bool) -> int:
    destino = Path.home() / "Library" / "LaunchAgents" / f"{ETIQUETA}.plist"
    if quitar:
        if not aplicar:
            print(f"  (simulacro) borraría {destino} y lo descargaría")
            return 0
        subprocess.run(["launchctl", "unload", str(destino)], capture_output=True)
        destino.unlink(missing_ok=True)
        print("✅ Autoguardado retirado.")
        return 0
    if not aplicar:
        print(f"  (simulacro) escribiría {destino}, cada {cada} min")
        return 0
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(_plist(cada), encoding="utf-8")
    subprocess.run(["launchctl", "unload", str(destino)], capture_output=True)
    r = subprocess.run(["launchctl", "load", str(destino)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⛔ launchctl no pudo cargarlo:\n{r.stderr.strip()}")
        return 1
    print(f"✅ Listo. Tu trabajo se guarda solo cada {cada} minutos.")
    print(f"   El registro va a exos/scripts/logs/autoguardado.log")
    return 0


def linux(cada: int, aplicar: bool, quitar: bool) -> int:
    marca = f"# {ETIQUETA}"
    linea = f"*/{cada} * * * * /bin/bash {SCRIPT}  {marca}"
    actual = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    lineas = [l for l in actual.splitlines() if marca not in l]
    if not quitar:
        lineas.append(linea)
    nuevo = "\n".join(lineas).strip() + "\n"
    if not aplicar:
        print(f"  (simulacro) dejaría el crontab así:\n{nuevo}")
        return 0
    r = subprocess.run(["crontab", "-"], input=nuevo, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⛔ No se pudo escribir el crontab:\n{r.stderr.strip()}")
        return 1
    print("✅ Autoguardado retirado." if quitar
          else f"✅ Listo. Tu trabajo se guarda solo cada {cada} minutos.")
    return 0


def windows(cada: int, quitar: bool) -> int:
    """Windows no se toca desde aquí: se le dan las órdenes exactas.

    Programar tareas en Windows pide permisos que este script no debería arrogarse, y una
    orden mal montada deja una tarea fantasma difícil de encontrar. Es más honesto darle
    la línea para que la pegue —o se la pegue su agente— que fallar a medias.
    """
    if quitar:
        print("Para quitarlo, pega esto en PowerShell:\n")
        print(f'  schtasks /Delete /TN "{ETIQUETA}" /F\n')
        return 0
    print("Windows: pega esto en PowerShell (o pídeselo a tu agente).\n")
    print("Necesitas Git for Windows, que ya trae `bash`:\n")
    print(f'  schtasks /Create /SC MINUTE /MO {cada} /TN "{ETIQUETA}" ^')
    print(f'    /TR "\\"C:\\Program Files\\Git\\bin\\bash.exe\\" \\"{SCRIPT}\\""\n')
    print("Si instalaste Git en otra carpeta, cambia esa ruta por la tuya.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cada", type=int, default=10, help="minutos entre guardados (10)")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--quitar", action="store_true")
    a = ap.parse_args()

    if a.cada < 1:
        print("⛔ `--cada` tiene que ser al menos 1 minuto.")
        return 1
    if not SCRIPT.is_file():
        print(f"⛔ No encuentro {SCRIPT}. ¿Se ha movido?")
        return 1

    sistema = platform.system()
    print(f"\n{'→ PROGRAMANDO' if a.aplicar else '· SIMULACRO'} · sistema: {sistema}")
    print(f"  script: {SCRIPT}\n")

    if sistema == "Darwin":
        return mac(a.cada, a.aplicar, a.quitar)
    if sistema == "Linux":
        return linux(a.cada, a.aplicar, a.quitar)
    if sistema == "Windows" or os.name == "nt":
        return windows(a.cada, a.quitar)
    print(f"⛔ Sistema no reconocido ({sistema}). Programa `{SCRIPT}` a mano cada "
          f"{a.cada} minutos con la herramienta que uses.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
