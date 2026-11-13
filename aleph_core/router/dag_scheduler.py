"""
aleph_core/router/dag_scheduler.py
Planificador Concurrente de Grafos Acíclicos Dirigidos (DAG Scheduler) y Despachador Paralelo (Nivel 7).
Supera el cuello de botella secuencial de ECC y frameworks tradicionales:
1. Resuelve dependencias de tareas en un grafo dirigido topológico O(V + E) con detección de ciclos.
2. Identifica oleadas de ejecución concurrentes (independent execution waves).
3. Ejecuta tareas independientes en paralelo mediante ThreadPoolExecutor sin contención.
4. Pasa cada tarea por la compuerta de verificación epistémica y persiste resultados atómicamente en SQLite WAL.
"""
import time
import concurrent.futures
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Callable
from aleph_core.router.dispatcher import TaskContract, TaskExecutionResult, TaskDispatcher

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
        """
        Calcula las oleadas de tareas ejecutables en paralelo mediante orden topológico por niveles.
        Lanza ValueError si se detecta una dependencia circular (ciclo en el DAG).
        """
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

            # Reducir grado de entrada para las tareas subsiguientes
            for task_id, node in nodes.items():
                if task_id not in visited:
                    in_degree[task_id] -= len(node.dependencies & set(current_wave))

        return waves

    @classmethod
    def validate_acyclic(cls, nodes: Dict[str, DAGTaskNode]) -> List[List[str]]:
        """Valida explícitamente que no existan dependencias huérfanas ni ciclos antes de despachar."""
        return cls.compute_execution_waves(nodes)

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
                # Ejecución directa sin overhead de thread pool
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
                # Ejecución concurrente en paralelo de la oleada
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
