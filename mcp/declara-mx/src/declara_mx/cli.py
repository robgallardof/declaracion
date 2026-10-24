"""CLI: los mismos casos de uso que el MCP, para usarlos sin agente.

  declara estado 2026
  declara resico 2026 45000.50 [--ret 0]
  declara iva [--trasladado 7200] [--acreditable 800] [--retenido 0] [--favor-previo 1500]
  declara desglose 2026 1383.56
  declara recargos 2026 --monto 1000 --vence 2026-04 --pago 2026-07
  declara vencimiento 2026 9
  declara url 2026 8 [--compl]
  declara acuses 2026 [--json]
  declara cfdi 2026 3
  declara mes 2026 11            (crea la carpeta)
"""

from __future__ import annotations

import argparse
import json
import sys

from . import app


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(prog="declara", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("estado"); x.add_argument("anio", type=int)
    x = sub.add_parser("resico"); x.add_argument("anio", type=int); x.add_argument("ingresos", type=float)
    x.add_argument("--ret", type=float, default=0)
    x = sub.add_parser("iva")
    for f in ("trasladado", "acreditable", "retenido", "favor-previo"):
        x.add_argument(f"--{f}", type=float, default=0)
    x = sub.add_parser("desglose"); x.add_argument("anio", type=int); x.add_argument("deposito", type=float)
    x = sub.add_parser("recargos"); x.add_argument("anio", type=int); x.add_argument("--monto", type=float, required=True)
    x.add_argument("--vence", required=True); x.add_argument("--pago", required=True)
    x = sub.add_parser("vencimiento"); x.add_argument("anio", type=int); x.add_argument("mes", type=int)
    x = sub.add_parser("url"); x.add_argument("anio", type=int); x.add_argument("mes", type=int)
    x.add_argument("--compl", action="store_true")
    x = sub.add_parser("acuses"); x.add_argument("anio", type=int); x.add_argument("--json", action="store_true")
    x = sub.add_parser("cfdi"); x.add_argument("anio", type=int); x.add_argument("mes", type=int)
    x = sub.add_parser("mes"); x.add_argument("anio", type=int); x.add_argument("mes", type=int)
    a = p.parse_args(argv)
    run = {
        "estado": lambda: app.estado_anio(a.anio),
        "resico": lambda: app.calcular_resico(a.anio, a.ingresos, a.ret),
        "iva": lambda: app.calcular_iva(a.trasladado, a.acreditable, a.retenido, a.favor_previo),
        "desglose": lambda: app.desglosar_iva(a.anio, a.deposito),
        "recargos": lambda: app.calcular_recargos(a.anio, a.monto, a.vence, a.pago),
        "vencimiento": lambda: app.vencimiento(a.anio, a.mes),
        "url": lambda: app.url_declaracion(a.anio, a.mes, a.compl)["url"],
        "acuses": lambda: app.leer_acuses(a.anio, como_tabla=not a.json),
        "cfdi": lambda: app.leer_cfdi(a.anio, a.mes),
        "mes": lambda: app.preparar_mes(a.anio, a.mes),
    }[a.cmd]
    try:
        out = run()
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(out if isinstance(out, str) else json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
