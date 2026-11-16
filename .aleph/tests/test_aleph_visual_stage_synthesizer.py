"""
.aleph/tests/test_aleph_visual_stage_synthesizer.py
Tests exhaustivos para el Motor de Síntesis de Escenografía Visual Interna (Aleph Visual Stage Synthesizer).
"""
import unittest
import os, sys
dot_lib = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
if dot_lib not in sys.path:
    sys.path.insert(0, dot_lib)


from aleph_visual_stage_synthesizer import (
    AlephVisualStageSynthesizer,
    VisualStageConfig,
    VisualStageType,
)



class TestAlephVisualStageSynthesizer(unittest.TestCase):
    def test_infer_stage_type_semantic_keywords(self):
        synth = AlephVisualStageSynthesizer
    
        # Red / Grafos / Cuántico
        assert synth.infer_stage_type(card_title="Red Cuántica Topológica", card_desc="Entrelazamiento cuántico") == VisualStageType.QUANTUM_NETWORK
        assert synth.infer_stage_type(card_title="Graph Topology Cluster") == VisualStageType.TOPOLOGY_GRAPH
    
        # Terminal / Código / SMT
        assert synth.infer_stage_type(card_title="Motor Z3 SMT", card_desc="Formal verification solver") == VisualStageType.CODE_TERMINAL
        assert synth.infer_stage_type(card_title="Interactive CLI Shell") == VisualStageType.CODE_TERMINAL
    
        # Criogénico / Radar
        assert synth.infer_stage_type(card_title="Cámara Criogénica Dilución", card_desc="Sub-Kelvin monitoring") == VisualStageType.CRYO_GAUGE
        assert synth.infer_stage_type(card_title="Radar Orbital Telemetry") == VisualStageType.RADIAL_RADAR
    
        # Bézier / Telemetría / Throughput
        assert synth.infer_stage_type(card_title="Rendimiento y Latencia p99", card_desc="Análisis de tráfico sostenido") == VisualStageType.BEZIER_CHART
        assert synth.infer_stage_type(card_title="Financial Delta Chart") == VisualStageType.BEZIER_CHART
    
        # Geometría Suiza / Áurea / Editorial
        assert synth.infer_stage_type(card_title="Proporción Áurea Editorial", card_desc="Retícula modular suiza") == VisualStageType.SWISS_GEOMETRY
        assert synth.infer_stage_type(card_title="Swiss International Grid") == VisualStageType.SWISS_GEOMETRY
    
    
    def test_infer_stage_type_cyclic_fallback_no_repetition(self):
        synth = AlephVisualStageSynthesizer
        stages = [synth.infer_stage_type(card_title="Tarjeta Genérica", card_index=i) for i in range(5)]
        # Verificar que no se repitan stages contiguos
        for i in range(len(stages) - 1):
            assert stages[i] != stages[i + 1]
    
    
    def test_generate_quantum_network_svg_attributes(self):
        cfg = VisualStageConfig(
            stage_type=VisualStageType.QUANTUM_NETWORK,
            title="QUANTUM_CLUSTER_01",
            accent_color="#00f0ff",
            secondary_color="#7928ca",
        )
        html_out = AlephVisualStageSynthesizer.generate_quantum_network(cfg)
    
        assert "aleph-visual-stage" in html_out
        assert "aleph-quantum-network-stage" in html_out
        assert "viewBox=\"0 0 600 260\"" in html_out
        assert "stroke-dasharray=\"16 140\"" in html_out
        assert "aleph-pulse-line" in html_out
        assert "QUANTUM_CLUSTER_01" in html_out
        assert "0x7F-CORE" in html_out
        assert "feGaussianBlur" in html_out
    
    
    def test_generate_code_terminal_syntax_highlighting(self):
        cfg = VisualStageConfig(
            stage_type=VisualStageType.CODE_TERMINAL,
            title="z3_proof.py",
            badge_text="● VERIFIED_UNSAT",
        )
        html_out = AlephVisualStageSynthesizer.generate_code_terminal(cfg)
    
        assert "aleph-code-terminal-stage" in html_out
        assert "aleph-terminal-lights" in html_out
        assert "tok-kw" in html_out
        assert "tok-cls" in html_out
        assert "tok-func" in html_out
        assert "aleph-terminal-cursor" in html_out
        assert "z3_proof.py" in html_out
        assert "● VERIFIED_UNSAT" in html_out
    
    
    def test_generate_cryo_gauge_trigonometric_ticks(self):
        cfg = VisualStageConfig(
            stage_type=VisualStageType.CRYO_GAUGE,
            title="CRYO_DILUTION_CHAMBER",
            metric_value="0.012",
            metric_unit="mK",
        )
        html_out = AlephVisualStageSynthesizer.generate_cryo_gauge(cfg)
    
        assert "aleph-cryo-gauge-stage" in html_out
        assert "aleph-radar-sweep-beam" in html_out
        assert "0.012" in html_out
        assert "mK" in html_out
        assert "line x1=" in html_out
        assert "stroke-dasharray=" in html_out
        assert "rotate(135" in html_out
    
    
    def test_generate_bezier_chart_smooth_splines(self):
        cfg = VisualStageConfig(
            stage_type=VisualStageType.BEZIER_CHART,
            title="LIVE_TRAFFIC_SPECTROGRAM",
            data_series=[10.0, 25.0, 18.0, 45.0, 38.0, 70.0, 62.0, 95.0],
        )
        html_out = AlephVisualStageSynthesizer.generate_bezier_chart(cfg)
    
        assert "aleph-bezier-chart-stage" in html_out
        assert "path d=\"M" in html_out
        assert "C " in html_out  # Bézier cúbica continua
        assert "LIVE_TRAFFIC_SPECTROGRAM" in html_out
        assert "aleph-ripple-circle" in html_out
        assert "req/s" in html_out
    
    
    def test_generate_swiss_geometry_canon_elements(self):
        cfg = VisualStageConfig(
            stage_type=VisualStageType.SWISS_GEOMETRY,
            title="TYPOGRAPHIC_CANON",
        )
        html_out = AlephVisualStageSynthesizer.generate_swiss_geometry(cfg)
    
        assert "aleph-swiss-geometry-stage" in html_out
        assert "1.6180339887" in html_out
        assert "pattern id=" in html_out
        assert "ZÜRICH" in html_out
        assert "TYPOGRAPHIC_CANON" in html_out
    
    
    def test_render_stage_html_unified_dispatcher(self):
        synth = AlephVisualStageSynthesizer
        palette = {"primary": "#ff007f", "secondary": "#00f0ff"}
    
        html_qnet = synth.render_stage_html("quantum_network", palette=palette)
        assert "#ff007f" in html_qnet
        assert "aleph-quantum-network-stage" in html_qnet
    
        html_code = synth.render_stage_html("code_terminal", palette=palette)
        assert "aleph-code-terminal-stage" in html_code
    
        html_cryo = synth.render_stage_html("cryo_gauge", palette=palette)
        assert "aleph-cryo-gauge-stage" in html_cryo
    
        html_bezier = synth.render_stage_html("bezier_chart", palette=palette)
        assert "aleph-bezier-chart-stage" in html_bezier
    
        html_swiss = synth.render_stage_html("swiss_geometry", palette=palette)
        assert "aleph-swiss-geometry-stage" in html_swiss
    
    
    def test_get_stage_css_anti_slop_compliance(self):
        css = AlephVisualStageSynthesizer.get_stage_css()
    
        # Invariante Anti-Slop: Prohibido transition: all
        assert "transition: all" not in css
        assert "transition:all" not in css
        # Debe soportar reducción de movimiento
        assert "@media (prefers-reduced-motion: reduce)" in css
        # Debe definir keyframes para pulsos y radares
        assert "@keyframes alephPulseFlow" in css
        assert "@keyframes alephRadarRotate" in css
    
    
    def test_generate_all_react_components(self):
        react_files = AlephVisualStageSynthesizer.generate_all_react_components()
    
        assert "components/visuals/QuantumNetworkStage.tsx" in react_files
        assert "components/visuals/CodeTerminalStage.tsx" in react_files
        assert "components/visuals/BezierTelemetryStage.tsx" in react_files
        assert "components/visuals/CryoGaugeStage.tsx" in react_files
        assert "components/visuals/SwissGeometryStage.tsx" in react_files
    
        for f_path, content in react_files.items():
            assert "import React from \"react\";" in content
            assert "export function" in content
            assert "export default" in content
    
    
    def test_topology_graph_parametric_props(self):
        synth = AlephVisualStageSynthesizer
        props = {
            "hub_label": "HAUTE.MAISON",
            "node_labels": ["PARIS", "LONDON", "TOKYO", "NEW YORK", "GENEVA", "MADRID"],
            "stage_title": "GLOBAL_ATELIER_GRID",
            "badge": "PARIS FASHION WEEK",
        }
        cfg = VisualStageConfig(
            stage_type=VisualStageType.TOPOLOGY_GRAPH,
            props=props,
        )
        html_out = synth.generate_quantum_network(cfg)
    
        assert "HAUTE.MAISON" in html_out
        assert "PARIS" in html_out
        assert "LONDON" in html_out
        assert "TOKYO" in html_out
        assert "GLOBAL_ATELIER_GRID" in html_out
        assert "PARIS FASHION WEEK" in html_out
        assert "aleph-topology-graph-stage" in html_out
        assert "aleph-quantum-network-stage" in html_out
    
    
    def test_topology_graph_contextual_fallbacks_no_quantum_slop(self):
        synth = AlephVisualStageSynthesizer
    
        # 1. Alta Costura: No debe forzar física cuántica
        cfg_luxury = VisualStageConfig(
            stage_type=VisualStageType.TOPOLOGY_GRAPH,
            card_title="Alta Costura y Sastrería de Lujo",
            paradigm="haute_luxury",
        )
        html_luxury = synth.generate_quantum_network(cfg_luxury)
        assert "ATELIER.CENTRAL" in html_luxury
        assert "SOIE.LYON" in html_luxury
        assert "0x7F-CORE" not in html_luxury
        assert "Q-NODE.01" not in html_luxury
    
        # 2. Finanzas: Debe inferir liquidez y settlement
        cfg_fin = VisualStageConfig(
            stage_type=VisualStageType.TOPOLOGY_GRAPH,
            card_title="Liquidity Pool & Yield Farming",
            paradigm="finance",
        )
        html_fin = synth.generate_quantum_network(cfg_fin)
        assert "SETTLEMENT.HUB" in html_fin
        assert "ORDER.BOOK" in html_fin
        assert "0x7F-CORE" not in html_fin
    
    
    def test_code_terminal_parametric_props(self):
        synth = AlephVisualStageSynthesizer
        props = {
            "file_name": "LiquidityVault.sol",
            "status_badge": "● AUDITED [VERIFIED]",
            "code_lines": [
                "pragma solidity ^0.8.20;",
                "contract LiquidityVault {",
                "    uint256 public totalReserve;",
                "    function deposit() external payable {",
                "        totalReserve += msg.value;",
                "    }",
                "}"
            ]
        }
        cfg = VisualStageConfig(
            stage_type=VisualStageType.CODE_TERMINAL,
            props=props,
        )
        html_out = synth.generate_code_terminal(cfg)
    
        assert "LiquidityVault.sol" in html_out
        assert "● AUDITED [VERIFIED]" in html_out
        assert "01" in html_out
        assert "02" in html_out
        assert "07" in html_out
        assert "pragma" in html_out
        assert "contract" in html_out
        assert "totalReserve" in html_out
        assert "aleph-terminal-cursor" in html_out
    
    
    def test_code_terminal_contextual_fallbacks_domain(self):
        synth = AlephVisualStageSynthesizer
    
        # Alta Costura / Horlogerie: No debe ser Z3 SMT
        cfg_luxury = VisualStageConfig(
            stage_type=VisualStageType.CODE_TERMINAL,
            card_title="Calibre Mécanique et Atelier",
            paradigm="haute_luxury",
        )
        html_luxury = synth.generate_code_terminal(cfg_luxury)
        assert "calibre_chronometer.spec" in html_luxury
        assert "CHRONOMÈTRE CERTIFIÉ" in html_luxury
        assert "aleph_smt_prover.py" not in html_luxury
        assert "ParachromHairspring" in html_luxury
    
        # Finanzas: Debe generar contrato de bóveda
        cfg_fin = VisualStageConfig(
            stage_type=VisualStageType.CODE_TERMINAL,
            card_title="Smart Contract Vault",
            paradigm="finance",
        )
        html_fin = synth.generate_code_terminal(cfg_fin)
        assert "VaultLiquidity.sol" in html_fin
        assert "AUDITED" in html_fin
    
    
    def test_cryo_gauge_parametric_props_and_dynamic_stroke_dasharray(self):
        synth = AlephVisualStageSynthesizer
    
        # Test 1: fill_percentage = 0.50 (50% de 400.55 = 200.28 px)
        props_50 = {
            "metric_value": "142.5",
            "metric_unit": "ETH/s",
            "dial_label": "BURN_RATE: OPTIMAL",
            "fill_percentage": 0.50,
            "title": "ETHEREUM_GAS_TELEMETRY",
        }
        cfg_50 = VisualStageConfig(
            stage_type=VisualStageType.CRYO_GAUGE,
            props=props_50,
        )
        html_50 = synth.generate_cryo_gauge(cfg_50)
    
        assert "142.5" in html_50
        assert "ETH/s" in html_50
        assert "BURN_RATE: OPTIMAL" in html_50
        assert "ETHEREUM_GAS_TELEMETRY" in html_50
        # Arco activo al 50%: 400.55 * 0.50 = 200.28px
        assert "200.28" in html_50
        # Arco inactivo base: 400.55 133.52
        assert "400.55 133.52" in html_50
    
        # Test 2: fill_percentage = 0.75 (75% de 400.55 = 300.41 px)
        cfg_75 = VisualStageConfig(
            stage_type=VisualStageType.CRYO_GAUGE,
            fill_percentage=75.0,  # debe soportar formato 0-100
        )
        html_75 = synth.generate_cryo_gauge(cfg_75)
        assert "300.41" in html_75
    
    
    def test_cryo_gauge_contextual_fallbacks_no_cryo_slop(self):
        synth = AlephVisualStageSynthesizer
    
        # Alta Costura / Relojería: 28,800 Alt/h en lugar de 0.015 mK
        cfg_luxury = VisualStageConfig(
            stage_type=VisualStageType.CRYO_GAUGE,
            card_title="Régulateur de Haute Horlogerie",
            paradigm="haute_luxury",
        )
        html_luxury = synth.generate_cryo_gauge(cfg_luxury)
        assert "28,800" in html_luxury
        assert "Alt/h" in html_luxury
        assert "CHRONOMÈTRE ISOCRONE" in html_luxury
        assert "0.015" not in html_luxury
        assert "mK" not in html_luxury
    
        # Finanzas: 98.42 % APY
        cfg_fin = VisualStageConfig(
            stage_type=VisualStageType.CRYO_GAUGE,
            card_title="Capital Efficiency Index",
            paradigm="finance",
        )
        html_fin = synth.generate_cryo_gauge(cfg_fin)
        assert "98.42" in html_fin
        assert "% APY" in html_fin
        assert "CAPITAL_EFFICIENCY: OPTIMAL" in html_fin
        assert "0.015" not in html_fin
    
    
    def test_bezier_chart_parametric_data_points_and_peak_label(self):
        synth = AlephVisualStageSynthesizer
        props = {
            "data_points": [10.0, 45.0, 30.0, 85.0, 140.0],
            "peak_label": "$140.0M TVL",
            "title": "PROTOCOL_LIQUIDITY_SURGE",
            "badge": "+140% MOM",
        }
        cfg = VisualStageConfig(
            stage_type=VisualStageType.BEZIER_CHART,
            props=props,
        )
        html_out = synth.generate_bezier_chart(cfg)
    
        assert "$140.0M TVL" in html_out
        assert "PROTOCOL_LIQUIDITY_SURGE" in html_out
        assert "+140% MOM" in html_out
        assert "C " in html_out  # Curva Bézier Catmull-Rom
        # No debe forzar req/s si el usuario pasó peak_label
        assert "req/s" not in html_out
    
    
    def test_bezier_chart_contextual_fallbacks_domain(self):
        synth = AlephVisualStageSynthesizer
    
        # Finanzas
        cfg_fin = VisualStageConfig(
            stage_type=VisualStageType.BEZIER_CHART,
            card_title="Total Value Locked in DeFi",
            paradigm="finance",
        )
        html_fin = synth.generate_bezier_chart(cfg_fin)
        assert "Total Value Locked in DeFi" in html_fin
        assert "$184.2M" in html_fin
        assert "+38.4% APY YIELD" in html_fin
    
        # Lujo
        cfg_lux = VisualStageConfig(
            stage_type=VisualStageType.BEZIER_CHART,
            card_title="Patrimoine & Cote Horlogère",
            paradigm="haute_luxury",
        )
        html_lux = synth.generate_bezier_chart(cfg_lux)
        assert "Patrimoine &amp; Cote Horlogère" in html_lux or "Patrimoine" in html_lux
        assert "CHF 180K" in html_lux
        assert "+64.2% ARCHIVE_VALUE" in html_lux
    
    
    def test_swiss_geometry_parametric_props(self):
        synth = AlephVisualStageSynthesizer
        props = {
            "coordinates_text": "COORD: 40°42'N 74°00'W // NEW YORK",
            "figure_label": "FIG. 09 — METROPOLITAN GRID",
            "ratio_label": "RATIO: 16 : 9 // WIDESCREEN",
            "plate_label": "PLATE NY-01",
            "section_label": "URBAN PLANNING",
            "title": "MANHATTAN_GRID_CANON",
        }
        cfg = VisualStageConfig(
            stage_type=VisualStageType.SWISS_GEOMETRY,
            props=props,
        )
        html_out = synth.generate_swiss_geometry(cfg)
    
        assert "NEW YORK" in html_out
        assert "FIG. 09" in html_out
        assert "RATIO: 16 : 9 // WIDESCREEN" in html_out
        assert "PLATE NY-01" in html_out
        assert "URBAN PLANNING" in html_out
        assert "MANHATTAN_GRID_CANON" in html_out
    
    
    def test_swiss_geometry_contextual_fallbacks_domain(self):
        synth = AlephVisualStageSynthesizer
    
        # Alta Costura: París Place Vendôme
        cfg_lux = VisualStageConfig(
            stage_type=VisualStageType.SWISS_GEOMETRY,
            card_title="Maison de Haute Couture",
            paradigm="haute_luxury",
        )
        html_lux = synth.generate_swiss_geometry(cfg_lux)
        assert "PARIS - PLACE VEND" in html_lux
        assert "ATELIER" in html_lux
        assert "MAISON CANON" in html_lux
    
        # Finanzas: City of London
        cfg_fin = VisualStageConfig(
            stage_type=VisualStageType.SWISS_GEOMETRY,
            card_title="Quantitative Risk Frontier",
            paradigm="finance",
        )
        html_fin = synth.generate_swiss_geometry(cfg_fin)
        assert "CITY OF LONDON" in html_fin
        assert "PORTFOLIO EQUILIBRIUM MODEL" in html_fin

if __name__ == "__main__":
    unittest.main()
