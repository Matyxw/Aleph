"""
aleph_core/verification/contracts.py
Definiciones de contratos formales, tipos refinados e invariantes para El Aleph v2.0.
"""
from dataclasses import dataclass
from typing import Callable, Any, TypeVar, Generic

T = TypeVar("T")

@dataclass(frozen=True)
class ContractSpec:
    preconditions: list[str]
    postconditions: list[str]
    invariants: list[str]

def _ensure_contract_spec(target: Any) -> ContractSpec:
    if not hasattr(target, "__contracts__"):
        target.__contracts__ = ContractSpec(preconditions=[], postconditions=[], invariants=[])
    return target.__contracts__

def requires(condition_str: str):
    """Especifica una precondición formal requerida para la función. Ej: @requires("x > 0 and y != 0")"""
    def decorator(fn: Callable) -> Callable:
        spec = _ensure_contract_spec(fn)
        spec.preconditions.append(condition_str)
        return fn
    return decorator

def ensures(condition_str: str):
    """Especifica una poscondición formal garantizada por la función ('result' es el retorno)."""
    def decorator(fn: Callable) -> Callable:
        spec = _ensure_contract_spec(fn)
        spec.postconditions.append(condition_str)
        return fn
    return decorator

def invariant(condition_str: str):
    """Especifica un invariante de estado o bucle. Ej: @invariant("balance >= 0")"""
    def decorator(cls_or_fn: Any) -> Any:
        spec = _ensure_contract_spec(cls_or_fn)
        spec.invariants.append(condition_str)
        return cls_or_fn
    return decorator

class Refined(Generic[T]):
    """Tipo refinado formal: T con un predicado lógico adjunto."""
    pass

def loop_invariant(condition_str: str):
    """Especifica un invariante inductivo de bucle formal (Hoare Logic). Ej: @loop_invariant("i >= 0 and acc >= 0")"""
    def decorator(fn: Callable) -> Callable:
        spec = _ensure_contract_spec(fn)
        spec.invariants.append(f"LOOP_INV:{condition_str}")
        return fn
    return decorator

def loop_variant(ranking_expr_str: str):
    """Especifica la función de ranking estrictamente decreciente para demostrar terminación de bucle."""
    def decorator(fn: Callable) -> Callable:
        spec = _ensure_contract_spec(fn)
        spec.invariants.append(f"LOOP_VARIANT:{ranking_expr_str}")
        return fn
    return decorator
