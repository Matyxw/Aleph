"""
.aleph/lib/aleph_shader_compiler.py
Compilador de Activos Soberanos: Shaders GLSL WebGL2, Fallbacks Deterministas 2D/SVG,
Físicas de Resorte y Tipografía Monumental Continua con Alineamiento al Baseline de 4px/8px.
Estándar: Aleph Sovereign Design Engine / Emil Kowalski & GPU Shader Architecture.
Capítulo 5 del Plan Maestro V7.0: Coreografía Espacial Asimétrica Suiza y Shaders WebGL.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# ==============================================================================
# 1. FÍSICAS DE RESORTE Y EASING CSS linear()
# ==============================================================================

@dataclass
class SpringConfig:
    mass: float = 1.0        # m
    stiffness: float = 180.0 # k
    damping: float = 12.0    # d
    initial_velocity: float = 0.0

    @property
    def natural_frequency(self) -> float:
        """omega_0 = sqrt(k / m)"""
        return math.sqrt(self.stiffness / self.mass)

    @property
    def damping_ratio(self) -> float:
        """zeta = d / (2 * sqrt(m * k))"""
        return self.damping / (2.0 * math.sqrt(self.mass * self.stiffness))

    def evaluate_at(self, t: float) -> float:
        """
        Evalúa el desplazamiento x(t) partiendo de x(0)=0 hacia x_target=1.
        Satisface la ecuación diferencial del oscilador armónico amortiguado.
        """
        if t <= 0.0:
            return 0.0

        zeta = self.damping_ratio
        omega_0 = self.natural_frequency

        if zeta < 1.0:
            # Subamortiguado (Underdamped): oscilación suave que se asienta
            omega_d = omega_0 * math.sqrt(1.0 - zeta * zeta)
            decay = math.exp(-zeta * omega_0 * t)
            c1 = 1.0
            c2 = (zeta * omega_0 - self.initial_velocity) / omega_d
            pos = 1.0 - decay * (c1 * math.cos(omega_d * t) + c2 * math.sin(omega_d * t))
            return pos
        elif math.isclose(zeta, 1.0, rel_tol=1e-4):
            # Amortiguamiento crítico (Critically Damped): regreso más rápido sin oscilación
            decay = math.exp(-omega_0 * t)
            pos = 1.0 - decay * (1.0 + (omega_0 - self.initial_velocity) * t)
            return pos
        else:
            # Sobreamortiguado (Overdamped)
            r1 = -omega_0 * (zeta - math.sqrt(zeta * zeta - 1.0))
            r2 = -omega_0 * (zeta + math.sqrt(zeta * zeta - 1.0))
            c2 = (r1 + self.initial_velocity) / (r1 - r2)
            c1 = 1.0 - c2
            pos = 1.0 - (c1 * math.exp(r1 * t) + c2 * math.exp(r2 * t))
            return pos

    def generate_css_linear_easing(self, duration_s: float = 0.6, samples: int = 30) -> str:
        """
        Genera una función CSS linear(...) muestreada en GPU sin costo de JS en runtime.
        Ejemplo: linear(0, 0.02, 0.15, ..., 1)
        """
        points = []
        for i in range(samples + 1):
            t = (i / samples) * duration_s
            val = self.evaluate_at(t)
            points.append(f"{round(val, 4)}")
        
        # Garantizar que el último valor sea exactamente 1
        points[-1] = "1"
        return f"linear({', '.join(points)})"


# ==============================================================================
# 2. TIPOGRAFÍA MONUMENTAL CONTINUA CON ALINEAMIENTO A BASELINE (4px / 8px)
# ==============================================================================

@dataclass(frozen=True)
class MonumentalTypographyToken:
    """
    Token tipográfico monumental continuo gobernado por la función analítica clamp()
    con garantía matemática de alineamiento estricto a la cuadrícula vertical de 4px/8px.
    """
    name: str
    min_size_px: float
    max_size_px: float
    min_viewport_px: float
    max_viewport_px: float
    baseline_unit: int
    target_lh_ratio: float
    slope: float
    intercept_px: float
    slope_vw: float
    intercept_rem: float
    min_rem: float
    max_rem: float
    clamp_expr: str
    line_height_min_px: float
    line_height_max_px: float
    line_height_clamp_expr: str

    def eval_font_size(self, viewport_w: float) -> float:
        """Evalúa el tamaño de fuente continuo en px para cualquier ancho de pantalla."""
        w_clamped = max(self.min_viewport_px, min(self.max_viewport_px, viewport_w))
        val = self.slope * w_clamped + self.intercept_px
        return max(self.min_size_px, min(self.max_size_px, val))

    def eval_line_height(self, viewport_w: float) -> float:
        """Evalúa la altura de línea continua en px para cualquier viewport."""
        w_clamped = max(self.min_viewport_px, min(self.max_viewport_px, viewport_w))
        lh_slope = (self.line_height_max_px - self.line_height_min_px) / (self.max_viewport_px - self.min_viewport_px)
        lh_intercept = self.line_height_min_px - lh_slope * self.min_viewport_px
        val = lh_slope * w_clamped + lh_intercept
        return max(self.line_height_min_px, min(self.line_height_max_px, val))

    def verify_baseline_alignment(self, viewport_w: float, baseline_unit: Optional[int] = None) -> Dict[str, Any]:
        """
        Verifica la conformidad del ritmo vertical con la cuadrícula base de 4px u 8px.
        """
        unit = baseline_unit or self.baseline_unit
        lh = self.eval_line_height(viewport_w)
        # Residuo respecto a la unidad base vertical
        remainder = round(lh % unit, 4)
        is_exact = math.isclose(remainder, 0.0, abs_tol=1e-3) or math.isclose(remainder, float(unit), abs_tol=1e-3)
        return {
            "name": self.name,
            "viewport_w": viewport_w,
            "font_size_px": round(self.eval_font_size(viewport_w), 3),
            "line_height_px": round(lh, 3),
            "baseline_unit": unit,
            "remainder": remainder,
            "aligned_to_baseline": is_exact,
        }


def calculate_monumental_clamp(
    name: str,
    min_size_px: float,
    max_size_px: float,
    min_viewport_px: float = 320.0,
    max_viewport_px: float = 3840.0,
    baseline_unit: int = 4,
    target_lh_ratio: float = 1.15,
    snap_to_baseline: bool = True,
) -> MonumentalTypographyToken:
    """
    Calcula la fórmula matemática de interpolación de clamp continua:
    font-size: clamp(min_size, slope * 100vw + intercept, max_size)
    
    Asegura que los tamaños de calibración y las alturas de línea se alineen
    estrictamente con la cuadrícula de baseline vertical de 4px u 8px.
    """
    if min_viewport_px >= max_viewport_px:
        raise ValueError("min_viewport_px debe ser estrictamente menor que max_viewport_px")
    if baseline_unit not in (4, 8):
        raise ValueError("baseline_unit debe ser 4 o 8 (estándar suizo)")

    # Snapping de calibración a múltiplos enteros del baseline
    if snap_to_baseline:
        min_px = round(min_size_px / baseline_unit) * baseline_unit
        max_px = round(max_size_px / baseline_unit) * baseline_unit
    else:
        min_px = min_size_px
        max_px = max_size_px

    if min_px > max_px:
        max_px = min_px

    # Cálculo analítico de pendiente e intercepto (y = mx + b)
    delta_v = max_viewport_px - min_viewport_px
    delta_s = max_px - min_px

    slope = delta_s / delta_v
    intercept_px = min_px - slope * min_viewport_px

    slope_vw = slope * 100.0
    intercept_rem = intercept_px / 16.0
    min_rem = min_px / 16.0
    max_rem = max_px / 16.0

    # Expresión clamp estándar W3C CSS
    clamp_expr = f"clamp({min_rem:.4f}rem, {slope_vw:.4f}vw + {intercept_rem:.4f}rem, {max_rem:.4f}rem)"

    # Altura de línea estrictamente alineada al baseline vertical en ambos extremos
    lh_min_raw = min_px * target_lh_ratio
    lh_max_raw = max_px * target_lh_ratio

    lh_min_px = float(math.ceil(lh_min_raw / baseline_unit) * baseline_unit)
    lh_max_px = float(math.ceil(lh_max_raw / baseline_unit) * baseline_unit)

    lh_slope = (lh_max_px - lh_min_px) / delta_v
    lh_intercept_px = lh_min_px - lh_slope * min_viewport_px
    lh_slope_vw = lh_slope * 100.0
    lh_intercept_rem = lh_intercept_px / 16.0
    lh_min_rem = lh_min_px / 16.0
    lh_max_rem = lh_max_px / 16.0

    line_height_clamp_expr = f"clamp({lh_min_rem:.4f}rem, {lh_slope_vw:.4f}vw + {lh_intercept_rem:.4f}rem, {lh_max_rem:.4f}rem)"

    return MonumentalTypographyToken(
        name=name,
        min_size_px=min_px,
        max_size_px=max_px,
        min_viewport_px=min_viewport_px,
        max_viewport_px=max_viewport_px,
        baseline_unit=baseline_unit,
        target_lh_ratio=target_lh_ratio,
        slope=slope,
        intercept_px=intercept_px,
        slope_vw=slope_vw,
        intercept_rem=intercept_rem,
        min_rem=min_rem,
        max_rem=max_rem,
        clamp_expr=clamp_expr,
        line_height_min_px=lh_min_px,
        line_height_max_px=lh_max_px,
        line_height_clamp_expr=line_height_clamp_expr,
    )


def generate_swiss_monumental_scale(
    baseline_unit: int = 4,
    min_viewport_px: float = 320.0,
    max_viewport_px: float = 3840.0,
) -> Dict[str, MonumentalTypographyToken]:
    """
    Genera la escala canónica del Capítulo 5 de Aleph Sovereign Engine:
    Display Hero, H1, H2, H3, Lead, Body, Caption.
    Alineada al baseline vertical suizo de 4px o 8px.
    """
    specs: List[Tuple[str, float, float, float]] = [
        # (name, min_px, max_px, target_lh_ratio)
        ("display", 48.0, 224.0, 0.95),  # Hero Monumental (48px y 224px múltiplos de 8 y 16)
        ("h1", 36.0, 124.0, 1.05),       # H1 Monumental
        ("h2", 28.0, 72.0, 1.15),        # H2 Arquitectónico
        ("h3", 24.0, 44.0, 1.25),        # H3 Estructural
        ("lead", 20.0, 28.0, 1.35),      # Lead Editorial
        ("body", 16.0, 24.0, 1.50),      # Body Base
        ("caption", 12.0, 16.0, 1.40),   # Micro-Metadata
    ]

    scale: Dict[str, MonumentalTypographyToken] = {}
    for name, s_min, s_max, lh_ratio in specs:
        scale[name] = calculate_monumental_clamp(
            name=name,
            min_size_px=s_min,
            max_size_px=s_max,
            min_viewport_px=min_viewport_px,
            max_viewport_px=max_viewport_px,
            baseline_unit=baseline_unit,
            target_lh_ratio=lh_ratio,
            snap_to_baseline=True,
        )
    return scale


def generate_monumental_typography_css(
    scale: Optional[Dict[str, MonumentalTypographyToken]] = None,
    baseline_unit: int = 4
) -> str:
    """
    Emite el bloque CSS con variables fluidas clamp() y clases de utilidad
    con compensación óptica y alineamiento de baseline.
    """
    tokens = scale or generate_swiss_monumental_scale(baseline_unit=baseline_unit)
    lines = [
        "/* ==========================================================================",
        f"   ALEPH SOVEREIGN MONUMENTAL FLUID TYPOGRAPHY (BASELINE {baseline_unit}px)",
        "   ========================================================================== */",
        ":root {",
        f"  --aleph-baseline-unit: {baseline_unit}px;",
    ]

    for name, token in tokens.items():
        lines.append(f"  --font-size-{name}: {token.clamp_expr};")
        lines.append(f"  --line-height-{name}: {token.line_height_clamp_expr};")

    lines.extend([
        "  /* Tracking Óptico Inverso */",
        "  --letter-spacing-display: clamp(-0.055em, -0.02em - 0.01vw, -0.02em);",
        "  --letter-spacing-h1: clamp(-0.04em, -0.015em - 0.008vw, -0.01em);",
        "  --letter-spacing-body: clamp(-0.01em, 0em, 0.015em);",
        "}",
        "",
        ".aleph-type-display {",
        "  font-family: var(--aleph-font-monumental, 'Neue Haas Grotesk', -apple-system, sans-serif);",
        "  font-size: var(--font-size-display);",
        "  line-height: var(--line-height-display);",
        "  letter-spacing: var(--letter-spacing-display);",
        "  font-weight: 800;",
        "  text-transform: uppercase;",
        "  text-wrap: balance;",
        "}",
        "",
        ".aleph-type-h1 {",
        "  font-size: var(--font-size-h1);",
        "  line-height: var(--line-height-h1);",
        "  letter-spacing: var(--letter-spacing-h1);",
        "  font-weight: 700;",
        "  text-wrap: balance;",
        "}",
        "",
        ".aleph-type-body {",
        "  font-size: var(--font-size-body);",
        "  line-height: var(--line-height-body);",
        "  letter-spacing: var(--letter-spacing-body);",
        "  font-weight: 400;",
        "  text-wrap: pretty;",
        "}",
    ])
    return "\n".join(lines)


# ==============================================================================
# 3. CATÁLOGO CANÓNICO DE SHADERS GLSL ES 3.0 / WEBGL 2.0
# ==============================================================================

GLSL_SHADER_CATALOG = {
    # 1. RAYMARCHING: Múltiple campo de distancias con iluminación volumétrica y glow
    "raymarching": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

float sdSphere(vec3 p, float s) {
    return length(p) - s;
}

float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float map(vec3 p) {
    vec3 q = p;
    float t = u_time * 0.4;
    float c = cos(t);
    float s = sin(t);
    q.xz = mat2(c, -s, s, c) * q.xz;
    float d1 = sdTorus(q, vec2(1.2, 0.35));
    float d2 = sdSphere(p - vec3(sin(t * 1.5) * 0.4, cos(t * 1.2) * 0.3, 0.0), 0.75);
    return smin(d1, d2, 0.45);
}

vec3 calcNormal(vec3 p) {
    const float eps = 0.002;
    vec2 h = vec2(eps, 0.0);
    return normalize(vec3(
        map(p + h.xyy) - map(p - h.xyy),
        map(p + h.yxy) - map(p - h.yxy),
        map(p + h.yyx) - map(p - h.yyx)
    ));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    vec3 ro = vec3(0.0, 0.0, -3.2);
    vec3 rd = normalize(vec3(uv, 1.2));
    
    float dO = 0.0;
    float glow = 0.0;
    for(int i = 0; i < 48; i++) {
        vec3 p = ro + rd * dO;
        float dS = map(p);
        glow += 0.015 / (0.05 + abs(dS));
        dO += dS * 0.8;
        if(dS < 0.003 || dO > 12.0) break;
    }
    
    vec3 col = vec3(0.03, 0.03, 0.06);
    if(dO < 12.0) {
        vec3 p = ro + rd * dO;
        vec3 n = calcNormal(p);
        vec3 light = normalize(vec3(1.0, 2.0, -2.0));
        float diff = max(dot(n, light), 0.0);
        float spec = pow(max(dot(reflect(-light, n), -rd), 0.0), 16.0);
        vec3 base = vec3(0.12, 0.25, 0.45);
        col = base * diff + vec3(0.9, 0.95, 1.0) * spec;
    }
    col += vec3(0.2, 0.45, 0.9) * (glow * 0.06);
    fragColor = vec4(col, 1.0);
}""",

    # 2. CAMPO CUÁNTICO: Simulación de función de onda, amplitudes y densidad de probabilidad
    "quantum_field": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float r = length(uv);
    float theta = atan(uv.y, uv.x);
    
    // Superposición de estados cuánticos y fluctuaciones del vacío
    float psi1 = sin(r * 18.0 - u_time * 2.0 + theta * 3.0);
    float psi2 = cos(r * 28.0 + u_time * 1.5 - theta * 5.0);
    float psi3 = sin((uv.x + uv.y) * 12.0 - u_time);
    
    float psi_real = psi1 * 0.5 + psi3 * 0.5;
    float psi_imag = psi2 * 0.6 + sin(theta * 2.0) * 0.4;
    float prob_density = (psi_real * psi_real + psi_imag * psi_imag) * 0.5;
    
    float nodal_ring = smoothstep(0.02, 0.0, abs(fract(r * 6.0 - u_time * 0.2) - 0.5) - 0.46);
    
    vec3 void_col = vec3(0.02, 0.02, 0.05);
    vec3 phase_cyan = vec3(0.0, 0.85, 1.0);
    vec3 phase_violet = vec3(0.68, 0.15, 0.95);
    vec3 nodal_glow = vec3(0.3, 0.7, 1.0);
    
    vec3 col = mix(void_col, phase_violet, prob_density);
    col = mix(col, phase_cyan, psi_real * 0.5 + 0.5);
    col += nodal_glow * nodal_ring * 0.8;
    col *= smoothstep(1.5, 0.2, r);
    fragColor = vec4(col, 1.0);
}""",

    # 3. SCANLINES CRT: Tubo catódico, distorsión cilíndrica, máscara de fósforo y entrelazado
    "crt_scanlines": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

vec2 barrelDistortion(vec2 uv, float k) {
    vec2 cc = uv - 0.5;
    float dist = dot(cc, cc);
    return uv + cc * dist * k;
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    vec2 uv = barrelDistortion(st, 0.14);
    
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    vec2 dir = uv - 0.5;
    float dist = length(dir);
    
    // Haz de electrones: líneas de escaneo activas
    float scanline = sin(uv.y * u_resolution.y * 1.5 + u_time * 6.0);
    float scanMod = mix(0.75, 1.0, scanline * 0.5 + 0.5);
    
    // Máscara de apertura de tríada RGB
    float triadX = uv.x * u_resolution.x * 3.14159265 * 2.0 / 3.0;
    vec3 phosphorMask = vec3(
        0.5 + 0.5 * sin(triadX),
        0.5 + 0.5 * sin(triadX + 2.09439),
        0.5 + 0.5 * sin(triadX + 4.18879)
    );
    
    // Contenido SCADA / HUD fosforescente
    float grid = step(0.96, fract(uv.x * 20.0)) + step(0.96, fract(uv.y * 14.0));
    vec3 content = vec3(0.04, 0.12, 0.08);
    content += vec3(0.1, 0.85, 0.3) * clamp(grid, 0.0, 1.0);
    
    float vig = smoothstep(0.72, 0.25, dist);
    vec3 finalCol = content * scanMod * (vec3(0.4) + 0.6 * phosphorMask) * vig;
    fragColor = vec4(finalCol, 1.0);
}""",

    # 4. FLUIDO ORGÁNICO: Navier-Stokes / deformación de dominio multi-octava (Curl Noise)
    "organic_fluid": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
    p = 50.0 * fract(p * 0.3183099 + vec2(0.71, 0.113));
    return -1.0 + 2.0 * fract(16.0 * p.x * p.y * (p.x + p.y));
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    vec2 shift = vec2(100.0);
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 4; ++i) {
        v += a * noise(p);
        p = rot * p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.18;
    
    vec2 q = vec2(fbm(uv + vec2(0.0, 0.0) + t), fbm(uv + vec2(5.2, 1.3) + t));
    vec2 r = vec2(fbm(uv + 4.0 * q + vec2(1.7, 9.2) + 0.15 * t),
                  fbm(uv + 4.0 * q + vec2(8.3, 2.8) + 0.126 * t));
    
    float f = fbm(uv + 4.0 * r);
    
    vec3 c1 = vec3(0.03, 0.05, 0.08);
    vec3 c2 = vec3(0.12, 0.38, 0.32);
    vec3 c3 = vec3(0.85, 0.55, 0.28);
    vec3 c4 = vec3(0.92, 0.95, 0.98);
    
    vec3 col = mix(c1, c2, clamp(f * f * 4.0, 0.0, 1.0));
    col = mix(col, c3, clamp(length(q), 0.0, 1.0));
    col = mix(col, c4, clamp(length(r.x), 0.0, 1.0));
    col *= (1.0 - 0.3 * length(uv));
    fragColor = vec4(col, 1.0);
}""",

    # 5. CÁUSTICAS MINERALES: Refracción de cristal, Voronoi F2-F1 y dispersión cromática RGB
    "mineral_caustics": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453);
}

vec2 voronoi(vec2 x, float timeOffset) {
    vec2 n = floor(x);
    vec2 f = fract(x);
    float m1 = 8.0;
    float m2 = 8.0;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = hash2(n + g);
            o = 0.5 + 0.5 * sin(timeOffset + 6.2831853 * o);
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < m1) {
                m2 = m1;
                m1 = d;
            } else if (d < m2) {
                m2 = d;
            }
        }
    }
    return vec2(sqrt(m1), sqrt(m2));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.4;
    
    float scale = 5.0;
    vec2 vR = voronoi(uv * scale + vec2(0.01, 0.0), t);
    vec2 vG = voronoi(uv * scale, t + 0.05);
    vec2 vB = voronoi(uv * scale - vec2(0.01, 0.0), t + 0.1);
    
    float cR = pow(1.0 - clamp(vR.y - vR.x, 0.0, 1.0), 3.5);
    float cG = pow(1.0 - clamp(vG.y - vG.x, 0.0, 1.0), 3.5);
    float cB = pow(1.0 - clamp(vB.y - vB.x, 0.0, 1.0), 3.5);
    
    vec2 v2 = voronoi(uv * (scale * 2.2) + vec2(t * 0.2), -t * 0.5);
    float cSub = pow(1.0 - clamp(v2.y - v2.x, 0.0, 1.0), 2.5) * 0.4;
    
    vec3 deepMineral = vec3(0.02, 0.06, 0.11);
    vec3 causticCol = vec3(cR, cG, cB) * 1.8 + vec3(cSub * 0.6, cSub * 0.9, cSub * 1.2);
    vec3 finalCol = deepMineral + causticCol * vec3(0.4, 0.85, 1.0);
    fragColor = vec4(finalCol, 1.0);
}""",

    # Shaders de catálogo continuo para compatibilidad
    "convective_noise_mesh": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
    p = 50.0 * fract(p * 0.3183099 + vec2(0.71, 0.113));
    return -1.0 + 2.0 * fract(16.0 * p.x * p.y * (p.x + p.y));
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f*f*(3.0-2.0*f);
    return mix(mix(hash(i + vec2(0.0,0.0)), hash(i + vec2(1.0,0.0)), u.x),
               mix(hash(i + vec2(0.0,1.0)), hash(i + vec2(1.0,1.0)), u.x), u.y);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    float n = noise(st * 3.0 + u_time * 0.1);
    vec3 c1 = vec3(0.05, 0.05, 0.08);
    vec3 c2 = vec3(0.18, 0.22, 0.35);
    fragColor = vec4(mix(c1, c2, n * 0.5 + 0.5), 1.0);
}""",

    "raymarched_atmospheric_field": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

float sdSphere(vec3 p, float s) { return length(p) - s; }

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    vec3 ro = vec3(0.0, 0.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.0));
    float dO = 0.0;
    for(int i = 0; i < 32; i++) {
        vec3 p = ro + rd * dO;
        float dS = sdSphere(p - vec3(sin(u_time * 0.5) * 0.5, 0.0, 0.0), 1.0);
        dO += dS;
        if(dS < 0.01 || dO > 10.0) break;
    }
    float glow = 1.0 / (1.0 + dO * dO * 0.5);
    fragColor = vec4(vec3(0.1, 0.2, 0.4) * glow, 1.0);
}""",

    "chromatic_grid_distortion": """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 center = uv - 0.5;
    float dist = length(center);
    vec2 uvR = uv + center * (dist * 0.03);
    vec2 uvB = uv - center * (dist * 0.03);
    
    vec2 gridR = abs(fract(uvR * 20.0 - 0.5) - 0.5) / fwidth(uvR * 20.0);
    vec2 gridG = abs(fract(uv * 20.0 - 0.5) - 0.5) / fwidth(uv * 20.0);
    vec2 gridB = abs(fract(uvB * 20.0 - 0.5) - 0.5) / fwidth(uvB * 20.0);
    
    float lineR = 1.0 - min(gridR.x, gridR.y);
    float lineG = 1.0 - min(gridG.x, gridG.y);
    float lineB = 1.0 - min(gridB.x, gridB.y);
    
    fragColor = vec4(clamp(lineR, 0.0, 1.0), clamp(lineG, 0.0, 1.0), clamp(lineB, 0.0, 1.0), 0.4);
}"""
}

# Diccionario de alias canónicos
SHADER_ALIASES = {
    "campo_cuantico": "quantum_field",
    "scanlines_crt": "crt_scanlines",
    "fluido_organico": "organic_fluid",
    "causticas_minerales": "mineral_caustics",
    "raymarched_manifold": "raymarching",
}


# ==============================================================================
# 4. COMPILADOR DE SHADERS Y FALLBACK DETERMINISTA
# ==============================================================================

class ShaderCompiler:
    """
    Compilador y empaquetador de shaders WebGL 2.0 con fallback determinista en 2D Canvas o SVG,
    auto-pausa por IntersectionObserver, contención estricta de CLS y tipografía monumental continua.
    """

    def __init__(self):
        self._shaders = dict(GLSL_SHADER_CATALOG)
        self._aliases = dict(SHADER_ALIASES)

    def _resolve_name(self, name: str) -> str:
        return self._aliases.get(name, name)

    def get_shader(self, name: str) -> Optional[str]:
        resolved = self._resolve_name(name)
        return self._shaders.get(resolved)

    def list_shaders(self) -> List[str]:
        return list(self._shaders.keys())

    # --- Generadores de Fallback Determinista ---

    def generate_deterministic_svg_fallback(
        self,
        shader_name: str,
        width: int = 1200,
        height: int = 800
    ) -> str:
        """
        Genera un activo vectorial SVG matemáticamente puro y determinista
        cuando WebGL 2.0 no está disponible o en modos de ahorro de energía.
        """
        resolved = self._resolve_name(shader_name)

        if resolved in ("raymarching", "raymarched_manifold", "raymarched_atmospheric_field"):
            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback Raymarching">
  <defs>
    <radialGradient id="rm-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.8" />
      <stop offset="35%" stop-color="#1d4ed8" stop-opacity="0.4" />
      <stop offset="70%" stop-color="#0f172a" stop-opacity="0.2" />
      <stop offset="100%" stop-color="#030712" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="rm-sphere" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#93c5fd" />
      <stop offset="45%" stop-color="#2563eb" />
      <stop offset="90%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#020617" />
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#030712" />
  <circle cx="{width * 0.5}" cy="{height * 0.5}" r="{min(width, height) * 0.45}" fill="url(#rm-glow)" />
  <circle cx="{width * 0.5}" cy="{height * 0.5}" r="{min(width, height) * 0.22}" fill="url(#rm-sphere)" />
  <ellipse cx="{width * 0.5}" cy="{height * 0.5}" rx="{min(width, height) * 0.38}" ry="{min(width, height) * 0.12}" stroke="#60a5fa" stroke-width="2" stroke-dasharray="8 6" opacity="0.6" transform="rotate(-15 {width * 0.5} {height * 0.5})" />
</svg>"""

        elif resolved in ("quantum_field", "campo_cuantico"):
            rings = []
            cx = width * 0.5
            cy = height * 0.5
            max_r = min(width, height) * 0.45
            for i in range(1, 7):
                r = (i / 6.0) * max_r
                op = 0.8 - (i * 0.1)
                rings.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="{4*i} {3*i}" opacity="{op:.2f}" />')
            rings_markup = "\n  ".join(rings)

            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback Quantum Field">
  <defs>
    <radialGradient id="qf-rad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#a855f7" stop-opacity="0.75" />
      <stop offset="40%" stop-color="#06b6d4" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#020617" stop-opacity="0" />
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#020617" />
  <circle cx="{cx}" cy="{cy}" r="{max_r}" fill="url(#qf-rad)" />
  {rings_markup}
</svg>"""

        elif resolved in ("crt_scanlines", "scanlines_crt"):
            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback CRT Scanlines">
  <defs>
    <pattern id="crt-scan-pat" width="100%" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="{width}" y2="0" stroke="#00ff66" stroke-width="1" stroke-opacity="0.18" />
    </pattern>
    <radialGradient id="crt-vignette" cx="50%" cy="50%" r="60%">
      <stop offset="50%" stop-color="#000000" stop-opacity="0" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.85" />
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#05140a" />
  <rect width="{width}" height="{height}" fill="url(#crt-scan-pat)" />
  <rect width="{width}" height="{height}" fill="url(#crt-vignette)" />
  <rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="12" stroke="#00ff66" stroke-width="1.5" stroke-opacity="0.4" />
</svg>"""

        elif resolved in ("organic_fluid", "fluido_organico"):
            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback Organic Fluid">
  <defs>
    <linearGradient id="org-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#042f2e" />
      <stop offset="45%" stop-color="#0d9488" stop-opacity="0.8" />
      <stop offset="75%" stop-color="#d97706" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#022c22" />
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#021c17" />
  <path d="M 0,{height*0.4} Q {width*0.25},{height*0.1} {width*0.5},{height*0.5} T {width},{height*0.3} L {width},{height} L 0,{height} Z" fill="url(#org-grad)" opacity="0.85" />
  <path d="M 0,{height*0.65} Q {width*0.35},{height*0.9} {width*0.7},{height*0.6} T {width},{height*0.75} L {width},{height} L 0,{height} Z" fill="#0f766e" opacity="0.6" />
</svg>"""

        elif resolved in ("mineral_caustics", "causticas_minerales"):
            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback Mineral Caustics">
  <defs>
    <linearGradient id="caustic-beam" x1="0%" y1="0%" x2="100%" y2="50%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#38bdf8" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#082f49" stop-opacity="0.1" />
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#031628" />
  <polygon points="{width*0.1},{height*0.2} {width*0.4},{height*0.05} {width*0.7},{height*0.3} {width*0.35},{height*0.6}" fill="url(#caustic-beam)" opacity="0.6" />
  <polygon points="{width*0.5},{height*0.4} {width*0.85},{height*0.25} {width*0.95},{height*0.75} {width*0.6},{height*0.85}" fill="url(#caustic-beam)" opacity="0.5" />
  <path d="M 0,{height*0.5} C {width*0.3},{height*0.2} {width*0.6},{height*0.8} {width},{height*0.4}" stroke="#7dd3fc" stroke-width="3" fill="none" opacity="0.75" />
</svg>"""

        else:
            # Fallback genérico para otros shaders
            return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fallback Shader">
  <defs>
    <linearGradient id="gen-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="50%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#gen-grad)" />
</svg>"""

    def generate_canvas2d_fallback_js(self, shader_name: str) -> str:
        """
        Genera el fragmento JavaScript para renderizar el fallback determinista en 2D Canvas.
        """
        resolved = self._resolve_name(shader_name)

        if resolved in ("raymarching", "raymarched_manifold", "raymarched_atmospheric_field"):
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#030712';
  ctx.fillRect(0, 0, w, h);
  const cx = w * 0.5, cy = h * 0.5;
  const rad = Math.min(w, h) * 0.4;
  const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
  g.addColorStop(0, 'rgba(59, 130, 246, 0.7)');
  g.addColorStop(0.5, 'rgba(29, 78, 216, 0.3)');
  g.addColorStop(1, 'rgba(3, 7, 18, 0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(cx, cy, rad, 0, Math.PI * 2);
  ctx.fill();
}"""
        elif resolved in ("quantum_field", "campo_cuantico"):
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#020617';
  ctx.fillRect(0, 0, w, h);
  const cx = w * 0.5, cy = h * 0.5;
  const maxR = Math.min(w, h) * 0.45;
  for (let i = 1; i <= 6; i++) {
    const r = (i / 6.0) * maxR;
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 1.5;
    ctx.globalAlpha = 0.9 - i * 0.12;
    ctx.setLineDash([6 * i, 4 * i]);
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.globalAlpha = 1.0;
  ctx.setLineDash([]);
}"""
        elif resolved in ("crt_scanlines", "scanlines_crt"):
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#05140a';
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = 'rgba(0, 255, 102, 0.12)';
  for (let y = 0; y < h; y += 4) {
    ctx.fillRect(0, y, w, 1);
  }
  ctx.strokeStyle = 'rgba(0, 255, 102, 0.4)';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(16, 16, w - 32, h - 32);
}"""
        elif resolved in ("organic_fluid", "fluido_organico"):
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#021c17';
  ctx.fillRect(0, 0, w, h);
  const grad = ctx.createLinearGradient(0, 0, w, h);
  grad.addColorStop(0, '#042f2e');
  grad.addColorStop(0.5, '#0d9488');
  grad.addColorStop(1, '#d97706');
  ctx.fillStyle = grad;
  ctx.globalAlpha = 0.75;
  ctx.beginPath();
  ctx.moveTo(0, h * 0.4);
  ctx.quadraticCurveTo(w * 0.3, h * 0.1, w * 0.5, h * 0.5);
  ctx.quadraticCurveTo(w * 0.8, h * 0.9, w, h * 0.3);
  ctx.lineTo(w, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  ctx.fill();
  ctx.globalAlpha = 1.0;
}"""
        elif resolved in ("mineral_caustics", "causticas_minerales"):
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#031628';
  ctx.fillRect(0, 0, w, h);
  const grad = ctx.createRadialGradient(w * 0.5, h * 0.5, 20, w * 0.5, h * 0.5, Math.min(w, h) * 0.5);
  grad.addColorStop(0, 'rgba(56, 189, 248, 0.5)');
  grad.addColorStop(0.7, 'rgba(2, 132, 199, 0.2)');
  grad.addColorStop(1, 'rgba(3, 22, 40, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = 'rgba(125, 211, 252, 0.6)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, h * 0.5);
  ctx.bezierCurveTo(w * 0.3, h * 0.2, w * 0.6, h * 0.8, w, h * 0.4);
  ctx.stroke();
}"""
        else:
            return """
function drawFallback2D(ctx, w, h, t) {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, w, h);
}"""

    def wrap_shader_in_html_canvas(
        self,
        shader_name: str,
        canvas_id: str = "gl-canvas",
        fps_budget: float = 16.6,
        fallback_mode: str = "canvas2d"
    ) -> str:
        """
        Genera el snippet HTML/JS autónomo con WebGL 2.0, fallback determinista en 2D Canvas o SVG,
        auto-pausa por IntersectionObserver y contención estricta contra Cumulative Layout Shift (CLS).
        """
        resolved = self._resolve_name(shader_name)
        source = self.get_shader(resolved)
        if not source:
            raise ValueError(f"Shader '{shader_name}' no existe en el catálogo.")

        # Escapado para incrustar en JavaScript template literal
        escaped_source = source.replace("`", "\\`")
        fallback_fn_js = self.generate_canvas2d_fallback_js(resolved)
        svg_fallback_raw = self.generate_deterministic_svg_fallback(resolved, 1200, 675)
        escaped_svg = svg_fallback_raw.replace("`", "\\`").replace("\n", " ")

        return f"""
<div class="shader-container aleph-webgl-viewport-wrapper" style="position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 0; contain: strict; aspect-ratio: 16 / 9;">
  <canvas id="{canvas_id}" style="width: 100%; height: 100%; display: block;"></canvas>
  <div id="{canvas_id}-svg-fallback" style="display: none; width: 100%; height: 100%;">
    {svg_fallback_raw}
  </div>
</div>
<script>
(() => {{
  const canvas = document.getElementById('{canvas_id}');
  if (!canvas) return;

  const fallbackMode = '{fallback_mode}';
  const svgFallbackEl = document.getElementById('{canvas_id}-svg-fallback');

  {fallback_fn_js}

  function activateFallback() {{
    if (fallbackMode === 'svg' && svgFallbackEl) {{
      canvas.style.display = 'none';
      svgFallbackEl.style.display = 'block';
      return;
    }}
    const ctx2d = canvas.getContext('2d');
    if (!ctx2d) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.floor(canvas.clientWidth * dpr);
    canvas.height = Math.floor(canvas.clientHeight * dpr);
    drawFallback2D(ctx2d, canvas.width, canvas.height, performance.now() * 0.001);
  }}

  // Detección de soporte de WebGL 2.0 y ahorro de batería
  const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gl = canvas.getContext('webgl2', {{ powerPreference: 'low-power', alpha: true }});
  if (!gl || isReducedMotion) {{
    console.warn('WebGL 2.0 no disponible o reduced-motion activo. Desplegando fallback determinista ({fallback_mode}).');
    activateFallback();
    return;
  }}

  const vsSource = `#version 300 es
  in vec2 position;
  void main() {{
    gl_Position = vec4(position, 0.0, 1.0);
  }}`;

  const fsSource = `{escaped_source}`;

  function createShader(gl, type, source) {{
    const s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {{
      console.error(gl.getShaderInfoLog(s));
      gl.deleteShader(s);
      return null;
    }}
    return s;
  }}

  const vs = createShader(gl, gl.VERTEX_SHADER, vsSource);
  const fs = createShader(gl, gl.FRAGMENT_SHADER, fsSource);
  if (!vs || !fs) {{
    console.warn('Fallo al compilar shaders GLSL. Activando fallback determinista.');
    activateFallback();
    return;
  }}

  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {{
    console.error(gl.getProgramInfoLog(prog));
    activateFallback();
    return;
  }}

  const quad = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW);

  const posAttr = gl.getAttribLocation(prog, 'position');
  const uRes = gl.getUniformLocation(prog, 'u_resolution');
  const uTime = gl.getUniformLocation(prog, 'u_time');

  let active = false;
  const obs = new IntersectionObserver(([entry]) => {{
    active = entry.isIntersecting;
    if (active) requestAnimationFrame(render);
  }}, {{ threshold: 0.05 }});
  obs.observe(canvas);

  function resize() {{
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const w = Math.floor(canvas.clientWidth * dpr);
    const h = Math.floor(canvas.clientHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) {{
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }}
  }}

  let start = performance.now();
  function render(now) {{
    if (!active) return;
    resize();
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.enableVertexAttribArray(posAttr);
    gl.vertexAttribPointer(posAttr, 2, gl.FLOAT, false, 0, 0);

    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, (now - start) * 0.001);
    gl.drawArrays(gl.TRIANGLES, 0, 6);

    requestAnimationFrame(render);
  }}
}})();
</script>
"""

    def compile_shader_with_fallback(
        self,
        shader_name: str,
        canvas_id: str = "gl-canvas",
        fallback_mode: str = "canvas2d"
    ) -> Dict[str, Any]:
        """
        Compila el paquete completo de activos de render: código GLSL, envoltura HTML/JS con fallback
        y representación SVG determinista independiente.
        """
        resolved = self._resolve_name(shader_name)
        source = self.get_shader(resolved)
        if not source:
            raise ValueError(f"Shader '{shader_name}' no existe en el catálogo.")

        html_snippet = self.wrap_shader_in_html_canvas(
            shader_name=resolved,
            canvas_id=canvas_id,
            fallback_mode=fallback_mode
        )
        svg_fallback = self.generate_deterministic_svg_fallback(resolved)

        return {
            "shader_name": resolved,
            "glsl_source": source,
            "html_snippet": html_snippet,
            "svg_fallback": svg_fallback,
            "fallback_mode": fallback_mode,
        }

    # --- Procedural Vector Ribbons y Filtros SVG ---

    def generate_procedural_svg_ribbon(
        self,
        width: int = 1200,
        height: int = 400,
        color_start: str = "#3b82f6",
        color_end: str = "#8b5cf6"
    ) -> str:
        """
        Genera una cinta paramétrica Bézier continua en SVG matemáticamente puro.
        """
        p0 = (0, height * 0.5)
        p1 = (width * 0.3, height * 0.1)
        p2 = (width * 0.7, height * 0.9)
        p3 = (width, height * 0.5)

        path_d = f"M {p0[0]} {p0[1]} C {p1[0]} {p1[1]}, {p2[0]} {p2[1]}, {p3[0]} {p3[1]}"

        return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="aleph-ribbon-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{color_start}" stop-opacity="0.8" />
      <stop offset="100%" stop-color="{color_end}" stop-opacity="0.2" />
    </linearGradient>
  </defs>
  <path d="{path_d}" stroke="url(#aleph-ribbon-grad)" stroke-width="48" stroke-linecap="round" />
</svg>"""

    def generate_svg_displacement_filter(self, filter_id: str = "organic-glass", base_freq: float = 0.04) -> str:
        """Genera un filtro SVG de ruido no lineal para texturas y vidrio esmerilado."""
        return f"""<svg style="display:none;" xmlns="http://www.w3.org/2000/svg">
  <filter id="{filter_id}">
    <feTurbulence type="fractalNoise" baseFrequency="{base_freq}" numOctaves="3" result="noise" />
    <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" />
  </filter>
</svg>"""

    # --- Métodos de Conveniencia Tipográfica ---

    def calculate_monumental_clamp(
        self,
        name: str,
        min_size_px: float,
        max_size_px: float,
        min_viewport_px: float = 320.0,
        max_viewport_px: float = 3840.0,
        baseline_unit: int = 4,
        target_lh_ratio: float = 1.15,
        snap_to_baseline: bool = True,
    ) -> MonumentalTypographyToken:
        return calculate_monumental_clamp(
            name=name,
            min_size_px=min_size_px,
            max_size_px=max_size_px,
            min_viewport_px=min_viewport_px,
            max_viewport_px=max_viewport_px,
            baseline_unit=baseline_unit,
            target_lh_ratio=target_lh_ratio,
            snap_to_baseline=snap_to_baseline,
        )

    def generate_swiss_monumental_scale(
        self,
        baseline_unit: int = 4,
        min_viewport_px: float = 320.0,
        max_viewport_px: float = 3840.0,
    ) -> Dict[str, MonumentalTypographyToken]:
        return generate_swiss_monumental_scale(
            baseline_unit=baseline_unit,
            min_viewport_px=min_viewport_px,
            max_viewport_px=max_viewport_px,
        )

    def generate_monumental_typography_css(
        self,
        scale: Optional[Dict[str, MonumentalTypographyToken]] = None,
        baseline_unit: int = 4
    ) -> str:
        return generate_monumental_typography_css(scale=scale, baseline_unit=baseline_unit)


# Alias de interoperabilidad y estándar Aleph
AlephShaderCompiler = ShaderCompiler
