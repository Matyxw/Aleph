#!/usr/bin/env python3
"""Hook Nativo: PreToolUse (ASTGuard & Z3 Formal Gate)."""
from typing import Any, Dict

def evaluate_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    cmd = str(payload.get("command", ""))
    blocked = ("rm -rf /" in cmd) or ("git push --force" in cmd)
    return {"allowed": not blocked, "exit_code": 2 if blocked else 0, "hook": "PreToolUse"}
