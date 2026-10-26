<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/banner-es-dark.svg">
  <img src="assets/readme/banner-es-light.svg" alt="declaracion — Tus impuestos en México, dentro de tu agente de IA" width="100%">
</picture>

<br/>

[![pruebas](https://github.com/robgallardof/declaracion/actions/workflows/tests.yml/badge.svg)](https://github.com/robgallardof/declaracion/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-stdio%20%C2%B7%20HTTP-8A2BE2)
![México](https://img.shields.io/badge/solo-M%C3%A9xico%20🇲🇽-006847)
![privado](https://img.shields.io/badge/tus%20datos-se%20quedan%20en%20tu%20PC-2ea44f)

</div>

<p align="center">
<a href="#-qué-hace"><img src="https://img.shields.io/badge/Qu%C3%A9%20hace-6D28D9?style=for-the-badge" alt="Qué hace" /></a>
<a href="#-tu-información-es-tuya"><img src="https://img.shields.io/badge/Tu%20informaci%C3%B3n%20es%20tuya-5B21B6?style=for-the-badge" alt="Tu información es tuya" /></a>
<a href="#-funciona-con-cualquier-agente"><img src="https://img.shields.io/badge/Funciona%20con%20cualquier%20agente-4F46E5?style=for-the-badge" alt="Funciona con cualquier agente" /></a>
<a href="#-empezar"><img src="https://img.shields.io/badge/Empezar-4338CA?style=for-the-badge" alt="Empezar" /></a>
<a href="#️-herramientas-mcp"><img src="https://img.shields.io/badge/Herramientas%20MCP-2563EB?style=for-the-badge" alt="Herramientas MCP" /></a>
<a href="#-roles-y-skills"><img src="https://img.shields.io/badge/Roles%20y%20skills-0284C7?style=for-the-badge" alt="Roles y skills" /></a>
<a href="#-estructura"><img src="https://img.shields.io/badge/Estructura-0EA5E9?style=for-the-badge" alt="Estructura" /></a>
<a href="#-desarrollo"><img src="https://img.shields.io/badge/Desarrollo-0891B2?style=for-the-badge" alt="Desarrollo" /></a>
</p>

<p align="center"><img src="assets/readme/divider.svg" alt="" width="80%" /></p>

> **Proyecto independiente.** No está afiliado, avalado ni relacionado con ninguna autoridad fiscal ni dependencia de
> gobierno. Informa y calcula; **no es asesoría fiscal**. Las decisiones y el envío final son siempre tuyos.

<a id="-qué-hace"></a>
<p align="center"><img src="assets/readme/sections/es-01.svg" alt="01 · Qué hace" width="100%" /></p>

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

<a id="-tu-información-es-tuya"></a>
<p align="center"><img src="assets/readme/sections/es-02.svg" alt="02 · Tu información es tuya" width="100%" /></p>

- Tus datos (RFC, CURP, e.firma, comprobantes, acuses, montos) viven **solo en tu computadora**.
- El repositorio usa un `.gitignore` de **lista blanca**: los años, `clientes.json` y `config/contribuyente.yaml`
  nunca se suben.
- Una prueba automática **rechaza cualquier RFC o CURP personal** en archivos versionados.
- El agente **nunca** lee ni guarda la contraseña de tu e.firma. El inicio de sesión y la firma los haces tú.

<a id="-funciona-con-cualquier-agente"></a>
<p align="center"><img src="assets/readme/sections/es-03.svg" alt="03 · Funciona con cualquier agente" width="100%" /></p>

Es un **servidor MCP** estándar (`declara-mx`). Además de las herramientas, publica cada skill como recurso MCP
(`skill://…`) y cada rol como prompt, así cualquier cliente recibe el manual completo.

| Cliente | Cómo se conecta |
|---|---|
| Claude Code | `.mcp.json` de la carpeta o, para tu usuario, el instalador (también enlaza skills y agentes en `~/.claude`) |
| Codex | `.codex/config.toml` / `~/.codex/config.toml` |
| Antigravity | `.agents/mcp_config.json` / `~/.gemini/antigravity/mcp_config.json` |
| Cursor · VS Code · Gemini CLI · Windsurf · Claude Desktop | configs generadas o el instalador |

<a id="-empezar"></a>
<p align="center"><img src="assets/readme/sections/es-04.svg" alt="04 · Empezar" width="100%" /></p>

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

### Con Docker (opcional)

Si prefieres no instalar Python ni uv, usa la imagen. Solo lleva el código del MCP: **tus datos nunca entran a la
imagen**, se montan al ejecutarla (la carpeta del repo con tus años, `config/` y `datos/`).

```bash
docker build -t declara-mx:local .
```

**stdio** (lo lanza tu agente; sin puertos ni token). Configúralo en tu cliente MCP así:

```json
{
  "mcpServers": {
    "declara-mx": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "C:/ruta/a/declaracion:/workspace", "declara-mx:local"]
    }
  }
}
```

Usa `-i` y nunca `-t` (la terminal corrompe JSON-RPC). La CLI también va en la imagen:
`docker run --rm -v "C:/ruta/a/declaracion:/workspace" --entrypoint declara declara-mx:local --help`.

**HTTP con token** (Streamable HTTP en `http://127.0.0.1:<puerto>/mcp`, cabecera `Authorization: Bearer <token>`):

```powershell
$env:DECLARA_MCP_TOKEN = python -c "import secrets; print(secrets.token_hex(32))"
$env:DECLARA_PORT = '8765'                       # opcional, 8080 por defecto
docker compose up -d --build --wait
```

| Variable | Por defecto | Para qué |
|---|---|---|
| `DECLARA_MCP_TOKEN` | obligatoria | Token de al menos 32 caracteres para cada petición |
| `DECLARA_PORT` | `8080` | Puerto en tu PC (dentro del contenedor siempre es 8080) |
| `DECLARA_BIND_ADDRESS` | `127.0.0.1` | Interfaz donde se publica; solo tu PC por defecto |
| `DECLARA_WORKSPACE` | `.` | Carpeta que se monta en `/workspace` |
| `DECLARA_USER` | `10001:10001` | UID:GID; en Linux usa `"$(id -u):$(id -g)"` |

Sin Docker, el mismo modo: `uv run declara-mx-mcp --http --listen 127.0.0.1:8765`. `/healthz` responde sin token;
se rechazan navegadores (cabecera `Origin`) y hosts desconocidos. Es un servicio de un solo usuario: no lo publiques
en internet sin un proxy con TLS (`--allow-host tu.dominio` para aceptar ese nombre).

<a id="️-herramientas-mcp"></a>
<p align="center"><img src="assets/readme/sections/es-05.svg" alt="05 · Herramientas MCP" width="100%" /></p>

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

<a id="-roles-y-skills"></a>
<p align="center"><img src="assets/readme/sections/es-06.svg" alt="06 · Roles y skills" width="100%" /></p>

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

<a id="-estructura"></a>
<p align="center"><img src="assets/readme/sections/es-07.svg" alt="07 · Estructura" width="100%" /></p>

```
2026/                      ← privado
  03-marzo/  comprobantes/ facturas/ acuse/ calculo.md resumen.json
  saldos.json  declaraciones_presentadas.md
clientes.json              ← privado
config/contribuyente.yaml  ← privado (copia de contribuyente.example.yaml)
datos/vigentes-2026.json   tasas, UMA, recargos, vencimientos (con fuente oficial)
mcp/declara-mx/            el servidor MCP + CLI
.agents/                   skills y roles portables
scripts/                   bootstrap, sync, install-mcp, test_docker
Dockerfile, compose.yaml   imagen opcional (stdio o HTTP con token)
```

<a id="-desarrollo"></a>
<p align="center"><img src="assets/readme/sections/es-08.svg" alt="08 · Desarrollo" width="100%" /></p>

```bash
cd mcp/declara-mx && uv run pytest      # 27 pruebas: privacidad, cálculos y MCP por HTTP real
python scripts/test_docker.py           # imagen real: stdio, HTTP con token y sin datos personales
python scripts/sync.py                  # tras editar .agents/ o config/
python scripts/install-mcp.py --list    # clientes detectados
```

Capas: `domain/` (reglas puras) → `services/` (archivos) → `app.py` → `server.py` (MCP) y `cli.py`.
Detalles para agentes en [`AGENTS.md`](AGENTS.md).

<div align="center"><sub>Hecho en México 🇲🇽 para que declarar deje de ser un dolor de cabeza.</sub></div>

<br/>

<img src="assets/readme/footer-es.svg" alt="declaracion" width="100%" />
