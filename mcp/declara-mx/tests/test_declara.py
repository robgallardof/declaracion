import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pytest

from declara_mx import config
from declara_mx.domain import calc, calendario, dyp
from declara_mx.services import acuses, cfdi, espacio

ROOT = Path(__file__).resolve().parents[3]
V = json.loads((ROOT / "datos" / "vigentes-2026.json").read_text(encoding="utf-8"))
RFC_PF = "XAXX010101000"  # RFC genérico: nunca uses uno real en pruebas


# ---------- cálculos (mismos resultados que los scripts originales) ----------
def test_resico_tramos_y_retenciones():
    assert calc.resico(V, 25000)["tasa"] == 0.01 and calc.resico(V, 25000)["isr_a_pagar"] == 250
    out = calc.resico(V, 25175)
    assert out["tasa"] == 0.011 and out["isr_causado"] == 276.93 and out["isr_a_pagar"] == 277
    assert calc.resico(V, 1000, retenciones=50)["isr_a_favor"] == 40
    with pytest.raises(calc.FiscalError, match="último tramo"):
        calc.resico(V, 4_000_000)


def test_iva_aplica_saldo_a_favor_y_genera_nuevo():
    assert calc.iva(trasladado=221, acreditable=334)["saldo_a_favor_nuevo"] == 113
    out = calc.iva(trasladado=500, favor_previo=113)
    assert out["favor_previo_aplicado"] == 113 and out["iva_a_pagar"] == 387 and out["remanente_favor_previo"] == 0
    assert calc.iva(trasladado=50, favor_previo=113)["remanente_favor_previo"] == 63


def test_desglose_iva_incluido():
    out = calc.desglose_iva(V, 1160)
    assert out["base"] == 1000 and out["iva"] == 160


def test_recargos_exige_verificado_e_inpc():
    falso = {**V, "recargos_tasa_mensual": {**V["recargos_tasa_mensual"], "verificado": False}}
    with pytest.raises(calc.FiscalError, match="no está verificado"):
        calc.recargos(falso, 1000, "2026-04", "2026-07")
    with pytest.raises(calc.FiscalError, match="INPC"):
        calc.recargos(V, 1000, "2026-04", "2026-07")
    con_inpc = {**V, "inpc": {"valores": {"2026-03": 140.0, "2026-06": 141.4}}}
    out = calc.recargos(con_inpc, 1000, "2026-04", "2026-07")
    assert out["factor_actualizacion"] == 1.01 and out["meses"] == 3 and out["recargos"] == 62.72


def test_tope_resico_avisa():
    assert calc.tope_resico(V, 2_900_000)["aviso"] == "más del 80% del tope"


# ---------- calendario ----------
@pytest.mark.parametrize("anio,mes,esperado", [(2026, 8, "2026-09-23"), (2026, 9, "2026-10-23"),
                                                (2026, 7, "2026-08-21"), (2026, 5, "2026-06-23")])
def test_vencimiento_por_sexto_digito(anio, mes, esperado):
    rfc = "XXXX970228XX0"  # sexto dígito numérico 8 → 4 días hábiles extra
    assert calendario.vencimiento(anio, mes, rfc)["fecha"] == esperado


def test_vencimiento_confirmado_gana():
    v = calendario.vencimiento(2026, 6, "XXXX970228XX0", {"2026-06": "2026-07-24"})
    assert v["fecha"] == "2026-07-24" and "confirmada" in v["fuente"]


def test_mes_terminado_y_carpeta():
    assert not calendario.mes_terminado(2026, 9, date(2026, 9, 24))
    assert calendario.mes_terminado(2026, 12, date(2027, 1, 1))
    assert calendario.carpeta(2026, 3) == "2026/03-marzo"


def test_url_declaracion_roundtrip():
    d = dyp.decode(dyp.url(2026, 8, complementaria=True))
    assert d["periodo"] == "008" and d["periodoDesc"] == "Agosto" and d["tipoDeclaracion"] == "002"
    assert d["obligaciones"] == ["0168", "0318"] and d["regimen"] == 38


# ---------- archivos ----------
CFDI = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
 Fecha="2026-03-10T10:00:00" TipoDeComprobante="I" SubTotal="1000" Total="1160" Moneda="MXN" MetodoPago="PUE" FormaPago="03">
 <cfdi:Emisor Rfc="{emisor}" Nombre="Emisor"/><cfdi:Receptor Rfc="{receptor}" UsoCFDI="G03" RegimenFiscalReceptor="601"/>
 <cfdi:Impuestos TotalImpuestosTrasladados="160"><cfdi:Traslados><cfdi:Traslado Impuesto="002" Importe="160"/></cfdi:Traslados></cfdi:Impuestos>
 <cfdi:Complemento><tfd:TimbreFiscalDigital UUID="{uuid}"/></cfdi:Complemento>
</cfdi:Comprobante>"""


def test_cfdi_clasifica_y_detecta_duplicados(tmp_path):
    (tmp_path / "a.xml").write_text(CFDI.format(emisor=RFC_PF, receptor="AAA010101AAA", uuid="U1"), encoding="utf-8")
    (tmp_path / "b.xml").write_text(CFDI.format(emisor="AAA010101AAA", receptor=RFC_PF, uuid="U2"), encoding="utf-8")
    (tmp_path / "c.xml").write_text(CFDI.format(emisor=RFC_PF, receptor="AAA010101AAA", uuid="U1"), encoding="utf-8")
    (tmp_path / "roto.xml").write_text("<no", encoding="utf-8")
    out = cfdi.leer(tmp_path, RFC_PF)
    lados = [c["lado"] for c in out["cfdi"]]
    assert lados.count("ingreso") == 2 and lados.count("gasto") == 1 and out["cfdi"][0]["iva"] == 160
    assert any("duplicado" in e["error"] for e in out["errores"]) and any(e["archivo"] == "roto.xml" for e in out["errores"])


ACUSE = """Número de operación: 123456789012 Tipo de declaración: Normal Período de la declaración: Marzo
Fecha y hora de presentación: 21/04/2026 10:00 Vencimiento Obligación: 23/04/2026
ISR simplificado A cargo: 277 Cantidad a pagar: 277 IVA simplificado A cargo: 3,778 Cantidad a pagar: 3,778
Línea de Captura: 0426 ABCD 1234 5678 9012 Importe total a pagar: $4,055 Vigente hasta: 30/04/2026"""


def test_acuses_extrae_campos(tmp_path):
    d = tmp_path / "2026" / "03-marzo" / "acuse"
    d.mkdir(parents=True)
    (d / "acuse_2026-03_normal_1.pdf").write_bytes(b"%PDF")
    filas = acuses.leer(tmp_path, 2026, texto=lambda p: ACUSE)
    f = filas[0]
    assert (f["operacion"], f["periodo"], f["isr_a_pagar"], f["iva_a_cargo"], f["importe_total"]) == \
        ("123456789012", "Marzo", 277, 3778, 4055)
    assert f["linea_captura"] == "0426 ABCD 1234 5678 9012" and "| Marzo |" in acuses.tabla(filas)


def test_estado_mes_y_preparar(tmp_path):
    espacio.crear_mes(tmp_path, 2026, 9)
    assert (tmp_path / "2026" / "09-septiembre" / "comprobantes").is_dir() and (tmp_path / "2026" / "saldos.json").exists()
    e = espacio.estado_mes(tmp_path, 2026, 9, date(2026, 10, 2), "XXXX970228XX0")
    assert e["estado"] == "pendiente" and "en 0" in e["aviso"] and e["vencimiento"] == "2026-10-23"
    assert espacio.estado_mes(tmp_path, 2026, 10, date(2026, 10, 2))["estado"] == "sin_terminar"


def test_perfil_nunca_expone_contrasenas(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "contribuyente.yaml").write_text(
        "rfc: XAXX010101000\nefirma: {carpeta: x, password: secreta, pass_file: y}\n", encoding="utf-8")
    pub = config.perfil(tmp_path).publico()
    assert pub["efirma"] == {"carpeta": "x"} and "secreta" not in json.dumps(pub)
    assert config.perfil(ROOT / "nada").ejemplo


# ---------- privacidad: nada personal en lo que se versiona ----------
RFC_PERSONA = re.compile(r"\b[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}\b")
CURP = re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b")
PERMITIDOS = {"XAXX010101000", "XEXX010101000", "XXXX970228XX0"}  # genéricos y ficticios


def versionados() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
        return [ROOT / f for f in out]
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git no disponible")


def test_ningun_dato_personal_en_archivos_versionados():
    malos = []
    for f in versionados():
        if f.suffix in {".pdf", ".jpg", ".png", ".xml"}:
            malos.append(f"{f.name}: tipo de archivo personal")
            continue
        texto = f.read_text(encoding="utf-8", errors="ignore") if f.exists() else ""
        hallados = (set(RFC_PERSONA.findall(texto)) | set(CURP.findall(texto))) - PERMITIDOS
        if hallados:
            malos.append(f"{f.relative_to(ROOT)}: {sorted(hallados)}")
    assert not malos, malos


def test_lo_privado_esta_ignorado():
    privados = ["config/contribuyente.yaml", "clientes.json", "2026/saldos.json", "2026/03-marzo/calculo.md"]
    out = subprocess.run(["git", "check-ignore", *privados], cwd=ROOT, capture_output=True, text=True)
    assert sorted(out.stdout.split()) == sorted(privados)


def test_skills_y_roles_tienen_frontmatter():
    import yaml
    for p in [*(ROOT / ".agents").glob("skills/*/SKILL.md"), *(ROOT / ".agents").glob("agents/*.md")]:
        m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
        fm = yaml.safe_load(m[1])
        assert fm["name"] == (p.parent.name if p.name == "SKILL.md" else p.stem) and len(fm["description"]) > 60


def test_servidor_mcp_expone_todo():
    import asyncio

    from declara_mx.server import mcp
    tools = {t.name for t in asyncio.run(mcp.list_tools())}
    assert {"contribuyente", "estado_anio", "calcular_resico", "url_declaracion", "leer_acuses"} <= tools
    assert len(asyncio.run(mcp.list_resources())) == 4 and len(asyncio.run(mcp.list_prompts())) == 6
