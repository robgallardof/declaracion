# syntax=docker/dockerfile:1
# Imagen del MCP declara-mx. Solo contiene el código del servidor: tus datos (años,
# comprobantes, config/contribuyente.yaml, clientes.json) NUNCA entran a la imagen;
# se montan en /workspace al ejecutar. Ver la sección Docker del README.
FROM python:3.12-slim-bookworm AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY mcp/declara-mx/pyproject.toml mcp/declara-mx/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-install-project
COPY mcp/declara-mx/src ./src
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-editable

FROM python:3.12-slim-bookworm
RUN groupadd --gid 10001 declara && useradd --uid 10001 --gid declara --create-home declara \
    && mkdir /workspace && chown declara:declara /workspace
COPY --from=build /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH DECLARA_ROOT=/workspace PYTHONUNBUFFERED=1 PYTHONUTF8=1
USER declara
WORKDIR /workspace
EXPOSE 8080
HEALTHCHECK NONE
ENTRYPOINT ["declara-mx-mcp"]
CMD ["--stdio"]
