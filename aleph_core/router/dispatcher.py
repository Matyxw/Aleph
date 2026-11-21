"""
Enrutador de Tareas, Motor Reducer Semántico, Proof-Carrying Causal Envelopes,
Fusión Políglota AST/JSON/Bloques CAS 3-Way, Localizador Causal Contrafactual
y Sandbox Transaccional con git worktree reales libre de colisiones (v33.2.0).
"""
from __future__ import annotations

import ast
import concurrent.futures
import difflib
import hashlib
import json
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
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
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


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
            args_obj = getattr(node, "args", None)
            params: Set[str] = set()
            if args_obj is not None:
                params = {
                    a.arg
                    for a in list(getattr(args_obj, "posonlyargs", []))
                    + list(getattr(args_obj, "args", []))
                    + list(getattr(args_obj, "kwonlyargs", []))
                }
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

    def verify_integrity(
        self,
        raw_output: Any = None,
        formal_source_code: Optional[str] = None,
    ) -> bool:
        """Verifica formato CAS SHA-256 y coincidencia determinista si se aporta el contenido original."""
        if not self.task_id or not _HEX64_RE.match(self.cas_sha256):
            return False
        if self.bpe_tokens_compacted < 0 or self.bpe_tokens_raw < 0:
            return False
        if formal_source_code is not None:
            return self.cas_sha256 == _canonical_ast_digest(formal_source_code)
        if raw_output is not None:
            canonical_payload = (
                json.dumps(raw_output, ensure_ascii=False, sort_keys=True, default=str)
                if isinstance(raw_output, (dict, list))
                else str(raw_output)
            )
            expected = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
            return self.cas_sha256 == expected
        return True


class JITContextEntropyCompiler:
    """Compresor léxico/diagnóstico de entropía mínima para eliminar context rot entre fases."""

    @staticmethod
    def compress_diagnostic_output(raw: Any, max_chars: int = MAX_REDUCER_TOKENS * 4) -> Tuple[str, int, int, float]:
        if isinstance(raw, (dict, list)):
            raw_text = json.dumps(raw, ensure_ascii=False, sort_keys=True, default=str)
        else:
            raw_text = "" if raw is None else str(raw)
        raw_tokens = estimate_bpe_tokens(raw_text)
        cleaned = _ANSI_RE.sub("", raw_text)
        lines = cleaned.splitlines()

        if len(lines) <= 1 and len(cleaned) <= max_chars:
            return cleaned, raw_tokens, raw_tokens, 1.0

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
            canonical_payload = (
                json.dumps(raw_output, ensure_ascii=False, sort_keys=True, default=str)
                if isinstance(raw_output, (dict, list))
                else str(raw_output)
            )
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
    Fusión Políglota 3-Way con direccionamiento por contenido SHA-256 (CAS):
    - Python (.py): Fusión por símbolo AST top-level.
    - JSON (.json): Fusión estructural recursiva por ruta de clave.
    - Resto de lenguajes (.ts, .tsx, .js, .rs, .go, .md, .sh, .yaml, .yml, .toml):
      Fusión determinista 3-way por bloques/hunks de líneas con detección de solapamientos.
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
        if branch_sources is None or not branch_sources:
            src = "" if base_source is None else base_source
            return {
                "merged": True,
                "conflicts": [],
                "merged_source": src,
                "cas_tree_sha256": _canonical_ast_digest(src),
                "symbols_merged": 0,
            }
        base_imports, base_syms, base_order = cls._extract_module_parts(base_source or "")
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

    @classmethod
    def _merge_json_dicts(
        cls,
        base_obj: Dict[str, Any],
        branch_objs: Dict[str, Dict[str, Any]],
        prefix: str = "",
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        sentinel = object()
        all_keys: Set[str] = set(base_obj.keys())
        for obj in branch_objs.values():
            all_keys |= set(obj.keys())

        merged: Dict[str, Any] = {}
        conflicts: List[Dict[str, Any]] = []

        for key in sorted(all_keys):
            key_path = f"{prefix}.{key}" if prefix else key
            base_val = base_obj.get(key, sentinel)
            deltas: List[Tuple[str, Any]] = []
            for bid in sorted(branch_objs.keys()):
                b_val = branch_objs[bid].get(key, sentinel)
                if b_val != base_val:
                    deltas.append((bid, b_val))

            if not deltas:
                if base_val is not sentinel:
                    merged[key] = base_val
                continue

            distinct_encoded = {
                json.dumps(v, sort_keys=True, ensure_ascii=False) if v is not sentinel else "__DELETED__"
                for _, v in deltas
            }
            if len(distinct_encoded) == 1:
                chosen = deltas[0][1]
                if chosen is not sentinel:
                    merged[key] = chosen
                continue

            if all(isinstance(v, dict) for _, v in deltas) and (isinstance(base_val, dict) or base_val is sentinel):
                sub_base = base_val if isinstance(base_val, dict) else {}
                sub_branches = {
                    bid: (branch_objs[bid][key] if isinstance(branch_objs[bid].get(key), dict) else sub_base)
                    for bid in branch_objs
                }
                sub_merged, sub_conflicts = cls._merge_json_dicts(sub_base, sub_branches, prefix=key_path)
                if sub_conflicts:
                    conflicts.extend(sub_conflicts)
                else:
                    merged[key] = sub_merged
            else:
                conflicts.append({
                    "json_path": key_path,
                    "branches": [bid for bid, _ in deltas],
                    "reason": "JSON_VALUE_COLLISION",
                })
        return merged, conflicts

    @classmethod
    def merge_json_branches(cls, base_source: str, branch_sources: Dict[str, str]) -> Dict[str, Any]:
        """Fusión estructural 3-way para archivos JSON."""
        if not branch_sources:
            src = "{}" if not (base_source or "").strip() else base_source
            return {
                "merged": True,
                "conflicts": [],
                "merged_source": src,
                "cas_tree_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
            }
        try:
            base_obj = json.loads(base_source) if (base_source or "").strip() else {}
        except json.JSONDecodeError as exc:
            return {
                "merged": False,
                "conflicts": [{"branch": "base", "reason": f"JSONDecodeError:{exc.msg}"}],
                "merged_source": "",
                "cas_tree_sha256": "",
            }
        parsed_branches: Dict[str, Dict[str, Any]] = {}
        for bid, b_src in sorted(branch_sources.items()):
            try:
                loaded = json.loads(b_src)
            except json.JSONDecodeError as exc:
                return {
                    "merged": False,
                    "conflicts": [{"branch": bid, "reason": f"JSONDecodeError:{exc.msg}"}],
                    "merged_source": "",
                    "cas_tree_sha256": "",
                }
            if not isinstance(loaded, dict) or not isinstance(base_obj, dict):
                return cls.merge_line_blocks_3way(base_source, branch_sources)
            parsed_branches[bid] = loaded

        merged_dict, conflicts = cls._merge_json_dicts(base_obj, parsed_branches)
        if conflicts:
            return {
                "merged": False,
                "conflicts": conflicts,
                "merged_source": "",
                "cas_tree_sha256": "",
            }
        merged_source = json.dumps(merged_dict, indent=2, ensure_ascii=False) + "\n"
        return {
            "merged": True,
            "conflicts": [],
            "merged_source": merged_source,
            "cas_tree_sha256": hashlib.sha256(merged_source.encode("utf-8")).hexdigest(),
        }

    @staticmethod
    def _hunks_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
        if a_start == a_end and b_start == b_end:
            return a_start == b_start
        if a_start == a_end:
            return b_start < a_start < b_end
        if b_start == b_end:
            return a_start < b_start < a_end
        return a_start < b_end and b_start < a_end

    @classmethod
    def merge_line_blocks_3way(cls, base_source: str, branch_sources: Dict[str, str]) -> Dict[str, Any]:
        """Fusión 3-way determinista por bloques de líneas para archivos políglotas no-Python."""
        base_text = "" if base_source is None else base_source
        if not branch_sources:
            return {
                "merged": True,
                "conflicts": [],
                "merged_source": base_text,
                "cas_tree_sha256": hashlib.sha256(base_text.encode("utf-8")).hexdigest(),
            }

        base_lines = base_text.splitlines(keepends=True)
        # (i1, i2, replacement_tuple, branch_id)
        all_edits: List[Tuple[int, int, Tuple[str, ...], str]] = []
        for bid in sorted(branch_sources.keys()):
            b_text = "" if branch_sources[bid] is None else branch_sources[bid]
            b_lines = b_text.splitlines(keepends=True)
            sm = difflib.SequenceMatcher(None, base_lines, b_lines, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != "equal":
                    all_edits.append((i1, i2, tuple(b_lines[j1:j2]), bid))

        if not all_edits:
            return {
                "merged": True,
                "conflicts": [],
                "merged_source": base_text,
                "cas_tree_sha256": hashlib.sha256(base_text.encode("utf-8")).hexdigest(),
            }

        unique_edits: Dict[Tuple[int, int, Tuple[str, ...]], List[str]] = {}
        for i1, i2, rep, bid in all_edits:
            unique_edits.setdefault((i1, i2, rep), []).append(bid)

        sorted_ops = sorted(unique_edits.keys(), key=lambda x: (x[0], x[1]))
        conflicts: List[Dict[str, Any]] = []
        for idx, op_a in enumerate(sorted_ops):
            a_i1, a_i2, a_rep = op_a
            for op_b in sorted_ops[idx + 1:]:
                b_i1, b_i2, b_rep = op_b
                if cls._hunks_overlap(a_i1, a_i2, b_i1, b_i2):
                    conflicts.append({
                        "line_range": [min(a_i1, b_i1) + 1, max(a_i2, b_i2) + 1],
                        "branches": sorted(set(unique_edits[op_a] + unique_edits[op_b])),
                        "reason": "OVERLAPPING_HUNK_COLLISION",
                    })

        if conflicts:
            return {
                "merged": False,
                "conflicts": conflicts,
                "merged_source": "",
                "cas_tree_sha256": "",
            }

        out_lines: List[str] = []
        cursor = 0
        for i1, i2, rep, in sorted_ops:
            if cursor < i1:
                out_lines.extend(base_lines[cursor:i1])
            out_lines.extend(rep)
            cursor = i2
        if cursor < len(base_lines):
            out_lines.extend(base_lines[cursor:])

        merged_source = "".join(out_lines)
        return {
            "merged": True,
            "conflicts": [],
            "merged_source": merged_source,
            "cas_tree_sha256": hashlib.sha256(merged_source.encode("utf-8")).hexdigest(),
            "hunks_merged": len(sorted_ops),
        }

    @classmethod
    def merge_polyglot_branches(
        cls,
        file_path: str,
        base_source: str,
        branch_sources: Dict[str, str],
    ) -> Dict[str, Any]:
        """Despacha estrategia de fusión determinista 3-way según extensión del archivo."""
        ext = Path(file_path).suffix.lower() if file_path else ""
        if ext == ".py":
            return cls.merge_ast_branches(base_source, branch_sources)
        if ext == ".json":
            return cls.merge_json_branches(base_source, branch_sources)
        return cls.merge_line_blocks_3way(base_source, branch_sources)


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
            err = f"Capacidad no registrada: {contract.task_type}"
            env = JITContextEntropyCompiler.build_envelope(
                task_id=contract.task_id,
                raw_output=f"!err:{err}",
                epistemic_status="REFUTED",
            )
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=False,
                raw_output=None,
                compact_output="",
                execution_time_ms=0.0,
                error=err,
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
    compute_allocation: Dict[str, Any] = field(default_factory=dict)
    fault_localization: Dict[str, Any] = field(default_factory=dict)
    worktree_transaction: Dict[str, Any] = field(default_factory=dict)


class DynamicDAGScheduler:
    """
    Planificador topológico concurrente con aislamiento de colisiones Read/Write,
    asignación cognitiva asimétrica, sobres PCCHE, fusión AST/políglota CAS y localización causal contrafactual.
    """

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers

    @staticmethod
    def _effective_rw_sets(node: DAGTaskNode) -> Tuple[Set[str], Set[str]]:
        if node is None:
            return set(), set()
        reads = set(node.read_symbols)
        writes = set(node.write_symbols)
        if node.formal_source_code and not (reads or writes):
            ast_r, ast_w = _extract_ast_rw_symbols(node.formal_source_code)
            reads |= ast_r
            writes |= ast_w
        return reads, writes

    @classmethod
    def compute_execution_waves_with_stats(cls, nodes: Dict[str, DAGTaskNode]) -> Tuple[List[List[str]], int]:
        if nodes is None or not nodes:
            return [], 0
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
        engine_execute_fn: Callable[..., Dict[str, Any]],
        base_files: Optional[Dict[str, str]] = None,
    ) -> DAGScheduleResult:
        from aleph_core.router.cost_router import SovereignCostRouter

        t0 = time.perf_counter_ns()
        if nodes is None or not nodes:
            return DAGScheduleResult(
                total_tasks=0,
                waves_executed=0,
                wall_clock_duration_ms=0.0,
                sequential_equivalent_duration_ms=0.0,
                speedup_ratio=1.0,
                results={},
                all_success=True,
                collisions_prevented_count=0,
                envelopes={},
                compute_allocation=SovereignCostRouter.allocate_dag_compute({}),
                fault_localization=CounterfactualFaultLocalizer.localize_dag_faults({}, None),
                worktree_transaction={},
            )

        node_prompts: Dict[str, str] = {}
        for tid, n in nodes.items():
            raw_p = n.contract.input_payload.get("prompt") or n.contract.input_payload.get("raw_text") or json.dumps(
                n.contract.input_payload, ensure_ascii=False, sort_keys=True, default=str
            )
            node_prompts[tid] = f"{raw_p}\n{n.formal_source_code or ''}".strip()
        compute_alloc = SovereignCostRouter.allocate_dag_compute(node_prompts)

        waves, collisions_prevented = self.compute_execution_waves_with_stats(nodes)
        results: Dict[str, Any] = {}
        envelopes: Dict[str, Dict[str, Any]] = {}
        all_success = True
        seq_ms_sum = 0.0
        vector_clock = {tid: 0 for tid in nodes}
        staged_patches: List[Tuple[str, str, str]] = []

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

            patch_map = node.contract.input_payload.get("file_patches")
            if res.get("status") == "SUCCESS" and isinstance(patch_map, dict):
                for fp, src in patch_map.items():
                    if isinstance(src, str):
                        staged_patches.append((tid, str(fp), src))

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

        worktree_tx_report: Dict[str, Any] = {}
        if base_files is not None or staged_patches:
            tx = EphemeralCASWorktreeTransaction(base_files or {})
            stage_errors: List[Dict[str, Any]] = []
            for tid, fp, src in staged_patches:
                st = tx.stage_agent_patch(tid, fp, src)
                if not st.get("staged"):
                    stage_errors.append({"task_id": tid, "file_path": fp, "reason": st.get("reason")})
            if stage_errors:
                worktree_tx_report = {
                    "committed": False,
                    "rolled_back": True,
                    "reason": "STAGE_REJECTED",
                    "conflicts": stage_errors,
                }
            else:
                worktree_tx_report = tx.commit_all()

        duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        speedup = round(seq_ms_sum / max(duration_ms, 0.001), 2)
        sched_res = DAGScheduleResult(
            total_tasks=len(nodes),
            waves_executed=len(waves),
            wall_clock_duration_ms=round(duration_ms, 3),
            sequential_equivalent_duration_ms=round(seq_ms_sum, 3),
            speedup_ratio=speedup,
            results=results,
            all_success=all_success,
            collisions_prevented_count=collisions_prevented,
            envelopes=envelopes,
            compute_allocation=compute_alloc,
            worktree_transaction=worktree_tx_report,
        )
        sched_res.fault_localization = CounterfactualFaultLocalizer.localize_dag_faults(nodes, sched_res)
        return sched_res


class CounterfactualFaultLocalizer:
    """
    Localización causal contrafactual sobre grafos de ejecución DAG y sobres PCCHE en O(|V| + |E|).
    Distingue la raíz primaria del fallo de las víctimas en cascada y preserva sobres sanos reutilizables.
    """

    @staticmethod
    def localize_dag_faults(
        nodes: Optional[Dict[str, DAGTaskNode]],
        schedule_result: Optional[DAGScheduleResult],
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
    Sandbox transaccional políglota AST/JSON/Bloques-CAS para ediciones paralelas sin colisiones,
    con soporte de escritura atómica en disco, recuperación ante fallos parciales y git worktrees reales.
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

        ext = Path(file_path).suffix.lower()
        if ext == ".py":
            try:
                ast.parse(patched_source)
            except SyntaxError as exc:
                return {"staged": False, "reason": f"SYNTAX_ERROR:{exc.msg}"}
        elif ext == ".json":
            try:
                json.loads(patched_source)
            except json.JSONDecodeError as exc:
                return {"staged": False, "reason": f"JSON_ERROR:{exc.msg}"}

        self._staged.setdefault(file_path, {})[agent_id] = patched_source
        digest = (
            _canonical_ast_digest(patched_source)
            if ext == ".py"
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
            m_res = SemanticCASWorktreeMerger.merge_polyglot_branches(file_path, base_src, branches)
            if not m_res.get("merged"):
                conflicts.extend(m_res.get("conflicts", [{"file": file_path, "reason": "MERGE_CONFLICT"}]))
            else:
                candidate_files[file_path] = str(m_res.get("merged_source", ""))

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

    def commit_to_disk(
        self,
        workspace_dir: Path,
        verifier_fn: Optional[Callable[[Dict[str, str]], bool]] = None,
        simulate_crash_after_n_files: int = 0,
    ) -> Dict[str, Any]:
        """Persiste la transacción en disco atómicamente con rollback completo ante fallo o caída parcial."""
        from aleph_core.state.store import StateStore

        if workspace_dir is None:
            return {"committed": False, "rolled_back": True, "reason": "INVALID_WORKSPACE", "conflicts": []}

        ws_path = Path(workspace_dir)
        prev_base = dict(self._base_files)
        target_rels = sorted(set(self._base_files.keys()) | set(self._staged.keys()))
        disk_before_exists: Dict[str, bool] = {}
        disk_before_text: Dict[str, str] = {}
        for rel in target_rels:
            fp = ws_path / rel
            disk_before_exists[rel] = fp.exists()
            if fp.exists():
                disk_before_text[rel] = fp.read_text(encoding="utf-8", errors="replace")

        res = self.commit_all(verifier_fn=verifier_fn)
        if not res.get("committed"):
            return res

        committed_files: Dict[str, str] = res.get("files", {})
        written_rels: List[str] = []
        try:
            for idx, (rel, content) in enumerate(sorted(committed_files.items()), 1):
                StateStore.atomic_write_file(ws_path / rel, content)
                written_rels.append(rel)
                if simulate_crash_after_n_files > 0 and idx >= simulate_crash_after_n_files:
                    raise RuntimeError(f"SIMULATED_MID_TX_CRASH_AT_FILE_{idx}")
        except Exception as exc:
            for rel in written_rels:
                fp = ws_path / rel
                if disk_before_exists.get(rel, False):
                    StateStore.atomic_write_file(fp, disk_before_text.get(rel, ""))
                elif fp.exists():
                    fp.unlink()
            self._base_files = prev_base
            return {
                "committed": False,
                "rolled_back": True,
                "reason": f"DISK_TX_ABORTED:{exc}",
                "conflicts": [{"reason": str(exc)}],
                "before_cas_root": res.get("before_cas_root", ""),
                "after_cas_root": self.cas_root(self._base_files),
                "files": dict(self._base_files),
            }

        res["written_to_disk"] = written_rels
        return res

    @classmethod
    def execute_git_worktree_parallel_tx(
        cls,
        repo_dir: Path,
        branch_patches: Dict[str, Dict[str, str]],
        max_workers: int = 4,
        verifier_fn: Optional[Callable[[Dict[str, str]], bool]] = None,
        simulate_crash_after_n_files: int = 0,
    ) -> Dict[str, Any]:
        """
        Ejecuta workers concurrentes reales sobre `git worktree` temporales físicos en disco,
        fusiona los resultados mediante SemanticCASWorktreeMerger y persiste vía `commit_to_disk`.
        """
        if repo_dir is None or branch_patches is None or not branch_patches:
            return {"committed": False, "rolled_back": True, "reason": "INVALID_GIT_WORKTREE_INPUT", "conflicts": []}

        repo_path = Path(repo_dir)
        all_rels = sorted({rel for files in branch_patches.values() for rel in files.keys()})
        base_files: Dict[str, str] = {}
        for rel in all_rels:
            fp = repo_path / rel
            base_files[rel] = fp.read_text(encoding="utf-8", errors="replace") if fp.exists() else ""

        tx = cls(base_files=base_files)
        disk_results: Dict[str, Dict[str, str]] = {}
        stage_rejections: List[Dict[str, Any]] = []

        with tempfile.TemporaryDirectory(prefix="awt_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            created_wts: List[Path] = []

            def _run_worker(agent_id: str, patches: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
                safe_id = re.sub(r"[^A-Za-z0-9_-]+", "_", agent_id)
                wt_dir = tmp_path / safe_id
                subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "add", "--detach", str(wt_dir), "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                created_wts.append(wt_dir)
                from aleph_core.state.store import StateStore
                observed: Dict[str, str] = {}
                for rel, new_src in patches.items():
                    target = wt_dir / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    StateStore.atomic_write_file(target, new_src)
                    observed[rel] = target.read_text(encoding="utf-8", errors="replace")
                return agent_id, observed

            try:
                workers_n = min(max(1, max_workers), len(branch_patches))
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers_n) as pool:
                    futs = {
                        pool.submit(_run_worker, aid, patches): aid
                        for aid, patches in sorted(branch_patches.items())
                    }
                    for fut in concurrent.futures.as_completed(futs):
                        aid, observed = fut.result()
                        disk_results[aid] = observed
            finally:
                for wt_dir in created_wts:
                    subprocess.run(
                        ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_dir)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "prune"],
                    check=False,
                    capture_output=True,
                    text=True,
                )

        for aid, observed in sorted(disk_results.items()):
            for rel, content in sorted(observed.items()):
                st = tx.stage_agent_patch(aid, rel, content)
                if not st.get("staged"):
                    stage_rejections.append({"agent_id": aid, "file_path": rel, "reason": st.get("reason")})

        if stage_rejections:
            before_root = tx.cas_root(base_files)
            return {
                "committed": False,
                "rolled_back": True,
                "reason": "STAGE_REJECTED",
                "conflicts": stage_rejections,
                "before_cas_root": before_root,
                "after_cas_root": before_root,
                "worktrees_executed": len(branch_patches),
                "files": base_files,
            }

        out = tx.commit_to_disk(
            repo_path,
            verifier_fn=verifier_fn,
            simulate_crash_after_n_files=simulate_crash_after_n_files,
        )
        out["worktrees_executed"] = len(branch_patches)
        out["workers_used"] = min(max(1, max_workers), len(branch_patches))
        return out
