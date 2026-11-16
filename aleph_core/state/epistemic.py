"""
Taxonomía Epistémica y Compuerta de Verificación Mecánica (v2.0).
Prohíbe que el modelo o agente se autoasigne certeza sin prueba determinista ejecutable.
Integra en cascada: Z3 SMT / Symbolic Prover -> Property-Based Testing -> Predicado Empírico.
"""
import ast
import hashlib
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Dict

class EpistemicStatus(str, Enum):
    INFERRED = "INFERRED"               # Afirmación cruda no verificada
    VERIFIED = "VERIFIED"               # Verificación empírica (tests unitarios finitos, exit code 0)
    PBT_VERIFIED = "PBT_VERIFIED"       # Verificación basada en propiedades (fuzzing acotado)
    FORMALLY_PROVEN = "FORMALLY_PROVEN" # Certeza matemática/simbólica (0 contraejemplos en dominio)
    REFUTED = "REFUTED"                 # Refutado por test o contraejemplo concreto verificado en runtime

@dataclass
class EpistemicClaim:
    claim_id: str
    description: str
    payload: Any
    status: EpistemicStatus = EpistemicStatus.INFERRED
    proof_hash: Optional[str] = None
    proof_output: Optional[str] = None
    verified_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "description": self.description,
            "payload": self.payload,
            "status": self.status.value,
            "proof_hash": self.proof_hash,
            "proof_output": self.proof_output,
            "verified_at": self.verified_at,
            "metadata": self.metadata,
        }

class VerificationGate:
    """
    Compuerta determinista de paso obligado.
    Ninguna afirmación o resultado se promueve a VERIFIED, PBT_VERIFIED o FORMALLY_PROVEN sin prueba mecánica.
    """
    @staticmethod
    def verify(
        claim: EpistemicClaim,
        verifier_fn: Callable[[Any], bool],
        proof_context: Optional[str] = None
    ) -> EpistemicClaim:
        if claim.status in (EpistemicStatus.VERIFIED, EpistemicStatus.PBT_VERIFIED, EpistemicStatus.FORMALLY_PROVEN):
            return claim
        try:
            passed = bool(verifier_fn(claim.payload))
            now = time.time()
            if passed:
                claim.status = EpistemicStatus.VERIFIED
                claim.verified_at = now
                proof_data = f"{claim.claim_id}:{now}:{proof_context or 'passed'}"
                claim.proof_hash = hashlib.sha256(proof_data.encode("utf-8")).hexdigest()
                claim.proof_output = proof_context or "Verification predicate passed successfully."
            else:
                claim.status = EpistemicStatus.REFUTED
                claim.proof_output = "Verification predicate returned False."
        except Exception as ex:
            claim.status = EpistemicStatus.REFUTED
            claim.proof_output = f"Verification predicate raised exception: {str(ex)}"
        return claim

    @staticmethod
    def verify_formal(
        claim: EpistemicClaim,
        func_node: Any = None,
        source_code: str = "",
        timeout_ms: int = 45,
        use_bitvectors: bool = False,
        auto_pbt_fallback: bool = True
    ) -> EpistemicClaim:
        """
        Eleva la compuerta epistemológica a demostración formal (Z3 / Symbolic Interval Solver).
        Si la prueba formal resulta TIMEOUT_OR_UNKNOWN y auto_pbt_fallback=True, degrada
        automáticamente a PropertyBasedFallback para evitar quedar en estado INFERRED.
        """
        from aleph_core.verification.z3_prover import Z3VerificationEngine, ProofStatus
        from aleph_core.verification.pbt_fallback import PropertyBasedFallback

        if func_node is None and source_code:
            tree = ast.parse(source_code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_node = node
                    break

        if func_node is None:
            claim.status = EpistemicStatus.REFUTED
            claim.proof_output = "No se encontró un nodo FunctionDef válido para verificar."
            return claim

        engine = Z3VerificationEngine(timeout_ms=timeout_ms)
        proof = engine.verify_function_ast(func_node, source_code=source_code, use_bitvectors=use_bitvectors)
        now = time.time()

        if proof.status == ProofStatus.PROVEN_SAFE:
            claim.status = EpistemicStatus.FORMALLY_PROVEN
            claim.verified_at = now
            proof_data = f"{claim.claim_id}:{now}:FORMALLY_PROVEN:{proof.theories_used}:{func_node.name}"
            claim.proof_hash = hashlib.sha256(proof_data.encode("utf-8")).hexdigest()
            claim.proof_output = (
                f"Demostrado formalmente en {proof.solver_duration_ms}ms con teorías {proof.theories_used}. 0 defectos."
            )
            claim.metadata["formal_duration_ms"] = proof.solver_duration_ms
            claim.metadata["theories"] = proof.theories_used
            return claim

        if proof.status == ProofStatus.DEFECT_FOUND:
            claim.status = EpistemicStatus.REFUTED
            claim.verified_at = now
            claim.proof_output = f"Defecto demostrado: {proof.defect_type.value}. Contraejemplo: {proof.counterexample}"
            claim.metadata["defect_type"] = proof.defect_type.value
            claim.metadata["counterexample"] = proof.counterexample
            claim.metadata["witness_test"] = proof.witness_test_code
            claim.metadata["witness_runtime_verified"] = proof.witness_verified_at_runtime
            return claim

        # Caso TIMEOUT_OR_UNKNOWN: ejecutar PBT Fallback automático si tenemos source_code
        if auto_pbt_fallback and source_code:
            scope: Dict[str, Any] = {}
            try:
                from aleph_core.verification.contracts import requires, ensures, invariant
                scope.update({"requires": requires, "ensures": ensures, "invariant": invariant})
                exec(source_code, scope)
                fn = scope.get(func_node.name)
                if callable(fn):
                    pbt_res = PropertyBasedFallback.run_from_contracts(fn)
                    if pbt_res.passed:
                        claim.status = EpistemicStatus.PBT_VERIFIED
                        claim.verified_at = now
                        proof_data = f"{claim.claim_id}:{now}:PBT_VERIFIED:{pbt_res.iterations_run}"
                        claim.proof_hash = hashlib.sha256(proof_data.encode("utf-8")).hexdigest()
                        claim.proof_output = (
                            f"SMT inconcluso ({proof.description}); verificado por PBT en {pbt_res.duration_ms}ms "
                            f"({pbt_res.iterations_run} casos generados)."
                        )
                        claim.metadata["pbt_iterations"] = pbt_res.iterations_run
                        return claim
                    else:
                        claim.status = EpistemicStatus.REFUTED
                        claim.verified_at = now
                        claim.proof_output = f"Refutado por PBT fallback: {pbt_res.falsifying_example}"
                        claim.metadata["counterexample"] = pbt_res.falsifying_example
                        return claim
            except Exception:
                pass

        claim.status = EpistemicStatus.INFERRED
        claim.proof_output = f"Demostración formal inconclusa ({proof.description}). Requiere revisión adicional."
        return claim
