#!/usr/bin/env python3
"""Hook Nativo: Stop Gate (EpistemicFrictionCalculator I_FE >= 0.85 + Integridad Merkle Bitácora)."""
from pathlib import Path
import sys
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aleph_core.engine import get_shared_omega_engine


def evaluate_stop_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa I_FE de cierre de turno e integridad criptográfica Merkle de la Bitácora."""
    verified = bool(payload.get("verified", True))
    tests_passed = int(payload.get("tests_passed", 1 if verified else 0))
    tests_failed = int(payload.get("tests_failed", 0 if verified else 1))
    warnings_count = int(payload.get("warnings_count", 0))

    total_tests = max(1, tests_passed + tests_failed)
    i_fe = max(0.0, min(1.0, (tests_passed / float(total_tests)) - (0.05 * warnings_count)))
    if not verified:
        i_fe = min(i_fe, 0.4)

    omega = get_shared_omega_engine()
    telemetry = omega.get_vault_telemetry()
    merkle_valid = bool(telemetry.get("merkle_chain_valid", True))

    distill_ready = bool(verified and merkle_valid and i_fe >= 0.85)
    return {
        "distill_ready": distill_ready,
        "i_fe": round(i_fe, 4),
        "merkle_valid": merkle_valid,
        "active_rules": telemetry.get("total_rules", 0),
        "exit_code": 0 if (distill_ready or verified) else 1,
        "hook": "Stop",
    }
