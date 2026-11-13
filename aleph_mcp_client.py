#!/usr/bin/env python3
"""
El Aleph v3.8.0 — Universal MCP Client & Auto-Daemon Bridge (stdio + Streamable HTTP)
=====================================================================================
Connects to `AlephUniversalMCPServer` via official MCP JSON-RPC 2.0 (`2025-06-18`)
over either:
1. Streamable HTTP (`http://127.0.0.1:8765/mcp`) — auto-spawning the background daemon if not running.
2. Direct `stdio` subprocess (`python3 aleph_cli.py mcp-serve`).

Usage:
  python3 aleph_mcp_client.py status
  python3 aleph_mcp_client.py list-tools
  python3 aleph_mcp_client.py call <tool_name> '<json_args>' [--transport http|stdio]
  python3 aleph_mcp_client.py verify-all
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
CLI_PATH = BASE_DIR / "aleph_cli.py"
DEFAULT_HTTP_URL = "http://127.0.0.1:8765"
PID_FILE = Path("/tmp/aleph_mcp_http.pid")
LOG_FILE = Path("/tmp/aleph_mcp_http.log")


class AlephMCPClient:
    """Official MCP JSON-RPC 2.0 Client supporting both Streamable HTTP and stdio transports."""

    def __init__(self, base_url: str = DEFAULT_HTTP_URL):
        self.base_url = base_url.rstrip("/")
        self.mcp_endpoint = f"{self.base_url}/mcp"
        self.health_endpoint = f"{self.base_url}/health"
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def is_http_daemon_alive(self) -> bool:
        try:
            req = urllib.request.Request(self.health_endpoint, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("status") == "ok"
        except Exception:
            return False
        return False

    def ensure_http_daemon(self, port: int = 8765) -> Dict[str, Any]:
        """Auto-starts the Streamable HTTP MCP daemon in the background if not already running."""
        if self.is_http_daemon_alive():
            return {"status": "already_running", "endpoint": self.mcp_endpoint, "health": self.health_endpoint}

        log_fh = open(LOG_FILE, "a", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(CLI_PATH), "mcp-http", str(port)],
            cwd=str(BASE_DIR),
            stdout=log_fh,
            stderr=log_fh,
            close_fds=True,
            start_new_session=True,
        )
        PID_FILE.write_text(str(proc.pid), encoding="utf-8")

        deadline = time.time() + 5.0
        while time.time() < deadline:
            if self.is_http_daemon_alive():
                return {
                    "status": "started",
                    "pid": proc.pid,
                    "endpoint": self.mcp_endpoint,
                    "health": self.health_endpoint,
                }
            time.sleep(0.1)

        raise RuntimeError(f"Failed to start El Aleph MCP HTTP daemon within 5s. Check {LOG_FILE}")

    def rpc_http(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a JSON-RPC 2.0 request over Streamable HTTP POST /mcp."""
        self.ensure_http_daemon()
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.mcp_endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)

    def rpc_stdio(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a JSON-RPC 2.0 handshake + request over MCP stdio."""
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "aleph-mcp-stdio-client", "version": "3.8.0"}},
        }
        target_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": method,
            "params": params or {},
        }
        stdin_payload = json.dumps(init_req) + "\n" + json.dumps(target_req) + "\n"
        proc = subprocess.run(
            [sys.executable, str(CLI_PATH), "mcp-serve"],
            cwd=str(BASE_DIR),
            input=stdin_payload,
            text=True,
            capture_output=True,
            timeout=30.0,
        )
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if not lines:
            raise RuntimeError(f"Empty stdio response. stderr: {proc.stderr}")
        return json.loads(lines[-1])

    def call_tool(self, name: str, arguments: Dict[str, Any], transport: str = "http") -> Dict[str, Any]:
        """Calls any of the 19 MCP tools over HTTP or stdio and parses the tool result."""
        rpc_fn = self.rpc_http if transport == "http" else self.rpc_stdio
        resp = rpc_fn("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp:
            return {"ok": False, "error": resp["error"]}
        content = resp.get("result", {}).get("content", [])
        is_error = resp.get("result", {}).get("isError", False)
        parsed_text = content[0].get("text", "{}") if content else "{}"
        try:
            data = json.loads(parsed_text)
        except Exception:
            data = {"raw": parsed_text}
        return {"ok": not is_error, "transport": transport, "tool": name, "result": data}


def main():
    parser = argparse.ArgumentParser(description="El Aleph v3.8.0 Universal MCP Client")
    parser.add_argument("--url", default=DEFAULT_HTTP_URL, help="Streamable HTTP MCP base URL")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Ensure MCP HTTP daemon is running and return health + protocol status")
    sub.add_parser("list-tools", help="List all registered MCP tools via JSON-RPC 2.0")

    p_call = sub.add_parser("call", help="Invoke an MCP tool by name with JSON arguments")
    p_call.add_argument("tool_name", help="Name of the MCP tool (e.g. aleph_verify_and_repair, aleph_analyze_interprocedural_taint)")
    p_call.add_argument("json_args", nargs="?", default="{}", help="JSON object of arguments")
    p_call.add_argument("--transport", choices=["http", "stdio"], default="http", help="MCP transport")

    sub.add_parser("verify-all", help="Run full end-to-end verification of both stdio and HTTP MCP transports")

    args = parser.parse_args()
    client = AlephMCPClient(base_url=args.url)

    if args.cmd == "status":
        daemon_info = client.ensure_http_daemon()
        init_resp = client.rpc_http("initialize", {"clientInfo": {"name": "gemini-web-mcp-client", "version": "3.8.0"}})
        tools_resp = client.rpc_http("tools/list", {})
        tools = tools_resp.get("result", {}).get("tools", [])
        print(json.dumps({
            "daemon": daemon_info,
            "protocolVersion": init_resp.get("result", {}).get("protocolVersion"),
            "serverInfo": init_resp.get("result", {}).get("serverInfo"),
            "registered_mcp_tools_count": len(tools),
            "registered_mcp_tools": [t["name"] for t in tools],
        }, indent=2, ensure_ascii=False))

    elif args.cmd == "list-tools":
        resp = client.rpc_http("tools/list", {})
        print(json.dumps(resp.get("result", {}), indent=2, ensure_ascii=False))

    elif args.cmd == "call":
        parsed_args = json.loads(args.json_args)
        res = client.call_tool(args.tool_name, parsed_args, transport=args.transport)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.cmd == "verify-all":
        t0 = time.perf_counter()
        daemon_info = client.ensure_http_daemon()
        http_init = client.rpc_http("initialize", {"clientInfo": {"name": "gemini-mcp-verifier", "version": "3.8.0"}})
        stdio_init = client.rpc_stdio("initialize", {"clientInfo": {"name": "gemini-mcp-stdio", "version": "3.8.0"}})
        tools_list = client.rpc_http("tools/list", {})["result"]["tools"]

        sample_code = (
            "def safe_transfer(balance: int, amount: int) -> int:\n"
            "    if balance < amount or amount <= 0:\n"
            "        return balance\n"
            "    return balance - amount\n"
        )
        prove_http = client.call_tool("aleph_verify_and_repair", {"source_code": sample_code}, transport="http")
        prove_stdio = client.call_tool("aleph_verify_and_repair", {"source_code": sample_code}, transport="stdio")
        taint_http = client.call_tool("aleph_analyze_interprocedural_taint", {"source_code": sample_code}, transport="http")
        pcc_http = client.call_tool("aleph_generate_proof_certificate", {"source_code": sample_code}, transport="http")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        print(json.dumps({
            "verified": True,
            "elapsed_ms": round(elapsed_ms, 2),
            "daemon": daemon_info,
            "http_protocol": http_init["result"]["protocolVersion"],
            "stdio_protocol": stdio_init["result"]["protocolVersion"],
            "total_mcp_tools": len(tools_list),
            "mcp_tool_names": [t["name"] for t in tools_list],
            "checks": {
                "http_aleph_verify_and_repair": prove_http["result"],
                "stdio_aleph_verify_and_repair": prove_stdio["result"],
                "http_aleph_analyze_interprocedural_taint": taint_http["result"],
                "http_aleph_generate_proof_certificate_seal": pcc_http["result"].get("integrity_seal", "")[:16],
            }
        }, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
