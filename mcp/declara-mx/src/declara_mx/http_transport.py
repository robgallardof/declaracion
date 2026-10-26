"""Transporte MCP opcional por Streamable HTTP, protegido con un token compartido.

stdio sigue siendo el modo normal (lo lanza el cliente MCP). HTTP existe para Docker
o para servir el MCP de forma explícita en una red, y solo arranca con ``--http``:

- toda petición a ``/mcp`` exige ``Authorization: Bearer <token>``; el token sale de
  una variable de entorno y debe tener al menos 32 caracteres ASCII imprimibles;
- ``/healthz`` responde sin token y solo indica que el proceso vive;
- se rechazan peticiones con cabecera ``Origin`` (navegadores): los clientes MCP
  nativos no la envían y así se evita que una página web hable con el servidor;
- el SDK valida la cabecera ``Host`` contra una lista (protección DNS rebinding) y
  limita el tamaño del cuerpo.

Mismo contrato que el servidor HTTP de Rekora, para que un cliente se configure igual.
"""

from __future__ import annotations

import hmac
import ipaddress
import os
import string

MIN_TOKEN_CHARS = 32
DEFAULT_LISTEN = "127.0.0.1:8080"
_PRINTABLE = set(string.printable) - set(string.whitespace)


class HttpConfigError(ValueError):
    """Configuración HTTP inválida; el mensaje se muestra tal cual al usuario."""


def read_token(env_var: str) -> str:
    """Lee y valida el token del entorno. Nunca se acepta un valor por defecto."""
    token = os.environ.get(env_var, "")
    if len(token) < MIN_TOKEN_CHARS or any(c not in _PRINTABLE for c in token):
        raise HttpConfigError(
            f"{env_var} debe tener al menos {MIN_TOKEN_CHARS} caracteres ASCII imprimibles "
            "(por ejemplo: python -c \"import secrets; print(secrets.token_hex(32))\")"
        )
    return token


def parse_listen(value: str) -> tuple[str, int]:
    """``HOST:PORT`` (IPv4 o IPv6 entre corchetes) a ``(host, port)``."""
    host, sep, port_text = value.rpartition(":")
    if not sep or not port_text.isdigit() or not 0 < int(port_text) < 65536:
        raise HttpConfigError(f"--listen espera HOST:PORT, recibido {value!r}")
    host = host[1:-1] if host.startswith("[") and host.endswith("]") else host
    try:
        ipaddress.ip_address(host)
    except ValueError as error:
        raise HttpConfigError(f"--listen necesita una dirección IP, recibido {host!r}") from error
    return host, int(port_text)


def allowed_hosts(extra: list[str]) -> list[str]:
    """Valores de ``Host`` aceptados: loopback siempre, más los nombres explícitos."""
    hosts = ["127.0.0.1", "localhost", "[::1]"] + [h for h in extra if h]
    return [pattern for h in hosts for pattern in (h, f"{h}:*")]


class BearerGuard:
    """Middleware ASGI: salud sin token, sin navegadores y token obligatorio."""

    def __init__(self, app, token: str):
        self.app = app
        self.token = token.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":  # lifespan del gestor de sesiones: pasa intacto
            await self.app(scope, receive, send)
            return
        if scope.get("path") == "/healthz":
            await _respond(send, 200, b"ok")
            return
        headers = dict(scope.get("headers") or [])
        if b"origin" in headers:
            await _respond(send, 403, b"browser origins are not allowed")
            return
        auth = headers.get(b"authorization", b"")
        scheme, _, presented = auth.partition(b" ")
        if scheme.lower() != b"bearer" or not hmac.compare_digest(presented.strip(), self.token):
            await _respond(send, 401, b"missing or invalid bearer token",
                           [(b"www-authenticate", b'Bearer realm="mcp"')])
            return
        await self.app(scope, receive, send)


async def _respond(send, status: int, body: bytes, extra: list | None = None) -> None:
    headers = [(b"content-type", b"text/plain; charset=utf-8"), (b"content-length", str(len(body)).encode())]
    await send({"type": "http.response.start", "status": status, "headers": headers + (extra or [])})
    await send({"type": "http.response.body", "body": body})


def serve(mcp, listen: str, extra_hosts: list[str], token_env: str) -> None:
    """Sirve ``mcp`` (un FastMCP) por HTTP hasta SIGINT/SIGTERM."""
    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings

    token = read_token(token_env)
    host, port = parse_listen(listen)
    mcp.settings.host, mcp.settings.port = host, port
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=allowed_hosts(extra_hosts), allowed_origins=[]
    )
    app = BearerGuard(mcp.streamable_http_app(), token)
    uvicorn.run(app, host=host, port=port, log_level="warning")


def add_arguments(parser) -> None:
    """Opciones de transporte compartidas por los servidores MCP de este repo."""
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--stdio", action="store_true", help="stdio (por defecto)")
    mode.add_argument("--http", action="store_true", help="Streamable HTTP con token")
    parser.add_argument("--listen", default=DEFAULT_LISTEN, help=f"HOST:PORT para --http (por defecto {DEFAULT_LISTEN})")
    parser.add_argument("--allow-host", action="append", default=[], metavar="NOMBRE",
                        help="nombre de host público aceptado además de loopback (repetible)")
