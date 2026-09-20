"""secrets_loader.py — carga secretos del Keychain de macOS a os.environ.

Fuente de verdad de los secretos = Keychain (servicio 'tu-marca').
Ningún valor vive en texto plano en el cerebro. Complementa a secrets.sh (versión shell).

Uso:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from secrets_loader import load_secrets
    load_secrets()                      # carga TODAS las claves de _secrets/.env.example
    load_secrets(["GEMINI_API_KEY"])    # o solo las indicadas
"""
import os
import subprocess
from pathlib import Path

# 15-ago-2026: antes `.parent.parent.parent` — la misma atadura que `parents[2]`,
# escrita de otra forma. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

SERVICE = "tu-marca"
_NAMES = raiz_vault() / "_secrets" / ".env.example"


def _keychain(key):
    """El valor del llavero del sistema, o None. Nunca lo imprime.

    Devuelve None —sin ruido— en cualquier sistema que no traiga `security`, que son
    todos menos macOS. Quien está en Windows o Linux no tiene por qué ver un error sobre
    una herramienta que su ordenador nunca iba a tener.
    """
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", key, "-s", SERVICE, "-w"],
            capture_output=True, text=True,
        )
    except (FileNotFoundError, OSError):
        return None
    return r.stdout.rstrip("\n") if r.returncode == 0 else None


def _del_env_local(key):
    """El valor de `_secrets/.env`, o None. El archivo está en .gitignore desde el día uno."""
    archivo = raiz_vault() / "_secrets" / ".env"
    if not archivo.exists():
        return None
    try:
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            nombre, valor = linea.split("=", 1)
            if nombre.strip() == key:
                return valor.strip().strip('"').strip("'")
    except OSError:
        return None
    return None


def _names_from_manifest():
    keys = []
    if _NAMES.exists():
        for line in _NAMES.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                keys.append(line.split("=", 1)[0].strip())
    return keys


def load_secrets(keys=None, override=False):
    """Carga en os.environ los secretos indicados (o todos los de _secrets/.env.example).

    - keys=None  -> usa los nombres del manifiesto _secrets/.env.example
    - override=False -> no pisa variables ya presentes en el entorno
    Busca en el llavero del sistema y, si no está o no hay llavero, en `_secrets/.env`.
    Devuelve {clave: bool_presente} para verificación (sin exponer valores).
    """
    if keys is None:
        keys = _names_from_manifest()
    for key in keys:
        if not override and os.environ.get(key):
            continue
        # El llavero primero y el archivo después: quien tenga las dos cosas suele tener
        # el archivo desactualizado, y la copia buena es la que el sistema protege.
        val = _keychain(key)
        if val is None:
            val = _del_env_local(key)
        if val is not None:
            os.environ[key] = val
    return {k: (os.environ.get(k) is not None) for k in keys}
