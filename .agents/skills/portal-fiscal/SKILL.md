---
name: portal-fiscal
description: "Operar los portales fiscales con e.firma desde el navegador (login del usuario, Declaraciones y Pagos, constancia de situación fiscal, descarga de CFDI, opinión de cumplimiento) con Claude in Chrome, chrome-devtools o Playwright. Usar cuando haya que entrar al portal para declarar, facturar o descargar documentos."
---

# Portal fiscal con e.firma

Navegador: **Claude in Chrome** (carga su skill y abre una pestaña nueva). Si falla, **chrome-devtools**
(`new_page`, `take_snapshot`, `fill`, `click`, `upload_file`) y como último recurso Playwright. Carga las herramientas
en una sola llamada a ToolSearch. Evita los diálogos `alert`/`confirm` (bloquean). Captura antes de cada paso irreversible.

URLs principales:
- **Declaración mensual RESICO → portal nuevo: https://pstcdypisr.clouda.sat.gob.mx/** (runbook: `dyp-resico.md`;
  URL directa: herramienta `url_declaracion`).
- No uses `ptscdecprov.clouda.sat.gob.mx` (portal viejo) para RESICO.
- Consulta de declaraciones: https://pstcdypisr.clouda.sat.gob.mx/Consulta/Consulta?tipoDocumento=4
- Factura electrónica (otro login): https://portal.facturaelectronica.sat.gob.mx/
- Consulta y cancelación de CFDI (otro login): https://portalcfdi.facturaelectronica.sat.gob.mx/

## Login (lo hace el USUARIO)
El agente no escribe contraseñas, no sube la e.firma para autenticarse ni resuelve captchas.
1. Abre la URL del trámite en una pestaña nueva.
2. Pide al usuario que inicie sesión con su e.firma (.cer + .key + contraseña) y que avise con "listo".
3. Con la sesión abierta, sigue tú. Si expira, pide que vuelva a entrar.
4. Si hay que firmar para enviar o sellar, el usuario captura esa parte.

## Declaración provisional mensual
**Lee `dyp-resico.md` antes de empezar** (URLs, campos obligatorios ocultos en modales, selectores, tiempos, descarga
del acuse). Resumen: sesión → `url_declaracion` → leer el modal de precarga → ISR (Ingresos, Determinación, Pago) →
IVA (Determinación, IVA acreditable, Pago) → Administración → screenshot → **OK del usuario** → Enviar → SI → acuse →
descarga masiva (acuse + declaración) a `MM-mes/acuse/`.

## Otros
- Constancia de Situación Fiscal → `AAAA/constancia.pdf`; si cambió el régimen, actualiza `config/contribuyente.yaml`.
- Descarga masiva de CFDI (emitidos/recibidos) por mes → XML a la carpeta del mes.
- Opinión de cumplimiento (32-D) → `AAAA/`.

Nunca aceptes diálogos de pago, cambies datos del contribuyente ni envíes nada sin un OK explícito.
