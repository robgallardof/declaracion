# declaracion — instrucciones para cualquier agente

Asistente de impuestos personales en **México**: organiza la contabilidad por mes, lee CFDI y comprobantes, calcula
ISR/IVA (RESICO PF y otros), recargos y vencimientos, resume las declaraciones presentadas y guía el llenado del
portal de declaraciones con el usuario. Funciona con cualquier agente que lea `AGENTS.md`, skills (`SKILL.md`) y MCP:
Claude Code, Codex, Antigravity, Cursor, Gemini CLI, VS Code. Responde siempre en el idioma del usuario.

**Perfil del contribuyente:** `config/contribuyente.yaml` (PRIVADO, git lo ignora) → herramienta `contribuyente`.
Si solo existe el ejemplo, pide los datos al usuario y crea el archivo. Nunca leas, muestres ni guardes la contraseña
de la e.firma.

## Qué hay aquí

| Ruta | Qué es | ¿En git? |
|---|---|---|
| `mcp/declara-mx/` | Servidor MCP + CLI (Python 3.12 + uv) | sí |
| `.agents/skills/`, `.agents/agents/` | Skills y roles portables | sí |
| `datos/vigentes-AAAA.json` | Valores fiscales oficiales con fuente y fecha | sí (sin datos personales) |
| `config/mcp.servers.json` | Fuente única de servidores MCP → `python scripts/sync.py` | sí |
| `config/contribuyente.yaml` | RFC, CURP, regímenes, ruta de la e.firma | **no** |
| `AAAA/MM-mes/` | `comprobantes/`, `facturas/`, `acuse/`, `calculo.md`, `resumen.json` | **no** |
| `AAAA/saldos.json`, `AAAA/declaraciones_presentadas.md` | IVA a favor por origen; historial | **no** |
| `clientes.json` | Pagadores conocidos y decisiones del usuario | **no** |

`.gitignore` es una lista blanca: lo personal nunca se versiona. No uses `git add -f` sobre datos del usuario.

## Cómo trabajar

1. Roles (si tu agente no tiene subagentes, lee el archivo y síguelo tú):
   `extractor-comprobantes` → `validador-cfdi` → `contador-mx` → `auditor-fiscal` (declaración mensual);
   `preparador-anual` (abril); `investigador-fiscal` (valores vigentes).
2. Skills: `declaracion-mensual`, `facturacion`, `fiscal-mx`, `portal-fiscal` (runbook del portal en `dyp-resico.md`).
3. Herramientas MCP (`declara-mx`): `contribuyente`, `estado_anio`, `preparar_mes`, `leer_cfdi`, `leer_acuses`,
   `vencimiento`, `calcular_resico`, `calcular_iva`, `desglosar_iva`, `calcular_recargos`, `tope_resico`,
   `url_declaracion`, `valores_vigentes`. Sin MCP: `cd mcp/declara-mx && uv run declara --help`.

## Reglas duras
1. "Declara/factura <mes>" sin comprobantes → pregunta **"No hay comprobantes de <mes>. ¿Seguro que quieres declarar
   en 0?"** y espera un sí.
2. No presentes un mes que no ha terminado.
3. Antes de **Enviar** una declaración o **Sellar** una factura: resumen y OK explícito (son irreversibles).
4. No inventes montos ni hagas aritmética fiscal a mano: usa las herramientas. Si algo es ilegible, pregunta.
5. Vencimiento: `vencimiento` estima; **manda la fecha del formulario oficial**. Avisa si ya pasó.
6. Entrega siempre la **línea de captura** (número, importe y vigencia). El pago lo hace el usuario.
7. El login y la firma los hace el usuario; el agente navega y llena (skill `portal-fiscal`).
8. Esto informa y calcula; no es asesoría fiscal. Montos altos o temas dudosos → recomienda un contador.

## Desarrollo
- Capas: `domain/` (puro: `calc`, `calendario`, `dyp`) → `services/` (`cfdi`, `acuses`, `espacio`) → `app.py` →
  `server.py` (MCP) y `cli.py`.
- Pruebas: `cd mcp/declara-mx && uv run pytest` (incluye una prueba que rechaza RFC/CURP personales en archivos versionados).
- Tras editar `.agents/` o `config/`: `python scripts/sync.py`. Instalar para tu usuario en todos los clientes:
  `python scripts/install-mcp.py --with-skills`.
- Docker (opcional): `Dockerfile` + `compose.yaml` (stdio o HTTP con `DECLARA_MCP_TOKEN`); la imagen nunca lleva
  datos personales (`.dockerignore` en lista blanca). Prueba real: `python scripts/test_docker.py`.
- Commits: `git config core.hooksPath .githooks` (el hook quita coautores de IA).
