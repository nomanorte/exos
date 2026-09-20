#!/bin/bash
# autoguardado.sh — guarda tu trabajo aunque nadie se acuerde de hacerlo.
#
# EL PROBLEMA QUE RESUELVE. Guardar el trabajo (hacer «commit») es el último paso de cada
# sesión, y es justo el que más se pierde: si la conversación se corta, si el agente se
# queda sin espacio, o sencillamente si se olvida. Lo que no se guarda no existe mañana —
# y el que lo descubre eres tú, dos días después, buscando algo que creías hecho.
#
# Este script mira si hay cambios sin guardar y los guarda. Nada más.
#
# ⚠️ LO QUE HACE Y LO QUE NO. Guarda TODO lo que haya cambiado, sin revisarlo uno a uno.
# Eso es a propósito: la alternativa —elegir qué se guarda— es precisamente lo que no
# ocurre cuando nadie está mirando. **Los guardianes siguen mandando**: si alguno bloquea,
# no se guarda nada, se deshace y queda anotado en el registro para que lo veas. O sea que
# esto no se salta ninguna regla tuya; solo evita que el trabajo se quede en el aire.
#
# Si prefieres decidir tú qué entra en cada guardado, no lo programes: es opcional y el
# sistema funciona igual sin él.
#
# CÓMO SE ENCIENDE. No corre solo por existir — hay que programarlo:
#
#     python3 exos/scripts/programar_autoguardado.py
#
# Eso te lo deja funcionando en tu ordenador, sea cual sea tu sistema.

set -uo pipefail

# La raíz se busca subiendo hasta el marcador, nunca escrita a mano: así el script sigue
# funcionando si mueves tu carpeta de sitio, que es lo normal tarde o temprano.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
while [ "$DIR" != "/" ] && [ ! -e "$DIR/.raiz-vault" ]; do
    DIR="$(dirname "$DIR")"
done
if [ ! -e "$DIR/.raiz-vault" ]; then
    echo "No encuentro la raíz: falta el marcador .raiz-vault por encima de este script." >&2
    exit 1
fi

cd "$DIR" || exit 1

LOG="$DIR/exos/scripts/logs/autoguardado.log"
mkdir -p "$(dirname "$LOG")"
ahora() { date '+%Y-%m-%d %H:%M:%S'; }

# Sin cambios, no hay nada que hacer. Ni log ni ruido: un registro que crece cada pocos
# minutos diciendo «no pasó nada» es un registro que nadie vuelve a abrir.
if [ -z "$(git status --porcelain)" ]; then
    exit 0
fi

echo "[$(ahora)] Hay cambios sin guardar. Guardando…" >> "$LOG"
git add -A

if git commit -m "Autoguardado: trabajo de la sesión" >> "$LOG" 2>&1; then
    echo "[$(ahora)] ✅ Guardado, y los guardianes lo dieron por bueno." >> "$LOG"
else
    # Se deshace el `add` a propósito: dejar archivos a medio preparar hace que el
    # siguiente guardado —tuyo o de un agente— arrastre cosas que nadie eligió.
    git reset >/dev/null 2>&1
    echo "[$(ahora)] ⛔ Un guardián lo bloqueó. NO se ha guardado nada y hay que mirarlo." >> "$LOG"
    echo "[$(ahora)]    Pídeselo a tu agente: «mira el log del autoguardado»." >> "$LOG"
fi
