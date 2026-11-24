"""ASGI MCP Remoto grado producción (Spec 2026-07-28: OAuth 2.1, RFC 9728/8707/6750, AegisShield)."""
from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
import datetime as _dt
import hashlib
import hmac
import json
import logging
import os
import re
import threading
import time
from typing import Any, Callable, Deque, Dict, FrozenSet, List, Optional, Tuple
import urllib.parse
import urllib.request

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

_AUDIT_LOG = logging.getLogger("aleph.remote.audit")
_SHELL_CHAIN_RE = re.compile(
    r"(?:(?:&&|\|\||;)\s*(?:cat|ls|sh|bash|zsh|cmd|powershell|pwsh|curl|wget|nc|whoami|id|uname|rm|python3?)\b|\$\([^)]+\)|`[^`]+`)",
    re.IGNORECASE,
)

REMOTE_SOVEREIGN_SCOPES: Dict[str, str] = {
    "aleph_bitacora_query_hipporag2_ppr": "aleph:read",
    "aleph_bitacora_vault_status_and_telemetry": "aleph:read",
    "aleph_bitacora_enforce_pre_turn_gate": "aleph:audit",
    "aleph_analyze_interprocedural_taint": "aleph:audit",
    "aleph_verify_deep_supabase_rls": "aleph:audit",
    "aleph_verify_and_repair": "aleph:verify",
    "aleph_run_optimality_tournament": "aleph:verify",
    "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault": "aleph:verify",
}
SCOPES_SUPPORTED: Tuple[str, ...] = ("aleph:read", "aleph:verify", "aleph:audit")
MAX_BODY_BYTES = 512 * 1024


@dataclass
class RemoteMCPConfig:
    canonical_url: str = "http://127.0.0.1:8080/mcp"
    oauth_issuer: str = "https://auth.example.com/"
    oauth_jwks_url: str = "https://auth.example.com/.well-known/jwks.json"
    jwks_ttl_sec: float = 300.0
    auth_mode: str = "oauth2_jwt"
    static_token: str = ""
    allowed_origins: FrozenSet[str] = field(default_factory=frozenset)
    allowed_hosts: FrozenSet[str] = field(default_factory=frozenset)
    max_body_bytes: int = MAX_BODY_BYTES
    rate_limit_rpm: int = 120
    tool_timeout_sec: float = 25.0
    jwks_fetcher: Optional[Callable[[str], Dict[str, Any]]] = None

    @classmethod
    def from_env(cls) -> "RemoteMCPConfig":
        raw_orig, raw_hosts = os.environ.get("ALEPH_MCP_ALLOWED_ORIGINS", ""), os.environ.get("ALEPH_MCP_ALLOWED_HOSTS", "")
        return cls(
            canonical_url=os.environ.get("ALEPH_MCP_CANONICAL_URL", "http://127.0.0.1:8080/mcp").strip(),
            oauth_issuer=os.environ.get("ALEPH_OAUTH_ISSUER", "https://auth.example.com/").strip(),
            oauth_jwks_url=os.environ.get("ALEPH_OAUTH_JWKS_URL", "https://auth.example.com/.well-known/jwks.json").strip(),
            jwks_ttl_sec=max(5.0, float(os.environ.get("ALEPH_OAUTH_JWKS_TTL_SEC", "300"))),
            auth_mode=os.environ.get("ALEPH_MCP_AUTH_MODE", "oauth2_jwt").strip().lower(),
            static_token=os.environ.get("ALEPH_MCP_STATIC_TOKEN", "").strip(),
            allowed_origins=frozenset(x.strip() for x in raw_orig.split(",") if x.strip()),
            allowed_hosts=frozenset(x.strip().lower() for x in raw_hosts.split(",") if x.strip()),
            max_body_bytes=min(MAX_BODY_BYTES, max(1024, int(os.environ.get("ALEPH_MCP_MAX_BODY_BYTES", str(MAX_BODY_BYTES))))),
            rate_limit_rpm=max(1, int(os.environ.get("ALEPH_MCP_RATE_LIMIT_RPM", "120"))),
            tool_timeout_sec=max(1.0, float(os.environ.get("ALEPH_MCP_TOOL_TIMEOUT_SEC", "25"))),
        )

    def metadata_url(self) -> str:
        p = urllib.parse.urlsplit(self.canonical_url)
        base = f"{p.scheme}://{p.netloc}" if p.scheme and p.netloc else ""
        return f"{base}/.well-known/oauth-protected-resource/mcp"


class _JWKSVerifier:
    """Caché TTL thread-safe de JWKS + verificación criptográfica OAuth 2.1 (iss/aud RFC 8707)."""

    def __init__(self, cfg: RemoteMCPConfig):
        self.cfg, self._lock, self._expires_at = cfg, threading.RLock(), 0.0
        self._keys_by_kid: Dict[str, Any] = {}
        self._all_keys: List[Any] = []

    def _load_jwks(self, force: bool = False) -> Tuple[Dict[str, Any], List[Any]]:
        import jwt as pyjwt

        now = time.monotonic()
        with self._lock:
            if not force and now < self._expires_at and self._all_keys:
                return self._keys_by_kid, self._all_keys
            if self.cfg.jwks_fetcher is not None:
                doc = self.cfg.jwks_fetcher(self.cfg.oauth_jwks_url)
            else:
                req = urllib.request.Request(self.cfg.oauth_jwks_url, headers={"User-Agent": "ElAleph-MCP-RS/33.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    doc = json.loads(resp.read().decode("utf-8"))
            jwk_set = pyjwt.PyJWKSet.from_dict(doc if isinstance(doc, dict) else {"keys": []})
            self._keys_by_kid = {k.key_id: k.key for k in jwk_set.keys if k.key_id}
            self._all_keys = [k.key for k in jwk_set.keys]
            self._expires_at = now + self.cfg.jwks_ttl_sec
            return self._keys_by_kid, self._all_keys

    def verify(self, token: str) -> Dict[str, Any]:
        import jwt as pyjwt

        header = pyjwt.get_unverified_header(token)
        kid, alg = header.get("kid"), str(header.get("alg") or "")
        if alg not in ("RS256", "RS384", "RS512", "ES256", "ES384", "PS256", "EdDSA"):
            raise pyjwt.InvalidAlgorithmError("Disallowed JWT algorithm")
        by_kid, all_k = self._load_jwks(force=False)
        candidates = [by_kid[kid]] if (kid and kid in by_kid) else ([] if kid else all_k)
        if not candidates and kid:
            by_kid, all_k = self._load_jwks(force=True)
            candidates = [by_kid[kid]] if kid in by_kid else []
        last_err: Optional[Exception] = None
        for key in candidates:
            try:
                return pyjwt.decode(token, key=key, algorithms=[alg], audience=self.cfg.canonical_url, issuer=self.cfg.oauth_issuer, options={"require": ["exp", "iss", "aud"]})
            except Exception as exc:
                last_err = exc
        raise last_err or pyjwt.InvalidTokenError("No matching JWK")


class _SlidingWindowLimiter:
    """Rate limiter en memoria por identidad o IP."""

    def __init__(self, rpm: int):
        self.rpm, self._lock, self._buckets = max(1, int(rpm)), threading.Lock(), {}  # type: ignore[var-annotated]

    def allow(self, key: str) -> bool:
        now, cutoff = time.monotonic(), time.monotonic() - 60.0
        with self._lock:
            q: Deque[float] = self._buckets.setdefault(key, deque())
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.rpm:
                return False
            q.append(now)
            return True


def _extract_scopes(claims: Dict[str, Any]) -> FrozenSet[str]:
    scopes: List[str] = []
    if isinstance(claims.get("scope"), str):
        scopes.extend(s for s in str(claims.get("scope")).split() if s)
    raw_scp = claims.get("scp")
    if isinstance(raw_scp, list):
        scopes.extend(str(s).strip() for s in raw_scp if str(s).strip())
    elif isinstance(raw_scp, str):
        scopes.extend(s for s in raw_scp.split() if s)
    return frozenset(scopes)


def _check_aegis_args(args: Any) -> Tuple[bool, str]:
    from aleph_core.security.aegis_shield import AegisShield

    report = AegisShield.scan_payload(args)
    if not report.safe:
        return False, "AEGIS_BLOCKED:" + ",".join(f.rule_id for f in report.findings[:3])
    serialized = json.dumps(args, ensure_ascii=False) if isinstance(args, (dict, list)) else str(args)
    if _SHELL_CHAIN_RE.search(serialized):
        return False, "AEGIS_BLOCKED:SHELL_CHAINING"
    return True, "OK"


def _emit_audit_log(sub: str, client_id: str, tool_name: str, req_scope: str, args: Any, status: str, t0_ns: int) -> None:
    raw = json.dumps(args if args is not None else {}, sort_keys=True, ensure_ascii=False).encode("utf-8")
    _AUDIT_LOG.info(json.dumps({
        "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(), "sub": str(sub or "anonymous"),
        "client_id": str(client_id or "unknown"), "tool_name": str(tool_name or ""), "required_scope": str(req_scope or ""),
        "args_sha256": hashlib.sha256(raw).hexdigest(), "status": status, "latency_ms": round((time.perf_counter_ns() - t0_ns) / 1_000_000.0, 2),
    }, ensure_ascii=False))


def create_remote_mcp_app(config: Optional[RemoteMCPConfig] = None, mcp_server: Any = None) -> Starlette:
    """Construye la app Starlette ASGI con OAuth 2.1 RS + RFC 9728 + AegisShield + remote_sovereign."""
    cfg = config if config is not None else RemoteMCPConfig.from_env()
    if cfg.auth_mode not in ("oauth2_jwt", "static_bearer"):
        raise ValueError(f"Unsupported ALEPH_MCP_AUTH_MODE: {cfg.auth_mode}")
    verifier, limiter, server, srv_lock = _JWKSVerifier(cfg), _SlidingWindowLimiter(cfg.rate_limit_rpm), mcp_server, threading.Lock()

    def _get_server() -> Any:
        nonlocal server
        with srv_lock:
            if server is None:
                from aleph_core.engine import AlephUniversalMCPServer
                server = AlephUniversalMCPServer()
            return server

    def _cors(origin: Optional[str]) -> Dict[str, str]:
        if origin and origin in cfg.allowed_origins:
            return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Headers": "Authorization, Content-Type, Mcp-Session-Id", "Access-Control-Allow-Methods": "POST, OPTIONS", "Vary": "Origin"}
        return {"Vary": "Origin"}

    async def healthz(_req: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def protected_resource_metadata(_req: Request) -> JSONResponse:
        return JSONResponse({"resource": cfg.canonical_url, "authorization_servers": [cfg.oauth_issuer], "scopes_supported": list(SCOPES_SUPPORTED), "bearer_methods_supported": ["header"]}, headers={"Cache-Control": "public, max-age=300"})

    async def mcp_options(req: Request) -> Response:
        orig = req.headers.get("origin")
        return Response(status_code=403) if (orig and orig not in cfg.allowed_origins) else Response(status_code=204, headers=_cors(orig))

    async def mcp_post(req: Request) -> Response:
        t0, origin = time.perf_counter_ns(), req.headers.get("origin")
        cors = _cors(origin)
        if origin and origin not in cfg.allowed_origins:
            return JSONResponse({"error": "origin_forbidden"}, status_code=403)
        if cfg.allowed_hosts and (req.headers.get("host") or "").split(":")[0].lower() not in cfg.allowed_hosts:
            return JSONResponse({"error": "host_forbidden"}, status_code=403)
        cl_raw = req.headers.get("content-length")
        if cl_raw is not None:
            try:
                if int(cl_raw) > cfg.max_body_bytes:
                    return JSONResponse({"error": "payload_too_large"}, status_code=413, headers=cors)
            except ValueError:
                return JSONResponse({"error": "invalid_content_length"}, status_code=400, headers=cors)

        auth_hdr, unauth_hdr = req.headers.get("authorization") or "", {**cors, "WWW-Authenticate": f'Bearer resource_metadata="{cfg.metadata_url()}"'}
        if not auth_hdr.startswith("Bearer ") or len(auth_hdr) <= 7:
            return JSONResponse({"error": "unauthorized"}, status_code=401, headers=unauth_hdr)
        token = auth_hdr[7:].strip()
        if cfg.auth_mode == "static_bearer":
            if not cfg.static_token or not hmac.compare_digest(token, cfg.static_token):
                return JSONResponse({"error": "invalid_token"}, status_code=401, headers=unauth_hdr)
            claims: Dict[str, Any] = {"sub": "static_local_operator", "client_id": "static_bearer", "scope": " ".join(SCOPES_SUPPORTED)}
        else:
            try:
                claims = verifier.verify(token)
            except Exception:
                return JSONResponse({"error": "invalid_token"}, status_code=401, headers=unauth_hdr)

        sub, client_id = str(claims.get("sub") or "unknown"), str(claims.get("client_id") or claims.get("azp") or claims.get("sub") or "unknown")
        if not limiter.allow(f"{sub}:{req.client.host if req.client else 'unknown'}"):
            return JSONResponse({"error": "rate_limited"}, status_code=429, headers={**cors, "Retry-After": "60"})
        raw_body = await req.body()
        if len(raw_body) > cfg.max_body_bytes:
            return JSONResponse({"error": "payload_too_large"}, status_code=413, headers=cors)
        try:
            rpc = json.loads(raw_body.decode("utf-8"))
        except Exception:
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}, status_code=400, headers=cors)
        if not isinstance(rpc, dict):
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}, status_code=400, headers=cors)

        req_id, method = rpc.get("id"), str(rpc.get("method") or "")
        params = rpc.get("params") if isinstance(rpc.get("params"), dict) else {}
        if method == "notifications/initialized":
            return Response(status_code=202, headers=cors)
        if method == "tools/list":
            full_sov = _get_server().handle_jsonrpc_request({"jsonrpc": "2.0", "id": req_id, "method": "tools/list", "params": {"profile": "sovereign"}})
            safe_tools = [t for t in full_sov.get("result", {}).get("tools", []) if t.get("name") in REMOTE_SOVEREIGN_SCOPES]
            _emit_audit_log(sub, client_id, "tools/list", "none", {"profile": "remote_sovereign"}, "OK", t0)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"tools": safe_tools}}, headers=cors)
        if method == "tools/call":
            tool_name, args = str(params.get("name") or ""), (params.get("arguments") if isinstance(params.get("arguments"), dict) else {})
            if tool_name not in REMOTE_SOVEREIGN_SCOPES:
                _emit_audit_log(sub, client_id, tool_name, "forbidden", args, "TOOL_FORBIDDEN", t0)
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32003, "message": f"Tool blocked in remote_sovereign profile: {tool_name}"}}, status_code=403, headers=cors)
            req_scope = REMOTE_SOVEREIGN_SCOPES[tool_name]
            if req_scope not in _extract_scopes(claims):
                _emit_audit_log(sub, client_id, tool_name, req_scope, args, "INSUFFICIENT_SCOPE", t0)
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32001, "message": f"Missing required scope: {req_scope}"}}, status_code=403, headers={**cors, "WWW-Authenticate": f'Bearer error="insufficient_scope", scope="{req_scope}"'})
            safe_ok, reason = _check_aegis_args(args)
            if not safe_ok:
                _emit_audit_log(sub, client_id, tool_name, req_scope, args, reason, t0)
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32002, "message": reason}}, status_code=403, headers=cors)
            try:
                res = await asyncio.wait_for(asyncio.to_thread(_get_server().handle_jsonrpc_request, {"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": tool_name, "arguments": args}}), timeout=cfg.tool_timeout_sec)
            except asyncio.TimeoutError:
                _emit_audit_log(sub, client_id, tool_name, req_scope, args, "TIMEOUT", t0)
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32004, "message": "Tool execution timeout"}}, status_code=504, headers=cors)
            _emit_audit_log(sub, client_id, tool_name, req_scope, args, "OK", t0)
            return JSONResponse(res, headers=cors)
        res = await asyncio.to_thread(_get_server().handle_jsonrpc_request, rpc)
        _emit_audit_log(sub, client_id, method, "none", {}, "OK", t0)
        return JSONResponse(res, headers=cors)

    return Starlette(routes=[
        Route("/healthz", healthz, methods=["GET"]),
        Route("/.well-known/oauth-protected-resource", protected_resource_metadata, methods=["GET"]),
        Route("/.well-known/oauth-protected-resource/mcp", protected_resource_metadata, methods=["GET"]),
        Route("/mcp", mcp_options, methods=["OPTIONS"]),
        Route("/mcp", mcp_post, methods=["POST"]),
    ])


def run_remote_mcp_server(host: str = "0.0.0.0", port: int = 8080) -> int:
    import uvicorn

    cfg = RemoteMCPConfig.from_env()
    if cfg is None:
        return 1
    app = create_remote_mcp_app(cfg)
    if app is None:
        return 1
    uvicorn.run(app, host=host, port=int(port), log_level="info", access_log=False)
    return 0
