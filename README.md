<div align="center">

# 🧾 declaracion

**Tu asistente de impuestos personales en México, dentro de tu agente de IA.**<br>
Ordena tu contabilidad por mes, lee tus facturas y comprobantes, calcula ISR e IVA,<br>
te avisa de vencimientos y te acompaña paso a paso al presentar tu declaración.

[![pruebas](https://github.com/robgallardof/declaracion/actions/workflows/tests.yml/badge.svg)](https://github.com/robgallardof/declaracion/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-stdio-8A2BE2)
![México](https://img.shields.io/badge/solo-M%C3%A9xico%20🇲🇽-006847)
![privado](https://img.shields.io/badge/tus%20datos-se%20quedan%20en%20tu%20PC-2ea44f)

</div>

---

> **Proyecto independiente.** No está afiliado, avalado ni relacionado con ninguna autoridad fiscal ni dependencia de
> gobierno. Informa y calcula; **no es asesoría fiscal**. Las decisiones y el envío final son siempre tuyos.

## ✨ Qué hace

| | |
|---|---|
| 📁 **Un orden que no falla** | Una carpeta por mes (`2026/03-marzo/`) con `comprobantes/`, `facturas/` y `acuse/`. Si hay acuse, el mes ya está hecho. |
| 🔍 **Lee tus papeles** | CFDI 4.0 (XML) clasificados en ingresos y gastos, transferencias SPEI, PDFs e imágenes. Detecta duplicados. |
| 🧮 **Cálculos exactos** | ISR mensual RESICO, IVA con saldo a favor por mes de origen, desglose de IVA incluido, actualización y recargos. Nunca "de memoria": solo con valores oficiales verificados y con fuente. |
| 📅 **Fechas límite** | Calcula tu vencimiento (día 17 + días extra según tu RFC, días inhábiles) y te avisa si se te pasó. |
| 📑 **Tu historial al día** | Lee tus acuses en PDF y arma la tabla de lo presentado: montos, líneas de captura y vigencias. |
| 🧭 **Te acompaña en el portal** | Un manual paso a paso, probado en el portal oficial, con los campos escondidos y los errores conocidos. Tú inicias sesión y firmas; el agente llena y te pide OK antes de enviar. |
| 🧾 **Facturación** | Arma el CFDI de ingreso, lo revisa contra las reglas 4.0 y lo guarda con nombre claro. |
| 📆 **Anual** | Junta el año (sueldos + RESICO, deducciones personales, retenciones) para la declaración de abril. |

## 🔒 Tu información es tuya

- Tus datos (RFC, CURP, e.firma, comprobantes, acuses, montos) viven **solo en tu computadora**.
- El repositorio usa un `.gitignore` de **lista blanca**: los años, `clientes.json` y `config/contribuyente.yaml`
  nunca se suben.
- Una prueba automática **rechaza cualquier RFC o CURP personal** en archivos versionados.
- El agente **nunca** lee ni guarda la contraseña de tu e.firma. El inicio de sesión y la firma los haces tú.

## 🧩 Funciona con cualquier agente

Es un **servidor MCP** estándar (`declara-mx`). Además de las herramientas, publica cada skill como recurso MCP
(`skill://…`) y cada rol como prompt, así cualquier cliente recibe el manual completo.

| Cliente | Cómo se conecta |
|---|---|
| Claude Code | `.mcp.json` de la carpeta o, para tu usuario, el instalador (también enlaza skills y agentes en `~/.claude`) |
| Codex | `.codex/config.toml` / `~/.codex/config.toml` |
| Antigravity | `.agents/mcp_config.json` / `~/.gemini/antigravity/mcp_config.json` |
| Cursor · VS Code · Gemini CLI · Windsurf · Claude Desktop | configs generadas o el instalador |

## 🚀 Empezar

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12 (uv lo instala).

```powershell
git clone https://github.com/robgallardof/declaracion.git
cd declaracion
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap.ps1   # Windows
# sh scripts/bootstrap.sh                                                    # macOS / Linux
```

El bootstrap instala el entorno, corre las pruebas, crea `config/contribuyente.yaml` (llénalo con tus datos),
genera las configs de cada agente y registra el MCP para tu usuario.

Luego, háblale a tu agente:

> *"¿Qué meses me faltan de 2026?"* · *"Declara septiembre"* · *"Declara agosto en 0"* · *"¿Cuánto IVA lleva este depósito?"* ·
> *"Ya se venció mi línea de captura de mayo"* · *"Factura a mi cliente lo de octubre"* · *"Prepara mi anual"*

## 🛠️ Herramientas MCP

| Herramienta | Qué hace |
|---|---|
| `contribuyente` | Tu perfil (régimen, RFC, ruta de la e.firma), sin contraseñas |
| `estado_anio` | Los 12 meses: presentado / pendiente / sin terminar, comprobantes, vencimiento, saldos a favor |
| `preparar_mes` | Crea la carpeta del mes |
| `leer_cfdi` | Lee y clasifica los XML del mes |
| `leer_acuses` | Resume lo presentado a partir de tus acuses PDF |
| `vencimiento` | Fecha límite estimada y si ya venció |
| `calcular_resico` · `calcular_iva` · `desglosar_iva` | ISR, IVA y desglose de IVA incluido |
| `calcular_recargos` · `tope_resico` | Pago tardío y tope anual |
| `url_declaracion` | Liga directa al formulario mensual (normal o complementaria) |
| `valores_vigentes` | Qué valores oficiales del año están verificados y con qué fuente |

Sin agente: `cd mcp/declara-mx && uv run declara --help` (por ejemplo `uv run declara estado 2026`).

## 👥 Roles y skills

**Roles:** `extractor-comprobantes` → `validador-cfdi` → `contador-mx` → `auditor-fiscal` para cada mes;
`preparador-anual` en abril; `investigador-fiscal` mantiene los valores oficiales al día (DOF, INEGI, Banxico).

**Skills:** `declaracion-mensual` · `facturacion` · `fiscal-mx` (conceptos: regímenes, ISR, IVA, saldos, recargos,
CFDI 4.0) · `portal-fiscal` (manual del portal con e.firma).

### Reglas que el agente no se salta
1. Sin comprobantes, pregunta antes de declarar en 0.
2. No presenta un mes que no ha terminado.
3. Antes de enviar una declaración o sellar una factura, te muestra el resumen y espera tu **OK**.
4. No inventa montos ni hace cuentas a mano.
5. Siempre te entrega la línea de captura (número, importe y vigencia). El pago lo haces tú.

## 📁 Estructura

```
2026/                      ← privado
  03-marzo/  comprobantes/ facturas/ acuse/ calculo.md resumen.json
  saldos.json  declaraciones_presentadas.md
clientes.json              ← privado
config/contribuyente.yaml  ← privado (copia de contribuyente.example.yaml)
datos/vigentes-2026.json   tasas, UMA, recargos, vencimientos (con fuente oficial)
mcp/declara-mx/            el servidor MCP + CLI
.agents/                   skills y roles portables
scripts/                   bootstrap, sync, install-mcp
```

## 🧪 Desarrollo

```bash
cd mcp/declara-mx && uv run pytest      # 20 pruebas, incluida la de privacidad
python scripts/sync.py                  # tras editar .agents/ o config/
python scripts/install-mcp.py --list    # clientes detectados
```

Capas: `domain/` (reglas puras) → `services/` (archivos) → `app.py` → `server.py` (MCP) y `cli.py`.
Detalles para agentes en [`AGENTS.md`](AGENTS.md).

<div align="center"><sub>Hecho en México 🇲🇽 para que declarar deje de ser un dolor de cabeza.</sub></div>
