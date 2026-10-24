"""Lectura de CFDI 4.0 (XML). Clasifica cada comprobante como ingreso o gasto respecto al RFC del perfil."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

TIPOS = {"I": "ingreso", "E": "egreso", "P": "pago", "N": "nomina", "T": "traslado"}


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _find(root, name: str) -> list:
    return [e for e in root.iter() if _local(e.tag) == name]


def parse(path: Path, rfc: str) -> dict:
    root = ET.parse(path).getroot()
    a = root.attrib
    emisor, receptor = _find(root, "Emisor")[0].attrib, _find(root, "Receptor")[0].attrib
    tfd = _find(root, "TimbreFiscalDigital")
    imp = next((e for e in root if _local(e.tag) == "Impuestos"), None)  # solo los del comprobante
    iva = ret_isr = ret_iva = 0.0
    if imp is not None:
        for t in _find(imp, "Traslado"):
            if t.get("Impuesto") == "002":
                iva += float(t.get("Importe", 0))
        for x in _find(imp, "Retencion"):
            if x.get("Impuesto") == "001":
                ret_isr += float(x.get("Importe", 0))
            elif x.get("Impuesto") == "002":
                ret_iva += float(x.get("Importe", 0))
    rfc = (rfc or "").upper()
    lado = "ingreso" if emisor.get("Rfc") == rfc else "gasto" if receptor.get("Rfc") == rfc else "ajeno"
    return {"archivo": path.name, "uuid": tfd[0].get("UUID") if tfd else None, "fecha": a.get("Fecha"),
            "tipo": TIPOS.get(a.get("TipoDeComprobante"), a.get("TipoDeComprobante")), "lado": lado,
            "emisor": emisor.get("Rfc"), "emisor_nombre": emisor.get("Nombre"),
            "receptor": receptor.get("Rfc"), "regimen_receptor": receptor.get("RegimenFiscalReceptor"),
            "uso_cfdi": receptor.get("UsoCFDI"), "metodo_pago": a.get("MetodoPago"),
            "forma_pago": a.get("FormaPago"), "moneda": a.get("Moneda"),
            "tipo_cambio": float(a.get("TipoCambio", 1)), "subtotal": float(a.get("SubTotal", 0)),
            "descuento": float(a.get("Descuento", 0)), "iva": round(iva, 2), "ret_isr": round(ret_isr, 2),
            "ret_iva": round(ret_iva, 2), "total": float(a.get("Total", 0))}


def leer(carpeta: Path, rfc: str) -> dict:
    out, errores, vistos = [], [], {}
    for p in sorted(Path(carpeta).rglob("*.xml")):
        try:
            c = parse(p, rfc)
        except Exception as e:  # noqa: BLE001 - un XML roto no debe tumbar la lectura del mes
            errores.append({"archivo": p.name, "error": str(e)})
            continue
        if c["uuid"] and c["uuid"] in vistos:
            errores.append({"archivo": p.name, "error": f"UUID duplicado con {vistos[c['uuid']]}"})
        vistos[c["uuid"]] = p.name
        out.append(c)
    totales = {lado: round(sum(c["subtotal"] - c["descuento"] for c in out if c["lado"] == lado), 2)
               for lado in ("ingreso", "gasto")}
    return {"cfdi": out, "errores": errores, "totales_subtotal": totales}
