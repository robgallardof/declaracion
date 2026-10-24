"""Espacio de trabajo y perfil del contribuyente.

El perfil vive en config/contribuyente.yaml, que es PRIVADO (git lo ignora). Si no existe se usa
config/contribuyente.example.yaml, que no trae datos reales.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("DECLARA_ROOT") or Path(__file__).resolve().parents[4])
PRIVADOS = ("password", "pass", "contrasena", "contraseña")


@dataclass
class Perfil:
    root: Path
    nombre: str = ""
    rfc: str = ""
    curp: str = ""
    regimenes: list[dict] = field(default_factory=list)
    efirma: dict = field(default_factory=dict)
    notas: list[str] = field(default_factory=list)
    ejemplo: bool = False

    def publico(self) -> dict:
        """Lo que se puede mostrar al agente: nunca contraseñas ni contenido de la e.firma."""
        efirma = {k: v for k, v in self.efirma.items() if not any(p in k.lower() for p in PRIVADOS)}
        return {"nombre": self.nombre, "rfc": self.rfc, "curp": self.curp, "regimenes": self.regimenes,
                "efirma": efirma, "notas": self.notas,
                "aviso": "PERFIL DE EJEMPLO: pide los datos al usuario y guárdalos en config/contribuyente.yaml"
                if self.ejemplo else ""}


def perfil(root: Path | None = None) -> Perfil:
    root = Path(root or ROOT)
    path = root / "config" / "contribuyente.yaml"
    ejemplo = not path.exists()
    if ejemplo:
        path = root / "config" / "contribuyente.example.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    known = {k: v for k, v in (data or {}).items() if k in Perfil.__dataclass_fields__}
    return Perfil(root=root, ejemplo=ejemplo, **known)


def vigentes(anio: int, root: Path | None = None) -> dict:
    path = Path(root or ROOT) / "datos" / f"vigentes-{anio}.json"
    if not path.exists():
        raise FileNotFoundError(f"No existe datos/vigentes-{anio}.json: lanza investigador-fiscal para crearlo")
    return json.loads(path.read_text(encoding="utf-8"))
