"""Lee los acuses y las declaraciones completas (PDF) de un año y resume cada declaración.

Busca AAAA/*/acuse/acuse_*.pdf y su par declaracion_*.pdf (nombres de la descarga masiva).
"""

from __future__ import annotations

import re
from pathlib import Path


def texto_pdf(path: Path) -> str:
    import pypdf

    t = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(str(path)).pages)
    return t.replace("ﬁ", "fi").replace("ﬂ", "fl")


def _num(pat: str, t: str) -> int | None:
    m = re.search(pat, t, re.I)
    return int(m.group(1).replace(",", "")) if m else None


def _g(pat: str, t: str) -> str | None:
    m = re.search(pat, t, re.I)
    return m.group(1) if m else None


def acuse(t: str) -> dict:
    isr, iva = (t.split("IVA simplificado", 1) + [""])[:2]
    return {"operacion": _g(r"operaci[oó]n:\s*(\d+)", t), "tipo": _g(r"Tipo de declaraci[oó]n:\s*(\w+)", t),
            "periodo": _g(r"Per[ií]odo de la declaraci[oó]n:\s*(\w+)", t),
            "presentada": _g(r"presentaci[oó]n:\s*([\d/]+ [\d:]+)", t),
            "vencimiento": _g(r"Vencimiento Obligaci[oó]n:\s*([\d/]+)", t),
            "isr_a_cargo": _num(r"A cargo:\s*([\d,]+)", isr), "isr_recargos": _num(r"Recargos:\s*([\d,]+)", isr),
            "isr_a_pagar": _num(r"Cantidad a pagar:\s*([\d,]+)", isr),
            "iva_a_cargo": _num(r"A cargo:\s*([\d,]+)", iva), "iva_a_favor": _num(r"A favor:\s*([\d,]+)", iva),
            "iva_a_pagar": _num(r"Cantidad a pagar:\s*([\d,]+)", iva),
            "linea_captura": (_g(r"Captura:\s*([\d A-Z]{20,30}?)\s*Importe", t) or "").strip() or None,
            "importe_total": _num(r"a pagar:\s*\$([\d,]+)", t), "vigente_hasta": _g(r"Vigente hasta:\s*([\d/]+)", t)}


def declaracion(t: str) -> dict:
    return {"ingresos": _num(r"TOTAL DE INGRESOS PERCIBIDOS POR LA ACTIVIDAD\s*([\d,]+)", t)
            or _num(r"ACTIVIDAD EMPRESARIAL\s*([\d,]+)", t) or 0,
            "tasa": _g(r"TASA APLICABLE\s*([\d.]+%)", t),
            "iva_16_base": _num(r"ACTIVIDADES GRAVADAS A LA TASA DEL 16%\s*([\d,]+)", t),
            "iva_acreditable": _num(r"IVA ACREDITABLE DEL PERIODO\s*([\d,]+)", t),
            "iva_pagado_gastos": _num(r"IVA PAGADO EN GASTOS Y ADQUISICIONES\s*([\d,]+)", t)}


def leer(root: Path, anio: int, texto=texto_pdf) -> list[dict]:
    filas = []
    for f in sorted((root / str(anio)).glob("*/acuse/acuse_*.pdf")):
        a = acuse(texto(f))
        d = f.with_name(f.name.replace("acuse_", "declaracion_", 1))
        if d.exists():
            a.update(declaracion(texto(d)))
        a["archivo"] = f.relative_to(root).as_posix()
        filas.append(a)
    return filas


def tabla(filas: list[dict]) -> str:
    out = ["| Periodo | Tipo | Operación | Presentada | Ingresos | ISR a pagar | IVA a cargo / a favor | Total | "
           "Línea (vigencia) |", "|---|---|---|---|---|---|---|---|---|"]
    for a in filas:
        linea = f"{a['linea_captura']} ({a['vigente_hasta']})" if a["linea_captura"] else "—"
        out.append(f"| {a['periodo']} | {a['tipo']} | {a['operacion']} | {a['presentada']} | {a.get('ingresos', '?')} | "
                   f"{a['isr_a_pagar']} | {a['iva_a_cargo'] or 0} / {a['iva_a_favor'] or 0} | "
                   f"{a['importe_total'] or 0} | {linea} |")
    return "\n".join(out)
