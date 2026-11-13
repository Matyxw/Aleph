#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
El Aleph v4.0 - Super-Swarm 1,000+ DAG-BFT Engine
Sub-sistema: Malla Descentralizada Concurrente, Economía VCG y Consenso Causal
Ruta: C:\\Users\\Lucas cardozo\\.aleph\\v4_engine\\super_swarm_bft.py
Doctrina: EL DEMIURGO - Protocolo Universal de Razonamiento y Ejecución
=============================================================================
"""

from __future__ import annotations
import math
import time
import hashlib
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# 1. Telemetría Universal de Escalabilidad (Gunther USL)
# =============================================================================

@dataclass(frozen=True)
class UslSample:
    """Muestra de telemetría de concurrencia N y throughput medido C."""
    concurrency_n: float
    throughput_c: float


@dataclass(frozen=True)
class UslParameters:
    """Parámetros ajustados de la Ley Universal de Escalabilidad de Gunther."""
    alpha: float  # Coeficiente de contención (espera serial, Amdahl)
    beta: float   # Coeficiente de coherencia (diafonía cuadrática, cross-talk)

    def critical_concurrency(self) -> Optional[float]:
        """Calcula el punto crítico N* = sqrt((1 - alpha) / beta) antes del colapso retrógrado."""
        if self.beta <= 0.0:
            return None
        numerator = 1.0 - self.alpha
        if numerator <= 0.0:
            return 1.0
        return math.sqrt(numerator / self.beta)

    def evaluate_throughput(self, n: float) -> float:
        """Evalúa C(N) = N / (1 + alpha*(N - 1) + beta*N*(N - 1))."""
        if n <= 0.0:
            return 0.0
        denom = 1.0 + self.alpha * (n - 1.0) + self.beta * n * (n - 1.0)
        return 0.0 if denom <= 0.0 else (n / denom)

    def linearity_percentage_at(self, n: float) -> float:
        """Calcula la eficiencia lineal respecto al caso ideal C(N)/N."""
        if n <= 0.0:
            return 0.0
        c_n = self.evaluate_throughput(n)
        return (c_n / n) * 100.0


class UslEngine:
    """Motor de cálculo y ajuste de mínimos cuadrados para telemetría USL."""

    def __init__(self) -> None:
        self.samples: List[UslSample] = []
        self.total_tasks_completed: int = 0

    def record_sample(self, concurrency_n: float, throughput_c: float) -> None:
        self.samples.append(UslSample(concurrency_n=concurrency_n, throughput_c=throughput_c))

    def record_task_completed(self, count: int = 1) -> None:
        self.total_tasks_completed += count

    def fit_parameters(self, samples: Optional[List[UslSample]] = None) -> UslParameters:
        """
        Ajusta alpha y beta mediante regresión lineal sobre la ecuación invertida:
        N / C(N) - 1 = alpha * (N - 1) + beta * N * (N - 1)
        Sea Y = (N / C) - 1, X1 = N - 1, X2 = N * (N - 1)
        """
        dataset = samples if samples is not None else self.samples
        valid_samples = [s for s in dataset if s.throughput_c > 0.0 and s.concurrency_n > 1.0]

        if len(valid_samples) < 3:
            raise ValueError("Se requieren al menos 3 muestras válidas para ajustar la USL")

        sum_x1_sq = 0.0
        sum_x2_sq = 0.0
        sum_x1_x2 = 0.0
        sum_x1_y = 0.0
        sum_x2_y = 0.0

        for s in valid_samples:
            y = (s.concurrency_n / s.throughput_c) - 1.0
            x1 = s.concurrency_n - 1.0
            x2 = s.concurrency_n * (s.concurrency_n - 1.0)

            sum_x1_sq += x1 * x1
            sum_x2_sq += x2 * x2
            sum_x1_x2 += x1 * x2
            sum_x1_y += x1 * y
            sum_x2_y += x2 * y

        det = sum_x1_sq * sum_x2_sq - sum_x1_x2 * sum_x1_x2
        if abs(det) < 1e-18:
            raise ValueError("Matriz singular: muestras colineales o insuficientemente diferenciadas")

        alpha = (sum_x2_sq * sum_x1_y - sum_x1_x2 * sum_x2_y) / det
        beta = (sum_x1_sq * sum_x2_y - sum_x1_x2 * sum_x1_y) / det

        # Clamping de validez física
        clamped_alpha = max(0.0, min(0.999, alpha))
        clamped_beta = max(0.0, min(0.1, beta))

        return UslParameters(alpha=clamped_alpha, beta=clamped_beta)


# =============================================================================
# 2. Economía de Cómputo: Subastas Combinatorias VCG (Clarke Pivot)
# =============================================================================

@dataclass(frozen=True)
class TaskBid:
    """Puja de un agente por un subconjunto de tareas (Bundle)."""
    bidder: str
    task_ids: Tuple[int, ...]
    claimed_cost: int
    max_execution_ms: int = 100
    collateral_locked: int = 10_000


@dataclass(frozen=True)
class AllocationResult:
    """Asignación de una tarea a un ganador con su pago Clarke Pivot."""
    task_id: int
    winner: str
    clarke_payment: int


class VcgAuctionEngine:
    """
    Subasta Reversa Combinatoria de Vickrey-Clarke-Groves (VCG).
    Garantiza:
    1. Eficiencia Social Ex-Post (minimiza el costo total de computación).
    2. Veracidad en Estrategia Débilmente Dominante (DSIC): b_i = c_i.
    3. Racionalidad Individual: Utility >= 0.
    """

    @classmethod
    def clear_auction(
        cls, all_tasks: List[int], bids: List[TaskBid]
    ) -> List[AllocationResult]:
        if not all_tasks:
            return []

        task_set = set(all_tasks)

        # 1. Resolver el problema óptimo global V* con todos los agentes
        global_alloc, global_cost = cls._solve_wdp(task_set, bids)
        if global_alloc is None:
            raise ValueError("No existe asignación factible que cubra todas las tareas solicitadas")

        winning_agents = set(global_alloc.values())
        results: List[AllocationResult] = []

        # 2. Para cada agente ganador, computar el pago de Clarke Pivot
        for winner in winning_agents:
            bids_without_winner = [b for b in bids if b.bidder != winner]
            alloc_without, cost_without = cls._solve_wdp(task_set, bids_without_winner)

            # Si sin el ganador no hay asignación factible, se toma el costo global como cota
            v_minus_i = cost_without if alloc_without is not None else global_cost

            # Suma de costos declarados por los DEMÁS ganadores en la solución global
            sum_other_winners_cost = sum(
                b.claimed_cost
                for b in bids
                if b.bidder != winner and cls._is_bid_active(b, global_alloc)
            )

            # Clarke Payment: P_i = V_{-i}^* - sum_{j != i} b_j(x*)
            clarke_payment = max(0, v_minus_i - sum_other_winners_cost)

            for tid, agent in global_alloc.items():
                if agent == winner:
                    results.append(
                        AllocationResult(
                            task_id=tid,
                            winner=winner,
                            clarke_payment=clarke_payment,
                        )
                    )

        # Ordenar deterministamente por task_id
        results.sort(key=lambda r: r.task_id)
        return results

    @classmethod
    def _solve_wdp(
        cls, tasks: Set[int], bids: List[TaskBid]
    ) -> Tuple[Optional[Dict[int, str]], int]:
        """
        Resuelve el Winner Determination Problem (WDP) de costo mínimo
        mediante branch-and-bound con heurística greedy y poda estricta.
        """
        best_alloc: Optional[Dict[int, str]] = None
        min_cost = float("inf")

        # Ordenar pujas por eficiencia: costo / cantidad de tareas
        sorted_bids = sorted(
            bids,
            key=lambda b: (b.claimed_cost / len(b.task_ids)) if b.task_ids else float("inf")
        )

        stack: List[Tuple[int, Dict[int, str], int, Set[int]]] = [
            (0, {}, 0, set())
        ]

        while stack:
            idx, current_alloc, current_cost, covered = stack.pop()

            if covered == tasks:
                if current_cost < min_cost:
                    min_cost = current_cost
                    best_alloc = current_alloc.copy()
                continue

            if current_cost >= min_cost or idx >= len(sorted_bids):
                continue

            bid = sorted_bids[idx]

            # Opción 1: No seleccionar esta puja
            stack.append((idx + 1, current_alloc, current_cost, covered))

            # Opción 2: Seleccionar esta puja si aporta tareas nuevas y el agente no está asignado
            bid_tasks = set(bid.task_ids) & tasks
            provides_new = bool(bid_tasks - covered)
            already_assigned = bid.bidder in current_alloc.values()

            if provides_new and not already_assigned:
                new_covered = covered | bid_tasks
                new_alloc = current_alloc.copy()
                for t in bid_tasks:
                    new_alloc[t] = bid.bidder
                new_cost = current_cost + bid.claimed_cost
                if new_cost < min_cost:
                    stack.append((idx + 1, new_alloc, new_cost, new_covered))

        return best_alloc, int(min_cost) if best_alloc is not None else int(1e12)

    @staticmethod
    def _is_bid_active(bid: TaskBid, alloc: Dict[int, str]) -> bool:
        return any(alloc.get(t) == bid.bidder for t in bid.task_ids)


# =============================================================================
# 3. Tarificación Dinámica EIP-1559 Multidimensional
# =============================================================================

@dataclass(frozen=True)
class GasMetrics:
    """Vector de recursos de 4 dimensiones ortogonales."""
    cpu_cycles: int
    memory_byte_seconds: int
    io_ops: int
    zk_air_constraints: int


@dataclass
class MultidimensionalGasPrice:
    """Tarifa base por unidad de gas para cada dimensión."""
    price_cpu: float = 1.0
    price_mem: float = 0.5
    price_io: float = 2.0
    price_zk: float = 5.0


@dataclass
class GasControllerConfig:
    target_capacity: GasMetrics
    elasticity_delta: float = 0.125  # Max 12.5% de cambio por ronda
    min_prices: MultidimensionalGasPrice = field(
        default_factory=lambda: MultidimensionalGasPrice(0.1, 0.05, 0.2, 0.5)
    )
    max_prices: MultidimensionalGasPrice = field(
        default_factory=lambda: MultidimensionalGasPrice(100.0, 50.0, 200.0, 500.0)
    )


class DynamicGasController:
    """Controlador de gas EIP-1559 multidimensional con quema deflacionaria."""

    def __init__(
        self,
        config: GasControllerConfig,
        initial_prices: Optional[MultidimensionalGasPrice] = None,
    ) -> None:
        self.config = config
        self.current_prices = initial_prices or MultidimensionalGasPrice()
        self.total_gas_burned: int = 0

    def update_prices_for_next_round(self, usage: GasMetrics) -> MultidimensionalGasPrice:
        self.current_prices.price_cpu = self._compute_next_price(
            self.current_prices.price_cpu,
            usage.cpu_cycles,
            self.config.target_capacity.cpu_cycles,
            self.config.min_prices.price_cpu,
            self.config.max_prices.price_cpu,
        )
        self.current_prices.price_mem = self._compute_next_price(
            self.current_prices.price_mem,
            usage.memory_byte_seconds,
            self.config.target_capacity.memory_byte_seconds,
            self.config.min_prices.price_mem,
            self.config.max_prices.price_mem,
        )
        self.current_prices.price_io = self._compute_next_price(
            self.current_prices.price_io,
            usage.io_ops,
            self.config.target_capacity.io_ops,
            self.config.min_prices.price_io,
            self.config.max_prices.price_io,
        )
        self.current_prices.price_zk = self._compute_next_price(
            self.current_prices.price_zk,
            usage.zk_air_constraints,
            self.config.target_capacity.zk_air_constraints,
            self.config.min_prices.price_zk,
            self.config.max_prices.price_zk,
        )
        return self.current_prices

    def calculate_and_burn_fee(self, usage: GasMetrics, priority_tip: int = 0) -> Tuple[int, int]:
        """
        Calcula la tarifa base que es 100% quemada, y la tarifa total con priority tip.
        Retorna (base_fee_burned, total_fee).
        """
        base_fee_float = (
            usage.cpu_cycles * self.current_prices.price_cpu
            + usage.memory_byte_seconds * self.current_prices.price_mem
            + usage.io_ops * self.current_prices.price_io
            + usage.zk_air_constraints * self.current_prices.price_zk
        )
        base_fee = int(math.ceil(base_fee_float))
        self.total_gas_burned += base_fee
        total_fee = base_fee + priority_tip
        return base_fee, total_fee

    def _compute_next_price(
        self, current: float, actual: int, target: int, min_p: float, max_p: float
    ) -> float:
        if target <= 0:
            return current
        ratio = (actual - target) / target
        next_val = current * (1.0 + self.config.elasticity_delta * ratio)
        return max(min_p, min(max_p, next_val))


# =============================================================================
# 4. Reputación Bayesiana Beta-Binomial y Slashing
# =============================================================================

@dataclass
class AgentReputationState:
    alpha_successes: float = 1.0  # Laplace prior
    beta_failures: float = 1.0
    staked_collateral: int = 10_000
    is_slashed_byzantine: bool = False

    def expected_reputation(self) -> float:
        """E[R] = (alpha + 1) / (alpha + beta + 2)"""
        if self.is_slashed_byzantine:
            return 0.0
        return (self.alpha_successes + 1.0) / (
            self.alpha_successes + self.beta_failures + 2.0
        )

    def reputation_variance(self) -> float:
        """Var(R) = (alpha + 1)(beta + 1) / ((alpha + beta + 2)^2 * (alpha + beta + 3))"""
        a = self.alpha_successes + 1.0
        b = self.beta_failures + 1.0
        denom = ((a + b) ** 2) * (a + b + 1.0)
        return (a * b) / denom if denom > 0 else 0.0


class ReputationManager:
    """Administrador Bayesiano de Reputación y Slashing Criptográfico."""

    def __init__(
        self, aging_factor_lambda: float = 0.985, min_stake_required: int = 10_000
    ) -> None:
        self.agents: Dict[str, AgentReputationState] = {}
        self.aging_factor_lambda = aging_factor_lambda
        self.min_stake_required = min_stake_required
        self.insurance_treasury: int = 0

    def register_agent(self, agent_id: str, stake: int) -> None:
        if stake < self.min_stake_required:
            raise ValueError(f"Colateral insuficiente: {stake} < {self.min_stake_required}")
        self.agents[agent_id] = AgentReputationState(staked_collateral=stake)

    def record_success(self, agent_id: str, weight: float = 1.0) -> None:
        state = self.agents.get(agent_id)
        if state and not state.is_slashed_byzantine:
            state.alpha_successes += max(0.1, weight)

    def record_failure(self, agent_id: str, weight: float = 1.0) -> int:
        """Registra un fallo operativo y aplica slashing cuadrático proporcional."""
        state = self.agents.get(agent_id)
        if not state or state.is_slashed_byzantine:
            return 0

        state.beta_failures += max(0.1, weight)
        failure_rate = state.beta_failures / (state.alpha_successes + state.beta_failures)
        slash_fraction = min(0.35, 2.5 * (failure_rate ** 2))
        slash_amount = int(state.staked_collateral * slash_fraction)
        state.staked_collateral = max(0, state.staked_collateral - slash_amount)
        self.insurance_treasury += slash_amount
        return slash_amount

    def slash_byzantine_equivocation(self, agent_id: str) -> int:
        """Slashing incondicional del 100% de colateral por fraude o firma doble."""
        state = self.agents.get(agent_id)
        if not state:
            return 0
        burned = state.staked_collateral
        state.staked_collateral = 0
        state.is_slashed_byzantine = True
        state.alpha_successes = 0.0
        state.beta_failures = 1_000_000.0
        return burned

    def apply_epoch_aging(self) -> None:
        """Aplica decaimiento temporal (aging) para prevenir whitewashing."""
        for state in self.agents.values():
            if not state.is_slashed_byzantine:
                state.alpha_successes *= self.aging_factor_lambda
                state.beta_failures *= self.aging_factor_lambda

    def get_reputation(self, agent_id: str) -> float:
        state = self.agents.get(agent_id)
        return state.expected_reputation() if state else 0.0


# =============================================================================
# 5. Motor de Consenso Asíncrono Narwhal-Bullshark DAG-BFT
# =============================================================================

@dataclass(frozen=True)
class NarwhalVertex:
    """Vértice de disponibilidad de datos en el DAG de Narwhal."""
    origin: int
    round: int
    batch_digest: str
    previous_certs: Tuple[str, ...]

    def compute_digest(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(f"vertex:{self.origin}:{self.round}:{self.batch_digest}".encode())
        for p in sorted(self.previous_certs):
            hasher.update(p.encode())
        return hasher.hexdigest()


@dataclass(frozen=True)
class NarwhalCertificate:
    """Certificado que comprueba la disponibilidad del vértice con 2f+1 firmas."""
    vertex: NarwhalVertex
    signatures: Tuple[int, ...]  # IDs de validadores que firmaron

    @property
    def digest(self) -> str:
        return self.vertex.compute_digest()


class BullsharkDagEngine:
    """
    Motor de Consenso DAG-BFT Narwhal-Bullshark.
    Tolerancia a fallas: N = 3f + 1, quórum = 2f + 1.
    Zero-network-overhead: el orden total se extrae de la topología local del DAG.
    """

    def __init__(self, total_nodes: int) -> None:
        self.total_nodes = total_nodes
        self.f = (total_nodes - 1) // 3
        self.quorum_threshold = 2 * self.f + 1
        # round -> {digest: certificate}
        self.dag_rounds: Dict[int, Dict[str, NarwhalCertificate]] = {}
        self.committed_digests: Set[str] = set()
        self.linearized_sequence: List[str] = []

    def insert_certificate(self, cert: NarwhalCertificate) -> bool:
        r = cert.vertex.round
        # Para rondas r > 1, verificar quórum causal de certificados de r-1
        if r > 1 and len(cert.vertex.previous_certs) < self.quorum_threshold:
            raise ValueError(
                f"Quórum causal insuficiente: {len(cert.vertex.previous_certs)} < {self.quorum_threshold}"
            )

        # Verificar firmas de disponibilidad de datos
        if len(cert.signatures) < self.quorum_threshold:
            raise ValueError(
                f"Firmas insuficientes en certificado: {len(cert.signatures)} < {self.quorum_threshold}"
            )

        if r not in self.dag_rounds:
            self.dag_rounds[r] = {}

        self.dag_rounds[r][cert.digest] = cert
        self.try_advance_bullshark_commits()
        return True

    def try_advance_bullshark_commits(self) -> List[str]:
        """
        Regla de Bullshark:
        Para rondas impares r, el líder predeterminado L_r queda comprometido
        si la ronda par r+1 contiene >= 2f+1 certificados con enlace causal hacia él.
        """
        new_commits: List[str] = []
        rounds = sorted(self.dag_rounds.keys())

        for r in rounds:
            if r % 2 == 1 and (r + 1) in self.dag_rounds:
                leader_node_id = self.elect_leader_for_round(r)
                round_certs = self.dag_rounds[r]
                leader_cert = next(
                    (c for c in round_certs.values() if c.vertex.origin == leader_node_id),
                    None,
                )

                if leader_cert and leader_cert.digest not in self.committed_digests:
                    directed_votes = self._count_directed_votes(r + 1, leader_cert.digest)
                    if directed_votes >= self.quorum_threshold:
                        committed = self._linearize_causal_history(leader_cert.digest)
                        new_commits.extend(committed)

        return new_commits

    def _linearize_causal_history(self, anchor_digest: str) -> List[str]:
        """Recorrido topológico determinista hacia atrás para ordenar los ancestros causales."""
        to_commit: List[str] = []
        visited: Set[str] = set()
        queue: List[str] = [anchor_digest]

        while queue:
            curr = queue.pop(0)
            if curr in self.committed_digests or curr in visited:
                continue
            visited.add(curr)
            to_commit.append(curr)

            # Buscar el certificado en cualquier ronda
            cert = self._find_cert(curr)
            if cert:
                for parent_digest in cert.vertex.previous_certs:
                    if parent_digest not in self.committed_digests and parent_digest not in visited:
                        queue.append(parent_digest)

        # Ordenar deterministamente: ronda ascendente, luego digest lexicográfico
        to_commit.sort(key=lambda d: (self._get_cert_round(d), d))

        newly_committed: List[str] = []
        for d in to_commit:
            if d not in self.committed_digests:
                self.committed_digests.add(d)
                self.linearized_sequence.append(d)
                newly_committed.append(d)

        return newly_committed

    def _count_directed_votes(self, voting_round: int, target_leader: str) -> int:
        certs_in_voting_round = self.dag_rounds.get(voting_round, {})
        count = 0
        for voter in certs_in_voting_round.values():
            if self._has_causal_path(voter, target_leader):
                count += 1
        return count

    def _has_causal_path(self, from_cert: NarwhalCertificate, target: str) -> bool:
        if target in from_cert.vertex.previous_certs:
            return True
        prev_round = self.dag_rounds.get(from_cert.vertex.round - 1, {})
        for parent_digest in from_cert.vertex.previous_certs:
            parent = prev_round.get(parent_digest)
            if parent:
                if parent.digest == target or target in parent.vertex.previous_certs:
                    return True
        return False

    def elect_leader_for_round(self, round_num: int) -> int:
        """Elección determinista pseudoaleatoria de líder mediante SHA-256."""
        h = hashlib.sha256(f"aleph:bullshark:leader:{round_num}".encode()).digest()
        val = int.from_bytes(h[:4], "little")
        return val % self.total_nodes

    def _find_cert(self, digest: str) -> Optional[NarwhalCertificate]:
        for round_map in self.dag_rounds.values():
            if digest in round_map:
                return round_map[digest]
        return None

    def _get_cert_round(self, digest: str) -> int:
        for r, round_map in self.dag_rounds.items():
            if digest in round_map:
                return r
        return 0


# =============================================================================
# 6. Malla Epidémica Plumtree (Push-Lazy-Push)
# =============================================================================

@dataclass(frozen=True)
class GossipData:
    message_id: str
    payload: bytes
    hops: int = 0


@dataclass(frozen=True)
class IHaveMsg:
    message_ids: Tuple[str, ...]


@dataclass(frozen=True)
class GraftMsg:
    message_id: str


@dataclass(frozen=True)
class PruneMsg:
    pass


class PlumtreeNode:
    """Nodo del árbol de expansión estructurado híbrido Plumtree."""

    def __init__(self, node_id: str, graft_timeout_ms: float = 25.0) -> None:
        self.node_id = node_id
        self.eager_peers: Set[str] = set()
        self.lazy_peers: Set[str] = set()
        self.received_messages: Set[str] = set()
        # msg_id -> (timestamp_received_ihave, source_peer)
        self.missing_messages: Dict[str, Tuple[float, str]] = {}
        self.graft_timeout_ms = graft_timeout_ms

    def add_peer(self, peer_id: str, as_eager: bool = True) -> None:
        if peer_id == self.node_id:
            return
        if as_eager:
            self.eager_peers.add(peer_id)
            self.lazy_peers.discard(peer_id)
        else:
            self.lazy_peers.add(peer_id)
            self.eager_peers.discard(peer_id)

    def on_receive_gossip(
        self, sender: str, msg: GossipData
    ) -> List[Tuple[str, Any]]:
        actions: List[Tuple[str, Any]] = []

        # 1. Detección de duplicado: Ciclo detectado -> PRUNE
        if msg.message_id in self.received_messages:
            if sender in self.eager_peers:
                self.eager_peers.remove(sender)
                self.lazy_peers.add(sender)
                actions.append((sender, PruneMsg()))
            return actions

        # 2. Mensaje nuevo aceptado
        self.received_messages.add(msg.message_id)
        self.missing_messages.pop(msg.message_id, None)

        # 3. Eager Push hacia vecinos activos (excepto emisor)
        for eager in self.eager_peers:
            if eager != sender:
                actions.append(
                    (
                        eager,
                        GossipData(
                            message_id=msg.message_id,
                            payload=msg.payload,
                            hops=msg.hops + 1,
                        ),
                    )
                )

        # 4. Lazy Push (IHAVE) hacia enlaces pasivos
        for lazy in self.lazy_peers:
            if lazy != sender:
                actions.append((lazy, IHaveMsg(message_ids=(msg.message_id,))))

        return actions

    def on_receive_ihave(self, sender: str, msg: IHaveMsg) -> None:
        now = time.time() * 1000.0
        for m_id in msg.message_ids:
            if m_id not in self.received_messages:
                self.missing_messages.setdefault(m_id, (now, sender))

    def check_timeouts_and_graft(self) -> List[Tuple[str, GraftMsg]]:
        now = time.time() * 1000.0
        grafts: List[Tuple[str, GraftMsg]] = []
        to_remove = []

        for m_id, (ts, peer) in self.missing_messages.items():
            if now - ts >= self.graft_timeout_ms:
                to_remove.append(m_id)
                # Promover enlace a eager
                self.lazy_peers.discard(peer)
                self.eager_peers.add(peer)
                grafts.append((peer, GraftMsg(message_id=m_id)))

        for m_id in to_remove:
            self.missing_messages.pop(m_id, None)

        return grafts

    def on_receive_prune(self, sender: str) -> None:
        self.eager_peers.discard(sender)
        self.lazy_peers.add(sender)

    def on_receive_graft(self, sender: str) -> None:
        self.lazy_peers.discard(sender)
        self.eager_peers.add(sender)


# =============================================================================
# 7. Orquestador Maestro del Super-Enjambre (1,000+ Agentes)
# =============================================================================

class SuperSwarmOrchestrator:
    """
    Orquestador Central Concurrente de El Aleph para 1,000+ Agentes.
    Coordina:
    - Registro de agentes y colateral inicial.
    - Mecanismo de subastas VCG combinatorias.
    - Monitoreo de gas multidimensional EIP-1559 con quema.
    - Consenso causal Narwhal-Bullshark con quórum 2f+1.
    - Reputación Bayesiana y erradicación de bizantinos.
    - Métricas de telemetría USL y límites de saturación.
    """

    def __init__(
        self,
        total_agents: int = 1000,
        initial_stake_per_agent: int = 10_000,
    ) -> None:
        self.total_agents = total_agents
        self.initial_stake = initial_stake_per_agent

        # Sub-sistemas
        self.usl_engine = UslEngine()
        self.gas_controller = DynamicGasController(
            config=GasControllerConfig(
                target_capacity=GasMetrics(
                    cpu_cycles=10_000_000,
                    memory_byte_seconds=5_000_000,
                    io_ops=100_000,
                    zk_air_constraints=500_000,
                ),
                elasticity_delta=0.125,
            )
        )
        self.reputation_manager = ReputationManager(
            aging_factor_lambda=0.985, min_stake_required=initial_stake_per_agent
        )
        self.dag_engine = BullsharkDagEngine(total_nodes=total_agents)
        self.plumtree_nodes: Dict[str, PlumtreeNode] = {}

        # Inicialización de agentes
        for i in range(total_agents):
            agent_id = f"agent_{i:04d}"
            self.reputation_manager.register_agent(agent_id, initial_stake_per_agent)
            self.plumtree_nodes[agent_id] = PlumtreeNode(node_id=agent_id)

        # Configurar topología básica de Plumtree (árbol k-regular inicial)
        self._initialize_plumtree_topology()

    def _initialize_plumtree_topology(self, fanout: int = 6) -> None:
        for i in range(self.total_agents):
            curr_id = f"agent_{i:04d}"
            for k in range(1, fanout + 1):
                neighbor_idx = (i + k) % self.total_agents
                neigh_id = f"agent_{neighbor_idx:04d}"
                self.plumtree_nodes[curr_id].add_peer(neigh_id, as_eager=(k <= 2))

    def run_auction_round(
        self, tasks: List[int], bids: List[TaskBid]
    ) -> List[AllocationResult]:
        """Ejecuta una ronda de subasta VCG y registra métricas de gas."""
        return VcgAuctionEngine.clear_auction(tasks, bids)

    def execute_dag_round(
        self,
        round_num: int,
        honest_count: int,
        byzantine_count: int = 0,
        byzantine_equivocators: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta una ronda completa del DAG de Narwhal:
        - Nodos honestos generan vértices con 2f+1 referencias causales.
        - Se detectan y slashan nodos bizantinos por equivocación.
        - Se insertan certificados válidos en el motor Bullshark.
        - Se retornan los commits totalizados.
        """
        if honest_count + byzantine_count > self.total_agents:
            raise ValueError("El número total de nodos excede la capacidad del enjambre")

        quorum = self.dag_engine.quorum_threshold
        slashed_byzantines = []

        # 1. Procesar equivocaciones bizantinas si las hay
        if byzantine_equivocators:
            for b_idx in byzantine_equivocators:
                agent_id = f"agent_{b_idx:04d}"
                burned = self.reputation_manager.slash_byzantine_equivocation(agent_id)
                slashed_byzantines.append((agent_id, burned))

        # 2. Obtener certificados de la ronda anterior para causalidad
        previous_certs: Tuple[str, ...] = ()
        if round_num > 1:
            prev_round_certs = self.dag_engine.dag_rounds.get(round_num - 1, {})
            available_digests = list(prev_round_certs.keys())
            if len(available_digests) >= quorum:
                previous_certs = tuple(available_digests)
            else:
                raise RuntimeError(
                    f"Ronda {round_num}: Quórum previo insuficiente ({len(available_digests)} < {quorum})"
                )

        # 3. Emisión de certificados de nodos honestos
        certificates_generated: List[NarwhalCertificate] = []
        signatures_quorum = tuple(range(quorum))

        for node_id in range(honest_count):
            batch_hash = hashlib.sha256(f"batch:{round_num}:{node_id}".encode()).hexdigest()
            vertex = NarwhalVertex(
                origin=node_id,
                round=round_num,
                batch_digest=batch_hash,
                previous_certs=previous_certs,
            )
            cert = NarwhalCertificate(
                vertex=vertex,
                signatures=signatures_quorum,
            )
            self.dag_engine.insert_certificate(cert)
            certificates_generated.append(cert)
            self.reputation_manager.record_success(f"agent_{node_id:04d}", weight=1.0)

        # 4. Registrar telemetría de tareas y evaluar commits
        self.usl_engine.record_task_completed(len(certificates_generated))
        commits = self.dag_engine.linearized_sequence

        return {
            "round": round_num,
            "certificates_count": len(certificates_generated),
            "total_commits": len(commits),
            "slashed_byzantines": slashed_byzantines,
        }

    def broadcast_plumtree(self, origin_id: str, payload: bytes) -> int:
        """Simula la difusión de un mensaje a través de la malla Plumtree."""
        msg_id = hashlib.sha256(payload).hexdigest()
        initial_msg = GossipData(message_id=msg_id, payload=payload, hops=0)
        
        delivered = {origin_id}
        queue = [(origin_id, dest, initial_msg) for dest in self.plumtree_nodes[origin_id].eager_peers]

        max_iterations = 50_000
        iterations = 0

        while queue and iterations < max_iterations:
            iterations += 1
            sender, receiver, msg = queue.pop(0)
            if receiver not in self.plumtree_nodes:
                continue

            node = self.plumtree_nodes[receiver]
            delivered.add(receiver)
            actions = node.on_receive_gossip(sender, msg)

            for target, next_action in actions:
                if isinstance(next_action, GossipData):
                    queue.append((receiver, target, next_action))

        return len(delivered)
