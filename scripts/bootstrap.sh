#!/bin/sh
# Instalación en macOS / Linux.
set -e
root="$(cd "$(dirname "$0")/.." && pwd)"
(cd "$root/mcp/declara-mx" && uv sync --python 3.12 && uv run pytest -q)
[ -f "$root/config/contribuyente.yaml" ] || cp "$root/config/contribuyente.example.yaml" "$root/config/contribuyente.yaml"
git -C "$root" config core.hooksPath .githooks
python3 "$root/scripts/sync.py"
python3 "$root/scripts/install-mcp.py" --with-skills
