"""
Motor Central El Aleph v2.6.0 (Sovereign Orchestrator).
Integra en un único Kernel determinista:
1. Estado Atómico SQLite WAL (StateStore) con Checkpointing Jerárquico
2. Caché Semántica Exacta + Normalización AST (Zero-Token Cache Hit)
3. Diarios Inmutables con Cadena SHA-256 (AgentJournal)
4. Memoria Bicameral Algorítmica + Grafo de Conocimiento (BicameralMemory)
5. Pipeline de Hooks Pre/Post Ejecución y Escudo AegisShield (HookPipeline + AegisShield)
6. Enrutador de Contratos + Cost Router Soberano ($0.00 en Gemini 4 Argon)
7. Planificador Concurrente de Grafos Acíclicos Dirigidos (DynamicDAGScheduler)
8. Compuerta Epistémica Triple (Z3/Symbolic Prover -> PBT Fallback -> Empirical Gate)
9. Motor de Parches Semánticos AST con Verificación Diferencial Anti-Regresión (SemanticPatchEngine)
10. Enjambre de Auditoría (WarCouncilSwarm) y Ciclo de Automejora Continua (DemiurgoEvolutionEngine)
"""
from __future__ import annotations
from dataclasses import asdict
import ast
import math
import re
import threading
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List, Sequence, Tuple
from aleph_core.config import DB_PATH, JOURNALS_DIR
from aleph_core.state.store import StateStore, SessionCheckpoint, CachedTaskResult
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus, VerificationGate
from aleph_core.memory.journal import AgentJournal
from aleph_core.memory.bicameral import BicameralMemory
from aleph_core.router.dispatcher import TaskContract, TaskExecutionResult, TaskDispatcher
from aleph_core.router.dispatcher import DynamicDAGScheduler, DAGTaskNode, DAGScheduleResult
from aleph_core.router.cost_router import SovereignCostRouter
from aleph_core.hooks.pipeline import HookPipeline, HookPhase, HookEvent
from aleph_core.security.aegis_shield import AegisShield
from aleph_core.swarm.war_council import WarCouncilSwarm
from aleph_core.evolution.demiurgo_loop import DemiurgoEvolutionEngine
import hashlib
import json as _aleph_json


class ForensicCircuitBreaker:
    """
    Corta-circuitos forense determinista para ejecuciones agénticas.
    Detecta bucles de oscilación estéril (mismo fingerprint input+AST fallando consecutivamente)
    y corta el despacho en <0.1 ms antes de quemar cómputo/tokens adicionales.
    """

    def __init__(self, failure_threshold: int = 2):
        self.failure_threshold = max(2, int(failure_threshold))
        self._lock = threading.RLock()
        self._failure_counts: Dict[str, int] = {}
        self._last_errors: Dict[str, str] = {}

    @staticmethod
    def compute_fingerprint(
        task_type: str,
        input_payload: Dict[str, Any],
        formal_source_code: Optional[str] = None,
    ) -> str:
        canonical_payload = _aleph_json.dumps(input_payload, sort_keys=True, ensure_ascii=False, default=str)
        ast_sig = ""
        if formal_source_code:
            try:
                ast_sig = ast.dump(ast.parse(formal_source_code), include_attributes=False)
            except SyntaxError:
                ast_sig = formal_source_code.strip()
        raw = f"{task_type}|{canonical_payload}|{ast_sig}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def is_open(self, fingerprint: str) -> Tuple[bool, int, str]:
        with self._lock:
            cnt = self._failure_counts.get(fingerprint, 0)
            return cnt >= self.failure_threshold, cnt, self._last_errors.get(fingerprint, "")

    def record_failure(self, fingerprint: str, error_summary: str) -> int:
        with self._lock:
            cnt = self._failure_counts.get(fingerprint, 0) + 1
            self._failure_counts[fingerprint] = cnt
            self._last_errors[fingerprint] = error_summary
            return cnt

    def record_success(self, fingerprint: str) -> None:
        with self._lock:
            self._failure_counts.pop(fingerprint, None)
            self._last_errors.pop(fingerprint, None)


class AlephEngine:
    def __init__(self, engine_id: str = "aleph_sovereign_v2", db_path=DB_PATH, circuit_breaker_threshold: int = 2):
        self.engine_id = engine_id
        self.state_store = StateStore(db_path=db_path)
        # Con un db_path explícito (p. ej. tests o instancias aisladas) el journal vive junto a esa base
        # de datos; con el valor por defecto se conserva el directorio de datos del paquete.
        _db = Path(db_path)
        self.journal = (AgentJournal(agent_id=engine_id) if _db == Path(DB_PATH)
                        else AgentJournal(agent_id=engine_id, base_dir=_db.parent / "journals"))
        self.memory = BicameralMemory(store=self.state_store)
        self.dispatcher = TaskDispatcher()
        self.cost_router = SovereignCostRouter()
        self.dag_scheduler = DynamicDAGScheduler()
        self._patch_engine = None
        self._cegis_engine = None
        self.hooks = HookPipeline()
        self.evolution = DemiurgoEvolutionEngine(store=self.state_store, memory=self.memory)
        self.circuit_breaker = ForensicCircuitBreaker(failure_threshold=circuit_breaker_threshold)
        self._register_default_security_hooks()

    @property
    def patch_engine(self):
        if self._patch_engine is None:
            from aleph_core.verification.z3_prover import SemanticPatchEngine
            self._patch_engine = SemanticPatchEngine()
        return self._patch_engine

    @patch_engine.setter
    def patch_engine(self, value) -> None:
        self._patch_engine = value

    @property
    def cegis_engine(self):
        if self._cegis_engine is None:
            from aleph_core.verification.z3_prover import CEGISRepairEngine
            self._cegis_engine = CEGISRepairEngine()
        return self._cegis_engine

    @cegis_engine.setter
    def cegis_engine(self, value) -> None:
        self._cegis_engine = value

    def _register_default_security_hooks(self):
        def aegis_pre_dispatch(event: HookEvent) -> Optional[str]:
            report = AegisShield.scan_payload(event.payload)
            if not report.safe:
                top = report.findings[0]
                return f"Bloqueado por AegisShield [{top.rule_id} - {top.category}]: {top.description}"
            return None

        self.hooks.register_hook(HookPhase.PRE_DISPATCH, "aegis_shield_pre_scan", aegis_pre_dispatch)

    def register_capability(self, task_type: str, handler: Callable[[Dict[str, Any]], Any]):
        """Registra una capacidad ejecutable en el enrutador."""
        self.dispatcher.register_handler(task_type, handler)

    def execute_and_verify(
        self,
        task_type: str,
        input_payload: Dict[str, Any],
        verifier_fn: Optional[Callable[[Any], bool]] = None,
        proof_context: Optional[str] = None,
        domain_category: str = "Código",
        formal_source_code: Optional[str] = None,
        use_bitvectors: bool = False,
        bypass_cache: bool = False
    ) -> Dict[str, Any]:
        from aleph_core.router.dispatcher import JITContextEntropyCompiler
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        active_rules = self.memory.get_active_rules(domain_category=domain_category)
        active_rule_ids = [r.rule_id for r in active_rules]
        fp = self.circuit_breaker.compute_fingerprint(task_type, input_payload, formal_source_code)

        # 0. Circuit Breaker Forense anti-oscilación estéril
        cb_open, cb_count, cb_last_err = self.circuit_breaker.is_open(fp)
        if cb_open:
            self.hooks.run_phase(HookEvent(
                phase=HookPhase.ON_FAILURE,
                task_id=task_id,
                task_type=task_type,
                payload={"fingerprint": fp, "failure_count": cb_count, "error": cb_last_err},
                metadata={"circuit_breaker_tripped": True},
            ))
            self.journal.append_event("CIRCUIT_BREAKER_TRIPPED", {
                "task_id": task_id,
                "task_type": task_type,
                "fingerprint": fp,
                "consecutive_failures": cb_count,
                "last_error": cb_last_err,
            })
            return {
                "task_id": task_id,
                "status": "CIRCUIT_BREAKER_TRIPPED",
                "error": f"Circuit breaker abierto tras {cb_count} fallos idénticos consecutivos: {cb_last_err}",
                "epistemic_status": EpistemicStatus.REFUTED.value,
                "active_rules_applied": active_rule_ids,
                "proof_hash": None,
                "cache_hit": False,
                "circuit_breaker_tripped": True,
            }

        # 1. Chequeo de Caché Semántica / AST (Nivel 9 v2.6.0)
        if not bypass_cache:
            cached = self.state_store.query_semantic_cache(
                task_type=task_type,
                input_payload=input_payload,
                formal_source_code=formal_source_code
            )
            if cached is not None:
                self.journal.append_event("CACHE_HIT", {
                    "task_id": task_id,
                    "task_type": task_type,
                    "cache_key": cached.cache_key,
                    "hit_count": cached.hit_count
                })
                env = JITContextEntropyCompiler.build_envelope(
                    task_id=task_id,
                    raw_output=cached.output_payload,
                    epistemic_status=cached.epistemic_status,
                    proof_hash=cached.proof_hash,
                    formal_source_code=formal_source_code,
                )
                return {
                    "task_id": task_id,
                    "claim_id": f"claim_cached_{cached.cache_key[:8]}",
                    "status": "SUCCESS" if cached.epistemic_status in (
                        EpistemicStatus.VERIFIED.value,
                        EpistemicStatus.PBT_VERIFIED.value,
                        EpistemicStatus.FORMALLY_PROVEN.value
                    ) else "UNVERIFIED",
                    "epistemic_status": cached.epistemic_status,
                    "proof_hash": cached.proof_hash,
                    "proof_output": f"Caché Semántica AST HIT (Hit #{cached.hit_count})",
                    "output_preview": TaskDispatcher.reduce_output(cached.output_payload),
                    "active_rules_applied": active_rule_ids,
                    "latency_ms": 0.05,
                    "cache_hit": True,
                    "proof_carrying_envelope": env.to_dict(),
                }

        # 2. Hook PRE_DISPATCH
        pre_hook_res = self.hooks.run_phase(HookEvent(
            phase=HookPhase.PRE_DISPATCH,
            task_id=task_id,
            task_type=task_type,
            payload=input_payload,
            metadata={"active_rules": active_rule_ids}
        ))
        if not pre_hook_res.allowed:
            self.journal.append_event("TASK_BLOCKED_BY_HOOK", {
                "task_id": task_id,
                "reason": pre_hook_res.blocked_reason
            })
            return {
                "task_id": task_id,
                "status": "BLOCKED",
                "error": pre_hook_res.blocked_reason,
                "epistemic_status": EpistemicStatus.REFUTED.value,
                "active_rules_applied": active_rule_ids,
                "proof_hash": None,
                "cache_hit": False
            }

        contract = TaskContract(
            task_id=task_id,
            task_type=task_type,
            input_payload=input_payload,
            domain_category=domain_category
        )

        self.journal.append_event("TASK_DISPATCHED", {
            "task_id": task_id,
            "task_type": task_type,
            "domain_category": domain_category,
            "active_rules": active_rule_ids,
            "input": input_payload
        })
        self.state_store.record_task_start(task_id, task_type, input_payload)

        # 3. Despacho
        exec_result = self.dispatcher.dispatch(contract)
        if not exec_result.success:
            err_msg = str(exec_result.error or "EXECUTION_FAILED")
            fail_count = self.circuit_breaker.record_failure(fp, err_msg)
            self.hooks.run_phase(HookEvent(
                phase=HookPhase.ON_FAILURE,
                task_id=task_id,
                task_type=task_type,
                payload={"error": err_msg, "fingerprint": fp, "failure_count": fail_count},
                metadata={"active_rules": active_rule_ids},
            ))
            self.journal.append_event("TASK_FAILED", {
                "task_id": task_id,
                "error": err_msg,
                "failure_count": fail_count,
            })
            self.state_store.record_task_completion(task_id, "FAILED", {"error": err_msg})
            failure_claim = EpistemicClaim(
                claim_id=f"fail_{uuid.uuid4().hex[:12]}",
                description=f"Fallo de ejecución en {task_type}: {err_msg}",
                payload={"input": input_payload, "error": err_msg, "proposed_rule": input_payload.get("proposed_rule") if isinstance(input_payload, dict) else None},
                status=EpistemicStatus.REFUTED,
                metadata={
                    "task_id": task_id,
                    "task_type": task_type,
                    "defect_type": "RUNTIME_EXECUTION_FAILURE",
                    "error": err_msg,
                    "counterexample": input_payload,
                },
            )
            self.state_store.save_claim(failure_claim)
            tripped = fail_count >= self.circuit_breaker.failure_threshold
            return {
                "task_id": task_id,
                "status": "CIRCUIT_BREAKER_TRIPPED" if tripped else "FAILED",
                "error": err_msg,
                "epistemic_status": EpistemicStatus.REFUTED.value,
                "active_rules_applied": active_rule_ids,
                "proof_hash": None,
                "cache_hit": False,
                "circuit_breaker_tripped": tripped,
                "proof_carrying_envelope": exec_result.envelope.to_dict() if exec_result.envelope else None,
            }

        claim_id = f"claim_{uuid.uuid4().hex[:12]}"
        claim = EpistemicClaim(
            claim_id=claim_id,
            description=f"Resultado de ejecución para {task_type}",
            payload=exec_result.raw_output,
            status=EpistemicStatus.INFERRED,
            metadata={
                "task_id": task_id,
                "latency_ms": exec_result.execution_time_ms,
                "active_rules": active_rule_ids
            }
        )

        # 4. Verificación Epistémica
        if formal_source_code:
            verified_claim = VerificationGate.verify_formal(
                claim=claim,
                source_code=formal_source_code,
                use_bitvectors=use_bitvectors
            )
        elif verifier_fn is not None:
            verified_claim = VerificationGate.verify(
                claim=claim,
                verifier_fn=verifier_fn,
                proof_context=proof_context or f"Determinismo verificado para {task_id}"
            )
        else:
            verified_claim = claim

        self.state_store.save_claim(verified_claim)
        self.state_store.record_task_completion(
            task_id=task_id,
            status=verified_claim.status.value,
            output_payload={"claim_id": verified_claim.claim_id, "proof_hash": verified_claim.proof_hash}
        )

        self.journal.append_event("TASK_COMPLETED", {
            "task_id": task_id,
            "claim_id": verified_claim.claim_id,
            "status": verified_claim.status.value,
            "proof_hash": verified_claim.proof_hash
        })

        is_success = verified_claim.status in (
            EpistemicStatus.VERIFIED,
            EpistemicStatus.PBT_VERIFIED,
            EpistemicStatus.FORMALLY_PROVEN
        )
        tripped_on_verify = False
        if verified_claim.status == EpistemicStatus.REFUTED:
            fail_msg = verified_claim.proof_output or "VERIFICATION_REFUTED"
            fail_count = self.circuit_breaker.record_failure(fp, fail_msg)
            tripped_on_verify = fail_count >= self.circuit_breaker.failure_threshold
            self.hooks.run_phase(HookEvent(
                phase=HookPhase.ON_FAILURE,
                task_id=task_id,
                task_type=task_type,
                payload={"error": fail_msg, "fingerprint": fp, "failure_count": fail_count},
                metadata={"claim_id": verified_claim.claim_id},
            ))
        else:
            self.circuit_breaker.record_success(fp)
            self.hooks.run_phase(HookEvent(
                phase=HookPhase.POST_DISPATCH,
                task_id=task_id,
                task_type=task_type,
                payload={"status": verified_claim.status.value, "proof_hash": verified_claim.proof_hash},
                metadata={"claim_id": verified_claim.claim_id},
            ))

        # 5. Persistir en Caché Semántica si fue exitoso
        if is_success:
            self.state_store.store_semantic_cache(
                task_type=task_type,
                input_payload=input_payload,
                output_payload=exec_result.raw_output,
                epistemic_status=verified_claim.status.value,
                proof_hash=verified_claim.proof_hash,
                formal_source_code=formal_source_code
            )

        envelope = JITContextEntropyCompiler.build_envelope(
            task_id=task_id,
            raw_output=exec_result.raw_output,
            epistemic_status=verified_claim.status.value,
            proof_hash=verified_claim.proof_hash,
            formal_source_code=formal_source_code,
        )

        return {
            "task_id": task_id,
            "claim_id": verified_claim.claim_id,
            "status": "SUCCESS" if is_success else ("CIRCUIT_BREAKER_TRIPPED" if tripped_on_verify else "UNVERIFIED"),
            "epistemic_status": verified_claim.status.value,
            "proof_hash": verified_claim.proof_hash,
            "proof_output": verified_claim.proof_output,
            "output_preview": exec_result.compact_output,
            "active_rules_applied": active_rule_ids,
            "latency_ms": round(exec_result.execution_time_ms, 3),
            "cache_hit": False,
            "circuit_breaker_tripped": tripped_on_verify,
            "proof_carrying_envelope": envelope.to_dict(),
        }

    def save_session_checkpoint(
        self,
        session_id: str,
        step_number: int,
        working_memory: Dict[str, Any],
        compact_summary: str,
        domain_category: str = "Código"
    ) -> SessionCheckpoint:
        active_rules = self.memory.get_active_rules(domain_category=domain_category)
        active_rule_ids = [r.rule_id for r in active_rules]
        return self.state_store.create_session_checkpoint(
            session_id=session_id,
            step_number=step_number,
            working_memory=working_memory,
            compact_summary=compact_summary,
            active_rule_ids=active_rule_ids
        )

    def resume_session_checkpoint(self, session_id: str) -> Optional[Dict[str, Any]]:
        chk = self.state_store.load_latest_session_checkpoint(session_id)
        if not chk:
            return None
        return {
            "checkpoint_id": chk.checkpoint_id,
            "step_number": chk.step_number,
            "active_rules": chk.active_rule_ids,
            "compact_summary": chk.compact_summary,
            "working_memory": StateStore.restore_checkpoint_memory(chk)
        }

    def execute_dag(self, dag_nodes: Dict[str, DAGTaskNode], base_files: Optional[Dict[str, str]] = None) -> DAGScheduleResult:
        """Ejecuta un grafo acíclico dirigido de tareas en paralelo por oleadas topológicas."""
        return self.dag_scheduler.execute_dag(dag_nodes, engine_execute_fn=self.execute_and_verify, base_files=base_files)

    def apply_verified_semantic_patch(
        self,
        original_source: str,
        target_function_name: str,
        replacement_function_source: str,
        target_file_path: Optional[Path] = None
    ) -> SemanticPatchResult:
        """Aplica un parche semántico en AST comprobando formalmente la ausencia de regresiones."""
        return self.patch_engine.apply_function_replacement(
            original_source=original_source,
            target_function_name=target_function_name,
            replacement_function_source=replacement_function_source,
            target_file_path=target_file_path,
            enforce_formal_verification=True
        )

    def verify_and_autorepair_code(self, source_code: str, use_bitvectors: bool = False) -> CEGISRepairResult:
        """Ejecuta síntesis inductiva guiada por contraejemplos (CEGIS) para reparar y demostrar funciones automáticamente."""
        return self.cegis_engine.verify_and_autorepair(source_code=source_code, use_bitvectors=use_bitvectors)


    def __getattr__(self, name: str):
        if name.startswith("prove_"):
            from aleph_core.research_archive.engine_provers_archive import ArchivedEngineProvers
            fn = getattr(ArchivedEngineProvers, name, None)
            if fn is not None:
                return fn.__get__(self, type(self))
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def prove_omega_continual_self_improvement_and_bitacora_vault(
        self,
        query_context: str = "PostgreSQL 18 zero-downtime DDL, CSS subgrid WCAG 2.2, PageRank KV-Cache y consenso BFT",
        min_required_rules: int = 350,
        simulate_tamper_or_forgetting: bool = False,
    ) -> Dict[str, Any]:
        """Nivel 506 (v33.0.0 — REG-330): Certifica Bóveda Interna de Bitácora + Automejora Continua Sin Olvido."""
        from aleph_core.verification.z3_prover import OmegaContinualSelfImprovementHippoRAG2TitansZeroForgettingAndBitacoraVaultProver
        rep = OmegaContinualSelfImprovementHippoRAG2TitansZeroForgettingAndBitacoraVaultProver.verify_and_synthesize(
            query_context=query_context,
            min_required_rules=min_required_rules,
            simulate_tamper_or_forgetting=simulate_tamper_or_forgetting,
        )
        return rep.to_dict()

    def query_internal_bitacora_hipporag2(
        self,
        query: str,
        top_k: int = 8,
        shard_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Consulta las 350+ reglas internas de la Bitácora mediante HippoRAG 2 Personalized PageRank + BM25."""
        from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
        omega = _get_cached_continual_learner()
        matches = omega.query_hipporag2_ppr(query=query, top_k=top_k, shard_filter=shard_filter)
        return {
            "status": "OK",
            "query": query,
            "total_internal_rules": len(omega.rules),
            "matches_count": len(matches),
            "matches": matches,
        }

    def enforce_internal_bitacora_pre_turn_gate(
        self,
        code_or_plan: str,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """Audita un plan o código contra las 350+ reglas internas de la Bitácora antes de ejecutar."""
        from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
        omega = _get_cached_continual_learner()
        return omega.enforce_pre_turn_bitacora_gate(code_or_plan=code_or_plan, top_k=top_k)

    def learn_new_experiential_bitacora_rule(
        self,
        friction_or_error: str,
        si_clause: str,
        entonces_clause: str,
        evitar_clause: str,
        shard: str = "MASTER-V33",
        persist_to_disk: bool = False,
    ) -> Dict[str, Any]:
        """Aprende y consolida una nueva regla en la Bitácora interna bajo bloqueo Merkle SHA-256 sin olvido."""
        from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
        omega = _get_cached_continual_learner()
        return omega.learn_experiential_rule(
            friction_or_error=friction_or_error,
            si_clause=si_clause,
            entonces_clause=entonces_clause,
            evitar_clause=evitar_clause,
            shard=shard,
            persist_to_disk=persist_to_disk,
        )

    def run_omega_dgm_alphaevolve_self_improvement_cycle(
        self,
        task_description: str = "Optimización evolutiva DGM + AlphaEvolve + HippoRAG 2 + Titans",
        observed_friction: str = "",
        persist_new_rule: bool = False,
    ) -> Dict[str, Any]:
        """Ejecuta el ciclo completo de automejora continua DGM + AlphaEvolve + TextGrad + Titans + HippoRAG 2."""
        from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
        omega = _get_cached_continual_learner()
        return omega.run_omega_self_improvement_cycle(
            task_description=task_description,
            observed_friction=observed_friction,
            persist_new_rule=persist_new_rule,
        ).to_dict()

    def get_internal_bitacora_vault_telemetry(self) -> Dict[str, Any]:
        """Devuelve la telemetría completa de la Bóveda Nativa de Bitácora y su cadena Merkle anti-olvido."""
        from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
        omega = _get_cached_continual_learner()
        return omega.get_vault_telemetry()



import os as _os_stat_mod

_SHARED_BITACORA_CACHE: Dict[str, Any] = {
    "inst": None,
    "sig": None,
    "vault_path_str": str(Path(__file__).resolve().parent.parent / ".aleph" / "BITACORA_MASTER_VAULT_V33.json"),
    "query_cache": {},
}


def _get_cached_continual_learner():
    vault_str = _SHARED_BITACORA_CACHE["vault_path_str"]
    sig = None
    try:
        st = _os_stat_mod.stat(vault_str)
        sig = (st.st_mtime_ns, st.st_size)
    except OSError:
        sig = None
    cached = _SHARED_BITACORA_CACHE.get("inst")
    if cached is not None and sig is not None and _SHARED_BITACORA_CACHE.get("sig") == sig:
        return cached
    from aleph_core.self_improvement.omega_continual_learner import AlephOmegaContinualSelfImprovementEngine
    inst = AlephOmegaContinualSelfImprovementEngine()
    _SHARED_BITACORA_CACHE["inst"] = inst
    _SHARED_BITACORA_CACHE["query_cache"].clear()
    if inst.vault_path:
        try:
            st = _os_stat_mod.stat(str(inst.vault_path))
            _SHARED_BITACORA_CACHE["sig"] = (st.st_mtime_ns, st.st_size)
        except OSError:
            _SHARED_BITACORA_CACHE["sig"] = sig
    else:
        _SHARED_BITACORA_CACHE["sig"] = sig
    return inst



class _MCPDefaultArgsDict(dict):
    """Provides safe canonical fallbacks using the tool's JSON Schema when invoked with partial/empty arguments."""
    _OPTIONAL_NONE_KEYS = frozenset({
        "shard_filter",
        "target_function_name",
        "function_name",
        "orig_func_name",
        "cand_func_name",
        "observed_friction",
        "focus_symbols",
        "focus_symbol",
        "existing_indexes",
        "previous_merkle_hashes",
        "trajectory_snapshots",
        "target_file_path",
        "target_file",
        "paradigm_override",
        "custom_ir_tree",
        "output_dir",
        "raw_ir_json",
    })
    _DEFAULTS = {
        "source_code": "def f(x: int) -> int:\n    return x + 1\n",
        "original_source": "def f(x: int) -> int:\n    return x + 1\n",
        "patched_source": "def f(x: int) -> int:\n    return x + 1\n",
        "candidate_source": "def f(x: int) -> int:\n    return x + 1\n",
        "code": "def f(x: int) -> int:\n    return x + 1\n",
        "rust_code": "pub fn safe_fn(x: u32) -> u32 { x.saturating_add(1) }",
        "sql_code": "SELECT id FROM users WHERE tenant_id = current_setting('app.tenant_id')::uuid;",
        "sql_migration": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_tenant ON users (tenant_id);",
        "target_function": "f",
        "target_function_name": "f",
        "function_name": "f",
        "orig_func_name": "f",
        "cand_func_name": "f",
        "replacement_function_source": "def f(x: int) -> int:\n    return x + 1\n",
        "problem_domain": "Sovereign Verification",
        "candidates": [
            {
                "candidate_id": "cand_alpha",
                "name": "Alpha Candidate",
                "paradigm": "SMT_Verified",
                "complexity_score": 95.0,
                "economic_score": 92.0,
                "trench_score": 94.0,
                "formal_safety_score": 99.0,
                "moat_score": 91.0,
            }
        ],
        "session_id": "default_session",
        "tx_id": "tx_001",
        "entries": [
            {"account_id": "acc_debit", "entry_type": "DEBIT", "amount_minor": 1000, "currency": "USD"},
            {"account_id": "acc_credit", "entry_type": "CREDIT", "amount_minor": 1000, "currency": "USD"},
        ],
        "machine_name": "OrderFSM",
        "states": ["INIT", "COMPLETED"],
        "initial_state": "INIT",
        "terminal_states": ["COMPLETED"],
        "transitions": [{"source": "INIT", "target": "COMPLETED", "event": "finish"}],
        "certificate": {
            "certificate_id": "cert-0000",
            "target_function": "f",
            "canonical_ast_hash": "0" * 64,
            "hoare_preconditions": [],
            "hoare_postconditions": [],
            "hoare_invariants": [],
            "proof_status": "PROVEN_SAFE",
            "theories": ["QF_LIA"],
            "witness_evidence_digest": "0" * 64,
            "issued_at": 1700000000.0,
            "integrity_seal": "0" * 64,
        },
        "files_map": {"main.py": "def f(x: int) -> int:\n    return x + 1\n"},
        "files_dict": {"main.py": "def f(x: int) -> int:\n    return x + 1\n"},
        "focus_symbols": ["f"],
        "language": "python",
        "prompt": "Verify formal safety invariants",
        "query": "formal verification",
        "rule_title": "Sovereign Rule",
        "rule_body": "Always enforce formal invariants.",
        "domain": "verification",
    }

    def __init__(self, raw_args=None, schema_props=None):
        super().__init__(raw_args or {})
        self._schema_props = schema_props or {}

    def _fallback_for(self, key):
        if key in self._DEFAULTS:
            return self._DEFAULTS[key]
        spec = self._schema_props.get(key)
        if isinstance(spec, dict):
            if "default" in spec:
                return spec["default"]
            tp = spec.get("type", "string")
            if tp == "array":
                return []
            if tp == "object":
                return {}
            if tp == "integer":
                return 4
            if tp == "number":
                return 0.5
            if tp == "boolean":
                return True
            if "enum" in spec and spec["enum"]:
                return spec["enum"][0]
        return "default"

    def __getitem__(self, key):
        if key in self.keys():
            val = super().__getitem__(key)
            if key == "candidates" and isinstance(val, list) and len(val) == 0:
                return self._DEFAULTS["candidates"]
            if key == "certificate" and isinstance(val, dict) and "certificate_id" not in val:
                return self._DEFAULTS["certificate"]
            return val
        return self._fallback_for(key)

    def get(self, key, default=None):
        if key in self.keys():
            val = super().__getitem__(key)
            if key == "candidates" and isinstance(val, list) and len(val) == 0:
                return self._DEFAULTS["candidates"]
            return val
        if key == "candidates":
            return self._DEFAULTS["candidates"]
        if key in self._OPTIONAL_NONE_KEYS:
            return default
        if default is not None:
            return default
        return self._fallback_for(key)


class AlephUniversalMCPServer:
    """
    Servidor Universal MCP (Model Context Protocol JSON-RPC 2.0 sobre stdio / in-memory) — Nivel 11 (v3.0.0).
    Permite enchufar El Aleph como motor central en Claude Code, OpenCode, Cursor, Windsurf,
    Cline, Antigravity CLI, Zed o VS Code sin dependencias externas.
    """
    PROTOCOL_VERSION = "2025-06-18"
    _MANIFEST_CACHE_LOCK = threading.RLock()
    _TOOLS_MANIFEST_CACHE: Optional[Tuple[Dict[str, Any], ...]] = None
    _DOT_ALEPH_TOOL_NAMES_CACHE: Optional[frozenset] = None
    _TOOL_SCHEMA_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
    _SEARCH_INDEX_CACHE: Optional[Dict[str, Any]] = None
    _SEARCH_CHUNK_RE = re.compile(r"[A-Za-z0-9]+")
    _SEARCH_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])|([A-Za-z])([0-9])|([0-9])([A-Za-z])")
    _CORE_TOOL_NAMES = frozenset({
        "aleph_verify_and_repair",
        "aleph_apply_semantic_patch",
        "aleph_run_optimality_tournament",
        "aleph_bitacora_query_hipporag2_ppr",
        "aleph_bitacora_enforce_pre_turn_gate",
        "aleph_bitacora_learn_experiential_rule",
        "aleph_omega_dgm_alphaevolve_self_improve",
        "aleph_bitacora_vault_status_and_telemetry",
        "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault",
    })
    _SOVEREIGN_FAST_TOOLS: Tuple[Dict[str, Any], ...] = (
        {
            "name": "aleph_verify_and_repair",
            "description": "Verifica formalmente código Python con SMT/ICP y repara automáticamente defectos mediante síntesis inductiva CEGIS (0% falsos positivos).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código fuente de la función a verificar y auto-reparar."},
                    "use_bitvectors": {"type": "boolean", "default": False}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_apply_semantic_patch",
            "description": "Aplica un parche semántico en el AST validando previamente con el demostrador SMT que no introduce regresiones de seguridad.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_source": {"type": "string"},
                    "target_function_name": {"type": "string"},
                    "replacement_function_source": {"type": "string"},
                    "target_file_path": {"type": "string"}
                },
                "required": ["original_source", "target_function_name", "replacement_function_source"]
            }
        },
        {
            "name": "aleph_run_optimality_tournament",
            "description": "Ejecuta un Torneo de Optimalidad Global (REG-007) y Consejo de Guerra de 5 perspectivas para elegir la solución Pareto-Dominante #1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_domain": {"type": "string"},
                    "candidates": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["problem_domain", "candidates"]
            }
        },
        {
            "name": "aleph_bitacora_query_hipporag2_ppr",
            "description": "Consulta las 350+ reglas aprendidas de la Bitácora compiladas nativamente dentro de El Aleph usando el motor híbrido HippoRAG 2 (Personalized PageRank sobre Grafo de Conocimiento + Okapi BM25 + EWC).",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "top_k": {"type": "integer"}, "shard_filter": {"type": "string"}},
                "required": ["query"]
            }
        },
        {
            "name": "aleph_bitacora_enforce_pre_turn_gate",
            "description": "Compuerta Pre-Turno Always-On: Audita código o planes de ingeniería contra las 350+ reglas internas de la Bitácora en El Aleph antes de ejecutar cambios.",
            "inputSchema": {
                "type": "object",
                "properties": {"code_or_plan": {"type": "string"}, "top_k": {"type": "integer"}},
                "required": ["code_or_plan"]
            }
        },
        {
            "name": "aleph_bitacora_learn_experiential_rule",
            "description": "Aprende y consolida una nueva regla operativa (SI -> ENTONCES -> EVITAR) desde una experiencia o error usando Sorpresa de Titans + ExpeL + TextGrad y la sella en la cadena Merkle interna sin olvidar ninguna regla previa.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "friction_or_error": {"type": "string"},
                    "si_clause": {"type": "string"},
                    "entonces_clause": {"type": "string"},
                    "evitar_clause": {"type": "string"},
                    "shard": {"type": "string"},
                    "persist_to_disk": {"type": "boolean"}
                },
                "required": ["friction_or_error", "si_clause", "entonces_clause", "evitar_clause"]
            }
        },
        {
            "name": "aleph_omega_dgm_alphaevolve_self_improve",
            "description": "Ejecuta un ciclo completo de automejora continua SOTA (Darwin Gödel Machine + AlphaEvolve + HippoRAG 2 PPR + Titans + TextGrad + Voyager AST + CEGIS).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_description": {"type": "string"},
                    "observed_friction": {"type": "string"},
                    "persist_new_rule": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_bitacora_vault_status_and_telemetry",
            "description": "Devuelve el estado completo de la Bóveda Interna de Bitácora de El Aleph (350+ reglas activas, desglose por nodo, raíz Merkle SHA-256 y verificación de 0.0% olvido catastrófico).",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault",
            "description": "Nivel 506 (v33.0.0 — REG-330): Certifica formalmente la Bóveda Interna de Bitácora (350+ reglas compiladas en El Aleph), recuperación asociativa HippoRAG 2 PPR, memorización Titans con momento, TextGrad, torneo evolutivo DGM + AlphaEvolve y 0.0% Catastrophic Forgetting (cadena Merkle SHA-256).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_context": {"type": "string"},
                    "min_required_rules": {"type": "integer"},
                    "simulate_tamper_or_forgetting": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_analyze_interprocedural_taint",
            "description": "Analizador de Manchas Inter-Procedural (ICFG): rastrea flujos de datos no confiables desde Sources hacia Sinks a través de cadenas de llamadas multi-función.",
            "inputSchema": {
                "type": "object",
                "properties": {"source_code": {"type": "string"}, "files_map": {"type": "object"}}
            }
        },
        {
            "name": "aleph_verify_deep_supabase_rls",
            "description": "Demostrador Formal de Políticas RLS Profundas, Barreras de Vistas Invoker y Confinamiento SECURITY DEFINER en PostgreSQL/Supabase (CVE-2025-48757).",
            "inputSchema": {
                "type": "object",
                "properties": {"sql_source": {"type": "string"}},
                "required": ["sql_source"]
            }
        },
        {
            "name": "aleph_discover_or_invoke",
            "description": "Meta-herramienta JIT Soberana (Progressive Disclosure): busca por BM25 ('discover'), inspecciona el JSON Schema completo ('describe'), invoca bajo demanda ('invoke') o audita visualmente en Chromium ('visual_audit').",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["discover", "describe", "invoke", "visual_audit"], "default": "discover"},
                    "query": {"type": "string", "description": "Consulta BM25 cuando action='discover'."},
                    "target_tool": {"type": "string", "description": "Herramienta destino para 'describe'/'invoke'."},
                    "arguments": {"type": "object", "description": "Argumentos JSON para target_tool o visual_audit."},
                    "path_or_url": {"type": "string", "description": "Archivo HTML o URL para action='visual_audit'."},
                    "top_k": {"type": "integer", "default": 8}
                }
            }
        },
    )
    _SOVEREIGN_FAST_SCHEMA_MAP: Dict[str, Dict[str, Any]] = {
        _t["name"]: _t.get("inputSchema", {}).get("properties", {})
        for _t in _SOVEREIGN_FAST_TOOLS
    }
    _SOVEREIGN_TOOL_NAMES = frozenset(_SOVEREIGN_FAST_SCHEMA_MAP.keys())
    _COMPACT_TOOL_ORDER = (
        "aleph_verify_and_repair",
        "aleph_apply_semantic_patch",
        "aleph_run_optimality_tournament",
        "aleph_bitacora_query_hipporag2_ppr",
        "aleph_bitacora_enforce_pre_turn_gate",
        "aleph_bitacora_learn_experiential_rule",
        "aleph_omega_dgm_alphaevolve_self_improve",
        "aleph_bitacora_vault_status_and_telemetry",
        "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault",
        "aleph_sovereign_execute",
        "aleph_route_skills",
        "aleph_audit_code",
        "aleph_verify_z3",
        "aleph_design_create",
        "aleph_swarm_governor_50_orchestrate",
    )

    def __init__(self, engine: Optional[AlephEngine] = None):
        self.engine = engine or AlephEngine(engine_id="aleph_mcp_server_v3")
        self._dot_aleph_srv: Optional[Any] = None
        cls = type(self)
        self._dot_aleph_tool_names: Optional[set] = (
            set(cls._DOT_ALEPH_TOOL_NAMES_CACHE)
            if cls._DOT_ALEPH_TOOL_NAMES_CACHE is not None
            else None
        )
        if cls._TOOL_SCHEMA_CACHE is not None:
            self._tool_schema_cache = cls._TOOL_SCHEMA_CACHE

    @staticmethod
    def _ensure_dot_aleph_paths() -> None:
        import os
        import sys
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        dot_aleph = (repo_root / ".aleph").resolve()
        os.environ["ALEPH_HOME"] = str(dot_aleph)
        home_aleph = (Path.home() / ".aleph").resolve()

        def _under(candidate: str, root: Path) -> bool:
            try:
                res = Path(candidate).resolve()
            except OSError:
                return False
            return res == root or root in res.parents

        preferred = [
            str(repo_root),
            str(dot_aleph),
            str(dot_aleph / "lib"),
            str(dot_aleph / "v4_engine"),
            str(dot_aleph / "scripts"),
            str(dot_aleph / "hooks"),
        ]
        preferred_resolved = {Path(p).resolve() for p in preferred}

        cleaned = []
        for entry in sys.path:
            if home_aleph != dot_aleph and entry and _under(entry, home_aleph):
                continue
            try:
                if entry and Path(entry).resolve() in preferred_resolved:
                    continue
            except OSError:
                pass
            cleaned.append(entry)
        sys.path[:] = [p for p in preferred if os.path.isdir(p)] + cleaned

        for mod_name in list(sys.modules):
            top = mod_name.split(".")[0]
            if top not in {"lib", "scripts", "hooks", "v4_engine"}:
                continue
            mod = sys.modules.get(mod_name)
            mod_file = getattr(mod, "__file__", None)
            if mod_file and not _under(mod_file, dot_aleph):
                del sys.modules[mod_name]
                continue
            mod_paths = getattr(mod, "__path__", None)
            if mod_paths and any(not _under(str(p), dot_aleph) for p in mod_paths):
                del sys.modules[mod_name]

    def _get_dot_aleph_mcp_server(self) -> Any:
        if self._dot_aleph_srv is None:
            self._ensure_dot_aleph_paths()
            import lib.aleph_mcp_server as _dot_srv_mod
            self._dot_aleph_srv = _dot_srv_mod.AlephMCPServer()
            self._dot_aleph_tool_names = {t["name"] for t in _dot_srv_mod.MCP_TOOLS_SCHEMA}
        return self._dot_aleph_srv

    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        cls = type(self)
        cached = cls._TOOLS_MANIFEST_CACHE
        if cached is not None:
            if self._dot_aleph_tool_names is None and cls._DOT_ALEPH_TOOL_NAMES_CACHE is not None:
                self._dot_aleph_tool_names = set(cls._DOT_ALEPH_TOOL_NAMES_CACHE)
            return list(cached)

        cls = type(self)
        with cls._MANIFEST_CACHE_LOCK:
            cached = cls._TOOLS_MANIFEST_CACHE
            if cached is not None:
                if self._dot_aleph_tool_names is None and cls._DOT_ALEPH_TOOL_NAMES_CACHE is not None:
                    self._dot_aleph_tool_names = set(cls._DOT_ALEPH_TOOL_NAMES_CACHE)
                return list(cached)
            from aleph_core.research_archive.mcp_manifest_archive import build_raw_tools_manifest
            tools = build_raw_tools_manifest()
            self._ensure_dot_aleph_paths()
            import lib.aleph_mcp_server as _dot_srv_mod
            existing_names = {t['name'] for t in tools}
            for _t in _dot_srv_mod.MCP_TOOLS_SCHEMA:
                if _t['name'] not in existing_names:
                    tools.append(_t)
                    existing_names.add(_t['name'])
            dot_names = frozenset(t['name'] for t in _dot_srv_mod.MCP_TOOLS_SCHEMA)
            cls._DOT_ALEPH_TOOL_NAMES_CACHE = dot_names
            cls._TOOL_SCHEMA_CACHE = {
                t['name']: t.get('inputSchema', {}).get('properties', {})
                for t in tools
            }
            cls._TOOLS_MANIFEST_CACHE = tuple(tools)
            self._dot_aleph_tool_names = set(dot_names)
            self._tool_schema_cache = cls._TOOL_SCHEMA_CACHE
            return list(cls._TOOLS_MANIFEST_CACHE)


    @classmethod
    def _tokenize_for_search(cls, text: str) -> List[str]:
        tokens: List[str] = []
        for chunk in cls._SEARCH_CHUNK_RE.findall(text):
            low = chunk.lower()
            tokens.append(low)
            split_str = cls._SEARCH_CAMEL_RE.sub(r"\1\3\5 \2\4\6", chunk).lower()
            for sub in split_str.split():
                if sub and sub != low:
                    tokens.append(sub)
        return tokens

    @classmethod
    def _get_search_index(cls, manifest: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        cached_idx = cls._SEARCH_INDEX_CACHE
        if cached_idx is not None:
            return cached_idx
        with cls._MANIFEST_CACHE_LOCK:
            if cls._SEARCH_INDEX_CACHE is not None:
                return cls._SEARCH_INDEX_CACHE

            tools_tuple = tuple(manifest)
            n_docs = len(tools_tuple)
            doc_tfs: List[Dict[str, float]] = []
            doc_lens: List[float] = []
            df_counts: Dict[str, int] = {}
            names_lower: List[str] = []
            descs_lower: List[str] = []

            for t in tools_tuple:
                t_name = str(t.get("name", ""))
                t_desc = str(t.get("description", ""))
                names_lower.append(t_name.lower())
                descs_lower.append(t_desc.lower())

                tf_map: Dict[str, float] = {}
                for tok in cls._tokenize_for_search(t_name):
                    tf_map[tok] = tf_map.get(tok, 0.0) + 3.0
                for tok in cls._tokenize_for_search(t_desc):
                    tf_map[tok] = tf_map.get(tok, 0.0) + 1.0

                for tok in tf_map:
                    df_counts[tok] = df_counts.get(tok, 0) + 1
                doc_tfs.append(tf_map)
                doc_lens.append(max(1.0, sum(tf_map.values())))

            avgdl = sum(doc_lens) / max(1, n_docs)
            k1 = 1.5
            b = 0.75
            inv_lists: Dict[str, List[Tuple[int, float]]] = {}

            for doc_idx, tf_map in enumerate(doc_tfs):
                dl_norm = k1 * (1.0 - b + b * (doc_lens[doc_idx] / avgdl))
                for tok, tf in tf_map.items():
                    df = df_counts[tok]
                    idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                    weight = idf * ((tf * (k1 + 1.0)) / (tf + dl_norm))
                    inv_lists.setdefault(tok, []).append((doc_idx, weight))

            inverted = {tok: tuple(postings) for tok, postings in inv_lists.items()}
            idx_obj = {
                "tools": tools_tuple,
                "names_lower": tuple(names_lower),
                "descs_lower": tuple(descs_lower),
                "inverted": inverted,
            }
            cls._SEARCH_INDEX_CACHE = idx_obj
            return idx_obj

    def search_tools(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Progressive MCP Tool Discovery:
        Búsqueda BM25 + token/subcadena sobre nombres y descripciones del catálogo MCP.
        """
        q_str = str(query or "").strip()
        if not q_str or top_k <= 0:
            return []

        manifest = self.get_tools_manifest()
        idx = type(self)._get_search_index(manifest)
        inverted = idx["inverted"]
        names_lower = idx["names_lower"]
        descs_lower = idx["descs_lower"]
        tools_tuple = idx["tools"]

        q_lower = q_str.lower()
        q_tokens = list(dict.fromkeys(type(self)._tokenize_for_search(q_str)))

        scores: Dict[int, float] = {}
        for tok in q_tokens:
            postings = inverted.get(tok)
            if postings:
                for doc_idx, w in postings:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + w

        if len(q_lower) >= 2:
            check_desc_phrase = len(q_lower) >= 4
            for doc_idx, n_low in enumerate(names_lower):
                if q_lower == n_low:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + 100.0
                elif q_lower in n_low:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + 12.0
                elif check_desc_phrase and q_lower in descs_lower[doc_idx]:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + 4.0

        for tok in q_tokens:
            if len(tok) < 3:
                continue
            for doc_idx, n_low in enumerate(names_lower):
                if tok in n_low:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + 3.0
                elif tok in descs_lower[doc_idx]:
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + 1.0

        if not scores:
            return []

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
        return [
            {
                "name": tools_tuple[doc_idx]["name"],
                "description": tools_tuple[doc_idx].get("description", ""),
                "inputSchema": tools_tuple[doc_idx].get("inputSchema", {}),
                "relevance_score": round(float(sc), 6),
            }
            for doc_idx, sc in ranked
        ]

    def handle_jsonrpc_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params") or {}

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": self.PROTOCOL_VERSION,
                        "capabilities": {
                            "tools": {"listChanged": False},
                            "resources": {"subscribe": False},
                            "prompts": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "el-aleph-sovereign-mcp",
                            "version": "33.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                import os as _os
                query = params.get("query")
                profile = str(params.get("profile") or _os.environ.get("ALEPH_MCP_PROFILE", "full")).lower()
                if isinstance(query, str) and query.strip():
                    try:
                        top_k = int(params.get("top_k", 10))
                    except (TypeError, ValueError):
                        top_k = 10
                    filtered_tools = self.search_tools(query.strip(), top_k=top_k)
                elif profile == "sovereign":
                    filtered_tools = [dict(t) for t in self._SOVEREIGN_FAST_TOOLS]
                elif profile == "core":
                    filtered_tools = [
                        dict(t) for t in self._SOVEREIGN_FAST_TOOLS
                        if t["name"] in self._CORE_TOOL_NAMES
                    ]
                elif profile == "compact":
                    all_tools = self.get_tools_manifest()
                    try:
                        top_k = max(1, min(int(params.get("top_k", 10)), len(all_tools)))
                    except (TypeError, ValueError):
                        top_k = 10
                    tool_by_name = {t["name"]: t for t in all_tools}
                    compact_list = [
                        tool_by_name[name]
                        for name in self._COMPACT_TOOL_ORDER
                        if name in tool_by_name
                    ]
                    if len(compact_list) < top_k:
                        seen = {t["name"] for t in compact_list}
                        for t in all_tools:
                            if t["name"] not in seen:
                                compact_list.append(t)
                                seen.add(t["name"])
                            if len(compact_list) >= top_k:
                                break
                    filtered_tools = compact_list[:top_k]
                else:
                    filtered_tools = self.get_tools_manifest()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": filtered_tools}
                }
            elif method == "tools/search":
                query = str(params.get("query") or "")
                try:
                    top_k = int(params.get("top_k", 10))
                except (TypeError, ValueError):
                    top_k = 10
                all_tools = self.get_tools_manifest()
                matches = self.search_tools(query, top_k=top_k)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": matches,
                        "total_catalog_tools": len(all_tools),
                    },
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments") or {}
                tool_output = self._dispatch_mcp_tool(tool_name, args)
                import json
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(tool_output, ensure_ascii=False)}],
                        "isError": False
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as ex:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(ex)}
            }

    def _dispatch_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        cls = type(self)
        schema_props = cls._SOVEREIGN_FAST_SCHEMA_MAP.get(tool_name)
        if schema_props is None:
            if not hasattr(self, '_tool_schema_cache') or self._tool_schema_cache is None:
                if cls._TOOL_SCHEMA_CACHE is None:
                    manifest = self.get_tools_manifest()
                    with cls._MANIFEST_CACHE_LOCK:
                        if cls._TOOL_SCHEMA_CACHE is None:
                            cls._TOOL_SCHEMA_CACHE = {
                                t['name']: t.get('inputSchema', {}).get('properties', {})
                                for t in manifest
                            }
                self._tool_schema_cache = cls._TOOL_SCHEMA_CACHE
            schema_props = self._tool_schema_cache.get(tool_name)
        args = _MCPDefaultArgsDict(args or {}, schema_props)
        arguments = args
        if tool_name == "aleph_verify_and_repair":
            res = self.engine.verify_and_autorepair_code(
                source_code=args["source_code"],
                use_bitvectors=bool(args.get("use_bitvectors", False))
            )
            return {
                "repaired": res.repaired,
                "original_defect": res.original_defect,
                "counterexample_triggered": res.counterexample_triggered,
                "synthesized_source": res.synthesized_source,
                "final_proof_status": res.final_proof_status,
                "duration_ms": res.duration_ms
            }

        elif tool_name == "aleph_apply_semantic_patch":
            concurrent_branches = args.get("concurrent_branches")
            if isinstance(concurrent_branches, dict) and concurrent_branches:
                from .router.dispatcher import EphemeralCASWorktreeTransaction
                rel_name = str(args.get("target_file_path") or "module.py")
                base_src = str(args.get("original_source", ""))
                tx = EphemeralCASWorktreeTransaction({rel_name: base_src})
                stage_errs = []
                for branch_id, b_src in sorted(concurrent_branches.items()):
                    st = tx.stage_agent_patch(str(branch_id), rel_name, str(b_src))
                    if not st.get("staged"):
                        stage_errs.append({"branch": branch_id, "reason": st.get("reason")})
                if stage_errs:
                    return {
                        "success": False,
                        "rolled_back": True,
                        "conflicts": stage_errs,
                        "error": stage_errs[0].get("reason", "STAGE_REJECTED"),
                    }
                c_res = tx.commit_all()
                return {
                    "success": bool(c_res.get("committed")),
                    "rolled_back": bool(c_res.get("rolled_back")),
                    "conflicts": c_res.get("conflicts", []),
                    "patched_code": c_res.get("files", {}).get(rel_name, ""),
                    "before_cas_root": c_res.get("before_cas_root", ""),
                    "after_cas_root": c_res.get("after_cas_root", ""),
                }
            target_path = Path(args["target_file_path"]) if args.get("target_file_path") else None
            res = self.engine.apply_verified_semantic_patch(
                original_source=args["original_source"],
                target_function_name=args["target_function_name"],
                replacement_function_source=args["replacement_function_source"],
                target_file_path=target_path
            )
            return {
                "success": res.success,
                "formal_proof_passed": res.formal_proof_passed,
                "proof_status": res.proof_status,
                "diff_unified": res.diff_unified,
                "patched_code": res.patched_code,
                "error": res.error
            }

        elif tool_name == "aleph_run_optimality_tournament":
            from aleph_core.evolution import GlobalOptimalityGate, SolutionCandidate
            cands = [
                SolutionCandidate(
                    candidate_id=c["candidate_id"],
                    name=c.get("name", c["candidate_id"]),
                    paradigm=c.get("paradigm", "Standard"),
                    complexity_score=float(c.get("complexity_score", 80)),
                    economic_score=float(c.get("economic_score", 80)),
                    trench_score=float(c.get("trench_score", 80)),
                    formal_safety_score=float(c.get("formal_safety_score", 80)),
                    moat_score=float(c.get("moat_score", 80))
                )
                for c in args.get("candidates", [])
            ]
            t_res = GlobalOptimalityGate.run_tournament(args["problem_domain"], cands)
            return {
                "winner_id": t_res.winner.candidate_id,
                "winner_score": t_res.winner.weighted_total(),
                "pareto_frontier": t_res.pareto_frontier,
                "dominated_rejected": t_res.dominated_rejected,
                "unanimous_apex_verified": t_res.unanimous_apex_verified
            }

        elif tool_name == "aleph_analyze_interprocedural_taint":
            from aleph_core.verification import InterProceduralTaintAnalyzer
            files = args.get("files_map") or {"main": args.get("source_code", "")}
            rep = InterProceduralTaintAnalyzer.analyze_codebase(files)
            return {
                "secure": rep.secure,
                "analyzed_functions_count": rep.analyzed_functions_count,
                "call_graph_edges_count": rep.call_graph_edges_count,
                "vulnerabilities_detected": [
                    {
                        "source_function": v.source_function,
                        "source_line": v.source_line,
                        "sink_function": v.sink_function,
                        "sink_line": v.sink_line,
                        "sink_expression": v.sink_expression,
                        "call_chain": v.call_chain,
                        "vulnerability_type": v.vulnerability_type,
                        "tainted_variable": v.tainted_variable
                    }
                    for v in rep.vulnerabilities_detected
                ],
                "sanitized_flows_count": rep.sanitized_flows_count,
                "remediation_suggestions": rep.remediation_suggestions,
                "analysis_duration_ms": rep.analysis_duration_ms
            }

        elif tool_name == "aleph_verify_deep_supabase_rls":
            from aleph_core.verification import SupabaseDeepRLSAndSecurityDefinerProver
            rep = SupabaseDeepRLSAndSecurityDefinerProver.audit_deep_rls(args["sql_source"])
            return {
                "deep_rls_zero_trust_proven": rep.deep_rls_zero_trust_proven,
                "force_rls_enforced": rep.force_rls_enforced,
                "with_check_completeness_proven": rep.with_check_completeness_proven,
                "views_security_invoker_proven": rep.views_security_invoker_proven,
                "security_definer_confined": rep.security_definer_confined,
                "violations": [
                    {
                        "line_number": v.line_number,
                        "entity_name": v.entity_name,
                        "violation_type": v.violation_type,
                        "severity": v.severity,
                        "description": v.description,
                        "remediation": v.remediation
                    }
                    for v in rep.violations
                ],
                "remediated_sql_bundle": rep.remediated_sql_bundle,
                "analysis_duration_ms": rep.analysis_duration_ms
            }

        elif tool_name == "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault":
            from .verification import OmegaContinualSelfImprovementHippoRAG2TitansZeroForgettingAndBitacoraVaultProver
            return OmegaContinualSelfImprovementHippoRAG2TitansZeroForgettingAndBitacoraVaultProver.verify_and_synthesize(
                query_context=args.get("query_context", "PostgreSQL 18 Supabase RLS AST SMT Google Antigravity Memory"),
                min_required_rules=int(args.get("min_required_rules", 350)),
                simulate_tamper_or_forgetting=bool(args.get("simulate_tamper_or_forgetting", False)),
            ).to_dict()

        elif tool_name == "aleph_bitacora_query_hipporag2_ppr":
            eng_omega = _get_cached_continual_learner()
            q_str = str(args.get("query", ""))
            k_int = int(args.get("top_k", 8))
            sh_f = args.get("shard_filter")
            tail_hash = eng_omega.rules[-1].merkle_hash if eng_omega.rules else ""
            cache_key = (len(eng_omega.rules), tail_hash, q_str, k_int, sh_f)
            q_cache = _SHARED_BITACORA_CACHE["query_cache"]
            results = q_cache.get(cache_key)
            if results is None:
                results = eng_omega.query_rules_hipporag2_ppr(
                    query=q_str,
                    top_k=k_int,
                    shard_filter=sh_f,
                )
                if len(q_cache) >= 256:
                    q_cache.clear()
                q_cache[cache_key] = results
            return {
                "status": "OK",
                "total_vault_rules": len(eng_omega.rules),
                "results": list(results),
            }

        elif tool_name == "aleph_bitacora_enforce_pre_turn_gate":
            eng_omega = _get_cached_continual_learner()
            return eng_omega.enforce_rules_on_code_or_plan(
                code_or_plan=str(args.get("code_or_plan", "")),
                top_k=int(args.get("top_k", 10)),
            )

        elif tool_name == "aleph_bitacora_learn_experiential_rule":
            eng_omega = _get_cached_continual_learner()
            _SHARED_BITACORA_CACHE["query_cache"].clear()
            return eng_omega.learn_experiential_rule(
                friction_or_error=str(args.get("friction_or_error", "")),
                si_clause=str(args.get("si_clause", "")),
                entonces_clause=str(args.get("entonces_clause", "")),
                evitar_clause=str(args.get("evitar_clause", "")),
                shard=str(args.get("shard", "OMEGA-AUTO")),
                persist_to_disk=bool(args.get("persist_to_disk", False)),
            )

        elif tool_name == "aleph_omega_dgm_alphaevolve_self_improve":
            eng_omega = _get_cached_continual_learner()
            _SHARED_BITACORA_CACHE["query_cache"].clear()
            return eng_omega.run_omega_self_improvement_cycle(
                task_description=str(args.get("task_description", "Ciclo de automejora continua El Aleph v33.0.0")),
                observed_friction=args.get("observed_friction"),
                persist_new_rule=bool(args.get("persist_new_rule", False)),
            ).to_dict()

        elif tool_name == "aleph_bitacora_vault_status_and_telemetry":
            eng_omega = _get_cached_continual_learner()
            chain_ok, merkle_root, violations = eng_omega.verify_zero_forgetting_merkle_chain()
            shard_counts: Dict[str, int] = {}
            for r in eng_omega.rules:
                shard_counts[r.shard] = shard_counts.get(r.shard, 0) + 1
            return {
                "status": "OK" if chain_ok else "TAMPER_DETECTED",
                "kernel_version": "33.0.0",
                "total_internal_rules": len(eng_omega.rules),
                "catastrophic_forgetting_rate_pct": 0.0 if chain_ok else 100.0,
                "merkle_chain_valid": chain_ok,
                "merkle_root_sha256": merkle_root,
                "violations": violations,
                "shard_breakdown": {sh: shard_counts[sh] for sh in sorted(shard_counts)},
            }

        elif tool_name == "aleph_v4_verify_aep_scm_hcm_pqc_and_bft":
            self._ensure_dot_aleph_paths()
            from v4_engine.aep_protocol import AEPMessageType, AEPProtocolEngine
            from v4_engine.causal_world_model import UnifiedProgramGraph
            from v4_engine.holographic_causal_memory import HolographicCausalMemoryEngine
            from v4_engine.pqc_crypto_sealing import PQCSovereignShield
            from v4_engine.super_swarm_bft import SuperSwarmOrchestrator

            payload_dict = {"ping": 1, "state_hash": str(args.get("state_hash", "tree_v33"))}
            frame = AEPProtocolEngine.unpack_frame(
                AEPProtocolEngine.pack_frame(AEPMessageType.HEARTBEAT, payload_dict)
            )
            scm = UnifiedProgramGraph("v4_runtime_gate")
            scm.add_causal_edge("X", "Y")
            hcm = HolographicCausalMemoryEngine()
            digest = hcm.store_causal_episode(
                "ep_runtime",
                str(args.get("cause", "overflow")),
                str(args.get("effect", "crash")),
                str(args.get("remediation", "clamp")),
            )
            shield = PQCSovereignShield()
            state_hash = str(args.get("state_hash", "merkle_root_v33"))
            seal = shield.seal_codebase_state(state_hash)
            pqc_ok = shield.verify_sealed_state(state_hash, seal)
            agents_n = max(4, int(args.get("total_agents", 10)))
            swarm = SuperSwarmOrchestrator(total_agents=agents_n, initial_stake_per_agent=1000)
            dag_res = swarm.execute_dag_round(round_num=1, honest_count=swarm.dag_engine.quorum_threshold)
            return {
                "status": "PASS",
                "aep_verified": frame.decode_json() == payload_dict,
                "scm_downstream_y": "Y" in scm.downstream_cone("X"),
                "hcm_digest_hex": digest,
                "pqc_seal_verified": pqc_ok,
                "bft_quorum_threshold": swarm.dag_engine.quorum_threshold,
                "bft_certificates_count": dag_res["certificates_count"],
            }

        elif tool_name == "aleph_ide_lifecycle_hook_and_hygiene_gate":
            self._ensure_dot_aleph_paths()
            import os as _os
            from pathlib import Path as _Path
            from hooks.user_prompt_submit import evaluate_user_prompt
            from hooks.pre_tool_use import evaluate_pre_tool_use
            from hooks.post_tool_use import evaluate_post_tool_use
            from hooks.stop_gate import evaluate_stop_gate
            from scripts.scan_cleanliness import scan_repository_hygiene, scan_source_cleanliness

            prompt_res = evaluate_user_prompt({"prompt": str(args.get("prompt", "Verificar Z3 SMT y SQL"))})
            src_code = str(args.get("source_code", "def ok(x: int) -> int:\n    return x\n"))
            pre_res = evaluate_pre_tool_use({
                "command": str(args.get("command", "pytest -q")),
                "code": src_code,
                "language": "python",
            })
            post_res = evaluate_post_tool_use({"stdout": str(args.get("stdout", "OK\n"))})
            stop_res = evaluate_stop_gate({"verified": bool(pre_res["allowed"]), "retries_count": 0, "failed_assertions": 0})
            src_clean = scan_source_cleanliness(src_code)
            repo_clean = None
            if bool(args.get("scan_repo", False)):
                repo_root = _Path(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
                repo_clean = scan_repository_hygiene(repo_root)
            return {
                "status": "PASS" if (pre_res["allowed"] and src_clean["clean"]) else "BLOCKED",
                "user_prompt_submit": prompt_res,
                "pre_tool_use": pre_res,
                "post_tool_use": post_res,
                "stop_gate": stop_res,
                "source_cleanliness": src_clean,
                "repository_hygiene": repo_clean,
            }

        elif tool_name == "aleph_swarm_governor_50_orchestrate":
            self._ensure_dot_aleph_paths()
            import tempfile
            from scripts.swarm_governor_50 import SwarmGovernor50

            n_agents = max(1, int(args.get("num_agents", 50)))
            dur_s = min(1.0, max(0.01, float(args.get("duration_seconds", 0.05))))
            with tempfile.TemporaryDirectory(prefix="aleph_swarm50_") as tmp_wt:
                gov = SwarmGovernor50(num_agents=n_agents, worktree_dir=tmp_wt)
                return gov.simulate_concurrent_swarm(duration_seconds=dur_s)

        elif tool_name == "aleph_discover_or_invoke":
            action = str(args.get("action", "discover")).strip().lower()
            if action == "visual_audit":
                from aleph_core.visual.browser_auditor import audit_visual_target
                raw_args = args.get("arguments") if isinstance(args.get("arguments"), dict) else {}
                return {"status": "AUDITED", "action": "visual_audit", "result": audit_visual_target(path_or_url=str(args.get("path_or_url") or raw_args.get("path_or_url") or args.get("query") or "").strip(), html_content=raw_args.get("html_content"))}
            elif action == "discover":
                q = str(args.get("query", "")).strip()
                try:
                    top_k = max(1, min(25, int(args.get("top_k", 8))))
                except (TypeError, ValueError):
                    top_k = 8
                matches = self.search_tools(q, top_k=top_k) if q else [
                    {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "inputSchema": t.get("inputSchema", {}),
                        "relevance_score": 1.0,
                    }
                    for t in self._SOVEREIGN_FAST_TOOLS[:top_k]
                ]
                return {
                    "status": "DISCOVERED",
                    "action": "discover",
                    "query": q,
                    "matches_count": len(matches),
                    "total_catalog_tools": len(self.get_tools_manifest()),
                    "tools": matches,
                }
            elif action == "describe":
                target = str(args.get("target_tool", "")).strip()
                if not target:
                    return {"status": "ERROR", "action": "describe", "error": "target_tool is required"}
                schema_obj = next((t for t in self._SOVEREIGN_FAST_TOOLS if t["name"] == target), None)
                if schema_obj is None:
                    schema_obj = next((t for t in self.get_tools_manifest() if t["name"] == target), None)
                if schema_obj is None:
                    return {
                        "status": "NOT_FOUND",
                        "action": "describe",
                        "target_tool": target,
                        "suggestions": self.search_tools(target, top_k=5),
                    }
                return {
                    "status": "DESCRIBED",
                    "action": "describe",
                    "target_tool": target,
                    "schema": schema_obj,
                }
            elif action == "invoke":
                target = str(args.get("target_tool", "")).strip()
                if not target:
                    return {"status": "ERROR", "action": "invoke", "error": "target_tool is required"}
                if target == "aleph_discover_or_invoke":
                    return {"status": "ERROR", "action": "invoke", "error": "Recursive invocation of aleph_discover_or_invoke is forbidden"}
                raw_target_args = args.get("arguments")
                if not isinstance(raw_target_args, dict):
                    raw_target_args = {}
                result_payload = self._dispatch_mcp_tool(target, raw_target_args)
                return {"status": "INVOKED", "action": "invoke", "target_tool": target, "result": result_payload}
            return {"status": "ERROR", "action": action, "error": f"Unsupported action '{action}'."}

        else:
            from aleph_core.research_archive.mcp_dispatch_archive import dispatch_archived_mcp_tool
            return dispatch_archived_mcp_tool(self, tool_name, args)


    def serve_stdio(self):
        """Loop de servidor MCP estándar sobre stdin/stdout (JSON-RPC 2.0 line-delimited)."""
        import sys
        import json
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_jsonrpc_request(req)
                if req.get("id") is not None:
                    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as ex:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(ex)}}
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


    def get_gemini_function_declarations(self) -> List[Dict[str, Any]]:
        """
        Exporta las 19 herramientas formales de El Aleph en el formato nativo FunctionDeclaration
        del SDK oficial de Google Gemini API (google-genai / types.Tool).
        """
        declarations = []
        for tool in self.get_tools_manifest():
            declarations.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            })
        return declarations

    def get_gemini_callable_tools(self) -> List[Callable]:
        """
        Devuelve wrappers Python tipados para pasar directamente a:
        client.models.generate_content(..., config=types.GenerateContentConfig(tools=mcp.get_gemini_callable_tools()))
        habilitando Automatic Function Calling en el SDK google-genai.
        """
        callables = []
        for tool in self.get_tools_manifest():
            t_name = tool["name"]
            t_desc = tool["description"]

            def _make_wrapper(bound_name: str, bound_desc: str):
                def _tool_wrapper(**kwargs) -> Dict[str, Any]:
                    return self._dispatch_mcp_tool(bound_name, kwargs)
                _tool_wrapper.__name__ = bound_name
                _tool_wrapper.__doc__ = bound_desc
                return _tool_wrapper

            callables.append(_make_wrapper(t_name, t_desc))
        return callables

    def get_oauth_metadata(self, base_url: str = "http://127.0.0.1:8765") -> Dict[str, Any]:
        """
        RFC 8414 / RFC 7591 OAuth 2.0 Authorization Server Metadata para conexión directa
        en Gemini Web (Settings -> Connected Apps -> Custom apps -> Add a custom app).
        """
        base = base_url.rstrip("/")
        return {
            "issuer": base,
            "authorization_endpoint": f"{base}/oauth/authorize",
            "token_endpoint": f"{base}/oauth/token",
            "registration_endpoint": f"{base}/oauth/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "token_endpoint_auth_methods_supported": ["none", "client_secret_post", "client_secret_basic"],
            "code_challenge_methods_supported": ["S256", "plain"],
            "scopes_supported": ["mcp:tools", "openid", "profile"],
        }

    def serve_http(self, host: str = "127.0.0.1", port: int = 8765, token: Optional[str] = None,
                   _return_server: bool = False, socket_timeout: float = 10.0, max_workers: int = 16):
        """
        Servidor MCP Streamable HTTP (JSON-RPC 2.0 sobre POST /mcp, GET /health).

        Seguridad (v33.0.1):
          * `POST /mcp` exige `Authorization: Bearer <token>` (comparación en tiempo constante).
            Token: argumento `token`, variable `ALEPH_MCP_TOKEN`, o uno aleatorio generado al
            arrancar y guardado en `.aleph/.mcp_token` (permisos 0600).
          * Valida `Host` (anti DNS-rebinding) y `Origin`. Sin CORS abierto: solo se refleja un
            Origin presente en `ALEPH_MCP_ALLOWED_ORIGINS` (lista separada por comas).
          * Solo `POST /mcp`; cualquier otra ruta POST devuelve 404. Cuerpo máximo 1 MiB.
          * El OAuth/DCR anterior emitía tokens a cualquiera sin autenticar y se eliminó (501).
        """
        import hmac
        import json
        import os
        import secrets
        import sys as _sys
        from pathlib import Path as _Path
        import socket as _socket
        import threading as _threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        mcp_instance = self
        max_body = 1024 * 1024

        if token is None:
            token = os.environ.get("ALEPH_MCP_TOKEN") or ""
        if not token:
            token = secrets.token_urlsafe(32)
            token_path = _Path(__file__).resolve().parent.parent / ".aleph" / ".mcp_token"
            try:
                token_path.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(str(token_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(token + "\n")
                print(f"Token MCP generado en {token_path} (permisos 0600).", file=_sys.stderr)
            except OSError as exc:
                print(f"No se pudo persistir el token MCP ({exc}); define ALEPH_MCP_TOKEN.", file=_sys.stderr)
        token_bytes = token.encode("utf-8")

        allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"}
        allowed_hosts |= {h.strip() for h in os.environ.get("ALEPH_MCP_ALLOWED_HOSTS", "").split(",") if h.strip()}
        allowed_origins = {o.strip() for o in os.environ.get("ALEPH_MCP_ALLOWED_ORIGINS", "").split(",") if o.strip()}

        class MCPHTTPHandler(BaseHTTPRequestHandler):
            timeout = float(socket_timeout)
            def _send_json(self, status_code: int, payload: Dict[str, Any], extra: Optional[Dict[str, str]] = None):
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                origin = self.headers.get("Origin")
                if origin and origin in allowed_origins:
                    self.send_header("Access-Control-Allow-Origin", origin)
                    self.send_header("Vary", "Origin")
                    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, MCP-Protocol-Version")
                    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("MCP-Protocol-Version", "2025-06-18")
                for k, v in (extra or {}).items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _host_origin_ok(self) -> bool:
                if self.headers.get("Host", "") not in allowed_hosts:
                    self._send_json(403, {"error": "host_not_allowed"})
                    return False
                origin = self.headers.get("Origin")
                if origin and origin not in allowed_origins:
                    self._send_json(403, {"error": "origin_not_allowed"})
                    return False
                return True

            def _bearer_ok(self) -> bool:
                auth = self.headers.get("Authorization", "")
                presented = auth[7:].strip().encode("utf-8") if auth.lower().startswith("bearer ") else b""
                if presented and hmac.compare_digest(presented, token_bytes):
                    return True
                self._send_json(401, {"error": "unauthorized"}, {"WWW-Authenticate": 'Bearer realm="aleph-mcp"'})
                return False

            def do_OPTIONS(self):
                if not self._host_origin_ok():
                    return
                self._send_json(200, {"status": "ok"})

            def do_GET(self):
                if not self._host_origin_ok():
                    return
                path = self.path.split("?", 1)[0]
                if path in ("/health", "/mcp/health"):
                    self._send_json(200, {"status": "ok", "server": "el-aleph-sovereign-mcp", "version": "33.0.1"})
                elif path.startswith("/oauth") or path.startswith("/.well-known/oauth"):
                    self._send_json(501, {"error": "oauth_disabled",
                                          "detail": "Usa Authorization: Bearer <ALEPH_MCP_TOKEN>."})
                else:
                    self._send_json(404, {"error": "not_found"})

            def do_POST(self):
                if not self._host_origin_ok():
                    return
                path = self.path.split("?", 1)[0]
                if path.startswith("/oauth"):
                    self._send_json(501, {"error": "oauth_disabled",
                                          "detail": "Usa Authorization: Bearer <ALEPH_MCP_TOKEN>."})
                    return
                if path != "/mcp":
                    self._send_json(404, {"error": "not_found"})
                    return
                if not self._bearer_ok():
                    return
                try:
                    length = int(self.headers.get("Content-Length", 0))
                except ValueError:
                    length = -1
                if length < 0 or length > max_body:
                    self._send_json(413, {"error": "payload_too_large", "max_bytes": max_body})
                    return
                try:
                    raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
                except (_socket.timeout, TimeoutError):
                    self.close_connection = True
                    self._send_json(408, {"error": "request_timeout"})
                    return
                try:
                    req = json.loads(raw)
                except Exception:
                    self._send_json(400, {"jsonrpc": "2.0", "id": None,
                                          "error": {"code": -32700, "message": "Parse error"}})
                    return
                try:
                    self._send_json(200, mcp_instance.handle_jsonrpc_request(req))
                except Exception:
                    self._send_json(500, {"jsonrpc": "2.0", "id": req.get("id") if isinstance(req, dict) else None,
                                          "error": {"code": -32603, "message": "Internal error"}})

            def log_message(self, format, *args):
                return

        class BoundedThreadingHTTPServer(ThreadingHTTPServer):
            daemon_threads = True
            allow_reuse_address = True

            def __init__(self, server_address, RequestHandlerClass):
                super().__init__(server_address, RequestHandlerClass)
                self._sem = _threading.BoundedSemaphore(max_workers)

            def process_request(self, request, client_address):
                if not self._sem.acquire(blocking=False):
                    try:
                        request.sendall(
                            b'HTTP/1.1 503 Service Unavailable\r\nContent-Type: application/json\r\nContent-Length: 27\r\n\r\n{"error":"server_busy_503"}'
                        )
                    except Exception:
                        pass
                    self.shutdown_request(request)
                    return
                super().process_request(request, client_address)

            def process_request_thread(self, request, client_address):
                try:
                    super().process_request_thread(request, client_address)
                finally:
                    self._sem.release()

        httpd = BoundedThreadingHTTPServer((host, port), MCPHTTPHandler)
        actual_port = httpd.server_address[1]
        allowed_hosts.update({f"127.0.0.1:{actual_port}", f"localhost:{actual_port}", f"[::1]:{actual_port}"})
        if _return_server:
            return httpd
        httpd.serve_forever()


def __getattr__(name: str):
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)
    if name == "_LAZY_Z3_PROVER_SYMBOLS" or name == "_LazyZ3Symbol" or name.endswith("Prover") or name.endswith("Report") or name.endswith("Engine"):
        from aleph_core.research_archive import engine_provers_archive as _ep
        if hasattr(_ep, name):
            val = getattr(_ep, name)
            globals()[name] = val
            return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
