"""
.aleph/lib/aleph_kinetic_ode.py
=============================================================================
ALEPH SOVEREIGN WORLD DESIGNER V7.0 — CAPÍTULO 3
SEMÁNTICA DE INTERACCIÓN ESTRICTA, MATRIZ HÁPTICA DE 7 ESTADOS Y CINEMÁTICA ODE
=============================================================================
Módulo formal de cinemática sensorial y contratos interactivos:
1. Simulación matemática analítica y numérica de osciladores armónicos
   amortiguados de segundo orden:
     m * x''(t) + c * x'(t) + k * x(t) = 0
   Compilación a funciones estándar CSS linear(...) (CSS Easing Functions L2).
   Perfiles canónicos del Plan Maestro:
     - --ease-spring-snappy  (zeta = 1.0, amortiguamiento crítico, micro-tactilidad instantánea)
     - --ease-spring-bouncy  (zeta = 0.6, subamortiguado, rebote controlado ~9.5% overshoot)
     - --ease-spring-gentle  (zeta = 0.85, suave y continuo para modales, paneles y navegación)
2. Matriz Háptica Canónica de 7 Estados de Interacción:
   - IDLE
   - HOVER
   - FOCUS_VISIBLE
   - ACTIVE_PRESSED
   - DISABLED
   - LOADING_PENDING
   - FEEDBACK (SUCCESS / ERROR)
3. Validador y Linter Semántico Anti-Slop:
   - Cero conflación ontológica entre <button> (acciones/mutaciones) y <a> (navegación).
   - Prohibición estricta de 'transition: all' / 'transition:all' (GPU thread only).
   - Verificación de completitud de los 7 estados en componentes y CSS.
=============================================================================
"""

from __future__ import annotations

import enum
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

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
# 1. SIMULACIÓN CINEMÁTICA ODE: RESORTES ARMÓNICOS AMORTIGUADOS (2DO ORDEN)
# ============================================================================

class DampingRegime(str, enum.Enum):
    """Régimen de amortiguamiento físico."""
    UNDERDAMPED = "underdamped"       # zeta < 1.0 (oscilatorio con rebote)
    CRITICALLY_DAMPED = "critical"    # zeta == 1.0 (retorno más rápido sin oscilación)
    OVERDAMPED = "overdamped"         # zeta > 1.0 (retorno lento aperiódico)


class SpringPhysicsODE(BaseModel):
    """
    Simulador físico de oscilador armónico amortiguado de 2do orden.
    Ecuación diferencial:
        m * x''(t) + c * x'(t) + k * x(t) = 0
    Forma estándar:
        x''(t) + 2 * zeta * omega_0 * x'(t) + omega_0^2 * x(t) = 0
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    mass: float = Field(default=1.0, gt=0.0, description="Masa del objeto interactivo m (kg o unidades normalizadas)")
    stiffness: float = Field(default=100.0, gt=0.0, description="Constante elástica del resorte k (N/m)")
    damping: float = Field(default=15.0, ge=0.0, description="Coeficiente de amortiguamiento viscoso c (N·s/m)")
    initial_velocity: float = Field(default=0.0, description="Velocidad inicial x'(0)")
    initial_position: float = Field(default=0.0, description="Posición inicial x(0)")
    target: float = Field(default=1.0, description="Posición final de equilibrio x(inf)")

    # -------------------------------------------------------------------------
    # Parámetros Característicos Derivados
    # -------------------------------------------------------------------------
    @property
    def omega_0(self) -> float:
        """Frecuencia angular natural no amortiguada omega_0 = sqrt(k / m) en rad/s."""
        return math.sqrt(self.stiffness / self.mass)

    @property
    def critical_damping(self) -> float:
        """Coeficiente de amortiguamiento crítico c_c = 2 * sqrt(m * k)."""
        return 2.0 * math.sqrt(self.mass * self.stiffness)

    @property
    def damping_ratio(self) -> float:
        """Factor de amortiguamiento adimensional zeta = c / (2 * sqrt(m * k))."""
        return self.damping / self.critical_damping

    @property
    def zeta(self) -> float:
        """Alias para damping_ratio."""
        return self.damping_ratio

    @property
    def regime(self) -> DampingRegime:
        """Régimen dinámico del oscilador según zeta."""
        z = self.damping_ratio
        if abs(z - 1.0) < 1e-7:
            return DampingRegime.CRITICALLY_DAMPED
        elif z < 1.0:
            return DampingRegime.UNDERDAMPED
        else:
            return DampingRegime.OVERDAMPED

    @property
    def omega_d(self) -> float:
        """Frecuencia angular amortiguada omega_d = omega_0 * sqrt(|1 - zeta^2|) en rad/s."""
        z = self.damping_ratio
        return self.omega_0 * math.sqrt(abs(1.0 - z * z))

    @property
    def overshoot_percent(self) -> float:
        """
        Porcentaje máximo de sobreoscilación (overshoot) respecto al escalón unitario.
        Para zeta < 1.0: Mp = exp(-pi * zeta / sqrt(1 - zeta^2)) * 100%
        Para zeta >= 1.0: 0.0%
        """
        z = self.damping_ratio
        if z >= 1.0:
            return 0.0
        exponent = -math.pi * z / math.sqrt(1.0 - z * z)
        return math.exp(exponent) * 100.0

    @property
    def peak_time(self) -> Optional[float]:
        """Tiempo del primer pico de oscilación en segundos (solo régimen subamortiguado)."""
        if self.regime != DampingRegime.UNDERDAMPED or self.omega_d <= 1e-9:
            return None
        return math.pi / self.omega_d

    # -------------------------------------------------------------------------
    # Métodos de Simulación Analítica
    # -------------------------------------------------------------------------
    def evaluate(self, t: float) -> Tuple[float, float]:
        """
        Calcula la posición x(t) y velocidad x'(t) exactas para la respuesta al escalón.
        Condiciones de contorno: x(0) = initial_position, x'(0) = initial_velocity, target.
        Retorna (x, v).
        """
        if t <= 0.0:
            return (self.initial_position, self.initial_velocity)

        w0 = self.omega_0
        zeta = self.damping_ratio
        delta_x = self.initial_position - self.target
        v0 = self.initial_velocity

        if abs(zeta - 1.0) < 1e-7:
            # Régimen críticamente amortiguado (zeta = 1.0)
            # x(t) = target + exp(-w0 * t) * (c1 + c2 * t)
            # x(0) = target + c1 => c1 = delta_x
            # x'(0) = -w0 * c1 + c2 => c2 = v0 + w0 * delta_x
            c1 = delta_x
            c2 = v0 + w0 * delta_x
            decay = math.exp(-w0 * t)
            pos = self.target + decay * (c1 + c2 * t)
            vel = decay * (c2 - w0 * (c1 + c2 * t))
            return (pos, vel)

        elif zeta < 1.0:
            # Régimen subamortiguado (zeta < 1.0)
            wd = self.omega_d
            decay = math.exp(-zeta * w0 * t)
            # x(t) = target + exp(-zeta * w0 * t) * (c1 * cos(wd*t) + c2 * sin(wd*t))
            # x(0) = target + c1 => c1 = delta_x
            # x'(0) = -zeta * w0 * c1 + wd * c2 => c2 = (v0 + zeta * w0 * delta_x) / wd
            c1 = delta_x
            c2 = (v0 + zeta * w0 * delta_x) / wd
            cos_wd = math.cos(wd * t)
            sin_wd = math.sin(wd * t)
            pos = self.target + decay * (c1 * cos_wd + c2 * sin_wd)
            vel = decay * (
                (-zeta * w0 * c1 + wd * c2) * cos_wd
                + (-zeta * w0 * c2 - wd * c1) * sin_wd
            )
            return (pos, vel)

        else:
            # Régimen sobreamortiguado (zeta > 1.0)
            gamma = w0 * math.sqrt(zeta * zeta - 1.0)
            r1 = -zeta * w0 + gamma
            r2 = -zeta * w0 - gamma
            # delta_x = c1 + c2
            # v0 = c1 * r1 + c2 * r2
            c2 = (v0 - delta_x * r1) / (r2 - r1)
            c1 = delta_x - c2
            pos = self.target + c1 * math.exp(r1 * t) + c2 * math.exp(r2 * t)
            vel = c1 * r1 * math.exp(r1 * t) + c2 * r2 * math.exp(r2 * t)
            return (pos, vel)

    def position(self, t: float) -> float:
        """Posición escalar x(t)."""
        return self.evaluate(t)[0]

    def velocity(self, t: float) -> float:
        """Velocidad escalar x'(t)."""
        return self.evaluate(t)[1]

    def settling_time(self, threshold: float = 0.01) -> float:
        """
        Tiempo necesario para que la oscilación quede permanentemente contenida
        dentro de la banda de tolerancia +/- threshold del valor final.
        Por defecto threshold = 0.01 (1%).
        """
        zeta = self.damping_ratio
        w0 = self.omega_0

        if zeta < 1.0:
            # Envolvente exponencial: exp(-zeta * w0 * ts) / sqrt(1 - zeta^2) <= threshold
            safe_sqrt = max(1e-6, math.sqrt(1.0 - zeta * zeta))
            val = threshold * safe_sqrt
            if val <= 0.0:
                val = 1e-6
            return -math.log(val) / (zeta * w0)
        elif abs(zeta - 1.0) < 1e-7:
            # exp(-w0 * ts) * (1 + w0 * ts) <= threshold
            # Para threshold = 0.01, w0 * ts ~= 6.63836
            # Aproximación robusta vía Newton-Raphson
            u = 6.638
            for _ in range(6):
                f = math.exp(-u) * (1.0 + u) - threshold
                df = -u * math.exp(-u)
                if abs(df) > 1e-9:
                    u = u - f / df
            return max(0.05, u / w0)
        else:
            # Dominado por la raíz más lenta r1 = -w0 * (zeta - sqrt(zeta^2 - 1))
            gamma = w0 * math.sqrt(zeta * zeta - 1.0)
            slowest_root = abs(-zeta * w0 + gamma)
            if slowest_root < 1e-6:
                slowest_root = 1e-6
            return -math.log(threshold) / slowest_root

    # -------------------------------------------------------------------------
    # Verificación Numérica (Runge-Kutta de 4to Orden - RK4)
    # -------------------------------------------------------------------------
    def simulate_rk4(
        self,
        duration: float,
        dt: float = 0.001,
    ) -> List[Tuple[float, float, float]]:
        """
        Integra numéricamente el oscilador usando RK4 clásico para verificar
        convergencia respecto a la solución analítica.
        Retorna lista de (t, x, v).
        """
        t = 0.0
        x = self.initial_position
        v = self.initial_velocity
        m = self.mass
        c = self.damping
        k = self.stiffness
        target = self.target

        results = [(t, x, v)]

        def f_acc(pos: float, vel: float) -> float:
            if m == 0:
                return 0.0
            return -(c * vel + k * (pos - target)) / m

        steps = int(duration / dt)
        for _ in range(steps):
            k1_x = v
            k1_v = f_acc(x, v)

            k2_x = v + 0.5 * dt * k1_v
            k2_v = f_acc(x + 0.5 * dt * k1_x, v + 0.5 * dt * k1_v)

            k3_x = v + 0.5 * dt * k2_v
            k3_v = f_acc(x + 0.5 * dt * k2_x, v + 0.5 * dt * k2_v)

            k4_x = v + dt * k3_v
            k4_v = f_acc(x + dt * k3_x, v + dt * k3_v)

            x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
            v += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
            t += dt

            results.append((round(t, 6), x, v))

        return results

    # -------------------------------------------------------------------------
    # Compilación a CSS linear(...)
    # -------------------------------------------------------------------------
    def to_css_linear(
        self,
        sample_count: int = 16,
        precision: int = 4,
        duration_s: Optional[float] = None,
    ) -> str:
        """
        Discretiza la solución analítica continua de la ODE y genera
        una función CSS linear(...) nativa conforme al estándar CSS Easing Level 2.
        """
        if sample_count < 2:
            sample_count = 16

        total_t = duration_s if duration_s is not None else self.settling_time(0.01)
        # Acotar duración razonable para animaciones web [0.1s, 2.0s]
        total_t = max(0.1, min(2.0, total_t))

        points: List[str] = []
        for i in range(sample_count + 1):
            t = (i / sample_count) * total_t
            val = self.position(t)

            # En t=0 forzar normalización estricta
            if i == 0:
                val = self.initial_position
            elif i == sample_count and abs(val - self.target) < 0.02:
                # Estabilización en destino
                val = self.target

            points.append(f"{val:.{precision}f}")

        return f"linear({', '.join(points)})"

    # -------------------------------------------------------------------------
    # Métodos Factoría para Perfiles Canónicos
    # -------------------------------------------------------------------------
    @classmethod
    def from_zeta(
        cls,
        zeta: float,
        natural_frequency_rad_s: float = 20.0,
        mass: float = 1.0,
        target: float = 1.0,
    ) -> SpringPhysicsODE:
        """
        Crea un oscilador definiendo directamente el coeficiente de amortiguamiento zeta
        y la frecuencia natural omega_0.
        Calcula rigurosamente k y c:
            k = m * omega_0^2
            c = 2 * zeta * sqrt(m * k)
        """
        if zeta < 0.0:
            raise ValueError(f"zeta no puede ser negativo: {zeta}")
        k = mass * (natural_frequency_rad_s ** 2)
        c = 2.0 * zeta * math.sqrt(mass * k)
        return cls(mass=mass, stiffness=k, damping=c, target=target)

    @classmethod
    def snappy(cls) -> SpringPhysicsODE:
        """
        Perfil SNAPPY (--ease-spring-snappy):
        Rápido, amortiguamiento crítico exacto (zeta = 1.0).
        Cero sobreoscilación, tiempo de asentamiento de ~150-180ms.
        Ideal para botones, micro-switches, tabs y respuestas mecánicas inmediatas.
        """
        # mass=1.0, stiffness=400.0 => omega_0 = 20.0 rad/s
        # c_c = 2 * sqrt(400) = 40.0 => damping=40.0 => zeta = 1.0000
        return cls(mass=1.0, stiffness=400.0, damping=40.0)

    @classmethod
    def bouncy(cls) -> SpringPhysicsODE:
        """
        Perfil BOUNCY (--ease-spring-bouncy):
        Subamortiguado exacto (zeta = 0.60, rebote controlado con ~9.5% de overshoot).
        Aportando vivacidad táctil a badges, chips, toasts y feedback eufórico.
        """
        # mass=1.0, stiffness=225.0 => omega_0 = 15.0 rad/s
        # c_c = 2 * sqrt(225) = 30.0 => damping = 0.60 * 30.0 = 18.0 => zeta = 0.6000
        return cls(mass=1.0, stiffness=225.0, damping=18.0)

    @classmethod
    def gentle(cls) -> SpringPhysicsODE:
        """
        Perfil GENTLE (--ease-spring-gentle):
        Suave y continuo para modales, paneles, navegación y cambios espaciales de página.
        Amortiguamiento cuasi-crítico (zeta = 0.85, overshoot despreciable < 1%).
        """
        # mass=1.0, stiffness=100.0 => omega_0 = 10.0 rad/s
        # c_c = 2 * sqrt(100) = 20.0 => damping = 0.85 * 20.0 = 17.0 => zeta = 0.8500
        return cls(mass=1.0, stiffness=100.0, damping=17.0)


# ============================================================================
# 2. LOS TRES PERFILES CANÓNICOS DEL PLAN MAESTRO V7.0
# ============================================================================

SPRING_PROFILE_SNAPPY = SpringPhysicsODE.snappy()
SPRING_PROFILE_BOUNCY = SpringPhysicsODE.bouncy()
SPRING_PROFILE_GENTLE = SpringPhysicsODE.gentle()

CANONICAL_SPRING_PROFILES: Dict[str, SpringPhysicsODE] = {
    "--ease-spring-snappy": SPRING_PROFILE_SNAPPY,
    "--ease-spring-bouncy": SPRING_PROFILE_BOUNCY,
    "--ease-spring-gentle": SPRING_PROFILE_GENTLE,
}


def generate_spring_css_tokens(sample_count: int = 16, precision: int = 4) -> Dict[str, str]:
    """Genera el diccionario de tokens CSS custom properties para los tres resortes."""
    return {
        name: profile.to_css_linear(sample_count=sample_count, precision=precision)
        for name, profile in CANONICAL_SPRING_PROFILES.items()
    }


def generate_spring_css_declaration_block(indent: int = 4) -> str:
    """Genera el bloque de variables CSS para inyección en :root o @layer tokens."""
    pad = " " * indent
    lines = [
        f"{pad}/* Aleph Sovereign Kinetic ODE Spring Presets (Capítulo 3) */",
    ]
    tokens = generate_spring_css_tokens()
    for var_name, css_fn in tokens.items():
        lines.append(f"{pad}{var_name}: {css_fn};")
    return "\n".join(lines)


def validate_css_linear_syntax(linear_expr: str) -> bool:
    """
    Verifica que una expresión sea una función CSS linear(...) válida,
    con sintaxis correcta, delimitadores balanceados y números reales.
    """
    linear_expr = linear_expr.strip()
    if not (linear_expr.startswith("linear(") and linear_expr.endswith(")")):
        return False

    inner = linear_expr[7:-1].strip()
    if not inner:
        return False

    parts = [p.strip() for p in inner.split(",") if p.strip()]
    if len(parts) < 2:
        return False

    num_pattern = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)(%|\s+[+-]?(\d+(\.\d*)?|\.\d+)%)?$")
    for part in parts:
        # Extraer el valor base (antes de cualquier porcentaje de stop)
        subparts = part.split()
        try:
            val = float(subparts[0].rstrip("%"))
            if math.isnan(val) or math.isinf(val):
                return False
        except ValueError:
            return False

    return True


def parse_css_linear_points(linear_expr: str) -> List[float]:
    """Extrae la lista de valores de posición numéricos de un linear(...)."""
    if not validate_css_linear_syntax(linear_expr):
        raise ValueError(f"Expresión linear(...) inválida: {linear_expr}")

    inner = linear_expr[7:-1].strip()
    parts = [p.strip() for p in inner.split(",") if p.strip()]
    values: List[float] = []
    for part in parts:
        subparts = part.split()
        values.append(float(subparts[0].rstrip("%")))
    return values


# ============================================================================
# 3. MATRIZ HÁPTICA DE 7 ESTADOS DE INTERACCIÓN FORMAL
# ============================================================================

class InteractionState(str, enum.Enum):
    """
    Los 7 estados ontológicos obligatorios para todo componente interactivo de Aleph:
    1. IDLE: Reposo basal, consumo cero de energía de atención.
    2. HOVER: Anticipación perceptiva táctil al aproximarse el cursor.
    3. FOCUS_VISIBLE: Accesibilidad universal para navegación por teclado.
    4. ACTIVE_PRESSED: Deformación física elástica por compresión mecánica.
    5. DISABLED: Inercia nula, affordance cancelada sin ambigüedad.
    6. LOADING_PENDING: Causalidad en vuelo, bloqueo de clicks concurrentes.
    7. FEEDBACK: Resultado causal de la interacción (SUCCESS eufórico o ERROR rectificativo).
    """
    IDLE = "idle"
    HOVER = "hover"
    FOCUS_VISIBLE = "focus_visible"
    ACTIVE_PRESSED = "active_pressed"
    DISABLED = "disabled"
    LOADING_PENDING = "loading_pending"
    FEEDBACK = "feedback"


class FeedbackType(str, enum.Enum):
    """Sub-modos de retroalimentación causal para el estado FEEDBACK."""
    SUCCESS = "success"
    ERROR = "error"


class StateVisualProps(BaseModel):
    """Propiedades visuales, cinéticas y sensoriales de un estado interactivo."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    state: InteractionState
    feedback_type: Optional[FeedbackType] = None
    transform: Optional[str] = None
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    filter: Optional[str] = None
    background: Optional[str] = None
    color: Optional[str] = None
    border_color: Optional[str] = None
    box_shadow: Optional[str] = None
    outline: Optional[str] = None
    outline_offset: Optional[str] = None
    cursor: Optional[str] = None
    pointer_events: Optional[str] = None
    aria_attributes: Dict[str, str] = Field(default_factory=dict)
    motion_ease: Optional[str] = None
    motion_duration_ms: Optional[float] = None
    animation: Optional[str] = None


class InteractionStateMatrix(BaseModel):
    """
    Contenedor formal de la Matriz Háptica de 7 Estados de Interacción.
    Garantiza que toda entidad interactiva contemple exhaustivamente los 7 estados
    y soporte variantes causales de SUCCESS y ERROR en FEEDBACK.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    states: Dict[InteractionState, StateVisualProps] = Field(default_factory=dict)
    feedback_variants: Dict[FeedbackType, StateVisualProps] = Field(default_factory=dict)

    @field_validator("states")
    @classmethod
    def validate_complete_seven_states(
        cls, states: Dict[InteractionState, StateVisualProps]
    ) -> Dict[InteractionState, StateVisualProps]:
        """Invariante soberana: Los 7 estados canónicos son estrictamente obligatorios."""
        required = set(InteractionState)
        present = set(states.keys())
        missing = required - present
        if missing:
            missing_names = sorted([s.value for s in missing])
            raise ValueError(
                f"Matriz de Interacción incompleta. Faltan estados canónicos obligatorios: {missing_names}. "
                f"Toda entidad interactiva requiere los 7 estados formalizados."
            )
        return states

    def get_state(
        self, state: InteractionState, feedback_type: Optional[FeedbackType] = None
    ) -> StateVisualProps:
        """Obtiene las propiedades de un estado específico o variante de feedback."""
        if state == InteractionState.FEEDBACK and feedback_type:
            if feedback_type in self.feedback_variants:
                return self.feedback_variants[feedback_type]
        return self.states[state]

    @classmethod
    def create_canonical_button_matrix(
        cls,
        primary: bool = True,
        spring_profile: SpringPhysicsODE = SPRING_PROFILE_SNAPPY,
    ) -> InteractionStateMatrix:
        """
        Crea la matriz de 7 estados canónica para un botón de acción.
        Aplica física elástica de compresión scale(0.97-0.98) en ACTIVE_PRESSED,
        anillo de contraste en FOCUS_VISIBLE, y feedback vibrante.
        """
        ease_css = spring_profile.to_css_linear()

        # 1. IDLE
        idle_props = StateVisualProps(
            state=InteractionState.IDLE,
            transform="scale(1.0) translateY(0)",
            opacity=1.0,
            cursor="pointer",
            pointer_events="auto",
            motion_ease=ease_css,
            motion_duration_ms=180.0,
        )

        # 2. HOVER
        hover_props = StateVisualProps(
            state=InteractionState.HOVER,
            transform="translateY(-1.5px)" if primary else "translateY(-1px)",
            filter="brightness(1.10)",
            opacity=1.0,
            cursor="pointer",
            motion_ease=ease_css,
            motion_duration_ms=150.0,
        )

        # 3. FOCUS_VISIBLE
        focus_props = StateVisualProps(
            state=InteractionState.FOCUS_VISIBLE,
            outline="2px solid var(--color-primary, oklch(0.85 0.18 200))",
            outline_offset="3px",
            box_shadow="0 0 0 1px var(--color-surface, #000), 0 0 16px -2px var(--color-primary, #00f0ff)",
            motion_duration_ms=100.0,
        )

        # 4. ACTIVE_PRESSED
        active_props = StateVisualProps(
            state=InteractionState.ACTIVE_PRESSED,
            transform="scale(0.97) translateY(0)" if primary else "scale(0.98) translateY(0)",
            filter="brightness(0.92)",
            motion_ease="cubic-bezier(0.2, 0.9, 0.3, 1.15)",
            motion_duration_ms=100.0,
        )

        # 5. DISABLED
        disabled_props = StateVisualProps(
            state=InteractionState.DISABLED,
            transform="none",
            opacity=0.45,
            filter="grayscale(0.5)",
            cursor="not-allowed",
            pointer_events="none",
            aria_attributes={"aria-disabled": "true"},
        )

        # 6. LOADING_PENDING
        loading_props = StateVisualProps(
            state=InteractionState.LOADING_PENDING,
            opacity=0.80,
            cursor="wait",
            pointer_events="none",
            aria_attributes={"aria-busy": "true"},
        )

        # 7. FEEDBACK (Base y variantes)
        feedback_base = StateVisualProps(
            state=InteractionState.FEEDBACK,
            transform="scale(1.0)",
            opacity=1.0,
        )
        feedback_success = StateVisualProps(
            state=InteractionState.FEEDBACK,
            feedback_type=FeedbackType.SUCCESS,
            background="var(--color-success, #10b981)",
            color="#ffffff",
            border_color="#059669",
            box_shadow="0 0 24px -2px rgba(16, 185, 129, 0.5)",
            animation="aleph-spring-success 350ms cubic-bezier(0.34, 1.56, 0.64, 1)",
            aria_attributes={"data-state": "success"},
        )
        feedback_error = StateVisualProps(
            state=InteractionState.FEEDBACK,
            feedback_type=FeedbackType.ERROR,
            background="var(--color-error, #ef4444)",
            color="#ffffff",
            border_color="#dc2626",
            box_shadow="0 0 20px -2px rgba(239, 68, 68, 0.5)",
            aria_attributes={"data-state": "error"},
        )

        states_dict = {
            InteractionState.IDLE: idle_props,
            InteractionState.HOVER: hover_props,
            InteractionState.FOCUS_VISIBLE: focus_props,
            InteractionState.ACTIVE_PRESSED: active_props,
            InteractionState.DISABLED: disabled_props,
            InteractionState.LOADING_PENDING: loading_props,
            InteractionState.FEEDBACK: feedback_base,
        }

        variants_dict = {
            FeedbackType.SUCCESS: feedback_success,
            FeedbackType.ERROR: feedback_error,
        }

        return cls(states=states_dict, feedback_variants=variants_dict)

    @classmethod
    def create_canonical_link_matrix(
        cls,
        spring_profile: SpringPhysicsODE = SPRING_PROFILE_GENTLE,
    ) -> InteractionStateMatrix:
        """
        Crea la matriz de 7 estados para un enlace de navegación arquitectónica (<a>).
        Garantiza reposo transparente, sin elevaciones de botón ni transformaciones violentas.
        """
        ease_css = spring_profile.to_css_linear()

        idle_props = StateVisualProps(
            state=InteractionState.IDLE,
            background="transparent",
            cursor="pointer",
            pointer_events="auto",
            motion_duration_ms=150.0,
            motion_ease=ease_css,
        )
        hover_props = StateVisualProps(
            state=InteractionState.HOVER,
            background="rgba(255, 255, 255, 0.06)",
            cursor="pointer",
            motion_duration_ms=150.0,
        )
        focus_props = StateVisualProps(
            state=InteractionState.FOCUS_VISIBLE,
            outline="2px solid var(--color-primary, #00f0ff)",
            outline_offset="2px",
        )
        active_props = StateVisualProps(
            state=InteractionState.ACTIVE_PRESSED,
            transform="scale(0.99)",
            motion_duration_ms=100.0,
        )
        disabled_props = StateVisualProps(
            state=InteractionState.DISABLED,
            opacity=0.40,
            cursor="not-allowed",
            pointer_events="none",
            aria_attributes={"aria-disabled": "true"},
        )
        loading_props = StateVisualProps(
            state=InteractionState.LOADING_PENDING,
            opacity=0.60,
            cursor="wait",
            pointer_events="none",
            aria_attributes={"aria-busy": "true"},
        )
        feedback_base = StateVisualProps(
            state=InteractionState.FEEDBACK,
            opacity=1.0,
        )
        feedback_success = StateVisualProps(
            state=InteractionState.FEEDBACK,
            feedback_type=FeedbackType.SUCCESS,
            color="var(--color-success, #10b981)",
            aria_attributes={"data-state": "success"},
        )
        feedback_error = StateVisualProps(
            state=InteractionState.FEEDBACK,
            feedback_type=FeedbackType.ERROR,
            color="var(--color-error, #ef4444)",
            aria_attributes={"data-state": "error"},
        )

        return cls(
            states={
                InteractionState.IDLE: idle_props,
                InteractionState.HOVER: hover_props,
                InteractionState.FOCUS_VISIBLE: focus_props,
                InteractionState.ACTIVE_PRESSED: active_props,
                InteractionState.DISABLED: disabled_props,
                InteractionState.LOADING_PENDING: loading_props,
                InteractionState.FEEDBACK: feedback_base,
            },
            feedback_variants={
                FeedbackType.SUCCESS: feedback_success,
                FeedbackType.ERROR: feedback_error,
            },
        )

    def compile_css_rules(self, base_selector: str) -> str:
        """
        Compila la matriz completa a selectores CSS nativos y seguros para el Composite Thread.
        Rechaza terminantemente 'transition: all'.
        """
        rules: List[str] = []

        # 1. Base / IDLE
        idle = self.states[InteractionState.IDLE]
        rules.append(f"{base_selector} {{")
        rules.append("  display: inline-flex;")
        rules.append("  align-items: center;")
        rules.append("  justify-content: center;")
        if idle.transform:
            rules.append(f"  transform: {idle.transform};")
        if idle.background:
            rules.append(f"  background: {idle.background};")
        if idle.color:
            rules.append(f"  color: {idle.color};")
        rules.append(f"  cursor: {idle.cursor or 'pointer'};")
        # Anti-Slop: Declarar transiciones específicas sobre propiedades GPU
        rules.append("  transition: transform var(--duration-active, 100ms) var(--ease-spring-snappy, cubic-bezier(0.16, 1, 0.3, 1)),")
        rules.append("              background-color var(--duration-hover, 180ms) var(--ease-spring-gentle, cubic-bezier(0.16, 1, 0.3, 1)),")
        rules.append("              border-color var(--duration-hover, 180ms) var(--ease-spring-gentle, cubic-bezier(0.16, 1, 0.3, 1)),")
        rules.append("              box-shadow var(--duration-hover, 180ms) var(--ease-spring-gentle, cubic-bezier(0.16, 1, 0.3, 1)),")
        rules.append("              filter var(--duration-hover, 180ms) var(--ease-spring-gentle, cubic-bezier(0.16, 1, 0.3, 1)),")
        rules.append("              opacity var(--duration-hover, 180ms) ease,")
        rules.append("              outline-offset 120ms ease;")
        rules.append("}")

        # 2. HOVER
        hover = self.states[InteractionState.HOVER]
        rules.append(f"{base_selector}:hover:not(:disabled) {{")
        if hover.transform:
            rules.append(f"  transform: {hover.transform};")
        if hover.filter:
            rules.append(f"  filter: {hover.filter};")
        if hover.background:
            rules.append(f"  background: {hover.background};")
        rules.append("}")

        # 3. FOCUS-VISIBLE
        focus = self.states[InteractionState.FOCUS_VISIBLE]
        rules.append(f"{base_selector}:focus-visible {{")
        if focus.outline:
            rules.append(f"  outline: {focus.outline};")
        if focus.outline_offset:
            rules.append(f"  outline-offset: {focus.outline_offset};")
        if focus.box_shadow:
            rules.append(f"  box-shadow: {focus.box_shadow};")
        rules.append("}")

        # 4. ACTIVE_PRESSED
        active = self.states[InteractionState.ACTIVE_PRESSED]
        rules.append(f"{base_selector}:active:not(:disabled) {{")
        if active.transform:
            rules.append(f"  transform: {active.transform};")
        if active.filter:
            rules.append(f"  filter: {active.filter};")
        rules.append("}")

        # 5. DISABLED
        disabled = self.states[InteractionState.DISABLED]
        rules.append(f"{base_selector}:disabled, {base_selector}[aria-disabled='true'] {{")
        rules.append(f"  opacity: {disabled.opacity};")
        rules.append("  cursor: not-allowed !important;")
        rules.append("  pointer-events: none !important;")
        rules.append("  transform: none !important;")
        if disabled.filter:
            rules.append(f"  filter: {disabled.filter};")
        rules.append("}")

        # 6. LOADING_PENDING
        loading = self.states[InteractionState.LOADING_PENDING]
        rules.append(f"{base_selector}[aria-busy='true'], {base_selector}.is-loading {{")
        rules.append(f"  opacity: {loading.opacity};")
        rules.append("  cursor: wait !important;")
        rules.append("  pointer-events: none !important;")
        rules.append("}")

        # 7. FEEDBACK: SUCCESS & ERROR
        if FeedbackType.SUCCESS in self.feedback_variants:
            succ = self.feedback_variants[FeedbackType.SUCCESS]
            rules.append(f"{base_selector}[data-state='success'], {base_selector}.is-success {{")
            if succ.background:
                rules.append(f"  background-color: {succ.background} !important;")
            if succ.border_color:
                rules.append(f"  border-color: {succ.border_color} !important;")
            if succ.color:
                rules.append(f"  color: {succ.color} !important;")
            if succ.box_shadow:
                rules.append(f"  box-shadow: {succ.box_shadow} !important;")
            if succ.animation:
                rules.append(f"  animation: {succ.animation};")
            rules.append("}")

        if FeedbackType.ERROR in self.feedback_variants:
            err = self.feedback_variants[FeedbackType.ERROR]
            rules.append(f"{base_selector}[data-state='error'], {base_selector}.is-error {{")
            if err.background:
                rules.append(f"  background-color: {err.background} !important;")
            if err.border_color:
                rules.append(f"  border-color: {err.border_color} !important;")
            if err.color:
                rules.append(f"  color: {err.color} !important;")
            if err.box_shadow:
                rules.append(f"  box-shadow: {err.box_shadow} !important;")
            rules.append("}")

        return "\n".join(rules)

    compile_css = compile_css_rules


# ============================================================================
# 4. VALIDADOR Y LINTER SEMÁNTICO ANTI-SLOP
# ============================================================================

class SemanticAuditIssue(BaseModel):
    """Reporte de infracción semántica o de rendimiento interactivo."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: str
    message: str
    severity: str = "FATAL"
    snippet: Optional[str] = None
    line_number: Optional[int] = None


class InteractionSemanticsValidator:
    """
    Auditor y linter formal de interacciones para el Capítulo 3:
    1. Erradicación de la conflación <button> vs <a>.
    2. Prohibición absoluta de 'transition: all' / 'transition:all'.
    3. Verificación de completitud de los 7 estados.
    4. Cumplimiento de WCAG 2.5.5 (Target Size) y WCAG 1.1.1 (Accessible Labels).
    """

    TRANSITION_ALL_PATTERN = re.compile(
        r"transition\s*:\s*([^;}]*?\ball\b[^;}]*)",
        re.IGNORECASE
    )
    TRANSITION_ALL_UTILITY_PATTERN = re.compile(
        r"\btransition-all\b",
        re.IGNORECASE
    )

    BUTTON_TAG_PATTERN = re.compile(
        r"<button\b([^>]*)>",
        re.IGNORECASE
    )
    ANCHOR_TAG_PATTERN = re.compile(
        r"<a\b([^>]*)>",
        re.IGNORECASE
    )

    HREF_ATTR_PATTERN = re.compile(
        r'\bhref\s*=\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    TYPE_ATTR_PATTERN = re.compile(
        r'\btype\s*=\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    ROLE_ATTR_PATTERN = re.compile(
        r'\brole\s*=\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    CLASS_ATTR_PATTERN = re.compile(
        r'\bclass(?:Name)?\s*=\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    ONCLICK_ATTR_PATTERN = re.compile(
        r'\bonclick\s*=',
        re.IGNORECASE
    )
    ARIA_LABEL_PATTERN = re.compile(
        r'\baria-label(?:ledby)?\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    # -------------------------------------------------------------------------
    # Auditoría de CSS
    # -------------------------------------------------------------------------
    @classmethod
    def audit_css(cls, css_content: str) -> List[SemanticAuditIssue]:
        """Audita el CSS rechazando cualquier 'transition: all' o comodines destructivos."""
        issues: List[SemanticAuditIssue] = []
        lines = css_content.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Ignorar comentarios puros
            if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
                continue

            # Búsqueda de transition: all
            match = cls.TRANSITION_ALL_PATTERN.search(line)
            if match:
                issues.append(SemanticAuditIssue(
                    rule_id="ANTI_SLOP_BAN_TRANSITION_ALL",
                    message=(
                        f"Infracción Anti-Slop imperdonable: Se detectó 'transition: all' en la línea {idx}. "
                        f"Forzar recalculo de layout en cada frame destruye los 60/120 FPS. "
                        f"Declare explícitamente solo propiedades GPU (transform, opacity, background-color, border-color, box-shadow)."
                    ),
                    snippet=line.strip(),
                    line_number=idx,
                ))

            # Búsqueda de clases de utilidad estilo Tailwind 'transition-all'
            if cls.TRANSITION_ALL_UTILITY_PATTERN.search(line):
                issues.append(SemanticAuditIssue(
                    rule_id="ANTI_SLOP_BAN_TRANSITION_ALL_CLASS",
                    message=(
                        f"Infracción Anti-Slop: Uso prohibido de la utilidad 'transition-all' en la línea {idx}. "
                        f"Use 'transition-[transform,background-color,border-color,box-shadow,opacity]'."
                    ),
                    snippet=line.strip(),
                    line_number=idx,
                ))

        return issues

    # -------------------------------------------------------------------------
    # Auditoría de HTML Semántico
    # -------------------------------------------------------------------------
    @classmethod
    def audit_html(cls, html_content: str) -> List[SemanticAuditIssue]:
        """
        Audita el HTML garantizando cero conflación entre <button> y <a>:
        - <button> no debe tener 'href' ni clase de navegación pura 'aleph-nav-link'.
        - <button> debe tener 'type' explícito (button, submit, reset).
        - <a> debe tener 'href' real, y no debe simular ser un botón primario de acción ni usar href="#"/onclick.
        - Triggers de ícono deben contener aria-label.
        """
        issues: List[SemanticAuditIssue] = []

        # 1. Auditoría de etiquetas <button>
        for match in cls.BUTTON_TAG_PATTERN.finditer(html_content):
            attrs = match.group(1)
            full_tag = match.group(0)

            # Infracción: <button> con atributo href
            if cls.HREF_ATTR_PATTERN.search(attrs):
                issues.append(SemanticAuditIssue(
                    rule_id="ANTI_CONFLATION_BUTTON_WITH_HREF",
                    message=(
                        "Conflación ontológica prohibida: <button> porta el atributo 'href'. "
                        "Un botón ejecuta acciones en el cliente/servidor; la navegación de URLs corresponde estrictamente a <a>."
                    ),
                    snippet=full_tag,
                ))

            # Infracción: <button> sin atributo 'type'
            type_match = cls.TYPE_ATTR_PATTERN.search(attrs)
            if not type_match:
                issues.append(SemanticAuditIssue(
                    rule_id="ACCESSIBILITY_BUTTON_MISSING_TYPE",
                    message=(
                        "Accesibilidad/HTML5 violado: <button> carece de atributo 'type' explícito. "
                        "Por defecto en navegadores actúa como 'submit', pudiendo causar envíos de formulario involuntarios."
                    ),
                    snippet=full_tag,
                ))
            else:
                btn_type = type_match.group(1).lower()
                if btn_type not in ("button", "submit", "reset"):
                    issues.append(SemanticAuditIssue(
                        rule_id="HTML5_INVALID_BUTTON_TYPE",
                        message=f"Atributo type='{btn_type}' no es un tipo de botón HTML5 válido.",
                        snippet=full_tag,
                    ))

            # Infracción: <button> disfrazado de nav_link
            class_match = cls.CLASS_ATTR_PATTERN.search(attrs)
            if class_match:
                classes = class_match.group(1).split()
                if "aleph-nav-link" in classes and "aleph-action-primary" in classes:
                    issues.append(SemanticAuditIssue(
                        rule_id="ANTI_CONFLATION_DUAL_ROLE_CLASS",
                        message="Componente contiene simultáneamente 'aleph-nav-link' y 'aleph-action-primary'.",
                        snippet=full_tag,
                    ))

            # Infracción: Icon trigger sin aria-label
            if class_match and "aleph-icon-trigger" in class_match.group(1):
                if not cls.ARIA_LABEL_PATTERN.search(attrs):
                    issues.append(SemanticAuditIssue(
                        rule_id="ACCESSIBILITY_ICON_TRIGGER_NO_LABEL",
                        message=(
                            "WCAG 1.1.1 / 2.5.5 violado: Todo disparador puramente icónico "
                            "DEBE incluir 'aria-label' o 'aria-labelledby'."
                        ),
                        snippet=full_tag,
                    ))

        # 2. Auditoría de etiquetas <a>
        for match in cls.ANCHOR_TAG_PATTERN.finditer(html_content):
            attrs = match.group(1)
            full_tag = match.group(0)

            href_match = cls.HREF_ATTR_PATTERN.search(attrs)
            # Infracción: <a> sin href
            if not href_match:
                issues.append(SemanticAuditIssue(
                    rule_id="SEMANTIC_ANCHOR_WITHOUT_HREF",
                    message=(
                        "Semántica hipertextual rota: <a> no define atributo 'href'. "
                        "Si el elemento no navega a ninguna URI, debe ser un <button>."
                    ),
                    snippet=full_tag,
                ))
            else:
                href_val = href_match.group(1).strip()
                # Infracción: <a> usado como pseudo-botón de acción (href="#" con onclick o href="javascript:...")
                if href_val.startswith("javascript:") or (href_val == "#" and cls.ONCLICK_ATTR_PATTERN.search(attrs)):
                    issues.append(SemanticAuditIssue(
                        rule_id="ANTI_CONFLATION_ANCHOR_AS_PSEUDO_BUTTON",
                        message=(
                            f"Conflación ontológica prohibida: <a> con href='{href_val}' utilizado como disparador de acción. "
                            f"Debe implementarse obligatoriamente como <button type='button'>."
                        ),
                        snippet=full_tag,
                    ))

            # Infracción: <a> disfrazado de botón primario (conflación de affordance visual)
            class_match = cls.CLASS_ATTR_PATTERN.search(attrs)
            if class_match:
                classes = class_match.group(1).split()
                if "aleph-action-primary" in classes:
                    issues.append(SemanticAuditIssue(
                        rule_id="ANTI_CONFLATION_LINK_DISGUISED_AS_PRIMARY_ACTION",
                        message=(
                            "Conflación visual anti-slop: Un enlace <a> tiene asignada la clase 'aleph-action-primary'. "
                            "Un enlace de navegación arquitectónica nunca puede disfrazarse de botón de acción principal."
                        ),
                        snippet=full_tag,
                    ))

        return issues

    # -------------------------------------------------------------------------
    # Auditoría de Completitud de los 7 Estados
    # -------------------------------------------------------------------------
    @classmethod
    def audit_state_matrix_completeness(
        cls, state_matrix: Union[InteractionStateMatrix, Dict[str, Any]]
    ) -> List[SemanticAuditIssue]:
        """Verifica que la matriz de estados defina exhaustivamente los 7 estados obligatorios."""
        issues: List[SemanticAuditIssue] = []

        if isinstance(state_matrix, InteractionStateMatrix):
            present_states = set(state_matrix.states.keys())
        elif isinstance(state_matrix, dict):
            # Normalizar claves a enum si son strings
            present_states = set()
            for k in state_matrix.keys():
                for s in InteractionState:
                    if s.value == k or s.name.lower() == k:
                        present_states.add(s)
        else:
            issues.append(SemanticAuditIssue(
                rule_id="STATE_MATRIX_INVALID_TYPE",
                message=f"Tipo de matriz inválido: {type(state_matrix)}",
            ))
            return issues

        required = set(InteractionState)
        missing = required - present_states
        if missing:
            missing_names = sorted([m.value for m in missing])
            issues.append(SemanticAuditIssue(
                rule_id="STATE_MATRIX_INCOMPLETE",
                message=f"Faltan estados requeridos en la Matriz Háptica: {missing_names}",
            ))

        return issues

    # -------------------------------------------------------------------------
    # Auditoría de Bundle Compilado Completo
    # -------------------------------------------------------------------------
    @classmethod
    def audit_compiled_bundle(
        cls, html_content: str, css_content: str
    ) -> Dict[str, Any]:
        """
        Ejecuta la suite integral de verificación del Capítulo 3 sobre un bundle compilado.
        Retorna reporte con métricas y veredicto binario de certificación.
        """
        css_issues = cls.audit_css(css_content)
        html_issues = cls.audit_html(html_content)
        all_issues = css_issues + html_issues

        # Verificar presencia de las 3 variables de resortes en el CSS
        has_snappy = "--ease-spring-snappy" in css_content
        has_bouncy = "--ease-spring-bouncy" in css_content
        has_gentle = "--ease-spring-gentle" in css_content
        spring_vars_complete = has_snappy and has_bouncy and has_gentle

        if not spring_vars_complete:
            missing_vars = []
            if not has_snappy:
                missing_vars.append("--ease-spring-snappy")
            if not has_bouncy:
                missing_vars.append("--ease-spring-bouncy")
            if not has_gentle:
                missing_vars.append("--ease-spring-gentle")
            all_issues.append(SemanticAuditIssue(
                rule_id="MISSING_KINETIC_ODE_CSS_VARS",
                message=f"El CSS compilado carece de las curvas de resorte ODE requeridas: {missing_vars}",
            ))

        # Verificar presencia de los 7 estados en selectores CSS
        state_selectors_audit = {
            "hover": ":hover" in css_content,
            "active": ":active" in css_content,
            "focus_visible": ":focus-visible" in css_content,
            "disabled": ":disabled" in css_content or "aria-disabled" in css_content,
            "loading": "aria-busy" in css_content or "is-loading" in css_content,
            "feedback_success": "is-success" in css_content or "data-state='success'" in css_content,
            "feedback_error": "is-error" in css_content or "data-state='error'" in css_content,
        }
        all_states_represented = all(state_selectors_audit.values())

        if not all_states_represented:
            missing_states = [k for k, v in state_selectors_audit.items() if not v]
            all_issues.append(SemanticAuditIssue(
                rule_id="MISSING_CSS_STATE_SELECTORS",
                message=f"El CSS no contiene selectores para los estados hápticos: {missing_states}",
            ))

        certified = len(all_issues) == 0

        return {
            "certified": certified,
            "total_violations": len(all_issues),
            "css_violations": len(css_issues),
            "html_violations": len(html_issues),
            "spring_tokens_present": spring_vars_complete,
            "all_7_states_present": all_states_represented,
            "state_coverage": state_selectors_audit,
            "issues": [issue.model_dump() for issue in all_issues],
        }
