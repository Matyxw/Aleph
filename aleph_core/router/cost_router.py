"""
Enrutador Tecno-Económico Soberano y Compuerta Anti-Hype (REG-002).
Garantiza que toda carga interactiva o de razonamiento pesado se enrute primero a
Gemini 4 Argon ($0.00 USD marginal en suscripción Gemini Pro) antes de gastar un solo
centavo en APIs externas, y evalúa modelos candidatos con la rúbrica cuantitativa 0-100.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from aleph_core.config import BASELINE_MODEL, BASELINE_MARGINAL_COST_USD, ANTI_HYPE_MIN_SCORE

@dataclass
class RoutingDecision:
    selected_model: str
    tier: str
    estimated_marginal_cost_usd: float
    rationale: str

@dataclass
class AntiHypeEvaluation:
    model_name: str
    frontier_pareto_pts: int       # 0-35
    reproducibility_pts: int       # 0-25
    architectural_novelty_pts: int # 0-20
    practical_leverage_pts: int    # 0-20
    total_score: int
    verdict: str                   # 'MIGRAR YA' | 'PROBAR EN SANDBOX' | 'MONITOREAR' | 'DESCARTADO POR HYPE'
    passed_gate: bool

class SovereignCostRouter:
    @staticmethod
    def route_task(
        task_complexity: str = "high",
        requires_airgapped_local: bool = False,
        requires_sub_100ms_fim: bool = False,
        context_tokens: int = 25000,
        output_tokens: int = 2000
    ) -> RoutingDecision:
        if requires_airgapped_local:
            return RoutingDecision(
                selected_model="vllm-local/qwen2.5-coder-32b-instruct-awq",
                tier="TIER_LOCAL_AIRGAPPED",
                estimated_marginal_cost_usd=0.00,
                rationale="Ejecución local air-gapped sin salida a internet (vLLM / SGLang)."
            )
        if requires_sub_100ms_fim:
            return RoutingDecision(
                selected_model="local-fim/qwen2.5-coder-7b",
                tier="TIER_1_FIM_AUTOCOMPLETE",
                estimated_marginal_cost_usd=0.00,
                rationale="Autocompletado FIM de ultra-baja latencia (<100ms)."
            )
        # Por defecto: Línea base obligatoria Gemini 4 Argon ($0.00 USD marginal en Gemini Pro)
        return RoutingDecision(
            selected_model=BASELINE_MODEL,
            tier="TIER_3_SOVEREIGN_REASONER",
            estimated_marginal_cost_usd=BASELINE_MARGINAL_COST_USD,
            rationale=(
                f"Enrutado a {BASELINE_MODEL} ($0.00 USD marginal cubierto por suscripción Gemini Pro) "
                f"para {context_tokens} tokens de entrada y {output_tokens} de salida (REG-002)."
            )
        )

    @staticmethod
    def evaluate_external_model(
        model_name: str,
        frontier_pareto_pts: int,
        reproducibility_pts: int,
        architectural_novelty_pts: int,
        practical_leverage_pts: int
    ) -> AntiHypeEvaluation:
        f_pts = max(0, min(35, frontier_pareto_pts))
        r_pts = max(0, min(25, reproducibility_pts))
        a_pts = max(0, min(20, architectural_novelty_pts))
        p_pts = max(0, min(20, practical_leverage_pts))
        total = f_pts + r_pts + a_pts + p_pts
        passed = total >= ANTI_HYPE_MIN_SCORE
        if not passed:
            verdict = "DESCARTADO POR HYPE"
        elif total >= 85:
            verdict = "MIGRAR YA"
        elif total >= 75:
            verdict = "PROBAR EN SANDBOX"
        else:
            verdict = "MONITOREAR"
        return AntiHypeEvaluation(
            model_name=model_name,
            frontier_pareto_pts=f_pts,
            reproducibility_pts=r_pts,
            architectural_novelty_pts=a_pts,
            practical_leverage_pts=p_pts,
            total_score=total,
            verdict=verdict,
            passed_gate=passed
        )
