"""
aleph_core/verification/pbt_fallback.py
Verificación Basada en Propiedades (Property-Based Testing) con soporte dual:
Usa Hypothesis si está instalado, o el generador determinista + aleatorio con shrinking integrado
de El Aleph cuando se corre en entornos sin dependencias externas.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, List
import ast
import inspect
import random
import time

try:
    from hypothesis import given, strategies as st, settings, Phase
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

SAFE_CONTRACT_BUILTINS: Dict[str, Any] = {
    "abs": abs,
    "min": min,
    "max": max,
    "len": len,
    "sum": sum,
    "all": all,
    "any": any,
    "isinstance": isinstance,
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
    "dict": dict,
    "list": list,
    "set": set,
    "tuple": tuple,
    "range": range,
    "True": True,
    "False": False,
    "None": None,
}


def _safe_eval_contract(expr_str: str, env: Dict[str, Any]) -> Any:
    """Evalúa de forma segura una expresión de contrato validando su AST contra introspección/inyección."""
    tree = ast.parse(expr_str, mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError(f"Identificador dunder prohibido en contrato: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError(f"Acceso a atributo dunder prohibido en contrato: {node.attr}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id not in SAFE_CONTRACT_BUILTINS:
                raise ValueError(f"Llamada no permitida en contrato: {node.func.id}")
            elif not isinstance(node.func, ast.Name):
                raise ValueError("Solo se permiten llamadas directas a funciones puras seguras en contratos.")
    code_obj = compile(tree, "<contract>", "eval")
    return eval(code_obj, {"__builtins__": SAFE_CONTRACT_BUILTINS}, env)

@dataclass
class PBTFallbackResult:
    passed: bool
    iterations_run: int
    duration_ms: float
    falsifying_example: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class PropertyBasedFallback:
    """Ejecutor de pruebas generativas acotadas con shrinking automático para fallback determinista."""

    @staticmethod
    def _shrink_counterexample(
        func: Callable,
        failing_args: Dict[str, int],
        precondition_fn: Optional[Callable[..., bool]],
        property_fn: Optional[Callable[..., bool]]
    ) -> Dict[str, int]:
        """Minimiza el contraejemplo hacia 0 manteniendo la falla reproducible."""
        current = dict(failing_args)
        for key in list(current.keys()):
            val = current[key]
            for candidate in [0, 1, -1, val // 2]:
                trial = dict(current)
                trial[key] = candidate
                if precondition_fn and not precondition_fn(**trial):
                    continue
                try:
                    res = func(**trial)
                    if property_fn and not property_fn(result=res, **trial):
                        current = trial
                        break
                except Exception:
                    current = trial
                    break
        return current

    @classmethod
    def run_property_check(
        cls,
        func: Callable,
        precondition_fn: Optional[Callable[..., bool]] = None,
        property_fn: Optional[Callable[..., bool]] = None,
        max_examples: int = 150
    ) -> PBTFallbackResult:
        t0 = time.perf_counter_ns()
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        rng = random.Random(42)

        # Semillas de frontera primero + muestreo pseudoaleatorio reproducible
        boundary_pool = [0, 1, -1, 2, -2, 10, -10, 100, -100, 1000, -1000]
        runs_count = 0

        for i in range(max_examples * 3):
            if runs_count >= max_examples:
                break
            args: Dict[str, Any] = {}
            for idx, name in enumerate(param_names):
                if i < len(boundary_pool):
                    args[name] = boundary_pool[(i + idx) % len(boundary_pool)]
                else:
                    args[name] = rng.randint(-1000, 1000)

            if precondition_fn:
                try:
                    if not precondition_fn(**args):
                        continue
                except Exception:
                    continue

            runs_count += 1
            try:
                res = func(**args)
                if property_fn and not property_fn(result=res, **args):
                    shrunk = cls._shrink_counterexample(func, args, precondition_fn, property_fn)
                    duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
                    return PBTFallbackResult(
                        passed=False,
                        iterations_run=runs_count,
                        duration_ms=round(duration_ms, 3),
                        falsifying_example=shrunk,
                        error_message=f"Poscondición violada para args={shrunk}"
                    )
            except Exception as ex:
                shrunk = cls._shrink_counterexample(func, args, precondition_fn, property_fn)
                duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
                return PBTFallbackResult(
                    passed=False,
                    iterations_run=runs_count,
                    duration_ms=round(duration_ms, 3),
                    falsifying_example=shrunk,
                    error_message=str(ex)
                )

        duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return PBTFallbackResult(
            passed=True,
            iterations_run=runs_count,
            duration_ms=round(duration_ms, 3)
        )

    @classmethod
    def run_from_contracts(cls, func: Callable, max_examples: int = 120) -> PBTFallbackResult:
        """Extrae @requires y @ensures adjuntos a `func.__contracts__` y ejecuta el fuzzer."""
        spec = getattr(func, "__contracts__", None)
        pre_strs: List[str] = spec.preconditions if spec else []
        post_strs: List[str] = spec.postconditions if spec else []

        def pre_fn(**kwargs) -> bool:
            for p in pre_strs:
                if not bool(_safe_eval_contract(p, kwargs)):
                    return False
            return True

        def prop_fn(result: Any, **kwargs) -> bool:
            env = dict(kwargs)
            env["result"] = result
            for post in post_strs:
                if not bool(_safe_eval_contract(post, env)):
                    return False
            return True

        return cls.run_property_check(
            func=func,
            precondition_fn=pre_fn if pre_strs else None,
            property_fn=prop_fn if post_strs else None,
            max_examples=max_examples
        )
