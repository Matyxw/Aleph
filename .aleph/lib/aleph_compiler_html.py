"""
.aleph/lib/aleph_compiler_html.py
Modern HTML5 & CSS Compiler (Aleph Sovereign Design Engine - Track 3).
Estándar: CSS @layer / CSS @property / Container Queries / CSS Anchor Positioning.

Compila un DesignIR v2.0 a HTML5 semántico hiper-optimizado y CSS moderno en capas,
eliminando de raíz todo rastro de slop de IA (banning de transition:all, Inter/Geist,
garantizando cero overflow-x y estados interactivos completos).
"""

from __future__ import annotations

import hashlib
import html
import re
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from lib.aleph_token_compiler import (
        generate_lame_superellipse_svg_mask,
        generate_lame_superellipse_svg_path,
    )
except ImportError:
    try:
        from aleph_token_compiler import (  # type: ignore
            generate_lame_superellipse_svg_mask,
            generate_lame_superellipse_svg_path,
        )
    except ImportError:
        import math
        def generate_lame_superellipse_svg_mask(exponent_n: float = 4.2, num_points: int = 64) -> str:
            if exponent_n <= 0.0:
                exponent_n = 4.2
            if num_points < 4:
                num_points = 64
            inv_n = 2.0 / exponent_n
            pts = []
            for i in range(num_points):
                theta = (2.0 * math.pi * i) / num_points
                ct = math.cos(theta)
                st = math.sin(theta)
                sct = 1.0 if ct > 0 else (-1.0 if ct < 0 else 0.0)
                sst = 1.0 if st > 0 else (-1.0 if st < 0 else 0.0)
                x = (abs(ct) ** inv_n) * sct if abs(ct) > 1e-15 else 0.0
                y = (abs(st) ** inv_n) * sst if abs(st) > 1e-15 else 0.0
                px = max(0.0, min(100.0, 50.0 + 50.0 * x))
                py = max(0.0, min(100.0, 50.0 + 50.0 * y))
                pts.append(f"{px:.2f}% {py:.2f}%")
            return f"polygon({', '.join(pts)})"

        def generate_lame_superellipse_svg_path(exponent_n: float = 4.2, num_points: int = 64, width: float = 100.0, height: float = 100.0) -> str:
            return ""

try:
    from lib.aleph_design_ir import (
        AestheticParadigm,
        DesignIR,
        HapticPhysicalState,
        InteractionRole,
        IRComponent,
        SpatialArchetype,
        StateName,
        TaskPhase,
    )
except ImportError:
    from aleph_design_ir import (  # type: ignore
        AestheticParadigm,
        DesignIR,
        HapticPhysicalState,
        InteractionRole,
        IRComponent,
        SpatialArchetype,
        StateName,
        TaskPhase,
    )
try:
    from lib.aleph_visual_stage_synthesizer import (
        AlephVisualStageSynthesizer,
        VisualStageConfig,
        VisualStageType,
    )
except ImportError:
    try:
        from aleph_visual_stage_synthesizer import (  # type: ignore
            AlephVisualStageSynthesizer,
            VisualStageConfig,
            VisualStageType,
        )
    except ImportError:
        AlephVisualStageSynthesizer = None
        VisualStageConfig = None
        VisualStageType = None


class HTMLCompilerError(Exception):
    """Error al compilar DesignIR a HTML5/CSS."""
    pass



PARADIGM_LAME_EXPONENTS: Dict[AestheticParadigm, float] = {
    AestheticParadigm.CINEMATIC_WEBGL: 4.2,
    AestheticParadigm.BENTO_HYPERGRID: 4.0,
    AestheticParadigm.INDUSTRIAL_BRUTALIST: 8.0,
    AestheticParadigm.ORGANIC_TACTILE: 3.2,
    AestheticParadigm.RETRO_FUTURIST: 3.5,
    AestheticParadigm.NEO_BRUTALIST: 2.0,
    AestheticParadigm.SWISS_INTERNATIONAL: 100.0,
    AestheticParadigm.LITERARY_EDITORIAL: 100.0,
    AestheticParadigm.HAUTE_LUXURY: 100.0,
    AestheticParadigm.CYBER_TELEMETRY: 100.0,
    AestheticParadigm.DOCUMENT_MINIMALIST: 100.0,
    AestheticParadigm.DECONSTRUCTIVIST: 100.0,
}

class AlephHTMLCompiler:
    """
    Compilador Soberano de HTML5 + CSS Moderno.
    Traduce el AST del Design IR a marcado semántico y estilos de nivel arquitecto.
    """

    def __init__(self, minify: bool = False, enable_anchors: bool = True):
        self.minify = minify
        self.enable_anchors = enable_anchors

    def compile_css(self, ir: DesignIR) -> str:
        """Genera el paquete CSS completo particionado en @layer."""
        layers = [
            "/* Aleph Sovereign CSS Engine - Anti-Slop Production Build */",
            "@layer reset, tokens, layout, components, utilities;",
            "",
            self._generate_reset_layer(),
            "",
            self._generate_properties_layer(),
            "",
            self._generate_tokens_layer(ir),
            "",
            self._generate_layout_layer(ir),
            "",
            self._generate_components_layer(ir),
            "",
            self._generate_reduced_motion_layer(ir),
        ]
        return "\n".join(layers)

    def compile_html(self, ir: DesignIR, full_document: bool = True) -> str:
        """Compila los componentes del DesignIR a marcado HTML5 semántico."""
        self._current_paradigm = ir.paradigm.value
        self._palette = {}
        color_sys = getattr(ir, "color_system", None)
        if color_sys and getattr(color_sys, "palette", None):
            for c_token in color_sys.palette:
                if getattr(c_token, "name", "") == "primary":
                    self._palette["primary"] = getattr(c_token.oklch, "to_hex", lambda: "oklch(0.85 0.18 200)")() if hasattr(getattr(c_token, "oklch", None), "to_hex") else "oklch(0.85 0.18 200)"
                elif getattr(c_token, "name", "") == "secondary":
                    self._palette["secondary"] = getattr(c_token.oklch, "to_hex", lambda: "oklch(0.55 0.28 310)")() if hasattr(getattr(c_token, "oklch", None), "to_hex") else "oklch(0.55 0.28 310)"

        rendered_components = []
        for comp in ir.root_components:
            rendered_components.append(self._render_component(comp, indent=2))

        body_inner = "\n".join(rendered_components)

        if not full_document:
            return body_inner

        css_content = self.compile_css(ir)
        shader_script = self._generate_shader_runtime(ir)
        spotlight_script = self._generate_spotlight_runtime(ir)
        google_fonts_links = self._generate_google_fonts_links(ir)

        doc = f"""<!DOCTYPE html>
<html lang="es" data-paradigm="{ir.paradigm.value}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{html.escape(ir.title)}</title>
{google_fonts_links}
  <style>
{css_content}
  </style>
</head>
<body class="aleph-root paradigm-{ir.paradigm.value.replace('_', '-')}">
  <main id="main-content" class="archetype-{ir.spatial_grammar.archetype.value.replace('_', '-')}">
{body_inner}
  </main>
{shader_script}
{spotlight_script}
</body>
</html>"""
        return doc

    def _generate_google_fonts_links(self, ir: DesignIR) -> str:
        """Genera enlaces <link> a Google Fonts para renderizado tipográfico de élite."""
        fonts = set()
        for fam in [ir.typography.primary_family, ir.typography.mono_family, ir.typography.secondary_family]:
            if not fam:
                continue
            for part in fam.split(","):
                clean = part.strip().strip("'\"")
                if clean.lower() not in (
                    "sans-serif", "serif", "monospace", "system-ui", "-apple-system",
                    "blinkmacsystemfont", "segoe ui", "helvetica neue", "arial",
                    "georgia", "times new roman", "courier new", "ui-monospace"
                ):
                    fonts.add(clean.replace(" ", "+"))

        if not fonts:
            return ""

        font_params = "&".join(f"family={f}:wght@300;400;500;600;700;800" for f in sorted(fonts))
        return f"""  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?{font_params}&display=swap" rel="stylesheet">"""

    def compile_bundle(self, ir: DesignIR) -> Dict[str, str]:
        """Retorna un diccionario con artefactos separados: html, css, js_runtime."""
        return {
            "html": self.compile_html(ir, full_document=True),
            "css": self.compile_css(ir),
            "paradigm": ir.paradigm.value,
            "archetype": ir.spatial_grammar.archetype.value,
        }

    # =========================================================================
    # GENERADORES DE CAPAS CSS (@layer)
    # =========================================================================

    def _generate_reset_layer(self) -> str:
        """Capa de reseteo defensivo para erradicar overflow-x y artefactos de navegador."""
        return """@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  html {
    -webkit-text-size-adjust: 100%;
    tab-size: 4;
    overflow-x: hidden;
    scroll-behavior: smooth;
  }
  body {
    min-height: 100dvh;
    line-height: 1.5;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
    max-inline-size: 100%;
    overflow-wrap: break-word;
  }
  img, picture, video, canvas, svg {
    display: block;
    max-inline-size: 100%;
    block-size: auto;
  }
  pre, code, kbd, samp {
    max-inline-size: 100%;
    overflow-x: auto;
  }
  input, button, textarea, select {
    font: inherit;
    color: inherit;
  }
  button {
    background: none;
    border: none;
    cursor: pointer;
  }
  a {
    color: inherit;
    text-decoration: none;
  }
}"""

    def _generate_properties_layer(self) -> str:
        """CSS Houdini @property para animaciones GPU suaves de gradientes y ángulos."""
        return """@layer tokens {
  @property --shimmer-angle {
    syntax: '<angle>';
    inherits: false;
    initial-value: 0deg;
  }
  @property --glow-opacity {
    syntax: '<number>';
    inherits: false;
    initial-value: 0.0;
  }
  @property --scale-factor {
    syntax: '<number>';
    inherits: false;
    initial-value: 1.0;
  }
}"""

    def _generate_tokens_layer(self, ir: DesignIR) -> str:
        """Genera variables CSS a partir de los PerceptualTokens del DesignIR."""
        lines = ["@layer tokens {", "  :root {"]

        # 1. Colores
        for name, token in ir.perceptual_tokens.colors.items():
            safe_name = name.replace("_", "-")
            l, c, h = token.oklch
            lines.append(f"    --color-{safe_name}: oklch({l:.4f} {c:.4f} {h:.2f});")
            
        # 2. Sombras
        for name, s_token in ir.perceptual_tokens.shadows.items():
            safe_name = name.replace("_", "-")
            shadow_css = s_token.to_css_box_shadow() if hasattr(s_token, "to_css_box_shadow") else str(getattr(s_token, "css_box_shadow", "none"))
            shadow_css = re.sub(r"rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([\d\.]+)\s*\)", r"oklch(0.18 0.03 260 / \1)", shadow_css)
            lines.append(f"    --shadow-{safe_name}: {shadow_css};")

        lame_n = PARADIGM_LAME_EXPONENTS.get(ir.paradigm, 100.0)
        lines.append(f"    --morph-squircle-exponent: {lame_n:.1f};")
        if 2.5 <= lame_n <= 10.0:
            squircle_polygon = generate_lame_superellipse_svg_mask(exponent_n=lame_n, num_points=64)
            lines.append(f"    --morph-squircle-mask: {squircle_polygon};")

        # 3. Superficies
        for name, surf in ir.perceptual_tokens.surfaces.items():
            safe_name = name.replace("_", "-")
            for scale_k, scale_v in surf.border_radius_scale.items():
                lines.append(f"    --radius-{safe_name}-{scale_k}: {scale_v:.1f}px;")
            # Default radius
            default_rad = surf.border_radius_scale.get("md", 8.0)
            lines.append(f"    --radius-{safe_name}: {default_rad:.1f}px;")
            lines.append(f"    --border-w-{safe_name}: {surf.border_width_px:.1f}px;")
            if surf.backdrop_blur_px > 0:
                lines.append(f"    --backdrop-blur-{safe_name}: {surf.backdrop_blur_px:.1f}px;")

        # 4. Tipografía
        lines.append(f"    --font-primary: {ir.typography.primary_family};")
        lines.append(f"    --font-mono: {ir.typography.mono_family};")
        if ir.typography.secondary_family:
            lines.append(f"    --font-secondary: {ir.typography.secondary_family};")

        for s_name, scale in ir.typography.scales.items():
            safe_name = s_name.replace("_", "-")
            lines.append(f"    --font-size-{safe_name}: {scale.font_size_clamp};")
            lines.append(f"    --line-height-{safe_name}: {scale.line_height_ratio:.3f};")
            lines.append(f"    --letter-spacing-{safe_name}: {scale.letter_spacing_em:.3f}em;")
            weight = 700 if scale.is_headline else 400
            lines.append(f"    --font-weight-{safe_name}: {weight};")

        # 5. Espaciado y bounds
        b = ir.spatial_grammar.bounds
        lines.append(f"    --max-container-w: {b.max_container_width:.1f}px;")
        lines.append(f"    --gutter-min: {b.fluid_gutter_min:.1f}px;")
        lines.append(f"    --gutter-max: {b.fluid_gutter_max:.1f}px;")

        # 6. Motion Tokens (Física de resortes)
        for m_name, mot in ir.motion.tokens.items():
            safe_name = m_name.replace("_", "-")
            lines.append(f"    --duration-{safe_name}: {mot.duration_ms}ms;")
            if mot.linear_spline:
                lines.append(f"    --ease-{safe_name}: {mot.linear_spline};")
            elif mot.spring:
                lines.append(f"    --ease-{safe_name}: {mot.spring.to_css_linear()};")
            else:
                lines.append(f"    --ease-{safe_name}: cubic-bezier(0.16, 1, 0.3, 1);")

        lines.append("  }")
        lines.append("}")
        return "\n".join(lines)

    def _generate_layout_layer(self, ir: DesignIR) -> str:
        """Capa de Layout basada en los 8 Arquetipos Espaciales Asimétricos y Container Queries."""
        arch = ir.spatial_grammar.archetype
        ratio = ir.spatial_grammar.asymmetric_ratio

        layout_css = [
            "@layer layout {",
            "  .aleph-root {",
            "    background-color: var(--color-surface, oklch(1 0 0));",
            "    color: var(--color-on-surface, oklch(0 0 0));",
            "    font-family: var(--font-primary);",
            "    min-height: 100dvh;",
            "    display: flex;",
            "    flex-direction: column;",
            "    position: relative;",
            "  }",
            "  #main-content {",
            "    width: 100%;",
            "    max-width: var(--max-container-w);",
            "    margin-inline: auto;",
            "    padding-inline: clamp(var(--gutter-min), 4vw, var(--gutter-max));",
            "    padding-block: clamp(2rem, 6vh, 6rem);",
            "    container-type: inline-size;",
            "    container-name: aleph-main;",
            "    position: relative;",
            "    z-index: 1;",
            "  }",
        ]

        # Especializaciones de los 8 arquetipos
        if arch == SpatialArchetype.HERO_MONOLITH:
            layout_css.extend([
                "  .archetype-hero-monolith {",
                "    display: grid;",
                "    gap: clamp(2rem, 4vw, 4rem);",
                "    grid-template-columns: 1fr;",
                "  }",
            ])
        elif arch == SpatialArchetype.ASYMMETRIC_SPLIT_70_30:
            layout_css.extend([
                "  .archetype-asymmetric-split-70-30 {",
                "    display: grid;",
                "    gap: clamp(1.5rem, 3vw, 3rem);",
                f"    grid-template-columns: {ratio:.2f}fr 1fr;",
                "  }",
                "  @container aleph-main (max-width: 860px) {",
                "    .archetype-asymmetric-split-70-30 {",
                "      grid-template-columns: 1fr;",
                "    }",
                "  }",
            ])
        elif arch == SpatialArchetype.BENTO_HIERARCHICAL:
            layout_css.extend([
                "  .archetype-bento-hierarchical {",
                "    display: grid;",
                "    gap: clamp(1rem, 2vw, 1.5rem);",
                "    grid-template-columns: repeat(12, 1fr);",
                "  }",
                "  .bento-hero { grid-column: span 8; grid-row: span 2; }",
                "  .bento-side { grid-column: span 4; }",
                "  .bento-wide { grid-column: span 12; }",
                "  .bento-half { grid-column: span 6; }",
                "  @container aleph-main (max-width: 768px) {",
                "    .archetype-bento-hierarchical > * {",
                "      grid-column: span 12 !important;",
                "      grid-row: span 1 !important;",
                "    }",
                "  }",
            ])
        elif arch == SpatialArchetype.EDITORIAL_STAGGERED:
            layout_css.extend([
                "  .archetype-editorial-staggered {",
                "    display: grid;",
                "    gap: clamp(2rem, 5vw, 5rem);",
                "    grid-template-columns: 1fr;",
                "    max-width: 820px;",
                "    margin-inline: auto;",
                "  }",
            ])
        elif arch == SpatialArchetype.TELEMETRY_DASHBOARD:
            layout_css.extend([
                "  .archetype-telemetry-dashboard {",
                "    display: grid;",
                "    gap: 1px;",
                "    background-color: var(--color-border, oklch(0.3 0 0));",
                "    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));",
                "    border: 1px solid var(--color-border, oklch(0.3 0 0));",
                "  }",
            ])
        else:
            # Fallback limpio para otros arquetipos
            layout_css.extend([
                f"  .archetype-{arch.value.replace('_', '-')} {{",
                "    display: flex;",
                "    flex-direction: column;",
                "    gap: clamp(1.5rem, 3vw, 3rem);",
                "  }",
            ])

        layout_css.append("}")
        return "\n".join(layout_css)

    def _generate_components_layer(self, ir: DesignIR) -> str:
        """Capa de Componentes con matriz completa de 7 estados e interactividad Anti-Slop."""
        lame_n = PARADIGM_LAME_EXPONENTS.get(ir.paradigm, 100.0)
        squircle_clip_rule = "    clip-path: var(--morph-squircle-mask);" if (2.5 <= lame_n <= 10.0) else "    /* squircle: standard */"
        comp_css = [
            "@layer components {",
            "  /* Regla de Oro: Titulares nunca superan 3 líneas */",
            "  .aleph-headline {",
            "    display: -webkit-box;",
            "    -webkit-line-clamp: 3;",
            "    -webkit-box-orient: vertical;",
            "    overflow: hidden;",
            "    text-wrap: balance;",
            "    font-weight: var(--font-weight-display, 700);",
            "    letter-spacing: var(--letter-spacing-display, -0.02em);",
            "  }",
            "",
            "  /* Contenedores con Container Queries integrados y Smoked Glass */",
            "  .aleph-card {",
            "    container-type: inline-size;",
            "    background: linear-gradient(180deg, oklch(1 0 0 / 0.05) 0%, oklch(1 0 0 / 0.015) 100%);",
            "    backdrop-filter: blur(24px);",
            "    -webkit-backdrop-filter: blur(24px);",
            "    border: 1px solid oklch(1 0 0 / 0.08);",
            "    border-radius: 20px;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.12), 0 20px 40px -15px oklch(0 0 0 / 0.5);",
            "    padding: clamp(1.25rem, 2vw, 28px);",
            "    position: relative;",
            "    overflow: hidden;",
            "    --mouse-x: -999px;",
            "    --mouse-y: -999px;",
            "    --spotlight-radius: 380px;",
            "    --spotlight-color: oklch(0.85 0.18 200 / 0.12);",
            "    --spotlight-border-color: oklch(0.85 0.18 200 / 0.45);",
            "    transition: transform var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                box-shadow var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                border-color var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1));",
            "  }",
            "  .aleph-card::before, .aleph-spotlight-card::before {",
            "    content: '';",
            "    position: absolute;",
            "    inset: 0;",
            "    border-radius: inherit;",
            "    background: radial-gradient(circle var(--spotlight-radius) at var(--mouse-x) var(--mouse-y), var(--spotlight-color), transparent 80%);",
            "    opacity: 0;",
            "    transition: opacity 250ms cubic-bezier(0.16, 1, 0.3, 1);",
            "    pointer-events: none;",
            "    z-index: 1;",
            "  }",
            "  .aleph-card::after, .aleph-spotlight-card::after {",
            "    content: '';",
            "    position: absolute;",
            "    inset: 0;",
            "    border-radius: inherit;",
            "    padding: 1px;",
            "    background: radial-gradient(circle calc(var(--spotlight-radius) * 0.75) at var(--mouse-x) var(--mouse-y), var(--spotlight-border-color), oklch(1 0 0 / 0.05) 35%, transparent 75%);",
            "    -webkit-mask: linear-gradient(oklch(1 0 0) 0 0) content-box, linear-gradient(oklch(1 0 0) 0 0);",
            "    -webkit-mask-composite: xor;",
            "    mask-composite: exclude;",
            "    opacity: 0;",
            "    transition: opacity 250ms cubic-bezier(0.16, 1, 0.3, 1);",
            "    pointer-events: none;",
            "    z-index: 2;",
            "  }",
            "  .aleph-card:hover, .aleph-spotlight-card:hover {",
            "    transform: translateY(-3px);",
            "    border-color: oklch(0.85 0.18 200 / 0.35);",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.2), 0 25px 50px -12px oklch(0 0 0 / 0.7), 0 0 30px -10px oklch(0.85 0.18 200 / 0.2);",
            "  }",
            "  .aleph-card:hover::before, .aleph-card:hover::after,",
            "  .aleph-spotlight-card:hover::before, .aleph-spotlight-card:hover::after {",
            "    opacity: 1;",
            "  }",
            "",
            "  /* Botones Soberanos: Matriz 7 estados obligatorios */",
            "  .aleph-button {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    gap: 0.5rem;",
            "    padding-inline: 1.5rem;",
            "    padding-block: 0.75rem;",
            "    font-family: var(--font-primary);",
            "    font-size: 0.875rem;",
            "    font-weight: 600;",
            "    border-radius: 9999px;",
            "    background-color: var(--color-primary, oklch(0.85 0.18 200));",
            "    color: oklch(0.12 0.02 240);",
            "    border: 1px solid transparent;",
            "    cursor: pointer;",
            "    user-select: none;",
            "    /* Anti-Slop: NUNCA usar wildcard transition. Solo propiedades transform/opacity/background */",
            "    transition: background-color var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                transform var(--duration-active, 100ms) var(--ease-active, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                border-color var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                box-shadow var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                filter var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                outline-offset 150ms ease;",
            "  }",
            "",
            "  /* 1. Estado HOVER */",
            "  .aleph-button:hover:not(:disabled) {",
            "    filter: brightness(1.08);",
            "    transform: translateY(-1px);",
            "  }",
            "",
            "  /* 2. Estado ACTIVE: Tactilidad háptica obligatoria scale(0.98) */",
            "  .aleph-button:active:not(:disabled) {",
            "    transform: scale(0.98) translateY(0);",
            "    filter: brightness(0.92);",
            "  }",
            "",
            "  /* 3. Estado FOCUS-VISIBLE: Accesibilidad estricta WCAG */",
            "  .aleph-button:focus-visible {",
            "    outline: 2px solid var(--color-primary, oklch(0 0 0));",
            "    outline-offset: 3px;",
            "  }",
            "",
            "  /* 4. Estado DISABLED */",
            "  .aleph-button:disabled {",
            "    opacity: 0.45;",
            "    cursor: not-allowed;",
            "    transform: none !important;",
            "    filter: grayscale(0.5);",
            "  }",
            "",
            "  /* 5. Estado LOADING */",
            "  .aleph-button[aria-busy='true'], .aleph-button.is-loading {",
            "    cursor: wait;",
            "    pointer-events: none;",
            "    opacity: 0.8;",
            "  }",
            "",
            "  /* 6. Estado ERROR */",
            "  .aleph-button.is-error {",
            "    background-color: var(--color-error, oklch(0.58 0.22 25));",
            "    color: oklch(1 0 0);",
            "    border-color: oklch(0.50 0.22 25);",
            "  }",
            "",
            "  /* 7. Estado SUCCESS (Confirmación Háptica Cinética con Pulso Resorte) */",
            "  .aleph-button.is-success, .aleph-interactive.is-success, [data-state='success'] {",
            "    background-color: var(--color-success, oklch(0.72 0.19 155)) !important;",
            "    border-color: oklch(0.60 0.18 155) !important;",
            "    color: oklch(1 0 0) !important;",
            "    box-shadow: 0 0 24px -2px oklch(0.72 0.19 155 / 0.5) !important;",
            "    animation: aleph-spring-success 350ms cubic-bezier(0.34, 1.56, 0.64, 1);",
            "  }",
            "  @keyframes aleph-spring-success {",
            "    0% { transform: scale(0.97); }",
            "    50% { transform: scale(1.04); }",
            "    100% { transform: scale(1.0); }",
            "  }",
            "",
            "  /* TAXONOMÍA ESTRICTA DE ROLES INTERACTIVOS (InteractionRole) */",
            "  /* 1. NAV_LINK: Navegación limpia, sin elevación ni background pesado */",
            "  .aleph-nav-link {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    gap: 0.5rem;",
            "    background: transparent !important;",
            "    color: var(--color-on-surface-muted, oklch(1 0 0 / 0.72));",
            "    font-weight: 500;",
            "    font-size: 0.875rem;",
            "    padding: 0.375rem 0.75rem;",
            "    border-radius: var(--radius-sm, 6px);",
            "    text-decoration: none;",
            "    border: 1px solid transparent !important;",
            "    box-shadow: none !important;",
            "    cursor: pointer;",
            "    transition: color 150ms cubic-bezier(0.16, 1, 0.3, 1),",
            "                background-color 150ms cubic-bezier(0.16, 1, 0.3, 1);",
            "  }",
            "  .aleph-nav-link:hover {",
            "    color: var(--color-on-surface, oklch(1 0 0)) !important;",
            "    background: oklch(1 0 0 / 0.06) !important;",
            "  }",
            "  .aleph-nav-link:active {",
            "    transform: scale(0.99);",
            "  }",
            "  .aleph-nav-link:focus-visible {",
            "    outline: 2px solid var(--color-primary, oklch(0.85 0.18 200));",
            "    outline-offset: 2px;",
            "  }",
            "",
            "  /* 2. ACTION_PRIMARY: CTA supremo, único por jerarquía */",
            "  .aleph-action-primary {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    gap: 0.5rem;",
            "    padding: 0.75rem 1.75rem;",
            "    background-color: var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "    color: var(--color-on-primary, oklch(0.12 0.02 240)) !important;",
            "    font-weight: 600;",
            "    font-size: 0.9375rem;",
            "    border-radius: 9999px;",
            "    border: 1px solid transparent;",
            "    box-shadow: 0 0 24px -4px var(--color-primary-glow, oklch(0.85 0.18 200 / 0.45)),",
            "                inset 0 1px 0 0 oklch(1 0 0 / 0.3);",
            "    cursor: pointer;",
            "    user-select: none;",
            "    transition: transform 120ms cubic-bezier(0.2, 0.9, 0.3, 1.15),",
            "                box-shadow 150ms ease,",
            "                filter 150ms ease;",
            "  }",
            "  .aleph-action-primary:hover:not(:disabled) {",
            "    filter: brightness(1.1);",
            "    transform: translateY(-1.5px);",
            "    box-shadow: 0 0 32px -2px var(--color-primary-glow, oklch(0.85 0.18 200 / 0.65)),",
            "                inset 0 1px 0 0 oklch(1 0 0 / 0.4);",
            "  }",
            "  .aleph-action-primary:active:not(:disabled) {",
            "    transform: scale(0.97) translateY(0);",
            "    filter: brightness(0.92);",
            "    box-shadow: 0 0 12px -2px var(--color-primary-glow, oklch(0.85 0.18 200 / 0.3));",
            "  }",
            "  .aleph-action-primary:focus-visible {",
            "    outline: 2px solid var(--color-primary, oklch(0.85 0.18 200));",
            "    outline-offset: 3px;",
            "    box-shadow: 0 0 0 1px var(--color-surface, oklch(0.12 0.02 240)), 0 0 16px -2px var(--color-primary, oklch(0.85 0.18 200));",
            "  }",
            "",
            "  /* 3. ACTION_SECONDARY: Acción complementaria en Smoked Glass */",
            "  .aleph-action-secondary {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    gap: 0.5rem;",
            "    padding: 0.75rem 1.5rem;",
            "    background: oklch(1 0 0 / 0.05);",
            "    backdrop-filter: blur(12px);",
            "    -webkit-backdrop-filter: blur(12px);",
            "    color: var(--color-on-surface, oklch(1 0 0));",
            "    font-weight: 500;",
            "    font-size: 0.9375rem;",
            "    border-radius: 9999px;",
            "    border: 1px solid oklch(1 0 0 / 0.14);",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.1);",
            "    cursor: pointer;",
            "    transition: background-color 150ms ease,",
            "                border-color 150ms ease,",
            "                transform 120ms cubic-bezier(0.16, 1, 0.3, 1);",
            "  }",
            "  .aleph-action-secondary:hover:not(:disabled) {",
            "    background: oklch(1 0 0 / 0.09);",
            "    border-color: oklch(1 0 0 / 0.25);",
            "    transform: translateY(-1px);",
            "  }",
            "  .aleph-action-secondary:active:not(:disabled) {",
            "    transform: scale(0.98);",
            "    background: oklch(1 0 0 / 0.04);",
            "  }",
            "",
            "  /* 4. ACTION_GHOST: Acción utilitaria sin caja visual de reposo */",
            "  .aleph-action-ghost {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    gap: 0.5rem;",
            "    padding: 0.625rem 1.25rem;",
            "    background: transparent;",
            "    color: var(--color-on-surface-muted, oklch(1 0 0 / 0.7));",
            "    font-weight: 500;",
            "    font-size: 0.875rem;",
            "    border-radius: var(--radius-md, 8px);",
            "    border: 1px solid transparent;",
            "    cursor: pointer;",
            "    transition: color 150ms ease, background-color 150ms ease, transform 100ms ease;",
            "  }",
            "  .aleph-action-ghost:hover:not(:disabled) {",
            "    color: var(--color-on-surface, oklch(1 0 0));",
            "    background: oklch(1 0 0 / 0.06);",
            "  }",
            "  .aleph-action-ghost:active:not(:disabled) {",
            "    transform: scale(0.98);",
            "  }",
            "",
            "  /* 5. BADGE_CHIP: Microchip interactivo */",
            "  .aleph-badge-chip {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    gap: 6px;",
            "    padding: 4px 12px;",
            "    border-radius: 9999px;",
            "    background: oklch(0.85 0.18 200 / 0.06);",
            "    border: 1px solid oklch(0.85 0.18 200 / 0.2);",
            "    color: var(--color-primary, oklch(0.85 0.18 200));",
            "    font-family: var(--font-mono, monospace);",
            "    font-size: 0.75rem;",
            "    font-weight: 600;",
            "    letter-spacing: 0.05em;",
            "    text-transform: uppercase;",
            "    cursor: pointer;",
            "    user-select: none;",
            "    transition: background-color 140ms ease, border-color 140ms ease, transform 120ms cubic-bezier(0.34, 1.56, 0.64, 1);",
            "  }",
            "  .aleph-badge-chip:hover {",
            "    background: oklch(0.85 0.18 200 / 0.12);",
            "    border-color: oklch(0.85 0.18 200 / 0.4);",
            "    transform: translateY(-0.5px);",
            "  }",
            "  .aleph-badge-chip:active, .aleph-badge-chip[aria-pressed='true'] {",
            "    background: var(--color-primary, oklch(0.85 0.18 200));",
            "    color: oklch(0.12 0.02 240);",
            "    transform: scale(0.96);",
            "  }",
            "",
            "  /* 6. ICON_TRIGGER: Disparador táctil simétrico (Target 44x44px) */",
            "  .aleph-icon-trigger {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    min-width: 44px;",
            "    min-height: 44px;",
            "    width: 44px;",
            "    height: 44px;",
            "    padding: 0;",
            "    border-radius: 50%;",
            "    background: oklch(1 0 0 / 0.04);",
            "    border: 1px solid oklch(1 0 0 / 0.1);",
            "    color: var(--color-on-surface, oklch(1 0 0));",
            "    cursor: pointer;",
            "    user-select: none;",
            "    transition: transform 120ms cubic-bezier(0.2, 0.9, 0.3, 1.15),",
            "                background-color 150ms ease,",
            "                border-color 150ms ease;",
            "  }",
            "  .aleph-icon-trigger:hover:not(:disabled) {",
            "    background: oklch(1 0 0 / 0.08);",
            "    border-color: oklch(1 0 0 / 0.25);",
            "    transform: scale(1.05);",
            "  }",
            "  .aleph-icon-trigger:active:not(:disabled) {",
            "    transform: scale(0.92);",
            "    background: oklch(1 0 0 / 0.03);",
            "  }",
            "  .aleph-icon-trigger:focus-visible {",
            "    outline: 2px solid var(--color-primary, oklch(0.85 0.18 200));",
            "    outline-offset: 3px;",
            "  }",
            "",
            "  /* 7. TAB_SELECTOR: Selector segmentado sin CLS */",
            "  .aleph-tab-selector {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    padding: 0.625rem 1.25rem;",
            "    font-family: var(--font-primary);",
            "    font-size: 0.875rem;",
            "    font-weight: 500;",
            "    color: var(--color-on-surface-muted, oklch(1 0 0 / 0.6));",
            "    background: transparent;",
            "    border: none;",
            "    border-radius: var(--radius-md, 8px);",
            "    position: relative;",
            "    cursor: pointer;",
            "    white-space: nowrap;",
            "    transition: color 150ms ease, background-color 150ms ease;",
            "  }",
            "  .aleph-tab-selector:hover {",
            "    color: var(--color-on-surface, oklch(1 0 0));",
            "  }",
            "  .aleph-tab-selector[aria-selected='true'], .aleph-tab-selector.is-selected {",
            "    color: oklch(1 0 0);",
            "    font-weight: 600;",
            "    background: oklch(1 0 0 / 0.08);",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.12), 0 2px 8px oklch(0 0 0 / 0.3);",
            "  }",
            "  .aleph-tab-selector:focus-visible {",
            "    outline: 2px solid var(--color-primary, oklch(0.85 0.18 200));",
            "    outline-offset: 2px;",
            "  }",
            "",
            "  /* 8. METRIC_COUNTER: Cifra telemetría con tabular-nums anti-jitter */",
            "  .aleph-metric-counter {",
            "    font-variant-numeric: tabular-nums;",
            "    font-feature-settings: 'tnum' 1;",
            "    font-family: var(--font-mono, monospace);",
            "    cursor: default;",
            "    transition: color 150ms ease, text-shadow 150ms ease;",
            "  }",
            "  .aleph-metric-counter:hover {",
            "    color: var(--color-primary, oklch(0.85 0.18 200));",
            "    text-shadow: 0 0 12px oklch(0.85 0.18 200 / 0.35);",
            "  }",
            "",
            "  /* Anchor Positioning (si está activo) */",
            "  .has-anchor-target {",
            "    anchor-name: --aleph-active-anchor;",
            "  }",
            "  .aleph-popover {",
            "    position: fixed;",
            "    position-anchor: --aleph-active-anchor;",
            "    top: anchor(bottom);",
            "    left: anchor(center);",
            "    transform: translateX(-50%);",
            "    margin-top: 0.5rem;",
            "    z-index: 50;",
            "    background: var(--color-surface, oklch(1 0 0));",
            "    border: 1px solid var(--color-border, oklch(0.92 0 0));",
            "    border-radius: 0.5rem;",
            "    padding: 1rem;",
            "    box-shadow: var(--shadow-lg, 0 10px 15px -3px oklch(0 0 0 / 0.1));",
            "  }",
            "",
            "  /* 1. NAVBAR: Píldora Flotante de Cristal Oscuro (Plan V5 - Awwwards Tier) */",
            "  .aleph-navbar {",
            "    max-width: min(1200px, calc(100% - 40px));",
            "    margin: 20px auto 40px auto;",
            "    padding: 12px 24px;",
            "    overflow: hidden;",
            "    background: oklch(0.12 0.02 240 / 0.7);",
            "    backdrop-filter: blur(20px);",
            "    -webkit-backdrop-filter: blur(20px);",
            "    border: 1px solid oklch(1 0 0 / 0.08);",
            "    border-radius: 9999px;",
            "    display: flex;",
            "    align-items: center;",
            "    justify-content: space-between;",
            "    gap: 1.25rem;",
            "    width: 100%;",
            "    box-sizing: border-box;",
            "    box-shadow: 0 20px 40px -15px oklch(0 0 0 / 0.6), inset 0 1px 0 0 oklch(1 0 0 / 0.1);",
            "  }",
            "  .aleph-navbar .aleph-nav-link,",
            "  .aleph-navbar a,",
            "  .aleph-navbar button:not(:last-child) {",
            "    background: transparent !important;",
            "    color: oklch(1 0 0 / 0.75) !important;",
            "    border: 1px solid transparent !important;",
            "    box-shadow: none !important;",
            "    white-space: nowrap;",
            "    font-size: 0.875rem;",
            "    font-weight: 500;",
            "    padding: 6px 14px;",
            "    border-radius: 9999px;",
            "    transition: color 150ms ease, background-color 150ms ease;",
            "    text-decoration: none;",
            "    display: inline-flex;",
            "    align-items: center;",
            "  }",
            "  .aleph-navbar .aleph-nav-link:hover,",
            "  .aleph-navbar a:hover,",
            "  .aleph-navbar button:not(:last-child):hover {",
            "    color: oklch(1 0 0) !important;",
            "    background: oklch(1 0 0 / 0.07) !important;",
            "  }",
            "  .aleph-navbar .aleph-badge {",
            "    background: oklch(1 0 0 / 0.04);",
            "    border: 1px solid oklch(1 0 0 / 0.12);",
            "    color: oklch(1 0 0 / 0.9);",
            "    font-size: 0.8125rem;",
            "    font-family: var(--font-mono, monospace);",
            "    font-weight: 600;",
            "    padding: 4px 14px;",
            "    border-radius: 9999px;",
            "    white-space: nowrap;",
            "    letter-spacing: 0.04em;",
            "  }",
            "  .aleph-navbar button:last-child,",
            "  .aleph-navbar .aleph-nav-cta {",
            "    background: var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "    color: oklch(0.12 0.02 240) !important;",
            "    font-weight: 600 !important;",
            "    border-radius: 9999px !important;",
            "    padding: 8px 22px !important;",
            "    border: 1px solid transparent !important;",
            "    box-shadow: 0 0 20px -3px var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "    white-space: nowrap;",
            "    transition: filter 180ms ease, transform 180ms ease !important;",
            "  }",
            "  .aleph-navbar button:last-child:hover,",
            "  .aleph-navbar .aleph-nav-cta:hover {",
            "    filter: brightness(1.1) !important;",
            "    transform: translateY(-1px) !important;",
            "  }",
            "",
            "  /* 2. HERO STAGE & DRAMATIC HIERARCHY */",
            "  .aleph-hero-stage {",
            "    display: flex;",
            "    flex-direction: column;",
            "    align-items: flex-start;",
            "    gap: 1.25rem;",
            "    padding: 2.5rem 0 4rem 0;",
            "    width: 100%;",
            "    max-width: 900px;",
            "  }",
            "  .aleph-hero-stage .aleph-badge,",
            "  .aleph-hero-badge {",
            "    display: inline-flex;",
            "    align-items: center;",
            "    gap: 8px;",
            "    padding: 6px 14px;",
            "    border-radius: 9999px;",
            "    background: oklch(0.85 0.18 200 / 0.08) !important;",
            "    border: 1px solid oklch(0.85 0.18 200 / 0.25) !important;",
            "    color: oklch(0.82 0.12 205) !important;",
            "    font-size: 0.75rem !important;",
            "    font-family: var(--font-mono, monospace) !important;",
            "    font-weight: 600 !important;",
            "    letter-spacing: 0.08em !important;",
            "    text-transform: uppercase;",
            "    box-shadow: 0 0 15px -3px oklch(0.85 0.18 200 / 0.2);",
            "    margin-bottom: 0.5rem;",
            "  }",
            "  .aleph-hero-stage .aleph-headline,",
            "  .aleph-hero-stage h1 {",
            "    font-size: clamp(2.8rem, 5vw, 4.5rem) !important;",
            "    line-height: 1.04 !important;",
            "    letter-spacing: -0.03em !important;",
            "    max-width: 18ch !important;",
            "    background: linear-gradient(180deg, oklch(1 0 0) 0%, oklch(1 0 0 / 0.65) 100%) !important;",
            "    -webkit-background-clip: text !important;",
            "    -webkit-text-fill-color: transparent !important;",
            "    text-wrap: balance !important;",
            "    margin-top: 12px;",
            "    margin-bottom: 16px;",
            "  }",
            "  .aleph-hero-stage .aleph-text {",
            "    font-size: 1.125rem;",
            "    line-height: 1.6;",
            "    max-width: 52ch;",
            "    color: oklch(1 0 0 / 0.72);",
            "  }",
            "  .aleph-hero-actions {",
            "    display: flex;",
            "    flex-direction: row;",
            "    flex-wrap: wrap;",
            "    gap: 16px;",
            "    align-items: center;",
            "    margin-top: 32px;",
            "  }",
            "  .aleph-button-primary,",
            "  .aleph-hero-actions .aleph-button:first-child {",
            "    background: var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "    color: oklch(0.12 0.02 240) !important;",
            "    font-weight: 600 !important;",
            "    border-radius: 9999px !important;",
            "    padding: 12px 28px !important;",
            "    border: 1px solid transparent !important;",
            "    box-shadow: 0 0 25px -5px var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "    transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease !important;",
            "  }",
            "  .aleph-button-primary:hover,",
            "  .aleph-hero-actions .aleph-button:first-child:hover {",
            "    filter: brightness(1.1) !important;",
            "    transform: translateY(-2px) !important;",
            "    box-shadow: 0 0 35px 0px var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "  }",
            "  .aleph-button-ghost,",
            "  .aleph-button-secondary,",
            "  .aleph-hero-actions .aleph-button:nth-child(2) {",
            "    background: oklch(1 0 0 / 0.04) !important;",
            "    color: oklch(1 0 0) !important;",
            "    border: 1px solid oklch(1 0 0 / 0.15) !important;",
            "    backdrop-filter: blur(12px) !important;",
            "    -webkit-backdrop-filter: blur(12px) !important;",
            "    border-radius: 9999px !important;",
            "    padding: 12px 28px !important;",
            "    font-weight: 500 !important;",
            "    transition: background-color 180ms ease, border-color 180ms ease, transform 180ms ease !important;",
            "  }",
            "  .aleph-button-ghost:hover,",
            "  .aleph-button-secondary:hover,",
            "  .aleph-hero-actions .aleph-button:nth-child(2):hover {",
            "    background: oklch(1 0 0 / 0.09) !important;",
            "    border-color: oklch(1 0 0 / 0.3) !important;",
            "    transform: translateY(-2px) !important;",
            "  }",
            "",
            "  /* 3. SUPERFICIES SMOKED GLASSMORPHISM (METRIC TICKER & BENTO CARDS) */",
            "  .aleph-metric-ticker {",
            "    display: grid;",
            "    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));",
            "    gap: 1.5rem;",
            "    padding: 28px !important;",
            "    margin: 2.5rem 0;",
            "    width: 100%;",
            "    box-sizing: border-box;",
            "    background-color: oklch(0.18 0.03 260 / 0.8) !important;",
            "    background: linear-gradient(180deg, oklch(0.18 0.03 260 / 0.75) 0%, oklch(0.12 0.02 250 / 0.85) 100%) !important;",
            "    backdrop-filter: blur(24px) saturate(180%) !important;",
            "    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;",
            "    border: 1px solid oklch(1 0 0 / 0.08) !important;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.12), 0 20px 40px -15px oklch(0 0 0 / 0.5) !important;",
            "    border-radius: 24px !important;",
            "  }",
            "  .aleph-metric-item {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 0.375rem;",
            "  }",
            "  .aleph-metric-value {",
            "    font-size: 2.25rem;",
            "    font-weight: 700;",
            "    color: oklch(1 0 0);",
            "    font-family: var(--font-mono, monospace);",
            "    letter-spacing: -0.02em;",
            "  }",
            "  .aleph-metric-delta {",
            "    font-size: 0.75rem;",
            "    font-weight: 600;",
            "    color: oklch(0.72 0.19 155);",
            "    font-family: var(--font-mono, monospace);",
            "  }",
            "  .aleph-metric-label {",
            "    font-size: 0.8125rem;",
            "    color: oklch(1 0 0 / 0.65);",
            "    text-transform: uppercase;",
            "    letter-spacing: 0.06em;",
            "    font-family: var(--font-mono, monospace);",
            "  }",
            "  .tabular-nums {",
            "    font-variant-numeric: tabular-nums;",
            "  }",
            "  .aleph-bento-grid {",
            "    display: grid;",
            "    grid-template-columns: repeat(12, 1fr);",
            "    gap: 1.5rem;",
            "    padding: 3rem 0;",
            "    width: 100%;",
            "  }",
            "  .aleph-card,",
            "  .aleph-bento-card {",
            "    container-type: inline-size;",
            squircle_clip_rule if squircle_clip_rule else "    /* squircle: standard */",
            "    background-color: oklch(0.18 0.03 260 / 0.8) !important;",
            "    background: linear-gradient(180deg, oklch(0.18 0.03 260 / 0.75) 0%, oklch(0.12 0.02 250 / 0.85) 100%) !important;",
            "    backdrop-filter: blur(24px) saturate(180%) !important;",
            "    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;",
            "    border: 1px solid oklch(1 0 0 / 0.08) !important;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.12), 0 20px 40px -15px oklch(0 0 0 / 0.5) !important;",
            "    border-radius: 24px !important;",
            "    padding: 28px !important;",
            "    box-sizing: border-box;",
            "    transition: transform var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                border-color var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1)),",
            "                box-shadow var(--duration-hover, 180ms) var(--ease-hover, cubic-bezier(0.16, 1, 0.3, 1));",
            "  }",
            "  .aleph-card:hover,",
            "  .aleph-bento-card:hover {",
            "    transform: translateY(-3px);",
            "    border-color: oklch(0.85 0.18 200 / 0.35) !important;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.2), 0 25px 50px -12px oklch(0 0 0 / 0.7), 0 0 30px -10px oklch(0.85 0.18 200 / 0.2) !important;",
            "  }",
            "  .aleph-card-title {",
            "    font-size: 1.25rem;",
            "    font-weight: 600;",
            "    color: oklch(1 0 0);",
            "    margin-bottom: 0.5rem;",
            "  }",
            "  .aleph-card-desc {",
            "    font-size: 0.9375rem;",
            "    line-height: 1.6;",
            "    color: oklch(1 0 0 / 0.7);",
            "  }",
            "  .aleph-telemetry-panel,",
            "  .aleph-tabs,",
            "  .aleph-comparison-table,",
            "  .aleph-editorial-block,",
            "  .aleph-cta-banner {",
            "    background: linear-gradient(180deg, oklch(1 0 0 / 0.05) 0%, oklch(1 0 0 / 0.015) 100%) !important;",
            "    backdrop-filter: blur(24px) !important;",
            "    -webkit-backdrop-filter: blur(24px) !important;",
            "    border: 1px solid oklch(1 0 0 / 0.08) !important;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.12), 0 20px 40px -15px oklch(0 0 0 / 0.5) !important;",
            "    border-radius: 20px !important;",
            "    padding: 28px !important;",
            "    box-sizing: border-box;",
            "  }",
            "  .aleph-telemetry-panel {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 1.25rem;",
            "    margin: 2.5rem 0;",
            "    width: 100%;",
            "  }",
            "  .aleph-cta-banner {",
            "    display: flex;",
            "    flex-direction: column;",
            "    align-items: center;",
            "    text-align: center;",
            "    gap: 1.5rem;",
            "    padding: 4rem 2rem !important;",
            "    margin: 3.5rem 0;",
            "    width: 100%;",
            "  }",
            "  .aleph-footer {",
            "    display: grid;",
            "    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));",
            "    gap: 2rem;",
            "    padding: 3.5rem 0 2rem 0;",
            "    width: 100%;",
            "    border-top: 1px solid oklch(1 0 0 / 0.08);",
            "  }",
            "  .col-span-12 { grid-column: span 12 / span 12; }",
            "  .col-span-8 { grid-column: span 8 / span 8; }",
            "  .col-span-6 { grid-column: span 6 / span 6; }",
            "  .col-span-4 { grid-column: span 4 / span 4; }",
            "  .col-span-3 { grid-column: span 3 / span 3; }",
            "",
            "  .aleph-tabs {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 1.5rem;",
            "    width: 100%;",
            "    margin: 2rem 0;",
            "  }",
            "  .aleph-comparison-table {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 1.25rem;",
            "    width: 100%;",
            "    margin: 2rem 0;",
            "  }",
            "  .aleph-pricing-matrix {",
            "    display: grid;",
            "    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));",
            "    gap: 1.5rem;",
            "    width: 100%;",
            "    padding: 2rem 0;",
            "  }",
            "  .aleph-editorial-block {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 1.25rem;",
            "    width: 100%;",
            "    margin: 2rem 0;",
            "    border-left: 3px solid var(--color-primary, oklch(0.85 0.18 200)) !important;",
            "  }",
            "  .aleph-island {",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 1rem;",
            "    width: 100%;",
            "    max-width: 100%;",
            "    box-sizing: border-box;",
            "    overflow: hidden;",
            "    padding: clamp(1rem, 3vw, 28px);",
            "    background: oklch(0.10 0.02 240 / 0.9);",
            "    border: 1px solid oklch(1 0 0 / 0.08);",
            "    border-radius: 20px;",
            "    box-shadow: inset 0 1px 0 0 oklch(1 0 0 / 0.1), 0 20px 40px -15px oklch(0 0 0 / 0.5);",
            "  }",
            "  .aleph-code-block {",
            "    width: 100%;",
            "    max-width: 100%;",
            "    box-sizing: border-box;",
            "    overflow-x: auto;",
            "    background: oklch(0 0 0 / 0.75);",
            "    border: 1px solid oklch(1 0 0 / 0.08);",
            "    border-radius: 0.75rem;",
            "    padding: 1.25rem;",
            "    font-family: var(--font-mono, monospace);",
            "    font-size: 0.8125rem;",
            "    line-height: 1.5;",
            "    white-space: pre;",
            "    tab-size: 2;",
            "  }",
            "  .aleph-code-block code {",
            "    font-family: inherit;",
            "    font-size: inherit;",
            "    white-space: inherit;",
            "    display: block;",
            "  }",
            "",
            "  @media (max-width: 768px) {",
            "    .aleph-navbar {",
            "      border-radius: 24px;",
            "      padding: 14px 18px;",
            "      flex-wrap: wrap;",
            "      gap: 0.75rem;",
            "    }",
            "    .aleph-navbar .aleph-nav-link,",
            "    .aleph-navbar a,",
            "    .aleph-navbar button:not(:last-child) {",
            "      padding: 4px 10px;",
            "      font-size: 0.8125rem;",
            "    }",
            "    .aleph-hero-actions {",
            "      flex-direction: column;",
            "      align-items: stretch;",
            "      width: 100%;",
            "    }",
            "    .aleph-hero-actions .aleph-button {",
            "      width: 100%;",
            "      text-align: center;",
            "    }",
            "    .aleph-bento-grid > * {",
            "      grid-column: span 12 !important;",
            "    }",
            "    .aleph-pricing-matrix {",
            "      grid-template-columns: 1fr;",
            "    }",
            "    .aleph-footer {",
            "      grid-template-columns: 1fr;",
            "    }",
            "    .aleph-tabs, .aleph-comparison-table, .aleph-editorial-block, .aleph-telemetry-panel, .aleph-metric-ticker, .aleph-card {",
            "      padding: clamp(1rem, 3vw, 1.5rem) !important;",
            "    }",
            "  }",
            "}",
        ]
        if AlephVisualStageSynthesizer is not None:
            comp_css.append(AlephVisualStageSynthesizer.get_stage_css())
        return "\n".join(comp_css)

    def _generate_reduced_motion_layer(self, ir: DesignIR) -> str:
        """Fallo seguro inquebrantable para usuarios con sensibilidad motriz/vestibular."""
        return """@layer utilities {
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
      transform: none !important;
    }
    .aleph-shader-canvas {
      display: none !important;
    }
  }
}"""

    # =========================================================================
    # RENDERIZADO DE NODOS DEL AST (IRComponent)
    # =========================================================================

    def _render_component(self, comp: IRComponent, indent: int = 2) -> str:
        """Renderiza recursivamente un componente del IR en HTML5 semántico."""
        pad = " " * indent
        c_type = comp.component_type.lower()
        tag = "div"
        extra_attrs: List[str] = [f'id="{html.escape(comp.id)}"']
        classes: List[str] = [f"aleph-comp-{c_type}"]

        # Asignación de tags semánticos según intención
        int_role = getattr(comp, "interaction_role", None)
        if int_role is not None:
            r_str = int_role.value if hasattr(int_role, "value") else str(int_role)
            classes.append(f"aleph-{r_str.replace('_', '-')}")
            if r_str == "nav_link":
                tag = "a"
                classes.append("aleph-nav-link")
                if "href" in comp.props:
                    extra_attrs.append(f'href="{html.escape(str(comp.props["href"]))}"')
                else:
                    extra_attrs.append('href="#"')
            elif r_str == "action_primary":
                tag = "button"
                classes.extend(["aleph-button", "aleph-action-primary"])
                extra_attrs.append('type="button"')
            elif r_str == "action_secondary":
                tag = "button"
                classes.extend(["aleph-button", "aleph-action-secondary"])
                extra_attrs.append('type="button"')
            elif r_str == "action_ghost":
                tag = "button"
                classes.extend(["aleph-button", "aleph-action-ghost"])
                extra_attrs.append('type="button"')
            elif r_str == "badge_chip":
                tag = "button" if comp.is_interactive else "span"
                classes.append("aleph-badge-chip")
                if comp.is_interactive:
                    extra_attrs.append('type="button"')
            elif r_str == "icon_trigger":
                tag = "button"
                classes.extend(["aleph-button", "aleph-icon-trigger"])
                extra_attrs.append('type="button"')
                aria_lbl = comp.props.get("aria_label") or comp.props.get("aria-label", "Trigger")
                extra_attrs.append(f'aria-label="{html.escape(str(aria_lbl))}"')
            elif r_str == "tab_selector":
                tag = "button"
                classes.append("aleph-tab-selector")
                extra_attrs.append('type="button"')
                extra_attrs.append('role="tab"')
                sel = comp.props.get("selected", False) or comp.props.get("is_active", False)
                extra_attrs.append(f'aria-selected="{"true" if sel else "false"}"')
            elif r_str == "metric_counter":
                tag = "div"
                classes.extend(["aleph-metric-counter", "tabular-nums"])
        elif c_type in ("headline", "heading", "title"):
            tag = "h1" if comp.task_phase == TaskPhase.ORIENT else "h2"
            classes.append("aleph-headline")
            if comp.type_scale:
                classes.append(f"scale-{comp.type_scale.replace('_', '-')}")
        elif c_type in ("button", "action"):
            if "href" in comp.props:
                tag = "a"
                extra_attrs.append(f'href="{html.escape(str(comp.props["href"]))}"')
                classes.append("aleph-nav-link")
            else:
                tag = "button"
                classes.append("aleph-button")
                extra_attrs.append('type="button"')

            variant = comp.props.get("variant")
            if variant == "primary":
                classes.append("aleph-button-primary")
            elif variant in ("ghost", "link"):
                classes.append("aleph-button-ghost")
            elif variant == "secondary":
                classes.append("aleph-button-secondary")

            if comp.task_phase == TaskPhase.CONFIRM:
                classes.append("aleph-button-confirm")
        elif c_type in ("hero_actions", "actions_group", "actions"):
            tag = "div"
            classes.append("aleph-hero-actions")
        elif c_type in ("card", "panel", "bento_item", "bento_card"):
            tag = "article"
            classes.extend(["aleph-card", "aleph-spotlight-card"])
            if c_type in ("bento_item", "bento_card"):
                classes.append("aleph-bento-card")
            extra_attrs.append('data-spotlight="true"')
        elif c_type in ("nav", "navbar", "navigation"):
            tag = "nav"
            classes.extend(["aleph-nav", "aleph-navbar"])
            extra_attrs.append('role="navigation"')
        elif c_type in ("hero_stage", "hero"):
            tag = "header"
            classes.extend(["aleph-hero-stage", "aleph-section"])
        elif c_type in ("metric_ticker", "ticker"):
            tag = "section"
            classes.append("aleph-metric-ticker")
        elif c_type in ("bento_grid", "grid"):
            tag = "section"
            classes.extend(["aleph-bento-grid", "bento-hypergrid"])
        elif c_type in ("telemetry_panel", "telemetry"):
            tag = "section"
            classes.extend(["aleph-telemetry-panel", "aleph-card"])
        elif c_type in ("interactive_tabs", "tabs"):
            tag = "div"
            classes.append("aleph-tabs")
        elif c_type in ("comparison_table", "table"):
            tag = "div"
            classes.append("aleph-comparison-table")
        elif c_type in ("pricing_matrix", "pricing"):
            tag = "section"
            classes.append("aleph-pricing-matrix")
        elif c_type in ("editorial_block", "editorial"):
            tag = "article"
            classes.append("aleph-editorial-block")
        elif c_type in ("cta_banner", "cta"):
            tag = "section"
            classes.append("aleph-cta-banner")
        elif c_type in ("footer",):
            tag = "footer"
            classes.append("aleph-footer")
            extra_attrs.append('role="contentinfo"')
        elif c_type in ("section", "container"):
            tag = "section"
            classes.append("aleph-section")
        elif c_type in ("badge", "tag"):
            tag = "span"
            classes.append("aleph-badge")
            variant = comp.props.get("variant")
            if variant:
                classes.append(f"aleph-badge-{variant}")
        elif c_type in ("text", "paragraph", "subtext"):
            tag = "p"
            classes.append("aleph-text")
        elif c_type in ("code_island", "island"):
            tag = "section"
            classes.append("aleph-island")
            extra_attrs.append(f'data-island-id="{html.escape(comp.id)}"')

        # Soporte para grid_span y tabular_nums
        grid_span = comp.props.get("grid_span") or comp.spatial_intent.get("grid_span")
        if grid_span:
            classes.append(str(grid_span).replace(" ", "-"))
        if comp.props.get("tabular_nums"):
            classes.append("tabular-nums")

        # Accesibilidad ARIA
        aria_label = comp.props.get("aria_label")
        if aria_label:
            extra_attrs.append(f'aria-label="{html.escape(str(aria_label))}"')
        role_val = comp.props.get("role")
        if role_val:
            extra_attrs.append(f'role="{html.escape(str(role_val))}"')

        # Estado inicial
        curr_state = comp.props.get("state", "default")
        if curr_state != "default":
            classes.append(f"state-{curr_state}")
            if curr_state == "disabled":
                extra_attrs.append("disabled")
            elif curr_state == "loading":
                extra_attrs.append('aria-busy="true"')

        class_str = " ".join(classes)
        attr_str = f'class="{class_str}" ' + " ".join(extra_attrs)

        # Generación de contenido enriquecido (métricas, código, copy)
        content_parts: List[str] = []
        if "value" in comp.props and "label" in comp.props:
            val_txt = html.escape(str(comp.props["value"]))
            lbl_txt = html.escape(str(comp.props["label"]))
            delta_html = ""
            if "delta" in comp.props:
                d_txt = html.escape(str(comp.props["delta"]))
                delta_html = f'<span class="aleph-metric-delta">{d_txt}</span>'
            content_parts.append(
                f'<div class="aleph-metric-item"><span class="aleph-metric-value tabular-nums">{val_txt}</span>{delta_html}<span class="aleph-metric-label">{lbl_txt}</span></div>'
            )
        elif "text" in comp.props:
            content_parts.append(html.escape(str(comp.props["text"])))
        elif "label" in comp.props:
            content_parts.append(html.escape(str(comp.props["label"])))
        elif "title" in comp.props:
            if c_type in ("headline", "heading", "title"):
                content_parts.append(html.escape(str(comp.props["title"])))
            elif c_type not in ("button", "action", "hero_stage", "navbar", "nav", "bento_grid", "section", "container"):
                content_parts.append(f'<h3 class="aleph-card-title">{html.escape(str(comp.props["title"]))}</h3>')
                if "description" in comp.props:
                    content_parts.append(f'<p class="aleph-card-desc">{html.escape(str(comp.props["description"]))}</p>')

                # Síntesis Soberana de Escenografía Visual Interna (Anti-Empty Bento Card Syndrome)
                if c_type in ("card", "panel", "bento_item", "bento_card", "telemetry_panel", "telemetry"):
                    stage_type = comp.props.get("visual_stage")
                    if not stage_type and (c_type in ("bento_item", "bento_card", "telemetry_panel", "telemetry") or comp.props.get("synthesize_stage")):
                        if AlephVisualStageSynthesizer is not None:
                            stage_type = AlephVisualStageSynthesizer.infer_stage_type(
                                card_title=str(comp.props.get("title", "")),
                                card_desc=str(comp.props.get("description", "")),
                                badge=str(comp.props.get("badge", "")),
                                paradigm=getattr(self, "_current_paradigm", "cyber_telemetry"),
                                card_index=int(hashlib.md5(comp.id.encode()).hexdigest()[:8], 16) % 5,
                            )
                    if stage_type and AlephVisualStageSynthesizer is not None:
                        stage_cfg = VisualStageConfig(
                            stage_type=VisualStageType(stage_type) if isinstance(stage_type, str) else stage_type,
                            title=str(comp.props.get("stage_title") or comp.props.get("title") or ""),
                            badge_text=str(comp.props.get("stage_badge") or comp.props.get("badge") or ""),
                            metric_value=str(comp.props.get("metric_value") or comp.props.get("stage_value") or comp.props.get("value")) if (comp.props.get("metric_value") or comp.props.get("stage_value") or comp.props.get("value")) else None,
                            metric_unit=str(comp.props.get("metric_unit") or comp.props.get("stage_unit")) if (comp.props.get("metric_unit") or comp.props.get("stage_unit")) else None,
                            props=comp.props,
                            card_title=str(comp.props.get("title", "")),
                            card_desc=str(comp.props.get("description", "")),
                            paradigm=getattr(self, "_current_paradigm", "cyber_telemetry"),
                        )
                        stage_html = AlephVisualStageSynthesizer.render_stage_html(
                            stage_type,
                            config=stage_cfg,
                            palette=getattr(self, "_palette", None),
                        )
                        content_parts.append(f"\n{stage_html}\n")
                    elif c_type in ("bento_card", "bento_item"):
                        content_parts.append(
                            '<div class="aleph-bento-icon-wrapper" style="margin-bottom:12px;"><svg class="aleph-bento-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>'
                        )

        if c_type in ("telemetry_panel", "telemetry") and not comp.props.get("title") and not comp.props.get("value") and not comp.children:
            if AlephVisualStageSynthesizer is not None:
                stage_type = comp.props.get("visual_stage") or VisualStageType.BEZIER_CHART
                stage_cfg = VisualStageConfig(
                    stage_type=VisualStageType(stage_type) if isinstance(stage_type, str) else stage_type,
                    props=comp.props,
                    card_title=str(comp.props.get("title", "")),
                    card_desc=str(comp.props.get("description", "")),
                    paradigm=getattr(self, "_current_paradigm", "cyber_telemetry"),
                )
                stage_html = AlephVisualStageSynthesizer.render_stage_html(
                    stage_type,
                    config=stage_cfg,
                    palette=getattr(self, "_palette", None),
                )
                content_parts.append(f"\n{stage_html}\n")

        if "code_snippet" in comp.props:
            snippet_txt = html.escape(str(comp.props["code_snippet"]))
            content_parts.append(f'<pre class="aleph-code-block"><code>{snippet_txt}</code></pre>')

        content_text = "".join(content_parts)

        # Renderizar hijos si existen
        if comp.children:
            if c_type in ("hero_stage", "hero"):
                non_buttons = [c for c in comp.children if c.component_type not in ("button", "action", "hero_actions", "actions_group")]
                buttons = [c for c in comp.children if c.component_type in ("button", "action")]
                hero_actions_nodes = [c for c in comp.children if c.component_type in ("hero_actions", "actions_group")]

                if buttons and not hero_actions_nodes:
                    rendered_non_buttons = [self._render_component(nb, indent=indent + 2) for nb in non_buttons]
                    rendered_buttons = "\n".join(self._render_component(b, indent=indent + 4) for b in buttons)
                    actions_wrapper = f'{pad}  <div class="aleph-hero-actions">\n{rendered_buttons}\n{pad}  </div>'
                    all_rendered = rendered_non_buttons + [actions_wrapper]
                    children_str = "\n".join(all_rendered)
                    inner = f"\n{children_str}\n{pad}"
                    return f"{pad}<{tag} {attr_str}>{content_text}{inner}</{tag}>"

            children_str = "\n".join(
                self._render_component(child, indent=indent + 2)
                for child in comp.children
            )
            inner = f"\n{children_str}\n{pad}"
            return f"{pad}<{tag} {attr_str}>{content_text}{inner}</{tag}>"
        else:
            return f"{pad}<{tag} {attr_str}>{content_text}</{tag}>"

    def _generate_shader_runtime(self, ir: DesignIR) -> str:
        """Inyecta un runtime ligero de WebGL si el IR incluye shaders soberanos."""
        if not ir.assets.shaders:
            return ""

        first_shader = next(iter(ir.assets.shaders.values()))
        shader_code = getattr(first_shader, "glsl_source", getattr(first_shader, "fragment_glsl", ""))
        shader_code = shader_code.replace("`", "\\`")

        # Shader cuántico de alta fidelidad si viene el de fallback estático
        if not shader_code or "void main() { gl_FragColor = vec4(0.0, 0.94, 1.0, 1.0); }" in shader_code:
            shader_code = """#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.25;
    float d = length(uv);
    float a = atan(uv.y, uv.x);
    float rings = sin(d * 16.0 - t * 2.5 + sin(a * 4.0 + t));
    float glow = 0.045 / (abs(rings) + 0.05);
    vec3 col = vec3(0.0, 0.94, 1.0) * glow;
    col += vec3(0.06, 0.0, 0.22) * (1.0 - min(1.0, d * 0.8));
    fragColor = vec4(col, min(0.85, glow * 0.9));
}"""

        return f"""  <script>
    /* Aleph Sovereign WebGL 2.0 Auto-Pausing Shader Runtime */
    (function() {{
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const canvas = document.createElement('canvas');
      canvas.className = 'aleph-shader-canvas';
      canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:0.65;';
      document.body.prepend(canvas);
      const gl = canvas.getContext('webgl2');
      if (!gl) return;
      // Pipeline WebGL compilado de bajo consumo
      const vsSource = `#version 300 es\\nin vec2 position;void main(){{gl_Position=vec4(position,0.0,1.0);}}`;
      const fsSource = `{shader_code}`;
      function compile(type, src) {{
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        return s;
      }}
      const program = gl.createProgram();
      gl.attachShader(program, compile(gl.VERTEX_SHADER, vsSource));
      gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fsSource));
      gl.linkProgram(program);
      const posBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
      gl.useProgram(program);
      const posLoc = gl.getAttribLocation(program, 'position');
      gl.enableVertexAttribArray(posLoc);
      gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
      const uRes = gl.getUniformLocation(program, 'u_resolution');
      const uTime = gl.getUniformLocation(program, 'u_time');
      let animId, isVisible = true;
      function resize() {{
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        gl.viewport(0, 0, canvas.width, canvas.height);
      }}
      window.addEventListener('resize', resize);
      resize();
      function render(time) {{
        if (!isVisible) return;
        gl.uniform2f(uRes, canvas.width, canvas.height);
        gl.uniform1f(uTime, time * 0.001);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
        animId = requestAnimationFrame(render);
      }}
      document.addEventListener('visibilitychange', () => {{
        isVisible = !document.hidden;
        if (isVisible) animId = requestAnimationFrame(render);
        else cancelAnimationFrame(animId);
      }});
      animId = requestAnimationFrame(render);
    }})();
  </script>"""

    def _generate_spotlight_runtime(self, ir: DesignIR) -> str:
        """Runtime ultra-eficiente de Spotlight Cursor Tracking (Zero-Jank en GPU con rAF coalescing)."""
        return """  <script>
    /* Aleph Sovereign Zero-Jank Spotlight Cursor Engine */
    (function() {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      if (window.matchMedia('(hover: none) and (pointer: coarse)').matches) return;

      let mouseX = -999, mouseY = -999;
      let rafPending = false;
      const elements = [];

      function updateCards() {
        for (let i = 0; i < elements.length; i++) {
          const el = elements[i];
          const rect = el.getBoundingClientRect();
          const x = mouseX - rect.left;
          const y = mouseY - rect.top;
          if (x >= -120 && x <= rect.width + 120 && y >= -120 && y <= rect.height + 120) {
            el.style.setProperty('--mouse-x', x.toFixed(1) + 'px');
            el.style.setProperty('--mouse-y', y.toFixed(1) + 'px');
          }
        }
        rafPending = false;
      }

      function onPointerMove(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (!rafPending) {
          rafPending = true;
          requestAnimationFrame(updateCards);
        }
      }

      function init() {
        const cards = document.querySelectorAll('.aleph-card, .aleph-spotlight-card, .aleph-bento-card, .aleph-telemetry-panel');
        cards.forEach(function(c) { elements.push(c); });
        if (elements.length > 0) {
          window.addEventListener('pointermove', onPointerMove, { passive: true });
        }
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
      } else {
        init();
      }
    })();
  </script>"""

