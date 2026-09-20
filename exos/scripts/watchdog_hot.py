#!/usr/bin/env python3
"""watchdog_hot.py — el registro se escribe MIENTRAS se trabaja, no al final.

POR QUÉ EXISTE. Tu doctrina dice «registra según avanzas»: si la sesión se corta —y se
corta— lo que no esté escrito no existió. Pero una regla que nadie comprueba se incumple
sin que nadie se entere. Esto la convierte en candado: si hay trabajo reciente y ni
`hot.md` ni `mi-vida/sesiones/` se han tocado, el commit no pasa hasta que se registre.

Y de paso vigila lo contrario: que `hot.md` no engorde. Es tu memoria de trabajo, no un
diario — pasada una pantalla, lo que ya no obliga a nadie se archiva.
"""
import os
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

# La ruta se deduce de dónde vive el script, no se escribe a fuego. Con la ruta fija,
# ejecutado desde un worktree miraba la carpeta equivocada: daba por no registrado un
# trabajo que sí lo estaba, y bloqueaba el commit sin motivo. Un guardián que se equivoca
# de sitio es un guardián que se acaba saltando.
VAULT_DIR = raiz_vault()
HOT_MD = VAULT_DIR / "mi-vida" / "hot.md"
SESIONES_DIR = VAULT_DIR / "mi-vida" / "sesiones"
TOLERANCIA_SEGUNDOS = 600 # 10 minutos de gracia

def get_latest_work_time():
    latest_time = 0
    for root, _, files in os.walk(VAULT_DIR):
        if "exos" in root or ".git" in root or "/." in root: continue
        for file in files:
            if not file.endswith('.md'): continue
            mtime = (Path(root) / file).stat().st_mtime
            if mtime > latest_time: latest_time = mtime
    return latest_time

def main():
    work_mtime = get_latest_work_time()
    
    hot_mtime = HOT_MD.stat().st_mtime if HOT_MD.exists() else 0
    
    if HOT_MD.exists():
        with open(HOT_MD, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > 50:
                print(f"🚨 ALERTA DEL GUARDIÁN:")
                print(f"hot.md tiene {len(lines)} líneas (Límite estricto: 50).")
                print("Estás usándolo como diario y no como memoria de trabajo.")
                print("Poda: lo que ya no obliga a nadie -> mi-vida/hot-historial-AAAA-MM.md,")
                print("y la narrativa de la sesión -> mi-vida/sesiones/. Luego vuelve a comitear.")
                exit(1)
                
    sesiones_mtime = max([f.stat().st_mtime for f in SESIONES_DIR.glob("*.md")], default=0)
    last_log_time = max(hot_mtime, sesiones_mtime)
    
    drift = work_mtime - last_log_time
    if drift > TOLERANCIA_SEGUNDOS:
        print(f"🚨 ALERTA DEL GUARDIÁN:")
        print(f"Has modificado archivos de trabajo hace {int(drift/60)} minutos,")
        print(f"pero ni hot.md ni mi-vida/sesiones/ han sido actualizados.")
        print("El agente DEBE actualizar el registro incremental ANTES de comitear o cerrar.")
        exit(1)
        
    exit(0)

if __name__ == "__main__":
    main()
