"""
aleph_core/evolution/optimality_gate.py
Compuerta de Optimalidad Global Pareto-Dominante (REG-007).
Prohíbe aceptar cualquier diseño o algoritmo si existe una alternativa estrictamente superior
en el estado del arte mundial evaluada bajo los 5 ejes del Consejo de Guerra:
1. Complejidad y Latencia Mecánica (Performance)
2. Costo Marginal y Eficiencia Tecno-Económica (Finanzas)
3. Autonomía y Cero Dependencias Rotas (Trinchera)
4. Garantía Matemática y Superficie de Ataque (Red-Team)
5. Composición y Foso Defensivo (Moats)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SolutionCandidate:
    candidate_id: str
    name: str
    paradigm: str
    complexity_score: float   # 0-100 (mayor = menor complejidad asintótica / menor latencia)
    economic_score: float     # 0-100 (mayor = menor costo marginal / mayor ROI)
    trench_score: float       # 0-100 (mayor = cero fricción / 100% autónomo)
    formal_safety_score: float# 0-100 (mayor = demostración formal completa / 0% falsos positivos)
    moat_score: float         # 0-100 (mayor = componibilidad / ventaja estructural)
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
        # Pesos alineados con la exigencia soberana de El Aleph
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
            dominators = [other.candidate_id for other in candidates if other.candidate_id != cand.candidate_id and cls.dominates(other, cand)]
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
