"""URL directa al formulario de la declaración mensual RESICO PF en el portal de Declaraciones y Pagos."""

from __future__ import annotations

import base64
import json

from .calendario import nombre_mes

PORTAL = "https://pstcdypisr.clouda.sat.gob.mx"
# 38 = RESICO PF en este portal; 0168 ISR simplificado de confianza PF; 0318 IVA simplificado de confianza
REGIMEN_RESICO = 38
OBLIGACIONES = ["0168", "0318"]


def datos(anio: int, mes: int, complementaria: bool = False) -> dict:
    return {"tipopersona": "A", "regimen": REGIMEN_RESICO, "ejercicio": str(anio), "periodicidad": "M",
            "periodo": f"{mes:03d}", "periodoDesc": nombre_mes(mes), "fechaCausacion": "",
            "tipoDeclaracion": "002" if complementaria else "001",
            "tipoDeclaracionDesc": "Complementaria" if complementaria else "Normal",
            "tipoComplementaria": "", "tipoComplementariaDesc": "", "obligaciones": OBLIGACIONES}


def url(anio: int, mes: int, complementaria: bool = False) -> str:
    raw = json.dumps(datos(anio, mes, complementaria), separators=(",", ":"), ensure_ascii=False)
    return f"{PORTAL}/Formulario/Formulario?data={base64.b64encode(raw.encode()).decode()}"


def decode(link: str) -> dict:
    return json.loads(base64.b64decode(link.split("data=", 1)[1]))
