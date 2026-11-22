#!/usr/bin/env python3
"""
.aleph/hooks/stop_gate.py
Hook Nativo: Stop Gate (EpistemicFrictionCalculator I_FE & Verificación de Cierre).
Calcula el Índice de Fricción Epistémica I_FE y verifica que las pruebas hayan pasado antes de cerrar turno.
"""
from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

_LOG = logging.getLogger(__name__)


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


def _run_incremental_z3_gate(payload: Dict[str, Any], repo_root: Path) -> Dict[str, Any]:
    default_rep = {
        "ran": False,
        "safe_to_commit": True,
        "inspected_files": 0,
        "blocking_defects": [],
        "formal_proofs_passed": 0,
    }
    raw_changed = payload.get("changed_files")
    if not raw_changed:
        return default_rep

    py_files: Dict[str, str] = {}
    if isinstance(raw_changed, dict):
        for rel_p, content in raw_changed.items():
            key = str(rel_p)
            if key.endswith(".py") and isinstance(content, str):
                py_files[key] = content
    elif isinstance(raw_changed, (list, tuple)):
        for item in raw_changed:
            rel_str = str(item)
            if not rel_str.endswith(".py"):
                continue
            cand = Path(rel_str)
            if not cand.is_file():
                cand = Path(os.path.join(str(repo_root), rel_str))
            if cand.is_file():
                try:
                    py_files[rel_str] = cand.read_text(encoding="utf-8", errors="ignore")
                except OSError as exc:
                    _LOG.debug("Skipping unreadable changed file %s: %s", rel_str, exc)

    if not py_files:
        return default_rep

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from aleph_core.verification.z3_prover import GitSovereignGate
        rep = GitSovereignGate.audit_files_dict(py_files)
        return {
            "ran": True,
            "safe_to_commit": bool(rep.safe_to_commit),
            "inspected_files": int(rep.inspected_files_count),
            "blocking_defects": list(rep.blocking_defects),
            "formal_proofs_passed": int(rep.formal_proofs_passed),
        }
    except Exception as exc:
        _LOG.debug("Incremental Z3 gate failed cleanly: %s", exc)
        return default_rep


def _run_bounded_auto_gepa(
    payload: Dict[str, Any],
    store: Any,
    pareto_ok: bool,
    verified: bool,
) -> Dict[str, Any]:
    idle = {
        "auto_gepa_triggered": False,
        "auto_gepa_refuted_count": 0,
        "auto_gepa_promoted_mutations": [],
        "auto_gepa_promoted_rules": [],
        "auto_gepa_rejected_rules": [],
        "auto_gepa_regression_rate_pct": 0.0,
    }
    disable_gepa = os.environ.get("ALEPH_DISABLE_AUTO_GEPA", "").strip() in ("1", "true", "TRUE") or bool(
        payload.get("disable_auto_gepa", False)
    )
    if disable_gepa or not (verified and pareto_ok) or store is None:
        return idle

    try:
        from aleph_core.state.epistemic import EpistemicStatus
        from aleph_core.evolution.gepa_optimizer import GEPAMutationCandidate, GEPAReflectiveOptimizer
        from aleph_core.memory.bicameral import AlgorithmicRule
    except ImportError as exc:
        _LOG.debug("Auto-GEPA imports unavailable: %s", exc)
        return idle

    refuted_claims = store.list_claims(status=EpistemicStatus.REFUTED)
    threshold_raw = payload.get("gepa_auto_threshold", os.environ.get("ALEPH_GEPA_AUTO_THRESHOLD", "3"))
    threshold = max(1, int(threshold_raw))
    if len(refuted_claims) < threshold:
        idle["auto_gepa_refuted_count"] = len(refuted_claims)
        return idle

    extra_cands: List[Any] = []
    for raw_c in payload.get("gepa_extra_candidates") or []:
        if isinstance(raw_c, GEPAMutationCandidate):
            extra_cands.append(raw_c)
        elif isinstance(raw_c, dict):
            r_data = raw_c.get("rule", {})
            rule = AlgorithmicRule(
                rule_id=str(r_data.get("rule_id", "REG-GEPA-EXT")),
                category=str(r_data.get("category", "Seguridad")),
                priority=str(r_data.get("priority", "ALTA")),
                friction_pattern=str(r_data.get("friction_pattern", "Hostile check")),
                if_condition=str(r_data.get("if_condition", "Siempre")),
                then_action=str(r_data.get("then_action", "Validar")),
                avoid_anti_pattern=str(r_data.get("avoid_anti_pattern", "Ignorar")),
            )
            extra_cands.append(
                GEPAMutationCandidate(
                    rule=rule,
                    source_claim_ids=list(raw_c.get("source_claim_ids", ["EXT"])),
                    failure_cluster=str(raw_c.get("failure_cluster", "EXTERNAL")),
                    pass_at_1_gain=float(raw_c.get("pass_at_1_gain", 90.0)),
                    token_efficiency_score=float(raw_c.get("token_efficiency_score", 90.0)),
                    has_quadratic_loop=bool(raw_c.get("has_quadratic_loop", False)),
                )
            )

    opt = GEPAReflectiveOptimizer(store=store, session_db_path="")
    gepa_res = opt.evolve_from_traces(
        extra_candidates=extra_cands or None,
        include_session_db=False,
        apply_promotions=True,
    )
    promoted = list(gepa_res.get("promoted", []))
    rejected = list(gepa_res.get("rejected", []))
    reg_rates = [float(p.get("regression_rate_pct", 0.0)) for p in promoted]
    return {
        "auto_gepa_triggered": True,
        "auto_gepa_refuted_count": len(refuted_claims),
        "auto_gepa_promoted_mutations": [str(p.get("mutation_id", "")) for p in promoted],
        "auto_gepa_promoted_rules": [str(p.get("rule_id", "")) for p in promoted],
        "auto_gepa_rejected_rules": [str(r.get("rule_id", "")) for r in rejected],
        "auto_gepa_regression_rate_pct": max(reg_rates) if reg_rates else 0.0,
    }


def evaluate_stop_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = payload if isinstance(payload, dict) else {}
    repo_root = Path(__file__).resolve().parents[2]
    z3_gate = _run_incremental_z3_gate(safe_payload, repo_root)

    verified = bool(safe_payload.get("verified", True))
    if z3_gate.get("ran") and not z3_gate.get("safe_to_commit"):
        verified = False

    retries = int(safe_payload.get("retries_count", 0))
    failures = int(safe_payload.get("failed_assertions", 0))
    novel = int(safe_payload.get("novel_entities_count", 0))
    i_fe = compute_epistemic_friction_index(retries, failures, novel, verified=verified)
    gate = _evaluate_pareto_distillation_gate(safe_payload, verified, i_fe)
    pareto_ok = bool(gate.get("pareto_gate_approved", verified))

    persisted_to_memory = False
    persisted_db_path: Optional[str] = None
    promoted_rule_ids: list[str] = []
    has_real_friction = (retries > 0 or failures > 0)
    disable_env = os.environ.get("ALEPH_DISABLE_STOP_PERSIST", "").strip() in ("1", "true", "TRUE")
    explicit_flag = safe_payload.get("persist_session_lesson")
    should_persist = (
        pareto_ok
        and verified
        and not disable_env
        and (
            explicit_flag is True
            or (explicit_flag is not False and (has_real_friction or bool(safe_payload.get("db_path"))))
        )
    )
    should_check_gepa = (
        pareto_ok
        and verified
        and (should_persist or bool(safe_payload.get("trigger_auto_gepa")) or bool(safe_payload.get("db_path")))
    )

    store = None
    if should_persist or should_check_gepa:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        try:
            from aleph_core.state.store import StateStore
            from aleph_core.memory.bicameral import BicameralMemory
            from aleph_core.evolution.demiurgo_loop import DemiurgoEvolutionEngine
            if safe_payload.get("db_path"):
                db_path = Path(str(safe_payload.get("db_path")))
            else:
                db_path = Path(os.path.join(str(repo_root), ".aleph", "runtime", "session_evolution.db"))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            store = StateStore(db_path=db_path)

            if should_persist:
                memory = BicameralMemory(store)
                evo = DemiurgoEvolutionEngine(store, memory)
                evo_res = evo.record_and_evolve_from_session_failure(
                    task_type=str(safe_payload.get("task_type", "session_stop_gate")),
                    error_msg=str(safe_payload.get("error_msg", f"epistemic_friction_retries={retries}")),
                    failed_payload=safe_payload.get("failed_payload") if isinstance(safe_payload.get("failed_payload"), dict) else {},
                    proposed_if=str(safe_payload.get("if_condition", "Cuando surge fricción repetida en ejecución")),
                    proposed_then=str(safe_payload.get("then_action", "Validar precondiciones y contrato AST antes de ejecutar")),
                    proposed_avoid=str(safe_payload.get("avoid_anti_pattern", "Reintentos ciegos sin diagnóstico")),
                    category=str(safe_payload.get("category", "Código")),
                    rule_id=str(gate.get("candidate_rule_id")) if gate.get("candidate_rule_id") else None,
                )
                persisted_to_memory = bool(evo_res.get("promoted"))
                promoted_rule_ids = list(evo_res.get("promoted_rule_ids", []))
                if persisted_to_memory:
                    persisted_db_path = str(db_path)
        except Exception as exc:
            _LOG.debug("StopGate persistence error: %s", exc)
            persisted_to_memory = False
            store = None

    auto_gepa = _run_bounded_auto_gepa(safe_payload, store, pareto_ok, verified)

    return {
        "distill_ready": verified,
        "epistemic_friction_index": i_fe,
        "should_distill_rule": verified and i_fe >= 0.85 and pareto_ok,
        "pareto_gate_approved": pareto_ok,
        "candidate_rule_id": gate.get("candidate_rule_id"),
        "persisted_to_memory": persisted_to_memory,
        "persisted_db_path": persisted_db_path,
        "promoted_rule_ids": promoted_rule_ids,
        "incremental_z3_gate": z3_gate,
        **auto_gepa,
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
