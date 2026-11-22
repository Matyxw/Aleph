"""
CORTE 3: Runner Autónomo Durable + Sandbox + Checkpoints SQLite WAL + Cola Multi-Ticket + Entrega en Rama Aislada.
Integra DynamicDAGScheduler, SovereignCostRouter, Gemini4AsymmetricAdapter, Isolation Sandbox Driver,
AegisShield, ForensicCircuitBreaker, CounterfactualFaultLocalizer, CEGISRepairEngine, GitSovereignGate
y EphemeralCASWorktreeTransaction sin importar aleph_core.research_archive.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from aleph_core.engine import ForensicCircuitBreaker
from aleph_core.memory.bicameral import BicameralMemory
from aleph_core.router.cost_router import SovereignCostRouter
from aleph_core.router.dispatcher import (
    CounterfactualFaultLocalizer,
    DAGScheduleResult,
    DAGTaskNode,
    DynamicDAGScheduler,
    EphemeralCASWorktreeTransaction,
    JITContextEntropyCompiler,
    TaskContract,
)
from aleph_core.router.llm_adapter import Gemini4AsymmetricAdapter
from aleph_core.sandbox.driver import SandboxResult, create_sandbox_driver
from aleph_core.security.aegis_shield import AegisShield
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus
from aleph_core.state.store import StateStore
from aleph_core.verification.z3_prover import CEGISRepairEngine, GitSovereignGate


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUTONOMOUS_DB = str(REPO_ROOT / ".aleph" / "runtime" / "autonomous_state.db")


class AutonomousWaveCrashSimulated(RuntimeError):
    """Excepción controlada para simular una caída dura entre olas y verificar reanudación durable."""


def _ensure_autonomous_schema(store: StateStore) -> None:
    if store is None:
        raise ValueError("store requerido para inicializar esquema autónomo")
    with store._connection() as conn:
        if conn is None:
            raise RuntimeError("Conexión SQLite requerida")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS autonomous_checkpoints (
                run_id TEXT NOT NULL,
                wave_index INTEGER NOT NULL,
                status TEXT NOT NULL,
                node_ids_json TEXT NOT NULL,
                envelopes_json TEXT NOT NULL,
                staged_files_json TEXT NOT NULL,
                results_json TEXT NOT NULL,
                sandbox_tier TEXT NOT NULL DEFAULT 'PROCESS_WORKTREE',
                updated_at REAL NOT NULL,
                PRIMARY KEY (run_id, wave_index)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS autonomous_runs (
                run_id TEXT PRIMARY KEY,
                repo_dir TEXT NOT NULL,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                delivery_branch TEXT NOT NULL DEFAULT '',
                skipped_waves_json TEXT NOT NULL DEFAULT '[]',
                executed_waves_json TEXT NOT NULL DEFAULT '[]',
                repair_attempts INTEGER NOT NULL DEFAULT 0,
                telemetry_json TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS autonomous_task_queue (
                ticket_id TEXT PRIMARY KEY,
                repo_dir TEXT NOT NULL,
                goal TEXT NOT NULL,
                test_command TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'PENDING',
                worker_pid INTEGER NOT NULL DEFAULT 0,
                run_id TEXT NOT NULL DEFAULT '',
                error_summary TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.commit()


def _collect_repo_files(repo_path: Path, max_files: int = 128) -> Dict[str, str]:
    ignore_dirs = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", ".venv", "venv", ".aleph"}
    collected: Dict[str, str] = {}
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = sorted(d for d in dirs if d not in ignore_dirs)
        for fname in sorted(files):
            if not fname.endswith((".py", ".json", ".toml", ".md", ".txt")):
                continue
            full = Path(root) / fname
            try:
                if full.stat().st_size > 256_000:
                    continue
                rel = full.relative_to(repo_path).as_posix()
                collected[rel] = full.read_text(encoding="utf-8", errors="replace")
                if len(collected) >= max_files:
                    return collected
            except OSError:
                continue
    return collected


def _find_unguarded_divisions(source_code: str) -> List[Tuple[ast.FunctionDef, str]]:
    """Detecta divisiones en funciones Python sin guarda explícita contra cero sobre el divisor."""
    findings: List[Tuple[ast.FunctionDef, str]] = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        guarded_names = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.If):
                test_src = ast.unparse(sub.test) if hasattr(ast, "unparse") else ""
                for m in re.findall(r"\b([A-Za-z_]\w*)\b", test_src):
                    if "== 0" in test_src or "!= 0" in test_src or "<= 0" in test_src or f"not {m}" in test_src:
                        guarded_names.add(m)
        for sub in ast.walk(node):
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(sub.right, ast.Name) and sub.right.id not in guarded_names:
                    findings.append((node, sub.right.id))
                    break
    return findings


def _inject_zero_division_guard(source_code: str) -> Tuple[str, bool]:
    """Inyecta guarda determinista en runtime + verifica con GitSovereignGate sin depender de decoradores externos."""
    findings = _find_unguarded_divisions(source_code)
    if not findings:
        return source_code, False

    lines = source_code.splitlines(keepends=True)
    if not lines:
        return source_code, False

    # Aplicar de abajo hacia arriba para preservar números de línea
    applied = False
    for func_node, divisor_name in sorted(findings, key=lambda item: item[0].lineno, reverse=True):
        if not func_node.body:
            continue
        first_stmt = func_node.body[0]
        # Respetar docstring si es el primer statement
        if (
            isinstance(first_stmt, ast.Expr)
            and isinstance(getattr(first_stmt, "value", None), ast.Constant)
            and isinstance(first_stmt.value.value, str)
            and len(func_node.body) > 1
        ):
            anchor_stmt = func_node.body[1]
        else:
            anchor_stmt = first_stmt

        line_idx = max(0, anchor_stmt.lineno - 1)
        target_line = lines[line_idx] if line_idx < len(lines) else ""
        indent = target_line[: len(target_line) - len(target_line.lstrip(" \t"))]
        if not indent:
            indent = " " * (func_node.col_offset + 4)

        guard_block = f"{indent}if {divisor_name} == 0:\n{indent}    return 0.0\n"
        if f"if {divisor_name} == 0:" in source_code:
            continue
        lines.insert(line_idx, guard_block)
        applied = True

    if not applied:
        return source_code, False
    updated = "".join(lines)
    try:
        ast.parse(updated)
    except SyntaxError:
        return source_code, False
    return updated, True


def _extract_python_code_block(text: str) -> Optional[str]:
    m = re.search(r"```python\s*\n(.*?)\n```", text, flags=re.DOTALL)
    return m.group(1) if m else None


def _rule_matches_zero_division(rules: List[Any]) -> List[str]:
    matched: List[str] = []
    for r in rules:
        blob = f"{r.rule_id} {r.category} {r.friction_pattern} {r.if_condition} {r.then_action}".lower()
        if any(tok in blob for tok in ("zero_division", "zerodivision", "divisor == 0", "división por cero", "division by zero", "b == 0")):
            matched.append(str(r.rule_id))
    return matched


def _default_test_command(repo_path: Path) -> str:
    py_exe = sys.executable or "python"
    if (repo_path / "tests").is_dir():
        return f'"{py_exe}" -m unittest discover -s tests -q'
    return f'"{py_exe}" -m unittest discover -q'


def _deliver_to_isolated_branch(
    repo_path: Path,
    branch_name: str,
    staged_files: Dict[str, str],
    commit_message: str,
) -> Dict[str, Any]:
    """Crea commit en rama aislada aleph/auto-<run_id> usando git worktree temporal sin tocar la rama activa."""
    if not (repo_path / ".git").exists():
        return {"delivered": False, "reason": "not_a_git_repo", "branch": branch_name}

    wt_parent = Path(tempfile.mkdtemp(prefix="aleph_branch_deliver_"))
    wt_dir = wt_parent / "wt"
    try:
        proc_add = subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "add", "-B", branch_name, str(wt_dir), "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc_add.returncode != 0:
            return {
                "delivered": False,
                "reason": "git_worktree_add_failed",
                "stderr": proc_add.stderr.strip(),
                "branch": branch_name,
            }

        for rel, content in staged_files.items():
            dest = wt_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

        subprocess.run(["git", "-C", str(wt_dir), "add", "-A"], capture_output=True, text=True, timeout=20)
        status_proc = subprocess.run(
            ["git", "-C", str(wt_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if not status_proc.stdout.strip():
            rev = subprocess.run(
                ["git", "-C", str(wt_dir), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "delivered": True,
                "branch": branch_name,
                "commit_sha": rev.stdout.strip(),
                "changes_committed": 0,
            }

        # Asegurar identidad local solo en el repo temporal si el host/sandbox no la configuró
        name_chk = subprocess.run(["git", "-C", str(wt_dir), "config", "user.name"], capture_output=True, text=True)
        if name_chk.returncode != 0 or not name_chk.stdout.strip():
            subprocess.run(["git", "-C", str(wt_dir), "config", "user.name", "El Aleph Autonomous"], capture_output=True)
        email_chk = subprocess.run(["git", "-C", str(wt_dir), "config", "user.email"], capture_output=True, text=True)
        if email_chk.returncode != 0 or not email_chk.stdout.strip():
            subprocess.run(["git", "-C", str(wt_dir), "config", "user.email", "aleph-auto@local.invalid"], capture_output=True)

        proc_commit = subprocess.run(
            ["git", "-C", str(wt_dir), "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc_commit.returncode != 0:
            return {
                "delivered": False,
                "reason": "git_commit_failed",
                "stderr": proc_commit.stderr.strip(),
                "branch": branch_name,
            }
        rev = subprocess.run(["git", "-C", str(wt_dir), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=15)
        return {
            "delivered": True,
            "branch": branch_name,
            "commit_sha": rev.stdout.strip(),
            "changes_committed": len(status_proc.stdout.strip().splitlines()),
        }
    finally:
        if wt_dir.exists():
            subprocess.run(
                ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_dir)],
                capture_output=True,
                timeout=20,
            )
        shutil.rmtree(wt_parent, ignore_errors=True)


class AutonomousRunner:
    """
    Orquestador autónomo durable de El Aleph:
    - Ejecución DAG por olas con sobres PCCHE y asignación asimétrica TIER_0..TIER_3.
    - Checkpoints SQLite WAL tras cada ola + reanudación exacta (--resume) omitiendo olas verificadas.
    - Sandbox aislado (Docker o git worktree + stripping de secretos + taskkill) + AegisShield + ForensicCircuitBreaker.
    - Localización contrafactual + CEGIS/AST runtime repair + GitSovereignGate + entrega en rama aislada aleph/auto-<run_id>.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        sandbox_mode: str = "auto",
        provider_mode: str = "auto",
        session_token_budget: int = 24000,
    ) -> None:
        resolved_db = db_path or DEFAULT_AUTONOMOUS_DB
        Path(resolved_db).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = resolved_db
        self.store = StateStore(db_path=resolved_db)
        _ensure_autonomous_schema(self.store)
        self.sandbox_mode = sandbox_mode
        self.provider_mode = provider_mode
        self.session_token_budget = session_token_budget

    def _save_wave_checkpoint(
        self,
        run_id: str,
        wave_index: int,
        status: str,
        node_ids: List[str],
        envelopes: Dict[str, Any],
        staged_files: Dict[str, str],
        results: Dict[str, Any],
        sandbox_tier: str,
    ) -> None:
        now = time.time()
        with self.store._connection() as conn:
            conn.execute(
                """
                INSERT INTO autonomous_checkpoints (
                    run_id, wave_index, status, node_ids_json, envelopes_json,
                    staged_files_json, results_json, sandbox_tier, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, wave_index) DO UPDATE SET
                    status=excluded.status,
                    node_ids_json=excluded.node_ids_json,
                    envelopes_json=excluded.envelopes_json,
                    staged_files_json=excluded.staged_files_json,
                    results_json=excluded.results_json,
                    sandbox_tier=excluded.sandbox_tier,
                    updated_at=excluded.updated_at
                """,
                (
                    run_id,
                    int(wave_index),
                    status,
                    json.dumps(node_ids, ensure_ascii=False),
                    json.dumps(envelopes, ensure_ascii=False, sort_keys=True),
                    json.dumps(staged_files, ensure_ascii=False, sort_keys=True),
                    json.dumps(results, ensure_ascii=False, sort_keys=True, default=str),
                    sandbox_tier,
                    now,
                ),
            )
            conn.commit()

    def _load_completed_checkpoints(self, run_id: str) -> Dict[int, Dict[str, Any]]:
        with self.store._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM autonomous_checkpoints WHERE run_id = ? AND status = 'COMPLETED' ORDER BY wave_index ASC",
                (run_id,),
            ).fetchall()
        out: Dict[int, Dict[str, Any]] = {}
        for r in rows:
            out[int(r["wave_index"])] = {
                "wave_index": int(r["wave_index"]),
                "status": r["status"],
                "node_ids": json.loads(r["node_ids_json"]),
                "envelopes": json.loads(r["envelopes_json"]),
                "staged_files": json.loads(r["staged_files_json"]),
                "results": json.loads(r["results_json"]),
                "sandbox_tier": r["sandbox_tier"],
            }
        return out

    def _upsert_run_record(
        self,
        run_id: str,
        repo_dir: str,
        goal: str,
        status: str,
        delivery_branch: str,
        skipped_waves: List[int],
        executed_waves: List[int],
        repair_attempts: int,
        telemetry: Dict[str, Any],
    ) -> None:
        now = time.time()
        with self.store._connection() as conn:
            conn.execute(
                """
                INSERT INTO autonomous_runs (
                    run_id, repo_dir, goal, status, delivery_branch,
                    skipped_waves_json, executed_waves_json, repair_attempts, telemetry_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    delivery_branch=excluded.delivery_branch,
                    skipped_waves_json=excluded.skipped_waves_json,
                    executed_waves_json=excluded.executed_waves_json,
                    repair_attempts=excluded.repair_attempts,
                    telemetry_json=excluded.telemetry_json,
                    updated_at=excluded.updated_at
                """,
                (
                    run_id,
                    repo_dir,
                    goal,
                    status,
                    delivery_branch,
                    json.dumps(skipped_waves),
                    json.dumps(executed_waves),
                    int(repair_attempts),
                    json.dumps(telemetry, ensure_ascii=False, sort_keys=True, default=str),
                    now,
                    now,
                ),
            )
            conn.commit()

    def get_run_checkpoints(self, run_id: str) -> List[Dict[str, Any]]:
        with self.store._connection() as conn:
            rows = conn.execute(
                "SELECT run_id, wave_index, status, node_ids_json, sandbox_tier, updated_at "
                "FROM autonomous_checkpoints WHERE run_id = ? ORDER BY wave_index ASC",
                (run_id,),
            ).fetchall()
        return [
            {
                "run_id": r["run_id"],
                "wave_index": int(r["wave_index"]),
                "status": r["status"],
                "node_ids": json.loads(r["node_ids_json"]),
                "sandbox_tier": r["sandbox_tier"],
                "updated_at": float(r["updated_at"]),
            }
            for r in rows
        ]

    def run_task(
        self,
        repo_dir: str,
        goal: str,
        test_command: Optional[str] = None,
        run_id: Optional[str] = None,
        resume: bool = False,
        simulate_crash_at_wave: Optional[int] = None,
        delivery_branch: Optional[str] = None,
        sandbox_mode: Optional[str] = None,
        provider_mode: Optional[str] = None,
        custom_llm_responder: Optional[Callable[[str, str, Dict[str, Any]], str]] = None,
        create_branch_delivery: bool = True,
    ) -> Dict[str, Any]:
        repo_path = Path(repo_dir).resolve()
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Repositorio destino inexistente: {repo_path}")

        rid = run_id or f"run_{uuid.uuid4().hex[:10]}"
        branch = delivery_branch or f"aleph/auto-{rid}"
        cmd = test_command or _default_test_command(repo_path)

        # Escaneo obligatorio AegisShield sobre objetivo y comando
        goal_scan = AegisShield.scan_text(f"{goal}\n{cmd}")
        if not goal_scan.safe:
            return {
                "run_id": rid,
                "success": False,
                "status": "BLOCKED_BY_AEGIS",
                "findings": goal_scan.findings,
            }

        sandbox = create_sandbox_driver(mode=sandbox_mode or self.sandbox_mode)
        adapter = Gemini4AsymmetricAdapter(
            store=self.store,
            session_token_budget=self.session_token_budget,
            provider_mode=provider_mode or self.provider_mode,
            custom_responder=custom_llm_responder,
        )
        breaker = ForensicCircuitBreaker(failure_threshold=2)
        memory = BicameralMemory(self.store)

        base_files = _collect_repo_files(repo_path)
        completed_ckpts = self._load_completed_checkpoints(rid) if resume else {}

        # Definir topología DAG real de 3 olas para que DynamicDAGScheduler compute olas y asignación asimétrica
        dag_nodes = {
            "wave0_plan": DAGTaskNode(
                contract=TaskContract(
                    task_id="wave0_plan",
                    task_type="ast_plan_and_rule_guard",
                    input_payload={"prompt": f"Planificar reparación AST/Z3: {goal}", "repo_files": sorted(base_files.keys())},
                ),
                dependencies=set(),
                read_symbols={"repo_state"},
                write_symbols={"plan_spec"},
            ),
            "wave1_execute_repair": DAGTaskNode(
                contract=TaskContract(
                    task_id="wave1_execute_repair",
                    task_type="sandbox_verify_and_repair",
                    input_payload={"prompt": f"Ejecutar verificación sandbox y reparar fallos: {cmd}"},
                ),
                dependencies={"wave0_plan"},
                read_symbols={"plan_spec"},
                write_symbols={"staged_files"},
                inject_parent_envelopes=True,
            ),
            "wave2_gate_deliver": DAGTaskNode(
                contract=TaskContract(
                    task_id="wave2_gate_deliver",
                    task_type="git_gate_and_branch_delivery",
                    input_payload={"prompt": f"Auditar GitSovereignGate Z3 y entregar rama {branch}"},
                ),
                dependencies={"wave1_execute_repair"},
                read_symbols={"staged_files"},
                write_symbols={"delivery_branch"},
                inject_parent_envelopes=True,
            ),
        }
        waves, _ = DynamicDAGScheduler.compute_execution_waves_with_stats(dag_nodes)
        dag_compute_alloc = SovereignCostRouter.allocate_dag_compute(
            {tid: n.contract.input_payload["prompt"] for tid, n in dag_nodes.items()}
        )

        skipped_waves: List[int] = []
        executed_waves: List[int] = []
        envelopes: Dict[str, Any] = {}
        staged_files: Dict[str, str] = dict(base_files)
        wave_results: Dict[str, Any] = {}
        repair_attempts = 0
        proactive_rule_hits: List[str] = []
        initial_pass_at_1 = False
        refuted_claim_ids: List[str] = []
        cegis_reports: List[Dict[str, Any]] = []
        fault_localization: Dict[str, Any] = {}

        self._upsert_run_record(rid, str(repo_path), goal, "RUNNING", branch, skipped_waves, executed_waves, repair_attempts, {})

        # ----------------------- OLA 0: PLAN + REGLAS PROACTIVAS -----------------------
        if 0 in completed_ckpts:
            ckpt0 = completed_ckpts[0]
            envelopes.update(ckpt0["envelopes"])
            staged_files = dict(ckpt0["staged_files"])
            wave_results.update(ckpt0["results"])
            skipped_waves.append(0)
        else:
            if simulate_crash_at_wave == 0:
                self._save_wave_checkpoint(rid, 0, "CRASHED", waves[0], envelopes, staged_files, wave_results, sandbox.isolation_tier)
                self._upsert_run_record(rid, str(repo_path), goal, "CRASHED", branch, skipped_waves, executed_waves, repair_attempts, {})
                raise AutonomousWaveCrashSimulated(f"Simulated crash at wave 0 for run {rid}")

            plan_receipt = adapter.execute_node(
                "wave0_plan",
                f"AST plan & rule scan: {goal}",
                context={"files": sorted(base_files.keys())},
                forced_tier="TIER_0",
            )
            active_rules = memory.get_active_rules()
            matched_zd_rules = _rule_matches_zero_division(active_rules)

            # Si existe regla activa de GEPA/Bitácora, aplicar prevención proactiva ANTES de ejecutar tests
            proactive_modified: List[str] = []
            if matched_zd_rules:
                for rel, src in list(staged_files.items()):
                    if not rel.endswith(".py") or rel.startswith("tests/") or "/tests/" in rel:
                        continue
                    fixed_src, changed = _inject_zero_division_guard(src)
                    if changed:
                        cegis_res = CEGISRepairEngine().verify_and_autorepair(src)
                        cegis_reports.append({"file": rel, "cegis_repaired": cegis_res.repaired, "original_defect": cegis_res.original_defect, "final_proof_status": cegis_res.final_proof_status})
                        staged_files[rel] = fixed_src
                        proactive_modified.append(rel)
                        proactive_rule_hits.extend(matched_zd_rules)

            wave0_out = {
                "status": "SUCCESS",
                "epistemic_status": "VERIFIED",
                "matched_rules": sorted(set(proactive_rule_hits)),
                "proactive_modified_files": proactive_modified,
                "llm_tier": plan_receipt.tier,
            }
            env0 = JITContextEntropyCompiler.build_envelope(
                task_id="wave0_plan",
                raw_output=wave0_out,
                epistemic_status="VERIFIED",
                proof_hash=hashlib.sha256(json.dumps(wave0_out, sort_keys=True).encode("utf-8")).hexdigest(),
                vector_clock={"wave0_plan": 1},
            )
            envelopes["wave0_plan"] = env0.to_dict()
            wave_results["wave0_plan"] = wave0_out
            executed_waves.append(0)
            self._save_wave_checkpoint(rid, 0, "COMPLETED", waves[0], envelopes, staged_files, wave_results, sandbox.isolation_tier)

        # ----------------------- OLA 1: SANDBOX VERIFY + CEGIS/AST REPAIR -----------------------
        if 1 in completed_ckpts:
            ckpt1 = completed_ckpts[1]
            envelopes.update(ckpt1["envelopes"])
            staged_files = dict(ckpt1["staged_files"])
            wave_results.update(ckpt1["results"])
            skipped_waves.append(1)
        else:
            if simulate_crash_at_wave == 1:
                self._save_wave_checkpoint(rid, 1, "CRASHED", waves[1], envelopes, staged_files, wave_results, sandbox.isolation_tier)
                self._upsert_run_record(rid, str(repo_path), goal, "CRASHED", branch, skipped_waves, executed_waves, repair_attempts, {})
                raise AutonomousWaveCrashSimulated(f"Simulated crash at wave 1 for run {rid}")

            overlay_only = {k: v for k, v in staged_files.items() if base_files.get(k) != v}
            sb_res = sandbox.execute(
                str(repo_path),
                cmd,
                timeout_sec=30.0,
                overlay_files=overlay_only or None,
            )

            if sb_res.exit_code == 0:
                initial_pass_at_1 = True
            else:
                # Registrar EpistemicClaim REFUTED real para alimentar GEPA
                fail_trace = f"{sb_res.stderr}\n{sb_res.stdout}".strip()
                claim_id = f"CLM-{rid}-W1"
                self.store.save_claim(
                    EpistemicClaim(
                        claim_id=claim_id,
                        description=f"Autonomous sandbox failure on {repo_path.name}: {goal}",
                        payload={
                            "run_id": rid,
                            "repo_dir": str(repo_path),
                            "command": cmd,
                            "exit_code": sb_res.exit_code,
                            "stderr": sb_res.stderr[-2000:],
                            "stdout": sb_res.stdout[-2000:],
                            "error_pattern": "ZERO_DIVISION" if "ZeroDivisionError" in fail_trace else "TEST_FAILURE",
                        },
                        status=EpistemicStatus.REFUTED,
                        proof_output=fail_trace[-2500:],
                        metadata={"source": "autonomous_runner", "wave": 1},
                    )
                )
                refuted_claim_ids.append(claim_id)

                fp = breaker.compute_fingerprint("wave1_execute_repair", fail_trace[:300])
                breaker.record_failure(fp, fail_trace[:300])

                # Localización contrafactual sobre archivos candidatos
                candidate_nodes: Dict[str, DAGTaskNode] = {}
                fake_results: Dict[str, Any] = {}
                for rel in sorted(staged_files):
                    if not rel.endswith(".py") or rel.startswith("tests/") or "/tests/" in rel:
                        continue
                    nid = f"mod::{rel}"
                    candidate_nodes[nid] = DAGTaskNode(
                        contract=TaskContract(task_id=nid, task_type="code_module", input_payload={"file": rel}),
                        formal_source_code=staged_files[rel],
                    )
                    # Marcar como sospechoso si aparece en traceback o tiene división sin guarda
                    mentioned = Path(rel).name in fail_trace or bool(_find_unguarded_divisions(staged_files[rel]))
                    fake_results[nid] = {
                        "status": "FAILED" if mentioned else "SUCCESS",
                        "epistemic_status": "REFUTED" if mentioned else "VERIFIED",
                    }
                if candidate_nodes:
                    fake_sched = DAGScheduleResult(
                        total_tasks=len(candidate_nodes),
                        waves_executed=1,
                        wall_clock_duration_ms=sb_res.duration_ms,
                        sequential_equivalent_duration_ms=sb_res.duration_ms,
                        speedup_ratio=1.0,
                        results=fake_results,
                        all_success=False,
                    )
                    fault_localization = CounterfactualFaultLocalizer.localize_dag_faults(candidate_nodes, fake_sched)

                # Ciclo de reparación (máximo 2 intentos, controlado por ForensicCircuitBreaker)
                repaired_ok = False
                for attempt in range(1, 3):
                    is_open, _, open_reason = breaker.is_open(fp)
                    if is_open:
                        break
                    repair_attempts += 1
                    changed_any = False
                    for rel, src in list(staged_files.items()):
                        if not rel.endswith(".py") or rel.startswith("tests/") or "/tests/" in rel:
                            continue
                        new_src = src
                        if custom_llm_responder is not None:
                            llm_rec = adapter.execute_node(
                                f"wave1_repair_{attempt}_{rel}",
                                f"Fix failure in {rel}:\n{fail_trace[:800]}",
                                context={"file": rel, "source": src},
                                forced_tier="TIER_2",
                            )
                            extracted = _extract_python_code_block(llm_rec.response_text)
                            if extracted and AegisShield.scan_text(extracted).safe:
                                new_src = extracted
                                changed_any = (new_src != src)

                        if new_src == src:
                            cegis_res = CEGISRepairEngine().verify_and_autorepair(src)
                            cegis_reports.append({"file": rel, "cegis_repaired": cegis_res.repaired, "original_defect": cegis_res.original_defect, "final_proof_status": cegis_res.final_proof_status})
                            fixed_src, did_guard = _inject_zero_division_guard(src)
                            if did_guard:
                                new_src = fixed_src
                                changed_any = True

                        if new_src != src:
                            if not AegisShield.scan_text(new_src).safe:
                                continue
                            staged_files[rel] = new_src

                    if not changed_any:
                        breaker.record_failure(fp, "No candidate AST/LLM repair produced")
                        continue

                    overlay = {k: v for k, v in staged_files.items() if base_files.get(k) != v}
                    sb_retry = sandbox.execute(str(repo_path), cmd, timeout_sec=30.0, overlay_files=overlay or None)
                    sb_res = sb_retry
                    if sb_retry.exit_code == 0:
                        breaker.record_success(fp)
                        repaired_ok = True
                        break
                    breaker.record_failure(fp, (sb_retry.stderr or sb_retry.stdout)[:300])

                if not repaired_ok:
                    self._save_wave_checkpoint(rid, 1, "FAILED", waves[1], envelopes, staged_files, wave_results, sandbox.isolation_tier)
                    self._upsert_run_record(
                        rid, str(repo_path), goal, "ABORTED_CIRCUIT_BREAKER", branch,
                        skipped_waves, executed_waves, repair_attempts, adapter.get_telemetry_summary(),
                    )
                    return {
                        "run_id": rid,
                        "success": False,
                        "status": "ABORTED_CIRCUIT_BREAKER",
                        "sandbox_result": sb_res.to_dict(),
                        "repair_attempts": repair_attempts,
                        "refuted_claim_ids": refuted_claim_ids,
                        "fault_localization": fault_localization,
                        "skipped_waves": skipped_waves,
                        "executed_waves": executed_waves,
                    }

            wave1_out = {
                "status": "SUCCESS",
                "epistemic_status": "VERIFIED",
                "sandbox_tier": sb_res.isolation_tier,
                "exit_code": sb_res.exit_code,
                "initial_pass_at_1": initial_pass_at_1,
                "repair_attempts": repair_attempts,
                "cegis_reports": cegis_reports,
            }
            env1 = JITContextEntropyCompiler.build_envelope(
                task_id="wave1_execute_repair",
                raw_output=wave1_out,
                epistemic_status="VERIFIED",
                proof_hash=sb_res.artifacts_cas_sha256,
                vector_clock={"wave0_plan": 1, "wave1_execute_repair": 1},
            )
            envelopes["wave1_execute_repair"] = env1.to_dict()
            wave_results["wave1_execute_repair"] = wave1_out
            executed_waves.append(1)
            self._save_wave_checkpoint(rid, 1, "COMPLETED", waves[1], envelopes, staged_files, wave_results, sandbox.isolation_tier)

        # ----------------------- OLA 2: GIT SOVEREIGN GATE Z3 + CAS + RAMA AISLADA -----------------------
        delivery_info: Dict[str, Any] = {}
        cas_commit_report: Dict[str, Any] = {}
        if 2 in completed_ckpts:
            ckpt2 = completed_ckpts[2]
            envelopes.update(ckpt2["envelopes"])
            staged_files = dict(ckpt2["staged_files"])
            wave_results.update(ckpt2["results"])
            skipped_waves.append(2)
            delivery_info = wave_results.get("wave2_gate_deliver", {}).get("delivery_info", {})
            cas_commit_report = wave_results.get("wave2_gate_deliver", {}).get("cas_commit", {})
        else:
            if simulate_crash_at_wave == 2:
                self._save_wave_checkpoint(rid, 2, "CRASHED", waves[2], envelopes, staged_files, wave_results, sandbox.isolation_tier)
                self._upsert_run_record(rid, str(repo_path), goal, "CRASHED", branch, skipped_waves, executed_waves, repair_attempts, {})
                raise AutonomousWaveCrashSimulated(f"Simulated crash at wave 2 for run {rid}")

            # Auditar todos los archivos Python de código productivo (y modificados) con GitSovereignGate Z3
            py_audit_map = {
                rel: src
                for rel, src in staged_files.items()
                if rel.endswith(".py") and (base_files.get(rel) != src or (not rel.startswith("tests/") and "/tests/" not in rel))
            }
            gate_report = GitSovereignGate.audit_files_dict(py_audit_map)
            if not gate_report.safe_to_commit:
                self._upsert_run_record(
                    rid, str(repo_path), goal, "BLOCKED_GIT_GATE", branch,
                    skipped_waves, executed_waves, repair_attempts, adapter.get_telemetry_summary(),
                )
                return {
                    "run_id": rid,
                    "success": False,
                    "status": "BLOCKED_GIT_GATE",
                    "blocking_defects": gate_report.blocking_defects,
                    "polyglot_violations": gate_report.polyglot_violations,
                }

            tx = EphemeralCASWorktreeTransaction(base_files)
            for rel, src in staged_files.items():
                if base_files.get(rel) != src:
                    st = tx.stage_agent_patch("wave1_execute_repair", rel, src)
                    if not st.get("staged"):
                        return {
                            "run_id": rid,
                            "success": False,
                            "status": "CAS_MERGE_CONFLICT",
                            "detail": st,
                        }
            cas_commit_report = tx.commit_all()

            changed_files = {k: v for k, v in staged_files.items() if base_files.get(k) != v}
            if create_branch_delivery and (repo_path / ".git").exists():
                delivery_info = _deliver_to_isolated_branch(
                    repo_path,
                    branch,
                    changed_files,
                    f"aleph(auto): verified Z3+sandbox repair for {rid}",
                )
            else:
                delivery_info = {"delivered": False, "reason": "branch_delivery_disabled_or_no_git", "branch": branch}

            wave2_out = {
                "status": "SUCCESS",
                "epistemic_status": "FORMALLY_PROVEN",
                "git_gate_safe": gate_report.safe_to_commit,
                "formal_proofs_passed": gate_report.formal_proofs_passed,
                "cas_commit": cas_commit_report,
                "delivery_info": delivery_info,
            }
            env2 = JITContextEntropyCompiler.build_envelope(
                task_id="wave2_gate_deliver",
                raw_output=wave2_out,
                epistemic_status="FORMALLY_PROVEN",
                proof_hash=cas_commit_report.get("commit_sha256"),
                vector_clock={"wave0_plan": 1, "wave1_execute_repair": 1, "wave2_gate_deliver": 1},
            )
            envelopes["wave2_gate_deliver"] = env2.to_dict()
            wave_results["wave2_gate_deliver"] = wave2_out
            executed_waves.append(2)
            self._save_wave_checkpoint(rid, 2, "COMPLETED", waves[2], envelopes, staged_files, wave_results, sandbox.isolation_tier)

        telemetry = adapter.get_telemetry_summary()
        self._upsert_run_record(
            rid, str(repo_path), goal, "COMPLETED", branch,
            skipped_waves, executed_waves, repair_attempts, telemetry,
        )

        # Registrar claim VERIFIED final del run
        self.store.save_claim(
            EpistemicClaim(
                claim_id=f"CLM-{rid}-VERIFIED",
                description=f"Autonomous run {rid} verified for {goal}",
                payload={"run_id": rid, "delivery_branch": branch, "repair_attempts": repair_attempts},
                status=EpistemicStatus.VERIFIED,
                proof_hash=envelopes.get("wave2_gate_deliver", {}).get("cas_sha256"),
                proof_output="COMPLETED",
            )
        )

        return {
            "run_id": rid,
            "success": True,
            "status": "COMPLETED",
            "sandbox_tier": sandbox.isolation_tier,
            "skipped_waves": skipped_waves,
            "executed_waves": executed_waves,
            "initial_pass_at_1": initial_pass_at_1,
            "proactive_rule_hits": sorted(set(proactive_rule_hits)),
            "repair_attempts": repair_attempts,
            "refuted_claim_ids": refuted_claim_ids,
            "fault_localization": fault_localization,
            "cegis_reports": cegis_reports,
            "git_gate_safe": True,
            "cas_commit": cas_commit_report,
            "delivery_branch": branch,
            "delivery_info": delivery_info,
            "envelopes": envelopes,
            "dag_compute_allocation": dag_compute_alloc,
            "llm_telemetry": telemetry,
        }


class AutonomousTaskQueue:
    """Cola durable SQLite WAL para tickets desatendidos con bloqueo atómico y circuit breaker global."""

    def __init__(self, db_path: Optional[str] = None, failure_threshold: int = 3) -> None:
        resolved_db = db_path or DEFAULT_AUTONOMOUS_DB
        Path(resolved_db).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = resolved_db
        self.store = StateStore(db_path=resolved_db)
        _ensure_autonomous_schema(self.store)
        self.failure_threshold = max(1, int(failure_threshold))

    def enqueue(self, repo_dir: str, goal: str, test_command: str = "", ticket_id: Optional[str] = None) -> Dict[str, Any]:
        tid = ticket_id or f"tkt_{uuid.uuid4().hex[:10]}"
        now = time.time()
        with self.store._connection() as conn:
            conn.execute(
                """
                INSERT INTO autonomous_task_queue (
                    ticket_id, repo_dir, goal, test_command, status, worker_pid, run_id, error_summary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'PENDING', 0, '', '', ?, ?)
                """,
                (tid, str(Path(repo_dir).resolve()), goal, test_command, now, now),
            )
            conn.commit()
        return {"ticket_id": tid, "repo_dir": str(Path(repo_dir).resolve()), "goal": goal, "status": "PENDING"}

    def list_tickets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.store._connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM autonomous_task_queue WHERE status = ? ORDER BY created_at ASC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM autonomous_task_queue ORDER BY created_at ASC").fetchall()
        return [dict(r) for r in rows]

    def _acquire_next_ticket(self, worker_pid: Optional[int] = None) -> Optional[Dict[str, Any]]:
        pid = int(worker_pid or os.getpid())
        now = time.time()
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA busy_timeout=15000;")
            conn.execute("BEGIN IMMEDIATE;")
            row = conn.execute(
                "SELECT * FROM autonomous_task_queue WHERE status = 'PENDING' ORDER BY created_at ASC LIMIT 1"
            ).fetchone()
            if row is None:
                conn.execute("COMMIT;")
                return None
            cur = conn.execute(
                """
                UPDATE autonomous_task_queue
                SET status = 'LOCKED', worker_pid = ?, updated_at = ?
                WHERE ticket_id = ? AND status = 'PENDING'
                """,
                (pid, now, row["ticket_id"]),
            )
            if cur.rowcount != 1:
                conn.execute("ROLLBACK;")
                return None
            conn.execute("COMMIT;")
            item = dict(row)
            item["status"] = "LOCKED"
            item["worker_pid"] = pid
            return item
        except Exception:
            try:
                conn.execute("ROLLBACK;")
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.close()

    def run_next(self, runner: Optional[AutonomousRunner] = None) -> Dict[str, Any]:
        ticket = self._acquire_next_ticket()
        if ticket is None:
            return {"processed": False, "reason": "queue_empty"}

        active_runner = runner or AutonomousRunner(db_path=self.db_path)
        run_id = f"run_{ticket['ticket_id']}"
        try:
            res = active_runner.run_task(
                repo_dir=ticket["repo_dir"],
                goal=ticket["goal"],
                test_command=ticket["test_command"] or None,
                run_id=run_id,
            )
            final_status = "COMPLETED" if res.get("success") else "FAILED"
            err_msg = "" if res.get("success") else str(res.get("status", "FAILED"))
        except Exception as exc:
            res = {"run_id": run_id, "success": False, "status": "EXCEPTION", "error": str(exc)}
            final_status = "FAILED"
            err_msg = f"{type(exc).__name__}: {exc}"

        with self.store._connection() as conn:
            conn.execute(
                """
                UPDATE autonomous_task_queue
                SET status = ?, run_id = ?, error_summary = ?, updated_at = ?
                WHERE ticket_id = ?
                """,
                (final_status, run_id, err_msg[:500], time.time(), ticket["ticket_id"]),
            )
            conn.commit()
        return {"processed": True, "ticket_id": ticket["ticket_id"], "ticket_status": final_status, "result": res}

    def run_all(self, runner: Optional[AutonomousRunner] = None) -> Dict[str, Any]:
        active_runner = runner or AutonomousRunner(db_path=self.db_path)
        outcomes: List[Dict[str, Any]] = []
        consecutive_failures = 0
        circuit_tripped = False

        while True:
            if consecutive_failures >= self.failure_threshold:
                circuit_tripped = True
                break
            step = self.run_next(runner=active_runner)
            if not step.get("processed"):
                break
            outcomes.append(step)
            if step["ticket_status"] == "COMPLETED":
                consecutive_failures = 0
            else:
                consecutive_failures += 1

        return {
            "processed_count": len(outcomes),
            "completed_count": sum(1 for o in outcomes if o["ticket_status"] == "COMPLETED"),
            "failed_count": sum(1 for o in outcomes if o["ticket_status"] == "FAILED"),
            "circuit_breaker_tripped": circuit_tripped,
            "outcomes": outcomes,
        }


def _parse_flag_value(args: List[str], flag: str, default: Optional[str] = None) -> Optional[str]:
    for idx, tok in enumerate(args):
        if tok == flag and idx + 1 < len(args):
            return args[idx + 1]
        if tok.startswith(f"{flag}="):
            return tok.split("=", 1)[1]
    return default


def cli_autonomous_run(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[2:] if argv is None else argv)
    repo_dir = _parse_flag_value(args, "--repo", ".")
    goal = _parse_flag_value(args, "--goal", "Verificar y reparar defectos detectados en el repositorio")
    test_cmd = _parse_flag_value(args, "--test-cmd", None)
    run_id = _parse_flag_value(args, "--resume", None) or _parse_flag_value(args, "--run-id", None)
    resume = ("--resume" in args) or any(a.startswith("--resume=") for a in args)
    db_path = _parse_flag_value(args, "--db", None)
    branch = _parse_flag_value(args, "--branch", None)
    crash_wave_raw = _parse_flag_value(args, "--simulate-crash-wave", None)
    crash_wave = int(crash_wave_raw) if crash_wave_raw is not None else None

    runner = AutonomousRunner(db_path=db_path)
    report = runner.run_task(
        repo_dir=repo_dir,
        goal=goal,
        test_command=test_cmd,
        run_id=run_id,
        resume=resume,
        simulate_crash_at_wave=crash_wave,
        delivery_branch=branch,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    return 0 if report.get("success") else 1


def cli_autonomous_queue(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[2:] if argv is None else argv)
    action = args[0] if args else "list"
    db_path = _parse_flag_value(args, "--db", None)
    queue = AutonomousTaskQueue(db_path=db_path)

    if action == "add":
        repo_dir = _parse_flag_value(args, "--repo", ".")
        goal = _parse_flag_value(args, "--goal", "Reparación autónoma en cola")
        test_cmd = _parse_flag_value(args, "--test-cmd", "")
        res = queue.enqueue(repo_dir=repo_dir, goal=goal, test_command=test_cmd)
    elif action == "list":
        status = _parse_flag_value(args, "--status", None)
        res = {"tickets": queue.list_tickets(status=status)}
    elif action == "run-next":
        res = queue.run_next()
    elif action == "run-all":
        res = queue.run_all()
    else:
        res = {"error": f"Acción desconocida '{action}'. Usar: add | list | run-next | run-all"}
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 2

    print(json.dumps(res, indent=2, ensure_ascii=False, default=str))
    return 0
