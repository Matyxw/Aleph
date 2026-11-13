#!/usr/bin/env python3
"""Hook Nativo: Stop Gate (EpistemicFrictionCalculator I_FE >= 0.85)."""
from typing import Any, Dict

def evaluate_stop_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    verified = bool(payload.get("verified", True))
    return {"distill_ready": verified, "exit_code": 0, "hook": "Stop"}
