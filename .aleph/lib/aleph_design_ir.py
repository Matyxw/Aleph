"""
.aleph/lib/aleph_design_ir.py
Estructura y Esquema Formal del Design IR v2.0 (Aleph Sovereign Design Engine).

Provee modelado de tipos, validación sintáctica y semántica rigurosa, serialización
bidireccional JSON <-> Design IR, mutación AST segura, soporte de los 12 paradigmas
estéticos soberanos, 8 arquetipos espaciales asimétricos, orden de tareas
Orient-Work-Confirm, métricas de supresión de CLS, física de resortes y matriz de
7 estados interactivos obligatorios.
"""

from __future__ import annotations

import copy
import enum
import json
import math
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Set, Tuple, Union

# --- Pydantic Dual v1/v2 Compatibility Shim ---
from pydantic import BaseModel, Field
try:
    from pydantic import ConfigDict, field_validator, model_validator
except ImportError:
    from pydantic import validator, root_validator
    def field_validator(*fields, **kwargs):
        return validator(*fields, allow_reuse=True)
    def model_validator(mode="after"):
        def decorator(fn):
            import inspect
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            if params and params[0] == "self":
                def adapted(cls, values):
                    return values
                adapted.__name__ = fn.__name__
                return root_validator(pre=False, allow_reuse=True)(adapted)
            return root_validator(pre=(mode == "before"), allow_reuse=True)(fn)
        return decorator
    ConfigDict = lambda **kw: dict(**kw)
# ----------------------------------------------


# ============================================================================
# EXCEPCIONES DEL SISTEMA DESIGN IR
# ============================================================================

class DesignIRError(Exception):
    """Error base de la infraestructura Design IR."""
    pass


class DesignIRValidationError(DesignIRError):
    """Lanzada cuando un Design IR viola invariantes sintácticos o semánticos."""
    pass


class ComponentNotFoundError(DesignIRError):
    """Lanzada cuando se busca o parchea un ID de componente inexistente."""
    pass


class InvalidMutationPathError(DesignIRError):
    """Lanzada cuando una ruta de token para mutate_token() es inválida o inalcanzable."""
    pass


# ============================================================================
# ENUMERACIONES FORMALES
# ============================================================================

class AestheticParadigm(str, enum.Enum):
    """Los 12 Paradigmas Estéticos Soberanos."""
    SWISS_INTERNATIONAL = "swiss_international"
    LITERARY_EDITORIAL = "literary_editorial"
    EDITORIAL_ELEGANCE = "literary_editorial"  # Alias canónico V7.0
    INDUSTRIAL_BRUTALIST = "industrial_brutalist"
    HAUTE_LUXURY = "haute_luxury"
    CINEMATIC_WEBGL = "cinematic_webgl"
    BENTO_HYPERGRID = "bento_hypergrid"
    NEO_BRUTALIST = "neo_brutalist"
    ORGANIC_TACTILE = "organic_tactile"
    CYBER_TELEMETRY = "cyber_telemetry"
    RETRO_FUTURIST = "retro_futurist"
    RETRO_FUTURISM = "retro_futurist"  # Alias canónico V7.0
    DOCUMENT_MINIMALIST = "document_minimalist"
    DECONSTRUCTIVIST = "deconstructivist"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_clean = value.strip().lower().replace("-", "_")
            if val_clean in ("editorial_elegance", "literary_editorial", "editorial"):
                return cls.LITERARY_EDITORIAL
            if val_clean in ("retro_futurism", "retro_futurist"):
                return cls.RETRO_FUTURIST
            for member in cls:
                if member.value == val_clean or member.name.lower() == val_clean:
                    return member
        return super()._missing_(value)


class SpatialArchetype(str, enum.Enum):
    """Los 8 Arquetipos Espaciales Asimétricos."""
    HERO_MONOLITH = "hero_monolith"
    EDITORIAL_STAGGERED = "editorial_staggered"
    ASYMMETRIC_SPLIT_70_30 = "asymmetric_split_70_30"
    BENTO_HIERARCHICAL = "bento_hierarchical"
    MASONRY_DENSE = "masonry_dense"
    GOLDEN_SPIRAL_FLOW = "golden_spiral_flow"
    TELEMETRY_DASHBOARD = "telemetry_dashboard"
    DECONSTRUCTED_OVERLAP = "deconstructed_overlap"


class TaskPhase(str, enum.Enum):
    """Fases de tarea psicológica y perceptual (Orient-Work-Confirm)."""
    ORIENT = "ORIENT"
    WORK = "WORK"
    CONFIRM = "CONFIRM"


class InteractionRole(str, enum.Enum):
    """
    Taxonomía estricta de roles interactivos (anti-conflación button/link).
    Garantiza jerarquía visual sin ambigüedades, accesibilidad de teclado y contraste auditado.
    """
    NAV_LINK = "nav_link"
    ACTION_PRIMARY = "action_primary"
    ACTION_SECONDARY = "action_secondary"
    ACTION_GHOST = "action_ghost"
    BADGE_CHIP = "badge_chip"
    ICON_TRIGGER = "icon_trigger"
    TAB_SELECTOR = "tab_selector"
    METRIC_COUNTER = "metric_counter"


class HapticPhysicalState(str, enum.Enum):
    """
    Matriz Háptica de 7 Estados Físicos Soberanos:
    idle, hover, active, focus-visible, disabled, loading, success.
    Dicta la física de resortes y respuesta táctil según energía cinética.
    """
    IDLE = "idle"
    HOVER = "hover"
    ACTIVE = "active"
    FOCUS_VISIBLE = "focus-visible"
    DISABLED = "disabled"
    LOADING = "loading"
    SUCCESS = "success"


class StateName(str, enum.Enum):
    """Los 7 estados obligatorios para todo componente interactivo soberano."""
    DEFAULT = "default"
    HOVER = "hover"
    ACTIVE = "active"
    FOCUS = "focus"
    DISABLED = "disabled"
    LOADING = "loading"
    ERROR = "error"


class HydrationTrigger(str, enum.Enum):
    """Estrategia de hidratación para Code Islands."""
    LOAD = "load"
    IDLE = "idle"
    VISIBLE = "visible"
    MEDIA = "media"
    NONE = "none"


class ColorGamut(str, enum.Enum):
    """Espacio cromático soportado."""
    SRGB = "srgb"
    DISPLAY_P3 = "display-p3"
    REC2020 = "rec2020"


class SurfaceTreatment(str, enum.Enum):
    """Tratamiento físico/perceptual de superficies."""
    FLAT = "flat"
    GLASSMORPHIC = "glassmorphic"
    TACTILE_EMBOSS = "tactile_emboss"
    RAW_OUTLINE = "raw_outline"
    SCANLINE = "scanline"


# ============================================================================
# PERCEPTUAL TOKENS
# ============================================================================

class ColorToken(BaseModel):
    """Token de color formal con OKLCH, gama amplia y contraste."""
    class Config:
        extra = "forbid"
        frozen = True

    name: str
    oklch: Tuple[float, float, float] = Field(
        ..., description="Coordenadas OKLCH: L in [0, 1], C in [0, 0.4], H in [0, 360]"
    )
    hex_value: str = Field(..., pattern=r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
    gamut: ColorGamut = ColorGamut.SRGB
    alpha: float = Field(default=1.0, ge=0.0, le=1.0)
    role: str = Field(..., description="Rol semántico: surface, primary, on_surface, accent, border, etc.")
    wcag_contrast_on_surface: Optional[float] = Field(default=None, ge=1.0, le=21.0)
    apca_lc: Optional[float] = Field(default=None, ge=-108.0, le=108.0)

    @field_validator("oklch")
    @classmethod
    def validate_oklch(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        l, c, h = v
        if not (0.0 <= l <= 1.0):
            raise ValueError(f"Luminosidad OKLCH L={l} debe estar en [0, 1]")
        if not (0.0 <= c <= 0.45):
            raise ValueError(f"Croma OKLCH C={c} debe estar en [0, 0.45]")
        if not (0.0 <= h <= 360.0):
            raise ValueError(f"Matiz OKLCH H={h} debe estar en [0, 360]")
        return v


class ShadowToken(BaseModel):
    """Token de sombra y oclusión ambiental tridimensional."""
    class Config:
        extra = "forbid"
        frozen = True

    name: str
    elevation_level: int = Field(..., ge=0, le=5)
    x: float
    y: float
    blur: float = Field(..., ge=0.0)
    spread: float
    color: str
    ambient_occlusion: float = Field(default=0.0, ge=0.0, le=1.0)

    def to_css_box_shadow(self) -> str:
        """Genera la declaración CSS box-shadow compuesta."""
        base = f"{self.x}px {self.y}px {self.blur}px {self.spread}px {self.color}"
        if self.ambient_occlusion > 0.0:
            ao_blur = max(1.0, self.blur * 0.4)
            ao_alpha = min(1.0, self.ambient_occlusion * 0.25)
            base += f", 0px 1px {ao_blur}px 0px oklch(0 0 0 / {ao_alpha:.3f})"
        return base


class SurfaceToken(BaseModel):
    """Tratamiento superficial perceptual: blur, ruido, bordes."""
    class Config:
        extra = "forbid"
        frozen = True

    name: str
    backdrop_blur_px: float = Field(default=0.0, ge=0.0)
    noise_grain_opacity: float = Field(default=0.0, ge=0.0, le=1.0)
    border_radius_scale: Dict[str, float] = Field(
        default_factory=lambda: {"none": 0.0, "sm": 4.0, "md": 8.0, "lg": 16.0, "full": 9999.0}
    )
    border_width_px: float = Field(default=1.0, ge=0.0)
    surface_treatment: SurfaceTreatment = SurfaceTreatment.FLAT


class PerceptualTokens(BaseModel):
    """Contenedor de todos los tokens sensoriales y perceptuales."""
    class Config:
        extra = "forbid"
        frozen = True

    colors: Dict[str, ColorToken] = Field(default_factory=dict)
    shadows: Dict[str, ShadowToken] = Field(default_factory=dict)
    surfaces: Dict[str, SurfaceToken] = Field(default_factory=dict)


# ============================================================================
# SPATIAL GRAMMAR
# ============================================================================

class SpatialBounds(BaseModel):
    """Límites de viewport y contención geométrica."""
    class Config:
        extra = "forbid"
        frozen = True

    min_viewport: float = Field(default=320.0, ge=240.0)
    max_viewport: float = Field(default=2560.0, le=7680.0)
    max_container_width: float = Field(default=1440.0, gt=320.0)
    columns: int = Field(default=12, ge=1, le=32)
    fluid_gutter_min: float = Field(default=16.0, ge=0.0)
    fluid_gutter_max: float = Field(default=32.0, ge=0.0)
    safe_area_insets: Dict[str, float] = Field(
        default_factory=lambda: {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
    )
    baseline_grid_px: float = Field(default=8.0, gt=0.0)

    @model_validator(mode="after")
    def validate_bounds_coherence(self) -> SpatialBounds:
        if self.min_viewport >= self.max_viewport:
            raise ValueError(f"min_viewport ({self.min_viewport}) debe ser menor que max_viewport ({self.max_viewport})")
        if self.fluid_gutter_min > self.fluid_gutter_max:
            raise ValueError("fluid_gutter_min no puede ser mayor que fluid_gutter_max")
        return self


class SpatialGrammar(BaseModel):
    """Gramática espacial, arquetipos asimétricos y orden de tareas."""
    class Config:
        extra = "forbid"
        frozen = True

    archetype: SpatialArchetype
    bounds: SpatialBounds = Field(default_factory=SpatialBounds)
    task_order: List[TaskPhase] = Field(
        default_factory=lambda: [TaskPhase.ORIENT, TaskPhase.WORK, TaskPhase.CONFIRM]
    )
    asymmetric_ratio: float = Field(default=1.618, gt=0.0)
    rhythm_gap_scale: Dict[str, float] = Field(
        default_factory=lambda: {"xs": 4.0, "sm": 8.0, "md": 16.0, "lg": 24.0, "xl": 32.0, "2xl": 48.0, "3xl": 64.0}
    )

    @field_validator("task_order")
    @classmethod
    def validate_task_order(cls, v: List[TaskPhase]) -> List[TaskPhase]:
        """Asegura el orden estricto de orientación, ejecución y confirmación."""
        expected = [TaskPhase.ORIENT, TaskPhase.WORK, TaskPhase.CONFIRM]
        if v != expected:
            raise ValueError(f"task_order debe ser exactamente {expected}, recibido: {v}")
        return v


# ============================================================================
# TYPOGRAPHY SYSTEM Y SUPRESIÓN DE CLS
# ============================================================================

class CLSMoverrideMetrics(BaseModel):
    """
    Métricas de compensación geométrica para WebFont Fallback.
    Anulan el Cumulative Layout Shift (CLS) antes de que la fuente variable descargue.
    """
    class Config:
        extra = "forbid"
        frozen = True

    size_adjust: float = Field(default=100.0, gt=0.0, description="CSS size-adjust en porcentaje")
    ascent_override: float = Field(default=90.0, ge=0.0, description="CSS ascent-override en porcentaje")
    descent_override: float = Field(default=20.0, ge=0.0, description="CSS descent-override en porcentaje")
    line_gap_override: float = Field(default=0.0, ge=0.0, description="CSS line-gap-override en porcentaje")

    def to_css_font_face_overrides(self) -> str:
        return (
            f"size-adjust: {self.size_adjust:.2f}%;\n"
            f"ascent-override: {self.ascent_override:.2f}%;\n"
            f"descent-override: {self.descent_override:.2f}%;\n"
            f"line-gap-override: {self.line_gap_override:.2f}%;"
        )


class VariableAxes(BaseModel):
    """Ejes de variación tipográfica OpenType / WOFF2."""
    class Config:
        extra = "forbid"
        frozen = True

    wght: float = Field(default=400.0, ge=100.0, le=1000.0)
    wdth: Optional[float] = Field(default=100.0, ge=25.0, le=200.0)
    opsz: Optional[float] = Field(default=None, ge=6.0, le=144.0)
    slnt: Optional[float] = Field(default=0.0, ge=-90.0, le=90.0)
    ital: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)


class TypeScaleLevel(BaseModel):
    """Nivel de escala tipográfica con fluid clamp y límites de línea."""
    class Config:
        extra = "forbid"
        frozen = True

    name: str
    font_size_clamp: str = Field(..., description="Expresión CSS clamp()")
    line_height_ratio: float = Field(..., gt=0.5, le=3.0)
    letter_spacing_em: float = Field(default=0.0, ge=-0.2, le=1.0)
    is_headline: bool = False
    max_lines: Optional[int] = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_headline_golden_rule(self) -> TypeScaleLevel:
        if self.is_headline:
            if self.max_lines is None:
                raise ValueError(
                    f"Nivel tipográfico titular '{self.name}' debe definir max_lines <= 3."
                )
            if self.max_lines > 3:
                raise ValueError(
                    f"Regla de oro de titulares violada en '{self.name}': "
                    f"max_lines={self.max_lines} excede el máximo absoluto permitido de 3."
                )
        return self


class TypographySystem(BaseModel):
    """Sistema tipográfico soberano con supresión de CLS."""
    class Config:
        extra = "forbid"
        frozen = True

    primary_family: str
    secondary_family: Optional[str] = None
    mono_family: str
    cls_overrides: Dict[str, CLSMoverrideMetrics] = Field(default_factory=dict)
    scales: Dict[str, TypeScaleLevel] = Field(default_factory=dict)
    default_variable_axes: VariableAxes = Field(default_factory=VariableAxes)


# ============================================================================
# PHYSICS MOTION Y REDUCED-MOTION SAFETY
# ============================================================================

class SpringPhysics(BaseModel):
    """Modelo físico de resorte armónico amortiguado (m*x'' + c*x' + k*x = 0)."""
    class Config:
        extra = "forbid"
        frozen = True

    mass: float = Field(default=1.0, gt=0.0)
    stiffness: float = Field(default=100.0, gt=0.0)
    damping: float = Field(default=15.0, gt=0.0)
    initial_velocity: float = Field(default=0.0)

    @property
    def damping_ratio(self) -> float:
        """Coeficiente de amortiguamiento zeta."""
        return self.damping / (2.0 * math.sqrt(self.mass * self.stiffness))

    @property
    def natural_frequency(self) -> float:
        """Frecuencia natural no amortiguada omega_0 en rad/s."""
        return math.sqrt(self.stiffness / self.mass)

    def is_underdamped(self) -> bool:
        return self.damping_ratio < 1.0

    def settling_time(self, threshold: float = 0.01) -> float:
        """Tiempo aproximado para entrar en banda del 1% del valor final (segundos)."""
        zeta = self.damping_ratio
        w0 = self.natural_frequency
        if zeta >= 1.0:
            return 4.0 / w0
        return -math.log(threshold * math.sqrt(1 - zeta**2)) / (zeta * w0)

    def to_css_linear(self, sample_count: int = 16) -> str:
        """
        Simula la ODE analítica y genera una función CSS linear() nativa de alto rendimiento.
        """
        zeta = self.damping_ratio
        w0 = self.natural_frequency
        points = []

        total_t = min(1.5, max(0.3, self.settling_time()))
        for i in range(sample_count + 1):
            t = (i / sample_count) * total_t
            if zeta < 1.0:
                wd = w0 * math.sqrt(1.0 - zeta**2)
                envelope = math.exp(-zeta * w0 * t)
                val = 1.0 - envelope * (math.cos(wd * t) + (zeta / math.sqrt(1.0 - zeta**2)) * math.sin(wd * t))
            else:
                val = 1.0 - math.exp(-w0 * t) * (1.0 + w0 * t)
            points.append(f"{round(val, 4)}")
        return f"linear({', '.join(points)})"


# ============================================================================
# PRESETS FORMALES DE CINÉTICA HÁPTICA (FÍSICA ARMÓNICA AMORTIGUADA)
# ============================================================================
# 1. SNAPPY: Botones, switches, microinteracciones instantáneas (~110ms settling, zeta ~0.726)
SPRING_PRESET_SNAPPY = SpringPhysics(mass=1.0, stiffness=320.0, damping=26.0)
# 2. GENTLE: Tarjetas, elevación espacial, modales (~220ms settling, zeta ~0.820)
SPRING_PRESET_GENTLE = SpringPhysics(mass=1.0, stiffness=180.0, damping=22.0)
# 3. BOUNCY: Badges, chips, success feedback (~280ms settling, zeta ~0.484, overshoot 16%)
SPRING_PRESET_BOUNCY = SpringPhysics(mass=1.0, stiffness=240.0, damping=15.0)


class ReducedMotionFallback(BaseModel):
    """
    Fallo seguro obligatorio para usuarios con prefers-reduced-motion: reduce.
    Rechaza cualquier traslación o escala violenta.
    """
    class Config:
        extra = "forbid"
        frozen = True

    enabled: bool = Field(default=True)
    duration_ms: float = Field(default=0.0, ge=0.0, le=50.0)
    opacity_only: bool = Field(default=True)
    transform_disabled: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_safety(self) -> ReducedMotionFallback:
        if not self.enabled:
            raise ValueError("ReducedMotionFallback DEBE estar activado (enabled=True)")
        if not self.transform_disabled:
            raise ValueError("ReducedMotionFallback DEBE desactivar transforms (transform_disabled=True)")
        if self.duration_ms > 50.0:
            raise ValueError("ReducedMotionFallback duration_ms no puede exceder 50ms para evitar mareo cinético")
        return self


class MotionToken(BaseModel):
    """Token de animación y cinemática con fallback obligatorio."""
    class Config:
        extra = "forbid"
        frozen = True

    name: str
    spring: Optional[SpringPhysics] = None
    linear_spline: Optional[str] = None
    duration_ms: float = Field(default=250.0, ge=0.0)
    reduced_motion_fallback: ReducedMotionFallback = Field(default_factory=ReducedMotionFallback)


class PhysicsMotionSystem(BaseModel):
    """Sistema de movimiento y cinemática física."""
    class Config:
        extra = "forbid"
        frozen = True

    tokens: Dict[str, MotionToken] = Field(default_factory=dict)
    default_spring: SpringPhysics = Field(default_factory=SpringPhysics)
    reduced_motion_global_policy: ReducedMotionFallback = Field(default_factory=ReducedMotionFallback)


# ============================================================================
# STATE MATRIX (7 ESTADOS OBLIGATORIOS)
# ============================================================================

class ComponentState(BaseModel):
    """Propiedades visuales de un estado interactivo individual."""
    class Config:
        extra = "forbid"
        frozen = True

    state_name: StateName
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    box_shadow: Optional[str] = None
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    transform: Optional[str] = None
    cursor: Optional[str] = None
    aria_attributes: Dict[str, str] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)


class StateMatrix(BaseModel):
    """
    Matriz de estados interactivos completa.
    DEBE contener rigurosamente los 7 estados: default, hover, active, focus, disabled, loading, error.
    """
    class Config:
        extra = "forbid"
        frozen = True

    states: Dict[StateName, ComponentState] = Field(default_factory=dict)

    @field_validator("states")
    @classmethod
    def validate_complete_matrix(cls, states: Dict[StateName, ComponentState]) -> Dict[StateName, ComponentState]:
        required_states = set(StateName)
        present_states = set(states.keys())
        missing = required_states - present_states
        if missing:
            missing_names = sorted([s.value for s in missing])
            raise ValueError(
                f"StateMatrix incompleta. Faltan estados obligatorios: {missing_names}. "
                f"Toda entidad interactiva requiere los 7 estados formales."
            )
        return states

    @classmethod
    def create_complete(
        cls,
        base_state: ComponentState,
        hover_patch: Optional[Dict[str, Any]] = None,
        active_patch: Optional[Dict[str, Any]] = None,
        focus_patch: Optional[Dict[str, Any]] = None,
        disabled_patch: Optional[Dict[str, Any]] = None,
        loading_patch: Optional[Dict[str, Any]] = None,
        error_patch: Optional[Dict[str, Any]] = None,
    ) -> StateMatrix:
        """Factory helper para instanciar una StateMatrix con los 7 estados formalizados."""
        all_states: Dict[StateName, ComponentState] = {}

        def _make_state(sn: StateName, patch: Optional[Dict[str, Any]] = None) -> ComponentState:
            data = base_state.model_dump()
            data["state_name"] = sn
            if patch:
                data.update(patch)
            return ComponentState(**data)

        all_states[StateName.DEFAULT] = _make_state(StateName.DEFAULT)
        all_states[StateName.HOVER] = _make_state(StateName.HOVER, hover_patch or {"opacity": 0.9})
        all_states[StateName.ACTIVE] = _make_state(StateName.ACTIVE, active_patch or {"transform": "scale(0.98)"})
        all_states[StateName.FOCUS] = _make_state(StateName.FOCUS, focus_patch or {"box_shadow": "0 0 0 2px #3B82F6"})
        all_states[StateName.DISABLED] = _make_state(StateName.DISABLED, disabled_patch or {"opacity": 0.4, "cursor": "not-allowed"})
        all_states[StateName.LOADING] = _make_state(StateName.LOADING, loading_patch or {"opacity": 0.7, "cursor": "wait"})
        all_states[StateName.ERROR] = _make_state(StateName.ERROR, error_patch or {"border_color": "#EF4444"})

        return cls(states=all_states)


# ============================================================================
# SOVEREIGN ASSETS Y CODE ISLANDS
# ============================================================================

class GLSLShader(BaseModel):
    """Definición formal de un Shader WebGL soberano."""
    class Config:
        extra = "forbid"
        frozen = True

    shader_id: str
    shader_type: Literal["fragment", "vertex", "compute"] = "fragment"
    glsl_source: str
    uniforms: Dict[str, str] = Field(default_factory=dict)
    precision: Literal["lowp", "mediump", "highp"] = "highp"
    fallback_canvas_color: str = "#000000"


class ProceduralSVG(BaseModel):
    """Gráfico vectorial algorítmico parametrizado."""
    class Config:
        extra = "forbid"
        frozen = True

    asset_id: str
    view_box: str = "0 0 100 100"
    path_templates: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    animated: bool = False


class NoiseTexture(BaseModel):
    """Textura generativa procedimental (grano, perlin, simplex)."""
    class Config:
        extra = "forbid"
        frozen = True

    texture_id: str
    noise_type: Literal["perlin", "simplex", "white", "blue", "cellular"] = "perlin"
    frequency: float = Field(default=0.05, gt=0.0)
    octaves: int = Field(default=4, ge=1, le=12)
    opacity: float = Field(default=0.05, ge=0.0, le=1.0)


class SovereignAssets(BaseModel):
    """Activos generativos y shaders sin dependencias de CDN externas."""
    class Config:
        extra = "forbid"
        frozen = True

    shaders: Dict[str, GLSLShader] = Field(default_factory=dict)
    svgs: Dict[str, ProceduralSVG] = Field(default_factory=dict)
    noises: Dict[str, NoiseTexture] = Field(default_factory=dict)


class CodeIsland(BaseModel):
    """Isla de hidratación parcial independiente."""
    class Config:
        extra = "forbid"
        frozen = True

    island_id: str
    component_name: str
    framework: Literal["react", "vanilla", "webgl", "solid", "svelte"] = "react"
    hydration_trigger: HydrationTrigger = HydrationTrigger.IDLE
    media_query: Optional[str] = None
    client_only: bool = False
    props: Dict[str, Any] = Field(default_factory=dict)
    bundle_budget_kb: float = Field(default=30.0, gt=0.0)


# ============================================================================
# COMPONENT TREE (AST DE DISEÑO)
# ============================================================================

CANONICAL_COMPONENT_TYPES: Set[str] = {
    "navbar", "hero_stage", "metric_ticker", "bento_grid", "bento_card",
    "telemetry_panel", "interactive_tabs", "comparison_table", "pricing_matrix",
    "editorial_block", "code_island", "cta_banner", "footer",
    "headline", "button", "card", "section", "text", "badge", "input",
    "widget", "island"
}

class IRComponent(BaseModel):
    """Nodo dentro del árbol de componentes de Design IR."""
    class Config:
        extra = "forbid"
        frozen = True

    id: str
    component_type: str = Field(..., description="Tipo semántico: headline, button, card, section, etc.")
    is_interactive: bool = False
    state_matrix: Optional[StateMatrix] = None
    task_phase: Optional[TaskPhase] = None
    type_scale: Optional[str] = None
    max_lines: Optional[int] = Field(default=None, ge=1)
    spatial_intent: Dict[str, Any] = Field(default_factory=dict)
    island: Optional[CodeIsland] = None
    children: List[IRComponent] = Field(default_factory=list)
    props: Dict[str, Any] = Field(default_factory=dict)
    interaction_role: Optional[InteractionRole] = None
    spotlight_tracking: bool = False

    @field_validator("task_phase", mode="before")
    @classmethod
    def _normalize_task_phase(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in TaskPhase.__members__:
                return TaskPhase[v_upper]
        return v

    @field_validator("interaction_role", mode="before")
    @classmethod
    def _normalize_interaction_role(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            for role in InteractionRole:
                if role.value == v_clean or role.name.lower() == v_clean:
                    return role
        return v


if hasattr(IRComponent, "model_rebuild"):
    IRComponent.model_rebuild()
else:
    IRComponent.update_forward_refs()


# ============================================================================
# REPORTES DE VALIDACIÓN
# ============================================================================

class ValidationReport(BaseModel):
    """Reporte formal de validación sintáctica y semántica."""
    class Config:
        extra = "forbid"
        frozen = True

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    inspected_components_count: int = 0
    inspected_tokens_count: int = 0


# ============================================================================
# VALIDADOR SINTÁCTICO Y SEMÁNTICO
# ============================================================================

class DesignIRValidator:
    """
    Motor de verificación de invariantes semánticos del Aleph Sovereign Design Engine:
    1. Regla de Oro de Titulares (max_lines <= 3 obligatorio).
    2. Completitud de la Matriz de 7 Estados en componentes interactivos.
    3. Fallo seguro inviolable para Reduced-Motion.
    4. Secuencia perceptual de fases de tarea Orient -> Work -> Confirm.
    5. Coherencia métrica de SpatialBounds y Tipografía CLS.
    """

    HEADLINE_TYPES = {"headline", "h1", "h2", "h3", "display", "hero_headline", "section_headline"}
    HEADLINE_SCALES = {"display", "h1", "h2", "h3"}

    @classmethod
    def validate(cls, ir: DesignIR, strict: bool = True) -> ValidationReport:
        errors: List[str] = []
        warnings: List[str] = []
        comp_count = 0

        # --- 1. Verificación de Motion y Reduced Motion Fallback ---
        if not ir.motion.reduced_motion_global_policy.enabled:
            errors.append("Global motion policy DEBE tener reduced_motion_fallback.enabled=True.")
        if not ir.motion.reduced_motion_global_policy.transform_disabled:
            errors.append("Global motion policy DEBE tener transform_disabled=True en reduced-motion.")

        for name, token in ir.motion.tokens.items():
            if token.reduced_motion_fallback is None:
                errors.append(f"Token de movimiento '{name}' carece de reduced_motion_fallback obligatorio.")
            else:
                if not token.reduced_motion_fallback.enabled:
                    errors.append(f"Token '{name}' reduced_motion_fallback debe estar enabled=True.")
                if not token.reduced_motion_fallback.transform_disabled:
                    errors.append(f"Token '{name}' reduced_motion_fallback debe tener transform_disabled=True.")
                if token.reduced_motion_fallback.duration_ms > 50.0:
                    errors.append(f"Token '{name}' reduced_motion_fallback duration_ms={token.reduced_motion_fallback.duration_ms} excede 50ms.")

        # --- 2. Verificación de Tipografía y CLS Overrides ---
        for scale_name, scale in ir.typography.scales.items():
            if scale.is_headline:
                if scale.max_lines is None:
                    errors.append(f"Escala tipográfica titular '{scale_name}' carece de max_lines <= 3.")
                elif scale.max_lines > 3:
                    errors.append(
                        f"Regla de oro de titulares violada en escala '{scale_name}': max_lines={scale.max_lines} > 3."
                    )

        # --- 3. Verificación recursiva de Componentes ---
        seen_ids: Set[str] = set()
        task_sequence: List[Tuple[str, TaskPhase]] = []

        def _traverse(node: IRComponent, parent_phase: Optional[TaskPhase] = None):
            nonlocal comp_count
            comp_count += 1

            # Unicidad de ID
            if node.id in seen_ids:
                errors.append(f"ID de componente duplicado en el árbol: '{node.id}'")
            seen_ids.add(node.id)

            # Regla de Oro de Titulares en Componentes
            is_hl = (
                node.component_type.lower() in cls.HEADLINE_TYPES
                or (node.type_scale and node.type_scale.lower() in cls.HEADLINE_SCALES)
                or node.props.get("is_headline", False) is True
            )
            if is_hl:
                if node.max_lines is None:
                    errors.append(
                        f"Regla de oro de titulares violada: Componente titular '{node.id}' "
                        f"(tipo: {node.component_type}) DEBE especificar max_lines <= 3."
                    )
                elif node.max_lines > 3:
                    errors.append(
                        f"Regla de oro de titulares violada: Componente titular '{node.id}' "
                        f"define max_lines={node.max_lines}, superando el límite inviolable de 3."
                    )

            # Completitud de Estado Interactivo
            if node.is_interactive:
                if node.state_matrix is None:
                    errors.append(
                        f"Componente interactivo '{node.id}' DEBE proveer un StateMatrix con los 7 estados obligatorios."
                    )
                else:
                    required_states = set(StateName)
                    present_states = set(node.state_matrix.states.keys())
                    missing = required_states - present_states
                    if missing:
                        missing_str = ", ".join(sorted([s.value for s in missing]))
                        errors.append(
                            f"Componente interactivo '{node.id}' tiene StateMatrix incompleta. Estados faltantes: [{missing_str}]."
                        )

            # Validación de Taxonomía Estricta de InteractionRole (Anti-Slop Semantics)
            if node.interaction_role is not None:
                if node.interaction_role == InteractionRole.ICON_TRIGGER:
                    # WCAG 1.1.1 / 2.5.5: Todo trigger puramente icónico debe tener etiqueta accesible
                    aria_lbl = node.props.get("aria_label") or node.props.get("aria-label")
                    if not aria_lbl:
                        errors.append(
                            f"Accesibilidad violada: Componente '{node.id}' con interaction_role=ICON_TRIGGER "
                            f"DEBE definir 'aria_label' en props para lectores de pantalla (WCAG 2.5.5 / 1.1.1)."
                        )
                elif node.interaction_role == InteractionRole.NAV_LINK:
                    # Anti-conflación: Un link de navegación nunca puede disfrazarse de botón primario
                    if node.props.get("variant") == "primary":
                        errors.append(
                            f"Anti-slop violado: Componente '{node.id}' con interaction_role=NAV_LINK "
                            f"no puede tener variant='primary' (conflación de link de navegación con botón primario)."
                        )
                elif node.interaction_role == InteractionRole.METRIC_COUNTER:
                    # Supresión de CLS dinámico: activar tabular-nums para evitar jitter
                    if not node.props.get("tabular_nums", False) and "value" in node.props:
                        node.props["tabular_nums"] = True

            # Registro de fase de tarea
            current_phase = node.task_phase or parent_phase
            if node.task_phase:
                task_sequence.append((node.id, node.task_phase))

            # Recurrir en hijos
            for ch in node.children:
                _traverse(ch, current_phase)

        for root in ir.root_components:
            _traverse(root)

        # --- 4. Verificación de Secuencia de Fases de Tarea ---
        phase_weights = {TaskPhase.ORIENT: 1, TaskPhase.WORK: 2, TaskPhase.CONFIRM: 3}
        current_max_weight = 1
        for comp_id, phase in task_sequence:
            w = phase_weights[phase]
            if w < current_max_weight:
                errors.append(
                    f"Violación de orden de tarea Orient-Work-Confirm: componente '{comp_id}' "
                    f"especifica fase {phase.value} tras haberse alcanzado una fase posterior."
                )
            else:
                current_max_weight = w

        tokens_count = (
            len(ir.perceptual_tokens.colors)
            + len(ir.perceptual_tokens.shadows)
            + len(ir.perceptual_tokens.surfaces)
        )

        is_valid = len(errors) == 0
        report = ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            inspected_components_count=comp_count,
            inspected_tokens_count=tokens_count
        )

        if strict and not is_valid:
            error_details = "\n  - " + "\n  - ".join(errors)
            raise DesignIRValidationError(
                f"Validación formal de Design IR fallida ({len(errors)} errores):\n{error_details}"
            )

        return report


# ============================================================================
# TOP-LEVEL DESIGN IR V2.0
# ============================================================================

class DesignIR(BaseModel):
    """
    Design Intermediate Representation (v2.0) Soberana.
    El contenedor canónico completo para la compilación visual de Aleph.
    """
    class Config:
        extra = "forbid"
        frozen = True

    ir_version: str = Field(default="2.0.0", description="Versión del esquema Design IR")
    title: str = Field(..., description="Nombre del artefacto o pantalla de diseño")
    paradigm: AestheticParadigm = Field(..., description="Paradigma estético de los 12 soberanos")
    perceptual_tokens: PerceptualTokens
    spatial_grammar: SpatialGrammar
    typography: TypographySystem
    motion: PhysicsMotionSystem
    assets: SovereignAssets = Field(default_factory=SovereignAssets)
    root_components: List[IRComponent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------------
    # VALIDACIÓN
    # ------------------------------------------------------------------------

    def validate_ir(self, strict: bool = True) -> ValidationReport:
        """Ejecuta la suite de verificación semántica completa sobre la instancia."""
        return DesignIRValidator.validate(self, strict=strict)

    # ------------------------------------------------------------------------
    # SERIALIZACIÓN / DESERIALIZACIÓN BIDIRECCIONAL
    # ------------------------------------------------------------------------

    def to_json(self, indent: int = 2) -> str:
        """Serializa el Design IR a JSON estricto."""
        return self.model_dump_json(indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a un diccionario de tipos nativos de Python."""
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str: str, validate: bool = True) -> DesignIR:
        """Deserializa y valida rigurosamente desde una cadena JSON."""
        instance = cls.model_validate_json(json_str)
        if validate:
            instance.validate_ir(strict=True)
        return instance

    @classmethod
    def from_dict(cls, data: Dict[str, Any], validate: bool = True) -> DesignIR:
        """Deserializa y valida desde un diccionario."""
        instance = cls.model_validate(data)
        if validate:
            instance.validate_ir(strict=True)
        return instance

    # ------------------------------------------------------------------------
    # BÚSQUEDA EN EL ÁRBOL AST
    # ------------------------------------------------------------------------

    def find_component(self, component_id: str) -> Optional[IRComponent]:
        """Busca recursivamente un componente por su identificador único."""
        def _search(nodes: Sequence[IRComponent]) -> Optional[IRComponent]:
            for node in nodes:
                if node.id == component_id:
                    return node
                found = _search(node.children)
                if found is not None:
                    return found
            return None
        return _search(self.root_components)

    def all_components(self) -> List[IRComponent]:
        """Devuelve un aplanamiento de todos los nodos de componentes en orden de recorrido."""
        result: List[IRComponent] = []
        def _collect(nodes: Sequence[IRComponent]):
            if not nodes or not isinstance(nodes, (list, tuple)):
                return
            for n in nodes:
                result.append(n)
                _collect(n.children)
        _collect(self.root_components)
        return result

    # ------------------------------------------------------------------------
    # INSPECCIÓN Y PARCHE SEMÁNTICO (AST-SAFE MUTATION)
    # ------------------------------------------------------------------------

    def mutate_token(self, token_path: str, new_value: Any) -> DesignIR:
        """
        Mutación semántica segura de un token por ruta de puntos.
        Ejemplos de ruta:
          'perceptual_tokens.colors.primary.hex_value'
          'spatial_grammar.bounds.max_container_width'
          'typography.cls_overrides.primary.ascent_override'
          'motion.tokens.card_hover.spring.damping'
        Clona profundamente el árbol para garantizar inmutabilidad previa y revalida.
        """
        clone = self.model_copy(deep=True)
        parts = token_path.strip().split(".")
        if not parts:
            raise InvalidMutationPathError("La ruta de token no puede estar vacía.")

        curr: Any = clone
        for i, part in enumerate(parts[:-1]):
            if isinstance(curr, dict):
                if part in curr:
                    curr = curr[part]
                else:
                    raise InvalidMutationPathError(
                        f"Ruta '{token_path}' no encontrada: clave '{part}' no existe en dict."
                    )
            elif hasattr(curr, part):
                curr = getattr(curr, part)
            else:
                raise InvalidMutationPathError(
                    f"Ruta '{token_path}' no encontrada: atributo '{part}' no existe en {type(curr).__name__}."
                )

        target_attr = parts[-1]
        if isinstance(curr, dict):
            if target_attr not in curr and not isinstance(new_value, (dict, BaseModel)):
                # Si es una clave existente o permitida
                pass
            curr[target_attr] = new_value
        elif hasattr(curr, target_attr):
            setattr(curr, target_attr, new_value)
        else:
            raise InvalidMutationPathError(
                f"Propiedad final '{target_attr}' no encontrada en {type(curr).__name__}."
            )

        # Re-validación del clon
        clone.validate_ir(strict=True)
        return clone

    def patch_layout_intent(self, component_id: str, patch_data: Dict[str, Any]) -> DesignIR:
        """
        Actualiza el intent espacial de un componente determinado sin corromper el AST.
        """
        clone = self.model_copy(deep=True)
        target = clone.find_component(component_id)
        if target is None:
            raise ComponentNotFoundError(f"Componente '{component_id}' no encontrado en el árbol Design IR.")

        target.spatial_intent.update(patch_data)
        clone.validate_ir(strict=True)
        return clone

    def update_component_state(
        self,
        component_id: str,
        state_name: Union[StateName, str],
        state_patch: Dict[str, Any]
    ) -> DesignIR:
        """
        Actualiza un estado interactivo individual dentro de la StateMatrix de un componente.
        """
        clone = self.model_copy(deep=True)
        target = clone.find_component(component_id)
        if target is None:
            raise ComponentNotFoundError(f"Componente '{component_id}' no encontrado en el árbol.")
        if not target.is_interactive or target.state_matrix is None:
            raise DesignIRValidationError(
                f"Componente '{component_id}' no es interactivo o carece de StateMatrix."
            )

        sn = StateName(state_name) if isinstance(state_name, str) else state_name
        if sn not in target.state_matrix.states:
            raise DesignIRValidationError(
                f"Estado '{sn.value}' no encontrado en la StateMatrix del componente '{component_id}'."
            )

        current_state = target.state_matrix.states[sn]
        dumped = current_state.model_dump()
        dumped.update(state_patch)
        dumped["state_name"] = sn
        target.state_matrix.states[sn] = ComponentState(**dumped)

        clone.validate_ir(strict=True)
        return clone


# ============================================================================
# FABRICADOR Y PERFILES DE LOS 12 PARADIGMAS ESTÉTICOS SOBERANOS
# ============================================================================

def _build_default_state_matrix(bg: str, fg: str, border: str) -> StateMatrix:
    """Helper interno para construir una StateMatrix completa de 7 estados."""
    base = ComponentState(
        state_name=StateName.DEFAULT,
        background_color=bg,
        text_color=fg,
        border_color=border,
        box_shadow="none",
        opacity=1.0
    )
    return StateMatrix.create_complete(
        base_state=base,
        hover_patch={"opacity": 0.88, "transform": "scale(1.01)"},
        active_patch={"opacity": 0.95, "transform": "scale(0.98)"},
        focus_patch={"box_shadow": f"0 0 0 2px {border}"},
        disabled_patch={"opacity": 0.35, "cursor": "not-allowed"},
        loading_patch={"opacity": 0.6, "cursor": "wait"},
        error_patch={"border_color": "var(--color-error, oklch(0.63 0.24 25))"}
    )


def _build_rich_6section_template(
    paradigm: AestheticParadigm,
    headline_id: str,
    headline_text: str,
    action_id: str,
    action_label: str,
    confirm_id: str,
    confirm_label: str,
    primary_color: str,
    surface_color: str,
    on_surface_color: str,
    border_color: str,
    brand_name: str,
    code_island: Optional[CodeIsland] = None,
    type_scale: str = "display",
    headline_max_lines: int = 2
) -> List[IRComponent]:
    """
    Construye una arquitectura de producción rica de 6+ secciones y 25+ componentes AST
    respetando rigurosamente el orden de fases Orient -> Work -> Confirm y las matrices
    de 7 estados interactivos obligatorios.
    """
    p_val = paradigm.value

    # Matrices de estados
    primary_fg = "var(--color-on-primary, oklch(0.99 0 0))" if on_surface_color != "var(--color-on-primary, oklch(0.99 0 0))" else surface_color
    primary_btn_matrix = _build_default_state_matrix(primary_color, primary_fg, primary_color)
    ghost_btn_matrix = _build_default_state_matrix(surface_color, on_surface_color, border_color)
    accent_btn_matrix = _build_default_state_matrix(primary_color, on_surface_color, border_color)

    # 1. NAVBAR [ORIENT]
    nav_brand = IRComponent(
        id=f"{p_val}_nav_brand",
        component_type="badge",
        task_phase=TaskPhase.ORIENT,
        props={"text": brand_name, "role": "brand", "variant": "subtle"}
    )
    nav_item_1 = IRComponent(
        id=f"{p_val}_nav_item_1",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=ghost_btn_matrix,
        props={"label": "Arquitectura", "href": "#architecture"}
    )
    nav_item_2 = IRComponent(
        id=f"{p_val}_nav_item_2",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=ghost_btn_matrix,
        props={"label": "Especificación SMT", "href": "#smt"}
    )
    nav_item_3 = IRComponent(
        id=f"{p_val}_nav_item_3",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=ghost_btn_matrix,
        props={"label": "Telemetría", "href": "#telemetry"}
    )
    nav_item_4 = IRComponent(
        id=f"{p_val}_nav_item_4",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=ghost_btn_matrix,
        props={"label": "Benchmarks", "href": "#benchmarks"}
    )
    nav_cta = IRComponent(
        id=f"{p_val}_nav_cta",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=primary_btn_matrix,
        props={"label": "Terminal Soberana", "variant": "primary"}
    )
    navbar = IRComponent(
        id=f"{p_val}_navbar",
        component_type="navbar",
        task_phase=TaskPhase.ORIENT,
        props={"brand": brand_name, "items": ["Arquitectura", "Especificación SMT", "Telemetría", "Benchmarks"]},
        children=[nav_brand, nav_item_1, nav_item_2, nav_item_3, nav_item_4, nav_cta]
    )

    # 2. HERO STAGE [ORIENT]
    hero_badge = IRComponent(
        id=f"{p_val}_hero_badge",
        component_type="badge",
        task_phase=TaskPhase.ORIENT,
        props={"text": "v7.0 Soberano", "variant": "outline"}
    )
    hero_headline = IRComponent(
        id=headline_id,
        component_type="headline",
        task_phase=TaskPhase.ORIENT,
        type_scale=type_scale,
        max_lines=headline_max_lines,
        spatial_intent={"grid_column": "span 12"},
        props={"text": headline_text, "is_headline": True}
    )
    hero_subtext = IRComponent(
        id=f"{p_val}_hero_subtext",
        component_type="text",
        task_phase=TaskPhase.ORIENT,
        props={"text": "Diseño determinista verificado con solvers SMT, colorimetría APCA y microfísica de resortes sin plantillas genéricas."}
    )
    hero_btn_sec = IRComponent(
        id=f"{p_val}_hero_btn_sec",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.ORIENT,
        state_matrix=ghost_btn_matrix,
        props={"label": "Auditoría de Invariantes", "variant": "ghost"}
    )
    hero_stage = IRComponent(
        id=f"{p_val}_hero_stage",
        component_type="hero_stage",
        task_phase=TaskPhase.ORIENT,
        props={"badge": "v7.0 Soberano"},
        children=[hero_badge, hero_headline, hero_subtext, hero_btn_sec]
    )

    # 3. METRIC TICKER [WORK]
    m1 = IRComponent(
        id=f"{p_val}_metric_lat",
        component_type="metric_ticker",
        task_phase=TaskPhase.WORK,
        props={"label": "Latencia p99", "value": "120 µs", "delta": "-42%", "tabular_nums": True}
    )
    m2 = IRComponent(
        id=f"{p_val}_metric_tps",
        component_type="metric_ticker",
        task_phase=TaskPhase.WORK,
        props={"label": "Throughput", "value": "1.42 M req/s", "delta": "+88%", "tabular_nums": True}
    )
    m3 = IRComponent(
        id=f"{p_val}_metric_smt",
        component_type="metric_ticker",
        task_phase=TaskPhase.WORK,
        props={"label": "Verificación SMT Z3", "value": "100% UNSAT", "delta": "0 overflow", "tabular_nums": True}
    )
    m4 = IRComponent(
        id=f"{p_val}_metric_mem",
        component_type="metric_ticker",
        task_phase=TaskPhase.WORK,
        props={"label": "Huella Memoria", "value": "4.2 MB", "delta": "Zero-leak", "tabular_nums": True}
    )
    ticker = IRComponent(
        id=f"{p_val}_ticker",
        component_type="metric_ticker",
        task_phase=TaskPhase.WORK,
        props={"metrics": ["Latencia p99", "Throughput", "Verificación SMT Z3", "Huella Memoria"]},
        children=[m1, m2, m3, m4]
    )

    # 4. BENTO GRID [WORK]
    bento_head = IRComponent(
        id=f"{p_val}_bento_head",
        component_type="headline",
        task_phase=TaskPhase.WORK,
        max_lines=2,
        spatial_intent={"grid_column": "span 12"},
        props={"text": "Capacidades de Alto Rendimiento", "is_headline": True}
    )
    card_action = IRComponent(
        id=action_id,
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.WORK,
        island=code_island,
        state_matrix=accent_btn_matrix,
        spatial_intent={"grid_column": "span 8"},
        props={"label": action_label, "grid_span": "col-span-8"}
    )
    card_springs = IRComponent(
        id=f"{p_val}_bento_c2",
        component_type="bento_card",
        task_phase=TaskPhase.WORK,
        spatial_intent={"grid_column": "span 4"},
        props={"title": "Física de Resortes", "description": "Microfísica lineal CSS sin overshoot perceptible.", "grid_span": "col-span-4"}
    )
    card_apca = IRComponent(
        id=f"{p_val}_bento_c3",
        component_type="bento_card",
        task_phase=TaskPhase.WORK,
        spatial_intent={"grid_column": "span 4"},
        props={"title": "Gama OKLCH", "description": "Contraste APCA calibrado por encima de 60 Lc en todo el espectro.", "grid_span": "col-span-4"}
    )
    card_dual = IRComponent(
        id=f"{p_val}_bento_c4",
        component_type="bento_card",
        task_phase=TaskPhase.WORK,
        spatial_intent={"grid_column": "span 8"},
        props={"title": "Compilación Dual", "description": "Generación simultánea de TSX modular React 19 y HTML5 autocontenido.", "grid_span": "col-span-8"}
    )
    bento_grid = IRComponent(
        id=f"{p_val}_bento",
        component_type="bento_grid",
        task_phase=TaskPhase.WORK,
        spatial_intent={"grid_columns": 12},
        children=[bento_head, card_action, card_springs, card_apca, card_dual]
    )

    # 5. TELEMETRY PANEL [WORK]
    telem_head = IRComponent(
        id=f"{p_val}_telem_head",
        component_type="headline",
        task_phase=TaskPhase.WORK,
        max_lines=2,
        props={"text": "Matriz de Telemetría en Tiempo Real"}
    )
    telem_r1 = IRComponent(
        id=f"{p_val}_telem_r1",
        component_type="card",
        task_phase=TaskPhase.WORK,
        props={"metric": "Blink Render Time", "value": "12.4ms", "status": "VERIFIED"}
    )
    telem_r2 = IRComponent(
        id=f"{p_val}_telem_r2",
        component_type="card",
        task_phase=TaskPhase.WORK,
        props={"metric": "Z3 SMT Invariant", "value": "UNSAT", "status": "OPTIMAL"}
    )
    telem_r3 = IRComponent(
        id=f"{p_val}_telem_r3",
        component_type="card",
        task_phase=TaskPhase.WORK,
        props={"metric": "Cumulative Layout Shift", "value": "0.000", "status": "IMMUTABLE"}
    )
    telem_act = IRComponent(
        id=f"{p_val}_telem_act",
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.WORK,
        state_matrix=ghost_btn_matrix,
        props={"label": "Actualizar Muestreo"}
    )
    telemetry = IRComponent(
        id=f"{p_val}_telemetry",
        component_type="telemetry_panel",
        task_phase=TaskPhase.WORK,
        children=[telem_head, telem_r1, telem_r2, telem_r3, telem_act]
    )

    # 6. CTA BANNER [CONFIRM]
    cta_title = IRComponent(
        id=f"{p_val}_cta_title",
        component_type="headline",
        task_phase=TaskPhase.CONFIRM,
        max_lines=2,
        props={"text": "Despliegue Determinista Soberano"}
    )
    cta_sub = IRComponent(
        id=f"{p_val}_cta_sub",
        component_type="text",
        task_phase=TaskPhase.CONFIRM,
        props={"text": "Sin dependencias de CDN, sin suscripciones a APIs externas y con verificación formal."}
    )
    confirm_btn = IRComponent(
        id=confirm_id,
        component_type="button",
        is_interactive=True,
        task_phase=TaskPhase.CONFIRM,
        state_matrix=primary_btn_matrix,
        props={"label": confirm_label}
    )
    cta_banner = IRComponent(
        id=f"{p_val}_cta_banner",
        component_type="cta_banner",
        task_phase=TaskPhase.CONFIRM,
        children=[cta_title, cta_sub, confirm_btn]
    )

    # 7. FOOTER [CONFIRM]
    foot_brand = IRComponent(
        id=f"{p_val}_foot_brand",
        component_type="badge",
        task_phase=TaskPhase.CONFIRM,
        props={"text": brand_name, "role": "brand"}
    )
    foot_col1 = IRComponent(
        id=f"{p_val}_foot_col1",
        component_type="card",
        task_phase=TaskPhase.CONFIRM,
        props={"title": "Arquitectura", "items": ["Design IR", "SMT Z3", "Compiladores"]}
    )
    foot_col2 = IRComponent(
        id=f"{p_val}_foot_col2",
        component_type="card",
        task_phase=TaskPhase.CONFIRM,
        props={"title": "Seguridad", "items": ["PQC Sealing", "Zero-Leak", "Sandbox"]}
    )
    foot_meta = IRComponent(
        id=f"{p_val}_foot_meta",
        component_type="text",
        task_phase=TaskPhase.CONFIRM,
        props={"text": "© 2026 Aleph-Omega Prime v7.0. Todos los derechos reservados."}
    )
    footer = IRComponent(
        id=f"{p_val}_footer",
        component_type="footer",
        task_phase=TaskPhase.CONFIRM,
        props={"brand": brand_name, "columns": ["Arquitectura", "Seguridad"]},
        children=[foot_brand, foot_col1, foot_col2, foot_meta]
    )

    return [navbar, hero_stage, ticker, bento_grid, telemetry, cta_banner, footer]

def create_paradigm_ir(
    paradigm: AestheticParadigm,
    title: Optional[str] = None,
    custom_ir_tree: Optional[Union[Dict[str, Any], List[Dict[str, Any]], DesignIR]] = None
) -> DesignIR:
    """
    Construye una instancia canónica, válida y lista para producción del Design IR
    para cualquiera de los 12 Paradigmas Estéticos Soberanos.
    """
    t = title or f"Aleph Sovereign - {paradigm.value.replace('_', ' ').title()}"

    # Base Spring & Motion tokens (con fallback seguro inviolable)
    safe_reduced_motion = ReducedMotionFallback(
        enabled=True,
        duration_ms=0.0,
        opacity_only=True,
        transform_disabled=True
    )

    base_spring = SpringPhysics(mass=1.0, stiffness=120.0, damping=16.0)
    motion_sys = PhysicsMotionSystem(
        default_spring=base_spring,
        reduced_motion_global_policy=safe_reduced_motion,
        tokens={
            "interactive_spring": MotionToken(
                name="interactive_spring",
                spring=base_spring,
                duration_ms=250.0,
                reduced_motion_fallback=safe_reduced_motion
            ),
            "page_fade": MotionToken(
                name="page_fade",
                linear_spline="linear(0, 0.4, 0.8, 1)",
                duration_ms=180.0,
                reduced_motion_fallback=safe_reduced_motion
            )
        }
    )

    # Base CLS overrides
    cls_metric = CLSMoverrideMetrics(
        size_adjust=100.2,
        ascent_override=92.5,
        descent_override=21.0,
        line_gap_override=0.0
    )

    # ========================================================================
    # 1. SWISS INTERNATIONAL
    # ========================================================================
    if paradigm == AestheticParadigm.SWISS_INTERNATIONAL:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.98, 0.002, 90.0), hex_value="#F9F9F9", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.15, 0.005, 90.0), hex_value="#111111", role="on_surface", wcag_contrast_on_surface=16.5),
                "primary": ColorToken(name="primary", oklch=(0.55, 0.22, 28.0), hex_value="#E60000", role="primary", wcag_contrast_on_surface=5.2),
                "border": ColorToken(name="border", oklch=(0.88, 0.005, 90.0), hex_value="#D6D6D6", role="border")
            },
            shadows={
                "flat": ShadowToken(name="flat", elevation_level=0, x=0, y=0, blur=0, spread=0, color="transparent")
            },
            surfaces={
                "base": SurfaceToken(name="base", border_width_px=1.0, border_radius_scale={"none": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0})
            }
        )
        spatial = SpatialGrammar(
            archetype=SpatialArchetype.ASYMMETRIC_SPLIT_70_30,
            bounds=SpatialBounds(min_viewport=320.0, max_viewport=2560.0, max_container_width=1400.0, columns=12)
        )
        typography = TypographySystem(
            primary_family="Helvetica Neue, Arial, sans-serif",
            mono_family="JetBrains Mono, monospace",
            cls_overrides={"primary": cls_metric},
            scales={
                "display": TypeScaleLevel(name="display", font_size_clamp="clamp(2.5rem, 5vw + 1rem, 4.5rem)", line_height_ratio=1.05, is_headline=True, max_lines=2),
                "body": TypeScaleLevel(name="body", font_size_clamp="clamp(1rem, 0.5vw + 0.9rem, 1.125rem)", line_height_ratio=1.45)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="swiss_hero",
            headline_text="Rigor Matemático y Precisión Tipográfica",
            action_id="swiss_action",
            action_label="Examinar Sistema",
            confirm_id="swiss_confirm",
            confirm_label="Confirmar Especificación",
            primary_color="#E60000",
            surface_color="#F9F9F9",
            on_surface_color="#111111",
            border_color="#D6D6D6",
            brand_name="Helvetia Precision",
            type_scale="display",
            headline_max_lines=2
        )

    # ========================================================================
    # 2. LITERARY EDITORIAL
    # ========================================================================
    elif paradigm == AestheticParadigm.LITERARY_EDITORIAL:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.96, 0.015, 80.0), hex_value="#F7F4EE", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.20, 0.01, 60.0), hex_value="#1F1B18", role="on_surface", wcag_contrast_on_surface=14.2),
                "primary": ColorToken(name="primary", oklch=(0.42, 0.12, 35.0), hex_value="#7F2B1D", role="primary", wcag_contrast_on_surface=7.8),
                "border": ColorToken(name="border", oklch=(0.88, 0.02, 75.0), hex_value="#E2DCD2", role="border")
            },
            surfaces={"parchment": SurfaceToken(name="parchment", border_width_px=0.5)}
        )
        spatial = SpatialGrammar(
            archetype=SpatialArchetype.EDITORIAL_STAGGERED,
            bounds=SpatialBounds(max_container_width=960.0)
        )
        typography = TypographySystem(
            primary_family="Newsreader, Charter, Georgia, serif",
            mono_family="Courier Prime, monospace",
            cls_overrides={"primary": cls_metric},
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(2.2rem, 3vw + 1rem, 3.5rem)", line_height_ratio=1.18, is_headline=True, max_lines=3),
                "body": TypeScaleLevel(name="body", font_size_clamp="clamp(1.1rem, 0.2vw + 1rem, 1.25rem)", line_height_ratio=1.65)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="lit_title",
            headline_text="El Manuscrito de la Soberanía Algorítmica",
            action_id="lit_footnote_toggle",
            action_label="Ver Comentarios Marginales",
            confirm_id="lit_accept",
            confirm_label="Archivar Lectura",
            primary_color="#7F2B1D",
            surface_color="#F7F4EE",
            on_surface_color="#1C1814",
            border_color="#E2DCD2",
            brand_name="The Sovereign Folio",
            type_scale="h1",
            headline_max_lines=3
        )

    # ========================================================================
    # 3. INDUSTRIAL BRUTALIST
    # ========================================================================
    elif paradigm == AestheticParadigm.INDUSTRIAL_BRUTALIST:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.22, 0.005, 260.0), hex_value="#1F2124", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.005, 260.0), hex_value="#E8EAED", role="on_surface", wcag_contrast_on_surface=13.0),
                "primary": ColorToken(name="primary", oklch=(0.75, 0.16, 75.0), hex_value="#F5A623", role="primary", wcag_contrast_on_surface=9.5),
                "border": ColorToken(name="border", oklch=(0.40, 0.005, 260.0), hex_value="#4A4E57", role="border")
            },
            surfaces={"steel": SurfaceToken(name="steel", border_width_px=2.0, surface_treatment=SurfaceTreatment.RAW_OUTLINE)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.TELEMETRY_DASHBOARD)
        typography = TypographySystem(
            primary_family="JetBrains Mono, monospace",
            mono_family="JetBrains Mono, monospace",
            cls_overrides={"primary": cls_metric},
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(1.8rem, 2vw + 1rem, 2.8rem)", line_height_ratio=1.1, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="ind_header",
            headline_text="SPEC-084: REACCIÓN TÉRMICA NUCLEAR",
            action_id="ind_engage",
            action_label="INICIAR CIRCUITO",
            confirm_id="ind_lock",
            confirm_label="BLOQUEO SEGURO",
            primary_color="#F5A623",
            surface_color="#1F2124",
            on_surface_color="#E8EAED",
            border_color="#4A4E57",
            brand_name="Heavy Heavy Industries",
            type_scale="h1",
            headline_max_lines=2
        )

    # ========================================================================
    # 4. HAUTE LUXURY
    # ========================================================================
    elif paradigm == AestheticParadigm.HAUTE_LUXURY:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.12, 0.008, 280.0), hex_value="#0B0B0D", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.95, 0.015, 85.0), hex_value="#FAF8F5", role="on_surface", wcag_contrast_on_surface=16.8),
                "primary": ColorToken(name="primary", oklch=(0.76, 0.11, 85.0), hex_value="#D4AF37", role="primary", wcag_contrast_on_surface=9.2),
                "border": ColorToken(name="border", oklch=(0.30, 0.02, 85.0), hex_value="#3A3424", role="border")
            },
            shadows={"soft": ShadowToken(name="soft", elevation_level=2, x=0, y=8, blur=24, spread=-4, color="oklch(0 0 0 / 0.6)", ambient_occlusion=0.4)},
            surfaces={"velvet": SurfaceToken(name="velvet", border_width_px=0.5)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.GOLDEN_SPIRAL_FLOW)
        typography = TypographySystem(
            primary_family="Playfair Display, Cormorant Garamond, serif",
            mono_family="Cinzel, serif",
            cls_overrides={"primary": cls_metric},
            scales={
                "display": TypeScaleLevel(name="display", font_size_clamp="clamp(2.5rem, 6vw, 5.5rem)", line_height_ratio=1.08, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="lux_hero",
            headline_text="L'Élégance Éternelle",
            action_id="lux_curate",
            action_label="Découvrir la Collection",
            confirm_id="lux_reserve",
            confirm_label="Confirmer la Réservation",
            primary_color="#D4AF37",
            surface_color="#0B0B0D",
            on_surface_color="#FAF8F5",
            border_color="#3A3424",
            brand_name="Atelier Céleste",
            type_scale="display",
            headline_max_lines=2
        )

    # ========================================================================
    # 5. CINEMATIC WEBGL
    # ========================================================================
    elif paradigm == AestheticParadigm.CINEMATIC_WEBGL:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.08, 0.015, 270.0), hex_value="#05050A", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.95, 0.02, 210.0), hex_value="#F0F8FF", role="on_surface", wcag_contrast_on_surface=18.0),
                "primary": ColorToken(name="primary", oklch=(0.78, 0.18, 205.0), hex_value="#00F0FF", role="primary", wcag_contrast_on_surface=11.2),
                "border": ColorToken(name="border", oklch=(0.28, 0.06, 260.0), hex_value="#1A1C30", role="border")
            },
            surfaces={"lens": SurfaceToken(name="lens", backdrop_blur_px=16.0, surface_treatment=SurfaceTreatment.GLASSMORPHIC)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.HERO_MONOLITH)
        typography = TypographySystem(
            primary_family="Syne, Space Grotesk, sans-serif",
            mono_family="Space Mono, monospace",
            scales={
                "display": TypeScaleLevel(name="display", font_size_clamp="clamp(3rem, 7vw, 6rem)", line_height_ratio=1.02, is_headline=True, max_lines=2)
            }
        )
        assets = SovereignAssets(
            shaders={
                "volumetric_nebula": GLSLShader(
                    shader_id="volumetric_nebula",
                    glsl_source="void main() { gl_FragColor = vec4(0.0, 0.94, 1.0, 1.0); }",
                    uniforms={"u_time": "float", "u_resolution": "vec2"},
                    fallback_canvas_color="#05050A"
                )
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="cine_title",
            headline_text="Singularidad Cinemática",
            action_id="cine_trigger",
            action_label="Iniciar Órbita",
            confirm_id="cine_lock",
            confirm_label="Fijar Coordenadas",
            primary_color="#00F0FF",
            surface_color="#05050A",
            on_surface_color="#F0F8FF",
            border_color="#00B4D8",
            brand_name="Nebula Core",
            code_island=CodeIsland(island_id="webgl_ctrl", component_name="CameraControl", framework="webgl", hydration_trigger=HydrationTrigger.VISIBLE),
            type_scale="display",
            headline_max_lines=2
        )

    # ========================================================================
    # 6. BENTO HYPERGRID
    # ========================================================================
    elif paradigm == AestheticParadigm.BENTO_HYPERGRID:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.14, 0.005, 260.0), hex_value="#121316", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.94, 0.005, 260.0), hex_value="#EEEEEE", role="on_surface", wcag_contrast_on_surface=14.5),
                "primary": ColorToken(name="primary", oklch=(0.62, 0.19, 255.0), hex_value="#3B82F6", role="primary", wcag_contrast_on_surface=6.1),
                "border": ColorToken(name="border", oklch=(0.25, 0.005, 260.0), hex_value="#26282E", role="border")
            },
            surfaces={"bento_card": SurfaceToken(name="bento_card", border_radius_scale={"card": 20.0}, border_width_px=1.0)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.BENTO_HIERARCHICAL)
        typography = TypographySystem(
            primary_family="Geist, Inter, sans-serif",
            mono_family="Geist Mono, monospace",
            scales={
                "h2": TypeScaleLevel(name="h2", font_size_clamp="clamp(1.8rem, 3vw, 2.6rem)", line_height_ratio=1.15, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="bento_header",
            headline_text="Módulos de Alta Densidad Informacional",
            action_id="bento_action_card",
            action_label="Métricas en Tiempo Real",
            confirm_id="bento_commit",
            confirm_label="Guardar Disposición",
            primary_color="#3B82F6",
            surface_color="#121316",
            on_surface_color="#EEEEEE",
            border_color="#26282E",
            brand_name="HyperGrid OS",
            type_scale="h2",
            headline_max_lines=2
        )

    # ========================================================================
    # 7. NEO BRUTALIST
    # ========================================================================
    elif paradigm == AestheticParadigm.NEO_BRUTALIST:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.99, 0.01, 90.0), hex_value="#FFFDF8", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="on_surface", wcag_contrast_on_surface=17.2),
                "primary": ColorToken(name="primary", oklch=(0.65, 0.26, 355.0), hex_value="#FF4081", role="primary", wcag_contrast_on_surface=5.8),
                "border": ColorToken(name="border", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="border")
            },
            shadows={"hard_pop": ShadowToken(name="hard_pop", elevation_level=3, x=5, y=5, blur=0, spread=0, color="oklch(0.05 0 0)")},
            surfaces={"blocky": SurfaceToken(name="blocky", border_width_px=3.0, border_radius_scale={"none": 0.0})}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.MASONRY_DENSE)
        typography = TypographySystem(
            primary_family="Space Grotesk, sans-serif",
            mono_family="Space Mono, monospace",
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(2.5rem, 5vw, 4.5rem)", line_height_ratio=1.05, is_headline=True, max_lines=3)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="neo_headline",
            headline_text="IMPACTO VISUAL SIN CONCESIONES",
            action_id="neo_clicker",
            action_label="PULSAR AQUÍ",
            confirm_id="neo_finish",
            confirm_label="ACEPTAR TODO",
            primary_color="var(--color-primary, oklch(0.65 0.26 355.0))",
            surface_color="var(--color-surface, oklch(0.99 0.01 90.0))",
            on_surface_color="var(--color-on-surface, oklch(0.05 0 0))",
            border_color="var(--color-border, oklch(0.05 0 0))",
            brand_name="Pop Heavy",
            type_scale="h1",
            headline_max_lines=3
        )

    # ========================================================================
    # 8. ORGANIC TACTILE
    # ========================================================================
    elif paradigm == AestheticParadigm.ORGANIC_TACTILE:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.94, 0.02, 85.0), hex_value="#F0ECE1", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.25, 0.02, 45.0), hex_value="#2D2B2A", role="on_surface", wcag_contrast_on_surface=11.8),
                "primary": ColorToken(name="primary", oklch=(0.58, 0.14, 40.0), hex_value="#C86446", role="primary", wcag_contrast_on_surface=4.9),
                "border": ColorToken(name="border", oklch=(0.85, 0.03, 85.0), hex_value="#DCD6C7", role="border")
            },
            surfaces={"clay": SurfaceToken(name="clay", border_radius_scale={"pebble": 28.0}, border_width_px=1.5, surface_treatment=SurfaceTreatment.TACTILE_EMBOSS)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.GOLDEN_SPIRAL_FLOW)
        typography = TypographySystem(
            primary_family="Fraunces, Plus Jakarta Sans, serif",
            mono_family="DM Mono, monospace",
            scales={
                "h2": TypeScaleLevel(name="h2", font_size_clamp="clamp(2rem, 4vw, 3.2rem)", line_height_ratio=1.2, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="org_heading",
            headline_text="Formas Orgánicas y Resonancia Natural",
            action_id="org_touch_target",
            action_label="Sentir Textura",
            confirm_id="org_settle",
            confirm_label="Arraigar",
            primary_color="#C86446",
            surface_color="#F0ECE1",
            on_surface_color="#2D2B2A",
            border_color="#DCD6C7",
            brand_name="Terra Studio",
            type_scale="h2",
            headline_max_lines=2
        )

    # ========================================================================
    # 9. CYBER TELEMETRY
    # ========================================================================
    elif paradigm == AestheticParadigm.CYBER_TELEMETRY:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.10, 0.02, 145.0), hex_value="#020A05", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.88, 0.24, 145.0), hex_value="#00FF66", role="on_surface", wcag_contrast_on_surface=13.5),
                "primary": ColorToken(name="primary", oklch=(0.78, 0.20, 80.0), hex_value="#FFB000", role="primary", wcag_contrast_on_surface=10.2),
                "border": ColorToken(name="border", oklch=(0.30, 0.10, 145.0), hex_value="#0B381A", role="border")
            },
            surfaces={"phosphor_crt": SurfaceToken(name="phosphor_crt", surface_treatment=SurfaceTreatment.SCANLINE, border_width_px=1.0)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.TELEMETRY_DASHBOARD)
        typography = TypographySystem(
            primary_family="Berkeley Mono, IBM Plex Mono, monospace",
            mono_family="Berkeley Mono, monospace",
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(1.6rem, 2vw, 2.4rem)", line_height_ratio=1.1, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="cyber_status",
            headline_text="[NODE-01] TELEMETRÍA CUÁNTICA ACTIVA",
            action_id="cyber_poll",
            action_label="EJECUTAR SONDEO",
            confirm_id="cyber_ack",
            confirm_label="CONFIRMAR TELEMETRÍA",
            primary_color="#FFB000",
            surface_color="#020A05",
            on_surface_color="#00FF66",
            border_color="#0B381A",
            brand_name="CyberSentinel Node",
            type_scale="h1",
            headline_max_lines=2
        )

    # ========================================================================
    # 10. RETRO FUTURIST
    # ========================================================================
    elif paradigm == AestheticParadigm.RETRO_FUTURIST:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.18, 0.10, 310.0), hex_value="#241442", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.05, 70.0), hex_value="#FFF0E6", role="on_surface", wcag_contrast_on_surface=12.5),
                "primary": ColorToken(name="primary", oklch=(0.68, 0.22, 40.0), hex_value="#FF5E36", role="primary", wcag_contrast_on_surface=6.8),
                "border": ColorToken(name="border", oklch=(0.40, 0.18, 330.0), hex_value="#661C66", role="border")
            },
            surfaces={"synth": SurfaceToken(name="synth", border_radius_scale={"panel": 12.0}, border_width_px=2.0)}
        )
        spatial = SpatialGrammar(archetype=SpatialArchetype.BENTO_HIERARCHICAL)
        typography = TypographySystem(
            primary_family="Orbitron, Righteous, sans-serif",
            mono_family="VT323, monospace",
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(2.4rem, 4vw, 4rem)", line_height_ratio=1.1, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="retro_title",
            headline_text="TRANSMISIÓN ORBITAL 1984",
            action_id="retro_warp",
            action_label="ACTIVAR PROPULSIÓN",
            confirm_id="retro_dock",
            confirm_label="ATRAQUE COMPLETO",
            primary_color="#FF5E36",
            surface_color="#241442",
            on_surface_color="#FFF0E6",
            border_color="#661C66",
            brand_name="Vector Synth",
            type_scale="h1",
            headline_max_lines=2
        )

    # ========================================================================
    # 11. DOCUMENT MINIMALIST
    # ========================================================================
    elif paradigm == AestheticParadigm.DOCUMENT_MINIMALIST:
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(1.0, 0.0, 0.0), hex_value="#FFFFFF", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.10, 0.0, 0.0), hex_value="#1A1A1A", role="on_surface", wcag_contrast_on_surface=18.5),
                "primary": ColorToken(name="primary", oklch=(0.50, 0.16, 255.0), hex_value="#0969DA", role="primary", wcag_contrast_on_surface=4.8),
                "border": ColorToken(name="border", oklch=(0.85, 0.0, 0.0), hex_value="#D0D7DE", role="border")
            },
            surfaces={"doc": SurfaceToken(name="doc", border_width_px=1.0)}
        )
        spatial = SpatialGrammar(
            archetype=SpatialArchetype.HERO_MONOLITH,
            bounds=SpatialBounds(max_container_width=740.0)
        )
        typography = TypographySystem(
            primary_family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            mono_family="ui-monospace, monospace",
            scales={
                "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(1.75rem, 2vw + 1rem, 2.25rem)", line_height_ratio=1.25, is_headline=True, max_lines=2)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="doc_header",
            headline_text="Especificación Técnica Design IR v2.0",
            action_id="doc_inspect",
            action_label="Revisar Diff",
            confirm_id="doc_approve",
            confirm_label="Aprobar Documento",
            primary_color="#0969DA",
            surface_color="#FFFFFF",
            on_surface_color="#1A1A1A",
            border_color="#D0D7DE",
            brand_name="Minimal Lexicon",
            type_scale="h1",
            headline_max_lines=2
        )

    # ========================================================================
    # 12. DECONSTRUCTIVIST
    # ========================================================================
    else:  # AestheticParadigm.DECONSTRUCTIVIST
        tokens = PerceptualTokens(
            colors={
                "surface": ColorToken(name="surface", oklch=(0.10, 0.005, 0.0), hex_value="#0A0A0A", role="surface"),
                "on_surface": ColorToken(name="on_surface", oklch=(0.98, 0.0, 0.0), hex_value="#FFFFFF", role="on_surface", wcag_contrast_on_surface=19.2),
                "primary": ColorToken(name="primary", oklch=(0.60, 0.30, 20.0), hex_value="#FF0055", role="primary", wcag_contrast_on_surface=5.7),
                "border": ColorToken(name="border", oklch=(0.40, 0.01, 0.0), hex_value="#333333", role="border")
            },
            surfaces={"fragment": SurfaceToken(name="fragment", border_width_px=2.0)}
        )
        spatial = SpatialGrammar(
            archetype=SpatialArchetype.DECONSTRUCTED_OVERLAP,
            asymmetric_ratio=2.414
        )
        typography = TypographySystem(
            primary_family="Syne, serif",
            mono_family="Space Mono, monospace",
            scales={
                "display": TypeScaleLevel(name="display", font_size_clamp="clamp(2.8rem, 6vw, 5rem)", line_height_ratio=0.98, is_headline=True, max_lines=3)
            }
        )
        root = _build_rich_6section_template(
            paradigm=paradigm,
            headline_id="decon_title",
            headline_text="RUPTURA DEL RETÍCULO Y TENSIÓN CINÉTICA",
            action_id="decon_interact",
            action_label="COLAPSAR CAPAS",
            confirm_id="decon_freeze",
            confirm_label="CONGELAR FRAGMENTO",
            primary_color="#FF0055",
            surface_color="#0A0A0A",
            on_surface_color="#FFFFFF",
            border_color="#333333",
            brand_name="Fracture Lab",
            type_scale="display",
            headline_max_lines=3
        )

    if custom_ir_tree is not None:
        def _sanitize_node(c: Any) -> IRComponent:
            if isinstance(c, IRComponent):
                return c
            if isinstance(c, dict):
                c_copy = dict(c)
                if "task_phase" in c_copy and isinstance(c_copy["task_phase"], str):
                    c_copy["task_phase"] = c_copy["task_phase"].strip().upper()
                if c_copy.get("is_interactive") and not c_copy.get("state_matrix"):
                    bg = "var(--color-primary, oklch(0.65 0.26 355.0))"
                    fg = "var(--color-on-surface, oklch(0.99 0 0))"
                    border = "var(--color-border, oklch(0.5 0 0))"
                    c_copy["state_matrix"] = _build_default_state_matrix(bg, fg, border)
                if "children" in c_copy and isinstance(c_copy["children"], list):
                    c_copy["children"] = [_sanitize_node(child) for child in c_copy["children"]]
                return IRComponent.model_validate(c_copy)
            return IRComponent.model_validate(c)

        if isinstance(custom_ir_tree, DesignIR):
            custom_ir_tree.validate_ir(strict=True)
            return custom_ir_tree
        if isinstance(custom_ir_tree, dict):
            if "root_components" in custom_ir_tree and "perceptual_tokens" in custom_ir_tree:
                return DesignIR.from_dict(custom_ir_tree, validate=True)
            if "root_components" in custom_ir_tree:
                root = [_sanitize_node(c) for c in custom_ir_tree["root_components"]]
            elif "components" in custom_ir_tree:
                root = [_sanitize_node(c) for c in custom_ir_tree["components"]]
            else:
                root = [_sanitize_node(custom_ir_tree)]
        elif isinstance(custom_ir_tree, list):
            root = [_sanitize_node(c) for c in custom_ir_tree]

    assets_obj = assets if 'assets' in locals() and assets else SovereignAssets()
    ir = DesignIR(
        title=t,
        paradigm=paradigm,
        perceptual_tokens=tokens,
        spatial_grammar=spatial,
        typography=typography,
        motion=motion_sys,
        assets=assets_obj,
        root_components=root
    )
    ir.validate_ir(strict=True)
    return ir


# Alias de interoperabilidad
build_paradigm_template = create_paradigm_ir
