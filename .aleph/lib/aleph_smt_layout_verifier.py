"""
.aleph/lib/aleph_smt_layout_verifier.py
Verificador Formal SMT (Microsoft Z3) de Responsividad, Contención y Manifold Espacial 2D.
Estándar: Aleph Sovereign Design Engine / SMT Spatial Architecture v2.0.

Capacidades formales:
1. Invariante 1D de no-desbordamiento horizontal (ausencia de overflow-x).
2. Teorema de No-Solapamiento (Non-Overlapping Theorem): Separating Axis Theorem en R2 continuo [320.0, 3840.0].
3. Teorema de Contención de Viewport 2D (2D Bounding Box Containment Theorem).
4. Invariante de Accesibilidad Táctil (WCAG 2.5.5 / Apple HIG Touch Target Invariant >= 48x48px).
5. Invariante de Jerarquía Z-Index (Stacking Context & Layer Occlusion Invariant).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import z3
except ImportError:
    z3 = None


# ============================================================================
# MODELOS DE GEOMETRÍA Y MEDIDA FLUIDA
# ============================================================================

@dataclass
class FluidMeasure:
    """Representa una dimensión fluida CSS clamp(min_val, slope * w + base, max_val)."""
    min_val: float
    slope: float
    base: float
    max_val: float

    def eval_at(self, w: float) -> float:
        """Evalúa numéricamente en un ancho de viewport w."""
        val = self.slope * w + self.base
        return max(self.min_val, min(self.max_val, val))

    def to_z3_expr(self, w_var: z3.ArithRef) -> z3.ArithRef:
        """Traduce la función clamp a una expresión SMT en Z3."""
        val = self.slope * w_var + self.base
        return z3.If(
            val < self.min_val,
            z3.RealVal(self.min_val),
            z3.If(val > self.max_val, z3.RealVal(self.max_val), val)
        )

    @classmethod
    def fixed(cls, val: float) -> FluidMeasure:
        """Crea una medida estática invariable respecto a viewport."""
        return cls(min_val=val, slope=0.0, base=val, max_val=val)

    @classmethod
    def fluid(cls, min_val: float, slope: float, base: float, max_val: float) -> FluidMeasure:
        """Crea una medida fluida responsiva CSS clamp()."""
        return cls(min_val=min_val, slope=slope, base=base, max_val=max_val)


@dataclass
class FluidBox2D:
    """Representa una caja delimitadora 2D (Bounding Box) en coordenadas cartesianas."""
    x: FluidMeasure
    y: FluidMeasure
    width: FluidMeasure
    height: FluidMeasure

    def eval_at(self, w: float) -> Tuple[float, float, float, float]:
        """Evalúa numéricamente (x, y, width, height) para un ancho de viewport w."""
        return (
            self.x.eval_at(w),
            self.y.eval_at(w),
            self.width.eval_at(w),
            self.height.eval_at(w),
        )

    def to_z3_exprs(self, w_var: z3.ArithRef) -> Tuple[z3.ArithRef, z3.ArithRef, z3.ArithRef, z3.ArithRef]:
        """Traduce las 4 dimensiones cartesianas a expresiones SMT en Z3."""
        return (
            self.x.to_z3_expr(w_var),
            self.y.to_z3_expr(w_var),
            self.width.to_z3_expr(w_var),
            self.height.to_z3_expr(w_var),
        )


class LayerRank:
    """Estratificación canónica de capas para prevenir oclusión e inversión de Z-Index."""
    WEBGL_CANVAS: int = 0
    CONTENT_BASE: int = 100
    CONTENT_RAISED: int = 200
    STICKY_NAV: int = 500
    POPOVER_DROPDOWN: int = 700
    MODAL_BACKDROP: int = 900
    MODAL_CONTENT: int = 950
    TOAST_NOTIFICATION: int = 1000


@dataclass
class LayoutNode2D:
    """Nodo espacial 2D enriquecido con semántica interactiva, capa Z y contención perimétrica."""
    id: str
    box: FluidBox2D
    z_index: int = LayerRank.CONTENT_BASE
    is_interactive: bool = False
    is_critical_content: bool = False
    pointer_events: bool = True
    layer_category: str = "content"
    children: List[LayoutNode2D] = field(default_factory=list)
    padding: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)  # (top, right, bottom, left)


@dataclass
class LayoutElement:
    """Elemento hijo dentro de un contenedor horizontal o grid (Modelo 1D)."""
    id: str
    width: FluidMeasure
    margin_left: float = 0.0
    margin_right: float = 0.0
    flex_grow: float = 0.0
    flex_shrink: float = 1.0
    min_width_zero: bool = True  # En CSS: min-width: 0 evita desbordes en flex
    is_wrap_breaker: bool = False

    def total_width_expr(self, w_var: z3.ArithRef) -> z3.ArithRef:
        """Ancho total ocupado por el elemento (incluyendo márgenes fijos)."""
        w_expr = self.width.to_z3_expr(w_var)
        margins = z3.RealVal(self.margin_left + self.margin_right)
        return w_expr + margins


@dataclass
class LayoutContainer:
    """Contenedor horizontal que alberga elementos secundarios (Modelo 1D)."""
    id: str
    width: FluidMeasure
    padding_left: float = 0.0
    padding_right: float = 0.0
    gap: float = 0.0
    direction: str = "row"  # "row" o "column"
    wrap: bool = False      # flex-wrap: wrap o nowrap
    children: List[LayoutElement] = field(default_factory=list)


@dataclass
class SMTVerificationResult:
    """Resultado formal unificado emitido por el solver Z3 (1D y 2D)."""
    is_overflow_free: bool
    status: str  # "UNSAT" (demostrado seguro), "SAT" (contraejemplo encontrado), "UNKNOWN"
    counterexample_w: Optional[float] = None
    expected_container_w: Optional[float] = None
    actual_children_w: Optional[float] = None
    overflow_margin_px: Optional[float] = None
    theorem: str = "Horizontal Containment Invariant"
    is_valid: Optional[bool] = None
    counterexample_details: Dict[str, Any] = field(default_factory=dict)
    proof_formula: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.is_valid is None:
            self.is_valid = self.is_overflow_free


# ============================================================================
# MOTOR DE VERIFICACIÓN FORMAL SMT (Z3)
# ============================================================================

class SMTLayoutVerifier:
    """
    Motor de verificación formal de restricciones de layout espacial usando Microsoft Z3.
    Demuestra teoremas geométricos en el continuo [min_viewport, max_viewport].
    """

    def __init__(self, min_viewport: float = 320.0, max_viewport: float = 3840.0):
        self.min_viewport = min_viewport
        self.max_viewport = max_viewport

    # ------------------------------------------------------------------------
    # 1. VERIFICACIÓN 1D: Ausencia de Desbordamiento Horizontal
    # ------------------------------------------------------------------------

    def verify_horizontal_containment(
        self,
        container: LayoutContainer,
        precision: float = 0.5
    ) -> SMTVerificationResult:
        """
        Demuestra si existe algún viewport w in [min_viewport, max_viewport]
        donde la suma de los anchos de los hijos supere el ancho del contenedor.
        """
        if container.direction == "column" or container.wrap:
            return self._verify_individual_children(container, precision)

        solver = z3.Solver()
        w = z3.Real("w")

        solver.add(w >= self.min_viewport)
        solver.add(w <= self.max_viewport)

        container_w_expr = container.width.to_z3_expr(w)
        available_inner_w = container_w_expr - (container.padding_left + container.padding_right)

        if not container.children:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="1D Horizontal Containment",
                details={"reason": "Contenedor sin hijos"}
            )

        num_children = len(container.children)
        total_gaps = max(0, num_children - 1) * container.gap
        children_sum = z3.RealVal(total_gaps)

        for child in container.children:
            children_sum = children_sum + child.total_width_expr(w)

        overflow_condition = children_sum > (available_inner_w + precision)
        solver.add(overflow_condition)

        check_status = solver.check()

        if check_status == z3.unsat:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="1D Horizontal Containment",
                details={
                    "container_id": container.id,
                    "children_count": num_children,
                    "checked_range": (self.min_viewport, self.max_viewport),
                    "proof": "Formalmente demostrado por Z3: insatisfacible condición de overflow."
                }
            )
        elif check_status == z3.sat:
            model = solver.model()
            w_val = float(model[w].as_decimal(4).replace("?", ""))
            
            cont_w_eval = container.width.eval_at(w_val) - (container.padding_left + container.padding_right)
            children_w_eval = total_gaps + sum(c.width.eval_at(w_val) + c.margin_left + c.margin_right for c in container.children)
            overflow_amount = children_w_eval - cont_w_eval

            return SMTVerificationResult(
                is_overflow_free=False,
                status="SAT",
                theorem="1D Horizontal Containment",
                counterexample_w=round(w_val, 2),
                expected_container_w=round(cont_w_eval, 2),
                actual_children_w=round(children_w_eval, 2),
                overflow_margin_px=round(overflow_amount, 2),
                details={
                    "container_id": container.id,
                    "offending_viewport": round(w_val, 2),
                    "overflow_px": round(overflow_amount, 2),
                    "recommendation": "Activar flex-wrap: wrap o ajustar fluid clamp de hijos."
                }
            )
        else:
            return SMTVerificationResult(
                is_overflow_free=False,
                status="UNKNOWN",
                theorem="1D Horizontal Containment",
                details={"reason": "Solver timeout o problema no decidible"}
            )

    def _verify_individual_children(
        self,
        container: LayoutContainer,
        precision: float
    ) -> SMTVerificationResult:
        """Verifica que ningún hijo individual supere el ancho interno del contenedor."""
        for child in container.children:
            solver = z3.Solver()
            w = z3.Real("w")
            solver.add(w >= self.min_viewport)
            solver.add(w <= self.max_viewport)

            container_inner_w = container.width.to_z3_expr(w) - (container.padding_left + container.padding_right)
            child_w = child.total_width_expr(w)

            solver.add(child_w > (container_inner_w + precision))

            if solver.check() == z3.sat:
                model = solver.model()
                w_val = float(model[w].as_decimal(4).replace("?", ""))
                cont_w = container.width.eval_at(w_val) - (container.padding_left + container.padding_right)
                ch_w = child.width.eval_at(w_val) + child.margin_left + child.margin_right
                return SMTVerificationResult(
                    is_overflow_free=False,
                    status="SAT",
                    theorem="1D Individual Child Containment",
                    counterexample_w=round(w_val, 2),
                    expected_container_w=round(cont_w, 2),
                    actual_children_w=round(ch_w, 2),
                    overflow_margin_px=round(ch_w - cont_w, 2),
                    details={
                        "container_id": container.id,
                        "child_id": child.id,
                        "offending_viewport": round(w_val, 2)
                    }
                )

        return SMTVerificationResult(
            is_overflow_free=True,
            status="UNSAT",
            theorem="1D Individual Child Containment",
            details={
                "container_id": container.id,
                "mode": "individual_children_check",
                "proof": "Ningún hijo individual supera el ancho de contenedor."
            }
        )

    # ------------------------------------------------------------------------
    # 2. TEOREMA DE NO-SOLAPAMIENTO 2D (Separating Axis Theorem en R2)
    # ------------------------------------------------------------------------

    def verify_non_overlapping(
        self,
        node_a: LayoutNode2D,
        node_b: LayoutNode2D,
        precision: float = 0.1,
        use_forall: bool = False
    ) -> SMTVerificationResult:
        """
        Demuestra formalmente que dos nodos nunca colisionan ni se solapan en R2
        en ningún viewport w in [min_viewport, max_viewport].

        Teorema:
          forall w in [w_min, w_max]: (xa + wa <= xb) V (xb + wb <= xa) V (ya + ha <= yb) V (yb + hb <= ya)
        Refutación dual:
          exists w in [w_min, w_max]: Overlap(A, B, w)
        """
        solver = z3.Solver()
        w = z3.Real("w")

        xa, ya, wa, ha = node_a.box.to_z3_exprs(w)
        xb, yb, wb, hb = node_b.box.to_z3_exprs(w)

        # Condición de colisión (intersección positiva de cajas 2D)
        overlap_condition = z3.And(
            xa + wa > xb + precision,
            xb + wb > xa + precision,
            ya + ha > yb + precision,
            yb + hb > ya + precision
        )

        if use_forall:
            separated = z3.Or(
                xa + wa <= xb,
                xb + wb <= xa,
                ya + ha <= yb,
                yb + hb <= ya
            )
            theorem_expr = z3.ForAll([w], z3.Implies(z3.And(w >= self.min_viewport, w <= self.max_viewport), separated))
            solver.add(z3.Not(theorem_expr))
        else:
            solver.add(w >= self.min_viewport)
            solver.add(w <= self.max_viewport)
            solver.add(overlap_condition)

        check_status = solver.check()

        if check_status == z3.unsat:
            proof_str = (
                f"UNSAT: Probado formalmente que {node_a.id} y {node_b.id} mantienen separación estricta en R2 "
                f"para todo viewport en [{self.min_viewport}, {self.max_viewport}]."
            )
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="2D Non-Overlapping Theorem",
                proof_formula=f"Separated({node_a.id}, {node_b.id}, w)",
                details={
                    "node_a": node_a.id,
                    "node_b": node_b.id,
                    "proof": proof_str
                }
            )
        elif check_status == z3.sat:
            model = solver.model()
            # En refutación libre, w está en el modelo; en ForAll negado, evaluamos solver o bound
            if w in model:
                w_val = float(model[w].as_decimal(4).replace("?", ""))
            else:
                w_val = self.min_viewport

            xa_v, ya_v, wa_v, ha_v = node_a.box.eval_at(w_val)
            xb_v, yb_v, wb_v, hb_v = node_b.box.eval_at(w_val)

            overlap_w = max(0.0, min(xa_v + wa_v, xb_v + wb_v) - max(xa_v, xb_v))
            overlap_h = max(0.0, min(ya_v + ha_v, yb_v + hb_v) - max(ya_v, yb_v))
            overlap_area = round(overlap_w * overlap_h, 2)

            return SMTVerificationResult(
                is_overflow_free=False,
                status="SAT",
                theorem="2D Non-Overlapping Theorem",
                counterexample_w=round(w_val, 2),
                counterexample_details={
                    "node_a": {"id": node_a.id, "box": (round(xa_v, 1), round(ya_v, 1), round(wa_v, 1), round(ha_v, 1))},
                    "node_b": {"id": node_b.id, "box": (round(xb_v, 1), round(yb_v, 1), round(wb_v, 1), round(hb_v, 1))},
                    "overlap_width_px": round(overlap_w, 2),
                    "overlap_height_px": round(overlap_h, 2),
                    "overlap_area_px2": overlap_area
                },
                details={
                    "reason": f"Colisión 2D entre {node_a.id} y {node_b.id} en w={round(w_val, 2)}px (penetración {round(overlap_w, 1)}x{round(overlap_h, 1)}px)"
                }
            )
        else:
            return SMTVerificationResult(
                is_overflow_free=False,
                status="UNKNOWN",
                theorem="2D Non-Overlapping Theorem"
            )

    # ------------------------------------------------------------------------
    # 3. TEOREMA DE CONTENCIÓN DE VIEWPORT / PADRE 2D
    # ------------------------------------------------------------------------

    def verify_viewport_containment_2d(
        self,
        parent: LayoutNode2D,
        child: LayoutNode2D,
        padding: Optional[Tuple[float, float, float, float]] = None,
        precision: float = 0.1
    ) -> SMTVerificationResult:
        """
        Demuestra formalmente que el bounding box del elemento hijo está estrictamente
        contenido dentro de los límites interiores del contenedor padre (o viewport root).

        Condición de contención perimétrica:
          inner_x_min <= xc AND xc + wc <= inner_x_max AND
          inner_y_min <= yc AND yc + hc <= inner_y_max
        """
        solver = z3.Solver()
        w = z3.Real("w")
        solver.add(w >= self.min_viewport, w <= self.max_viewport)

        xp, yp, wp, hp = parent.box.to_z3_exprs(w)
        xc, yc, wc, hc = child.box.to_z3_exprs(w)

        pad = padding or parent.padding
        top_p, right_p, bottom_p, left_p = pad

        inner_xp_min = xp + left_p
        inner_xp_max = xp + wp - right_p
        inner_yp_min = yp + top_p
        inner_yp_max = yp + hp - bottom_p

        # Condición de fuga perimétrica
        containment_violation = z3.Or(
            xc < inner_xp_min - precision,
            xc + wc > inner_xp_max + precision,
            yc < inner_yp_min - precision,
            yc + hc > inner_yp_max + precision
        )

        solver.add(containment_violation)
        check_status = solver.check()

        if check_status == z3.unsat:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="2D Viewport/Parent Containment Theorem",
                proof_formula=f"Contained({child.id}, {parent.id}, w)",
                details={
                    "parent_id": parent.id,
                    "child_id": child.id,
                    "proof": f"UNSAT: {child.id} garantizado 100% contenido en {parent.id} en todo el dominio continuo."
                }
            )
        elif check_status == z3.sat:
            model = solver.model()
            w_val = float(model[w].as_decimal(4).replace("?", ""))
            xp_v, yp_v, wp_v, hp_v = parent.box.eval_at(w_val)
            xc_v, yc_v, wc_v, hc_v = child.box.eval_at(w_val)

            overflow_x = max(0.0, (xc_v + wc_v) - (xp_v + wp_v - right_p), (xp_v + left_p) - xc_v)
            overflow_y = max(0.0, (yc_v + hc_v) - (yp_v + hp_v - bottom_p), (yp_v + top_p) - yc_v)

            return SMTVerificationResult(
                is_overflow_free=False,
                status="SAT",
                theorem="2D Viewport/Parent Containment Theorem",
                counterexample_w=round(w_val, 2),
                counterexample_details={
                    "parent_id": parent.id,
                    "child_id": child.id,
                    "parent_bounds": (xp_v, yp_v, wp_v, hp_v),
                    "child_bounds": (xc_v, yc_v, wc_v, hc_v),
                    "overflow_x_px": round(overflow_x, 2),
                    "overflow_y_px": round(overflow_y, 2),
                },
                details={
                    "reason": f"Fuga 2D: {child.id} desborda perimetro de {parent.id} en w={round(w_val, 2)}px (dX={round(overflow_x, 1)}px, dY={round(overflow_y, 1)}px)"
                }
            )
        else:
            return SMTVerificationResult(
                is_overflow_free=False,
                status="UNKNOWN",
                theorem="2D Viewport/Parent Containment Theorem"
            )

    # ------------------------------------------------------------------------
    # 4. INVARIANTE DE ACCESIBILIDAD TÁCTIL (Target Size >= 48x48px)
    # ------------------------------------------------------------------------

    def verify_touch_accessibility(
        self,
        node: LayoutNode2D,
        min_dim: float = 48.0,
        min_area: float = 2304.0,
        use_nonlinear: bool = False
    ) -> SMTVerificationResult:
        """
        Demuestra formalmente que las dimensiones de todo elemento interactivo
        satisfacen la directriz de accesibilidad táctil (WCAG 2.5.5 AAA / Apple HIG / Android M3).
        Por defecto en QF_LRA: width >= 48.0px AND height >= 48.0px.
        Opcionalmente en QF_NRA: area >= 2304.0px2 con ancho y alto mínimos >= 24px.
        """
        if not node.is_interactive:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="Touch Accessibility Invariant",
                details={"reason": f"Nodo {node.id} no es interactivo"}
            )

        solver = z3.Solver()
        w = z3.Real("w")
        solver.add(w >= self.min_viewport, w <= self.max_viewport)

        _, _, w_node, h_node = node.box.to_z3_exprs(w)

        if use_nonlinear:
            # QF_NRA: Comprobación no lineal de superficie cuadrática
            violation = z3.Or(
                w_node * h_node < z3.RealVal(min_area),
                w_node < z3.RealVal(24.0),
                h_node < z3.RealVal(24.0)
            )
        else:
            # QF_LRA: Decisión lineal estricta sobre caja delimitadora
            violation = z3.Or(
                w_node < z3.RealVal(min_dim),
                h_node < z3.RealVal(min_dim)
            )

        solver.add(violation)
        check_status = solver.check()

        if check_status == z3.unsat:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="Touch Accessibility Invariant",
                proof_formula=f"TouchAccessible({node.id}, w)",
                details={
                    "node_id": node.id,
                    "target_spec": f">={min_dim}x{min_dim}px",
                    "proof": f"UNSAT: Verificado formalmente que {node.id} satisface el tamaño objetivo en todo viewport."
                }
            )
        elif check_status == z3.sat:
            model = solver.model()
            w_val = float(model[w].as_decimal(4).replace("?", ""))
            _, _, w_v, h_v = node.box.eval_at(w_val)
            area_v = round(w_v * h_v, 2)

            return SMTVerificationResult(
                is_overflow_free=False,
                status="SAT",
                theorem="Touch Accessibility Invariant",
                counterexample_w=round(w_val, 2),
                counterexample_details={
                    "node_id": node.id,
                    "viewport_w": round(w_val, 2),
                    "measured_width": round(w_v, 2),
                    "measured_height": round(h_v, 2),
                    "measured_area": area_v,
                    "required_dim": min_dim,
                    "required_area": min_area
                },
                details={
                    "reason": f"Elemento táctil no conforme en {node.id}: {round(w_v, 1)}x{round(h_v, 1)}px en w={round(w_val, 2)}px (requerido {min_dim}x{min_dim}px)"
                }
            )
        else:
            return SMTVerificationResult(
                is_overflow_free=False,
                status="UNKNOWN",
                theorem="Touch Accessibility Invariant"
            )

    # ------------------------------------------------------------------------
    # 5. INVARIANTE DE JERARQUÍA Z-INDEX Y OCLUSIÓN DE CAPAS
    # ------------------------------------------------------------------------

    def verify_z_index_hierarchy(
        self,
        lower_node: LayoutNode2D,
        higher_node: LayoutNode2D,
        must_prevent_occlusion: bool = True
    ) -> SMTVerificationResult:
        """
        Demuestra formalmente la consistencia de apilamiento en el eje Z.
        Garantiza que ningún canvas WebGL o elemento de fondo ocluya o capture
        eventos de navegación o componentes críticos superpuestos en R2.

        Condición de violación:
          Overlap(lower, higher, w) AND z_higher <= z_lower
        """
        solver = z3.Solver()
        w = z3.Real("w")
        solver.add(w >= self.min_viewport, w <= self.max_viewport)

        xa, ya, wa, ha = lower_node.box.to_z3_exprs(w)
        xb, yb, wb, hb = higher_node.box.to_z3_exprs(w)

        # Proyección 2D de solapamiento
        overlap = z3.And(
            xa + wa > xb,
            xb + wb > xa,
            ya + ha > yb,
            yb + hb > ya
        )

        z_lower = z3.IntVal(lower_node.z_index)
        z_higher = z3.IntVal(higher_node.z_index)

        # La violación ocurre si coexisten en el espacio pero la capa superior tiene z-index <= inferior
        occlusion_violation = z3.And(overlap, z_higher <= z_lower)

        solver.add(occlusion_violation)
        check_status = solver.check()

        if check_status == z3.unsat:
            return SMTVerificationResult(
                is_overflow_free=True,
                status="UNSAT",
                theorem="Z-Index Hierarchy & Occlusion Invariant",
                proof_formula=f"LayerSafe({lower_node.id}, {higher_node.id})",
                details={
                    "lower_node": lower_node.id,
                    "higher_node": higher_node.id,
                    "lower_z": lower_node.z_index,
                    "higher_z": higher_node.z_index,
                    "proof": "UNSAT: Imposible que lower_node ocluya a higher_node en ningún viewport."
                }
            )
        elif check_status == z3.sat:
            model = solver.model()
            w_val = float(model[w].as_decimal(4).replace("?", ""))
            return SMTVerificationResult(
                is_overflow_free=False,
                status="SAT",
                theorem="Z-Index Hierarchy & Occlusion Invariant",
                counterexample_w=round(w_val, 2),
                counterexample_details={
                    "lower_node": {"id": lower_node.id, "z_index": lower_node.z_index},
                    "higher_node": {"id": higher_node.id, "z_index": higher_node.z_index},
                },
                details={
                    "reason": f"Inversión de capa: {lower_node.id} (z={lower_node.z_index}) ocluye a {higher_node.id} (z={higher_node.z_index}) en w={round(w_val, 2)}px"
                }
            )
        else:
            return SMTVerificationResult(
                is_overflow_free=False,
                status="UNKNOWN",
                theorem="Z-Index Hierarchy & Occlusion Invariant"
            )

    # ------------------------------------------------------------------------
    # 6. VERIFICADOR INTEGRAL DEL MANIFOLD ESPACIAL
    # ------------------------------------------------------------------------

    def verify_spatial_manifold_2d(
        self,
        nodes: List[LayoutNode2D],
        root_container: Optional[LayoutNode2D] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta la suite integral de verificación geométrica multidimensional
        sobre un grafo de nodos espaciales.
        """
        results: List[SMTVerificationResult] = []
        is_safe = True

        # A. Contención de hijos respecto al contenedor root o padres
        if root_container:
            for node in nodes:
                c_res = self.verify_viewport_containment_2d(root_container, node)
                results.append(c_res)
                if not c_res.is_overflow_free:
                    is_safe = False

        # B. Accesibilidad táctil de nodos interactivos
        for node in nodes:
            if node.is_interactive:
                t_res = self.verify_touch_accessibility(node)
                results.append(t_res)
                if not t_res.is_overflow_free:
                    is_safe = False

        # C. Jerarquía Z-Index y No-Solapamiento entre pares críticos
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n_a, n_b = nodes[i], nodes[j]

                # Si ambos son contenido crítico o botones interactivos adyacentes: no deben solaparse
                if (n_a.is_critical_content and n_b.is_critical_content) or (n_a.is_interactive and n_b.is_interactive):
                    o_res = self.verify_non_overlapping(n_a, n_b)
                    results.append(o_res)
                    if not o_res.is_overflow_free:
                        is_safe = False

                # Si uno es WebGL canvas de fondo y el otro es interfaz interactiva: z-index check
                if n_a.layer_category == "webgl_canvas" and n_b.is_interactive:
                    z_res = self.verify_z_index_hierarchy(n_a, n_b)
                    results.append(z_res)
                    if not z_res.is_overflow_free:
                        is_safe = False
                elif n_b.layer_category == "webgl_canvas" and n_a.is_interactive:
                    z_res = self.verify_z_index_hierarchy(n_b, n_a)
                    results.append(z_res)
                    if not z_res.is_overflow_free:
                        is_safe = False

        return {
            "is_safe": is_safe,
            "checks_run": len(results),
            "passed_proofs": sum(1 for r in results if r.status == "UNSAT"),
            "counterexamples_found": sum(1 for r in results if r.status == "SAT"),
            "reports": results
        }

    # ------------------------------------------------------------------------
    # 7. GENERACIÓN FORMAL DE TEOREMAS z3.ForAll
    # ------------------------------------------------------------------------

    def emit_forall_theorems(
        self,
        node_a: LayoutNode2D,
        node_b: LayoutNode2D
    ) -> Dict[str, z3.ExprRef]:
        """
        Construye las fórmulas de primer orden formalmente cerradas con z3.ForAll()
        para exportación como artefactos matemáticos auditables.
        """
        w = z3.Real("w")
        xa, ya, wa, ha = node_a.box.to_z3_exprs(w)
        xb, yb, wb, hb = node_b.box.to_z3_exprs(w)

        in_bounds = z3.And(w >= self.min_viewport, w <= self.max_viewport)

        # 1. Separación
        separated = z3.Or(xa + wa <= xb, xb + wb <= xa, ya + ha <= yb, yb + hb <= ya)
        th_separation = z3.ForAll([w], z3.Implies(in_bounds, separated))

        # 2. Accesibilidad táctil
        th_touch_a = z3.ForAll([w], z3.Implies(in_bounds, z3.And(wa >= 48.0, ha >= 48.0)))
        th_touch_b = z3.ForAll([w], z3.Implies(in_bounds, z3.And(wb >= 48.0, hb >= 48.0)))

        # 3. Z-Index
        overlap = z3.And(xa + wa > xb, xb + wb > xa, ya + ha > yb, yb + hb > ya)
        th_zindex = z3.ForAll([w], z3.Implies(z3.And(in_bounds, overlap), z3.IntVal(node_b.z_index) > z3.IntVal(node_a.z_index)))

        return {
            "theorem_non_overlapping": th_separation,
            "theorem_touch_accessibility_a": th_touch_a,
            "theorem_touch_accessibility_b": th_touch_b,
            "theorem_z_index_hierarchy": th_zindex
        }

    # ------------------------------------------------------------------------
    # 8. TESTING DIFERENCIAL (Plan B numérico)
    # ------------------------------------------------------------------------

    def differential_sampling_test(
        self,
        container: LayoutContainer,
        step_px: float = 16.0
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Plan B / Testing Diferencial: Muestrea físicamente de min_viewport a max_viewport.
        Verifica la concordancia entre la lógica matemática y el modelo SMT.
        """
        violations = []
        current_w = self.min_viewport

        while current_w <= self.max_viewport:
            cont_w = container.width.eval_at(current_w) - (container.padding_left + container.padding_right)
            if container.direction == "row" and not container.wrap:
                gaps = max(0, len(container.children) - 1) * container.gap
                total_children = gaps + sum(
                    c.width.eval_at(current_w) + c.margin_left + c.margin_right
                    for c in container.children
                )
                if total_children > cont_w + 0.5:
                    violations.append({
                        "viewport_w": round(current_w, 2),
                        "container_w": round(cont_w, 2),
                        "children_w": round(total_children, 2),
                        "overflow_px": round(total_children - cont_w, 2)
                    })
            else:
                for c in container.children:
                    cw = c.width.eval_at(current_w) + c.margin_left + c.margin_right
                    if cw > cont_w + 0.5:
                        violations.append({
                            "viewport_w": round(current_w, 2),
                            "child_id": c.id,
                            "container_w": round(cont_w, 2),
                            "child_w": round(cw, 2),
                            "overflow_px": round(cw - cont_w, 2)
                        })
            current_w += step_px

        return (len(violations) == 0, violations)
