#!/usr/bin/env python3
"""Hook Nativo: PostToolUse (SurgicalLogCrusher + Auditoría de Fuga de Secretos AegisShield)."""
from pathlib import Path
import sys
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aleph_core.security.aegis_shield import AegisShield

_PRIORITY_MARKERS = ("error", "fail", "exception", "traceback", "critical", "warning", "assert", "passed", "failed")


def _crush_lines(lines: List[str], max_lines: int = 80) -> List[str]:
    if len(lines) <= max_lines:
        return lines
    kept: List[str] = []
    prev_line: str = ""
    repeat_count = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx < 10 or idx >= len(lines) - 10 or any(m in stripped.lower() for m in _PRIORITY_MARKERS):
            if repeat_count > 0:
                kept.append(f"... ({repeat_count} líneas repetidas omitidas)")
                repeat_count = 0
            kept.append(line)
            prev_line = line
        elif line == prev_line:
            repeat_count += 1
        else:
            prev_line = line
            if len(kept) < max_lines:
                kept.append(line)
    if repeat_count > 0:
        kept.append(f"... ({repeat_count} líneas repetidas omitidas)")
    return kept[:max_lines]


def evaluate_post_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Comprime logs extensos preservando diagnósticos y detecta fugas de credenciales en stdout."""
    out = str(payload.get("stdout") or payload.get("tool_response") or "")
    lines = out.splitlines()
    crushed = _crush_lines(lines)
    sec_report = AegisShield.scan_text(out)
    secret_findings = [f.rule_id for f in sec_report.findings if f.rule_id == "AEGIS-002"]
    orig_cnt = max(1, len(lines)) if lines else 0
    reduction_pct = round((1.0 - (len(crushed) / orig_cnt)) * 100.0, 2) if orig_cnt else 0.0

    return {
        "original_lines": len(lines),
        "crushed_len": len(crushed),
        "reduction_pct": reduction_pct,
        "crushed_text": "\n".join(crushed),
        "secret_leak_detected": len(secret_findings) > 0,
        "secret_findings": secret_findings,
        "exit_code": 2 if secret_findings else 0,
        "hook": "PostToolUse",
    }
