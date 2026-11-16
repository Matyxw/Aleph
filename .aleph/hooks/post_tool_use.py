#!/usr/bin/env python3
"""
.aleph/hooks/post_tool_use.py
Hook Nativo: PostToolUse (SurgicalLogCrusher & Deduplicación Estructural de Trazas).
Comprime logs repetitivos preservando stack traces, líneas de error y resúmenes de salida.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List


CRITICAL_LOG_RE = re.compile(
    r"(Traceback|Error:|Exception:|FAIL:|ERROR:|AssertionError|SyntaxError|WARNING|CRITICAL)",
    re.IGNORECASE,
)


def crush_log_lines(lines: List[str], max_head: int = 20, max_tail: int = 25) -> List[str]:
    """
    Comprime quirúrgicamente salidas de herramientas masivas conservando:
    1. Cabecera inicial (`max_head` líneas)
    2. Todas las líneas con trazas de error o fallos críticos (con deduplicación consecutiva)
    3. Cola final (`max_tail` líneas)
    """
    if len(lines) <= (max_head + max_tail + 10):
        return lines

    head = lines[:max_head]
    tail = lines[-max_tail:]
    middle = lines[max_head:-max_tail]
    critical_middle: List[str] = []
    last_line = None
    for ln in middle:
        if CRITICAL_LOG_RE.search(ln) and ln != last_line:
            critical_middle.append(ln)
            last_line = ln

    omitted = len(middle) - len(critical_middle)
    summary_marker = f"... [SurgicalLogCrusher: {omitted} líneas rutinarias omitidas, {len(critical_middle)} alertas preservadas] ..."
    return head + [summary_marker] + critical_middle[:50] + tail


def evaluate_post_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    out = str(payload.get("stdout", ""))
    lines = out.splitlines()
    crushed = crush_log_lines(lines)
    compression_ratio = 1.0 - (len(crushed) / max(1, len(lines))) if lines else 0.0
    return {
        "crushed_len": len(lines),
        "retained_lines_count": len(crushed),
        "compression_ratio": round(max(0.0, compression_ratio), 4),
        "crushed_preview": "\n".join(crushed[:40]),
        "exit_code": 0,
        "hook": "PostToolUse",
    }


def main() -> int:
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {"stdout": raw}
    res = evaluate_post_tool_use(payload)
    sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
    return int(res["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
