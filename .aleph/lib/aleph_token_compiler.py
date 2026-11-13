"""
.aleph/lib/aleph_token_compiler.py
Aleph Sovereign Design Engine - Token & Perceptual Color Architect.
Estándar: W3C DTCG / OKLCH / APCA-W3 / WCAG 2.2 / Tailwind v4 @theme.

Módulo de producción de alta precisión matemática para:
1. Conversión bidireccional continua: sRGB <-> Linear sRGB <-> CIE XYZ <-> Display-P3 <-> OKLab <-> OKLCH.
2. Mapeo de Gamut Display-P3 y recorte a sRGB preservando estrictamente matiz (hue) y luminancia (L),
   reduciendo progresivamente el croma (c) mediante búsqueda dicotómica hasta la frontera de gamut.
3. Algoritmo APCA (Advanced Perceptual Contrast Algorithm - W3C Silver Draft v0.98G) dependiente de polaridad.
4. Ratio de contraste estándar WCAG 2.2 (L1 + 0.05) / (L2 + 0.05) con matriz de cumplimiento AA/AAA.
5. Generador de rampas de color sigmoideas en OKLCH con monotonía estricta de luminancia y croma modulado.
6. Generador de sombras físicas multicapa basadas en fuente de luz virtual 3D (x, y, z), oclusión ambiental y penumbra.
7. Generador de tipografía fluida clamp() con base en escalas musicales (Minor Third 1.2, Perfect Fifth 1.5, etc.).
8. Exportadores a formato W3C DTCG (Design Tokens Community Group) JSON, CSS Custom Properties y Tailwind v4 @theme.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


# ==============================================================================
# 1. CONSTANTES MATRICIALES Y MATEMÁTICAS (D65 STANDARDS)
# ==============================================================================

# Matrices Oklab (Björn Ottosson, 2020)
# M1: Linear sRGB -> LMS
OKLAB_M1: List[List[float]] = [
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005],
]

# M2: LMS^(1/3) -> OKLab (L, a, b)
OKLAB_M2: List[List[float]] = [
    [0.2104542553, 0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.8086757660],
]

# M2_INV: OKLab (L, a, b) -> LMS^(1/3)
OKLAB_M2_INV: List[List[float]] = [
    [1.0000000000, 0.3963377774, 0.2158037573],
    [1.0000000000, -0.1055613458, -0.0638541728],
    [1.0000000000, -0.0894841775, -1.2914855480],
]

# M1_INV: LMS -> Linear sRGB
OKLAB_M1_INV: List[List[float]] = [
    [4.0767416621, -3.3077115913, 0.2309699292],
    [-1.2684380046, 2.6097574011, -0.3413193965],
    [-0.0041960863, -0.7034186147, 1.7076147010],
]

# Matriz Linear sRGB -> CIE XYZ (D65)
SRGB_TO_XYZ_MATRIX: List[List[float]] = [
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
]

# Matriz CIE XYZ (D65) -> Linear sRGB
XYZ_TO_SRGB_MATRIX: List[List[float]] = [
    [3.2404542, -1.5371385, -0.4985314],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0556434, -0.2040259, 1.0572252],
]

# Matriz Linear Display-P3 -> CIE XYZ (D65)
P3_TO_XYZ_MATRIX: List[List[float]] = [
    [0.4865709486482162, 0.26566769316909306, 0.1982172852343625],
    [0.2289745640697488, 0.6917393478950682, 0.07928608803518296],
    [0.0000000000000000, 0.04511338185834892, 1.043944368900976],
]

# Matriz CIE XYZ (D65) -> Linear Display-P3
XYZ_TO_P3_MATRIX: List[List[float]] = [
    [2.493496911941425, -0.9313836179191239, -0.40271078445071684],
    [-0.8294889695615747, 1.7626640603183463, 0.023624685841943577],
    [0.03584583024378447, -0.07617238926804182, 0.9568845240076872],
]

# Matriz directa Linear Display-P3 -> Linear sRGB (CSS Color 4)
P3_TO_SRGB_DIRECT: List[List[float]] = [
    [1.22474526, -0.22490564, 0.00000000],
    [-0.04205793, 1.04208256, 0.00000000],
    [-0.01964228, -0.07865509, 1.09853736],
]

# Matriz directa Linear sRGB -> Linear Display-P3
SRGB_TO_P3_DIRECT: List[List[float]] = [
    [0.82259287, 0.17753461, 0.00000000],
    [0.03319946, 0.96678218, 0.00000000],
    [0.01708536, 0.07239583, 0.91030139],
]

# Constantes APCA-W3 v0.98G
APCA_SR_CO = 0.2126729
APCA_SG_CO = 0.7151522
APCA_SB_CO = 0.0721750
APCA_MAIN_TRC = 2.4
APCA_BLK_THRS = 0.022
APCA_BLK_CLMP = 1.414
APCA_SCALE_BOW = 1.14
APCA_SCALE_WOB = 1.14
APCA_NORM_BG = 0.56
APCA_NORM_TXT = 0.62
APCA_REV_BG = 0.65
APCA_REV_TXT = 0.57
APCA_LO_CLMP = 0.1
APCA_LO_THRS = 0.035991


def _mat_vec_mul(m: List[List[float]], v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Multiplicación vector-matriz 3x3 optimizada."""
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def srgb_transfer_to_linear(c: float) -> float:
    """Aplica la función de transferencia sRGB inversa para obtener energía lineal."""
    c_clamped = max(0.0, min(1.0, c))
    if c_clamped <= 0.04045:
        return c_clamped / 12.92
    return ((c_clamped + 0.055) / 1.055) ** 2.4


def linear_to_srgb_transfer(c: float) -> float:
    """Aplica la función de transferencia sRGB directa (gamma) desde energía lineal."""
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (max(0.0, c) ** (1.0 / 2.4)) - 0.055


# ==============================================================================
# 2. MODELOS DE COLOR Y ESTRUCTURAS DE DATOS
# ==============================================================================

@dataclass(frozen=True)
class RGBColor:
    """Color sRGB no lineal estándar con canales en [0.0, 1.0] y alpha en [0.0, 1.0]."""
    r: float
    g: float
    b: float
    a: float = 1.0

    @classmethod
    def from_hex(cls, hex_code: str) -> RGBColor:
        """Crea RGBColor a partir de string hexadecimal (#rgb, #rrggbb, #rrggbbaa)."""
        h = hex_code.lstrip("#").strip()
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        if len(h) == 4:
            h = "".join([c * 2 for c in h])
        if len(h) == 6:
            r = int(h[0:2], 16) / 255.0
            g = int(h[2:4], 16) / 255.0
            b = int(h[4:6], 16) / 255.0
            return cls(r=r, g=g, b=b, a=1.0)
        elif len(h) == 8:
            r = int(h[0:2], 16) / 255.0
            g = int(h[2:4], 16) / 255.0
            b = int(h[4:6], 16) / 255.0
            a = int(h[6:8], 16) / 255.0
            return cls(r=r, g=g, b=b, a=a)
        raise ValueError(f"Código hexadecimal no válido: '{hex_code}'")

    @classmethod
    def from_rgb255(cls, r: int, g: int, b: int, a: float = 1.0) -> RGBColor:
        """Crea RGBColor a partir de enteros 0-255."""
        return cls(r=r / 255.0, g=g / 255.0, b=b / 255.0, a=a)

    def to_rgb255(self) -> Tuple[int, int, int]:
        """Convierte a tupla entera (0-255, 0-255, 0-255)."""
        ir = int(round(max(0.0, min(1.0, self.r)) * 255.0))
        ig = int(round(max(0.0, min(1.0, self.g)) * 255.0))
        ib = int(round(max(0.0, min(1.0, self.b)) * 255.0))
        return ir, ig, ib

    def to_hex(self, include_alpha: bool = False) -> str:
        """Serializa a hexadecimal #rrggbb o #rrggbbaa."""
        ir, ig, ib = self.to_rgb255()
        if include_alpha or self.a < 0.999:
            ia = int(round(max(0.0, min(1.0, self.a)) * 255.0))
            return f"#{ir:02x}{ig:02x}{ib:02x}{ia:02x}"
        return f"#{ir:02x}{ig:02x}{ib:02x}"

    def to_linear(self) -> LinearRGBColor:
        """Convierte sRGB no lineal a Linear sRGB."""
        return LinearRGBColor(
            r=srgb_transfer_to_linear(self.r),
            g=srgb_transfer_to_linear(self.g),
            b=srgb_transfer_to_linear(self.b),
            a=self.a,
        )

    def to_oklab(self) -> OklabColor:
        """Convierte sRGB -> Linear sRGB -> OKLab."""
        return self.to_linear().to_oklab()

    def to_oklch(self) -> OklchColor:
        """Convierte sRGB -> OKLCH cilíndrico."""
        return self.to_oklab().to_oklch()

    def to_display_p3(self) -> DisplayP3Color:
        """Convierte sRGB a Display-P3 no lineal."""
        lin_srgb = self.to_linear()
        lin_p3_r, lin_p3_g, lin_p3_b = _mat_vec_mul(
            SRGB_TO_P3_DIRECT, (lin_srgb.r, lin_srgb.g, lin_srgb.b)
        )
        return DisplayP3Color(
            r=linear_to_srgb_transfer(lin_p3_r),
            g=linear_to_srgb_transfer(lin_p3_g),
            b=linear_to_srgb_transfer(lin_p3_b),
            a=self.a,
        )


@dataclass(frozen=True)
class LinearRGBColor:
    """Color sRGB en espacio de energía lineal (D65)."""
    r: float
    g: float
    b: float
    a: float = 1.0

    def to_srgb(self) -> RGBColor:
        """Convierte Linear sRGB a sRGB estándar con gamma aplicada."""
        return RGBColor(
            r=linear_to_srgb_transfer(self.r),
            g=linear_to_srgb_transfer(self.g),
            b=linear_to_srgb_transfer(self.b),
            a=self.a,
        )

    def to_xyz(self) -> XYZColor:
        """Convierte Linear sRGB a CIE XYZ (D65)."""
        x, y, z = _mat_vec_mul(SRGB_TO_XYZ_MATRIX, (self.r, self.g, self.b))
        return XYZColor(x=x, y=y, z=z, a=self.a)

    def to_oklab(self) -> OklabColor:
        """Convierte Linear sRGB a OKLab (L, a, b)."""
        l_lms, m_lms, s_lms = _mat_vec_mul(OKLAB_M1, (self.r, self.g, self.b))

        # Raíz cúbica preservando signo para estabilidad matemática en periferia
        l_prime = math.copysign(abs(l_lms) ** (1.0 / 3.0), l_lms) if l_lms != 0.0 else 0.0
        m_prime = math.copysign(abs(m_lms) ** (1.0 / 3.0), m_lms) if m_lms != 0.0 else 0.0
        s_prime = math.copysign(abs(s_lms) ** (1.0 / 3.0), s_lms) if s_lms != 0.0 else 0.0

        L, a_val, b_val = _mat_vec_mul(OKLAB_M2, (l_prime, m_prime, s_prime))
        return OklabColor(L=L, a=a_val, b=b_val, a_alpha=self.a)

    def to_oklch(self) -> OklchColor:
        """Convierte Linear sRGB a OKLCH cilíndrico."""
        return self.to_oklab().to_oklch()

    def relative_luminance(self) -> float:
        """Calcula la luminancia relativa estándar Y según ITU-R BT.709 / WCAG 2.2."""
        return 0.2126 * self.r + 0.7152 * self.g + 0.0722 * self.b


@dataclass(frozen=True)
class XYZColor:
    """Color en espacio CIE 1931 XYZ con punto blanco D65."""
    x: float
    y: float
    z: float
    a: float = 1.0

    def to_linear_srgb(self) -> LinearRGBColor:
        """Convierte CIE XYZ a Linear sRGB."""
        r, g, b = _mat_vec_mul(XYZ_TO_SRGB_MATRIX, (self.x, self.y, self.z))
        return LinearRGBColor(r=r, g=g, b=b, a=self.a)

    def to_linear_p3(self) -> LinearP3Color:
        """Convierte CIE XYZ a Linear Display-P3."""
        r, g, b = _mat_vec_mul(XYZ_TO_P3_MATRIX, (self.x, self.y, self.z))
        return LinearP3Color(r=r, g=g, b=b, a=self.a)


@dataclass(frozen=True)
class DisplayP3Color:
    """Color Display-P3 con curva de transferencia sRGB."""
    r: float
    g: float
    b: float
    a: float = 1.0

    def to_linear_p3(self) -> LinearP3Color:
        """Convierte Display-P3 a Linear Display-P3."""
        return LinearP3Color(
            r=srgb_transfer_to_linear(self.r),
            g=srgb_transfer_to_linear(self.g),
            b=srgb_transfer_to_linear(self.b),
            a=self.a,
        )

    def to_srgb(self) -> RGBColor:
        """Convierte Display-P3 a sRGB estándar (sin gamut clipping)."""
        return self.to_linear_p3().to_linear_srgb().to_srgb()

    def to_oklch(self) -> OklchColor:
        """Convierte Display-P3 a OKLCH cilíndrico."""
        return self.to_linear_p3().to_linear_srgb().to_oklch()


@dataclass(frozen=True)
class LinearP3Color:
    """Color Display-P3 en espacio de energía lineal."""
    r: float
    g: float
    b: float
    a: float = 1.0

    def to_display_p3(self) -> DisplayP3Color:
        """Convierte Linear P3 a Display-P3 estándar."""
        return DisplayP3Color(
            r=linear_to_srgb_transfer(self.r),
            g=linear_to_srgb_transfer(self.g),
            b=linear_to_srgb_transfer(self.b),
            a=self.a,
        )

    def to_xyz(self) -> XYZColor:
        """Convierte Linear P3 a CIE XYZ."""
        x, y, z = _mat_vec_mul(P3_TO_XYZ_MATRIX, (self.r, self.g, self.b))
        return XYZColor(x=x, y=y, z=z, a=self.a)

    def to_linear_srgb(self) -> LinearRGBColor:
        """Convierte Linear P3 directamente a Linear sRGB."""
        r, g, b = _mat_vec_mul(P3_TO_SRGB_DIRECT, (self.r, self.g, self.b))
        return LinearRGBColor(r=r, g=g, b=b, a=self.a)


@dataclass(frozen=True)
class OklabColor:
    """Coordenadas rectangulares en espacio perceptual OKLab (L, a, b)."""
    L: float  # Luminancia perceptual [0.0, 1.0]
    a: float  # Eje verde-rojo
    b: float  # Eje azul-amarillo
    a_alpha: float = 1.0

    def to_oklch(self) -> OklchColor:
        """Convierte coordenadas rectangulares OKLab (L, a, b) a cilíndricas OKLCH (L, c, h)."""
        c = math.sqrt(self.a * self.a + self.b * self.b)
        h_rad = math.atan2(self.b, self.a)
        h_deg = math.degrees(h_rad)
        if h_deg < 0.0:
            h_deg += 360.0
        # Normalizar caso acromático
        if c < 1e-6:
            h_deg = 0.0
        return OklchColor(L=self.L, c=c, h=h_deg, alpha=self.a_alpha)

    def to_linear_srgb(self) -> LinearRGBColor:
        """Convierte OKLab a Linear sRGB invirtiendo las matrices M2 y M1."""
        l_prime, m_prime, s_prime = _mat_vec_mul(OKLAB_M2_INV, (self.L, self.a, self.b))

        l_lms = l_prime**3
        m_lms = m_prime**3
        s_lms = s_prime**3

        r, g, b = _mat_vec_mul(OKLAB_M1_INV, (l_lms, m_lms, s_lms))
        return LinearRGBColor(r=r, g=g, b=b, a=self.a_alpha)

    def to_srgb(self) -> RGBColor:
        """Convierte OKLab directamente a sRGB."""
        return self.to_linear_srgb().to_srgb()


@dataclass(frozen=True)
class OklchColor:
    """Coordenadas cilíndricas en espacio perceptual OKLCH (L, c, h)."""
    L: float      # Luminancia [0.0, 1.0]
    c: float      # Croma [0.0, ~0.4]
    h: float      # Matiz en grados [0.0, 360.0)
    alpha: float = 1.0

    def __post_init__(self):
        # Asegurar invariantes cilíndricas
        h_norm = self.h % 360.0
        if h_norm < 0.0:
            h_norm += 360.0
        object.__setattr__(self, "h", h_norm)
        object.__setattr__(self, "c", max(0.0, self.c))
        object.__setattr__(self, "L", max(0.0, min(1.0, self.L)))

    def to_oklab(self) -> OklabColor:
        """Convierte OKLCH cilíndrico a OKLab rectangular."""
        h_rad = math.radians(self.h)
        a_val = self.c * math.cos(h_rad)
        b_val = self.c * math.sin(h_rad)
        return OklabColor(L=self.L, a=a_val, b=b_val, a_alpha=self.alpha)

    def to_srgb(self) -> RGBColor:
        """Convierte OKLCH a sRGB estándar (sin recortar gamut si está fuera)."""
        return self.to_oklab().to_srgb()

    def to_css(self) -> str:
        """Formatea como expresión CSS moderna: oklch(L c h / alpha)."""
        if self.alpha < 0.999:
            return f"oklch({self.L:.4f} {self.c:.4f} {self.h:.2f} / {self.alpha:.2f})"
        return f"oklch({self.L:.4f} {self.c:.4f} {self.h:.2f})"

    def is_in_srgb_gamut(self, tolerance: float = 1e-4) -> bool:
        """Determina si este color cae estrictamente dentro del gamut sRGB."""
        srgb = self.to_srgb()
        eps = tolerance
        return (
            (-eps <= srgb.r <= 1.0 + eps)
            and (-eps <= srgb.g <= 1.0 + eps)
            and (-eps <= srgb.b <= 1.0 + eps)
        )

    def is_in_p3_gamut(self, tolerance: float = 1e-4) -> bool:
        """Determina si este color cae dentro del gamut Display-P3."""
        lin_srgb = self.to_oklab().to_linear_srgb()
        p3_r, p3_g, p3_b = _mat_vec_mul(
            SRGB_TO_P3_DIRECT, (lin_srgb.r, lin_srgb.g, lin_srgb.b)
        )
        eps = tolerance
        return (
            (-eps <= p3_r <= 1.0 + eps)
            and (-eps <= p3_g <= 1.0 + eps)
            and (-eps <= p3_b <= 1.0 + eps)
        )

    def clip_to_srgb_gamut(
        self,
        max_iterations: int = 25,
        tolerance: float = 1e-4
    ) -> Tuple[RGBColor, OklchColor]:
        """
        Recorta este color al gamut sRGB preservando estrictamente matiz (h) y luminancia (L).
        Aplica búsqueda binaria reduciendo croma progresivamente hacia 0 hasta la frontera sRGB.
        Retorna (color_srgb_final, oklch_recortado).
        """
        return clip_oklch_to_srgb(self, max_iterations=max_iterations, tolerance=tolerance)


# ==============================================================================
# 3. ALGORITMO DE MAPEO Y RECORTE DE GAMUT A sRGB
# ==============================================================================

def clip_oklch_to_srgb(
    oklch: OklchColor,
    max_iterations: int = 25,
    tolerance: float = 1e-4
) -> Tuple[RGBColor, OklchColor]:
    """
    Algoritmo estándar CSS Color 4 para mapeo de gamut hacia sRGB:
    - Mantiene Luminancia L y Matiz h constantes.
    - Reduce croma c mediante búsqueda dicotómica si está fuera de gamut.
    - Retorna el RGBColor acotado a [0.0, 1.0] y el OklchColor ajustado.
    """
    raw_srgb = oklch.to_srgb()
    if oklch.is_in_srgb_gamut(tolerance=tolerance):
        # Color ya está dentro del gamut sRGB
        r_clamped = max(0.0, min(1.0, raw_srgb.r))
        g_clamped = max(0.0, min(1.0, raw_srgb.g))
        b_clamped = max(0.0, min(1.0, raw_srgb.b))
        return RGBColor(r=r_clamped, g=g_clamped, b=b_clamped, a=oklch.alpha), oklch

    # Búsqueda binaria sobre el croma en el intervalo [0, c_orig]
    low_c = 0.0
    high_c = oklch.c
    best_c = 0.0

    for _ in range(max_iterations):
        mid_c = (low_c + high_c) / 2.0
        candidate_oklch = OklchColor(L=oklch.L, c=mid_c, h=oklch.h, alpha=oklch.alpha)
        if candidate_oklch.is_in_srgb_gamut(tolerance=tolerance):
            best_c = mid_c
            low_c = mid_c  # Intentar obtener mayor croma
        else:
            high_c = mid_c  # Fuera de gamut, reducir croma

        if abs(high_c - low_c) < 1e-5:
            break

    clamped_oklch = OklchColor(L=oklch.L, c=best_c, h=oklch.h, alpha=oklch.alpha)
    final_srgb = clamped_oklch.to_srgb()
    final_rgb = RGBColor(
        r=max(0.0, min(1.0, final_srgb.r)),
        g=max(0.0, min(1.0, final_srgb.g)),
        b=max(0.0, min(1.0, final_srgb.b)),
        a=oklch.alpha,
    )
    return final_rgb, clamped_oklch


def clip_p3_to_srgb(p3_color: DisplayP3Color) -> RGBColor:
    """Convierte un color Display-P3 a sRGB recortando el gamut preservando matiz en OKLCH."""
    oklch = p3_color.to_oklch()
    final_rgb, _ = clip_oklch_to_srgb(oklch)
    return final_rgb


# ==============================================================================
# 4. APCA (ADVANCED PERCEPTUAL CONTRAST ALGORITHM - W3C SILVER v0.98G)
# ==============================================================================

@dataclass(frozen=True)
class APCAResult:
    """Resultado formal del algoritmo APCA W3C."""
    lc: float                   # Puntaje de contraste firmado (-108 a +106 aprox.)
    abs_lc: float               # Magnitud absoluta |Lc|
    polarity: str               # "dark-on-light" (positivo) o "light-on-dark" (negativo)
    y_text: float               # Luminancia perceptual del texto
    y_bg: float                 # Luminancia perceptual del fondo
    is_body_text_accessible: bool      # Apto para texto de lectura normal (>= 60 Lc)
    is_fluent_accessible: bool         # Apto para lectura fluida prolongada (>= 75 Lc)
    is_large_display_accessible: bool  # Apto para títulos grandes o displays (>= 45 Lc)
    recommended_min_px: float          # Tamaño mínimo de fuente sugerido en px


def _apca_perceptual_y(color: RGBColor) -> float:
    """Calcula la luminancia Y compensada para APCA considerando flare de pantalla."""
    r_pow = max(0.0, min(1.0, color.r)) ** APCA_MAIN_TRC
    g_pow = max(0.0, min(1.0, color.g)) ** APCA_MAIN_TRC
    b_pow = max(0.0, min(1.0, color.b)) ** APCA_MAIN_TRC

    y = APCA_SR_CO * r_pow + APCA_SG_CO * g_pow + APCA_SB_CO * b_pow

    # Flare soft-clamping en negros profundos
    if y < APCA_BLK_THRS:
        y += (APCA_BLK_THRS - y) ** APCA_BLK_CLMP
    return y


def calculate_apca(text_color: RGBColor, bg_color: RGBColor) -> APCAResult:
    """
    Calcula el puntaje de contraste APCA Lc entre texto y fondo.
    Sigue rigurosamente la especificación APCA-W3 v0.98G.
    """
    y_txt = _apca_perceptual_y(text_color)
    y_bg = _apca_perceptual_y(bg_color)

    delta_y = abs(y_bg - y_txt)

    # Evaluación de polaridad y cálculo de SAPCA
    if y_bg > y_txt:
        # Polaridad normal: texto oscuro sobre fondo claro (BoW: Black on White)
        sapca = (y_bg**APCA_NORM_BG - y_txt**APCA_NORM_TXT) * APCA_SCALE_BOW
        polarity = "dark-on-light"
    else:
        # Polaridad inversa: texto claro sobre fondo oscuro (WoB: White on Black)
        sapca = (y_bg**APCA_REV_BG - y_txt**APCA_REV_TXT) * APCA_SCALE_WOB
        polarity = "light-on-dark"

    # Soft clamp para contrastes por debajo del umbral de ruido visual
    if delta_y < APCA_LO_THRS:
        lc = 0.0
    elif sapca > APCA_LO_CLMP:
        lc = (sapca - APCA_LO_CLMP) * 100.0
    elif sapca < -APCA_LO_CLMP:
        lc = (sapca + APCA_LO_CLMP) * 100.0
    else:
        lc = 0.0

    abs_lc = abs(lc)

    # Determinación de accesibilidad según estándares APCA
    body_acc = abs_lc >= 60.0
    fluent_acc = abs_lc >= 75.0
    large_acc = abs_lc >= 45.0

    # Estimación de tamaño mínimo de texto según Lc
    if abs_lc >= 90.0:
        min_px = 12.0
    elif abs_lc >= 75.0:
        min_px = 14.0
    elif abs_lc >= 60.0:
        min_px = 18.0
    elif abs_lc >= 45.0:
        min_px = 24.0
    elif abs_lc >= 30.0:
        min_px = 36.0
    else:
        min_px = 999.0  # Inaccesible para texto estándar

    return APCAResult(
        lc=lc,
        abs_lc=abs_lc,
        polarity=polarity,
        y_text=y_txt,
        y_bg=y_bg,
        is_body_text_accessible=body_acc,
        is_fluent_accessible=fluent_acc,
        is_large_display_accessible=large_acc,
        recommended_min_px=min_px,
    )


def apca_contrast(text_hex: str, bg_hex: str) -> float:
    """Helper directo que retorna el puntaje Lc firmado dados dos códigos hex."""
    txt = RGBColor.from_hex(text_hex)
    bg = RGBColor.from_hex(bg_hex)
    return calculate_apca(txt, bg).lc


# ==============================================================================
# 5. RATIO DE CONTRASTE WCAG 2.2 ESTÁNDAR
# ==============================================================================

@dataclass(frozen=True)
class WCAGResult:
    """Resultado de evaluación de contraste WCAG 2.2."""
    ratio: float
    l1: float
    l2: float
    aa_normal: bool      # Ratio >= 4.5
    aa_large: bool       # Ratio >= 3.0 (>= 18pt o >= 14pt bold)
    aaa_normal: bool     # Ratio >= 7.0
    aaa_large: bool      # Ratio >= 4.5
    ui_component: bool   # Ratio >= 3.0 (WCAG 2.1+ SC 1.4.11)


def calculate_wcag_contrast(fg_color: RGBColor, bg_color: RGBColor) -> WCAGResult:
    """
    Calcula el ratio de contraste estándar WCAG 2.2 (L1 + 0.05) / (L2 + 0.05).
    L1 es la luminancia relativa del color más claro, L2 del más oscuro.
    """
    lum_fg = fg_color.to_linear().relative_luminance()
    lum_bg = bg_color.to_linear().relative_luminance()

    l1 = max(lum_fg, lum_bg)
    l2 = min(lum_fg, lum_bg)

    ratio = (l1 + 0.05) / (l2 + 0.05)

    return WCAGResult(
        ratio=ratio,
        l1=l1,
        l2=l2,
        aa_normal=(ratio >= 4.5),
        aa_large=(ratio >= 3.0),
        aaa_normal=(ratio >= 7.0),
        aaa_large=(ratio >= 4.5),
        ui_component=(ratio >= 3.0),
    )


def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """Helper directo que calcula el ratio WCAG 2.2 entre dos colores hexadecimales."""
    fg = RGBColor.from_hex(fg_hex)
    bg = RGBColor.from_hex(bg_hex)
    return calculate_wcag_contrast(fg, bg).ratio


# ==============================================================================
# 6. GENERADOR DE RAMPAS DE COLOR SIGMOIDEAS EN OKLCH
# ==============================================================================

STANDARD_RAMP_STEPS: List[int] = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]


@dataclass(frozen=True)
class ColorRampStep:
    """Un escalón específico dentro de una rampa perceptual OKLCH."""
    step: int
    oklch: OklchColor
    rgb: RGBColor
    hex: str
    luminance_wcag: float
    apca_vs_white: float
    apca_vs_black: float


@dataclass
class ColorRamp:
    """Rampa tonal completa de 11 pasos generada en OKLCH."""
    name: str
    base_hue: float
    steps: Dict[int, ColorRampStep] = field(default_factory=dict)

    @property
    def is_luminance_monotonic(self) -> bool:
        """Verifica formalmente que la luminancia perceptual descienda estrictamente paso a paso."""
        sorted_steps = sorted(self.steps.keys())
        for i in range(len(sorted_steps) - 1):
            s1 = sorted_steps[i]
            s2 = sorted_steps[i + 1]
            if self.steps[s1].oklch.L <= self.steps[s2].oklch.L:
                return False
        return True

    def to_dict(self) -> Dict[str, str]:
        """Exporta mapeo step -> hex string."""
        return {str(s): step_obj.hex for s, step_obj in self.steps.items()}


def _sigmoid_luminance(
    t: float,
    l_min: float = 0.18,
    l_max: float = 0.97,
    k: float = 4.5
) -> float:
    """
    Función logística sigmoidea normalizada para luminancia L(t) en [l_min, l_max].
    Garantiza matemáticamente dL/dt < 0 (monotonía decreciente estricta).
    """
    r0 = 1.0 / (1.0 + math.exp(k * (0.0 - 0.5)))
    r1 = 1.0 / (1.0 + math.exp(k * (1.0 - 0.5)))
    rt = 1.0 / (1.0 + math.exp(k * (t - 0.5)))
    norm = (rt - r1) / (r0 - r1)
    return l_min + norm * (l_max - l_min)


def _modulated_chroma(
    t: float,
    max_chroma: float = 0.18,
    c_floor: float = 0.015
) -> float:
    """
    Modulación de croma campana: máximo en tonos medios (t=0.5 / paso 500),
    atenuándose suavemente hacia los extremos luminosos y oscuros para respetar la física del gamut.
    """
    factor = math.sin(math.pi * t) ** 0.85
    return c_floor + (max_chroma - c_floor) * factor


def generate_sigmoid_oklch_ramp(
    name: str,
    base_hue: float,
    max_chroma: float = 0.18,
    steps: Optional[List[int]] = None,
    l_min: float = 0.18,
    l_max: float = 0.97,
    k: float = 4.5,
) -> ColorRamp:
    """
    Genera una rampa de color completa de alta calidad en OKLCH:
    - Utiliza curva sigmoidea normalizada para monotonía estricta de luminancia.
    - Modula el croma en campana física para máxima saturación en medios sin reventar extremos.
    - Aplica recorte automático a sRGB preservando matiz.
    """
    target_steps = steps if steps is not None else STANDARD_RAMP_STEPS
    ramp = ColorRamp(name=name, base_hue=base_hue)
    white = RGBColor(r=1.0, g=1.0, b=1.0)
    black = RGBColor(r=0.0, g=0.0, b=0.0)

    n = len(target_steps)
    for idx, step_val in enumerate(target_steps):
        t = idx / (n - 1) if n > 1 else 0.5
        L = _sigmoid_luminance(t, l_min=l_min, l_max=l_max, k=k)
        c = _modulated_chroma(t, max_chroma=max_chroma)

        raw_oklch = OklchColor(L=L, c=c, h=base_hue)
        clipped_rgb, final_oklch = clip_oklch_to_srgb(raw_oklch)

        # Cálculos de contraste
        lum_wcag = clipped_rgb.to_linear().relative_luminance()
        apca_white = calculate_apca(clipped_rgb, white).lc
        apca_black = calculate_apca(clipped_rgb, black).lc

        step_obj = ColorRampStep(
            step=step_val,
            oklch=final_oklch,
            rgb=clipped_rgb,
            hex=clipped_rgb.to_hex(),
            luminance_wcag=lum_wcag,
            apca_vs_white=apca_white,
            apca_vs_black=apca_black,
        )
        ramp.steps[step_val] = step_obj

    return ramp


# ==============================================================================
# 7. GENERADOR DE SOMBRAS FÍSICAS MULTICAPA (VIRTUAL LIGHT SOURCE)
# ==============================================================================

@dataclass(frozen=True)
class LightSource3D:
    """Posición 3D de fuente de luz virtual relativa al plano de interfaz."""
    x: float = 0.0      # Desplazamiento lateral (positivo hacia la derecha)
    y: float = -1.0     # Desplazamiento vertical (negativo luz cenital superior)
    z: float = 2.0      # Altura/distancia sobre el plano Z (determina penumbra)


@dataclass(frozen=True)
class ShadowLayer:
    """Capa individual de sombra física calculada."""
    x_offset_px: float
    y_offset_px: float
    blur_radius_px: float
    spread_radius_px: float
    color_rgba: str
    layer_type: str  # "ambient_occlusion", "key_umbra", "penumbra", "ambient_diffuse"


@dataclass
class PhysicalShadow:
    """Sombra compuesta multicapa realista."""
    name: str
    elevation_px: float
    layers: List[ShadowLayer] = field(default_factory=list)

    def to_css_box_shadow(self) -> str:
        """Serializa las capas a una regla CSS box-shadow completa."""
        chunks = []
        for l in self.layers:
            chunks.append(
                f"{l.x_offset_px:.1f}px {l.y_offset_px:.1f}px {l.blur_radius_px:.1f}px "
                f"{l.spread_radius_px:.1f}px {l.color_rgba}"
            )
        return ", ".join(chunks)


def generate_physical_shadow(
    name: str,
    elevation_px: float,
    light: Optional[LightSource3D] = None,
    tint_rgb: Optional[Tuple[int, int, int]] = None,
    num_layers: int = 4,
    base_alpha: float = 0.08,
) -> PhysicalShadow:
    """
    Genera un sistema de sombras físicas realista multicapa:
    1. Oclusión ambiental difusa (contacto cercano, desenfoque bajo, alta definición).
    2. Sombra umbra/directa dependiente del vector de luz.
    3. Penumbra con dispersión progresiva según la altura Z.
    """
    l_src = light if light is not None else LightSource3D()
    tr, tg, tb = tint_rgb if tint_rgb is not None else (15, 23, 42)  # Slate-900 por default

    # Dirección normalizada de la luz en el plano XY
    dir_x = l_src.x / max(0.5, l_src.z)
    dir_y = (-l_src.y) / max(0.5, l_src.z)  # Invertir Y porque luz arriba proyecta sombra abajo

    shadow = PhysicalShadow(name=name, elevation_px=elevation_px)

    # Capa 1: Oclusión Ambiental de Contacto (AO)
    ao_offset_y = max(1.0, elevation_px * 0.1)
    ao_blur = max(2.0, elevation_px * 0.25)
    ao_alpha = min(0.35, base_alpha * 2.2)
    shadow.layers.append(
        ShadowLayer(
            x_offset_px=0.0,
            y_offset_px=round(ao_offset_y, 1),
            blur_radius_px=round(ao_blur, 1),
            spread_radius_px=0.0,
            color_rgba=f"rgba({tr}, {tg}, {tb}, {ao_alpha:.3f})",
            layer_type="ambient_occlusion",
        )
    )

    # Capas intermedias y penumbra (distribución geométrica)
    remaining_layers = max(1, num_layers - 1)
    for i in range(1, remaining_layers + 1):
        progress = i / remaining_layers
        # Desplazamiento y dispersión crecen no-linealmente con la distancia
        layer_x = dir_x * elevation_px * (progress ** 1.1)
        layer_y = dir_y * elevation_px * (progress ** 1.1)
        layer_blur = (elevation_px * 1.5) * (progress ** 1.6) + 2.0
        # Spread negativo suave en capas exteriores para evitar halos turbios
        layer_spread = -(elevation_px * 0.1) * progress if i > 1 else 0.0
        # Disminución de opacidad conforme la penumbra se expande
        layer_alpha = (base_alpha * 1.5) * (1.0 - progress * 0.55) / remaining_layers

        l_type = "key_umbra" if i == 1 else ("penumbra" if i < remaining_layers else "ambient_diffuse")
        shadow.layers.append(
            ShadowLayer(
                x_offset_px=round(layer_x, 1),
                y_offset_px=round(layer_y, 1),
                blur_radius_px=round(layer_blur, 1),
                spread_radius_px=round(layer_spread, 1),
                color_rgba=f"rgba({tr}, {tg}, {tb}, {layer_alpha:.3f})",
                layer_type=l_type,
            )
        )

    return shadow


# ==============================================================================
# 8. GENERADOR DE TIPOGRAFÍA FLUIDA clamp() CON ESCALAS MUSICALES
# ==============================================================================

class MusicalScale(float, Enum):
    """Ratios de intervalos consonantes armónicos y geométricos."""
    MINOR_SECOND = 1.067
    MAJOR_SECOND = 1.125
    MINOR_THIRD = 1.200
    MAJOR_THIRD = 1.250
    PERFECT_FOURTH = 1.333
    AUGMENTED_FOURTH = 1.414
    PERFECT_FIFTH = 1.500
    GOLDEN_RATIO = 1.618


@dataclass(frozen=True)
class FluidTypographyToken:
    """Definición matemática de un token tipográfico responsivo en CSS clamp()."""
    name: str
    step_index: int
    min_px: float
    max_px: float
    min_viewport_px: float
    max_viewport_px: float
    slope_vw: float
    intercept_rem: float
    min_rem: float
    max_rem: float
    clamp_expr: str

    def eval_at(self, viewport_w: float) -> float:
        """Evalúa el tamaño resultante en px para un ancho de viewport arbitrario."""
        w_clamped = max(self.min_viewport_px, min(self.max_viewport_px, viewport_w))
        slope = (self.max_px - self.min_px) / (self.max_viewport_px - self.min_viewport_px)
        intercept = self.min_px - slope * self.min_viewport_px
        val = slope * w_clamped + intercept
        return max(self.min_px, min(self.max_px, val))


def calculate_fluid_clamp(
    name: str,
    min_px: float,
    max_px: float,
    min_viewport_px: float = 320.0,
    max_viewport_px: float = 1280.0,
    step_index: int = 0,
) -> FluidTypographyToken:
    """
    Calcula la función analítica CSS clamp() linealmente responsiva entre dos límites de viewport.
    clamp(min_rem, intercept_rem + slope_vw, max_rem).
    """
    if min_viewport_px >= max_viewport_px:
        raise ValueError("min_viewport_px debe ser estrictamente menor que max_viewport_px")

    min_rem = min_px / 16.0
    max_rem = max_px / 16.0

    if math.isclose(min_px, max_px, abs_tol=1e-5):
        expr = f"{min_rem:.4f}rem"
        return FluidTypographyToken(
            name=name,
            step_index=step_index,
            min_px=min_px,
            max_px=max_px,
            min_viewport_px=min_viewport_px,
            max_viewport_px=max_viewport_px,
            slope_vw=0.0,
            intercept_rem=min_rem,
            min_rem=min_rem,
            max_rem=max_rem,
            clamp_expr=expr,
        )

    # Pendiente en px / px
    slope = (max_px - min_px) / (max_viewport_px - min_viewport_px)
    intercept_px = min_px - slope * min_viewport_px

    slope_vw = slope * 100.0
    intercept_rem = intercept_px / 16.0

    # Construir expresión legible de CSS clamp
    clamp_expr = f"clamp({min_rem:.4f}rem, {intercept_rem:.4f}rem + {slope_vw:.4f}vw, {max_rem:.4f}rem)"

    return FluidTypographyToken(
        name=name,
        step_index=step_index,
        min_px=min_px,
        max_px=max_px,
        min_viewport_px=min_viewport_px,
        max_viewport_px=max_viewport_px,
        slope_vw=slope_vw,
        intercept_rem=intercept_rem,
        min_rem=min_rem,
        max_rem=max_rem,
        clamp_expr=clamp_expr,
    )


def generate_musical_fluid_typography(
    min_viewport_px: float = 320.0,
    max_viewport_px: float = 1280.0,
    base_min_px: float = 16.0,
    base_max_px: float = 18.0,
    ratio_min: Union[MusicalScale, float] = MusicalScale.MINOR_THIRD,
    ratio_max: Union[MusicalScale, float] = MusicalScale.PERFECT_FIFTH,
) -> Dict[str, FluidTypographyToken]:
    """
    Genera una escala tipográfica modular responsiva completa basada en proporciones musicales.
    Utiliza un ratio menor en móvil (p. ej. Minor Third 1.2) para evitar titulares gigantescos,
    y un ratio expansivo en desktop (p. ej. Perfect Fifth 1.5) para máximo impacto jerárquico.
    """
    r_min = float(ratio_min)
    r_max = float(ratio_max)

    scale_steps: List[Tuple[str, int]] = [
        ("xs", -2),
        ("sm", -1),
        ("base", 0),
        ("md", 1),
        ("lg", 2),
        ("xl", 3),
        ("2xl", 4),
        ("3xl", 5),
        ("4xl", 6),
        ("5xl", 7),
    ]

    tokens: Dict[str, FluidTypographyToken] = {}
    for name, idx in scale_steps:
        size_min = base_min_px * (r_min ** idx)
        size_max = base_max_px * (r_max ** idx)
        token = calculate_fluid_clamp(
            name=name,
            min_px=round(size_min, 2),
            max_px=round(size_max, 2),
            min_viewport_px=min_viewport_px,
            max_viewport_px=max_viewport_px,
            step_index=idx,
        )
        tokens[name] = token

    return tokens


# ==============================================================================
# 9. EXPORTADORES A FORMATOS W3C DTCG, CSS Y TAILWIND V4
# ==============================================================================

@dataclass
class DesignTokenBundle:
    """Contenedor de todos los tokens de diseño de un sistema soberano."""
    ramps: Dict[str, ColorRamp] = field(default_factory=dict)
    typography: Dict[str, FluidTypographyToken] = field(default_factory=dict)
    shadows: Dict[str, PhysicalShadow] = field(default_factory=dict)
    custom_colors: Dict[str, Union[RGBColor, OklchColor]] = field(default_factory=dict)
    polarities: Dict[str, PolarityConfig] = field(default_factory=dict)

    def to_w3c_dtcg(self) -> Dict[str, Any]:
        """
        Exporta al estándar W3C DTCG (Design Tokens Community Group) JSON.
        Estructura basada en grupos jerárquicos con `$value`, `$type` y `$description`.
        Todos los colores se expresan en OKLCH puro sin un solo literal #hex ni rgba().
        """
        root: Dict[str, Any] = {
            "$schema": "https://design-tokens.github.io/community-group/format/",
            "color": {},
            "typography": {
                "font-size": {}
            },
            "elevation": {}
        }

        # Exportar rampas de color en OKLCH puro
        for ramp_name, ramp in self.ramps.items():
            root["color"][ramp_name] = {}
            for step_key, step_data in ramp.steps.items():
                root["color"][ramp_name][str(step_key)] = {
                    "$value": step_data.oklch.to_css(),
                    "$type": "color",
                    "$description": f"{ramp_name} {step_key} en OKLCH ({step_data.oklch.to_css()})",
                    "oklch": step_data.oklch.to_css(),
                    "luminance_wcag": round(step_data.luminance_wcag, 4),
                    "apca_vs_white": round(step_data.apca_vs_white, 1),
                }

        # Exportar colores personalizados en OKLCH puro
        for c_name, c_val in self.custom_colors.items():
            if isinstance(c_val, OklchColor):
                c_css = c_val.to_css()
            elif hasattr(c_val, "to_oklch"):
                c_css = c_val.to_oklch().to_css()
            else:
                c_css = str(c_val)
            root["color"][c_name] = {
                "$value": c_css,
                "$type": "color",
                "$description": f"Color directo {c_name} en OKLCH",
            }

        # Exportar tipografía fluida
        for t_name, t_val in self.typography.items():
            root["typography"]["font-size"][t_name] = {
                "$value": t_val.clamp_expr,
                "$type": "dimension",
                "$description": f"Escala fluida {t_name} de {t_val.min_px}px a {t_val.max_px}px",
                "min_px": t_val.min_px,
                "max_px": t_val.max_px,
            }

        # Exportar sombras físicas
        for s_name, s_val in self.shadows.items():
            root["elevation"][s_name] = {
                "$value": s_val.to_css_box_shadow(),
                "$type": "shadow",
                "$description": f"Sombra física multicapa de elevación {s_val.elevation_px}px",
                "layers": [
                    {
                        "x": l.x_offset_px,
                        "y": l.y_offset_px,
                        "blur": l.blur_radius_px,
                        "spread": l.spread_radius_px,
                        "color": l.color_rgba,
                        "type": l.layer_type,
                    }
                    for l in s_val.layers
                ]
            }

        # Exportar polaridades visuales dinámicas
        if self.polarities:
            root["polarity"] = {}
            for pol_name, pol_cfg in self.polarities.items():
                root["polarity"][pol_name] = {
                    "bg": {"$value": pol_cfg.bg_color.to_css(), "$type": "color"},
                    "surface": {"$value": pol_cfg.surface_color.to_css(), "$type": "color"},
                    "surface-raised": {"$value": pol_cfg.surface_raised.to_css(), "$type": "color"},
                    "border": {"$value": pol_cfg.border_color.to_css(), "$type": "color"},
                    "text-primary": {"$value": pol_cfg.text_primary.to_css(), "$type": "color"},
                    "text-secondary": {"$value": pol_cfg.text_secondary.to_css(), "$type": "color"},
                    "text-muted": {"$value": pol_cfg.text_muted.to_css(), "$type": "color"},
                    "accent-primary": {"$value": pol_cfg.accent_primary.to_css(), "$type": "color"},
                    "accent-secondary": {"$value": pol_cfg.accent_secondary.to_css(), "$type": "color"},
                }

        return root

    def to_w3c_dtcg_json(self, indent: int = 2) -> str:
        """Serializa a JSON formateado W3C DTCG."""
        return json.dumps(self.to_w3c_dtcg(), indent=indent, ensure_ascii=False)

    def to_css_variables(self) -> str:
        """Exporta como bloque CSS Custom Properties (:root { ... }) en OKLCH sin literales #hex ni rgba()."""
        lines = [":root {"]

        # Colores de rampas en OKLCH puro
        lines.append("  /* --- Perceptual Color Ramps (OKLCH Sigmoid) --- */")
        for ramp_name, ramp in self.ramps.items():
            for step_key, step_data in ramp.steps.items():
                lines.append(f"  --color-{ramp_name}-{step_key}: {step_data.oklch.to_css()};")

        # Colores directos en OKLCH
        if self.custom_colors:
            lines.append("\n  /* --- Custom Colors (OKLCH) --- */")
            for c_name, c_val in self.custom_colors.items():
                if isinstance(c_val, OklchColor):
                    c_css = c_val.to_css()
                elif hasattr(c_val, "to_oklch"):
                    c_css = c_val.to_oklch().to_css()
                else:
                    c_css = str(c_val)
                lines.append(f"  --color-{c_name}: {c_css};")

        # Tipografía
        lines.append("\n  /* --- Fluid Typography Scales (Musical Clamp) --- */")
        for t_name, t_val in self.typography.items():
            lines.append(f"  --text-{t_name}: {t_val.clamp_expr};")

        # Sombras
        lines.append("\n  /* --- Multilayer Physical Shadows --- */")
        for s_name, s_val in self.shadows.items():
            lines.append(f"  --shadow-{s_name}: {s_val.to_css_box_shadow()};")

        # Polaridades dinámicas
        if self.polarities:
            lines.append("\n  /* --- Visual Polarities (OKLCH Dynamic Themes) --- */")
            for pol_name, pol_cfg in self.polarities.items():
                lines.append(f"  /* Polarity: {pol_name} */")
                lines.append(pol_cfg.to_css_variables(prefix=f"polar-{pol_name}"))

        lines.append("}\n")
        return "\n".join(lines)

    def to_tailwind_v4_theme(self) -> str:
        """
        Exporta al formato Tailwind CSS v4 (@theme { ... }).
        Usa variables CSS nativas en OKLCH sin necesidad de archivo tailwind.config.js antiguo.
        """
        lines = ["@theme {"]

        # Colores en OKLCH
        for ramp_name, ramp in self.ramps.items():
            for step_key, step_data in ramp.steps.items():
                lines.append(f"  --color-{ramp_name}-{step_key}: {step_data.oklch.to_css()};")

        for c_name, c_val in self.custom_colors.items():
            if isinstance(c_val, OklchColor):
                c_css = c_val.to_css()
            elif hasattr(c_val, "to_oklch"):
                c_css = c_val.to_oklch().to_css()
            else:
                c_css = str(c_val)
            lines.append(f"  --color-{c_name}: {c_css};")

        # Tipografía
        for t_name, t_val in self.typography.items():
            lines.append(f"  --text-{t_name}: {t_val.clamp_expr};")

        # Sombras
        for s_name, s_val in self.shadows.items():
            lines.append(f"  --shadow-{s_name}: {s_val.to_css_box_shadow()};")

        # Polaridades dinámicas
        if self.polarities:
            for pol_name, pol_cfg in self.polarities.items():
                lines.append(pol_cfg.to_css_variables(prefix=f"polar-{pol_name}"))

        lines.append("}\n")
        return "\n".join(lines)


# ==============================================================================
# 10. COMPILADOR ORQUESTADOR ALEPH
# ==============================================================================

class AlephTokenCompiler:
    """
    Compilador Maestro del Sistema de Diseño Soberano Aleph.
    Genera tokens de color, rampas sigmoideas, tipografías fluidas y sombras físicas,
    emitiendo simultáneamente especificaciones DTCG, CSS y Tailwind v4.
    """

    def __init__(self, brand_hue: float = 250.0, brand_name: str = "brand"):
        self.brand_hue = brand_hue
        self.brand_name = brand_name
        self.bundle = DesignTokenBundle()

    def build_default_system(self) -> DesignTokenBundle:
        """Genera un sistema de diseño canónico completo de grado de producción."""
        # 1. Rampa primaria y neutral
        primary_ramp = generate_sigmoid_oklch_ramp(
            name=self.brand_name,
            base_hue=self.brand_hue,
            max_chroma=0.19,
        )
        neutral_ramp = generate_sigmoid_oklch_ramp(
            name="neutral",
            base_hue=self.brand_hue,
            max_chroma=0.015,  # Neutros entintados armónicamente
        )
        self.bundle.ramps[self.brand_name] = primary_ramp
        self.bundle.ramps["neutral"] = neutral_ramp

        # 2. Escala tipográfica fluida musical (Minor Third a Perfect Fifth)
        self.bundle.typography = generate_musical_fluid_typography(
            min_viewport_px=320.0,
            max_viewport_px=1440.0,
            base_min_px=16.0,
            base_max_px=18.0,
            ratio_min=MusicalScale.MINOR_THIRD,
            ratio_max=MusicalScale.PERFECT_FIFTH,
        )

        # 3. Elevaciones de sombra física en OKLCH puro
        elevations = [
            ("sm", 2.0),
            ("md", 6.0),
            ("lg", 14.0),
            ("xl", 28.0),
            ("2xl", 48.0),
        ]
        neutral_surface = OklchColor(0.20, 0.012, self.brand_hue)
        for name, elev in elevations:
            self.bundle.shadows[name] = generate_physical_shadow_oklch(
                name=name,
                elevation_px=elev,
                surface_oklch=neutral_surface,
            )

        # 4. Colores fijos de contraste absoluto en OKLCH puro
        self.bundle.custom_colors["white"] = OklchColor(1.0, 0.0, 0.0)
        self.bundle.custom_colors["black"] = OklchColor(0.0, 0.0, 0.0)

        # 5. Las 5 polaridades visuales dinámicas canónicas
        for pol in VisualPolarity:
            self.bundle.polarities[pol.value] = get_canonical_polarity(pol, brand_hue=self.brand_hue)

        return self.bundle

    def compile_all(self) -> Dict[str, str]:
        """Ejecuta la compilación y devuelve artefactos serializados."""
        if not self.bundle.ramps:
            self.build_default_system()

        return {
            "dtcg_json": self.bundle.to_w3c_dtcg_json(),
            "css_variables": self.bundle.to_css_variables(),
            "tailwind_v4": self.bundle.to_tailwind_v4_theme(),
        }


# ==============================================================================
# 11. LAS 5 POLARIDADES VISUALES DINÁMICAS (ANTI-HALACIÓN L <= 0.90)
# ==============================================================================

class VisualPolarity(str, Enum):
    """Las 5 polaridades visuales dinámicas del sistema soberano Aleph."""
    LIGHT_MODE = "light"
    DARK_MODE = "dark"
    PAPER_D50 = "paper_d50"
    DEEP_INK = "deep_ink"
    HIGH_CONTRAST_MONOCHROME = "high_contrast_mono"


@dataclass
class PolarityConfig:
    """Configuración espectral completa de una polaridad visual con anti-halación."""
    polarity: VisualPolarity
    bg_color: OklchColor
    surface_color: OklchColor
    surface_raised: OklchColor
    border_color: OklchColor
    text_primary: OklchColor
    text_secondary: OklchColor
    text_muted: OklchColor
    accent_primary: OklchColor
    accent_secondary: OklchColor
    anti_halation_l_max: float = 0.90
    strict_anti_halation: bool = True

    def __post_init__(self):
        # Invariante anti-halación: En modos oscuros/nocturnos, el texto primario
        # no debe superar L <= anti_halation_l_max (0.90) para prevenir fatiga ciliar y dispersión intraocular.
        if self.polarity in (VisualPolarity.DARK_MODE, VisualPolarity.DEEP_INK):
            if self.text_primary.L > self.anti_halation_l_max:
                if self.strict_anti_halation:
                    object.__setattr__(
                        self,
                        "text_primary",
                        OklchColor(
                            L=self.anti_halation_l_max,
                            c=self.text_primary.c,
                            h=self.text_primary.h,
                            alpha=self.text_primary.alpha,
                        ),
                    )
                else:
                    raise ValueError(
                        f"Violación de invariante anti-halación: L={self.text_primary.L:.3f} > {self.anti_halation_l_max} en polaridad {self.polarity.value}"
                    )
        object.__setattr__(self, "_initialized", True)

    def __setattr__(self, name: str, value: Any):
        if getattr(self, "_initialized", False) and name == "text_primary":
            if self.polarity in (VisualPolarity.DARK_MODE, VisualPolarity.DEEP_INK):
                max_l = getattr(self, "anti_halation_l_max", 0.90)
                strict = getattr(self, "strict_anti_halation", True)
                if isinstance(value, OklchColor) and value.L > max_l:
                    if strict:
                        value = OklchColor(
                            L=max_l,
                            c=value.c,
                            h=value.h,
                            alpha=value.alpha,
                        )
                    else:
                        raise ValueError(
                            f"Violación de invariante anti-halación: L={value.L:.3f} > {max_l} en polaridad {self.polarity.value}"
                        )
        super().__setattr__(name, value)

    def to_css_variables(self, prefix: str = "polar") -> str:
        """Exporta las variables CSS de la polaridad."""
        tokens = {
            f"--{prefix}-bg": self.bg_color.to_css(),
            f"--{prefix}-surface": self.surface_color.to_css(),
            f"--{prefix}-surface-raised": self.surface_raised.to_css(),
            f"--{prefix}-border": self.border_color.to_css(),
            f"--{prefix}-text-primary": self.text_primary.to_css(),
            f"--{prefix}-text-secondary": self.text_secondary.to_css(),
            f"--{prefix}-text-muted": self.text_muted.to_css(),
            f"--{prefix}-accent-primary": self.accent_primary.to_css(),
            f"--{prefix}-accent-secondary": self.accent_secondary.to_css(),
        }
        return "\n".join(f"  {k}: {v};" for k, v in tokens.items())


def get_canonical_polarity(polarity: VisualPolarity, brand_hue: float = 250.0) -> PolarityConfig:
    """Devuelve la configuración canónica de una de las 5 polaridades visuales dinámicas."""
    if polarity == VisualPolarity.LIGHT_MODE:
        return PolarityConfig(
            polarity=polarity,
            bg_color=OklchColor(0.985, 0.002, brand_hue),
            surface_color=OklchColor(0.955, 0.005, brand_hue),
            surface_raised=OklchColor(1.000, 0.000, 0.0),
            border_color=OklchColor(0.880, 0.010, brand_hue),
            text_primary=OklchColor(0.180, 0.015, brand_hue),
            text_secondary=OklchColor(0.380, 0.018, brand_hue),
            text_muted=OklchColor(0.550, 0.015, brand_hue),
            accent_primary=OklchColor(0.580, 0.220, brand_hue),
            accent_secondary=OklchColor(0.680, 0.160, (brand_hue + 45.0) % 360.0),
        )
    elif polarity == VisualPolarity.DARK_MODE:
        return PolarityConfig(
            polarity=polarity,
            bg_color=OklchColor(0.140, 0.008, brand_hue),
            surface_color=OklchColor(0.180, 0.010, brand_hue),
            surface_raised=OklchColor(0.230, 0.012, brand_hue),
            border_color=OklchColor(0.280, 0.015, brand_hue),
            text_primary=OklchColor(0.880, 0.005, brand_hue),  # Anti-halación L <= 0.90
            text_secondary=OklchColor(0.700, 0.010, brand_hue),
            text_muted=OklchColor(0.520, 0.010, brand_hue),
            accent_primary=OklchColor(0.650, 0.200, brand_hue),
            accent_secondary=OklchColor(0.720, 0.140, (brand_hue + 45.0) % 360.0),
        )
    elif polarity == VisualPolarity.PAPER_D50:
        # Editorial CIE D50 (5003K) pergamino/marfil cálido
        return PolarityConfig(
            polarity=polarity,
            bg_color=OklchColor(0.950, 0.016, 82.0),
            surface_color=OklchColor(0.925, 0.018, 80.0),
            surface_raised=OklchColor(0.975, 0.012, 85.0),
            border_color=OklchColor(0.840, 0.020, 78.0),
            text_primary=OklchColor(0.200, 0.012, 60.0),
            text_secondary=OklchColor(0.380, 0.015, 65.0),
            text_muted=OklchColor(0.560, 0.018, 70.0),
            accent_primary=OklchColor(0.520, 0.180, 40.0),
            accent_secondary=OklchColor(0.580, 0.140, 95.0),
        )
    elif polarity == VisualPolarity.DEEP_INK:
        # Nocturna abisal de baja dispersión espectral
        return PolarityConfig(
            polarity=polarity,
            bg_color=OklchColor(0.080, 0.025, 260.0),
            surface_color=OklchColor(0.120, 0.028, 260.0),
            surface_raised=OklchColor(0.160, 0.030, 260.0),
            border_color=OklchColor(0.220, 0.035, 260.0),
            text_primary=OklchColor(0.860, 0.012, 85.0),  # L <= 0.90 pergamino bioluminiscente
            text_secondary=OklchColor(0.680, 0.015, 85.0),
            text_muted=OklchColor(0.480, 0.020, 260.0),
            accent_primary=OklchColor(0.680, 0.190, 185.0),
            accent_secondary=OklchColor(0.720, 0.160, 140.0),
        )
    elif polarity == VisualPolarity.HIGH_CONTRAST_MONOCHROME:
        # Accesibilidad máxima binaria acromática (croma 0.0)
        return PolarityConfig(
            polarity=polarity,
            bg_color=OklchColor(0.020, 0.000, 0.0),
            surface_color=OklchColor(0.080, 0.000, 0.0),
            surface_raised=OklchColor(0.150, 0.000, 0.0),
            border_color=OklchColor(0.500, 0.000, 0.0),
            text_primary=OklchColor(0.980, 0.000, 0.0),
            text_secondary=OklchColor(0.850, 0.000, 0.0),
            text_muted=OklchColor(0.700, 0.000, 0.0),
            accent_primary=OklchColor(0.950, 0.000, 0.0),
            accent_secondary=OklchColor(0.800, 0.000, 0.0),
        )
    raise ValueError(f"Polaridad no soportada: {polarity}")


# ==============================================================================
# 12. MATRIZ DE REQUISITOS APCA v0.98G (TAMAÑO / PESO vs Lc)
# ==============================================================================

# Matriz estandarizada APCA W3C Silver Draft:
# Columnas: font_weight (300, 400, 500, 600, 700, 900)
# Filas: font_size_px (12, 14, 16, 18, 24, 32, 48, 64)
APCA_MIN_LC_TABLE: Dict[int, Dict[int, float]] = {
    12: {300: 105.0, 400: 90.0, 500: 80.0, 600: 75.0, 700: 70.0, 900: 65.0},
    14: {300: 95.0,  400: 75.0, 500: 70.0, 600: 65.0, 700: 60.0, 900: 55.0},
    16: {300: 90.0,  400: 60.0, 500: 55.0, 600: 50.0, 700: 45.0, 900: 45.0},
    18: {300: 75.0,  400: 55.0, 500: 50.0, 600: 45.0, 700: 40.0, 900: 40.0},
    24: {300: 60.0,  400: 45.0, 500: 40.0, 600: 38.0, 700: 35.0, 900: 35.0},
    32: {300: 45.0,  400: 38.0, 500: 35.0, 600: 32.0, 700: 30.0, 900: 30.0},
    48: {300: 38.0,  400: 32.0, 500: 30.0, 600: 28.0, 700: 25.0, 900: 25.0},
    64: {300: 35.0,  400: 30.0, 500: 28.0, 600: 25.0, 700: 22.0, 900: 22.0},
}


def get_apca_required_lc(font_size_px: float, font_weight: int = 400) -> float:
    """
    Retorna el umbral mínimo absoluto |Lc| exigido por APCA v0.98G
    según tamaño de texto en px y peso numérico (100 a 900).
    Aplica cuantización al escalón más cercano conservador.
    """
    sizes = sorted(APCA_MIN_LC_TABLE.keys())
    matched_size = sizes[0]
    for s in sizes:
        if font_size_px >= s:
            matched_size = s

    weight_row = APCA_MIN_LC_TABLE[matched_size]
    weights = sorted(weight_row.keys())
    matched_weight = weights[0]
    for w in weights:
        if font_weight >= w:
            matched_weight = w

    return weight_row[matched_weight]


def verify_apca_text_conformance(
    font_size_px: float,
    font_weight: int,
    text_color: RGBColor,
    bg_color: RGBColor,
) -> Dict[str, Any]:
    """Evalúa la conformidad APCA v0.98G de un par tipográfico contra su contexto visual."""
    apca_res = calculate_apca(text_color, bg_color)
    req_lc = get_apca_required_lc(font_size_px, font_weight)
    passes = apca_res.abs_lc >= req_lc
    margin = apca_res.abs_lc - req_lc

    return {
        "font_size_px": font_size_px,
        "font_weight": font_weight,
        "actual_lc": apca_res.lc,
        "abs_actual_lc": apca_res.abs_lc,
        "required_min_lc": req_lc,
        "margin_lc": round(margin, 2),
        "passes": passes,
        "polarity": apca_res.polarity,
    }


# ==============================================================================
# 13. ÓPTICA PERCEPTUAL 2.5D: FRESNEL-SCHLICK, BLINN-PHONG Y SOMBRAS OKLCH
# ==============================================================================

def fresnel_schlick(cos_theta: float, r0: float = 0.0426) -> float:
    """
    Aproximación de Fresnel-Schlick para interfaces dieléctricas:
    R(θ) = R0 + (1 - R0) * (1 - cos(θ))^5.
    Para vidrio óptico común (n=1.52) en aire (n=1.0):
    R0 = ((1 - 1.52) / (1 + 1.52))^2 = (-0.52 / 2.52)^2 ≈ 0.042589 ≈ 0.0426.
    """
    c = max(0.0, min(1.0, cos_theta))
    return r0 + (1.0 - r0) * ((1.0 - c) ** 5)


def blinn_phong_specular_25d(
    light_dir: Tuple[float, float, float] = (0.2, -1.0, 2.0),
    shininess: float = 32.0,
    ks: float = 0.85,
) -> Dict[str, Any]:
    """
    Calcula el factor especular Blinn-Phong 2.5D para un plano ortográfico con normal N=(0, 0, 1).
    N · H = (L + V) / ||L + V|| proyectado sobre normal Z.
    """
    lx, ly, lz = light_dir
    l_len = math.sqrt(lx * lx + ly * ly + lz * lz)
    if l_len > 1e-9:
        lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

    # Vector observador cenital V = (0, 0, 1)
    vx, vy, vz = 0.0, 0.0, 1.0

    # Vector intermedio H = (L + V) / ||L + V||
    hx = lx + vx
    hy = ly + vy
    hz = lz + vz
    h_len = math.sqrt(hx * hx + hy * hy + hz * hz)
    if h_len > 1e-9:
        hx, hy, hz = hx / h_len, hy / h_len, hz / h_len

    # N · H = hz (dado que N = (0, 0, 1))
    n_dot_h = max(0.0, hz)
    specular_intensity = ks * (n_dot_h ** shininess)

    # Inset highlight CSS para recrear el reflejo especular en el borde superior
    highlight_alpha = min(0.95, specular_intensity * 0.45)
    fresnel_grazing = fresnel_schlick(0.1, r0=0.0426)

    return {
        "specular_intensity": round(specular_intensity, 4),
        "highlight_alpha": round(highlight_alpha, 4),
        "fresnel_grazing": round(fresnel_grazing, 4),
        "css_inset_highlight": f"inset 0 1px 0 0 oklch(1 0 0 / {highlight_alpha:.3f})",
        "css_border_rim": f"1px solid oklch(1 0 0 / {fresnel_grazing:.3f})",
    }


def generate_physical_shadow_oklch(
    name: str,
    elevation_px: float,
    surface_oklch: Optional[OklchColor] = None,
    light: Optional[LightSource3D] = None,
    num_layers: int = 4,
    base_alpha: float = 0.14,
) -> PhysicalShadow:
    """
    Genera sombras físicas multicapa calculadas en espacio OKLCH puro:
    - Conserva el matiz armónico h de la superficie de fondo para evitar turbidez grisácea.
    - Oclusión ambiental (contacto estricto), sombra directa (umbra) y penumbra difusa.
    """
    l_src = light if light is not None else LightSource3D(x=0.0, y=-1.0, z=2.0)
    surf = surface_oklch if surface_oklch is not None else OklchColor(0.20, 0.015, 250.0)

    # Dirección normalizada de la luz en el plano XY
    dir_x = l_src.x / max(0.5, l_src.z)
    dir_y = (-l_src.y) / max(0.5, l_src.z)

    shadow = PhysicalShadow(name=name, elevation_px=elevation_px)

    # Capa 1: Oclusión Ambiental de Contacto (AO)
    ao_offset_y = max(1.0, elevation_px * 0.08)
    ao_blur = max(2.0, elevation_px * 0.20)
    ao_alpha = min(0.40, base_alpha * 2.4)
    ao_color = f"oklch({max(0.02, surf.L * 0.25):.3f} {surf.c * 0.5:.4f} {surf.h:.1f} / {ao_alpha:.3f})"

    shadow.layers.append(
        ShadowLayer(
            x_offset_px=0.0,
            y_offset_px=round(ao_offset_y, 1),
            blur_radius_px=round(ao_blur, 1),
            spread_radius_px=0.0,
            color_rgba=ao_color,
            layer_type="ambient_occlusion",
        )
    )

    # Capas sucesivas de dispersión
    remaining_layers = max(1, num_layers - 1)
    for i in range(1, remaining_layers + 1):
        progress = i / remaining_layers
        layer_x = dir_x * elevation_px * (progress ** 1.15)
        layer_y = dir_y * elevation_px * (progress ** 1.15)
        layer_blur = (elevation_px * 1.6) * (progress ** 1.65) + 2.0
        layer_spread = -(elevation_px * 0.08) * progress if i > 1 else 0.0
        layer_alpha = (base_alpha * 1.3) * (1.0 - progress * 0.55) / remaining_layers

        l_type = "key_umbra" if i == 1 else ("penumbra" if i < remaining_layers else "ambient_diffuse")
        layer_color = f"oklch({max(0.01, surf.L * 0.20):.3f} {surf.c * 0.6:.4f} {surf.h:.1f} / {layer_alpha:.3f})"

        shadow.layers.append(
            ShadowLayer(
                x_offset_px=round(layer_x, 1),
                y_offset_px=round(layer_y, 1),
                blur_radius_px=round(layer_blur, 1),
                spread_radius_px=round(layer_spread, 1),
                color_rgba=layer_color,
                layer_type=l_type,
            )
        )

    return shadow


# ==============================================================================
# 14. PRESUPUESTO DE ACENTO VISUAL (REGLA 60-30-10) Y AUDITORÍA DE SUPERFICIE
# ==============================================================================

@dataclass(frozen=True)
class VisualElementArea:
    """Representación de un nodo de interfaz en el árbol de superficie visual."""
    element_id: str
    width_px: float
    height_px: float
    is_accent: bool
    chroma: float
    opacity: float = 1.0

    @property
    def effective_area(self) -> float:
        return self.width_px * self.height_px * max(0.0, min(1.0, self.opacity))


@dataclass(frozen=True)
class VisualBudgetReport:
    """Reporte formal de distribución de superficie visual (60-30-10)."""
    viewport_width: float
    viewport_height: float
    total_viewport_area: float
    dominant_surface_ratio: float   # Meta: ~0.60 (fondos/lienzos)
    structural_surface_ratio: float # Meta: ~0.30 (tarjetas/contenedores/texto)
    accent_surface_ratio: float     # Meta: 0.08 a 0.10 (focos/CTAs)
    is_accent_budget_compliant: bool
    status_message: str


def calculate_accent_budget(
    elements: List[VisualElementArea],
    viewport_width: float = 1920.0,
    viewport_height: float = 1080.0,
    max_accent_threshold: float = 0.10,
    min_accent_threshold: float = 0.02,
) -> VisualBudgetReport:
    """
    Calcula el presupuesto de superficie visual del viewport según la Regla 60-30-10.
    Garantiza formalmente que los acentos de alto croma no excedan el 8-10% del viewport.
    """
    viewport_area = viewport_width * viewport_height
    if viewport_area <= 0.0:
        raise ValueError("El área del viewport debe ser estrictamente positiva.")

    accent_area = sum(el.effective_area for el in elements if el.is_accent)
    accent_ratio = accent_area / viewport_area

    remaining_ratio = max(0.0, 1.0 - accent_ratio)
    dominant_ratio = remaining_ratio * (60.0 / 90.0)
    structural_ratio = remaining_ratio * (30.0 / 90.0)

    is_compliant = (accent_ratio <= max_accent_threshold) and (accent_ratio >= min_accent_threshold)

    if accent_ratio > max_accent_threshold:
        status = f"VIOLACIÓN DE PRESUPUESTO: Acento ocupa {accent_ratio * 100:.2f}% (Máximo permitido: {max_accent_threshold * 100:.1f}%)."
    elif accent_ratio < min_accent_threshold:
        status = f"SUB-ACENTUACIÓN: Acento ocupa {accent_ratio * 100:.2f}% (Mínimo recomendado: {min_accent_threshold * 100:.1f}%)."
    else:
        status = f"CONFORME: Acento óptimo equilibrado al {accent_ratio * 100:.2f}% de la superficie."

    return VisualBudgetReport(
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        total_viewport_area=viewport_area,
        dominant_surface_ratio=round(dominant_ratio, 4),
        structural_surface_ratio=round(structural_ratio, 4),
        accent_surface_ratio=round(accent_ratio, 4),
        is_accent_budget_compliant=is_compliant,
        status_message=status,
    )


# ==============================================================================
# 15. VALIDADOR DE ELIMINACIÓN TOTAL DE LITERALES CSS
# ==============================================================================

class ZeroLiteralCSSValidator:
    """
    Linter y verificador sintáctico para asegurar CERO valores literales en CSS.
    Prohíbe:
    - Códigos hexadecimales directos (#fff, #1a202c, etc.)
    - rgb() / rgba() / hsl() / hsla() literales (obliga a usar var(--...) o tokens OKLCH)
    """
    HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    LEGACY_COLOR_PATTERN = re.compile(r"\b(rgba?|hsla?)\s*\(")

    @classmethod
    def validate_css(cls, css_content: str) -> List[Dict[str, Any]]:
        """Escanea una cadena CSS y retorna todas las violaciones de valores literales prohibidos."""
        violations: List[Dict[str, Any]] = []
        lines = css_content.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Ignorar comentarios
            if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
                continue

            # 1. Búsqueda de códigos hexadecimales literales
            hex_matches = cls.HEX_PATTERN.findall(line)
            for h in hex_matches:
                violations.append({
                    "line": idx,
                    "rule": "ZERO_LITERAL_HEX",
                    "match": h,
                    "message": f"Valor hexadecimal literal prohibido '{h}'. Use tokens var(--color-*) o OKLCH generativo.",
                })

            # 2. Búsqueda de colores legados rgba/hsl
            legacy_matches = cls.LEGACY_COLOR_PATTERN.findall(line)
            for m in legacy_matches:
                violations.append({
                    "line": idx,
                    "rule": "ZERO_LITERAL_LEGACY_COLOR",
                    "match": m,
                    "message": f"Función de color legado '{m}' prohibida. Use espacio perceptual OKLCH o variables.",
                })

        return violations


# ==============================================================================
# 16. MATERIALIZACIÓN MATEMÁTICA DE LA SUPERELIPSE DE LAMÉ (|x/a|^n + |y/b|^n = 1)
# ==============================================================================

def generate_lame_superellipse_svg_mask(exponent_n: float = 4.2, num_points: int = 64) -> str:
    """
    Evalúa la ecuación paramétrica de la Superelipse de Gabriel Lamé (|x/a|^n + |y/b|^n = 1):
      x(theta) = |cos(theta)|^(2/n) * sgn(cos(theta))
      y(theta) = |sin(theta)|^(2/n) * sgn(sin(theta))
    Escalado y trasladado al espacio unitario porcentual [0.0%, 100.0%]:
      px = 50.0 + 50.0 * x(theta)
      py = 50.0 + 50.0 * y(theta)
    Generando un polígono cerrado CSS: 'polygon(px1% py1%, px2% py2%, ...)' listo para usar como 'clip-path' o máscara SVG.
    """
    if exponent_n <= 0.0:
        exponent_n = 4.2
    if num_points < 4:
        num_points = 64

    inv_n = 2.0 / exponent_n
    points: List[str] = []

    for i in range(num_points):
        theta = (2.0 * math.pi * i) / num_points
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # sgn(v)
        sgn_cos = 1.0 if cos_t > 0 else (-1.0 if cos_t < 0 else 0.0)
        sgn_sin = 1.0 if sin_t > 0 else (-1.0 if sin_t < 0 else 0.0)

        # x(theta) = |cos(theta)|^(2/n) * sgn(cos(theta))
        # y(theta) = |sin(theta)|^(2/n) * sgn(sin(theta))
        x = (abs(cos_t) ** inv_n) * sgn_cos if abs(cos_t) > 1e-15 else 0.0
        y = (abs(sin_t) ** inv_n) * sgn_sin if abs(sin_t) > 1e-15 else 0.0

        px = 50.0 + 50.0 * x
        py = 50.0 + 50.0 * y

        # Clamping estricto en el dominio [0.0, 100.0]%
        px = max(0.0, min(100.0, px))
        py = max(0.0, min(100.0, py))

        points.append(f"{px:.2f}% {py:.2f}%")

    return f"polygon({', '.join(points)})"


def generate_lame_superellipse_svg_path(
    exponent_n: float = 4.2,
    num_points: int = 64,
    width: float = 100.0,
    height: float = 100.0
) -> str:
    """Genera el atributo 'd' de un elemento <path> SVG cerrado con la superelipse de Lamé."""
    if exponent_n <= 0.0:
        exponent_n = 4.2
    if num_points < 4:
        num_points = 64

    inv_n = 2.0 / exponent_n
    path_cmds: List[str] = []

    for i in range(num_points):
        theta = (2.0 * math.pi * i) / num_points
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        sgn_cos = 1.0 if cos_t > 0 else (-1.0 if cos_t < 0 else 0.0)
        sgn_sin = 1.0 if sin_t > 0 else (-1.0 if sin_t < 0 else 0.0)
        x = (abs(cos_t) ** inv_n) * sgn_cos if abs(cos_t) > 1e-15 else 0.0
        y = (abs(sin_t) ** inv_n) * sgn_sin if abs(sin_t) > 1e-15 else 0.0
        px = (width / 2.0) + (width / 2.0) * x
        py = (height / 2.0) + (height / 2.0) * y
        px = max(0.0, min(width, px))
        py = max(0.0, min(height, py))
        cmd = "M" if i == 0 else "L"
        path_cmds.append(f"{cmd} {px:.2f} {py:.2f}")

    path_cmds.append("Z")
    return " ".join(path_cmds)


