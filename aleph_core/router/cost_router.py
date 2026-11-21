"""
Enrutador Tecno-Económico Soberano, Compuerta Anti-Hype y Orquestador Cognitivo Asimétrico (REG-002).
Garantiza que toda carga interactiva o de razonamiento pesado se enrute primero a
Gemini 4 Argon ($0.00 USD marginal en suscripción Gemini Pro) antes de gastar un solo
centavo en APIs externas, y asigna cómputo asimétrico (Tier 0 AST/CAS a Tier 3 Razón Profunda)
según entropía de Shannon y densidad estructural.
"""
from collections import Counter
from dataclasses import dataclass, asdict
import json
import math
import os
from pathlib import Path
import re
from typing import Dict, Any, Optional
from aleph_core.config import (
    BASELINE_MODEL,
    BASELINE_MARGINAL_COST_USD,
    ANTI_HYPE_MIN_SCORE,
    LOCAL_DETERMINISTIC_ENGINE,
    GEMINI4_HYDROGEN_MODEL,
    GEMINI4_NEON_MODEL,
    GEMINI4_ARGON_MODEL,
)

DEFAULT_GEMINI4_TIER_PROFILES: Dict[str, Dict[str, Any]] = {
    "TIER_0_DETERMINISTIC_AST_CAS": {
        "model_id": LOCAL_DETERMINISTIC_ENGINE,
        "variant": "Local-Deterministic",
        "max_tokens": 0,
        "marginal_cost_usd": 0.0,
        "delegation_mode": "local_deterministic_ast_cas",
    },
    "TIER_1_FIM_AUTOCOMPLETE": {
        "model_id": GEMINI4_HYDROGEN_MODEL,
        "variant": "Hydrogen",
        "max_tokens": 512,
        "marginal_cost_usd": 0.0,
        "delegation_mode": "subagent_fast_reactive",
    },
    "TIER_2_LIGHTWEIGHT_SOVEREIGN": {
        "model_id": GEMINI4_NEON_MODEL,
        "variant": "Neon",
        "max_tokens": 2048,
        "marginal_cost_usd": 0.0,
        "delegation_mode": "subagent_balanced_code",
    },
    "TIER_3_SOVEREIGN_REASONER": {
        "model_id": GEMINI4_ARGON_MODEL,
        "variant": "Argon",
        "max_tokens": 4096,
        "marginal_cost_usd": 0.0,
        "delegation_mode": "primary_deep_reasoner",
    },
}


def load_gemini4_tier_profiles() -> Dict[str, Dict[str, Any]]:
    """Carga los perfiles de enrutamiento cognitivo Gemini 4 desde env o .aleph/gemini4_models.json."""
    profiles = {k: dict(v) for k, v in DEFAULT_GEMINI4_TIER_PROFILES.items()}
    env_override = os.environ.get("ALEPH_GEMINI4_PROFILES_JSON", "").strip()
    if env_override:
        try:
            parsed = json.loads(env_override)
            tiers = parsed.get("tiers", parsed) if isinstance(parsed, dict) else {}
            if isinstance(tiers, dict):
                for tk, tv in tiers.items():
                    if tk in profiles and isinstance(tv, dict):
                        profiles[tk].update(tv)
                return profiles
        except Exception:
            pass
    cfg_path = Path(__file__).resolve().parents[2] / ".aleph" / "gemini4_models.json"
    if cfg_path.exists():
        try:
            parsed = json.loads(cfg_path.read_text(encoding="utf-8"))
            tiers = parsed.get("tiers", {})
            if isinstance(tiers, dict):
                for tk, tv in tiers.items():
                    if tk in profiles and isinstance(tv, dict):
                        profiles[tk].update(tv)
        except Exception:
            pass
    return profiles


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


@dataclass(frozen=True)
class AsymmetricComputeAllocation:
    """Asignación asimétrica de tier cognitivo y presupuesto de tokens para un nodo del DAG."""
    node_id: str
    tier: str
    token_budget: int
    shannon_entropy_bits: float
    structural_complexity_score: float
    selected_model: str = GEMINI4_ARGON_MODEL
    gemini4_variant: str = "Argon"
    delegation_mode: str = "primary_deep_reasoner"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    def allocate_dag_compute(
        nodes_prompts: Dict[str, str],
        total_token_budget: int = 12000,
    ) -> Dict[str, Any]:
        """
        Orquestación Cognitiva Asimétrica sobre nodos de un DAG:
        - TIER_0_DETERMINISTIC_AST_CAS (0 tokens LLM, local-ast-cas/python-z3): chequeos mecánicos, hashes CAS o tags [AST]/[CAS]/[Z3_LOCAL].
        - TIER_1_FIM_AUTOCOMPLETE (<= 512 tokens, gemini-4-hydrogen): ediciones locales de baja entropía.
        - TIER_2_LIGHTWEIGHT_SOVEREIGN (<= 2048 tokens, gemini-4-neon): lógica moderada / pruebas puntuales.
        - TIER_3_SOVEREIGN_REASONER (presupuesto prioritario, gemini-4-argon): síntesis formal Z3, arquitectura y auditoría crítica.
        """
        if not nodes_prompts:
            return {
                "allocations": {},
                "total_allocated_tokens": 0,
                "total_token_budget": total_token_budget,
                "naive_uniform_tokens": 0,
                "token_savings_pct": 0.0,
                "model_distribution": {},
            }

        tier_profiles = load_gemini4_tier_profiles()
        raw_specs: Dict[str, Tuple[str, int, float, float]] = {}
        for nid, text in nodes_prompts.items():
            m = _structural_complexity_metrics(text)
            ent = m["shannon_entropy_bits"]
            comp = m["structural_complexity_score"]
            tok = m["token_count"]
            markers = m["structural_markers"]
            upper = text.upper()
            has_formal_deep = bool(re.search(r"\b(z3|smt|theorem|prover|deadlock|rls|taint|invariant)\b", upper, re.IGNORECASE))

            if "[CAS]" in upper or "[AST]" in upper or "[Z3_LOCAL]" in upper or (tok <= 12 and ent < 3.4 and comp < 0.35):
                tier = "TIER_0_DETERMINISTIC_AST_CAS"
                desired = int(tier_profiles[tier].get("max_tokens", 0))
            elif tok < 45 and ent < 4.1 and markers <= 1 and comp < 0.55 and not has_formal_deep:
                tier = "TIER_1_FIM_AUTOCOMPLETE"
                desired = int(tier_profiles[tier].get("max_tokens", 512))
            elif (ent >= 4.65 and comp >= 0.56) or comp >= 0.65 or tok >= 120 or (tok >= 25 and has_formal_deep):
                tier = "TIER_3_SOVEREIGN_REASONER"
                max_t = int(tier_profiles[tier].get("max_tokens", 4096))
                desired = min(max_t, max(2048, tok * 8))
            else:
                tier = "TIER_2_LIGHTWEIGHT_SOVEREIGN"
                desired = min(1536, int(tier_profiles[tier].get("max_tokens", 2048)))
            raw_specs[nid] = (tier, desired, ent, comp)

        desired_sum = sum(v[1] for v in raw_specs.values())
        scale = min(1.0, float(total_token_budget) / max(1, desired_sum)) if desired_sum > total_token_budget else 1.0

        allocations: Dict[str, Dict[str, Any]] = {}
        model_distribution: Dict[str, int] = {}
        total_allocated = 0
        for nid in sorted(raw_specs.keys()):
            tier, desired, ent, comp = raw_specs[nid]
            budget = 0 if desired == 0 else max(128, int(desired * scale))
            prof = tier_profiles.get(tier, DEFAULT_GEMINI4_TIER_PROFILES["TIER_3_SOVEREIGN_REASONER"])
            selected_model = str(prof.get("model_id", GEMINI4_ARGON_MODEL))
            variant = str(prof.get("variant", "Argon"))
            delegation_mode = str(prof.get("delegation_mode", "primary_deep_reasoner"))
            alloc = AsymmetricComputeAllocation(
                node_id=nid,
                tier=tier,
                token_budget=budget,
                shannon_entropy_bits=ent,
                structural_complexity_score=comp,
                selected_model=selected_model,
                gemini4_variant=variant,
                delegation_mode=delegation_mode,
            )
            allocations[nid] = alloc.to_dict()
            model_distribution[selected_model] = model_distribution.get(selected_model, 0) + 1
            total_allocated += budget

        # Ajuste exacto si el redondeo superó total_token_budget
        if total_allocated > total_token_budget and total_allocated > 0:
            excess = total_allocated - total_token_budget
            for nid in sorted(allocations.keys(), key=lambda k: allocations[k]["token_budget"], reverse=True):
                if allocations[nid]["token_budget"] > excess:
                    allocations[nid]["token_budget"] -= excess
                    total_allocated -= excess
                    break

        naive_uniform = len(nodes_prompts) * 4096
        savings_pct = round(max(0.0, (1.0 - (total_allocated / max(1, naive_uniform))) * 100.0), 2)
        return {
            "allocations": allocations,
            "total_allocated_tokens": total_allocated,
            "total_token_budget": total_token_budget,
            "naive_uniform_tokens": naive_uniform,
            "token_savings_pct": savings_pct,
            "model_distribution": model_distribution,
        }

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
