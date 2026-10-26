"""Prueba real de la imagen Docker y del servicio Compose (solo biblioteca estándar).

Construye la imagen, habla MCP por stdio con `docker run -i`, comprueba que la imagen
no contiene datos personales y levanta Compose por HTTP en un puerto libre con token,
llamando una herramienta real. Usa un workspace temporal (copia de datos/ y .agents/),
nunca tus carpetas personales. Limpia contenedores y temporales al terminar.

    python scripts/test_docker.py
"""

import json
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "declara-mx:local"
SERVER_NAME = "declara-mx"
PREFIX = "DECLARA"  # variables de compose: <PREFIX>_MCP_TOKEN, _PORT, _WORKSPACE, _USER
WORKSPACE_COPY = ["datos", ".agents"]
TOOL = ("desglosar_iva", {"anio": 2026, "deposito": 1160})
FORBIDDEN_IN_IMAGE = ["config/contribuyente.yaml", "clientes.json", "2025", "2026"]


def run(*args, env=None, input=None, timeout=600):
    out = subprocess.run(args, env=env, input=input, text=True, capture_output=True, timeout=timeout,
                         encoding="utf-8")
    if out.returncode:
        raise RuntimeError(f"falló {' '.join(args)}:\n{out.stdout}\n{out.stderr}")
    return out.stdout


def rpc(url, token, message, session=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
               "Authorization": f"Bearer {token}"}
    if session:
        headers.update({"Mcp-Session-Id": session, "MCP-Protocol-Version": "2025-11-25"})
    req = urllib.request.Request(url, json.dumps(message).encode(), headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode()
        if "text/event-stream" in resp.headers.get("Content-Type", ""):
            data = next((line[5:].strip() for line in data.splitlines()
                         if line.startswith("data:") and line[5:].strip()), "")
        return (json.loads(data) if data else None), resp.headers.get("Mcp-Session-Id")


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "docker-smoke", "version": "1"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def main():
    run("docker", "build", "-t", IMAGE, str(ROOT))
    print("ok  build")

    listing = run("docker", "run", "--rm", "--entrypoint", "sh", IMAGE, "-c",
                  "find / -xdev \\( -path /proc -o -path /sys \\) -prune -o -print 2>/dev/null; true")
    for name in FORBIDDEN_IN_IMAGE:
        hits = [p for p in listing.splitlines() if p.endswith("/" + name) and "/site-packages/" not in p]
        assert not hits, f"la imagen contiene {name}: {hits}"
    print("ok  imagen sin datos personales")

    with tempfile.TemporaryDirectory(prefix="mcp-docker-") as tmp:
        work = Path(tmp)
        for name in WORKSPACE_COPY:
            if (ROOT / name).exists():
                shutil.copytree(ROOT / name, work / name)
        os.chmod(work, 0o777)
        user = f"{os.getuid()}:{os.getgid()}" if hasattr(os, "getuid") else "10001:10001"
        mount = f"{work}:/workspace"

        lines = "\n".join(json.dumps(m) for m in (INIT, INITIALIZED, {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": TOOL[0], "arguments": TOOL[1]}})) + "\n"
        out = run("docker", "run", "--rm", "-i", "--user", user, "-v", mount, IMAGE, input=lines, timeout=120)
        replies = {r.get("id"): r for r in map(json.loads, filter(None, out.splitlines()))}
        assert replies[1]["result"]["serverInfo"]["name"] == SERVER_NAME, out
        assert not replies[2]["result"].get("isError"), replies[2]
        print("ok  stdio: initialize + tools/call", TOOL[0])

        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        token = secrets.token_hex(32)
        project = f"smoke{secrets.token_hex(3)}"
        env = dict(os.environ, **{f"{PREFIX}_MCP_TOKEN": token, f"{PREFIX}_PORT": str(port),
                                  f"{PREFIX}_WORKSPACE": str(work), f"{PREFIX}_USER": user})
        compose = ["docker", "compose", "-p", project, "-f", str(ROOT / "compose.yaml")]
        try:
            run(*compose, "up", "-d", "--wait", env=env, timeout=300)
            url = f"http://127.0.0.1:{port}"
            with urllib.request.urlopen(url + "/healthz", timeout=10) as r:
                assert r.status == 200
            try:
                rpc(url + "/mcp", "x" * 64, INIT)
                raise AssertionError("aceptó un token incorrecto")
            except urllib.error.HTTPError as e:
                assert e.code == 401, e.code
            init, session = rpc(url + "/mcp", token, INIT)
            assert init["result"]["serverInfo"]["name"] == SERVER_NAME
            rpc(url + "/mcp", token, INITIALIZED, session)
            tools, _ = rpc(url + "/mcp", token, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session)
            names = {t["name"] for t in tools["result"]["tools"]}
            assert TOOL[0] in names, names
            called, _ = rpc(url + "/mcp", token, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                                  "params": {"name": TOOL[0], "arguments": TOOL[1]}}, session)
            assert not called["result"].get("isError"), called
            print(f"ok  compose HTTP en puerto {port}: token, {len(names)} herramientas, {TOOL[0]}")
        finally:
            subprocess.run([*compose, "down", "--remove-orphans"], env=env, capture_output=True, timeout=120)
            time.sleep(0.5)
    print("todo ok")


if __name__ == "__main__":
    main()
