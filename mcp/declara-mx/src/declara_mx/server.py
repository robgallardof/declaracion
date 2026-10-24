"""Servidor MCP declara-mx (stdio). Herramientas + skills como recursos (skill://) + roles como prompts."""

from __future__ import annotations

import re

from mcp.server.fastmcp import FastMCP

from . import app

mcp = FastMCP("declara-mx")


@mcp.tool()
def contribuyente() -> dict:
    """Perfil del contribuyente (nombre, RFC, regímenes, ruta de la e.firma). Nunca devuelve contraseñas."""
    return app.contribuyente()


@mcp.tool()
def estado_anio(anio: int) -> dict:
    """Estado de los 12 meses: presentada / pendiente / sin terminar, comprobantes, acuses, vencimiento y saldos."""
    return app.estado_anio(anio)


@mcp.tool()
def preparar_mes(anio: int, mes: int) -> dict:
    """Crea AAAA/MM-mes/{comprobantes,facturas,acuse} y el saldos.json del año si falta."""
    return app.preparar_mes(anio, mes)


@mcp.tool()
def leer_cfdi(anio: int, mes: int) -> dict:
    """Lee los CFDI XML del mes y los clasifica en ingreso/gasto respecto al RFC del perfil."""
    return app.leer_cfdi(anio, mes)


@mcp.tool()
def leer_acuses(anio: int, como_tabla: bool = False) -> dict | str:
    """Resume las declaraciones presentadas del año a partir de los PDF de acuse y declaración."""
    return app.leer_acuses(anio, como_tabla)


@mcp.tool()
def vencimiento(anio: int, mes: int) -> dict:
    """Fecha límite del pago mensual (estimada por regla o confirmada en vigentes) y si ya venció."""
    return app.vencimiento(anio, mes)


@mcp.tool()
def calcular_resico(anio: int, ingresos: float, retenciones: float = 0) -> dict:
    """ISR mensual RESICO persona física con la tabla vigente verificada."""
    return app.calcular_resico(anio, ingresos, retenciones)


@mcp.tool()
def calcular_iva(trasladado: float = 0, acreditable: float = 0, retenido: float = 0, favor_previo: float = 0) -> dict:
    """IVA del mes, aplicando primero el saldo a favor de periodos anteriores."""
    return app.calcular_iva(trasladado, acreditable, retenido, favor_previo)


@mcp.tool()
def desglosar_iva(anio: int, deposito: float) -> dict:
    """Separa base e IVA de un depósito que ya incluye IVA (p. ej. pagos por vistas)."""
    return app.desglosar_iva(anio, deposito)


@mcp.tool()
def calcular_recargos(anio: int, monto: float, vence: str, pago: str) -> dict:
    """Actualización por INPC + recargos por mora. vence/pago en formato AAAA-MM."""
    return app.calcular_recargos(anio, monto, vence, pago)


@mcp.tool()
def tope_resico(anio: int, acumulado: float) -> dict:
    """Uso del tope anual de RESICO con los ingresos acumulados del año."""
    return app.tope_resico(anio, acumulado)


@mcp.tool()
def url_declaracion(anio: int, mes: int, complementaria: bool = False) -> dict:
    """URL directa al formulario de la declaración mensual RESICO (normal o complementaria)."""
    return app.url_declaracion(anio, mes, complementaria)


@mcp.tool()
def valores_vigentes(anio: int) -> dict:
    """Qué valores fiscales del año están verificados, con fuente y fecha."""
    return app.valores_vigentes(anio)


def _registrar_skills_y_roles() -> None:
    base = app.root() / ".agents"
    meta = re.compile(r"^---\n(.*?)\n---\n", re.S)

    def descripcion(texto: str) -> str:
        m = meta.match(texto)
        d = re.search(r'description:\s*"?(.*?)"?\s*$', m[1], re.M) if m else None
        return d[1] if d else ""

    def constante(texto: str):
        return lambda: texto

    for skill in sorted(base.glob("skills/*/SKILL.md")):
        texto = skill.read_text(encoding="utf-8")
        mcp.resource(f"skill://{skill.parent.name}", name=skill.parent.name, description=descripcion(texto),
                     mime_type="text/markdown")(constante(texto))
    for rol in sorted(base.glob("agents/*.md")):
        texto = rol.read_text(encoding="utf-8")
        mcp.prompt(name=rol.stem, description=descripcion(texto))(constante(meta.sub("", texto, count=1)))


_registrar_skills_y_roles()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
