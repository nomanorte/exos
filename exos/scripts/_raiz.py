"""_raiz.py — encuentra la raíz del vault sin depender de la profundidad.

POR QUÉ EXISTE (15-ago-2026). Veinte scripts calculaban la raíz con
`Path(__file__).resolve().parents[2]`, que significa «sube dos carpetas». Eso ata cada
script a su posición exacta en el árbol: **moverlo lo rompe y NO se queja** — apunta a otra
carpeta y sigue corriendo. Con un vault que se reorganiza a menudo, y con generadores cuya
auditoría solo se dispara al construir, el fallo aparece semanas después: el día que vas a
entregarle a un cliente.

CÓMO LO ARREGLA. Sube desde donde esté hasta encontrar el marcador `.raiz-vault`. El script
puede vivir en cualquier carpeta y sigue funcionando. Si no encuentra el marcador, falla
**en voz alta y al arrancar**, que es cuando un fallo es barato.

USO:
    from _raiz import raiz_vault, ruta
    VAULT = raiz_vault()
    catalogo = ruta("capacidades")      # lee de exos/rutas.yaml
"""
from pathlib import Path
from typing import Optional
import os

MARCADOR = ".raiz-vault"


def raiz_vault(desde: Optional[Path] = None) -> Path:
    """Sube hasta encontrar el marcador. Explota si no está."""
    if entorno := os.environ.get("NOMA_VAULT"):
        return Path(entorno).expanduser().resolve()
    d = (desde or Path(__file__)).resolve()
    for candidata in [d, *d.parents]:
        if (candidata / MARCADOR).exists():
            return candidata
    raise SystemExit(
        f"No encuentro la raíz del vault: falta el marcador `{MARCADOR}` en ninguna carpeta "
        f"por encima de {d}. Créalo en la raíz o exporta NOMA_VAULT."
    )


def raiz_web() -> Path:
    """Dónde ESTARÍA el repositorio hermano de la web. Puede no existir.

    18-sep-2026 · Desde un carril (`.worktrees/loquesea/`) el padre NO es `~/Noma`, así que
    esto devolvía `.worktrees/web` y nadie encontraba la web. Lo cazó `generar_exos.py`, que
    falló en mitad de un build por eso. La raíz buena sale del `.git` compartido, que en un
    worktree sigue siendo el del repositorio principal."""
    if os.environ.get("NOMA_WEB"):
        return Path(os.environ["NOMA_WEB"]).resolve()
    v = raiz_vault()
    try:
        import subprocess
        r = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(v),
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            comun = Path(r.stdout.strip())
            if not comun.is_absolute():
                comun = (v / comun).resolve()
            v = comun.parent
    except Exception:
        pass
    return (v.parent / "web").resolve()


def hay_web() -> bool:
    """¿Existe de verdad el repo hermano de la web?

    18-sep-2026: estos scripts viajan dentro de EXOS, y **EXOS ya no lleva web** — construir
    webs es un programa aparte. Sin esta pregunta, la entrega le enseñaba al alumno un
    apartado «encargos en el repo web» de un repositorio que nunca ha tenido, y escaneaba
    secretos en una carpeta inexistente. Aquí la web es opcional: si está, se usa; si no,
    esa parte no existe y nadie se entera. Vale igual para el vault de la persona, que sí la
    tiene, sin cambiar su comportamiento ni una coma."""
    return raiz_web().is_dir()


def rutas_declaradas(vault: Optional[Path] = None) -> dict:
    """Las rutas de `rutas.yaml` **tal cual**, o sea relativas a la raíz.

    Se pasa `vault` cuando la pregunta no es por el vault de esta máquina: la auditoría
    de entrega corre contra un worktree o una copia recién generada, y ese árbol declara
    su propia distribución. Leer siempre el `rutas.yaml` local haría que una copia con
    otra estructura se auditara con el mapa equivocado.
    """
    import yaml  # se importa aquí para no exigirlo a quien solo quiere raiz_vault()
    v = Path(vault).resolve() if vault else raiz_vault()
    return yaml.safe_load((v / "exos" / "rutas.yaml").read_text())["rutas"]


def ruta(clave: str, vault: Optional[Path] = None) -> Path:
    """Resuelve una ruta declarada en `exos/rutas.yaml`.

    Las rutas del generador se declaran en UN sitio. Reorganizar el vault pasa a ser editar
    un archivo, no perseguir rutas literales por ocho scripts.
    """
    v = Path(vault).resolve() if vault else raiz_vault()
    declaradas = rutas_declaradas(v)
    if clave not in declaradas:
        raise SystemExit(
            f"Ruta `{clave}` no declarada en exos/rutas.yaml. "
            f"Declaradas: {', '.join(sorted(declaradas))}"
        )
    return v / declaradas[clave]
