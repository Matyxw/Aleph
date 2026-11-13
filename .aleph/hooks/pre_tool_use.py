#!/usr/bin/env python3
"""Hook Nativo: PreToolUse (AegisShield + Bitácora Gate + Z3 AST Guard)."""
from pathlib import Path
import re
import sys
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aleph_core.engine import get_shared_omega_engine
from aleph_core.security.aegis_shield import AegisShield

_BLOCKED_CMD_PATTERNS = (
    re.compile(r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(?:/(?:\s|$|\*)|~|\$HOME)", re.IGNORECASE),
    re.compile(r"git\s+push\s+(?:--force|-f)\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+(?:DATABASE|SCHEMA|TABLE)\s+\w+", re.IGNORECASE),
    re.compile(r"\bFORMAT\s+[A-Z]:", re.IGNORECASE),
)


def evaluate_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Audita comandos e insumos de herramientas antes de despacharlos al sistema."""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    cmd = str(payload.get("command") or tool_input.get("command") or tool_input.get("CommandLine") or "")
    code = str(payload.get("code") or payload.get("content") or tool_input.get("content") or "")
    combined = "\n".join(part for part in (cmd, code) if part)

    reasons: List[str] = []
    for pat in _BLOCKED_CMD_PATTERNS:
        if cmd and pat.search(cmd):
            reasons.append(f"Comando destructivo bloqueado ({pat.pattern})")

    sec_report = AegisShield.scan_payload(payload)
    if not sec_report.safe:
        reasons.extend(f"[{f.rule_id}] {f.description}" for f in sec_report.findings)

    omega = get_shared_omega_engine()
    gate = omega.enforce_pre_turn_bitacora_gate(combined or "tool invocation", top_k=3)
    if not gate.get("gate_passed", True):
        reasons.extend(gate.get("aegis_findings", ["Bitacora gate blocked payload"]))

    blocked = len(reasons) > 0
    return {
        "allowed": not blocked,
        "exit_code": 2 if blocked else 0,
        "hook": "PreToolUse",
        "reasons": reasons,
        "bitacora_rules": [r.get("rule_id") for r in gate.get("injected_rules", [])],
    }
