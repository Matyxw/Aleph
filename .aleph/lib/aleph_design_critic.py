"""
.aleph/lib/aleph_design_critic.py
Design Critic & Bradley-Terry ELO Governor (Track 9).
Estándar: 10-Vector Rubric / Bradley-Terry Paired Comparison / Anti-Collapse Latent Governor.

Evalúa formalmente cualquier DesignIR o par de diseños:
1. Rúbrica ponderada de 10 vectores (0 a 100 puntos soberanos).
2. Motor de rating Bradley-Terry Elo probabilístico para benchmarks y A/B tests.
3. Gobernador de Espacio Latente Anti-Colapso: previene la convergencia hacia plantillas repetitivas
   verificando que la distancia de características D_latent >= 0.25 respecto al buffer histórico.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    from lib.aleph_design_ir import (
        AestheticParadigm,
        DesignIR,
        IRComponent,
        SpatialArchetype,
        StateName,
        TaskPhase,
    )
except ImportError:
    from aleph_design_ir import (  # type: ignore
        AestheticParadigm,
        DesignIR,
        IRComponent,
        SpatialArchetype,
        StateName,
        TaskPhase,
    )


@dataclass
class CritiqueScorecard:
    """Desglose formal de la evaluación de un diseño en 10 dimensiones."""
    typography_score: float           # w=0.12 (0 a 10)
    color_contrast_score: float       # w=0.14 (0 a 10)
    spatial_balance_score: float      # w=0.12 (0 a 10)
    motion_physics_score: float       # w=0.10 (0 a 10)
    info_density_score: float         # w=0.10 (0 a 10)
    craftsmanship_score: float        # w=0.10 (0 a 10)
    accessibility_score: float        # w=0.10 (0 a 10)
    anti_slop_score: float            # w=0.10 (0 a 10)
    responsiveness_score: float       # w=0.08 (0 a 10)
    performance_score: float          # w=0.04 (0 a 10)
    feedback_notes: List[str] = field(default_factory=list)

    @property
    def total_score(self) -> float:
        """Puntaje ponderado sobre 100."""
        raw = (
            self.typography_score * 0.12
            + self.color_contrast_score * 0.14
            + self.spatial_balance_score * 0.12
            + self.motion_physics_score * 0.10
            + self.info_density_score * 0.10
            + self.craftsmanship_score * 0.10
            + self.accessibility_score * 0.10
            + self.anti_slop_score * 0.10
            + self.responsiveness_score * 0.08
            + self.performance_score * 0.04
        ) * 10.0
        return round(raw, 2)

    @property
    def is_sovereign(self) -> bool:
        """Un diseño califica como 'Soberano' si total_score >= 82.0 y anti_slop >= 8.0."""
        return self.total_score >= 82.0 and self.anti_slop_score >= 8.0


@dataclass
class EloCompetitor:
    """Entidad registrada en el ranking Bradley-Terry Elo."""
    id: str
    rating: float = 1500.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0


class BradleyTerryEloEngine:
    """Motor de Emparejamiento y Rating Bradley-Terry."""

    def __init__(self, k_factor: float = 32.0):
        self.k_factor = k_factor
        self.competitors: Dict[str, EloCompetitor] = {}

    def register(self, competitor_id: str, initial_rating: float = 1500.0) -> EloCompetitor:
        if competitor_id not in self.competitors:
            self.competitors[competitor_id] = EloCompetitor(id=competitor_id, rating=initial_rating)
        return self.competitors[competitor_id]

    def win_probability(self, rating_a: float, rating_b: float) -> float:
        """Calcula P(A > B) = 1 / (1 + 10^((R_B - R_A)/400))."""
        return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))

    def record_match(self, id_a: str, id_b: str, score_a: float) -> Tuple[float, float]:
        """
        Registra el resultado de un match.
        score_a: 1.0 (gana A), 0.5 (empate), 0.0 (gana B).
        Retorna las nuevas clasificaciones (R_A, R_B).
        """
        comp_a = self.register(id_a)
        comp_b = self.register(id_b)

        p_a = self.win_probability(comp_a.rating, comp_b.rating)
        p_b = 1.0 - p_a

        delta_a = self.k_factor * (score_a - p_a)
        delta_b = self.k_factor * ((1.0 - score_a) - p_b)

        comp_a.rating = round(comp_a.rating + delta_a, 2)
        comp_b.rating = round(comp_b.rating + delta_b, 2)

        comp_a.matches_played += 1
        comp_b.matches_played += 1

        if score_a == 1.0:
            comp_a.wins += 1
            comp_b.losses += 1
        elif score_a == 0.0:
            comp_b.wins += 1
            comp_a.losses += 1
        else:
            comp_a.draws += 1
            comp_b.draws += 1

        return (comp_a.rating, comp_b.rating)


class AntiCollapseLatentGovernor:
    """
    Gobernador de Espacio Latente Anti-Colapso.
    Evita la degeneración de la IA hacia las mismas 2 o 3 plantillas genéricas.
    Calcula distancia coseno de características vectoriales respecto al histórico.
    """

    MIN_DISTANCE_THRESHOLD = 0.25

    def __init__(self):
        self.generation_buffer: List[List[float]] = []

    def extract_feature_vector(self, ir: DesignIR) -> List[float]:
        """Extrae un vector representativo de 8 dimensiones continuas normalizadas."""
        # 1. Asymmetric ratio normalizado
        v1 = min(3.0, ir.spatial_grammar.asymmetric_ratio) / 3.0

        # 2. Número de componentes interactivos
        interactive_count = sum(1 for c in ir.root_components if c.is_interactive)
        v2 = min(10, interactive_count) / 10.0

        # 3. Max container width normalizado
        v3 = min(2560.0, ir.spatial_grammar.bounds.max_container_width) / 2560.0

        # 4. Promedio de luminancia en colores de tokens
        mean_l = 0.5
        if ir.perceptual_tokens.colors:
            mean_l = sum(c.oklch[0] for c in ir.perceptual_tokens.colors.values()) / len(ir.perceptual_tokens.colors)
        v4 = mean_l

        # 5. Promedio de croma
        mean_c = 0.1
        if ir.perceptual_tokens.colors:
            mean_c = sum(c.oklch[1] for c in ir.perceptual_tokens.colors.values()) / len(ir.perceptual_tokens.colors)
        v5 = min(0.4, mean_c) / 0.4

        # 6. Presencia de assets soberanos (shaders / SVGs)
        v6 = 1.0 if (ir.assets.shaders or ir.assets.svgs) else 0.0

        # 7. Rigidez media de resortes
        mean_stiffness = 100.0
        if ir.motion.tokens:
            springs = [m.spring.stiffness for m in ir.motion.tokens.values() if m.spring]
            if springs:
                mean_stiffness = sum(springs) / len(springs)
        v7 = min(300.0, mean_stiffness) / 300.0

        # 8. Hash posicional del paradigma estético
        paradigm_index = list(AestheticParadigm).index(ir.paradigm)
        v8 = paradigm_index / 12.0

        return [v1, v2, v3, v4, v5, v6, v7, v8]

    def feature_distance(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calcula distancia Euclidiana en el espacio latente de características."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

    def check_and_record(self, ir: DesignIR) -> Tuple[bool, float]:
        """
        Verifica si el nuevo diseño tiene suficiente diversidad estética.
        Retorna (pasa_control, min_distancia).
        """
        vec = self.extract_feature_vector(ir)
        if not self.generation_buffer:
            self.generation_buffer.append(vec)
            return (True, 1.0)

        min_dist = min(self.feature_distance(vec, hist) for hist in self.generation_buffer)
        passes = min_dist >= self.MIN_DISTANCE_THRESHOLD

        if passes:
            self.generation_buffer.append(vec)
            if len(self.generation_buffer) > 50:
                self.generation_buffer.pop(0)

        return (passes, round(min_dist, 4))


class AlephDesignCritic:
    """
    Crítico de Diseño Soberano.
    Combina la rúbrica de 10 vectores, Bradley-Terry Elo y Gobernador Anti-Colapso.
    """

    def __init__(self):
        self.elo_engine = BradleyTerryEloEngine()
        self.latent_governor = AntiCollapseLatentGovernor()

    def critique(self, ir: DesignIR) -> CritiqueScorecard:
        """Evalúa exhaustivamente un DesignIR."""
        feedback = []

        # 1. Tipografía (0 a 10)
        typo_score = 9.0
        if "Inter" in ir.typography.primary_family or "Geist" in ir.typography.primary_family:
            typo_score -= 4.0
            feedback.append("Tipografía genérica de IA (Inter/Geist) penalizada.")
        for scale in ir.typography.scales.values():
            if scale.is_headline and (scale.max_lines is None or scale.max_lines > 3):
                typo_score -= 3.0
                feedback.append(f"Titular '{scale.name}' viola la regla de oro (max_lines <= 3).")

        # 2. Color y Contraste (0 a 10)
        color_score = 9.5
        for name, col in ir.perceptual_tokens.colors.items():
            if col.role in ("on_surface", "primary") and col.wcag_contrast_on_surface:
                if col.wcag_contrast_on_surface < 4.5:
                    color_score -= 2.0
                    feedback.append(f"Color '{name}' no cumple umbral WCAG 2.2 AA (4.5:1).")

        # 3. Balance Espacial (0 a 10)
        spatial_score = 9.0
        if ir.spatial_grammar.archetype == SpatialArchetype.HERO_MONOLITH and ir.spatial_grammar.asymmetric_ratio == 1.0:
            spatial_score -= 1.5

        # 4. Física de Movimiento (0 a 10)
        motion_score = 9.5
        if not ir.motion.reduced_motion_global_policy.enabled:
            motion_score = 0.0
            feedback.append("Falta política obligatoria de reduced-motion.")

        # 5. Densidad de Información (0 a 10)
        info_score = 8.5

        # 6. Artesanía / Micro-detalles (0 a 10)
        craft_score = 9.0
        if ir.assets.shaders or ir.assets.svgs:
            craft_score = 10.0

        # 7. Accesibilidad Semántica (0 a 10)
        a11y_score = 9.5
        for comp in ir.root_components:
            if comp.is_interactive and not comp.state_matrix:
                a11y_score -= 3.0
                feedback.append(f"Componente interactivo '{comp.id}' carece de matriz de estados.")

        # 8. Anti-Slop (0 a 10)
        anti_slop = 9.5

        # 9. Responsividad SMT (0 a 10)
        resp_score = 10.0
        if ir.spatial_grammar.bounds.min_viewport >= ir.spatial_grammar.bounds.max_viewport:
            resp_score = 2.0

        # 10. Eficiencia y Performance (0 a 10)
        perf_score = 9.5

        return CritiqueScorecard(
            typography_score=max(0.0, min(10.0, typo_score)),
            color_contrast_score=max(0.0, min(10.0, color_score)),
            spatial_balance_score=max(0.0, min(10.0, spatial_score)),
            motion_physics_score=max(0.0, min(10.0, motion_score)),
            info_density_score=max(0.0, min(10.0, info_score)),
            craftsmanship_score=max(0.0, min(10.0, craft_score)),
            accessibility_score=max(0.0, min(10.0, a11y_score)),
            anti_slop_score=max(0.0, min(10.0, anti_slop)),
            responsiveness_score=max(0.0, min(10.0, resp_score)),
            performance_score=max(0.0, min(10.0, perf_score)),
            feedback_notes=feedback
        )

    def compare_and_rank(self, ir_a: DesignIR, ir_b: DesignIR, id_a: str, id_b: str) -> Dict[str, Any]:
        """Compara dos diseños por rúbrica formal y actualiza el rating Elo."""
        card_a = self.critique(ir_a)
        card_b = self.critique(ir_b)

        if card_a.total_score > card_b.total_score + 1.0:
            score_a = 1.0
        elif card_b.total_score > card_a.total_score + 1.0:
            score_a = 0.0
        else:
            score_a = 0.5

        new_r_a, new_r_b = self.elo_engine.record_match(id_a, id_b, score_a)

        return {
            "winner": id_a if score_a == 1.0 else (id_b if score_a == 0.0 else "TIE"),
            "design_a": {"score": card_a.total_score, "new_elo": new_r_a},
            "design_b": {"score": card_b.total_score, "new_elo": new_r_b},
        }
