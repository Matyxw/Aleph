"""
.aleph/tests/test_aleph_v7_interaction.py
=============================================================================
ALEPH SOVEREIGN WORLD DESIGNER V7.0 — CAPÍTULO 3
SUITE FORMAL DE CERTIFICACIÓN DE INTERACCIÓN, MATRIZ HÁPTICA Y CINEMÁTICA ODE
=============================================================================
Pruebas exhaustivas y deterministas para:
1. Simulación matemática de osciladores armónicos de 2do orden (m*x'' + c*x' + k*x = 0).
   - Verificación de regímenes físicos: críticamente amortiguado, subamortiguado y sobreamortiguado.
   - Perfiles canónicos: --ease-spring-snappy (zeta=1.0), --ease-spring-bouncy (zeta=0.60), --ease-spring-gentle (zeta=0.85).
   - Simulación analítica vs numérica (Runge-Kutta 4to Orden - RK4).
   - Compilación a funciones estándar CSS linear(...) (CSS Easing Level 2).
2. Matriz Háptica Canónica de 7 Estados de Interacción:
   - IDLE, HOVER, FOCUS_VISIBLE, ACTIVE_PRESSED, DISABLED, LOADING_PENDING, FEEDBACK (SUCCESS/ERROR).
   - Invariante estricta de completitud de 7 estados (forbid incomplete states).
   - Compilación de CSS con propiedades seguras para el Composite Thread de la GPU.
3. Auditoría Semántica y Linter Anti-Slop:
   - Prohibición absoluta de 'transition: all' y utilidades 'transition-all'.
   - Anti-conflación ontológica estricta: <button> (acciones/mutaciones) vs <a> (navegación).
   - Accesibilidad universal WCAG 2.5.5 / 1.1.1 (type en botones, aria-labels en icon triggers).
   - Certificación integral de bundles compilados (HTML + CSS).
=============================================================================
"""

import math
import sys
from pathlib import Path
try:
    import pytest
    _raises = pytest.raises
except ImportError:
    import unittest as _unittest
    _tc = _unittest.TestCase()

    def _raises(exc_type, match=None):  # type: ignore[misc]
        return _tc.assertRaisesRegex(exc_type, match) if match else _tc.assertRaises(exc_type)

# Asegurar importación de la librería de Aleph
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from aleph_kinetic_ode import (
    CANONICAL_SPRING_PROFILES,
    DampingRegime,
    FeedbackType,
    InteractionSemanticsValidator,
    InteractionState,
    InteractionStateMatrix,
    SemanticAuditIssue,
    SpringPhysicsODE,
    StateVisualProps,
    generate_spring_css_declaration_block,
    generate_spring_css_tokens,
    parse_css_linear_points,
    validate_css_linear_syntax,
)


# ============================================================================
# 1. PRUEBAS DE SIMULACIÓN CINEMÁTICA ODE Y RESORTES ARMÓNICOS
# ============================================================================

class TestKineticODESimulation:
    """Certificación matemática de la simulación de osciladores armónicos de 2do orden."""

    def test_spring_canonical_profiles_exist(self):
        """Verifica la existencia e integridad de los 3 perfiles canónicos del Plan Maestro V7.0."""
        assert "--ease-spring-snappy" in CANONICAL_SPRING_PROFILES
        assert "--ease-spring-bouncy" in CANONICAL_SPRING_PROFILES
        assert "--ease-spring-gentle" in CANONICAL_SPRING_PROFILES

    def test_snappy_spring_physics(self):
        """
        Perfil SNAPPY:
        - zeta = 1.0 (críticamente amortiguado exacto).
        - Cero sobreoscilación (overshoot == 0.0%).
        - Retorno rápido sin oscilaciones parásitas.
        """
        snappy = CANONICAL_SPRING_PROFILES["--ease-spring-snappy"]
        assert snappy.regime == DampingRegime.CRITICALLY_DAMPED
        assert math.isclose(snappy.damping_ratio, 1.0, rel_tol=1e-5)
        assert snappy.overshoot_percent == 0.0
        assert snappy.peak_time is None

        # Posición inicial y final
        pos_0, vel_0 = snappy.evaluate(0.0)
        assert pos_0 == 0.0
        assert vel_0 == 0.0

        # Monotonía: la posición nunca supera el target 1.0
        for step in range(1, 30):
            t = step * 0.01
            pos = snappy.position(t)
            assert 0.0 <= pos <= 1.0001, f"SNAPPY no debe sobrepasar target en t={t}: {pos}"

        # Tiempo de asentamiento rápido (< 350ms)
        ts = snappy.settling_time(0.01)
        assert 0.10 <= ts <= 0.40, f"Tiempo de asentamiento inesperado para snappy: {ts}s"
        assert math.isclose(snappy.position(ts), 1.0, abs_tol=0.015)

    def test_bouncy_spring_physics(self):
        """
        Perfil BOUNCY:
        - zeta = 0.60 (subamortiguado).
        - Overshoot controlado ~9.48% (entre 8% y 11%).
        - Frecuencia amortiguada omega_d y tiempo de pico válidos.
        """
        bouncy = CANONICAL_SPRING_PROFILES["--ease-spring-bouncy"]
        assert bouncy.regime == DampingRegime.UNDERDAMPED
        assert math.isclose(bouncy.damping_ratio, 0.60, rel_tol=1e-4)

        # Overshoot analítico teórico: exp(-pi * 0.6 / sqrt(1 - 0.36)) * 100% ~= 9.478%
        expected_overshoot = math.exp(-math.pi * 0.6 / math.sqrt(1.0 - 0.36)) * 100.0
        assert math.isclose(bouncy.overshoot_percent, expected_overshoot, rel_tol=1e-4)
        assert 8.5 <= bouncy.overshoot_percent <= 10.5

        # Tiempo de pico
        assert bouncy.peak_time is not None
        tp = bouncy.peak_time
        assert tp > 0.0
        pos_at_peak = bouncy.position(tp)
        # En el primer pico debe superar el target por el porcentaje de overshoot
        assert pos_at_peak > 1.05
        calculated_overshoot = (pos_at_peak - 1.0) * 100.0
        assert math.isclose(calculated_overshoot, bouncy.overshoot_percent, abs_tol=0.2)

    def test_gentle_spring_physics(self):
        """
        Perfil GENTLE:
        - zeta = 0.85 (cuasi-crítico).
        - Overshoot amortiguado imperceptible (< 1.0%).
        - Movimiento suave y continuo para modales y navegación.
        """
        gentle = CANONICAL_SPRING_PROFILES["--ease-spring-gentle"]
        assert gentle.regime == DampingRegime.UNDERDAMPED
        assert math.isclose(gentle.damping_ratio, 0.85, rel_tol=1e-4)
        assert gentle.overshoot_percent < 1.0
        assert gentle.overshoot_percent > 0.1

        # Comportamiento suave hacia target
        ts = gentle.settling_time(0.01)
        assert 0.3 <= ts <= 1.0
        assert math.isclose(gentle.position(ts), 1.0, abs_tol=0.015)

    def test_rk4_numerical_simulation_matches_analytical(self):
        """
        Verificación de consistencia entre la integración numérica Runge-Kutta 4to Orden (RK4)
        y la solución analítica cerrada de la ecuación diferencial.
        Error relativo máximo debe ser menor a 0.5% en todo el intervalo.
        """
        bouncy = CANONICAL_SPRING_PROFILES["--ease-spring-bouncy"]
        rk4_steps = bouncy.simulate_rk4(duration=0.5, dt=0.001)

        assert len(rk4_steps) > 400
        for t, num_x, _ in rk4_steps[::10]:  # muestrear cada 10ms
            if t == 0.0:
                continue
            ana_x = bouncy.position(t)
            diff = abs(num_x - ana_x)
            assert diff < 0.005, f"Discrepancia RK4 vs analítica en t={t}: RK4={num_x}, Ana={ana_x}, diff={diff}"

    def test_from_zeta_factory(self):
        """Verifica la factoría por zeta y frecuencia natural angular omega_0."""
        spring = SpringPhysicsODE.from_zeta(zeta=0.707, natural_frequency_rad_s=15.0, mass=2.0)
        assert math.isclose(spring.omega_0, 15.0, rel_tol=1e-5)
        assert math.isclose(spring.damping_ratio, 0.707, rel_tol=1e-5)
        assert spring.mass == 2.0

        with _raises(ValueError, match="zeta no puede ser negativo"):
            SpringPhysicsODE.from_zeta(zeta=-0.1)

    def test_overdamped_regime(self):
        """Verifica el cálculo de régimen sobreamortiguado (zeta > 1.0)."""
        overdamped = SpringPhysicsODE(mass=1.0, stiffness=100.0, damping=40.0)
        # critical damping = 2 * sqrt(100) = 20.0 => zeta = 40/20 = 2.0
        assert overdamped.regime == DampingRegime.OVERDAMPED
        assert overdamped.damping_ratio == 2.0
        assert overdamped.overshoot_percent == 0.0

        pos_1s = overdamped.position(0.5)
        assert 0.0 < pos_1s < 1.0


# ============================================================================
# 2. PRUEBAS DE COMPILACIÓN A CSS linear(...)
# ============================================================================

class TestCSSLinearCompilation:
    """Verificación de la generación de CSS linear(...) conforme a CSS Easing Level 2."""

    def test_linear_css_syntax_for_canonical_profiles(self):
        """Verifica que los tres perfiles canónicos generen funciones linear(...) válidas."""
        for name, profile in CANONICAL_SPRING_PROFILES.items():
            css_linear = profile.to_css_linear(sample_count=16, precision=4)
            assert css_linear.startswith("linear(")
            assert css_linear.endswith(")")
            assert validate_css_linear_syntax(css_linear), f"Sintaxis inválida en {name}: {css_linear}"

            points = parse_css_linear_points(css_linear)
            assert len(points) == 17  # 16 segmentos => 17 puntos
            assert points[0] == 0.0   # Normalización inicial
            assert math.isclose(points[-1], 1.0, abs_tol=0.01)  # Asentamiento final

    def test_linear_bouncy_overshoot_in_points(self):
        """Verifica que el perfil BOUNCY refleje explícitamente valores > 1.0 en sus puntos linear(...)."""
        bouncy_css = CANONICAL_SPRING_PROFILES["--ease-spring-bouncy"].to_css_linear(sample_count=32)
        points = parse_css_linear_points(bouncy_css)

        max_val = max(points)
        assert max_val > 1.05, f"BOUNCY debe tener puntos de sobreoscilación > 1.05: {max_val}"
        assert max_val < 1.15, f"BOUNCY no debe exceder límite físico razonable: {max_val}"

    def test_linear_snappy_no_overshoot_in_points(self):
        """Verifica que el perfil SNAPPY no contenga ningún punto > 1.0 (críticamente amortiguado)."""
        snappy_css = CANONICAL_SPRING_PROFILES["--ease-spring-snappy"].to_css_linear(sample_count=20)
        points = parse_css_linear_points(snappy_css)

        for p in points:
            assert p <= 1.0001, f"SNAPPY contiene sobreoscilación en linear(...): {p}"

    def test_css_tokens_and_declaration_block(self):
        """Verifica la generación completa del bloque de variables CSS para inyección en :root."""
        tokens = generate_spring_css_tokens()
        assert len(tokens) == 3
        for k in ["--ease-spring-snappy", "--ease-spring-bouncy", "--ease-spring-gentle"]:
            assert k in tokens
            assert validate_css_linear_syntax(tokens[k])

        block = generate_spring_css_declaration_block(indent=2)
        assert "--ease-spring-snappy: linear(" in block
        assert "--ease-spring-bouncy: linear(" in block
        assert "--ease-spring-gentle: linear(" in block

    def test_validate_css_linear_syntax_edge_cases(self):
        """Verifica el validador de sintaxis frente a expresiones correctas y corruptas."""
        # Válidas
        assert validate_css_linear_syntax("linear(0, 0.5, 1)")
        assert validate_css_linear_syntax("linear(0 0%, 0.5 50%, 1 100%)")
        assert validate_css_linear_syntax("linear(0.0000, 1.0948, 0.9980, 1.0000)")

        # Inválidas
        assert not validate_css_linear_syntax("cubic-bezier(0.1, 0.7, 1.0, 0.1)")
        assert not validate_css_linear_syntax("linear()")
        assert not validate_css_linear_syntax("linear(0)")
        assert not validate_css_linear_syntax("linear(abc, 123)")
        assert not validate_css_linear_syntax("linear(0, NaN, 1)")


# ============================================================================
# 3. PRUEBAS DE LA MATRIZ HÁPTICA FORMAL DE 7 ESTADOS
# ============================================================================

class TestHapticStateMatrix:
    """Certificación de la Matriz Háptica de 7 Estados de Interacción."""

    def test_seven_states_enumeration(self):
        """Verifica la definición ontológica exacta de los 7 estados requeridos."""
        expected = {
            "idle",
            "hover",
            "focus_visible",
            "active_pressed",
            "disabled",
            "loading_pending",
            "feedback",
        }
        actual = {s.value for s in InteractionState}
        assert actual == expected
        assert len(InteractionState) == 7

    def test_interaction_state_matrix_completeness_validation(self):
        """Verifica que la matriz rechace configuraciones incompletas con ValueError."""
        complete_matrix = InteractionStateMatrix.create_canonical_button_matrix()
        assert len(complete_matrix.states) == 7

        # Intentar instanciar con solo 6 estados debe lanzar ValueError
        incomplete_states = {
            s: StateVisualProps(state=s)
            for s in [
                InteractionState.IDLE,
                InteractionState.HOVER,
                InteractionState.FOCUS_VISIBLE,
                InteractionState.ACTIVE_PRESSED,
                InteractionState.DISABLED,
                InteractionState.LOADING_PENDING,
            ]
        }
        with _raises(ValueError, match="Matriz de Interacción incompleta"):
            InteractionStateMatrix(states=incomplete_states)

    def test_canonical_button_matrix_properties(self):
        """Verifica las propiedades visuales y cinéticas del botón canónico."""
        matrix = InteractionStateMatrix.create_canonical_button_matrix(primary=True)

        # 1. IDLE
        idle = matrix.get_state(InteractionState.IDLE)
        assert idle.transform == "scale(1.0) translateY(0)"
        assert idle.cursor == "pointer"
        assert idle.motion_duration_ms == 180.0

        # 2. HOVER
        hover = matrix.get_state(InteractionState.HOVER)
        assert hover.transform == "translateY(-1.5px)"
        assert hover.filter == "brightness(1.10)"

        # 3. FOCUS_VISIBLE
        focus = matrix.get_state(InteractionState.FOCUS_VISIBLE)
        assert "outline" in focus.model_fields_set or focus.outline is not None
        assert focus.outline_offset == "3px"

        # 4. ACTIVE_PRESSED (compresión mecánica de rebote)
        active = matrix.get_state(InteractionState.ACTIVE_PRESSED)
        assert active.transform == "scale(0.97) translateY(0)"
        assert active.filter == "brightness(0.92)"

        # 5. DISABLED
        disabled = matrix.get_state(InteractionState.DISABLED)
        assert disabled.opacity == 0.45
        assert disabled.cursor == "not-allowed"
        assert disabled.pointer_events == "none"
        assert disabled.aria_attributes.get("aria-disabled") == "true"

        # 6. LOADING_PENDING
        loading = matrix.get_state(InteractionState.LOADING_PENDING)
        assert loading.opacity == 0.80
        assert loading.cursor == "wait"
        assert loading.pointer_events == "none"
        assert loading.aria_attributes.get("aria-busy") == "true"

        # 7. FEEDBACK: SUCCESS & ERROR
        succ = matrix.get_state(InteractionState.FEEDBACK, feedback_type=FeedbackType.SUCCESS)
        assert "success" in (succ.background or "") or "#10b981" in (succ.background or "")
        assert succ.aria_attributes.get("data-state") == "success"

        err = matrix.get_state(InteractionState.FEEDBACK, feedback_type=FeedbackType.ERROR)
        assert "error" in (err.background or "") or "#ef4444" in (err.background or "")
        assert err.aria_attributes.get("data-state") == "error"

    def test_canonical_link_matrix_properties(self):
        """Verifica las propiedades del enlace arquitectónico <a> (sin elevación de botón)."""
        link_matrix = InteractionStateMatrix.create_canonical_link_matrix()
        assert len(link_matrix.states) == 7

        idle = link_matrix.get_state(InteractionState.IDLE)
        assert idle.background == "transparent"

        active = link_matrix.get_state(InteractionState.ACTIVE_PRESSED)
        assert active.transform == "scale(0.99)"

    def test_compile_css_rules_guarantees(self):
        """
        Verifica la compilación de reglas CSS:
        - Incluye todos los selectores necesarios (:hover, :focus-visible, :active, :disabled, aria-busy, etc.).
        - Prohíbe explícitamente 'transition: all'.
        """
        matrix = InteractionStateMatrix.create_canonical_button_matrix()
        css = matrix.compile_css_rules(".aleph-btn")

        # Cero transition: all
        assert "transition: all" not in css
        assert "transition:all" not in css

        # Transición explícita de propiedades GPU
        assert "transition: transform" in css
        assert "background-color" in css

        # Presencia de selectores para los estados
        assert ".aleph-btn:hover:not(:disabled)" in css
        assert ".aleph-btn:focus-visible" in css
        assert ".aleph-btn:active:not(:disabled)" in css
        assert ".aleph-btn:disabled" in css
        assert "[aria-busy='true']" in css
        assert "[data-state='success']" in css
        assert "[data-state='error']" in css


# ============================================================================
# 4. PRUEBAS DEL AUDITOR Y LINTER SEMÁNTICO ANTI-SLOP
# ============================================================================

class TestSemanticAntiSlopAuditor:
    """Certificación de las reglas de auditoría semántica y rendimiento GPU."""

    # -------------------------------------------------------------------------
    # A. Prohibición estricta de transition: all
    # -------------------------------------------------------------------------
    def test_audit_css_detects_transition_all(self):
        """Detecta y rechaza 'transition: all' en cualquier variante de formato."""
        bad_css_1 = """.bad-btn { transition: all 0.2s ease-in-out; }"""
        bad_css_2 = """.bad-btn { transition:all 150ms cubic-bezier(0.16, 1, 0.3, 1); }"""
        bad_css_3 = """.bad-btn { transition: color 100ms, all 200ms ease; }"""

        issues_1 = InteractionSemanticsValidator.audit_css(bad_css_1)
        assert len(issues_1) >= 1
        assert any(i.rule_id == "ANTI_SLOP_BAN_TRANSITION_ALL" for i in issues_1)

        issues_2 = InteractionSemanticsValidator.audit_css(bad_css_2)
        assert any(i.rule_id == "ANTI_SLOP_BAN_TRANSITION_ALL" for i in issues_2)

        issues_3 = InteractionSemanticsValidator.audit_css(bad_css_3)
        assert any(i.rule_id == "ANTI_SLOP_BAN_TRANSITION_ALL" for i in issues_3)

    def test_audit_css_detects_tailwind_transition_all_utility(self):
        """Detecta el uso de la clase utilitaria 'transition-all'."""
        tailwind_css = """.btn { @apply transition-all duration-150; }"""
        issues = InteractionSemanticsValidator.audit_css(tailwind_css)
        assert any(i.rule_id == "ANTI_SLOP_BAN_TRANSITION_ALL_CLASS" for i in issues)

    def test_audit_css_passes_gpu_specific_transitions(self):
        """Permite transiciones explícitas sobre propiedades GPU y compuestas."""
        good_css = """
        .good-btn {
            transition: transform 150ms var(--ease-spring-snappy),
                        opacity 180ms ease,
                        background-color 150ms ease,
                        box-shadow 150ms ease;
        }
        """
        issues = InteractionSemanticsValidator.audit_css(good_css)
        assert len(issues) == 0

    def test_audit_css_ignores_comments(self):
        """Ignora menciones de 'transition: all' dentro de comentarios de documentación."""
        comment_css = """
        /* Prohibido usar transition: all en componentes de Aleph */
        // Tampoco usar transition: all en inline
        .clean-btn {
            transition: transform 100ms ease;
        }
        """
        issues = InteractionSemanticsValidator.audit_css(comment_css)
        assert len(issues) == 0

    # -------------------------------------------------------------------------
    # B. Anti-conflación ontológica: <button> vs <a>
    # -------------------------------------------------------------------------
    def test_audit_html_flags_button_with_href(self):
        """Detecta <button> contaminado con atributo href."""
        bad_html = """<button type="button" href="/dashboard">Navegar</button>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "ANTI_CONFLATION_BUTTON_WITH_HREF" for i in issues)

    def test_audit_html_flags_button_missing_type(self):
        """Detecta <button> sin atributo 'type' explícito."""
        bad_html = """<button class="aleph-btn">Acción</button>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "ACCESSIBILITY_BUTTON_MISSING_TYPE" for i in issues)

    def test_audit_html_flags_button_invalid_type(self):
        """Detecta <button> con atributo 'type' no estándar."""
        bad_html = """<button type="custom-action">Acción</button>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "HTML5_INVALID_BUTTON_TYPE" for i in issues)

    def test_audit_html_flags_anchor_without_href(self):
        """Detecta <a> que carece de atributo href."""
        bad_html = """<a class="nav-item">Enlace Inerte</a>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "SEMANTIC_ANCHOR_WITHOUT_HREF" for i in issues)

    def test_audit_html_flags_anchor_used_as_pseudo_button(self):
        """Detecta <a> con href='#' y onclick, o href='javascript:...'."""
        bad_html_1 = """<a href="#" onclick="deleteItem(42)">Eliminar</a>"""
        bad_html_2 = """<a href="javascript:void(0)">Acción</a>"""

        issues_1 = InteractionSemanticsValidator.audit_html(bad_html_1)
        assert any(i.rule_id == "ANTI_CONFLATION_ANCHOR_AS_PSEUDO_BUTTON" for i in issues_1)

        issues_2 = InteractionSemanticsValidator.audit_html(bad_html_2)
        assert any(i.rule_id == "ANTI_CONFLATION_ANCHOR_AS_PSEUDO_BUTTON" for i in issues_2)

    def test_audit_html_flags_anchor_disguised_as_primary_action(self):
        """Detecta <a> estilizado con la clase de acción primaria de botón."""
        bad_html = """<a href="/pricing" class="aleph-action-primary">Ver Precios</a>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "ANTI_CONFLATION_LINK_DISGUISED_AS_PRIMARY_ACTION" for i in issues)

    def test_audit_html_flags_icon_trigger_missing_aria_label(self):
        """Detecta botones icónicos sin 'aria-label' o 'aria-labelledby' (WCAG 1.1.1)."""
        bad_html = """<button type="button" class="aleph-icon-trigger"><svg></svg></button>"""
        issues = InteractionSemanticsValidator.audit_html(bad_html)
        assert any(i.rule_id == "ACCESSIBILITY_ICON_TRIGGER_NO_LABEL" for i in issues)

        # Con aria-label debe aprobar sin ese issue
        good_html = """<button type="button" class="aleph-icon-trigger" aria-label="Cerrar panel"><svg></svg></button>"""
        good_issues = InteractionSemanticsValidator.audit_html(good_html)
        assert not any(i.rule_id == "ACCESSIBILITY_ICON_TRIGGER_NO_LABEL" for i in good_issues)

    def test_audit_html_passes_fully_compliant_code(self):
        """Verifica que un bloque HTML con semántica rigurosa apruebe con 0 violaciones."""
        good_html = """
        <header>
            <a href="/dashboard" class="aleph-nav-link">Inicio</a>
            <a href="/settings" class="aleph-nav-link">Ajustes</a>
            <button type="button" class="aleph-action-secondary" aria-label="Abrir menú">Menú</button>
            <button type="submit" class="aleph-action-primary">Guardar Cambios</button>
        </header>
        """
        issues = InteractionSemanticsValidator.audit_html(good_html)
        assert len(issues) == 0

    # -------------------------------------------------------------------------
    # C. Auditoría de completitud de la matriz de estados
    # -------------------------------------------------------------------------
    def test_audit_state_matrix_completeness(self):
        """Valida que la auditoría de completitud apruebe matrices completas y rechace diccionarios truncados."""
        matrix = InteractionStateMatrix.create_canonical_button_matrix()
        issues = InteractionSemanticsValidator.audit_state_matrix_completeness(matrix)
        assert len(issues) == 0

        # Diccionario incompleto
        truncated_dict = {
            "idle": {},
            "hover": {},
            "active_pressed": {},
        }
        issues_trunc = InteractionSemanticsValidator.audit_state_matrix_completeness(truncated_dict)
        assert len(issues_trunc) >= 1
        assert issues_trunc[0].rule_id == "STATE_MATRIX_INCOMPLETE"

    # -------------------------------------------------------------------------
    # D. Auditoría integral de Bundle Compilado (HTML + CSS)
    # -------------------------------------------------------------------------
    def test_audit_compiled_bundle_certification_success(self):
        """Verifica la certificación exitosa de un bundle completamente conforme."""
        spring_css = generate_spring_css_declaration_block()
        matrix = InteractionStateMatrix.create_canonical_button_matrix()
        component_css = matrix.compile_css_rules(".aleph-btn")

        full_css = f":root {{\n{spring_css}\n}}\n\n{component_css}"

        full_html = """
        <div class="interactive-stage">
            <button type="button" class="aleph-btn" aria-label="Ejecutar cálculo">
                Ejecutar ODE
            </button>
            <a href="/docs" class="aleph-nav-link">
                Documentación Técnica
            </a>
        </div>
        """

        result = InteractionSemanticsValidator.audit_compiled_bundle(full_html, full_css)
        assert result["certified"] is True
        assert result["total_violations"] == 0
        assert result["spring_tokens_present"] is True
        assert result["all_7_states_present"] is True
        assert len(result["issues"]) == 0

    def test_audit_compiled_bundle_certification_failure_on_missing_springs(self):
        """Verifica el rechazo del bundle si faltan variables de resortes cinéticos ODE."""
        matrix = InteractionStateMatrix.create_canonical_button_matrix()
        component_css = matrix.compile_css_rules(".aleph-btn")
        # CSS sin el bloque de variables de resortes
        full_html = """<button type="button" class="aleph-btn">Acción</button>"""

        result = InteractionSemanticsValidator.audit_compiled_bundle(full_html, component_css)
        assert result["certified"] is False
        assert result["spring_tokens_present"] is False
        assert any(i["rule_id"] == "MISSING_KINETIC_ODE_CSS_VARS" for i in result["issues"])

    def test_audit_compiled_bundle_certification_failure_on_transition_all(self):
        """Verifica el rechazo del bundle si se introduce 'transition: all'."""
        spring_css = generate_spring_css_declaration_block()
        matrix = InteractionStateMatrix.create_canonical_button_matrix()
        component_css = matrix.compile_css_rules(".aleph-btn")
        poisoned_css = f":root {{\n{spring_css}\n}}\n\n{component_css}\n.bad {{ transition: all 0.2s; }}"

        full_html = """<button type="button" class="aleph-btn">Acción</button>"""

        result = InteractionSemanticsValidator.audit_compiled_bundle(full_html, poisoned_css)
        assert result["certified"] is False
        assert any(i["rule_id"] == "ANTI_SLOP_BAN_TRANSITION_ALL" for i in result["issues"])
