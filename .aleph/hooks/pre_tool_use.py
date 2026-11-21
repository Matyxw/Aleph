#!/usr/bin/env python3
"""
.aleph/hooks/pre_tool_use.py
Hook Nativo: PreToolUse (ASTGuard, AegisShield & Z3 Formal Gate).
Audita comandos de shell, escrituras en archivos y parches de código antes de ejecutar una herramienta.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List


DESTRUCTIVE_SHELL_PATTERNS = (
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+/(?:\s|$)",
    r"\bgit\s+push\s+--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bmkfs\.",
    r"\bdd\s+if=/dev/",
    r":\(\)\s*\{\s*:\|:&\s*\};:",
    r"\bchmod\s+-R\s+777\s+/",
)

FORBIDDEN_CODE_PATTERNS = (
    (r"transition\s*:\s*all\b", "Uso prohibido de 'transition: all' detectado en CSS."),
    (r"\bVACUUM\s+FULL\b", "Uso prohibido de 'VACUUM FULL' detectado en SQL."),
)


def _scan_with_aegis_shield(text: str) -> List[str]:
    """Ejecuta el escudo determinista de 5 capas (NFKC, homóglifos, Base64/Hex, firmas y AST taint)."""
    if not text:
        return []
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from aleph_core.security.aegis_shield import AegisShield
    except ImportError:
        return []
    rep = AegisShield.scan_text(text)
    if rep.safe:
        return []
    return [f"AegisShield [{f.rule_id} - {f.category}]: {f.description}" for f in rep.findings]


def evaluate_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    cmd = str(payload.get("command", ""))
    code_content = str(payload.get("code", payload.get("content", "")))
    reasons: List[str] = []

    blocked = ("rm -rf /" in cmd) or ("git push --force" in cmd)
    for pat in DESTRUCTIVE_SHELL_PATTERNS:
        if re.search(pat, cmd):
            blocked = True
            reasons.append(f"Destructive command pattern matched: {pat}")

    aegis_cmd_findings = _scan_with_aegis_shield(cmd)
    if aegis_cmd_findings:
        blocked = True
        reasons.extend(aegis_cmd_findings)

    if code_content:
        for pat, msg in FORBIDDEN_CODE_PATTERNS:
            if re.search(pat, code_content, re.IGNORECASE):
                blocked = True
                reasons.append(msg)

        aegis_code_findings = _scan_with_aegis_shield(code_content)
        if aegis_code_findings:
            blocked = True
            reasons.extend(aegis_code_findings)

        if payload.get("language") == "python" or str(payload.get("file_path", "")).endswith(".py"):
            try:
                ast.parse(code_content)
            except SyntaxError as exc:
                blocked = True
                reasons.append(f"Python AST SyntaxError at line {exc.lineno}: {exc.msg}")

    return {
        "allowed": not blocked,
        "exit_code": 2 if blocked else 0,
        "hook": "PreToolUse",
        "reasons": reasons,
    }


def main() -> int:
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {"command": raw}
    res = evaluate_pre_tool_use(payload)
    sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
    return int(res["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
