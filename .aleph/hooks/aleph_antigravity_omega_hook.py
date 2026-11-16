#!/usr/bin/env python3
"""
.aleph/hooks/aleph_antigravity_omega_hook.py
Hook Always-On de Pre-Turno y Post-Turno para Google Antigravity.
- En Pre-Turno: Consulta las 350+ reglas internas de la Bitácora mediante HippoRAG 2 PPR y audita el plan/código.
- En Post-Turno: Si hubo un error reparado o nuevo aprendizaje, lo destila y sella en la cadena Merkle sin olvido.
"""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine


def main() -> int:
    engine = AlephOmegaContinualSelfImprovementEngine()
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    arg = sys.argv[2] if len(sys.argv) > 2 else ""

    if mode == "pre-turn":
        res = engine.enforce_pre_turn_bitacora_gate(arg or "general engineering audit", top_k=5)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["gate_passed"] else 1
    elif mode == "post-turn":
        rep = engine.run_omega_self_improvement_cycle(task_description=arg or "post-turn consolidation")
        print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        return 0 if rep.passed else 1
    else:
        print(json.dumps(engine.get_vault_telemetry(), indent=2, ensure_ascii=False))
        return 0


if __name__ == "__main__":
    sys.exit(main())
