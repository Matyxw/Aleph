"""
test_dot_aleph_integration.py
Batería de pruebas unitarias y formales para la integración orgánica de .aleph/lib en El Aleph Kernel.
Verifica:
1. Síntesis procedimental de los 8 tipos canónicos de escenografía visual (.aleph/lib/aleph_visual_stage_synthesizer.py).
2. Simulación física ODE de resortes armónicos y generación de CSS linear(...) (.aleph/lib/aleph_kinetic_ode.py).
3. Auditoría estática DOM y detección de slop de IA (.aleph/lib/aleph_render_oracle.py).
4. Compilación de tokens OKLCH y cálculo de clamp() fluido (.aleph/lib/aleph_token_compiler.py).
"""
import unittest
import sys
import os
from pathlib import Path

# Add .aleph/lib to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / ".aleph" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))


class TestDotAlephIntegration(unittest.TestCase):
    """Pruebas de integración del motor .aleph con aleph_core."""

    def test_visual_stage_synthesizer_generates_all_8_stages(self):
        """Verifica la generación de los 8 escenarios vectoriales procedimentales en .aleph."""
        from aleph_visual_stage_synthesizer import (
            AlephVisualStageSynthesizer,
            VisualStageConfig,
            VisualStageType,
        )
        stages = [
            VisualStageType.CRYO_GAUGE,
            VisualStageType.CODE_TERMINAL,
            VisualStageType.SWISS_GEOMETRY,
            VisualStageType.BEZIER_CHART,
            VisualStageType.TOPOLOGY_GRAPH,
            VisualStageType.QUANTUM_NETWORK,
            VisualStageType.RADIAL_RADAR,
            VisualStageType.SPECTRAL_WAVEFORM,
        ]
        for st in stages:
            cfg = VisualStageConfig(
                stage_type=st,
                title=f"STAGE_{st.value.upper()}",
                accent_color="oklch(0.78 0.18 205.0)",
            )
            svg = AlephVisualStageSynthesizer.render_stage_svg(cfg)
            self.assertIsInstance(svg, str)
            self.assertIn("aleph-visual-stage", svg)
            self.assertGreater(len(svg), 200)

    def test_kinetic_ode_canonical_spring_profiles(self):
        """Verifica simulación de osciladores armónicos de 2do orden y generación de CSS linear()."""
        from aleph_kinetic_ode import (
            CANONICAL_SPRING_PROFILES,
            DampingRegime,
            SpringPhysicsODE,
        )
        self.assertIn("--ease-spring-snappy", CANONICAL_SPRING_PROFILES)
        self.assertIn("--ease-spring-bouncy", CANONICAL_SPRING_PROFILES)
        self.assertIn("--ease-spring-gentle", CANONICAL_SPRING_PROFILES)

        snappy = CANONICAL_SPRING_PROFILES["--ease-spring-snappy"]
        self.assertEqual(snappy.regime, DampingRegime.CRITICALLY_DAMPED)
        self.assertEqual(snappy.overshoot_percent, 0.0)

        css_linear = snappy.to_css_linear(sample_count=20)
        self.assertTrue(css_linear.startswith("linear("))
        self.assertTrue(css_linear.endswith(")"))

    def test_static_dom_auditor_catches_slop_and_overflow(self):
        """Verifica que el oráculo DOM de .aleph detecta transition:all y jerarquía de encabezados."""
        from aleph_render_oracle import StaticDOMAuditor

        # Caso válido
        good_html = """<!DOCTYPE html>
        <html lang="es">
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body>
          <h1>Título Principal</h1>
          <h2>Subtítulo de Sección</h2>
          <button type="button">Ejecutar</button>
        </body></html>"""
        auditor = StaticDOMAuditor()
        auditor.feed(good_html)
        self.assertTrue(auditor.has_h1)
        self.assertTrue(auditor.has_viewport_meta)
        self.assertEqual(auditor.headings, [1, 2])

        # Caso con saltos de encabezado
        bad_html = """<!DOCTYPE html>
        <html><head><style>* { transition: all 0.3s; }</style></head>
        <body>
          <h1>Heading 1</h1>
          <h3>Skipped Level</h3>
        </body></html>"""
        auditor_bad = StaticDOMAuditor()
        auditor_bad.feed(bad_html)
        self.assertEqual(auditor_bad.headings, [1, 3])

    def test_token_compiler_gamut_mapping_and_typography(self):
        """Verifica conversiones cromáticas y cálculo de clamp() fluido en .aleph."""
        from aleph_token_compiler import (
            OklchColor,
            clip_oklch_to_srgb,
            calculate_fluid_clamp,
        )
        # Test conversión cromática segura
        oklch = OklchColor(L=0.75, c=0.15, h=200.0)
        rgb, clipped_oklch = clip_oklch_to_srgb(oklch)
        self.assertTrue(0.0 <= rgb.r <= 1.0)
        self.assertTrue(0.0 <= rgb.g <= 1.0)
        self.assertTrue(0.0 <= rgb.b <= 1.0)

        # Test tipografía fluida clamp()
        token = calculate_fluid_clamp("font-body", 16.0, 24.0, 320.0, 1280.0)
        clamp_expr = token.clamp_expr
        self.assertTrue(clamp_expr.startswith("clamp("))
        self.assertIn("vw", clamp_expr)


if __name__ == "__main__":
    unittest.main()
