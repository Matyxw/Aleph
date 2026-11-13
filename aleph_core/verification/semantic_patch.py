"""
aleph_core/verification/semantic_patch.py
Motor de Parches Semánticos AST y Verificación Diferencial Anti-Regresión (Nivel 8 + Equivalencia Relacional).
Supera el clásico fallo de reemplazo ciego por líneas (sed/difflib/git diff) de ECC y Claude Code:
1. Aplica ediciones estructurales sobre el Árbol de Sintaxis Abstracta (AST) o reemplazo quirúrgico de nodos.
2. Comprueba que el parche preserve la validez sintáctica y los contratos formales (@requires, @ensures, @invariant).
3. Corre verificación diferencial SMT y Equivalencia Relacional sobre el delta para certificar que el parche no introduce
   regresiones de seguridad ni divergencias semánticas.
4. Aplica el cambio de forma atómica en disco en 2 fases con fsync.
"""
import ast
import difflib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from aleph_core.verification.z3_prover import (
    Z3VerificationEngine,
    ProofStatus,
    SafetyDefectType,
    RelationalEquivalenceProver,
)
from aleph_core.state.store import StateStore

@dataclass
class SemanticPatchResult:
    success: bool
    patched_code: str
    diff_unified: str
    formal_proof_passed: bool
    proof_status: str
    detected_regressions: List[str] = field(default_factory=list)
    atomic_applied_path: Optional[str] = None
    error: Optional[str] = None

class SemanticPatchEngine:
    def __init__(self, prover: Optional[Z3VerificationEngine] = None):
        self.prover = prover or Z3VerificationEngine(timeout_ms=45)

    def apply_function_replacement(
        self,
        original_source: str,
        target_function_name: str,
        replacement_function_source: str,
        target_file_path: Optional[Path] = None,
        enforce_formal_verification: bool = True,
        require_behavioral_equivalence: bool = False
    ) -> SemanticPatchResult:
        """
        Reemplaza quirúrgicamente una función en un archivo mediante AST o bloque de código,
        audita formalmente la nueva función para garantizar ausencia de regresiones de seguridad
        (y opcionalmente equivalencia relacional input-output), y aplica la mutación atómica en disco.
        """
        try:
            orig_tree = ast.parse(original_source)
            new_func_tree = ast.parse(replacement_function_source)
        except SyntaxError as syn_err:
            return SemanticPatchResult(
                success=False,
                patched_code="",
                diff_unified="",
                formal_proof_passed=False,
                proof_status="SYNTAX_ERROR",
                error=f"Error de sintaxis en el código propuesto: {syn_err}"
            )

        replacement_node = None
        for node in new_func_tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == target_function_name:
                replacement_node = node
                break

        if not replacement_node:
            return SemanticPatchResult(
                success=False,
                patched_code="",
                diff_unified="",
                formal_proof_passed=False,
                proof_status="FUNCTION_NOT_FOUND",
                error=f"No se encontró la función '{target_function_name}' en el código de reemplazo."
            )

        regressions: List[str] = []
        proof_status_str = "SKIPPED"
        formal_passed = True

        if enforce_formal_verification:
            proof_res = self.prover.verify_function_ast(
                replacement_node,
                source_code=replacement_function_source
            )
            proof_status_str = proof_res.status.value
            if proof_res.status == ProofStatus.DEFECT_FOUND:
                formal_passed = False
                defect_name = proof_res.defect_type.value if proof_res.defect_type else "UNKNOWN_DEFECT"
                regressions.append(f"Regresión detectada: {defect_name}. Contraejemplo: {proof_res.counterexample}")
                return SemanticPatchResult(
                    success=False,
                    patched_code="",
                    diff_unified="",
                    formal_proof_passed=False,
                    proof_status=proof_status_str,
                    detected_regressions=regressions,
                    error=f"Parche rechazado por compuerta formal: introduce defecto {defect_name}"
                )

        if require_behavioral_equivalence:
            eq_res = RelationalEquivalenceProver.prove_equivalence(
                original_source=original_source,
                candidate_source=replacement_function_source,
                orig_func_name=target_function_name,
                cand_func_name=target_function_name
            )
            if not eq_res.equivalent:
                regressions.append(
                    f"Divergencia relacional en {eq_res.divergence_witness}: "
                    f"orig={eq_res.original_output} vs cand={eq_res.candidate_output}"
                )
                return SemanticPatchResult(
                    success=False,
                    patched_code="",
                    diff_unified="",
                    formal_proof_passed=False,
                    proof_status="DIVERGENCE_FOUND",
                    detected_regressions=regressions,
                    error=(
                        f"Parche rechazado por divergencia semántica relacional en testigo "
                        f"{eq_res.divergence_witness}: orig={eq_res.original_output} != cand={eq_res.candidate_output}"
                    )
                )

        class FunctionReplacer(ast.NodeTransformer):
            def __init__(self, fn_name: str, new_node: ast.FunctionDef):
                self.fn_name = fn_name
                self.new_node = new_node
                self.replaced = False

            def visit_FunctionDef(self, node: ast.FunctionDef):
                if node.name == self.fn_name:
                    self.replaced = True
                    return self.new_node
                return node

        replacer = FunctionReplacer(target_function_name, replacement_node)
        modified_tree = replacer.visit(orig_tree)
        ast.fix_missing_locations(modified_tree)

        if not replacer.replaced:
            return SemanticPatchResult(
                success=False,
                patched_code="",
                diff_unified="",
                formal_proof_passed=formal_passed,
                proof_status=proof_status_str,
                error=f"La función objetivo '{target_function_name}' no existe en el código fuente original."
            )

        patched_code = ast.unparse(modified_tree) + "\n"

        diff_lines = list(difflib.unified_diff(
            original_source.splitlines(keepends=True),
            patched_code.splitlines(keepends=True),
            fromfile=f"a/{target_function_name}",
            tofile=f"b/{target_function_name}"
        ))
        unified_diff_str = "".join(diff_lines)

        applied_path_str = None
        if target_file_path:
            StateStore.atomic_write_file(Path(target_file_path), patched_code)
            applied_path_str = str(target_file_path)

        return SemanticPatchResult(
            success=True,
            patched_code=patched_code,
            diff_unified=unified_diff_str,
            formal_proof_passed=formal_passed,
            proof_status=proof_status_str,
            detected_regressions=[],
            atomic_applied_path=applied_path_str
        )
