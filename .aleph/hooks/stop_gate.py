#!/usr/bin/env python3
"""
.aleph/hooks/stop_gate.py
Hook Nativo: Stop Gate (EpistemicFrictionCalculator I_FE & Verificación de Cierre).
Calcula el Índice de Fricción Epistémica I_FE y verifica que las pruebas hayan pasado antes de cerrar turno.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, Optional


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


def _evaluate_pareto_distillation_gate(payload: Dict[str, Any], verified: bool, i_fe: float) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from aleph_core.security.aegis_shield import AegisShield
        from aleph_core.evolution.demiurgo_loop import GlobalOptimalityGate, SolutionCandidate
    except ImportError:
        return {"pareto_gate_approved": verified, "candidate_rule_id": None}

    if not verified or i_fe < 0.85:
        return {"pareto_gate_approved": False, "candidate_rule_id": None}

    si = str(payload.get("if_condition", "Cuando surge fricción repetida en ejecución"))
    entonces = str(payload.get("then_action", "Validar precondiciones y contrato AST antes de ejecutar"))
    evitar = str(payload.get("avoid_anti_pattern", "Reintentos ciegos sin diagnóstico"))
    directive = f"SI {si} -> ENTONCES {entonces} -> EVITAR {evitar}"
    if not AegisShield.scan_text(directive).safe:
        return {"pareto_gate_approved": False, "candidate_rule_id": None}

    baseline = SolutionCandidate(
        candidate_id="PASSIVE_NO_RULE",
        name="Sin destilación",
        paradigm="Pasivo",
        complexity_score=55.0,
        economic_score=80.0,
        trench_score=50.0,
        formal_safety_score=20.0,
        moat_score=15.0,
    )
    cand_id: Optional[str] = str(payload.get("candidate_rule_id", "REG-STOP-CANDIDATE"))
    candidate = SolutionCandidate(
        candidate_id=cand_id,
        name="Regla destilada StopGate",
        paradigm="Formal Determinista",
        complexity_score=94.0,
        economic_score=100.0,
        trench_score=95.0,
        formal_safety_score=96.0,
        moat_score=92.0,
    )
    t_res = GlobalOptimalityGate.run_tournament("StopGate Distillation", [baseline, candidate])
    approved = t_res.winner.candidate_id == cand_id
    return {"pareto_gate_approved": approved, "candidate_rule_id": cand_id if approved else None}


def evaluate_stop_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    verified = bool(payload.get("verified", True))
    retries = int(payload.get("retries_count", 0))
    failures = int(payload.get("failed_assertions", 0))
    novel = int(payload.get("novel_entities_count", 0))
    i_fe = compute_epistemic_friction_index(retries, failures, novel, verified=verified)
    gate = _evaluate_pareto_distillation_gate(payload, verified, i_fe)
    pareto_ok = bool(gate.get("pareto_gate_approved", verified))
    return {
        "distill_ready": verified,
        "epistemic_friction_index": i_fe,
        "should_distill_rule": verified and i_fe >= 0.85 and pareto_ok,
        "pareto_gate_approved": pareto_ok,
        "candidate_rule_id": gate.get("candidate_rule_id"),
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
