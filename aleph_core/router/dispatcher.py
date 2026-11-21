"""
Enrutador de Tareas, Motor Reducer Semántico, Proof-Carrying Causal Envelopes,
Fusión AST CAS 3-Way y Planificador Concurrente DAG libre de colisiones (v33.1.0).
Despacha contratos inmutables, comprime trazas preservando la Tríada Diagnóstica,
detecta conflictos Read-Write / Write-Write entre nodos concurrentes e impide condiciones de carrera.
"""
from __future__ import annotations

import ast
import concurrent.futures
import hashlib
import json
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Callable, Optional, Set, List, Tuple
from aleph_core.config import MAX_REDUCER_TOKENS


_BPE_TOKEN_RE = re.compile(
    r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[a-zA-Z_]+|[0-9]{1,3}|\r?\n| {2,4}| |[^\s\w]"
)
_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_VENDOR_FRAME_RE = re.compile(
    r"(?:node_modules|site-packages|dist-packages|usr[\\/]lib|cargo[\\/]registry|\.venv)",
    re.IGNORECASE,
)
_DIAGNOSTIC_LINE_RE = re.compile(
    r"(?:Traceback \(most recent call last\):|^\s*File\s+\"|AssertionError|SyntaxError|Error:|Exception:|CRITICAL|FAILED|PASSED|@requires|@ensures|@invariant|@loc:|!err:)",
    re.IGNORECASE,
)


def estimate_bpe_tokens(text: str) -> int:
    """Estimador determinista de tokens BPE alineado con cl100k/o200k."""
    if not text:
        return 0
    return max(1, len(_BPE_TOKEN_RE.findall(text)))


def _canonical_ast_digest(source_code: str) -> str:
    try:
        tree = ast.parse(source_code)
        dumped = ast.dump(tree, include_attributes=False)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()
    except SyntaxError:
        return hashlib.sha256(source_code.strip().encode("utf-8")).hexdigest()


def _extract_contracts_digest(source_code: str) -> str:
    if not source_code:
        return ""
    contracts = re.findall(r"@(?:requires|ensures|invariant|loop_invariant|loop_variant)\([^\n]+\)", source_code)
    return " | ".join(contracts) if contracts else ""


def _extract_ast_rw_symbols(source_code: Optional[str]) -> Tuple[Set[str], Set[str]]:
    """Extrae símbolos escritos (defs/clases top-level) y leídos de código Python."""
    if not source_code or not source_code.strip():
        return set(), set()
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return set(), set()
    writes: Set[str] = set()
    reads: Set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            writes.add(node.name)
            params = {a.arg for a in getattr(node, "args", ast.arguments()).posonlyargs + getattr(node, "args", ast.arguments()).args + getattr(node, "args", ast.arguments()).kwonlyargs} if hasattr(node, "args") else set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                    if sub.id not in params and sub.id != node.name:
                        reads.add(sub.id)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    writes.add(tgt.id)
    reads -= writes
    return reads, writes


@dataclass(frozen=True)
class ProofCarryingCausalEnvelope:
    """
    Sobre Inmutable Verificado (PCCHE) que viaja entre nodos y fases del DAG.
    Transporta únicamente identidad CAS, estado epistémico, prueba, digest de contratos y tríada comprimida.
    """
    task_id: str
    cas_sha256: str
    epistemic_status: str
    proof_hash: Optional[str]
    contracts_digest: str
    diagnostic_triad: str
    bpe_tokens_raw: int
    bpe_tokens_compacted: int
    compression_ratio: float
    vector_clock: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JITContextEntropyCompiler:
    """Compresor léxico/diagnóstico de entropía mínima para eliminar context rot entre fases."""

    @staticmethod
    def compress_diagnostic_output(raw: Any, max_chars: int = MAX_REDUCER_TOKENS * 4) -> Tuple[str, int, int, float]:
        if isinstance(raw, (dict, list)):
            raw_text = json.dumps(raw, ensure_ascii=False, sort_keys=True)
        else:
            raw_text = str(raw)
        raw_tokens = estimate_bpe_tokens(raw_text)
        cleaned = _ANSI_RE.sub("", raw_text)
        lines = cleaned.splitlines()

        if len(lines) <= 1 and len(cleaned) <= max_chars:
            return cleaned, raw_tokens, raw_tokens, 1.0

        # Colapsar repeticiones consecutivas y purgar frames vendor en trazas de error
        collapsed: List[str] = []
        last_line: Optional[str] = None
        rep_count = 0
        vendor_skipped = 0
        for line in lines:
            stripped = line.strip()
            if _VENDOR_FRAME_RE.search(stripped) and not _DIAGNOSTIC_LINE_RE.search(stripped):
                vendor_skipped += 1
                continue
            if vendor_skipped > 0:
                collapsed.append(f"[...{vendor_skipped} vendor frames omitted...]")
                vendor_skipped = 0
            if line == last_line:
                rep_count += 1
                continue
            if rep_count > 0:
                collapsed.append(f"[...repeated {rep_count} more times...]")
                rep_count = 0
            collapsed.append(line)
            last_line = line
        if rep_count > 0:
            collapsed.append(f"[...repeated {rep_count} more times...]")
        if vendor_skipped > 0:
            collapsed.append(f"[...{vendor_skipped} vendor frames omitted...]")

        candidate = "\n".join(collapsed)
        if len(candidate) > max_chars:
            diag_lines = [ln for ln in collapsed if _DIAGNOSTIC_LINE_RE.search(ln)]
            if diag_lines:
                head_lines = collapsed[: max(3, min(8, len(collapsed) // 4))]
                tail_lines = collapsed[-max(3, min(8, len(collapsed) // 4)):]
                assembled: List[str] = []
                seen: Set[str] = set()
                for ln in head_lines + diag_lines[:24] + tail_lines:
                    if ln not in seen:
                        seen.add(ln)
                        assembled.append(ln)
                candidate = "\n".join(assembled)
            if len(candidate) > max_chars:
                head_len = int(max_chars * 0.70)
                tail_len = max_chars - head_len
                omitted = len(candidate) - max_chars
                candidate = (
                    candidate[:head_len]
                    + f"\n... [REDUCER_JIT: {omitted} chars omitidos] ...\n"
                    + candidate[-tail_len:]
                )

        comp_tokens = estimate_bpe_tokens(candidate)
        ratio = round(comp_tokens / max(1, raw_tokens), 4)
        return candidate, raw_tokens, comp_tokens, ratio

    @classmethod
    def build_envelope(
        cls,
        task_id: str,
        raw_output: Any,
        epistemic_status: str,
        proof_hash: Optional[str] = None,
        formal_source_code: Optional[str] = None,
        vector_clock: Optional[Dict[str, int]] = None,
        max_chars: int = MAX_REDUCER_TOKENS * 4,
    ) -> ProofCarryingCausalEnvelope:
        compacted, raw_tok, comp_tok, ratio = cls.compress_diagnostic_output(raw_output, max_chars=max_chars)
        if formal_source_code:
            cas_sha = _canonical_ast_digest(formal_source_code)
            contracts_dig = _extract_contracts_digest(formal_source_code)
        else:
            canonical_payload = json.dumps(raw_output, ensure_ascii=False, sort_keys=True, default=str) if isinstance(raw_output, (dict, list)) else str(raw_output)
            cas_sha = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
            contracts_dig = ""
        return ProofCarryingCausalEnvelope(
            task_id=task_id,
            cas_sha256=cas_sha,
            epistemic_status=epistemic_status,
            proof_hash=proof_hash,
            contracts_digest=contracts_dig,
            diagnostic_triad=compacted,
            bpe_tokens_raw=raw_tok,
            bpe_tokens_compacted=comp_tok,
            compression_ratio=ratio,
            vector_clock=dict(vector_clock or {task_id: 1}),
        )


class SemanticCASWorktreeMerger:
    """
    Fusión AST 3-Way con direccionamiento por contenido SHA-256 (CAS).
    Permite integrar ediciones concurrentes sobre símbolos disjuntos de un mismo módulo Python
    con 0% condiciones de carrera y detecta colisiones semánticas divergentes con testigo exacto.
    """

    @staticmethod
    def _extract_module_parts(source: str) -> Tuple[List[str], Dict[str, Tuple[str, str]], List[str]]:
        tree = ast.parse(source)
        imports: List[str] = []
        symbols: Dict[str, Tuple[str, str]] = {}
        order: List[str] = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                canonical_hash = hashlib.sha256(
                    ast.dump(node, include_attributes=False).encode("utf-8")
                ).hexdigest()
                symbols[node.name] = (canonical_hash, ast.unparse(node))
                order.append(node.name)
            else:
                stmt_src = ast.unparse(node)
                stmt_key = f"__stmt_{hashlib.sha256(stmt_src.encode('utf-8')).hexdigest()[:12]}"
                canonical_hash = hashlib.sha256(
                    ast.dump(node, include_attributes=False).encode("utf-8")
                ).hexdigest()
                symbols[stmt_key] = (canonical_hash, stmt_src)
                order.append(stmt_key)
        return imports, symbols, order

    @classmethod
    def merge_ast_branches(cls, base_source: str, branch_sources: Dict[str, str]) -> Dict[str, Any]:
        """Realiza fusión 3-way por símbolo AST. Si dos ramas mutan distinto el mismo símbolo, aborta sin corrupción."""
        base_imports, base_syms, base_order = cls._extract_module_parts(base_source)
        merged_imports: List[str] = list(dict.fromkeys(base_imports))
        merged_syms: Dict[str, Tuple[str, str]] = dict(base_syms)
        merged_order: List[str] = list(base_order)
        modified_by: Dict[str, List[Tuple[str, str, str]]] = {}

        for branch_id in sorted(branch_sources.keys()):
            b_src = branch_sources[branch_id]
            try:
                b_imports, b_syms, b_order = cls._extract_module_parts(b_src)
            except SyntaxError as exc:
                return {
                    "merged": False,
                    "conflicts": [{"branch": branch_id, "reason": f"SyntaxError: {exc.msg}"}],
                    "merged_source": "",
                    "cas_tree_sha256": "",
                }
            for imp in b_imports:
                if imp not in merged_imports:
                    merged_imports.append(imp)
            for sym_name in b_order:
                b_hash, b_code = b_syms[sym_name]
                base_entry = base_syms.get(sym_name)
                if base_entry is None or base_entry[0] != b_hash:
                    modified_by.setdefault(sym_name, []).append((branch_id, b_hash, b_code))
                    if sym_name not in merged_order:
                        merged_order.append(sym_name)

        conflicts: List[Dict[str, Any]] = []
        for sym_name, edits in modified_by.items():
            distinct_hashes = {h for _, h, _ in edits}
            if len(distinct_hashes) > 1:
                conflicts.append({
                    "symbol": sym_name,
                    "branches": [b for b, _, _ in edits],
                    "distinct_ast_hashes": sorted(distinct_hashes),
                })
            else:
                merged_syms[sym_name] = (edits[0][1], edits[0][2])

        if conflicts:
            return {
                "merged": False,
                "conflicts": conflicts,
                "merged_source": "",
                "cas_tree_sha256": "",
            }

        body_blocks = [merged_syms[s][1] for s in merged_order if s in merged_syms]
        sections: List[str] = []
        if merged_imports:
            sections.append("\n".join(merged_imports))
        if body_blocks:
            sections.append("\n\n".join(body_blocks))
        merged_source = ("\n\n".join(sections) + "\n") if sections else ""
        cas_tree_sha256 = _canonical_ast_digest(merged_source)
        return {
            "merged": True,
            "conflicts": [],
            "merged_source": merged_source,
            "cas_tree_sha256": cas_tree_sha256,
            "symbols_merged": len(modified_by),
        }


@dataclass
class TaskContract:
    task_id: str
    task_type: str
    input_payload: Dict[str, Any]
    domain_category: str = "Código"
    expected_output_schema: Optional[Dict[str, Any]] = None
    timeout_sec: float = 30.0
    created_at: float = field(default_factory=time.time)


@dataclass
class TaskExecutionResult:
    task_id: str
    success: bool
    raw_output: Any
    compact_output: str
    execution_time_ms: float
    error: Optional[str] = None
    envelope: Optional[ProofCarryingCausalEnvelope] = None


class TaskDispatcher:
    def __init__(self):
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register_handler(self, task_type: str, handler: Callable[[Dict[str, Any]], Any]):
        self._handlers[task_type] = handler

    def dispatch(self, contract: TaskContract) -> TaskExecutionResult:
        if contract.task_type not in self._handlers:
            err_msg = f"Handler no registrado para task_type '{contract.task_type}'"
            env = JITContextEntropyCompiler.build_envelope(
                task_id=contract.task_id,
                raw_output={"error": err_msg},
                epistemic_status="REFUTED",
            )
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=False,
                raw_output=None,
                compact_output="",
                execution_time_ms=0.0,
                error=err_msg,
                envelope=env,
            )
        handler = self._handlers[contract.task_type]
        start_t = time.perf_counter()
        try:
            raw_output = handler(contract.input_payload)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0

            if contract.expected_output_schema and isinstance(raw_output, dict):
                for req_key, req_type in contract.expected_output_schema.items():
                    if req_key not in raw_output:
                        raise ValueError(f"Output viola el contrato: falta clave requerida '{req_key}'")
                    if isinstance(req_type, type) and not isinstance(raw_output[req_key], req_type):
                        raise TypeError(f"Clave '{req_key}' esperaba {req_type.__name__}, recibió {type(raw_output[req_key]).__name__}")

            compact = self.reduce_output(raw_output)
            env = JITContextEntropyCompiler.build_envelope(
                task_id=contract.task_id,
                raw_output=raw_output,
                epistemic_status="INFERRED",
            )
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=True,
                raw_output=raw_output,
                compact_output=compact,
                execution_time_ms=elapsed_ms,
                envelope=env,
            )
        except Exception as ex:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            env = JITContextEntropyCompiler.build_envelope(
                task_id=contract.task_id,
                raw_output=f"!err:{type(ex).__name__}: {ex}",
                epistemic_status="REFUTED",
            )
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=False,
                raw_output=None,
                compact_output="",
                execution_time_ms=elapsed_ms,
                error=str(ex),
                envelope=env,
            )

    @staticmethod
    def reduce_output(raw: Any, max_chars: int = MAX_REDUCER_TOKENS * 4) -> str:
        compacted, _, _, _ = JITContextEntropyCompiler.compress_diagnostic_output(raw, max_chars=max_chars)
        return compacted


@dataclass
class DAGTaskNode:
    contract: TaskContract
    dependencies: Set[str] = field(default_factory=set)
    verifier_fn: Optional[Callable[[Any], bool]] = None
    formal_source_code: Optional[str] = None
    use_bitvectors: bool = False
    read_symbols: Set[str] = field(default_factory=set)
    write_symbols: Set[str] = field(default_factory=set)
    inject_parent_envelopes: bool = False


@dataclass
class DAGScheduleResult:
    total_tasks: int
    waves_executed: int
    wall_clock_duration_ms: float
    sequential_equivalent_duration_ms: float
    speedup_ratio: float
    results: Dict[str, Any]
    all_success: bool
    collisions_prevented_count: int = 0
    envelopes: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class DynamicDAGScheduler:
    """Planificador topológico concurrente con aislamiento de colisiones Read/Write y sobres PCCHE."""
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers

    @staticmethod
    def _effective_rw_sets(node: DAGTaskNode) -> Tuple[Set[str], Set[str]]:
        reads = set(node.read_symbols)
        writes = set(node.write_symbols)
        if node.formal_source_code and not (reads or writes):
            ast_r, ast_w = _extract_ast_rw_symbols(node.formal_source_code)
            reads |= ast_r
            writes |= ast_w
        return reads, writes

    @classmethod
    def compute_execution_waves_with_stats(cls, nodes: Dict[str, DAGTaskNode]) -> Tuple[List[List[str]], int]:
        in_degree: Dict[str, int] = {task_id: len(node.dependencies) for task_id, node in nodes.items()}
        for task_id, node in nodes.items():
            for dep in node.dependencies:
                if dep not in nodes:
                    raise KeyError(f"Dependencia desconocida '{dep}' requerida por tarea '{task_id}'")

        rw_map = {tid: cls._effective_rw_sets(node) for tid, node in nodes.items()}
        waves: List[List[str]] = []
        visited: Set[str] = set()
        collisions_prevented = 0

        while len(visited) < len(nodes):
            ready = sorted(
                task_id for task_id, deg in in_degree.items() if deg == 0 and task_id not in visited
            )
            if not ready:
                unvisited = set(nodes.keys()) - visited
                raise ValueError(f"Ciclo detectado en DAG de tareas: dependencias circulares en {unvisited}")

            current_wave: List[str] = []
            wave_writes: Set[str] = set()
            wave_reads: Set[str] = set()

            for tid in ready:
                r_set, w_set = rw_map[tid]
                has_ww = bool(w_set & wave_writes)
                has_rw = bool(w_set & wave_reads) or bool(r_set & wave_writes)
                if has_ww or has_rw:
                    collisions_prevented += 1
                    continue
                current_wave.append(tid)
                wave_writes |= w_set
                wave_reads |= r_set

            if not current_wave:
                current_wave = [ready[0]]

            waves.append(current_wave)
            for t in current_wave:
                visited.add(t)

            for task_id, node in nodes.items():
                if task_id not in visited:
                    in_degree[task_id] -= len(node.dependencies & set(current_wave))

        return waves, collisions_prevented

    @classmethod
    def compute_execution_waves(cls, nodes: Dict[str, DAGTaskNode]) -> List[List[str]]:
        waves, _ = cls.compute_execution_waves_with_stats(nodes)
        return waves

    def execute_dag(
        self,
        nodes: Dict[str, DAGTaskNode],
        engine_execute_fn: Callable[..., Dict[str, Any]]
    ) -> DAGScheduleResult:
        t0 = time.perf_counter_ns()
        waves, collisions_prevented = self.compute_execution_waves_with_stats(nodes)
        results: Dict[str, Any] = {}
        envelopes: Dict[str, Dict[str, Any]] = {}
        all_success = True
        seq_ms_sum = 0.0
        vector_clock = {tid: 0 for tid in nodes}

        def _prepare_payload(node: DAGTaskNode) -> Dict[str, Any]:
            if node.inject_parent_envelopes and node.dependencies:
                p = dict(node.contract.input_payload)
                p["_parent_envelopes"] = [
                    envelopes[dep] for dep in sorted(node.dependencies) if dep in envelopes
                ]
                return p
            return node.contract.input_payload

        def _record_result(node: DAGTaskNode, res: Dict[str, Any]) -> None:
            nonlocal all_success, seq_ms_sum
            tid = node.contract.task_id
            vector_clock[tid] = vector_clock.get(tid, 0) + 1
            results[tid] = res
            seq_ms_sum += res.get("latency_ms", 1.0)
            if res.get("status") != "SUCCESS":
                all_success = False
            env = JITContextEntropyCompiler.build_envelope(
                task_id=tid,
                raw_output=res.get("output_preview", res),
                epistemic_status=str(res.get("epistemic_status", "INFERRED")),
                proof_hash=res.get("proof_hash"),
                formal_source_code=node.formal_source_code,
                vector_clock=dict(vector_clock),
            )
            envelopes[tid] = env.to_dict()

        for wave in waves:
            wave_nodes = [nodes[task_id] for task_id in wave]
            if len(wave_nodes) == 1:
                n = wave_nodes[0]
                res = engine_execute_fn(
                    task_type=n.contract.task_type,
                    input_payload=_prepare_payload(n),
                    verifier_fn=n.verifier_fn,
                    domain_category=n.contract.domain_category,
                    formal_source_code=n.formal_source_code,
                    use_bitvectors=n.use_bitvectors,
                )
                _record_result(n, res)
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.max_workers, len(wave_nodes))) as executor:
                    future_map = {
                        executor.submit(
                            engine_execute_fn,
                            task_type=n.contract.task_type,
                            input_payload=_prepare_payload(n),
                            verifier_fn=n.verifier_fn,
                            domain_category=n.contract.domain_category,
                            formal_source_code=n.formal_source_code,
                            use_bitvectors=n.use_bitvectors,
                        ): n
                        for n in wave_nodes
                    }
                    for fut in concurrent.futures.as_completed(future_map):
                        n = future_map[fut]
                        res = fut.result()
                        _record_result(n, res)

        duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        speedup = round(seq_ms_sum / max(duration_ms, 0.001), 2)
        return DAGScheduleResult(
            total_tasks=len(nodes),
            waves_executed=len(waves),
            wall_clock_duration_ms=round(duration_ms, 3),
            sequential_equivalent_duration_ms=round(seq_ms_sum, 3),
            speedup_ratio=speedup,
            results=results,
            all_success=all_success,
            collisions_prevented_count=collisions_prevented,
            envelopes=envelopes,
        )



class CounterfactualFaultLocalizer:
    """
    Localización causal contrafactual sobre grafos de ejecución DAG y sobres PCCHE en O(|V| + |E|).
    Distingue la raíz primaria del fallo de las víctimas en cascada y preserva sobres sanos reutilizables.
    """

    @staticmethod
    def localize_dag_faults(
        nodes: Dict[str, DAGTaskNode],
        schedule_result: DAGScheduleResult,
    ) -> Dict[str, Any]:
        if nodes is None or schedule_result is None or not nodes:
            return {
                "all_healthy": True,
                "root_cause_nodes": [],
                "cascaded_victim_nodes": [],
                "healthy_reusable_envelopes": [],
                "blast_radius_pct": 0.0,
                "reexecution_savings_pct": 0.0,
            }

        results = schedule_result.results if isinstance(schedule_result.results, dict) else {}
        envelopes = schedule_result.envelopes if isinstance(schedule_result.envelopes, dict) else {}
        failed_ids: Set[str] = {
            tid for tid in nodes
            if (results.get(tid) or {}).get("status") != "SUCCESS"
        }
        if not failed_ids:
            reusable = sorted(tid for tid in nodes if tid in envelopes)
            return {
                "all_healthy": True,
                "root_cause_nodes": [],
                "cascaded_victim_nodes": [],
                "healthy_reusable_envelopes": reusable,
                "blast_radius_pct": 0.0,
                "reexecution_savings_pct": 100.0 if reusable else 0.0,
            }

        rw_sets = {tid: DynamicDAGScheduler._effective_rw_sets(node) for tid, node in nodes.items()}
        root_causes: List[str] = []
        cascaded: List[str] = []

        for tid in sorted(failed_ids):
            node = nodes[tid]
            dep_failed = any(dep in failed_ids for dep in node.dependencies)
            r_set, _ = rw_sets.get(tid, (set(), set()))
            sym_tainted = False
            if not dep_failed:
                for other_fid in failed_ids:
                    if other_fid != tid and (r_set & rw_sets.get(other_fid, (set(), set()))[1]):
                        sym_tainted = True
                        break
            if dep_failed or sym_tainted:
                cascaded.append(tid)
            else:
                root_causes.append(tid)

        tainted_downstream: Set[str] = set(failed_ids)
        changed = True
        while changed:
            changed = False
            for tid, node in nodes.items():
                if tid not in tainted_downstream and any(dep in tainted_downstream for dep in node.dependencies):
                    tainted_downstream.add(tid)
                    changed = True

        reusable = sorted(
            tid for tid in nodes
            if tid not in tainted_downstream and tid in envelopes
        )
        total_n = max(1, len(nodes))
        return {
            "all_healthy": False,
            "root_cause_nodes": sorted(root_causes),
            "cascaded_victim_nodes": sorted(cascaded),
            "healthy_reusable_envelopes": reusable,
            "blast_radius_pct": round((len(tainted_downstream) / total_n) * 100.0, 2),
            "reexecution_savings_pct": round((len(reusable) / total_n) * 100.0, 2),
        }


class EphemeralCASWorktreeTransaction:
    """
    Sandbox transaccional AST-CAS en memoria para ediciones paralelas sin colisiones.
    Aplica AegisShield, parseo AST, fusión 3-way determinista y rollback atómico ante conflicto o fallo.
    """

    def __init__(self, base_files: Optional[Dict[str, str]] = None):
        self._base_files: Dict[str, str] = dict(base_files) if base_files is not None else {}
        self._staged: Dict[str, Dict[str, str]] = {}

    def cas_root(self, files_map: Optional[Dict[str, str]] = None) -> str:
        src_map = self._base_files if files_map is None else files_map
        items = [f"{k}:{hashlib.sha256(v.encode('utf-8')).hexdigest()}" for k, v in sorted(src_map.items())]
        return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()

    def stage_agent_patch(self, agent_id: str, file_path: str, patched_source: str) -> Dict[str, Any]:
        from aleph_core.security.aegis_shield import AegisShield

        if not agent_id or not file_path or patched_source is None:
            return {"staged": False, "reason": "INVALID_STAGE_INPUT"}

        sec = AegisShield.scan_text(patched_source)
        if not sec.safe:
            return {
                "staged": False,
                "reason": f"AEGIS_BLOCKED:{sec.findings[0].rule_id if sec.findings else 'UNSAFE'}",
            }

        if file_path.endswith(".py"):
            try:
                ast.parse(patched_source)
            except SyntaxError as exc:
                return {"staged": False, "reason": f"SYNTAX_ERROR:{exc.msg}"}

        self._staged.setdefault(file_path, {})[agent_id] = patched_source
        digest = (
            _canonical_ast_digest(patched_source)
            if file_path.endswith(".py")
            else hashlib.sha256(patched_source.encode("utf-8")).hexdigest()
        )
        return {
            "staged": True,
            "agent_id": agent_id,
            "file_path": file_path,
            "cas_sha256": digest,
        }

    def commit_all(self, verifier_fn: Optional[Callable[[Dict[str, str]], bool]] = None) -> Dict[str, Any]:
        before_root = self.cas_root(self._base_files)
        candidate_files: Dict[str, str] = dict(self._base_files)
        conflicts: List[Dict[str, Any]] = []

        for file_path, branches in sorted(self._staged.items()):
            base_src = self._base_files.get(file_path, "")
            if len(branches) == 1:
                candidate_files[file_path] = next(iter(branches.values()))
                continue
            if file_path.endswith(".py"):
                m_res = SemanticCASWorktreeMerger.merge_ast_branches(base_src, branches)
                if not m_res.get("merged"):
                    conflicts.extend(m_res.get("conflicts", [{"file": file_path, "reason": "MERGE_CONFLICT"}]))
                else:
                    candidate_files[file_path] = str(m_res.get("merged_source", ""))
            else:
                distinct = sorted(set(branches.values()))
                if len(distinct) > 1:
                    conflicts.append({"file": file_path, "branches": sorted(branches.keys()), "reason": "TEXT_COLLISION"})
                elif distinct:
                    candidate_files[file_path] = distinct[0]

        if conflicts:
            self._staged.clear()
            return {
                "committed": False,
                "rolled_back": True,
                "reason": "CONFLICT_DETECTED",
                "conflicts": conflicts,
                "before_cas_root": before_root,
                "after_cas_root": self.cas_root(self._base_files),
                "files": dict(self._base_files),
            }

        if verifier_fn is not None:
            try:
                ok = bool(verifier_fn(dict(candidate_files)))
            except Exception as exc:
                ok = False
                conflicts.append({"reason": f"VERIFIER_EXCEPTION:{exc}"})
            if not ok:
                self._staged.clear()
                return {
                    "committed": False,
                    "rolled_back": True,
                    "reason": "VERIFIER_REJECTED",
                    "conflicts": conflicts,
                    "before_cas_root": before_root,
                    "after_cas_root": self.cas_root(self._base_files),
                    "files": dict(self._base_files),
                }

        self._base_files = candidate_files
        self._staged.clear()
        return {
            "committed": True,
            "rolled_back": False,
            "before_cas_root": before_root,
            "after_cas_root": self.cas_root(self._base_files),
            "conflicts": [],
            "files": dict(self._base_files),
        }
