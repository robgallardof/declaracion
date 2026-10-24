"""Calculadoras fiscales deterministas (México). Puras: reciben los valores vigentes, no los inventan.

Los valores (tasas, tramos, INPC, recargos) vienen de datos/vigentes-AAAA.json; cada bloque debe tener
`verificado: true` o el cálculo se niega (se pide al agente investigador-fiscal que lo verifique).
"""

from __future__ import annotations

import math


class FiscalError(ValueError):
    pass


def r(x: float) -> float:
    return round(x + 1e-9, 2)


def exige(vigentes: dict, nombre: str) -> dict:
    bloque = vigentes.get(nombre) or {}
    if not bloque.get("verificado"):
        raise FiscalError(f"'{nombre}' no está verificado en vigentes-{vigentes.get('ejercicio')}.json: "
                          "lanza investigador-fiscal")
    return bloque


def resico(vigentes: dict, ingresos: float, retenciones: float = 0) -> dict:
    """ISR mensual RESICO PF: ingresos cobrados del mes × tasa del tramo − retenciones."""
    t = exige(vigentes, "resico_pf_tasas_mensuales")
    tasa = next((x["tasa"] for x in t["tramos"] if ingresos <= x["hasta"]), None)
    if tasa is None:
        raise FiscalError("Los ingresos exceden el último tramo de RESICO")
    isr = r(ingresos * tasa)
    return {"ingresos": ingresos, "tasa": tasa, "isr_causado": isr, "retenciones": retenciones,
            "isr_a_pagar": max(0, round(isr - retenciones)), "isr_a_favor": max(0, r(retenciones - isr))}


def iva(trasladado: float = 0, acreditable: float = 0, retenido: float = 0, favor_previo: float = 0) -> dict:
    """IVA mensual: trasladado − acreditable − retenido; si queda a cargo, se acredita el saldo a favor previo."""
    neto = r(trasladado - acreditable - retenido)
    if neto < 0:
        return {"iva_mes": neto, "saldo_a_favor_nuevo": -neto, "favor_previo_aplicado": 0,
                "remanente_favor_previo": r(favor_previo), "iva_a_pagar": 0}
    aplica = min(neto, favor_previo)
    return {"iva_mes": neto, "saldo_a_favor_nuevo": 0, "favor_previo_aplicado": r(aplica),
            "remanente_favor_previo": r(favor_previo - aplica), "iva_a_pagar": round(neto - aplica)}


def desglose_iva(vigentes: dict, deposito: float) -> dict:
    """Depósito que YA incluye IVA (p. ej. pagos por vistas de plataformas): base = depósito / (1 + tasa)."""
    tasa = exige(vigentes, "iva")["general"]
    base = r(deposito / (1 + tasa))
    return {"deposito": deposito, "tasa": tasa, "base": base, "iva": r(deposito - base)}


def _mes_anterior(y: int, m: int) -> str:
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def recargos(vigentes: dict, monto: float, vence: str, pago: str) -> dict:
    """Actualización (INPC) + recargos por mora. vence/pago = 'AAAA-MM'."""
    tasa = exige(vigentes, "recargos_tasa_mensual")["valor"]
    inpc = (vigentes.get("inpc") or {}).get("valores") or {}
    y1, m1 = map(int, vence.split("-"))
    y2, m2 = map(int, pago.split("-"))
    k_pago, k_venc = _mes_anterior(y2, m2), _mes_anterior(y1, m1)
    if k_pago not in inpc or k_venc not in inpc:
        raise FiscalError(f"Faltan INPC {k_venc} y/o {k_pago} en vigentes: lanza investigador-fiscal")
    factor = max(1.0, math.floor(inpc[k_pago] / inpc[k_venc] * 10000) / 10000)
    act = r(monto * factor)
    meses = max(0, (y2 - y1) * 12 + (m2 - m1))
    rec = r(act * tasa * meses)
    return {"factor_actualizacion": factor, "monto_actualizado": act, "meses": meses,
            "tasa_recargos": tasa, "recargos": rec, "total": round(act + rec)}


def tope_resico(vigentes: dict, acumulado: float) -> dict:
    t = exige(vigentes, "resico_pf_tasas_mensuales")
    tope = t["tope_anual"]
    uso = acumulado / tope if tope else 0
    return {"acumulado": acumulado, "tope_anual": tope, "uso": round(uso, 4),
            "aviso": "rebasa el tope: sale del régimen" if uso > 1 else "más del 80% del tope" if uso >= 0.8 else ""}
