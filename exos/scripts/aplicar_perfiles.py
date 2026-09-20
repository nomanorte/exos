#!/usr/bin/env python3
"""aplicar_perfiles.py — traduce `exos/perfiles-agentes.yaml` a cada herramienta.

La política se declara UNA vez, en el repositorio, y se versiona. Cada programa
—Antigravity, OpenCode, Claude, Codex o el que venga— recibe su traducción. Añadir una
herramienta nueva es escribir un adaptador aquí, no reorganizar nada. Se comprobó el
1-ago-2026: dar de alta OpenCode fueron ~100 líneas en este archivo y CERO cambios en
el vault. Esa es la prueba de que la fuente única funciona.

Uso (lo ejecuta un agente, con la autorización de la persona):
    aplicar_perfiles.py --herramienta antigravity            → enseña el cambio
    aplicar_perfiles.py --herramienta antigravity --aplicar  → lo escribe
    aplicar_perfiles.py --herramienta opencode [--aplicar]  → escribe opencode.json
    aplicar_perfiles.py --herramienta claude   [--aplicar]
    aplicar_perfiles.py --herramienta codex                  → borrador para revisar
    aplicar_perfiles.py --todas                              → simula todas

Reglas duras de este script:
  · Sin `--aplicar` no escribe NADA. Nunca.
  · Antes de escribir hace copia de seguridad con fecha.
  · **Aborta si el cambio hiciera desaparecer una regla `deny` que ya existía.**
    Un traductor que relaja permisos en silencio es peor que no tenerlo.
  · Cada aplicación queda anotada en `exos/logs/` y sale como aviso al arrancar
    la siguiente sesión. Autorizar sí; en silencio, no.
  · Antigravity tiene que estar CERRADO o sobrescribe el archivo al salir.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

# 15-ago-2026: antes `parents[2]` — «sube dos carpetas», que ata el script a su sitio
# exacto y, al moverlo, apunta a otra carpeta SIN quejarse. Ver _raiz.py.
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _raiz import raiz_vault  # noqa: E402

VAULT = raiz_vault()
PERFILES = VAULT / "exos" / "perfiles-agentes.yaml"
LOG = VAULT / "exos" / "logs" / "perfiles-aplicados.log"

GEMINI = Path.home() / ".gemini" / "config"
CODEX_BORRADOR = VAULT / "exos" / "reglas-ide" / "codex-config.borrador.toml"

OFF = "CASCADE_COMMANDS_AUTO_EXECUTION_OFF"
AUTO = "CASCADE_COMMANDS_AUTO_EXECUTION_AUTO"
EN_SANDBOX = "CASCADE_COMMANDS_AUTO_EXECUTION_PROCEED_IN_SANDBOX"
NIEGA = "AGENT_SETTING_POLICY_DENY"


# ─── utilidades ──────────────────────────────────────────────────────────────

def cargar() -> dict:
    if not PERFILES.exists():
        sys.exit(f"⛔ No encuentro {PERFILES}")
    # El archivo lleva el frontmatter del vault (--- tipo/estado/fecha ---) como
    # PRIMER documento YAML; el perfil de verdad es el ÚLTIMO. `safe_load` exige
    # un solo documento y reventaba —roto en silencio desde que se añadió el
    # frontmatter—; `safe_load_all` los tolera y cogemos el último.
    docs = [d for d in yaml.safe_load_all(PERFILES.read_text(encoding="utf-8"))
            if isinstance(d, dict)]
    return docs[-1]


def ruta_abs(entrada: str, cfg: dict) -> str:
    """`repo:web` → la raíz del repo web. `repo:web/archivo` → archivo dentro. Lo demás, relativo al vault."""
    if entrada.startswith("repo:"):
        partes = entrada.split(":", 1)[1].split("/", 1)
        repo_name = partes[0]
        base = cfg["repos"][repo_name]
        if len(partes) > 1:
            return f"{base}/{partes[1]}"
        return f"{base}/"
    if entrada.startswith("**"):
        return entrada
    if entrada.startswith("/"):
        return entrada
    return f"{cfg['repos']['vault']}/{entrada}"


def antigravity_abierto() -> bool:
    r = subprocess.run(["pgrep", "-x", "Antigravity"], capture_output=True)
    if r.returncode == 0:
        return True
    # La app se llama «Antigravity IDE.app» desde la 2.x: buscar «Antigravity.app» ya no
    # la encontraba y el candado de «ciérralo antes» no saltaba. Se mira el ejecutable
    # principal, no los ayudantes que quedan vivos al cerrar (crashpad).
    r = subprocess.run(["pgrep", "-f", r"Antigravity( IDE)?\.app/Contents/MacOS/"],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def con_mesa(cfg: dict) -> dict:
    """Los perfiles vistos desde Antigravity: el vault es SU copia, no la de la persona."""
    mesa = cfg.get("antigravity") or {}
    if not mesa.get("repos"):
        return cfg
    return {**cfg, "repos": {**cfg["repos"], **mesa["repos"]}}


def adaptar_antigravity_global(cfg: dict, conf: dict, cambios: list[str]) -> None:
    """Lo global: que ningún chat —dentro o fuera de un proyecto— escriba en main.

    Solo QUITA concesiones que abren esa puerta (`write_file(*)` y escrituras en los
    repos de la persona) y las dos órdenes de un solo uso con datos personales que se habían
    quedado guardadas. Los `deny` solo se suman.
    """
    mesa = cfg.get("antigravity") or {}
    nunca = mesa.get("nunca_escribe", [])
    if not nunca:
        return
    us = conf.setdefault("userSettings", {})
    g = us.setdefault("globalPermissionGrants", {})

    def sobra(regla: str) -> bool:
        if regla == "write_file(*)" or regla.startswith("command(cat << "):
            return True
        return regla.startswith("write_file(") and any(regla[11:].startswith(n) for n in nunca)

    allow = g.get("allow", [])
    nuevo_allow = [r for r in allow if not sobra(r)]
    if nuevo_allow != allow:
        cambios.append(f"  global       permisos: {len(nuevo_allow) - len(allow):+d} allow "
                       "(escribir en todo, escribir en los repos de la persona, órdenes de un uso)")
        g["allow"] = nuevo_allow

    deny = g.get("deny", [])
    nuevo_deny = deny + [r for r in [f"write_file({n})" for n in nunca] + ["unsandboxed(*)"]
                         if r not in deny]
    if nuevo_deny != deny:
        cambios.append(f"  global       permisos: {len(nuevo_deny) - len(deny):+d} deny "
                       "(repos de la persona · fuera del sandbox)")
        g["deny"] = nuevo_deny

    for clave, valor in (("nonWorkspaceFileAccessPolicy", NIEGA),
                         ("autoExecutionPolicy", EN_SANDBOX),
                         ("enableTerminalSandbox", True)):
        if us.get(clave) != valor:
            cambios.append(f"  global       {clave} → {valor}")
            us[clave] = valor


def anotar(herramienta: str, cambios: list[str]) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    sello = datetime.now().strftime("%Y-%m-%d %H:%M")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{sello} | {herramienta} | {len(cambios)} cambio(s)\n")
        for c in cambios:
            f.write(f"    {c.strip()}\n")


def copia(p: Path) -> None:
    sello = datetime.now().strftime("%Y-%m-%d")
    shutil.copy2(p, p.with_suffix(f".antes-perfiles-{sello}{p.suffix}"))


def reglas_de(nombre: str, a: dict, cfg: dict) -> dict:
    """Las cuatro piezas del perímetro, ya en rutas absolutas."""
    permite = set(a.get("permite_pese_a_niega", []))

    lee = [ruta_abs(x, cfg) for x in cfg["nucleo_lee"]]
    lee += [ruta_abs(x, cfg) for x in a.get("lee_extra", [])]

    escribe = [ruta_abs(x, cfg) for x in a.get("escribe", [])]
    escribe += [ruta_abs(x, cfg) for x in cfg["comun_escribe"]]

    niega = [ruta_abs(x, cfg) for x in cfg["niega_todos"] if x not in permite]
    niega += [ruta_abs(x, cfg) for x in a.get("niega_extra", [])]

    # Un agente puede tener la terminal en automático y aun así haber comandos que
    # nunca deben correr sin que la persona los vea. La decisión no es «automático o
    # preguntar»: es qué sale de su ordenador.
    return {"lee": lee, "escribe": escribe, "niega": niega,
            "comandos_niega": cfg.get("niega_comandos", []) + a.get("comandos_preguntan", []),
            "terminal": a.get("terminal", "preguntar")}


# ─── VERIFICAR — ¿lo declarado coincide con lo aplicado? ─────────────────────
# Existe por un fallo real del 30-jul: La persona le dejó un encargo a agente-web en una carpeta
# que este archivo decía alcanzable, y en Claude Code no lo era. Un documento que dice
# quién puede leer qué y NO es cierto es peor que no tenerlo: cualquier agente que lo
# consulte para planificar, planifica mal — exactamente como le pasó a él.
#
# Y la parte incómoda que hay que decir en voz alta: **este archivo solo lo impone
# Antigravity**. Claude Code no tiene perímetro por agente (la sesión hereda la carpeta
# que abres) y Codex está sin configurar. Para esas dos, el perfil es documentación,
# no cerradura. Eso se declara aquí en vez de fingir que las tres son iguales.

IMPONE = {
    "antigravity": "SÍ — proyectos con carpetas y listas allow/deny por agente",
    "opencode": "SÍ — `agent.<n>.permission` con globs de ruta, y el archivo VIAJA en git",
    "claude": "PARCIAL — solo el suelo común (deny). El alcance lo da la carpeta que abres",
    "codex": "NO — sin configurar; su perímetro es el repo de la tarea",
    # Warp NO tiene adaptador y no lo tendrá: no es que falte trabajo, es que su modelo
    # de permisos no puede expresar lo que declara el vault. Verificado el 2026-08-02:
    # controla QUÉ COMANDOS corren sin preguntar (listas de regex en Ajustes > AI), no
    # QUÉ RUTAS puede tocar cada agente. Y esas listas viven en los ajustes de la app,
    # no en el repositorio: no viajan y no se revisan en un pull request.
    # ⇒ Si la persona usa Warp, que sea como TERMINAL ejecutando `opencode` dentro. Así
    #   conserva el perímetro entero. Si usa el agente propio de Warp, hereda la
    #   doctrina (lee AGENTS.md) pero NO el perímetro por agente.
    "warp": "NO APLICA — permisos por comando, no por ruta; y viven fuera del repo",
}


def verificar(cfg: dict) -> int:
    print("¿Lo que declara el archivo es lo que aplica cada herramienta?\n")
    for h, q in IMPONE.items():
        print(f"  {h:<12} {q}")
    print()

    fallos = 0
    proyectos = {}
    for f in (GEMINI / "projects").glob("*.json"):
        if "antes-" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        proyectos[d.get("name", "?")] = d

    print("── Antigravity: declarado vs aplicado ──")
    cfg = con_mesa(cfg)
    for nombre, a in cfg["agentes"].items():
        if a.get("activo") is False:
            continue
        proy = a.get("proyecto")
        d = proyectos.get(proy)
        if d is None:
            print(f"  ✗ {nombre:<9} el proyecto «{proy}» no existe")
            fallos += 1
            continue

        r = reglas_de(nombre, a, cfg)
        pg = d.get("permissionGrants", {}).get("permissionGrants", {})
        allow, deny = set(pg.get("allow", [])), set(pg.get("deny", []))

        choques = allow & deny
        faltan = {f"read_file({x})" for x in r["lee"]} - allow - deny
        conceden_y_niegan = {x for x in r["lee"] if f"read_file({x})" in deny}

        estado = "✓" if not (choques or faltan or conceden_y_niegan) else "✗"
        print(f"  {estado} {nombre:<9} ({proy})")
        for c in sorted(choques):
            print(f"      contradicción: «{c}» en allow Y en deny"); fallos += 1
        for x in sorted(conceden_y_niegan):
            print(f"      el perfil concede «{x}» pero está NEGADO → no lo alcanza"); fallos += 1
        for x in sorted(faltan):
            print(f"      declarado y no aplicado: {x}"); fallos += 1

    print()
    if fallos:
        print(f"❌ {fallos} desajuste(s). El archivo está afirmando algo que no es cierto.")
        print("   Arréglalo antes de que un agente planifique con él.")
        return 1
    print("✅ Lo declarado coincide con lo aplicado en Antigravity.")
    print("   Recuerda: en Claude y Codex el perímetro por agente NO se impone.")
    return 0


# ─── adaptador · OPENCODE ────────────────────────────────────────────────────
# Añadido el 1-ago-2026, cuando la persona planteó usar OpenCode como tercera sala para
# cuando se le acaben los tokens. La pregunta que hizo era la correcta: «¿tengo que
# configurar algo a mano?». Respuesta: no, porque añadir una herramienta es escribir
# un adaptador aquí — que es justo para lo que se creó `perfiles-agentes.yaml`.
#
# Verificado en la documentación de OpenCode el 1-ago-2026 (no de memoria):
#   · `opencode.json` en la raíz del proyecto · $schema https://opencode.ai/config.json
#   · `permission` admite: read · edit · glob · grep · bash · task · skill · lsp ·
#     question · webfetch · websearch · external_directory · doom_loop
#   · valores: allow | ask | deny
#   · `edit` y `bash` admiten MAPA DE PATRONES, y **gana la última regla que encaja**
#     → por eso el orden de las claves importa: primero `*`, luego permisos, y las
#       denegaciones AL FINAL.
#   · `agent.<nombre>.permission` sobrescribe al bloque global → los seis agentes
#     caben tal cual, que es lo que Claude Code NO puede hacer.
#   · lee `AGENTS.md` y `CLAUDE.md` solo, subiendo desde la carpeta actual.
#
# POR QUÉ ESTE ES EL MEJOR DE LOS CUATRO para lo que la persona quiere:
# el archivo vive DENTRO del repositorio y se versiona. La configuración de
# Antigravity vive en `~/.gemini/` — no viaja, no se revisa y se pierde al cambiar de
# ordenador. Este sí sube a GitHub con el resto.
#
# DECISIÓN DE CRITERIO, declarada porque no es obvia:
#   · `edit` se traduce como LISTA BLANCA (`*: deny` y luego lo suyo).
#   · `read` se traduce como LISTA NEGRA (`*: allow` y luego lo negado).
# No es incoherencia: es la asimetría real del daño. Leer el documento equivocado es
# un problema de foco; escribirlo es un problema de verdad. Y así se replica lo que
# Antigravity impone hoy, en vez de estrenar un perímetro distinto por herramienta.

OPENCODE_CONF = VAULT / "opencode.json"


def _glob(ruta: str) -> str:
    """Ruta absoluta → glob PORTABLE.

    Las de dentro del vault se vuelven relativas y las de fuera usan `~`. Sin esto el
    archivo llevaría `~/` escrito dentro, y un archivo versionado que
    contiene la ruta de un ordenador concreto no viaja: es justo lo que la persona quiere
    evitar al subirlo a GitHub.
    """
    v = str(VAULT)
    if ruta.startswith(v):
        ruta = ruta[len(v):].lstrip("/") or "."
    else:
        h = str(Path.home())
        if ruta.startswith(h):
            ruta = "~" + ruta[len(h):]
    if ruta.endswith("/"):
        return ruta + "**"
    return ruta + "/**" if "." not in Path(ruta).name else ruta


def adaptar_opencode(cfg: dict, aplicar: bool) -> int:
    # ⚠️ JSON NO TIENE COMENTARIOS y OpenCode valida el schema de forma ESTRICTA.
    # La primera versión metía una clave `"//"` con la nota de «generado, no editar» y
    # OpenCode se negó a arrancar: «Unrecognized key: //». La advertencia vive en la guía
    # (`exos/protocolos/PROTOCOLO — Permisos de agentes` §3-bis) y en este
    # script, no dentro del archivo.
    conf = {
        "$schema": "https://opencode.ai/config.json",
        "instructions": ["AGENTS.md", "CLAUDE.md", "mi-vida/hot.md"],
    }
    # Conserva claves locales (provider, model, mcp…) que no salen de perfiles.
    if OPENCODE_CONF.exists():
        try:
            prev = json.loads(OPENCODE_CONF.read_text(encoding="utf-8"))
            for k in ("provider", "model", "small_model", "theme", "keybinds",
                      "mcp", "formatter", "lsp", "share", "autoupdate", "username",
                      "disabled_providers", "enabled_providers"):
                if k in prev and k not in conf:
                    conf[k] = prev[k]
        except json.JSONDecodeError:
            pass

    # Suelo común: lo que ningún agente puede hacer, en ninguna sala.
    # ORDEN IMPORTANTE: OpenCode deja ganar la ÚLTIMA regla que encaja →
    # `*` primero, luego matices, deny AL FINAL.
    #
    # 2026-08-04 la persona: bash en `ask` hace OpenCode inoperable (confirma cada
    # comando, incluido el ritual de arranque). La seguridad real NO está en el
    # ask de terminal (la terminal se salta deny de archivos). Aquí: allow +
    # niega_comandos. Lo delicado (push, vercel…) sigue en `comandos_preguntan`.
    suelo_bash = {"*": "allow"}
    for c in cfg.get("niega_comandos", []):
        suelo_bash[f"{c} *"] = "deny"
        suelo_bash[f"{c}*"] = "deny"
    suelo_edit = {"*": "allow"}
    for x in cfg["niega_todos"]:
        suelo_edit[_glob(ruta_abs(x, cfg))] = "deny"

    conf["permission"] = {
        "read": {"*": "allow", **{_glob(ruta_abs(x, cfg)): "deny" for x in cfg["niega_todos"]}},
        "edit": suelo_edit,
        "bash": suelo_bash,
        # Fuera del proyecto: allow en repos declarados; el resto pregunta.
        # `*: ask` puro obligaba a confirmar hasta ~/tu-proyecto/web en cada paso.
        "external_directory": {"*": "ask", "~/tu-proyecto/web/**": "allow"},
        "webfetch": "allow",
        "websearch": "allow",
    }

    agentes = {}
    for nombre, a in cfg["agentes"].items():
        if a.get("activo") is False:
            continue
        r = reglas_de(nombre, a, cfg)

        # ── edit: lista blanca. `*: deny` primero, permisos después, denegado al final.
        edit = {"*": "deny"}
        for x in r["escribe"]:
            edit[_glob(x)] = "allow"
        for x in r["niega"]:
            edit[_glob(x)] = "deny"

        # ── read: lista negra. Todo salvo lo explícitamente negado.
        read = {"*": "allow"}
        for x in r["niega"]:
            read[_glob(x)] = "deny"

        # ── bash: allow por defecto (ver nota del suelo, 2026-08-04).
        # `comandos_preguntan` y `niega_comandos` van DESPUÉS y ganan.
        bash = {"*": "allow"}
        for c in a.get("comandos_preguntan", []):
            bash[f"{c}*"] = "ask"
        for c in cfg.get("niega_comandos", []):
            bash[f"{c} *"] = "deny"
            bash[f"{c}*"] = "deny"

        perm = {"read": read, "edit": edit, "bash": bash}

        # Quien trabaja en los dos repos necesita salir del vault sin que le pregunten
        # cada vez. El resto, no: `*: ask` heredado del suelo.
        otros = [cfg["repos"][x] for x in a.get("repos", []) if cfg["repos"][x] != str(VAULT)]
        if otros:
            perm["external_directory"] = {"*": "ask",
                                          **{_glob(p + "/"): "allow" for p in otros}}

        # `mode: primary` es OBLIGATORIO para que la persona pueda elegirlo con Tab. Sin él,
        # OpenCode lo trata como subagente invocable por otro agente, no como sala en la
        # que sentarse — y el equivalente al «proyecto» de Antigravity dejaría de existir
        # para él. Comprobado en la documentación el 2026-08-02.
        agentes[nombre] = {
            "mode": "primary",
            "description": f"{a.get('proyecto', '?')} · dominio {a.get('dominio', '?')}",
            "permission": perm,
        }

    conf["agent"] = agentes

    # Trinquete contra el fallo del 2026-08-02: solo claves que OpenCode reconoce.
    # Un archivo de configuración que el programa rechaza no es un error menor — deja a
    # la persona sin poder abrir la herramienta, y el mensaje que da no dice cómo arreglarlo.
    PERMITIDAS = {"$schema", "instructions", "permission", "agent", "provider",
                  "model", "theme", "keybinds", "mcp", "formatter", "lsp",
                  "share", "autoupdate", "username", "small_model", "disabled_providers"}
    invasoras = set(conf) - PERMITIDAS
    if invasoras:
        print(f"⛔ Claves no reconocidas por OpenCode: {sorted(invasoras)}")
        print("   Se aborta: escribir esto dejaría a la persona sin poder abrir la herramienta.")
        return 1

    nuevo = json.dumps(conf, indent=2, ensure_ascii=False) + "\n"
    antes = OPENCODE_CONF.read_text(encoding="utf-8") if OPENCODE_CONF.exists() else ""

    print(f"OpenCode — {OPENCODE_CONF.relative_to(VAULT)} (versionado: SÍ viaja a GitHub)\n")
    print(f"  agentes con perímetro propio: {', '.join(agentes)}")
    print(f"  suelo común: {len(cfg['niega_todos'])} rutas negadas · "
          f"{len(cfg.get('niega_comandos', []))} comandos negados")
    for nombre, d in agentes.items():
        e = d["permission"]["edit"]
        b = d["permission"]["bash"]["*"]
        print(f"    · {nombre:<9} escribe en {sum(1 for v in e.values() if v == 'allow')} sitios "
              f"· terminal {b}")

    if antes == nuevo:
        print("\n✓ Ya estaba al día. Nada que cambiar.")
        return 0
    if not aplicar:
        print("\n(simulación) Añade --aplicar para escribirlo.")
        return 0

    if OPENCODE_CONF.exists():
        copia(OPENCODE_CONF)
    OPENCODE_CONF.write_text(nuevo, encoding="utf-8")
    anotar("opencode", [f"opencode.json regenerado · {len(agentes)} agentes"])
    print(f"\n✅ Escrito {OPENCODE_CONF.relative_to(VAULT)}.")
    print("   la persona no tiene que tocar nada: OpenCode lo lee al abrir la carpeta.")
    return 0


# ─── adaptador · ANTIGRAVITY ─────────────────────────────────────────────────

def adaptar_antigravity(cfg: dict, aplicar: bool) -> int:
    conf_global = GEMINI / "config.json"
    if not conf_global.exists():
        print("⛔ No encuentro la configuración de Antigravity."); return 1

    if aplicar and antigravity_abierto():
        print("⛔ Antigravity está ABIERTO. Ciérralo o sobrescribirá el archivo al salir.")
        return 1

    # Índice de proyectos por nombre
    proyectos: dict[str, tuple[Path, dict]] = {}
    for f in (GEMINI / "projects").glob("*.json"):
        if "antes-" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        proyectos[d.get("name", "?")] = (f, d)

    cambios: list[str] = []
    tocados: list[tuple[Path, dict]] = []

    conf = json.loads(conf_global.read_text(encoding="utf-8"))
    adaptar_antigravity_global(cfg, conf, cambios)
    if cambios:
        tocados.append((conf_global, conf))

    mesa = cfg.get("antigravity") or {}
    cfg = con_mesa(cfg)

    for nombre, a in cfg["agentes"].items():
        if a.get("activo") is False:
            continue
        proy = a.get("proyecto")
        if proy not in proyectos:
            cambios.append(f"  ⚠️  {nombre}: no existe el proyecto «{proy}» — créalo en Antigravity")
            continue
        f, d = proyectos[proy]
        r = reglas_de(nombre, a, cfg)

        pg = d.setdefault("permissionGrants", {}).setdefault("permissionGrants", {})
        deny_antes = set(pg.get("deny", []))

        con_su_mesa = proy in mesa.get("proyectos_con_mesa", [])
        nuevo_deny = sorted({f"read_file({x})" for x in r["niega"]}
                            | {f"write_file({x})" for x in r["niega"]}
                            | {f"command({c})" for c in r["comandos_niega"]}
                            | ({f"write_file({n})" for n in mesa.get("nunca_escribe", [])}
                               if con_su_mesa else set())
                            | deny_antes)                      # nunca se pierde nada
        candidato_allow = ({f"read_file({x})" for x in r["lee"]}
                           | {f"write_file({x})" for x in r["escribe"]}
                           | {f"read_file({x})" for x in r["escribe"]})

        # Los comandos de solo lectura (ritual de arranque, cat/ls/git…) se
        # conceden como `command(...)`, simétrico al deny. Antigravity usa regex
        # en el argumento —de ahí las dos formas— y el deny sigue ganando abajo.
        for c in cfg.get("comandos_lectura", []):
            candidato_allow.add(f"command({c})")
            candidato_allow.add(f"command({c} .*)")

        # EL DENY GANA, SIEMPRE. La primera versión unía las dos listas sin mirar y
        # producía reglas que se contradicen: una misma carpeta acabó en allow Y en deny
        # para agente-web, porque el perfil lo concedía y una regla vieja lo negaba. Nadie
        # sabe entonces qué manda, y el archivo de perfiles pasa a afirmar algo falso
        # — que es peor que no declarar nada, porque los agentes planifican con él.
        # Lo cazó la persona el 30-jul dejándole un encargo a agente-web en una carpeta que el
        # perfil decía alcanzable. Se reporta y se resuelve a mano; no se elige solo.
        conflictos = sorted(candidato_allow & set(nuevo_deny))
        for c in conflictos:
            cambios.append(f"  ⚠️  {proy} ({nombre}) CONFLICTO: «{c}» está concedido en el "
                           f"perfil y negado por una regla previa → gana el deny")
        # Lo que el perfil no declara —webs (`read_url`), MCP— lo concedió la persona en la
        # app y se conserva: quitarlo solo traería ventanas de permiso de vuelta.
        ajenos = {x for x in pg.get("allow", [])
                  if not x.startswith(("read_file(", "write_file(", "command("))}
        nuevo_allow = sorted((candidato_allow | ajenos) - set(nuevo_deny))

        if pg.get("deny") != nuevo_deny or pg.get("allow") != nuevo_allow:
            n_d, n_a = len(nuevo_deny) - len(pg.get("deny", [])), len(nuevo_allow) - len(pg.get("allow", []))
            cambios.append(f"  {proy:<12} ({nombre}) permisos: {n_d:+d} deny · {n_a:+d} allow")
            pg["deny"], pg["allow"] = nuevo_deny, nuevo_allow

        quiere = AUTO if r["terminal"] == "automatica" else OFF
        s = d.setdefault("settings", {})
        if con_su_mesa:
            # El preset nativo «Default» de Antigravity, tal cual lo escribe la app:
            # comandos sin preguntar pero dentro del sandbox, y nada fuera de la carpeta.
            quiere = EN_SANDBOX if r["terminal"] == "automatica" else OFF
            for clave, valor in (("sandboxMode", True), ("fileAccessPolicy", NIEGA)):
                if s.get(clave) != valor:
                    cambios.append(f"  {proy:<12} ({nombre}) {clave} → {valor}")
                    s[clave] = valor
            carpeta = Path(mesa["mesa"]).as_uri()
            recursos = d.setdefault("projectResources", {}).setdefault("resources", [])
            fuera = [x for x in recursos
                     if x.get("folderUri", "").rstrip("/") in
                     {Path(v).as_uri() for v in (Path(cfg["repos"]["web"]).parent,)}
                     or any(x.get("folderUri", "").startswith(Path(n).as_uri())
                            for n in mesa.get("nunca_escribe", []))]
            nuevos = [x for x in recursos if x not in fuera]
            if not any(x.get("folderUri") == carpeta for x in nuevos):
                nuevos.insert(0, {"folderUri": carpeta})
            if nuevos != recursos:
                cambios.append(f"  {proy:<12} ({nombre}) carpetas → {mesa['mesa']} "
                               f"(fuera: {', '.join(x['folderUri'] for x in fuera) or '—'})")
                d["projectResources"]["resources"] = nuevos
        if s.get("autoExecutionPolicy") != quiere:
            cambios.append(f"  {proy:<12} ({nombre}) terminal → {r['terminal']}"
                           + (" (en sandbox)" if quiere == EN_SANDBOX else ""))
            s["autoExecutionPolicy"] = quiere

        tocados.append((f, d))

    if not cambios:
        print("✅ Antigravity ya refleja los perfiles. Nada que hacer."); return 0

    print("Antigravity — cambios que se derivan de perfiles-agentes.yaml:\n")
    print("\n".join(cambios))
    print("\nNinguna regla `deny` existente se pierde: el traductor solo suma.")

    if not aplicar:
        print("\n(simulación · para escribirlo: --aplicar, con Antigravity cerrado)")
        return 0

    for f, d in tocados:
        copia(f)
        f.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    anotar("antigravity", cambios)
    print("\n✅ Aplicado. Copias con sufijo .antes-perfiles-<fecha>.json")
    return 0


# ─── adaptador · CLAUDE CODE ─────────────────────────────────────────────────

def adaptar_claude(cfg: dict, aplicar: bool) -> int:
    """Claude no tiene proyectos por agente: la sesión hereda el directorio abierto.
    Así que aquí se escribe el suelo común — lo que NADIE puede hacer, venga el chat
    de donde venga. El enfoque por dominio lo da la carpeta desde la que se abre.
    """
    destino = VAULT / ".claude" / "settings.json"
    d = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    perms = d.setdefault("permissions", {})
    deny_antes = set(perms.get("deny", []))

    suelo = set()
    for x in cfg["niega_todos"]:
        r = ruta_abs(x, cfg)
        suelo.add(f"Read({r}**)" if not r.startswith("**") else f"Read({r})")
    for c in cfg.get("niega_comandos", []):
        suelo.add(f"Bash({c}:*)")

    # Los comandos de solo lectura van al ALLOW: el ritual de arranque es
    # obligatorio en cada chat y sin esto la persona los autorizaba a mano cada vez.
    # Formato Claude: `Bash(git status:*)` — el `:*` cubre con y sin argumentos.
    allow_antes = set(perms.get("allow", []))
    lectura = {f"Bash({c}:*)" for c in cfg.get("comandos_lectura", [])}
    nuevo_allow = sorted(allow_antes | lectura)

    nuevo = sorted(deny_antes | suelo)
    if nuevo == sorted(deny_antes) and nuevo_allow == sorted(allow_antes):
        print("✅ Claude ya tiene el suelo común y la lectura pre-aprobada. Nada que hacer.")
        return 0

    print("Claude Code — cambios en .claude/settings.json (versionado):\n")
    for r in sorted(suelo - deny_antes):
        print(f"  + deny  {r}")
    for r in sorted(lectura - allow_antes):
        print(f"  + allow {r}")
    print("\nEl enfoque por dominio no se declara aquí: en Claude lo da la carpeta")
    print("desde la que abres la sesión. Esto es solo el suelo que nadie pisa.")

    if not aplicar:
        print("\n(simulación · para escribirlo: --aplicar)")
        return 0

    if destino.exists():
        copia(destino)
    perms["deny"] = nuevo
    perms["allow"] = nuevo_allow
    destino.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    anotar("claude", [f"deny += {len(suelo - deny_antes)}",
                      f"allow += {len(lectura - allow_antes)} comandos de lectura"])
    print("\n✅ Aplicado en .claude/settings.json (va a git: esta sí viaja).")
    return 0


# ─── adaptador · CODEX ───────────────────────────────────────────────────────

def adaptar_codex(cfg: dict, aplicar: bool) -> int:
    """Codex está instalado pero sin configurar (`~/.codex/config.toml` vacío).

    NO se escribe su configuración automáticamente: no tengo verificado su esquema
    actual, y un traductor que inventa claves es peor que no tenerlo. Se emite un
    borrador legible al repositorio para contrastarlo con su documentación.
    """
    lineas = [
        "# BORRADOR generado desde exos/perfiles-agentes.yaml",
        "# ⚠️ SIN VERIFICAR contra la documentación de Codex. Contrastar antes de usar.",
        "# El perímetro de cada agente es el mismo de siempre: núcleo (lectura) +",
        "# dominio (escritura) + bandeja común (escritura) + lo negado.",
        "",
        'approval_policy = "on-request"',
        'sandbox_mode = "workspace-write"',
        "",
    ]
    for nombre, a in cfg["agentes"].items():
        if a.get("activo") is False:
            continue
        r = reglas_de(nombre, a, cfg)
        lineas += [
            f"# ── {nombre} · dominio «{a.get('dominio')}» ─────────────────────",
            f"#   repos:    {', '.join(a.get('repos', []))}",
            f"#   escribe:  {', '.join(a.get('escribe', [])) or '—'}",
            f"#   lee más:  {', '.join(a.get('lee_extra', [])) or '—'}",
            f"#   niega:    {', '.join(x.replace(cfg['repos']['vault'] + '/', '') for x in r['niega'])}",
            f"#   terminal: {r['terminal']}",
            "",
        ]

    texto = "\n".join(lineas)
    print(f"Codex — borrador ({len(cfg['agentes'])} perfiles).")
    print("No se escribe su configuración: su esquema no está verificado.\n")
    print("\n".join(lineas[:8]) + "\n  …")

    if not aplicar:
        print(f"\n(simulación · con --aplicar se guarda en {CODEX_BORRADOR.relative_to(VAULT)})")
        return 0

    CODEX_BORRADOR.parent.mkdir(parents=True, exist_ok=True)
    CODEX_BORRADOR.write_text(texto, encoding="utf-8")
    anotar("codex", ["borrador escrito (no aplicado a ~/.codex)"])
    print(f"\n✅ Borrador en {CODEX_BORRADOR.relative_to(VAULT)} — revísalo antes de usarlo.")
    return 0


# ─── entrada ─────────────────────────────────────────────────────────────────

ADAPTADORES = {
    "antigravity": adaptar_antigravity,
    "opencode": adaptar_opencode,
    "claude": adaptar_claude,
    "codex": adaptar_codex,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--herramienta", choices=sorted(ADAPTADORES))
    ap.add_argument("--todas", action="store_true", help="simula las tres, sin escribir")
    ap.add_argument("--verificar", action="store_true",
                    help="¿lo declarado coincide con lo aplicado? No escribe nada")
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()

    cfg = cargar()
    print(f"📋 perfiles-agentes.yaml v{cfg['meta']['version']} "
          f"({cfg['meta']['actualizado']}) · {len(cfg['agentes'])} agentes\n")

    if a.verificar:
        return verificar(cfg)

    if a.todas:
        for n, fn in ADAPTADORES.items():
            print(f"{'─' * 68}\n{n.upper()}\n")
            fn(cfg, False)
            print()
        return 0

    if not a.herramienta:
        ap.print_help()
        return 2
    return ADAPTADORES[a.herramienta](cfg, a.aplicar)


if __name__ == "__main__":
    sys.exit(main())
