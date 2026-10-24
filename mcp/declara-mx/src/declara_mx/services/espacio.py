"""Carpetas AAAA/MM-mes y estado de cada mes (qué hay, qué falta, si ya se presentó)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ..domain import calendario

SUBCARPETAS = ("comprobantes", "facturas", "acuse")


def crear_mes(root: Path, anio: int, mes: int) -> Path:
    base = root / calendario.carpeta(anio, mes)
    for sub in SUBCARPETAS:
        (base / sub).mkdir(parents=True, exist_ok=True)
    year = root / str(anio)
    if not (year / "saldos.json").exists():
        (year / "saldos.json").write_text(json.dumps(
            {"_nota": "Control de IVA a favor por periodo de origen.", "iva_a_favor": []}, indent=2), encoding="utf-8")
    return base


def _archivos(p: Path) -> list[str]:
    return sorted(f.name for f in p.iterdir() if f.is_file()) if p.exists() else []


def estado_mes(root: Path, anio: int, mes: int, hoy: date, rfc: str = "", fechas: dict | None = None) -> dict:
    base = root / calendario.carpeta(anio, mes)
    acuses = [a for a in _archivos(base / "acuse") if a.startswith("acuse_")]
    comprobantes = _archivos(base / "comprobantes")
    estado = ("presentada" if acuses else "sin_terminar" if not calendario.mes_terminado(anio, mes, hoy)
              else "pendiente")
    return {"periodo": f"{anio}-{mes:02d}", "carpeta": calendario.carpeta(anio, mes), "estado": estado,
            "comprobantes": comprobantes, "facturas": _archivos(base / "facturas"), "acuses": acuses,
            "complementarias": sum("complementaria" in a for a in acuses),
            "calculo": (base / "calculo.md").exists(), "resumen": (base / "resumen.json").exists(),
            "vencimiento": calendario.vencimiento(anio, mes, rfc, fechas)["fecha"],
            "aviso": "sin comprobantes: preguntar si se declara en 0" if estado == "pendiente" and not comprobantes else ""}


def saldos(root: Path, anio: int) -> dict:
    p = root / str(anio) / "saldos.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"iva_a_favor": []}
