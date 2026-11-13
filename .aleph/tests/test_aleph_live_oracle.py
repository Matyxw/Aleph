"""
.aleph/tests/test_aleph_live_oracle.py
Tests para el Oráculo de Renderizado Físico (Playwright + Chromium/Blink real) y Auditor DOM Estático.
Garantiza cero mocks en la verificación de layout físico y pruebas ultrarrápidas en modo estático.
"""

import pytest

from lib.aleph_render_oracle import AlephRenderOracle, LivePlaywrightOracle, StaticDOMAuditor
from lib.aleph_design_facade import AlephDesignFacade


def test_static_dom_auditor_fast_pass():
    """Modo estático evalúa estructura y a11y en menos de 5ms sin levantar navegador."""
    oracle = AlephRenderOracle()
    valid_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            h1 { font-family: 'Space Grotesk', sans-serif; }
            button { transition: opacity 150ms ease; }
        </style>
    </head>
    <body>
        <h1>Título Soberano de Producción</h1>
        <h2>Subtítulo de Sección</h2>
        <button type="button">Ejecutar Invariante</button>
    </body>
    </html>"""
    report = oracle.audit_html(valid_html, live=False)
    assert report.is_passing is True
    assert report.horizontal_overflow_px == 0.0
    assert report.accessibility_score >= 80.0
    assert len(report.heading_hierarchy_violations) == 0


def test_static_dom_auditor_catches_slop():
    """Detecta frases de marketing de IA y malas prácticas como transition: all."""
    oracle = AlephRenderOracle()
    slop_html = """<!DOCTYPE html>
    <html>
    <head>
        <style>
            * { transition: all 0.3s ease; }
        </style>
    </head>
    <body>
        <h1>Unleash your potential with revolutionary AI</h1>
        <h3>Skipped heading level</h3>
    </body>
    </html>"""
    report = oracle.audit_html(slop_html, live=False)
    assert report.is_passing is False
    assert report.slop_score > 0.20
    assert any("transition: all" in f for f in report.slop_findings)


def test_live_playwright_oracle_real_chromium():
    """
    Verifica que LivePlaywrightOracle ejecuta un proceso Chromium/Blink real
    y mide 0 overflow horizontal en viewports Mobile (375px), Tablet (768px) y Desktop (1440px).
    """
    facade = AlephDesignFacade()
    res = facade.generate_design_from_brief("Aerospace telemetry command dashboard")

    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(res.html_bundle, timeout_sec=15.0)

    # Verificación en motor Blink real
    assert report.is_passing is True
    assert report.horizontal_overflow_px == 0.0
    assert len(report.heading_hierarchy_violations) == 0

    # Métricas emitidas por el proceso Node / Chromium
    metrics = report.metrics
    assert "Chromium" in metrics.get("engine", "")
    viewports = metrics.get("viewports", {})
    # The oracle now uses granular keys (mobile_375, tablet_768, desktop_1440)
    mobile_keys = [k for k in viewports if k.startswith("mobile")]
    tablet_keys = [k for k in viewports if k.startswith("tablet")]
    desktop_keys = [k for k in viewports if k.startswith("desktop")]
    assert len(mobile_keys) > 0, f"No mobile viewport found in {list(viewports.keys())}"
    assert len(tablet_keys) > 0
    assert len(desktop_keys) > 0

    # Use first mobile viewport (mobile_375 or mobile_320)
    mobile_key = next(k for k in mobile_keys if "375" in k) if any("375" in k for k in mobile_keys) else mobile_keys[0]
    mobile_vp = viewports[mobile_key]
    assert mobile_vp["overflowX"] == 0
    assert mobile_vp["scrollWidth"] <= 375
    assert mobile_vp["clientWidth"] <= 375


def test_live_playwright_oracle_detects_physical_overflow():
    """
    Inyecta una caja con ancho forzado de 3000px y verifica que el motor Chromium
    físico detecta scrollWidth > clientWidth y rechaza el diseño.
    """
    overflow_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0;">
        <h1>Contenedor con Fuga Horizontal</h1>
        <div id="massive-box" style="width: 3200px; height: 100px; background: red;"></div>
    </body>
    </html>"""

    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(overflow_html, timeout_sec=10.0)

    # Must fail physically — find any mobile viewport with overflow
    assert report.is_passing is False
    assert report.horizontal_overflow_px > 0.0
    viewports = report.metrics["viewports"]
    mobile_keys = [k for k in viewports if k.startswith("mobile")]
    assert len(mobile_keys) > 0
    mobile_overflow = viewports[mobile_keys[0]]["overflowX"]
    assert mobile_overflow > 2000.0


def test_aleph_render_oracle_live_mode_flag():
    """AlephRenderOracle delega en LivePlaywrightOracle cuando live=True."""
    oracle = AlephRenderOracle()
    minimal_page = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; font-family: sans-serif; overflow-x: hidden; }
            h1 { font-size: 1.5rem; }
        </style>
    </head>
    <body>
        <h1>Página de Control Minimalista</h1>
        <p>Verificación de oráculo vivo.</p>
    </body>
    </html>"""

    report = oracle.audit_html(minimal_page, live=True)
    assert report.is_passing is True
    assert report.horizontal_overflow_px == 0.0
    assert "engine" in report.metrics


def test_live_oracle_detects_accent_budget_excess():
    """Ley 1: Presupuesto de Acento (60-30-10) rechaza páginas donde el acento supera el 10% del viewport."""
    accent_slop_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; background: #000; }
            .giant-neon-box {
                width: 100vw;
                height: 35vh; /* 35% del viewport > 10% permitido */
                background-color: #00f0ff; /* Saturación 100%, brillo 50% */
            }
        </style>
    </head>
    <body>
        <h1>Prueba de Presupuesto de Acento</h1>
        <div class="giant-neon-box">Exceso de Acento</div>
    </body>
    </html>"""
    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(accent_slop_html, timeout_sec=10.0)
    assert report.is_passing is False
    assert any("Presupuesto de Acento" in v for v in report.visual_design_violations)
    assert report.photometric_audit.get("accent_budget_passed") is False


def test_live_oracle_detects_colinearity_violation():
    """Ley 2: Co-linearidad de Acciones detecta botones no alineados horizontalmente en Desktop (delta Y > 4px)."""
    unaligned_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            .aleph-hero-actions { display: flex; align-items: flex-start; gap: 16px; }
            .btn-a { height: 44px; margin-top: 0; }
            .btn-b { height: 44px; margin-top: 14px; } /* Desfase de 14px > 4px */
        </style>
    </head>
    <body>
        <h1>Prueba de Co-linearidad</h1>
        <div class="aleph-hero-actions">
            <button class="btn-a">Acción Principal</button>
            <button class="btn-b">Acción Secundaria</button>
        </div>
    </body>
    </html>"""
    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(unaligned_html, timeout_sec=10.0)
    assert report.is_passing is False
    assert any("Co-linearidad" in v for v in report.visual_design_violations)
    assert report.photometric_audit.get("action_colinearity_passed") is False


def test_live_oracle_detects_unprotected_canvas_surface():
    """Ley 3: Superficie Protectora rechaza texto sobre canvas WebGL sin backdrop-filter ni opacidad protectora."""
    canvas_slop_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; background: #000; }
            canvas { position: absolute; top: 0; left: 0; width: 600px; height: 400px; }
            .floating-card {
                position: absolute; top: 50px; left: 50px; width: 250px;
                background: transparent; /* Carece de fondo protector y blur */
                color: #ffffff;
            }
        </style>
    </head>
    <body>
        <canvas width="600" height="400"></canvas>
        <article class="floating-card" id="card-unprotected">
            <h1>Texto Desprotegido</h1>
            <p>Ilegible sobre partículas dinámicas.</p>
        </article>
    </body>
    </html>"""
    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(canvas_slop_html, timeout_sec=10.0)
    assert report.is_passing is False
    assert any("Superficie Protectora" in v for v in report.visual_design_violations)
    assert report.photometric_audit.get("protective_surface_passed") is False


def test_live_oracle_detects_empty_bento_card():
    """Ley 4: Densidad Visual rechaza tarjetas Bento puramente textuales sin svg, canvas o code."""
    empty_bento_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Prueba de Bento Density</h1>
        <div class="aleph-bento-grid">
            <article class="aleph-bento-card" id="bento-text-slop">
                <h3>Solo Texto</h3>
                <p>Carece por completo de ícono vectorial, canvas o snippet de código.</p>
            </article>
        </div>
    </body>
    </html>"""
    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(empty_bento_html, timeout_sec=10.0)
    assert report.is_passing is False
    assert any("Densidad Visual" in v for v in report.visual_design_violations)
    assert report.photometric_audit.get("visual_density_passed") is False


def test_live_oracle_detects_menu_wrapping():
    """Ley 5: Detección de saltos de línea involuntarios en enlaces de navegación de menú."""
    wrapped_menu_html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            nav { width: 200px; }
            nav a {
                display: block;
                width: 50px; /* Forzado a ancho ínfimo para forzar división de línea */
                font-size: 14px;
                line-height: 18px;
            }
        </style>
    </head>
    <body>
        <nav class="aleph-navbar">
            <a href="#">Navegación Extensa Partida</a>
        </nav>
        <h1>Página Principal</h1>
    </body>
    </html>"""
    live_oracle = LivePlaywrightOracle()
    report = live_oracle.audit_live_rendered_html(wrapped_menu_html, timeout_sec=10.0)
    assert report.is_passing is False
    assert any("enlace de menú" in v for v in report.visual_design_violations)
    assert report.photometric_audit.get("menu_wrapping_passed") is False
