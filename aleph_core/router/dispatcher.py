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

@dataclass
class DAGTaskNode:
    contract: TaskContract
    dependencies: Set[str] = field(default_factory=set)
    verifier_fn: Optional[Callable[[Any], bool]] = None
    formal_source_code: Optional[str] = None
    use_bitvectors: bool = False

@dataclass
class DAGScheduleResult:
    total_tasks: int
    waves_executed: int
    wall_clock_duration_ms: float
    sequential_equivalent_duration_ms: float
    speedup_ratio: float
    results: Dict[str, Any]
    all_success: bool

class DynamicDAGScheduler:
    """Planificador topológico concurrente de tareas agénticas."""
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers

    @staticmethod
    def compute_execution_waves(nodes: Dict[str, DAGTaskNode]) -> List[List[str]]:
        in_degree: Dict[str, int] = {task_id: len(node.dependencies) for task_id, node in nodes.items()}
        for task_id, node in nodes.items():
            for dep in node.dependencies:
                if dep not in nodes:
                    raise KeyError(f"Dependencia desconocida '{dep}' requerida por tarea '{task_id}'")

        waves: List[List[str]] = []
        visited = set()

        while len(visited) < len(nodes):
            current_wave = [task_id for task_id, deg in in_degree.items() if deg == 0 and task_id not in visited]
            if not current_wave:
                unvisited = set(nodes.keys()) - visited
                raise ValueError(f"Ciclo detectado en DAG de tareas: dependencias circulares en {unvisited}")

            waves.append(current_wave)
            for t in current_wave:
                visited.add(t)

            for task_id, node in nodes.items():
                if task_id not in visited:
                    in_degree[task_id] -= len(node.dependencies & set(current_wave))

        return waves

    def execute_dag(
        self,
        nodes: Dict[str, DAGTaskNode],
        engine_execute_fn: Callable[..., Dict[str, Any]]
    ) -> DAGScheduleResult:
        t0 = time.perf_counter_ns()
        waves = self.compute_execution_waves(nodes)
        results: Dict[str, Any] = {}
        all_success = True
        seq_ms_sum = 0.0

        for wave in waves:
            wave_nodes = [nodes[task_id] for task_id in wave]
            if len(wave_nodes) == 1:
                n = wave_nodes[0]
                res = engine_execute_fn(
                    task_type=n.contract.task_type,
                    input_payload=n.contract.input_payload,
                    verifier_fn=n.verifier_fn,
                    domain_category=n.contract.domain_category,
                    formal_source_code=n.formal_source_code,
                    use_bitvectors=n.use_bitvectors
                )
                results[n.contract.task_id] = res
                seq_ms_sum += res.get("latency_ms", 1.0)
                if res.get("status") != "SUCCESS":
                    all_success = False
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.max_workers, len(wave_nodes))) as executor:
                    future_map = {
                        executor.submit(
                            engine_execute_fn,
                            task_type=n.contract.task_type,
                            input_payload=n.contract.input_payload,
                            verifier_fn=n.verifier_fn,
                            domain_category=n.contract.domain_category,
                            formal_source_code=n.formal_source_code,
                            use_bitvectors=n.use_bitvectors
                        ): n.contract.task_id
                        for n in wave_nodes
                    }
                    for fut in concurrent.futures.as_completed(future_map):
                        tid = future_map[fut]
                        res = fut.result()
                        results[tid] = res
                        seq_ms_sum += res.get("latency_ms", 1.0)
                        if res.get("status") != "SUCCESS":
                            all_success = False

        duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        speedup = round(seq_ms_sum / max(duration_ms, 0.001), 2)
        return DAGScheduleResult(
            total_tasks=len(nodes),
            waves_executed=len(waves),
            wall_clock_duration_ms=round(duration_ms, 3),
            sequential_equivalent_duration_ms=round(seq_ms_sum, 3),
            speedup_ratio=speedup,
            results=results,
            all_success=all_success
        )
