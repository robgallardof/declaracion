"""Casos de uso compartidos por el servidor MCP y la CLI."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import config
from .domain import calc, calendario, dyp
from .services import acuses, cfdi, espacio


def root() -> Path:
    return config.ROOT


def hoy() -> date:
    return date.today()


def _fechas(anio: int) -> dict:
    try:
        return (config.vigentes(anio).get("vencimientos_mensuales") or {}).get("fechas") or {}
    except FileNotFoundError:
        return {}


def contribuyente() -> dict:
    return config.perfil().publico()


def estado_anio(anio: int) -> dict:
    rfc = config.perfil().rfc
    meses = [espacio.estado_mes(root(), anio, m, hoy(), rfc, _fechas(anio)) for m in range(1, 13)]
    return {"anio": anio, "hoy": hoy().isoformat(), "meses": meses,
            "pendientes": [m["periodo"] for m in meses if m["estado"] == "pendiente"],
            "saldos_iva": espacio.saldos(root(), anio).get("iva_a_favor", [])}


def preparar_mes(anio: int, mes: int) -> dict:
    base = espacio.crear_mes(root(), anio, mes)
    return {"carpeta": base.relative_to(root()).as_posix(), "subcarpetas": list(espacio.SUBCARPETAS),
            "terminado": calendario.mes_terminado(anio, mes, hoy())}


def leer_cfdi(anio: int, mes: int) -> dict:
    return cfdi.leer(root() / calendario.carpeta(anio, mes), config.perfil().rfc)


def leer_acuses(anio: int, como_tabla: bool = False) -> dict | str:
    filas = acuses.leer(root(), anio)
    return acuses.tabla(filas) if como_tabla else {"anio": anio, "declaraciones": filas}


def vencimiento(anio: int, mes: int) -> dict:
    v = calendario.vencimiento(anio, mes, config.perfil().rfc, _fechas(anio))
    v["vencida"] = hoy().isoformat() > v["fecha"]
    v["mes_terminado"] = calendario.mes_terminado(anio, mes, hoy())
    return v


def calcular_resico(anio: int, ingresos: float, retenciones: float = 0) -> dict:
    return calc.resico(config.vigentes(anio), ingresos, retenciones)


def calcular_iva(trasladado: float = 0, acreditable: float = 0, retenido: float = 0, favor_previo: float = 0) -> dict:
    return calc.iva(trasladado, acreditable, retenido, favor_previo)


def desglosar_iva(anio: int, deposito: float) -> dict:
    return calc.desglose_iva(config.vigentes(anio), deposito)


def calcular_recargos(anio: int, monto: float, vence: str, pago: str) -> dict:
    return calc.recargos(config.vigentes(anio), monto, vence, pago)


def tope_resico(anio: int, acumulado: float) -> dict:
    return calc.tope_resico(config.vigentes(anio), acumulado)


def url_declaracion(anio: int, mes: int, complementaria: bool = False) -> dict:
    return {"url": dyp.url(anio, mes, complementaria), "datos": dyp.datos(anio, mes, complementaria),
            "nota": "Requiere sesión abierta con e.firma; si la rechaza, entra por /Declaracion/Temporales."}


def valores_vigentes(anio: int) -> dict:
    v = config.vigentes(anio)
    return {k: {"verificado": b.get("verificado"), "verificado_el": b.get("verificado_el"), "fuente": b.get("fuente")}
            for k, b in v.items() if isinstance(b, dict) and "verificado" in b}
