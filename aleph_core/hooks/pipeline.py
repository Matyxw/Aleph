"""
Pipeline Determinista de Hooks de Ciclo de Vida (Superación de ECC Hooks).
Mientras ECC depende de scripts shell sueltos (`observe.sh`) que pueden fallar por permisos o latencia,
El Aleph v2.0 ejecuta un bus tipado en memoria con presupuestos estrictos de latencia en 4 fases:
- PRE_DISPATCH (Validación de contratos, inyección de reglas activas SparkOS y escaneo AegisShield)
- POST_DISPATCH ( Auditoría de salida y poda semántica)
- PRE_COMMIT (Bloqueo si existen secretos expuestos o claims REFUTED)
- ON_FAILURE (Destilación automática de fricción para automejora)
"""
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional, Tuple

class HookPhase(str, Enum):
    PRE_DISPATCH = "PRE_DISPATCH"
    POST_DISPATCH = "POST_DISPATCH"
    PRE_COMMIT = "PRE_COMMIT"
    ON_FAILURE = "ON_FAILURE"

@dataclass
class HookEvent:
    phase: HookPhase
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HookResult:
    allowed: bool
    modified_payload: Dict[str, Any]
    annotations: Dict[str, Any] = field(default_factory=dict)
    blocked_reason: Optional[str] = None
    duration_ms: float = 0.0

class HookPipeline:
    def __init__(self):
        self._hooks: Dict[HookPhase, List[Tuple[str, Callable[[HookEvent], Optional[str]]]]] = {
            p: [] for p in HookPhase
        }

    def register_hook(self, phase: HookPhase, name: str, fn: Callable[[HookEvent], Optional[str]]):
        """
        Registra un hook para una fase. Si `fn(event)` devuelve un string no vacío,
        la ejecución se bloquea inmediatamente con ese motivo.
        """
        self._hooks[phase].append((name, fn))

    def run_phase(self, event: HookEvent) -> HookResult:
        t0 = time.perf_counter_ns()
        executed = []
        for name, fn in self._hooks.get(event.phase, []):
            reason = fn(event)
            executed.append(name)
            if reason:
                dur = (time.perf_counter_ns() - t0) / 1_000_000.0
                return HookResult(
                    allowed=False,
                    modified_payload=event.payload,
                    annotations={"executed_hooks": executed, "blocked_by": name},
                    blocked_reason=reason,
                    duration_ms=round(dur, 3)
                )
        dur = (time.perf_counter_ns() - t0) / 1_000_000.0
        return HookResult(
            allowed=True,
            modified_payload=event.payload,
            annotations={"executed_hooks": executed},
            duration_ms=round(dur, 3)
        )
