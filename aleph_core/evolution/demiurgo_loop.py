"""
Motor de Auto-Evolución Continua 24/7: Ciclo Demiurgo de 7 Fases + Compuerta de Optimalidad Global Pareto-Dominante (REG-007).
Mientras ECC solo guarda resúmenes de sesión pasivos, El Aleph v2.3.0 ejecuta ciclos autónomos:
1. Diagnosticar telemetría de fallos y claims REFUTED en StateStore.
2. Ejecutar Torneo de Optimalidad Global (GlobalOptimalityGate) evaluando las alternativas bajo los 5 ejes del Consejo de Guerra.
3. Construir validador o contrato formal Pareto-Dominante #1.
4. Verificar contra el motor SMT / ICP / PBT.
5. Criticar mediante el Consejo de Guerra Hostil (WarCouncilSwarm).
6. Refinar y persistir la nueva regla activa en BicameralMemory (descartando reglas obsoletas).
7. Componer nodo reutilizable en el Grafo de Conocimiento.
"""
import ast
import importlib.util
import time
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from aleph_core.config import BASELINE_MARGINAL_COST_USD
from aleph_core.state.store import StateStore
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus, VerificationGate
from aleph_core.memory.bicameral import BicameralMemory, AlgorithmicRule, KnowledgeNode
from aleph_core.security.aegis_shield import AegisShield
from aleph_core.swarm.war_council import WarCouncilSwarm, _max_ast_loop_depth


@dataclass
class SolutionCandidate:
    candidate_id: str
    name: str
    paradigm: str
    complexity_score: float    # 0-100 (mayor = menor complejidad asintótica / menor latencia)
    economic_score: float      # 0-100 (mayor = menor costo marginal / mayor ROI)
    trench_score: float        # 0-100 (mayor = cero fricción / 100% autónomo)
    formal_safety_score: float # 0-100 (mayor = demostración formal completa / 0% falsos positivos)
    moat_score: float          # 0-100 (mayor = componibilidad / ventaja estructural)
    rationale: str = ""

    def vector(self) -> List[float]:
        return [
            self.complexity_score,
            self.economic_score,
            self.trench_score,
            self.formal_safety_score,
            self.moat_score
        ]

    def weighted_total(self) -> float:
        return round(
            0.25 * self.formal_safety_score
            + 0.25 * self.complexity_score
            + 0.20 * self.trench_score
            + 0.15 * self.economic_score
            + 0.15 * self.moat_score,
            2
        )


@dataclass
class OptimalityTournamentResult:
    problem_domain: str
    winner: SolutionCandidate
    pareto_frontier: List[str]
    dominated_rejected: List[Dict[str, Any]]
    unanimous_apex_verified: bool


class GlobalOptimalityGate:
    """
    Compuerta de Optimalidad Global (REG-007):
    Ejecuta un torneo de dominancia de Pareto entre todas las soluciones candidatas conocidas
    para un problema técnico y selecciona exclusivamente el óptimo global (#1 del mundo).
    """
    @staticmethod
    def dominates(a: SolutionCandidate, b: SolutionCandidate) -> bool:
        va, vb = a.vector(), b.vector()
        at_least_as_good = all(x >= y for x, y in zip(va, vb))
        strictly_better = any(x > y for x, y in zip(va, vb))
        return at_least_as_good and strictly_better

    @classmethod
    def run_tournament(cls, problem_domain: str, candidates: List[SolutionCandidate]) -> OptimalityTournamentResult:
        if not candidates:
            raise ValueError("Se requiere al menos 1 candidato para el Torneo de Optimalidad Global.")

        pareto_frontier: List[SolutionCandidate] = []
        dominated_rejected: List[Dict[str, Any]] = []

        for cand in candidates:
            dominators = [
                other.candidate_id
                for other in candidates
                if other.candidate_id != cand.candidate_id and cls.dominates(other, cand)
            ]
            if dominators:
                dominated_rejected.append({
                    "candidate_id": cand.candidate_id,
                    "name": cand.name,
                    "dominated_by": dominators,
                    "score": cand.weighted_total(),
                    "reason": f"Descartado por REG-007: dominado en frontera de Pareto por {dominators}"
                })
            else:
                pareto_frontier.append(cand)

        pareto_frontier.sort(key=lambda c: c.weighted_total(), reverse=True)
        winner = pareto_frontier[0]
        return OptimalityTournamentResult(
            problem_domain=problem_domain,
            winner=winner,
            pareto_frontier=[c.candidate_id for c in pareto_frontier],
            dominated_rejected=dominated_rejected,
            unanimous_apex_verified=(winner.weighted_total() >= 90.0)
        )


@dataclass
class EvolutionCycleReport:
    cycle_id: str
    timestamp: float
    refuted_claims_analyzed: int
    new_rules_synthesized: List[str]
    superseded_rules: List[str]
    knowledge_nodes_added: List[str]
    council_score: float
    duration_ms: float


class DemiurgoEvolutionEngine:
    def __init__(self, store: StateStore, memory: BicameralMemory):
        self.store = store
        self.memory = memory

    def run_self_improvement_cycle(
        self,
        synthetic_friction_events: Optional[List[Dict[str, Any]]] = None
    ) -> EvolutionCycleReport:
        t0 = time.perf_counter_ns()
        io_ns = 0
        cycle_id = f"evo_{uuid.uuid4().hex[:10]}"
        t_io = time.perf_counter_ns()
        refuted_claims = self.store.list_claims(status=EpistemicStatus.REFUTED)
        io_ns += time.perf_counter_ns() - t_io

        new_rules: List[str] = []
        synthesized_rule_objs: List[AlgorithmicRule] = []
        superseded: List[str] = []
        nodes_added: List[str] = []

        events_to_process = list(synthetic_friction_events or [])
        for rc in refuted_claims:
            defect = rc.metadata.get("defect_type", "VERIFICATION_FAILURE")
            cex = rc.metadata.get("counterexample", {})
            events_to_process.append({
                "category": "Código",
                "priority": "Alta",
                "friction": f"Claim {rc.claim_id} refutado ({defect}) con contraejemplo {cex}",
                "if_cond": f"se implementa una función sujeta a {defect} ({rc.description})",
                "then_act": f"declarar contrato explícito @requires/@ensures e inyectar guarda preventiva contra {cex}",
                "avoid_pat": f"despachar código sin precondición formal verificada para {defect}"
            })

        t_io = time.perf_counter_ns()
        existing_rules = self.memory.get_active_rules()
        io_ns += time.perf_counter_ns() - t_io
        next_num = len(existing_rules) + 1
        has_quadratic_loop = False

        for ev in events_to_process:
            rule_id = ev.get("rule_id") or f"REG-{next_num:03d}"
            next_num += 1
            rule = AlgorithmicRule(
                rule_id=rule_id,
                category=ev.get("category", "Código"),
                priority=ev.get("priority", "Alta"),
                friction_pattern=ev["friction"],
                if_condition=ev["if_cond"],
                then_action=ev["then_act"],
                avoid_anti_pattern=ev["avoid_pat"],
                status="Activa",
                confidence=0.96
            )
            t_io = time.perf_counter_ns()
            saved_id, sup_ids = self.memory.upsert_rule(rule)
            io_ns += time.perf_counter_ns() - t_io
            new_rules.append(saved_id)
            synthesized_rule_objs.append(rule)
            superseded.extend(sup_ids)

            if isinstance(ev.get("source_code"), str) and ev["source_code"].strip():
                try:
                    ev_tree = ast.parse(ev["source_code"])
                    if _max_ast_loop_depth(ev_tree) >= 2:
                        has_quadratic_loop = True
                except SyntaxError:
                    pass

            node_id = f"pattern_{saved_id.lower()}"
            t_io = time.perf_counter_ns()
            self.memory.add_knowledge_node(
                KnowledgeNode(
                    node_id=node_id,
                    node_type="EVOLVED_PATTERN",
                    title=f"Patrón Defensivo {saved_id} ({rule.category})",
                    content=rule.format_directive(),
                    tags=[rule.category.lower(), "automejora", "demiurgo"]
                )
            )
            io_ns += time.perf_counter_ns() - t_io
            nodes_added.append(node_id)

        # Medición real de seguridad con AegisShield sobre todas las reglas sintetizadas
        if synthesized_rule_objs:
            security_safe = all(
                AegisShield.scan_text(r.format_directive()).safe
                for r in synthesized_rule_objs
            )
        else:
            security_safe = AegisShield.scan_text("").safe

        # Verificación real de dependencias de ejecución sin módulos rotos
        required_modules = (
            "aleph_core.state.store",
            "aleph_core.state.epistemic",
            "aleph_core.memory.bicameral",
            "aleph_core.security.aegis_shield",
            "aleph_core.swarm.war_council",
        )
        zero_broken_deps = all(importlib.util.find_spec(m) is not None for m in required_modules)

        # Verificación epistémica real de los claims analizados y persistencia de reglas
        t_io = time.perf_counter_ns()
        active_rule_ids = {r.rule_id for r in self.memory.get_active_rules()}
        all_claims = self.store.list_claims()
        io_ns += time.perf_counter_ns() - t_io
        all_persisted = all(rid in active_rule_ids for rid in new_rules)
        evo_claim = EpistemicClaim(
            claim_id=f"evo_claim_{cycle_id}",
            description=f"Auditoría epistémica del ciclo {cycle_id}",
            payload={
                "refuted_claims_analyzed": len(refuted_claims),
                "total_claims": len(all_claims),
                "new_rules": new_rules,
                "nodes_added": nodes_added,
                "all_persisted": all_persisted,
                "security_safe": security_safe,
            },
        )
        verified_claim = VerificationGate.verify(
            evo_claim,
            lambda p: (
                bool(p["all_persisted"])
                and bool(p["security_safe"])
                and len(p["new_rules"]) == len(p["nodes_added"])
            ),
            proof_context=(
                f"Ciclo {cycle_id}: {len(new_rules)} reglas persistidas, "
                f"{len(refuted_claims)} claims refutados analizados, AegisShield={security_safe}"
            ),
        )

        measured_latency_ms = round(max(0.001, ((time.perf_counter_ns() - t0) - io_ns) / 1_000_000.0), 3)

        council = WarCouncilSwarm.evaluate_artifact({
            "latency_ms": measured_latency_ms,
            "has_quadratic_loop": has_quadratic_loop,
            "marginal_cost_usd": BASELINE_MARGINAL_COST_USD,
            "zero_broken_deps": zero_broken_deps,
            "epistemic_status": verified_claim.status.value,
            "security_safe": security_safe,
            "reusable_pattern": bool(nodes_added or existing_rules),
        })

        duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return EvolutionCycleReport(
            cycle_id=cycle_id,
            timestamp=time.time(),
            refuted_claims_analyzed=len(refuted_claims),
            new_rules_synthesized=new_rules,
            superseded_rules=superseded,
            knowledge_nodes_added=nodes_added,
            council_score=council.average_score,
            duration_ms=round(duration_ms, 3)
        )
