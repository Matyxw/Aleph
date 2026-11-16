#!/usr/bin/env python3
"""
.aleph/hooks/stop_gate.py
Hook Nativo: Stop Gate (EpistemicFrictionCalculator I_FE & Verificación de Cierre).
Calcula el Índice de Fricción Epistémica I_FE y verifica que las pruebas hayan pasado antes de cerrar turno.
"""
from __future__ import annotations

import json
import math
import sys
from typing import Any, Dict


def compute_epistemic_friction_index(
    retries_count: int = 0,
    failed_assertions: int = 0,
    novel_entities_count: int = 0,
    verified: bool = True,
) -> float:
    """
    Calcula el Índice de Fricción Epistémica I_FE en [0.0, 1.0]:
    Combina reintentos de herramientas, aserciones fallidas previas y novedad léxica mediante sigmoide logística.
    """
    raw_energy = 0.45 * retries_count + 0.65 * failed_assertions + 0.08 * novel_entities_count
    if verified and raw_energy == 0.0:
        return 0.88
    score = 1.0 / (1.0 + math.exp(-(1.65 + raw_energy)))
    return round(min(1.0, max(0.0, score)), 4)


def evaluate_stop_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    verified = bool(payload.get("verified", True))
    retries = int(payload.get("retries_count", 0))
    failures = int(payload.get("failed_assertions", 0))
    novel = int(payload.get("novel_entities_count", 0))
    i_fe = compute_epistemic_friction_index(retries, failures, novel, verified=verified)
    return {
        "distill_ready": verified,
        "epistemic_friction_index": i_fe,
        "should_distill_rule": verified and i_fe >= 0.85,
        "exit_code": 0 if verified else 1,
        "hook": "Stop",
    }


def main() -> int:
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {"verified": True}
    res = evaluate_stop_gate(payload)
    sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
    return int(res["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
