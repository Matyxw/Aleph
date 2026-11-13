"""
Enrutador de Tareas, Motor Reducer Semántico y Planificador Concurrente DAG (Nivel 7 v2.4.0).
Despacha contratos inmutables, valida esquemas de salida y ejecuta grafos de dependencias
en paralelo por oleadas topológicas independientes (O(V+E)) superando la secuencialidad de ECC.
"""
import json
import time
import concurrent.futures
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, Set, List
from aleph_core.config import MAX_REDUCER_TOKENS

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

class TaskDispatcher:
    def __init__(self):
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register_handler(self, task_type: str, handler: Callable[[Dict[str, Any]], Any]):
        self._handlers[task_type] = handler

    def dispatch(self, contract: TaskContract) -> TaskExecutionResult:
        if contract.task_type not in self._handlers:
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=False,
                raw_output=None,
                compact_output="",
                execution_time_ms=0.0,
                error=f"Handler no registrado para task_type '{contract.task_type}'"
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
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=True,
                raw_output=raw_output,
                compact_output=compact,
                execution_time_ms=elapsed_ms
            )
        except Exception as ex:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return TaskExecutionResult(
                task_id=contract.task_id,
                success=False,
                raw_output=None,
                compact_output="",
                execution_time_ms=elapsed_ms,
                error=str(ex)
            )

    @staticmethod
    def reduce_output(raw: Any, max_chars: int = MAX_REDUCER_TOKENS * 4) -> str:
        if isinstance(raw, (dict, list)):
            text = json.dumps(raw, ensure_ascii=False)
        else:
            text = str(raw)
        if len(text) > max_chars:
            head_len = int(max_chars * 0.70)
            tail_len = max_chars - head_len
            omitted = len(text) - max_chars
            return (
                text[:head_len]
                + f"\n... [TRUNCADO POR REDUCER: {omitted} caracteres omitidos] ...\n"
                + text[-tail_len:]
            )
        return text

# Re-exportado desde dag_scheduler al final del módulo tras definir TaskDispatcher
# para evitar importación circular sin duplicar la lógica topológica.
from aleph_core.router.dag_scheduler import (
    DAGTaskNode,
    DAGScheduleResult,
    DynamicDAGScheduler,
)
