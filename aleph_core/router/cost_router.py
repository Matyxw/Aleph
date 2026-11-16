"""
Enrutador Tecno-Económico Soberano y Compuerta Anti-Hype (REG-002).
Garantiza que toda carga interactiva o de razonamiento pesado se enrute primero a
Gemini 4 Argon ($0.00 USD marginal en suscripción Gemini Pro) antes de gastar un solo
centavo en APIs externas, y evalúa modelos candidatos con la rúbrica cuantitativa 0-100.
"""
from collections import Counter
from dataclasses import dataclass
import math
import re
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


def _shannon_entropy_bits(text: str) -> float:
    """Calcula la entropía de Shannon H(X) en bits por carácter."""
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    entropy = 0.0
    for cnt in counts.values():
        p = cnt / n
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def _structural_complexity_metrics(prompt_text: str) -> Dict[str, Any]:
    """Mide entropía de Shannon y complejidad estructural de tokens en un prompt."""
    tokens = re.findall(r"\S+", prompt_text)
    token_count = len(tokens)
    unique_ratio = (len(set(tokens)) / token_count) if token_count else 0.0
    structural_markers = len(re.findall(
        r"(?:\b(?:def|class|async|await|import|from|SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|requires|ensures|invariant)\b|[{}()\[\];:<>]|=>|->|//|/\*)",
        prompt_text,
    ))
    structural_density = min(1.0, structural_markers / max(token_count, 1))
    line_count = max(1, prompt_text.count("\n") + 1)
    entropy_bits = _shannon_entropy_bits(prompt_text)
    complexity_score = round(
        min(1.0, (0.45 * min(1.0, entropy_bits / 6.0)) + (0.35 * structural_density) + (0.20 * unique_ratio)),
        4,
    )
    return {
        "shannon_entropy_bits": entropy_bits,
        "token_count": token_count,
        "unique_token_ratio": round(unique_ratio, 4),
        "structural_markers": structural_markers,
        "structural_density": round(structural_density, 4),
        "line_count": line_count,
        "structural_complexity_score": complexity_score,
    }


class SovereignCostRouter:
    @staticmethod
    def route_task(
        task_complexity: str = "high",
        requires_airgapped_local: bool = False,
        requires_sub_100ms_fim: bool = False,
        context_tokens: int = 25000,
        output_tokens: int = 2000,
        prompt_text: Optional[str] = None,
    ) -> RoutingDecision:
        metrics: Optional[Dict[str, Any]] = None
        if prompt_text is not None:
            metrics = _structural_complexity_metrics(prompt_text)

        if requires_airgapped_local:
            extra = (
                f" [entropía={metrics['shannon_entropy_bits']:.3f} bits/char, "
                f"complejidad_estructural={metrics['structural_complexity_score']:.3f}, "
                f"tokens_prompt={metrics['token_count']}]"
                if metrics is not None else ""
            )
            return RoutingDecision(
                selected_model="vllm-local/qwen2.5-coder-32b-instruct-awq",
                tier="TIER_LOCAL_AIRGAPPED",
                estimated_marginal_cost_usd=0.00,
                rationale=f"Ejecución local air-gapped sin salida a internet (vLLM / SGLang).{extra}",
            )
        if requires_sub_100ms_fim:
            extra = (
                f" [entropía={metrics['shannon_entropy_bits']:.3f} bits/char, "
                f"complejidad_estructural={metrics['structural_complexity_score']:.3f}, "
                f"tokens_prompt={metrics['token_count']}]"
                if metrics is not None else ""
            )
            return RoutingDecision(
                selected_model="local-fim/qwen2.5-coder-7b",
                tier="TIER_1_FIM_AUTOCOMPLETE",
                estimated_marginal_cost_usd=0.00,
                rationale=f"Autocompletado FIM de ultra-baja latencia (<100ms).{extra}",
            )

        tier = "TIER_3_SOVEREIGN_REASONER"
        effective_context_tokens = context_tokens
        metrics_suffix = ""
        if metrics is not None:
            effective_context_tokens = max(context_tokens, metrics["token_count"])
            if (
                task_complexity.lower() == "low"
                and metrics["shannon_entropy_bits"] < 3.6
                and metrics["structural_complexity_score"] < 0.35
                and metrics["token_count"] < 150
            ):
                tier = "TIER_2_LIGHTWEIGHT_SOVEREIGN"
            elif (
                metrics["shannon_entropy_bits"] >= 4.4
                or metrics["structural_complexity_score"] >= 0.55
                or metrics["token_count"] >= 500
            ):
                tier = "TIER_3_SOVEREIGN_REASONER"
            metrics_suffix = (
                f" Métricas prompt: entropía_shannon={metrics['shannon_entropy_bits']:.3f} bits/char, "
                f"complejidad_estructural={metrics['structural_complexity_score']:.3f}, "
                f"densidad_estructural={metrics['structural_density']:.3f}, "
                f"tokens_estimados={metrics['token_count']}."
            )

        # Por defecto: Línea base obligatoria Gemini 4 Argon ($0.00 USD marginal en Gemini Pro)
        return RoutingDecision(
            selected_model=BASELINE_MODEL,
            tier=tier,
            estimated_marginal_cost_usd=BASELINE_MARGINAL_COST_USD,
            rationale=(
                f"Enrutado a {BASELINE_MODEL} ($0.00 USD marginal cubierto por suscripción Gemini Pro) "
                f"para {effective_context_tokens} tokens de entrada y {output_tokens} de salida (REG-002)."
                f"{metrics_suffix}"
            ),
        )

    @staticmethod
    def evaluate_external_model(
        model_name: str,
        frontier_pareto_pts: int,
        reproducibility_pts: int,
        architectural_novelty_pts: int,
        practical_leverage_pts: int,
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
            passed_gate=passed,
        )
