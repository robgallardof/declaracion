"""Meses, carpetas y fechas de vencimiento de los pagos mensuales. Puro.

Vencimiento: día 17 del mes siguiente (si es inhábil, el siguiente hábil) y, para personas físicas, los días
hábiles adicionales según el sexto dígito numérico del RFC (Decreto de beneficios fiscales, art. 5.1).
Es una ESTIMACIÓN: manda la fecha que muestra el formulario oficial. Si `vigentes.vencimientos_mensuales.fechas`
trae la fecha del periodo, esa gana.
"""

from __future__ import annotations

from datetime import date, timedelta

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_EXTRA = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 0: 5}


def carpeta(anio: int, mes: int) -> str:
    """'2026/03-marzo'"""
    return f"{anio}/{mes:02d}-{MESES[mes - 1]}"


def nombre_mes(mes: int) -> str:
    return MESES[mes - 1].capitalize()


def _n_lunes(anio: int, mes: int, n: int) -> date:
    d = date(anio, mes, 1)
    d += timedelta(days=(7 - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def inhabiles(anio: int) -> set[date]:
    """Descanso obligatorio (LFT art. 74). Los periodos vacacionales de la autoridad no se modelan."""
    return {date(anio, 1, 1), _n_lunes(anio, 2, 1), _n_lunes(anio, 3, 3), date(anio, 5, 1),
            date(anio, 9, 16), _n_lunes(anio, 11, 3), date(anio, 12, 25)}


def habil(d: date) -> bool:
    return d.weekday() < 5 and d not in inhabiles(d.year)


def siguiente_habil(d: date) -> date:
    while not habil(d):
        d += timedelta(days=1)
    return d


def sexto_digito(rfc: str) -> int | None:
    digitos = [c for c in rfc if c.isdigit()]
    return int(digitos[5]) if len(digitos) >= 6 else None


def vencimiento(anio: int, mes: int, rfc: str | None = None, fechas: dict | None = None) -> dict:
    clave = f"{anio}-{mes:02d}"
    if fechas and clave in fechas:
        return {"periodo": clave, "fecha": fechas[clave], "fuente": "vigentes (confirmada)"}
    y, m = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    d = siguiente_habil(date(y, m, 17))
    extra = DIAS_EXTRA.get(sexto_digito(rfc)) if rfc and len(rfc) == 13 else 0
    for _ in range(extra or 0):
        d = siguiente_habil(d + timedelta(days=1))
    return {"periodo": clave, "fecha": d.isoformat(), "dias_extra": extra or 0,
            "fuente": "estimada: manda la fecha del formulario oficial"}


def mes_terminado(anio: int, mes: int, hoy: date) -> bool:
    y, m = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    return hoy >= date(y, m, 1)
