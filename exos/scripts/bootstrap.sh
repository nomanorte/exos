#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# bootstrap.sh — LO PRIMERO que se ejecuta en un clon nuevo. Una sola vez.
#
#     bash exos/scripts/bootstrap.sh
#
# POR QUÉ EXISTE
#
# Los guardianes de este sistema viven en `exos/githooks/`. Para que git los use hace
# falta una línea de configuración —`core.hooksPath`— que es **local**: vive en
# `.git/config`, que no se versiona y NO viaja en un `git clone`.
#
# Consecuencia: un repositorio recién clonado llega sin guardián de archivos, sin
# guardián de doctrina y sin guardián del registro. Y no falla nada. Sencillamente
# no existen. **Un guardián ausente no se queja** — es el peor modo de fallo que
# hay, porque parece que todo va bien.
#
# Esto lo arregla en un segundo, y hay que ejecutarlo en CADA clon nuevo: el
# portátil, el ordenador de casa, y cualquier copia que hagas más adelante.
#
# La otra mitad la cubre el servidor: `.github/workflows/guardianes.yml` ejecuta
# las mismas comprobaciones en GitHub, en cada cambio, y ésa no se puede saltar ni
# olvidar. Las dos hacen falta: ésta avisa en un segundo, la otra no se olvida.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"

git config core.hooksPath exos/githooks
echo "✅ Guardianes activados (core.hooksPath = exos/githooks)"

# Los ganchos solo corren si tienen permiso de ejecución. Git ignora un gancho sin
# el bit puesto SIN avisar de nada: el candado parece instalado y no lo está.
chmod +x exos/githooks/* 2>/dev/null || true

if python3 exos/scripts/validar_vault.py --breve; then
    echo "✅ El sistema llega en estado válido. Ya puedes trabajar."
else
    echo "⚠️  El sistema llega con errores. Míralos antes de trabajar."
fi
