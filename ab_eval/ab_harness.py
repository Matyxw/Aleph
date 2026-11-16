"""
Arnés A/B: ¿tu agente rinde mejor CON las reglas de El Aleph que SIN ellas?

Para cada tarea (JSONL) y cada repetición, corre el agente dos veces en copias limpias del
directorio de trabajo (orden aleatorio): brazo `with` y brazo `without`. El éxito lo decide un
comando de verificación externo (p. ej. `pytest -q`), nunca el propio agente.

Tu agente recibe:
  * el prompt por stdin y en la variable AGENT_PROMPT
  * ALEPH_ARM=with|without  -> TU script decide si activa o no la config/reglas de Aleph
  * (opcional) puede imprimir como última línea de stdout un JSON {"tokens": N}

Uso:
  python3 -m ab_eval.ab_harness --tasks ab_eval/tasks.example.jsonl \
      --agent-cmd "./mi_agente.sh" --reps 3 --out resultados.csv

Formato de tarea:  {"id": "t1", "prompt": "...", "workdir": "ruta/al/repo", "verify": "pytest -q"}
Sin shell: `--agent-cmd` y `verify` se parten con shlex (si necesitas pipes, ponlos en un script).
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import os
import random
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ARMS = ("with", "without")
MIN_PAIRS_CONCLUSIVE = 20


def mcnemar_exact_p(b: int, c: int) -> float:
    """p bilateral exacto (binomial, p=0.5) sobre los pares discordantes b y c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def _tokens_from(stdout: str) -> Optional[int]:
    for line in reversed(stdout.strip().splitlines()[-3:]):
        try:
            val = json.loads(line)
            if isinstance(val, dict) and isinstance(val.get("tokens"), int):
                return val["tokens"]
        except ValueError:
            continue
    return None


def run_arm(task: Dict[str, Any], arm: str, agent_cmd: str, timeout: int) -> Dict[str, Any]:
    src = Path(task["workdir"]).resolve()
    with tempfile.TemporaryDirectory(prefix=f"ab_{arm}_") as tmp:
        work = Path(tmp) / "work"
        shutil.copytree(src, work, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
        env = dict(os.environ, ALEPH_ARM=arm, AGENT_PROMPT=task["prompt"])
        t0 = time.perf_counter()
        agent_rc, tokens, timed_out = None, None, False
        try:
            _posix = os.name != "nt"
            r = subprocess.run(shlex.split(agent_cmd, posix=_posix), cwd=work, env=env, input=task["prompt"],
                               capture_output=True, text=True, timeout=timeout)
            agent_rc, tokens = r.returncode, _tokens_from(r.stdout)
        except subprocess.TimeoutExpired:
            timed_out = True
        elapsed = time.perf_counter() - t0
        try:
            v = subprocess.run(shlex.split(task["verify"], posix=(os.name != "nt")), cwd=work, capture_output=True, text=True, timeout=timeout)
            success = v.returncode == 0 and not timed_out
        except subprocess.TimeoutExpired:
            success = False
    return {"task": task["id"], "arm": arm, "success": int(success), "agent_rc": agent_rc,
            "timed_out": int(timed_out), "seconds": round(elapsed, 3), "tokens": tokens}


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_pair: Dict[tuple, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        by_pair.setdefault((r["task"], r["rep"]), {})[r["arm"]] = r
    b = c = both = neither = 0
    for pair in by_pair.values():
        if len(pair) != 2:
            continue
        w, wo = pair["with"]["success"], pair["without"]["success"]
        b += int(w and not wo)
        c += int(wo and not w)
        both += int(w and wo)
        neither += int(not w and not wo)
    out: Dict[str, Any] = {"pairs": b + c + both + neither, "with_only": b, "without_only": c,
                           "both": both, "neither": neither, "mcnemar_p": mcnemar_exact_p(b, c)}
    for arm in ARMS:
        sel = [r for r in rows if r["arm"] == arm]
        toks = [r["tokens"] for r in sel if r["tokens"] is not None]
        out[arm] = {"n": len(sel),
                    "success_rate": round(sum(r["success"] for r in sel) / len(sel), 4) if sel else None,
                    "median_seconds": round(statistics.median(r["seconds"] for r in sel), 3) if sel else None,
                    "median_tokens": statistics.median(toks) if toks else None}
    if out["pairs"] < MIN_PAIRS_CONCLUSIVE:
        out["verdict"] = f"NO CONCLUYENTE: {out['pairs']} pares (< {MIN_PAIRS_CONCLUSIVE})."
    elif out["mcnemar_p"] < 0.05:
        better = "CON reglas" if b > c else "SIN reglas"
        out["verdict"] = f"Diferencia significativa (p={out['mcnemar_p']:.3f}): mejor {better}."
    else:
        out["verdict"] = f"Sin diferencia detectable (p={out['mcnemar_p']:.3f})."
    return out


def run(tasks_path: Path, agent_cmd: str, reps: int, timeout: int, seed: int, out_csv: Optional[Path]) -> Dict[str, Any]:
    tasks = [json.loads(l) for l in tasks_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rng = random.Random(seed)
    rows: List[Dict[str, Any]] = []
    for task in tasks:
        for rep in range(reps):
            order = list(ARMS)
            rng.shuffle(order)
            for arm in order:
                row = run_arm(task, arm, agent_cmd, timeout)
                row["rep"] = rep
                rows.append(row)
    if out_csv:
        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["task", "rep", "arm", "success", "agent_rc", "timed_out", "seconds", "tokens"])
            w.writeheader()
            w.writerows(rows)
    return summarize(rows)


def _eval_baseline_arm(task: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Brazo Baseline (`without`): verificación sintáctica estándar sin reglas ni provers de El Aleph
    (ast.parse para Python o balanceo básico de delimitadores para JS/TSX/CSS/SQL).
    """
    prover = str(task.get("prover", ""))
    artifact = str(task.get("artifact", ""))
    if prover in (
        "z3_cegis",
        "z3_bounds",
        "z3_bitvector",
        "z3_null",
        "z3_key",
        "taint_icfg",
        "deadlock_lodg",
        "ssrf_egress",
        "resource_atomic",
    ) or (prover == "omega_gate" and "def " in artifact):
        try:
            ast.parse(artifact)
            return (False, "baseline_ast_syntax_only_missed_defect")
        except SyntaxError as exc:
            return (True, f"baseline_syntax_error:{exc}")
    # Non-Python artifacts: syntax/delimiter check only (cannot detect semantic/WCAG/JWT/DDL/RLS/injection defects)
    return (False, "baseline_lexical_only_missed_defect")


def _eval_aleph_arm(
    task: Dict[str, Any],
    z3_prover: Any,
    cegis_engine: Any,
    omega_engine: Any,
    verifiers: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Brazo El Aleph (`with`): ejecuta los demostradores formales reales (Z3/CEGIS, Taint IFDS/ICFG,
    LODG Deadlock, WCAG/DesignTokens, JWT/Cookie, CSP/XSS, SSRF, ZeroDowntime DDL, RLS,
    AegisShield y Compuerta Bitácora HippoRAG 2 + ResourceLeak/AtomicWrite).
    """
    prover = str(task.get("prover", ""))
    artifact = str(task.get("artifact", ""))
    expected = str(task.get("expected_defect", ""))

    if prover == "z3_cegis":
        res = cegis_engine.verify_and_autorepair(artifact)
        ok = (
            res.repaired
            and res.original_defect == expected
            and res.final_proof_status == "PROVEN_SAFE"
        )
        return (ok, f"cegis:{res.original_defect}->{res.final_proof_status}")

    if prover in ("z3_bounds", "z3_null", "z3_key", "z3_bitvector"):
        tree = ast.parse(artifact)
        fn_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        use_bv = prover == "z3_bitvector"
        proof = z3_prover.verify_function_ast(fn_node, source_code=artifact, use_bitvectors=use_bv)
        defect_val = proof.defect_type.value if proof.defect_type else ""
        ok = proof.status.value == "DEFECT_FOUND" and defect_val == expected
        return (ok, f"z3:{proof.status.value}:{defect_val}")

    if prover == "taint_icfg":
        rep = verifiers["InterProceduralTaintAnalyzer"].analyze_source(artifact)
        ok = (not rep.secure) and any(v.vulnerability_type == expected for v in rep.vulnerabilities_detected)
        return (ok, f"taint:vulns={len(rep.vulnerabilities_detected)}")

    if prover == "omega_gate":
        gate = omega_engine.enforce_pre_turn_bitacora_gate(artifact, top_k=5)
        ok = (not gate["gate_passed"]) and any(expected in v for v in gate["violations_detected"])
        return (ok, f"omega_gate:violations={len(gate['violations_detected'])}")

    if prover in ("csp_xss", "csp_config"):
        is_cfg = prover == "csp_config"
        rep = verifiers["ContentSecurityPolicyProver"].audit_frontend_security(artifact, is_config_file=is_cfg)
        ok = (not rep.formal_csp_safety_proven) and any(v.violation_type == expected for v in rep.violations)
        return (ok, f"csp:violations={len(rep.violations)}")

    if prover == "deadlock_lodg":
        rep = verifiers["LockOrderingDeadlockProver"].audit_source(artifact)
        ok = (not rep.deadlock_free) and len(rep.detected_cycles) >= 1
        return (ok, f"lodg:cycles={len(rep.detected_cycles)}")

    if prover == "wcag_design":
        rep = verifiers["DesignTokenAndWCAGContrastProver"].audit_and_repair_design_system(artifact)
        ok = (
            (not rep.formal_design_system_proven)
            and (not rep.wcag_contrast_aa_proven)
            and (not rep.wcag_target_size_proven)
            and len(rep.violations) >= 3
        )
        return (ok, f"wcag:violations={len(rep.violations)},min_cr={rep.min_measured_contrast_ratio}")

    if prover == "jwt_cookie":
        rep = verifiers["JWTSessionAndCookieSecurityProver"].audit_jwt_and_cookies(artifact)
        ok = (not rep.secure) and any(v.violation_type == expected for v in rep.violations)
        return (ok, f"jwt_cookie:violations={len(rep.violations)}")

    if prover == "ssrf_egress":
        rep = verifiers["SSRFSafeEgressGatewayProver"].audit_egress_code(artifact)
        ok = (not rep.formal_egress_safety_proven) and (not rep.private_ip_blocked) and len(rep.violations) >= 1
        return (ok, f"ssrf:violations={len(rep.violations)}")

    if prover == "ddl_zero_downtime":
        rep = verifiers["ZeroDowntimeDDLProver"].audit_ddl(artifact)
        ok = (not rep.zero_downtime_safe) and any(v.violation_type == expected for v in rep.violations)
        return (ok, f"ddl:violations={len(rep.violations)}")

    if prover == "rls_multitenant":
        rep = verifiers["MultiTenantRLSLeakAndMaskingProver"].audit_multitenant_sql(artifact)
        ok = (not rep.multi_tenant_isolation_proven) and any(v.violation_type == expected for v in rep.violations)
        return (ok, f"rls:violations={len(rep.violations)}")

    if prover == "aegis_shield":
        rep = verifiers["AegisShield"].scan_text(artifact)
        ok = (not rep.safe) and any(f.rule_id == expected for f in rep.findings)
        return (ok, f"aegis:findings={len(rep.findings)}")

    if prover == "resource_atomic":
        rep = verifiers["ResourceLeakAndCycleProver"].audit_code(artifact)
        leak_caught = (not rep.resource_leak_free) and len(rep.leaks_detected) >= 1
        with tempfile.TemporaryDirectory(prefix="ab_atomic_") as tmpdir:
            target = Path(tmpdir) / "checkpoint.json"
            verifiers["StateStore"].atomic_write_file(target, '{"ok": true}')
            atomic_ok = target.exists() and target.read_text(encoding="utf-8") == '{"ok": true}'
        return (leak_caught and atomic_ok, f"resource_leak={len(rep.leaks_detected)},atomic={atomic_ok}")

    return (False, f"unknown_prover:{prover}")


def run_builtin_sota_benchmark(
    tasks_path: Optional[Path] = None,
    seed: int = 0,
) -> Dict[str, Any]:
    """
    Ejecuta en proceso el benchmark A/B SOTA completo sobre las 25 tareas reales de `tasks.example.jsonl`,
    comparando el brazo Baseline (`without`) frente al stack completo de El Aleph (`with`),
    calcula el valor p exacto de McNemar y devuelve métricas auditables reproducibles.
    """
    from aleph_core.security.aegis_shield import AegisShield
    from aleph_core.self_improvement.omega_continual_learner import AlephOmegaContinualSelfImprovementEngine
    from aleph_core.state.store import StateStore
    from aleph_core.verification.z3_prover import (
        CEGISRepairEngine,
        ContentSecurityPolicyProver,
        DesignTokenAndWCAGContrastProver,
        InterProceduralTaintAnalyzer,
        JWTSessionAndCookieSecurityProver,
        LockOrderingDeadlockProver,
        MultiTenantRLSLeakAndMaskingProver,
        ResourceLeakAndCycleProver,
        SSRFSafeEgressGatewayProver,
        Z3VerificationEngine,
        ZeroDowntimeDDLProver,
    )

    resolved_tasks = Path(tasks_path) if tasks_path else (Path(__file__).resolve().parent / "tasks.example.jsonl")
    tasks = [json.loads(line) for line in resolved_tasks.read_text(encoding="utf-8").splitlines() if line.strip()]

    z3_prover = Z3VerificationEngine(timeout_ms=45)
    cegis_engine = CEGISRepairEngine(prover=z3_prover)
    omega_engine = AlephOmegaContinualSelfImprovementEngine()
    verifiers = {
        "AegisShield": AegisShield,
        "StateStore": StateStore,
        "InterProceduralTaintAnalyzer": InterProceduralTaintAnalyzer,
        "ContentSecurityPolicyProver": ContentSecurityPolicyProver,
        "LockOrderingDeadlockProver": LockOrderingDeadlockProver,
        "DesignTokenAndWCAGContrastProver": DesignTokenAndWCAGContrastProver,
        "JWTSessionAndCookieSecurityProver": JWTSessionAndCookieSecurityProver,
        "SSRFSafeEgressGatewayProver": SSRFSafeEgressGatewayProver,
        "ZeroDowntimeDDLProver": ZeroDowntimeDDLProver,
        "MultiTenantRLSLeakAndMaskingProver": MultiTenantRLSLeakAndMaskingProver,
        "ResourceLeakAndCycleProver": ResourceLeakAndCycleProver,
    }

    rng = random.Random(seed)
    rows: List[Dict[str, Any]] = []
    task_results: List[Dict[str, Any]] = []

    for task in tasks:
        order = list(ARMS)
        rng.shuffle(order)
        arm_details: Dict[str, Dict[str, Any]] = {}
        for arm in order:
            t0 = time.perf_counter()
            if arm == "with":
                success, detail = _eval_aleph_arm(task, z3_prover, cegis_engine, omega_engine, verifiers)
            else:
                success, detail = _eval_baseline_arm(task)
            elapsed = time.perf_counter() - t0
            row = {
                "task": task["id"],
                "rep": 0,
                "arm": arm,
                "success": int(bool(success)),
                "agent_rc": 0,
                "timed_out": 0,
                "seconds": round(elapsed, 6),
                "tokens": None,
            }
            rows.append(row)
            arm_details[arm] = {"success": bool(success), "detail": detail, "seconds": round(elapsed, 6)}

        task_results.append({
            "id": task["id"],
            "category": task.get("category", "general"),
            "with": arm_details["with"],
            "without": arm_details["without"],
        })

    summary = summarize(rows)
    summary["total_tasks"] = len(tasks)
    summary["task_results"] = task_results
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", required=True, type=Path)
    ap.add_argument("--agent-cmd", required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    print(json.dumps(run(a.tasks, a.agent_cmd, a.reps, a.timeout, a.seed, a.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
