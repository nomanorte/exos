#!/usr/bin/env bash
# rotar_secreto.sh — guarda una clave SIN que pase por el chat ni quede en ningún registro.
#
# POR QUÉ EXISTE. La forma natural de darle una clave a un agente es pegarla en el chat, y
# eso la deja escrita para siempre en el historial de esa conversación — que ni tú controlas
# ni puedes borrar del todo. Este script abre una ventana del sistema con el campo oculto,
# tú tecleas ahí, y el valor va del teclado al llavero sin pasar por ningún sitio
# intermedio. **No se imprime nunca**: ni en pantalla, ni en un archivo, ni en la respuesta
# del agente.
#
# ⚠️ SOLO FUNCIONA EN macOS, porque usa el llavero del sistema y su ventana nativa. Si
# estás en Windows o Linux, te lo dice al arrancar y te explica qué hacer en su lugar —
# no falla en silencio.
#
# Uso (lo lanza tu AGENTE, no tú):
#   rotar_secreto.sh NOMBRE_CLAVE              → pregunta y guarda en el llavero
#   rotar_secreto.sh NOMBRE_CLAVE --generar    → la inventa el script y la guarda
#
# `--generar` es para las claves que no te da nadie: las que te inventas tú, como el token
# de una ruta de administración. Así no hay que teclear a mano algo largo y aleatorio.

set -euo pipefail

# Antes que nada: ¿estamos donde este script puede funcionar?
if ! command -v security >/dev/null 2>&1; then
  cat <<'FIN'
⛔ Este script necesita el llavero de macOS, y este ordenador no lo tiene.

   No es un fallo tuyo ni te falta nada: guardar claves se hace distinto en cada sistema.
   Tienes dos maneras igual de válidas:

   1. Tu gestor de contraseñas (1Password, Bitwarden…). Es la mejor si ya usas uno: casi
      todos saben soltar las claves al entorno cuando abres una terminal.
   2. El archivo `_secrets/.env`, una línea por clave (NOMBRE=valor). Está en .gitignore
      desde el primer día, así que no se sube ni viaja en una copia del proyecto.

   Las dos cumplen la regla que importa: la clave no vive dentro de un archivo del
   proyecto. Díselo a tu agente y te deja montada la que prefieras.
FIN
  exit 2
fi
set +x   # por si alguien hereda trazas: aquí no se traza nada

CLAVE="${1:?Uso: rotar_secreto.sh NOMBRE_CLAVE [--vercel|--sincronizar]}"
MODO="${2:-}"
SERVICE="tu-marca"
REPO_WEB="${NOMA_WEB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/web}"

case "$CLAVE" in
  *[!A-Z0-9_]*) echo "⛔ Nombre de clave inválido: solo MAYÚSCULAS, números y _" >&2; exit 1 ;;
esac

# ── Modo sincronizar: el valor sale del Llavero, no del teclado ──────────────
if [ "$MODO" = "--sincronizar" ]; then
  VALOR="$(security find-generic-password -s "$SERVICE" -a "$CLAVE" -w 2>/dev/null || true)"
  if [ -z "$VALOR" ]; then
    echo "⛔ '$CLAVE no está en el Llavero. Guárdala primero sin --sincronizar." >&2
    exit 1
  fi
  echo "→ Copiando «$CLAVE del Llavero a Vercel producción (el valor no se imprime)…"
  cd "$REPO_WEB"
  npx --yes vercel env rm "$CLAVE" production --yes >/dev/null 2>&1 || true
  printf '%s' "$VALOR" | npx --yes vercel env add "$CLAVE" production >/dev/null 2>&1
  unset VALOR
  echo "✅ Vercel producción actualizado · $CLAVE"
  echo "⚠️  No llega al sitio hasta el siguiente despliegue."
  exit 0
fi

# ── Modo generar: el valor lo inventa el script y no lo ve nadie ─────────────
if [ "$MODO" = "--generar" ] || [ "$MODO" = "--generar-vercel" ]; then
  # 48 caracteres al azar. Solo letras y números: los símbolos se rompen al viajar por
  # una cabecera HTTP o una URL, y depurar eso después es un infierno.
  #
  # `head -c 512` PRIMERO y `cut` al final, a propósito: leer /dev/urandom sin límite y
  # cortar con `head` al final le cierra la tubería a `tr` a media escritura, y este
  # script aborta al primer error. Se leen 512 bytes —de sobra para sacar 48 caracteres—
  # y todo el mundo termina de su propia cuenta.
  VALOR="$(head -c 512 /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9' | cut -c1-48)"
  if [ "${#VALOR}" -ne 48 ]; then
    echo "⛔ No se pudo generar un valor completo. No se ha tocado nada." >&2
    exit 1
  fi
  security add-generic-password -a "$CLAVE" -s "$SERVICE" -w "$VALOR" -U >/dev/null 2>&1
  echo "✅ Generado y guardado en el Llavero (48 caracteres) · $CLAVE"
  echo "   Nadie lo ha visto: ni tú, ni el agente, ni la pantalla."

  NAMES_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_secrets/.env.example"
  if [ -f "$NAMES_FILE" ] && ! grep -q "^${CLAVE}=" "$NAMES_FILE"; then
    echo "${CLAVE}=" >> "$NAMES_FILE"
    echo "✅ Nombre añadido al manifiesto (sin valor)"
  fi

  if [ "$MODO" = "--generar-vercel" ]; then
    echo "→ Poniéndolo también en Vercel (PRODUCCIÓN)…"
    cd "$REPO_WEB"
    npx --yes vercel env rm "$CLAVE" production --yes >/dev/null 2>&1 || true
    printf '%s' "$VALOR" | npx --yes vercel env add "$CLAVE" production >/dev/null 2>&1
    echo "✅ Vercel producción actualizado · $CLAVE"
    echo "⚠️  NO llega al sitio hasta el siguiente despliegue."
  fi
  unset VALOR
  echo "🔒 Hecho."
  exit 0
fi

echo "→ Abriendo la ventana para «$CLAVE. Mira la pantalla."
echo "  (el valor no se imprime aquí ni queda en ningún registro)"

# La ventana. `with hidden answer` = campo de puntitos. Si la persona cancela, salimos limpio.
VALOR="$(osascript <<OSA 2>/dev/null || true
try
  set res to display dialog "Pega aquí el valor de " & "" & return & return & "No se mostrará ni se guardará en ningún registro." default answer "" with hidden answer with title "tu marca · rotar credencial" buttons {"Cancelar", "Guardar"} default button "Guardar" with icon caution
  if button returned of res is "Guardar" then
    return text returned of res
  end if
end try
return ""
OSA
)"

if [ -z "$VALOR" ]; then
  echo "⏹  Cancelado o vacío. No se ha tocado nada."
  exit 0
fi

# ── 1 · Llavero de macOS (fuente de verdad local) ────────────────────────────
security add-generic-password -a "$CLAVE" -s "$SERVICE" -w "$VALOR" -U >/dev/null 2>&1
echo "✅ Guardado en el Llavero (servicio '$SERVICE') · $CLAVE"

# Deja el nombre —solo el nombre— en el manifiesto, para que secrets_loader lo cargue.
NAMES_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_secrets/.env.example"
if [ -f "$NAMES_FILE" ] && ! grep -q "^${CLAVE}=" "$NAMES_FILE"; then
  echo "${CLAVE}=" >> "$NAMES_FILE"
  echo "✅ Nombre añadido al manifiesto (sin valor)"
fi

# ── 2 · Vercel producción, solo si se pide ───────────────────────────────────
if [ "$MODO" = "--vercel" ]; then
  echo "→ Actualizando también Vercel (PRODUCCIÓN)…"
  cd "$REPO_WEB"
  npx --yes vercel env rm "$CLAVE" production --yes >/dev/null 2>&1 || true
  printf '%s' "$VALOR" | npx --yes vercel env add "$CLAVE" production >/dev/null 2>&1
  echo "✅ Vercel producción actualizado · $CLAVE"
  echo "⚠️  Un cambio de variable NO llega al sitio hasta el siguiente despliegue."
fi

unset VALOR
echo "🔒 Hecho. El valor no ha quedado en ningún sitio salvo donde debía."
