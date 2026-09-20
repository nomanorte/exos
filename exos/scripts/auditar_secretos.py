#!/usr/bin/env python3
"""auditar_secretos.py — inventario de secretos SIN exponer valores.

Compara tres sitios donde pueden vivir las claves:
  1. El manifiesto  _secrets/.env.example   (nombres canónicos, sin valores)
  2. Los archivos   .env / .env.local       (texto plano — lo que hay que jubilar)
  3. El Keychain    servicio 'tu-marca'      (destino: fuente de verdad)

Imprime SOLO nombres y presencia. Ningún valor sale por pantalla jamás.

Uso:  python3 exos/scripts/auditar_secretos.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault, raiz_web  # noqa: E402
from _raiz import hay_web  # noqa: E402

VAULT = raiz_vault()
WEB = raiz_web()          # raiz_web() ya honra NOMA_WEB
SERVICE = "tu-marca"

PLANOS = [
    VAULT / ".env",
    VAULT / ".env.local",
    *([WEB / ".env.local"] if hay_web() else []),
]
MANIFIESTO = VAULT / "_secrets" / ".env.example"


def nombres(path):
    """Devuelve solo los nombres de clave de un archivo tipo .env. Nunca los valores."""
    if not path.exists():
        return []
    out = []
    for linea in path.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre = linea.split("=", 1)[0].strip().removeprefix("export ").strip()
        if nombre:
            out.append(nombre)
    return out


def hay_llavero():
    """¿Tiene este ordenador un llavero que sepamos leer?

    16-ago-2026 · La orden `security` solo existe en macOS. Sin esta comprobación, en
    Windows y en Linux la columna del llavero salía vacía para TODO — y una auditoría que
    dice «ninguna clave está guardada» cuando en realidad no ha podido mirar es peor que
    no auditar: da una alarma falsa que se aprende a ignorar.
    """
    return shutil.which("security") is not None


def en_keychain(clave):
    """True si la clave existe en el llavero. No lee ni devuelve el valor."""
    if not hay_llavero():
        return None
    r = subprocess.run(
        ["security", "find-generic-password", "-a", clave, "-s", SERVICE],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def main():
    manifiesto = nombres(MANIFIESTO)
    planos = {}
    for p in PLANOS:
        planos[p] = nombres(p)

    todas = sorted(set(manifiesto) | {k for v in planos.values() for k in v})

    if not todas:
        print("No se ha encontrado ninguna clave. ¿Rutas correctas?")
        return 1

    if not hay_llavero():
        print("\n· Este ordenador no tiene el llavero de macOS, así que esa columna no")
        print("  se puede comprobar. Lo que sí se comprueba —y es lo que importa— es que")
        print("  ninguna clave esté escrita en texto plano dentro de tus archivos.")
    print(f"\n{'CLAVE':<34} {'texto plano':<28} {'llavero'}")
    print("-" * 76)

    pendientes, huerfanas = [], []
    for clave in todas:
        ubicaciones = [p.name if p.parent == VAULT else f"web/{p.name}"
                       for p, ks in planos.items() if clave in ks]
        kc = en_keychain(clave)
        plano_txt = ", ".join(ubicaciones) if ubicaciones else "—"
        print(f"{clave:<34} {plano_txt:<28} {'✅' if kc else '❌'}")
        if ubicaciones and not kc:
            pendientes.append(clave)
        if not ubicaciones and not kc:
            huerfanas.append(clave)

    print("-" * 76)
    print(f"Total: {len(todas)} claves")
    print(f"Por migrar al Keychain: {len(pendientes)}")
    if pendientes:
        print("  " + ", ".join(pendientes))
    if huerfanas:
        print(f"En el manifiesto pero en ningún sitio ({len(huerfanas)}): "
              + ", ".join(huerfanas))

    en_plano = sum(1 for p, ks in planos.items() if ks)
    if en_plano:
        print(f"\n⚠️  {en_plano} archivo(s) con secretos en texto plano dentro del perímetro.")
    else:
        print("\n✅ Ningún secreto en texto plano dentro del perímetro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
