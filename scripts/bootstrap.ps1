# Instalación en Windows: entorno Python, pruebas, configs de cada agente y MCP para tu usuario.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root "mcp\declara-mx")
try { uv sync --python 3.12; uv run pytest -q } finally { Pop-Location }
$cfg = Join-Path $root "config\contribuyente.yaml"
if (-not (Test-Path $cfg)) { Copy-Item (Join-Path $root "config\contribuyente.example.yaml") $cfg; Write-Host "Creado config\contribuyente.yaml: llénalo con tus datos" }
git -C $root config core.hooksPath .githooks
python (Join-Path $root "scripts\sync.py")
python (Join-Path $root "scripts\install-mcp.py") --with-skills
