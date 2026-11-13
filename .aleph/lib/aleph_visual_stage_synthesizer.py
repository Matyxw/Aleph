"""
.aleph/lib/aleph_visual_stage_synthesizer.py
Motor Soberano de Síntesis de Escenografía Visual Interna (Track 12 - Aleph Design Engine).
Estándar: Procedural Vector Synthesis / Zero-External-Assets / Micro-UI Internals / SMT-Safe.

Elimina el "Síndrome de la Tarjeta Bento Vacía" (Empty Bento Card Syndrome) presente en v0,
Lovable y Framer AI, reemplazando contenedores desérticos con generadores procedimentales
de arte vectorial SVG, HUDs de telemetría, micro-terminales de código y retículas
áureas matemáticamente exactas, 100% paramétricas, desacopladas de dominios fijos y
conducidas por datos de comp.props con inferencia semántica contextual.

8 Tipos Canónicos Completos:
1. CRYO_GAUGE: Tacómetros, diales de frecuencia, calibres, medidores porcentuales.
2. CODE_TERMINAL: Terminales de código con badges, nombres de archivo y syntax highlighting en OKLCH.
3. SWISS_GEOMETRY: Proporciones áureas (Phi = 1.618), coordenadas lat/lon, diagramas ortogonales de canon.
4. BEZIER_CHART: Curvas polinomiales Catmull-Rom a Bézier, gradientes de área y marcadores de pico.
5. TOPOLOGY_GRAPH: Redes nodales dirigidas (DAG), grafos de dependencias, trenes de engranajes y pipelines.
6. QUANTUM_NETWORK: Redes complejas con órbitas probabilísticas y nodos entrelazados.
7. RADIAL_RADAR: Gráficos polares de radar/sonar para telemetría multivariable y barridos angulares.
8. SPECTRAL_WAVEFORM: Formas de onda cinéticas y analizadores de espectro de frecuencia FFT.
"""

from __future__ import annotations

import enum
import html
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# ==============================================================================
# ENUMERACIONES Y CONFIGURACIÓN CANÓNICA
# ==============================================================================

class VisualStageType(str, enum.Enum):
    """8 Tipos canónicos de escenografía visual procedimental interna para tarjetas y paneles."""
    CRYO_GAUGE = "cryo_gauge"
    CODE_TERMINAL = "code_terminal"
    SWISS_GEOMETRY = "swiss_geometry"
    BEZIER_CHART = "bezier_chart"
    TOPOLOGY_GRAPH = "topology_graph"
    QUANTUM_NETWORK = "quantum_network"
    RADIAL_RADAR = "radial_radar"
    SPECTRAL_WAVEFORM = "spectral_waveform"

    # Alias de compatibilidad semántica
    RADAR_TELEMETRY = "radar_telemetry"


@dataclass
class VisualStageConfig:
    """Configuración paramétrica para la síntesis de un escenario visual."""
    stage_type: VisualStageType = VisualStageType.TOPOLOGY_GRAPH
    title: Optional[str] = None
    subtitle: Optional[str] = None
    accent_color: str = "var(--color-primary, oklch(0.78 0.18 205.0))"
    secondary_color: str = "var(--color-accent, oklch(0.65 0.26 310.0))"
    bg_surface: str = "var(--color-surface, oklch(0.12 0.02 250.0 / 0.65))"
    interactive: bool = True
    seed: int = 42

    # Diccionario conducido por comp.props
    props: Dict[str, Any] = field(default_factory=dict)

    # 1. CRYO_GAUGE
    metric_value: Optional[str] = None
    metric_unit: Optional[str] = None
    dial_label: Optional[str] = None
    fill_percentage: Optional[float] = None

    # 2. CODE_TERMINAL
    code_lines: Optional[List[str]] = None
    file_name: Optional[str] = None
    status_badge: Optional[str] = None
    code_snippet: Optional[str] = None

    # 3. SWISS_GEOMETRY
    coordinates_text: Optional[str] = None
    figure_label: Optional[str] = None
    ratio_label: Optional[str] = None
    plate_label: Optional[str] = None
    section_label: Optional[str] = None

    # 4. BEZIER_CHART
    data_points: Optional[List[float]] = None
    data_series: Optional[List[float]] = None
    peak_label: Optional[str] = None

    # 5. TOPOLOGY_GRAPH
    dag_layers: Optional[List[List[str]]] = None

    # 6. QUANTUM_NETWORK / TOPOLOGY_GRAPH
    node_labels: Optional[List[str]] = None
    hub_label: Optional[str] = None

    # 7. RADIAL_RADAR
    radar_axes: Optional[List[str]] = None
    radar_values: Optional[List[float]] = None
    target_pings: Optional[List[Dict[str, Any]]] = None

    # 8. SPECTRAL_WAVEFORM
    frequencies: Optional[List[float]] = None
    frequency_bands: Optional[List[str]] = None
    sample_rate: Optional[str] = None
    db_range: Optional[str] = None

    # Contexto semántico
    card_title: Optional[str] = None
    card_desc: Optional[str] = None
    paradigm: Optional[str] = None
    badge_text: Optional[str] = None

    def get_param(self, *keys: str, default: Any = None) -> Any:
        """
        Obtiene un parámetro buscando en orden en self.props (comp.props)
        y en los atributos directos de self.
        """
        for k in keys:
            if self.props and k in self.props and self.props[k] is not None:
                val = self.props[k]
                if isinstance(val, str) and not val.strip():
                    continue
                return val
            if hasattr(self, k):
                val = getattr(self, k)
                if val is not None:
                    if isinstance(val, str) and not val.strip():
                        continue
                    return val
        return default


# ==============================================================================
# UTILIDADES DE SINTAXIS Y TOKENIZACIÓN SEGURA
# ==============================================================================

def _highlight_code_line(line: str, is_last: bool = False) -> str:
    """Aplica coloreado de sintaxis sintético y seguro a una línea de código."""
    if 'tok-' in line or '<span' in line:
        res = line
    else:
        escaped = html.escape(line)
        # Comentarios (# o //)
        if "//" in escaped:
            parts = escaped.split("//", 1)
            comment_html = f'<span class="tok-cm">// {parts[1]}</span>'
            code_html = _highlight_code_line(parts[0], is_last=False)
            res = f"{code_html}{comment_html}"
        elif "#" in escaped:
            parts = escaped.split("#", 1)
            comment_html = f'<span class="tok-cm"># {parts[1]}</span>'
            code_html = _highlight_code_line(parts[0], is_last=False)
            res = f"{code_html}{comment_html}"
        else:
            # Strings ("..." o '...')
            res = re.sub(
                r'(&quot;.*?&quot;|&#x27;.*?&#x27;|&apos;.*?&apos;|"[^"]*"|\'[^\']*\')',
                r'<span class="tok-str">\1</span>',
                escaped
            )
            # Palabras clave de control y contratos
            kw_pat = r'\b(from|import|def|class|function|contract|assert|return|if|else|struct|interface|event|emit|require|public|private|view|pure|payable|external|internal|const|let|var|async|await|uint256|address|bool|string)\b'
            res = re.sub(kw_pat, r'<span class="tok-kw">\1</span>', res)

            # Números decimales o enteros
            res = re.sub(r'\b(\d+(\.\d+)?)\b', r'<span class="tok-num">\1</span>', res)

            # Tipos, Clases o Constantes PascalCase/UPPER
            res = re.sub(r'\b([A-Z][a-zA-Z0-9_]+)\b', r'<span class="tok-cls">\1</span>', res)

    if is_last and '<span class="aleph-terminal-cursor">' not in res:
        res += '<span class="aleph-terminal-cursor">▋</span>'
    return res


def _border_color_alpha(accent: str) -> str:
    """Calcula un color de borde compatible con variables OKLCH y hex."""
    if accent.startswith("#"):
        return f"{accent}40"
    return f"color-mix(in oklch, {accent} 35%, transparent)"


# ==============================================================================
# MOTOR SINTETIZADOR DE ESCENOGRAFÍA VISUAL PROCEDURAL
# ==============================================================================

class AlephVisualStageSynthesizer:
    """
    Motor Soberano de Síntesis Gráfica Procedimental.
    Sintetiza SVGs interactivos de alta fidelidad y micro-interfaces sin requerir
    imágenes rasterizadas ni dependencias de terceros, 100% paramétricos.
    """

    @classmethod
    def detect_semantic_domain(cls, config: VisualStageConfig) -> str:
        """
        Determina el dominio semántico (haute_luxury, finance, biotech_medicine,
        swiss_editorial, cyber_quantum) a partir del paradigma, títulos y descripciones.
        """
        paradigm = str(config.get_param("paradigm", default="") or "").lower()
        title = str(config.get_param("card_title", "title", "stage_title", default="") or "").lower()
        desc = str(config.get_param("card_desc", "description", "subtitle", default="") or "").lower()
        badge = str(config.get_param("badge_text", "badge", "stage_badge", "status_badge", default="") or "").lower()
        filename = str(config.get_param("file_name", "filename", default="") or "").lower()
        combined = f"{paradigm} {title} {desc} {badge} {filename}"

        # 1. Alta Costura / Lujo / Relojería / Sastrería / Artesanía
        if any(w in combined for w in (
            "haute_luxury", "couture", "moda", "fashion", "lujo", "luxury", "reloj", "watch",
            "horlogerie", "horology", "horolog", "atelier", "taller", "artesan", "joaillerie", "jewelry", "parfum",
            "perfume", "calibre", "soie", "silk", "sastrer", "sastreria", "prestige", "heritage"
        )):
            return "haute_luxury"

        # 2. Finanzas / DeFi / Cripto / Trading / Liquidez
        if any(w in combined for w in (
            "finan", "defi", "crypto", "token", "yield", "liquidez", "liquidity", "trading",
            "capital", "apy", "banca", "bank", "asset", "portafolio", "portfolio", "arbitrage",
            "vault", "swap", "orderbook", "bolsa", "inversión", "inversion", "equity", "clearing", "hedg"
        )):
            return "finance"

        # 3. Biotecnología / Medicina / Salud
        if any(w in combined for w in (
            "medicin", "biotech", "salud", "health", "clínic", "clinic", "farma", "pharma",
            "genom", "adn", "dna", "crispr", "terapia", "diagnost", "paciente", "célula", "cell",
            "biometr", "spo2", "cardio", "biomark", "hospital", "molecular", "enzym"
        )):
            return "biotech_medicine"

        # 4. Diseño Suizo / Tipografía / Editorial
        if any(w in combined for w in (
            "swiss_international", "literary_editorial", "editorial", "suiz", "swiss", "retícula",
            "reticula", "grid", "helvetica", "áurea", "aurea", "golden", "müller", "muller",
            "brockmann", "zürich", "zurich", "basel", "tipograf", "typograph", "modulor", "fibonacci"
        )):
            return "swiss_editorial"

        # 5. Default / Cuántico / SMT / Cyber Telemetry
        return "cyber_quantum"

    @classmethod
    def infer_stage_type(
        cls,
        card_title: str = "",
        card_desc: str = "",
        badge: str = "",
        paradigm: str = "cyber_telemetry",
        card_index: int = 0
    ) -> VisualStageType:
        """
        Infiere semánticamente el tipo de escenario visual óptimo analizando el
        título, descripción, badge y paradigma de diseño de la tarjeta.
        Cubre los 8 tipos canónicos completos sin vacíos ni repeticiones adyacentes.
        """
        content_txt = f"{card_title} {card_desc} {badge}".lower()

        # 1. RADIAL_RADAR: Radar polar, sonar, barrido azimutal, telemetría multivariable
        if any(w in content_txt for w in ("radar", "sonar", "polar", "azimut", "azim", "vectorial", "target", "rango", "range", "detecc", "spider", "multivariable")):
            return VisualStageType.RADIAL_RADAR

        # 2. SPECTRAL_WAVEFORM: Formas de onda, espectro de frecuencia, audio, FFT, RF
        if any(w in content_txt for w in ("espectr", "espectro", "spectral", "waveform", "onda", "wave", "frecuencia", "frec", "audio", "rf", "acústic", "acustic", "hertz", "hz", "equaliz", "armónic", "armonica", "fourier", "fft")):
            return VisualStageType.SPECTRAL_WAVEFORM

        # 3. TOPOLOGY_GRAPH: Grafos dirigidos, DAG, dependencias, trenes de engranajes, pipelines
        if any(w in content_txt for w in ("dag", "dependen", "pipeline", "flujo", "flow", "directed", "engranaje", "gear", "arqui", "cluster")):
            return VisualStageType.TOPOLOGY_GRAPH

        # 4. QUANTUM_NETWORK: Cuántica, entrelazamiento, órbitas, qubits, superposición
        if any(w in content_txt for w in ("cuántic", "cuantic", "quantum", "entangle", "entrelaz", "órbita", "orbita", "qubit", "hamiltonian", "malla", "mesh", "superposic")):
            return VisualStageType.QUANTUM_NETWORK

        # 5. CODE_TERMINAL: Código, terminal, SMT, AST, compilador, scripts
        if any(w in content_txt for w in ("código", "codigo", "code", "terminal", "z3", "smt", "ast", "cli", "shell", "solver", "compil", "kernel", "solidity", "script", "syntax")):
            return VisualStageType.CODE_TERMINAL

        # 6. CRYO_GAUGE: Tacómetros, diales de frecuencia, calibres, medidores porcentuales
        if any(w in content_txt for w in ("criogén", "criogen", "cryo", "gauge", "dial", "sensor", "temperatura", "tacómetr", "tacometr", "calibre", "porcent", "medidor", "rpm")):
            return VisualStageType.CRYO_GAUGE

        # 7. BEZIER_CHART: Curvas de rendimiento, latencia, throughput, métricas
        if any(w in content_txt for w in ("bezier", "curva", "gráfico", "grafico", "chart", "latencia", "throughput", "tráfico", "trafico", "financier", "delta", "volumen", "trend", "tvl", "growth")):
            return VisualStageType.BEZIER_CHART

        # 8. SWISS_GEOMETRY: Retículas suizas, proporción áurea, editorial, canon
        if any(w in content_txt for w in ("suiz", "swiss", "áurea", "aurea", "golden", "editorial", "retícula", "reticula", "grid", "lujo", "luxury", "brutalis", "proporci", "canon", "fibonacci", "muller", "brockmann")):
            return VisualStageType.SWISS_GEOMETRY

        # Heurística secundaria por términos generales de red o grafo
        if any(w in content_txt for w in ("topolog", "grafo", "graph", "red", "network")):
            return VisualStageType.TOPOLOGY_GRAPH if (card_index % 2 == 0) else VisualStageType.QUANTUM_NETWORK

        # Si el paradigma sugiere un estilo particular
        p_lower = (paradigm or "").lower()
        if any(p in p_lower for p in ("swiss_international", "literary_editorial", "haute_luxury")):
            if card_index % 2 == 0:
                return VisualStageType.SWISS_GEOMETRY

        # Asignación Cíclica Equilibrada de los 8 Tipos Canónicos
        cycle = [
            VisualStageType.CRYO_GAUGE,
            VisualStageType.CODE_TERMINAL,
            VisualStageType.SWISS_GEOMETRY,
            VisualStageType.BEZIER_CHART,
            VisualStageType.TOPOLOGY_GRAPH,
            VisualStageType.QUANTUM_NETWORK,
            VisualStageType.RADIAL_RADAR,
            VisualStageType.SPECTRAL_WAVEFORM,
        ]
        return cycle[card_index % len(cycle)]

    # --------------------------------------------------------------------------
    # 1. GENERADOR: CRYO GAUGE (Tacómetros, Diales de Frecuencia y Calibres)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_cryo_gauge(cls, config: VisualStageConfig) -> str:
        """
        Genera un tacómetro / dial circular de instrumentación trigonométrica con arco
        polar dinámico de 270 grados, marcas de graduación calculadas y lectura monumental.
        Conducido 100% por comp.props (metric_value, metric_unit, dial_label, fill_percentage).
        """
        accent = config.accent_color
        stage_id = f"cryo_{config.seed}"
        domain = cls.detect_semantic_domain(config)
        cx, cy, r = 300, 130, 85

        domain_defaults = {
            "haute_luxury": {
                "val": "28,800",
                "unit": "Alt/h",
                "dial": "CHRONOMÈTRE ISOCRONE",
                "title": "REGULATEUR_HAUTE_HORLOGERIE",
                "badge": "ISOCRONISMO: NOMINAL",
                "fill": 0.85
            },
            "finance": {
                "val": "98.42",
                "unit": "% APY",
                "dial": "CAPITAL_EFFICIENCY: OPTIMAL",
                "title": "LIQUIDITY_DEPTH_GAUGE",
                "badge": "LIQUIDITY DEPTH: AAA",
                "fill": 0.92
            },
            "biotech_medicine": {
                "val": "99.4",
                "unit": "SpO2",
                "dial": "HOMEOSTASIS: STABLE",
                "title": "BIOMETRIC_TELEMETRY",
                "badge": "VITALS: NOMINAL",
                "fill": 0.95
            },
            "swiss_editorial": {
                "val": "1.618",
                "unit": "PHI",
                "dial": "PROPORTION: DIVINE",
                "title": "HARMONIC_MODULATOR",
                "badge": "CANONICAL RATIO",
                "fill": 0.618
            },
            "cyber_quantum": {
                "val": "0.015",
                "unit": "mK",
                "dial": "THERMAL_NOISE: OPTIMAL",
                "title": "CRYO_CHAMBER_STAGE_2",
                "badge": "TELEMETRY ACTIVE",
                "fill": 0.78
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        metric_val = config.get_param("metric_value", "stage_value", "value", default=None) or defaults["val"]
        metric_unit = config.get_param("metric_unit", "stage_unit", "unit", default=None) or defaults["unit"]
        dial_label = config.get_param("dial_label", "sublabel", default=None) or defaults["dial"]
        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]

        raw_fill = config.get_param("fill_percentage", "fill_pct", "percentage", default=None)
        if raw_fill is not None:
            try:
                fill_pct = float(raw_fill)
                if fill_pct > 1.0:
                    fill_pct = fill_pct / 100.0
                fill_pct = max(0.0, min(1.0, fill_pct))
            except (ValueError, TypeError):
                fill_pct = defaults["fill"]
        else:
            fill_pct = defaults["fill"]

        ticks_svg = []
        total_ticks = 36
        start_angle = -225
        end_angle = 45
        span = end_angle - start_angle

        for i in range(total_ticks + 1):
            deg = start_angle + (i / total_ticks) * span
            rad = math.radians(deg)
            is_major = (i % 6 == 0)
            length = 10 if is_major else 5
            stroke_color = accent if is_major else "oklch(1 0 0 / 0.2)"
            stroke_w = "2" if is_major else "1"

            x1 = cx + (r + 14) * math.cos(rad)
            y1 = cy + (r + 14) * math.sin(rad)
            x2 = cx + (r + 14 + length) * math.cos(rad)
            y2 = cy + (r + 14 + length) * math.sin(rad)

            ticks_svg.append(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                f'stroke="{stroke_color}" stroke-width="{stroke_w}" stroke-linecap="round" />'
            )

        arc_len = 2 * math.pi * r
        dash_len = 400.55
        dash_gap = arc_len - dash_len
        active_dash_len = dash_len * fill_pct
        active_gap = arc_len - active_dash_len
        badge_border = _border_color_alpha(accent)

        return f"""<div class="aleph-visual-stage aleph-cryo-gauge-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge" style="color:{accent}; border-color:{badge_border};">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Dial de Telemetría Dinámica">
    <defs>
      <linearGradient id="{stage_id}_arcGrad" x1="0%" y1="100%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{config.secondary_color}" />
        <stop offset="70%" stop-color="{accent}" />
        <stop offset="100%" stop-color="oklch(1 0 0)" />
      </linearGradient>
      <filter id="{stage_id}_glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <!-- Anillos Concéntricos de Radar -->
    <g opacity="0.15">
      <circle cx="{cx}" cy="{cy}" r="35" fill="none" stroke="oklch(1 0 0)" stroke-width="1" />
      <circle cx="{cx}" cy="{cy}" r="60" fill="none" stroke="oklch(1 0 0)" stroke-width="1" stroke-dasharray="3 4" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="oklch(1 0 0)" stroke-width="1" />
      <circle cx="{cx}" cy="{cy}" r="115" fill="none" stroke="oklch(1 0 0)" stroke-width="1" stroke-dasharray="2 6" />
      <line x1="{cx - 125}" y1="{cy}" x2="{cx + 125}" y2="{cy}" stroke="oklch(1 0 0)" stroke-width="1" stroke-dasharray="4 4" />
      <line x1="{cx}" y1="{cy - 125}" x2="{cx}" y2="{cy + 125}" stroke="oklch(1 0 0)" stroke-width="1" stroke-dasharray="4 4" />
    </g>
    <!-- Marcas de Graduación Trigonométricas -->
    <g>
      {"".join(ticks_svg)}
    </g>
    <!-- Arco de Fondo Inactivo (400.55px de span) -->
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="oklch(1 0 0 / 0.06)" stroke-width="8"
      stroke-linecap="round" stroke-dasharray="{dash_len:.2f} {dash_gap:.2f}"
      transform="rotate(135 {cx} {cy})" />
    <!-- Arco Activo de Telemetría Dinámico -->
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#{stage_id}_arcGrad)" stroke-width="8"
      stroke-linecap="round" stroke-dasharray="{active_dash_len:.2f} {active_gap:.2f}"
      transform="rotate(135 {cx} {cy})" filter="url(#{stage_id}_glow)" />
    <!-- Haz de Barrido de Radar Animado -->
    <g class="aleph-radar-sweep-beam" style="transform-origin: {cx}px {cy}px;">
      <line x1="{cx}" y1="{cy}" x2="{cx + 115}" y2="{cy}" stroke="{accent}" stroke-width="1.8" stroke-linecap="round" />
      <polygon points="{cx},{cy} {cx + 115},{cy} {cx + 110},{cy - 28}" fill="{accent}" opacity="0.12" />
    </g>
    <!-- Lectura Digital Monumental Central -->
    <g text-anchor="middle">
      <text x="{cx}" y="{cy - 2}" font-family="monospace" font-size="28" font-weight="700" fill="oklch(1 0 0)" letter-spacing="-0.02em" class="tabular-nums">{html.escape(str(metric_val))}</text>
      <text x="{cx}" y="{cy + 20}" font-family="monospace" font-size="11" font-weight="600" fill="{accent}" letter-spacing="0.1em">{html.escape(str(metric_unit))}</text>
      <text x="{cx}" y="{cy + 36}" font-family="monospace" font-size="8" fill="oklch(1 0 0 / 0.4)" letter-spacing="0.05em">{html.escape(str(dial_label))}</text>
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 2. GENERADOR: CODE TERMINAL (HUD & Mini-Terminal con Syntax en OKLCH)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_code_terminal(cls, config: VisualStageConfig) -> str:
        """
        Genera un mini-terminal de código estilo macOS 100% paramétrico y conducido
        por comp.props (code_lines, file_name, status_badge) con syntax highlighting en OKLCH.
        """
        accent = config.accent_color
        stage_id = f"term_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "file_name": "calibre_chronometer.spec",
                "status_badge": "● CHRONOMÈTRE CERTIFIÉ",
                "code": [
                    "// Calibre 3235 — Micro-Mécanique Horlogère",
                    "oscillator = ParachromHairspring(freq=28800.0)",
                    "escapement = Chronergy(efficiency=1.15)",
                    "reserve = PowerBarrel(hours=70.0)",
                    "assert tolerance_per_day <= (-2.0, +2.0)  // COSC Standard"
                ],
                "branch": "⎇ geneva-master",
                "metric": "ISO 3159 // COSC ACCREDITED"
            },
            "finance": {
                "file_name": "VaultLiquidity.sol — Smart Contract",
                "status_badge": "● AUDITED [VERIFIED]",
                "code": [
                    "// Sovereign Liquidity Vault Contract",
                    "function deposit(uint256 amount) external nonReentrant {",
                    '    require(amount > 0, "ZeroAmount");',
                    "    shares = calculateShares(amount, totalReserve);",
                    "    emit LiquidityAdded(msg.sender, amount, shares);"
                ],
                "branch": "⎇ main (audited)",
                "metric": "GAS: 21,450 // OPTIMISM"
            },
            "biotech_medicine": {
                "file_name": "crispr_sequence_matcher.py — Biotech",
                "status_badge": "● SEQUENCED [100%]",
                "code": [
                    "from biotech.crispr import Cas9Target, GenomicLocus",
                    "# Target cleavage fidelity assay",
                    'locus = GenomicLocus(chromosome="11p15.5", strand="+")',
                    "off_targets = Cas9Target.scan(locus, max_mismatches=0)",
                    "assert len(off_targets) == 0  # Zero off-target cutting"
                ],
                "branch": "⎇ genomic-tree",
                "metric": "FIDELITY: 99.999% // CAS9"
            },
            "swiss_editorial": {
                "file_name": "typographic_grid.spec — Modular Canon",
                "status_badge": "● RASTER VALID",
                "code": [
                    "# Swiss Typographic Grid Formulation",
                    "ratio = GoldenSection(phi=1.6180339887)",
                    "baseline = BaselineGrid(unit=8.0, gutter=16.0)",
                    "columns = ModularGrid(count=12, max_width=1400.0)",
                    "assert columns.gutter_harmony() == True  // Müller-Brockmann"
                ],
                "branch": "⎇ zurich-canon",
                "metric": "GRID: 12-COL // PHI HARMONY"
            },
            "cyber_quantum": {
                "file_name": "aleph_smt_prover.py — Z3 Engine",
                "status_badge": "● PROVING [UNSAT]",
                "code": [
                    '<span class="tok-kw">from</span> <span class="tok-mod">aleph.z3</span> <span class="tok-kw">import</span> <span class="tok-cls">Solver</span>, <span class="tok-func">Int</span>, <span class="tok-func">ForAll</span>',
                    '<span class="tok-cm"># Verificación formal de ausencia de overflow</span>',
                    '<span class="tok-var">solver</span> = <span class="tok-cls">Solver</span>(theory=<span class="tok-str">"QF_NRA"</span>)',
                    '<span class="tok-var">solver</span>.<span class="tok-func">add</span>(<span class="tok-var">vw</span> &gt;= <span class="tok-num">320</span>, <span class="tok-var">overflow_px</span> == <span class="tok-num">0.0</span>)',
                    '<span class="tok-kw">assert</span> <span class="tok-var">solver</span>.<span class="tok-func">check</span>() == <span class="tok-const">UNSAT</span>  <span class="tok-cm"># 100% demostrado</span>',
                ],
                "branch": "⎇ main (clean)",
                "metric": "MEM: 3.8 MB // Z3 SMT"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        title_bar = config.get_param("file_name", "filename", "title", "stage_title", default=None) or defaults["file_name"]
        badge_val = config.get_param("status_badge", "badge_text", "stage_badge", "badge", default=None) or defaults["status_badge"]

        raw_code = config.get_param("code_lines", "code_snippet", default=None)
        if raw_code and isinstance(raw_code, list) and len(raw_code) > 0:
            lines_input = [str(l) for l in raw_code]
        elif raw_code and isinstance(raw_code, str):
            lines_input = [l for l in raw_code.splitlines() if l.strip()]
        else:
            lines_input = defaults["code"]

        code_lines_html = []
        for idx, line_content in enumerate(lines_input, start=1):
            is_last = (idx == len(lines_input))
            highlighted = _highlight_code_line(line_content, is_last=is_last)
            code_lines_html.append(
                f'<div class="aleph-terminal-line">'
                f'<span class="aleph-line-number tabular-nums">{idx:02d}</span>'
                f'<span class="aleph-line-code">{highlighted}</span>'
                f'</div>'
            )

        return f"""<div class="aleph-visual-stage aleph-code-terminal-stage">
  <div class="aleph-terminal-chrome">
    <div class="aleph-terminal-lights" aria-hidden="true">
      <span class="light close"></span>
      <span class="light min"></span>
      <span class="light max"></span>
    </div>
    <div class="aleph-terminal-title font-mono">{html.escape(title_bar)}</div>
    <div class="aleph-terminal-meta">
      <span class="aleph-terminal-badge live">{html.escape(badge_val)}</span>
      <span class="aleph-terminal-badge latency font-mono">118µs</span>
    </div>
  </div>
  <div class="aleph-terminal-body font-mono">
    {"".join(code_lines_html)}
  </div>
  <div class="aleph-terminal-telemetry-strip" style="padding:0 12px; opacity:0.35;">
    <svg viewBox="0 0 600 24" class="aleph-stage-svg aleph-terminal-wave-svg" preserveAspectRatio="none" role="img" aria-label="AST Execution Waveform">
      <defs>
        <linearGradient id="{stage_id}_waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="{accent}" stop-opacity="0.1" />
          <stop offset="50%" stop-color="{accent}" stop-opacity="0.6" />
          <stop offset="100%" stop-color="oklch(0.80 0.16 160)" stop-opacity="0.2" />
        </linearGradient>
      </defs>
      <path d="M 0 12 Q 75 4 150 12 T 300 12 T 450 12 T 600 12" fill="none" stroke="url(#{stage_id}_waveGrad)" stroke-width="1.5" />
      <circle cx="300" cy="12" r="3" fill="{accent}" />
      <circle cx="450" cy="12" r="2" fill="oklch(0.80 0.16 160)" />
    </svg>
  </div>
  <div class="aleph-terminal-footer font-mono">
    <span class="aleph-git-branch">{defaults["branch"]}</span>
    <span class="aleph-mem-metric">{defaults["metric"]}</span>
  </div>
</div>"""

    # --------------------------------------------------------------------------
    # 3. GENERADOR: SWISS GEOMETRY (Retículas Áureas y Composición Tipográfica)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_swiss_geometry(cls, config: VisualStageConfig) -> str:
        """
        Genera composiciones geométricas rigurosas basadas en la proporción áurea
        (Phi = 1.618), cruces de imprenta suiza, módulos de Fibonacci y micro-tipografía.
        """
        accent = config.accent_color
        stage_id = f"swiss_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "coords": "COORD: 48°51'N 2°20'E // PARIS - PLACE VENDÔME",
                "figure": "ATELIER D'ARTISANAT // COUTURE",
                "ratio": "PROPORTION DORÉE: 1 : 1.618",
                "plate": "COLLECTION N° 01",
                "section": "MAISON CANON",
                "title": "MAISON DE HAUTE COUTURE",
                "badge": "ÉDITION LIMITÉE"
            },
            "finance": {
                "coords": "COORD: 51°30'N 0°07'W // CITY OF LONDON",
                "figure": "PORTFOLIO EQUILIBRIUM MODEL",
                "ratio": "SHARPE RATIO: 3.24 // ALPHA",
                "plate": "INDEX F-1",
                "section": "RISK MATRIX",
                "title": "QUANTITATIVE_EQUILIBRIUM",
                "badge": "AAA SOVEREIGN"
            },
            "biotech_medicine": {
                "coords": "COORD: 47°33'N 7°35'E // BASEL PHARMA",
                "figure": "FIG. 12 — MOLECULAR HELIX GEOMETRY",
                "ratio": "HELICAL PITCH: 3.4 nm",
                "plate": "BIO-STRUCTURE",
                "section": "CRYSTALLOGRAPHY",
                "title": "BIOMOLECULAR_SYNTHESIS",
                "badge": "ISO 13485 CERT"
            },
            "swiss_editorial": {
                "coords": "COORD: 47°22'N 8°32'E // ZÜRICH",
                "figure": "FIG. 04 — MODULAR HARMONY",
                "ratio": "RATIO: 1 : 1.6180339887",
                "plate": "PLATE A-1",
                "section": "TYPOGRAPHIC GRID",
                "title": "GOLDEN_SECTION // § 1.61803",
                "badge": "SWISS CANON"
            },
            "cyber_quantum": {
                "coords": "COORD: 47°22'N 8°32'E // ZÜRICH",
                "figure": "FIG. 04 — MODULAR HARMONY",
                "ratio": "RATIO: 1 : 1.6180339887",
                "plate": "PLATE A-1",
                "section": "TYPOGRAPHIC GRID",
                "title": "GOLDEN_SECTION // § 1.61803",
                "badge": "SWISS CANON"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["swiss_editorial"])

        coord_txt = config.get_param("coordinates_text", "coordinates", "coords", default=None) or defaults["coords"]
        figure_lbl = config.get_param("figure_label", "figure", "fig", default=None) or defaults["figure"]
        ratio_lbl = config.get_param("ratio_label", "ratio", default=None) or defaults["ratio"]
        plate_lbl = config.get_param("plate_label", "plate", default=None) or defaults["plate"]
        section_lbl = config.get_param("section_label", "section", default=None) or defaults["section"]
        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]

        return f"""<div class="aleph-visual-stage aleph-swiss-geometry-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:oklch(1 0 0);"></span>
      <span class="aleph-stage-status-text font-mono">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge font-mono" style="color:oklch(1 0 0); border-color:oklch(1 0 0 / 0.25);">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Composición Modular Suiza">
    <defs>
      <pattern id="{stage_id}_dots" width="14" height="14" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1.1" fill="oklch(1 0 0 / 0.2)" />
      </pattern>
    </defs>
    <!-- Cuadrícula Modular Áurea de Fondo -->
    <rect x="50" y="30" width="310" height="195" fill="none" stroke="oklch(1 0 0 / 0.18)" stroke-width="1" />
    <rect x="360" y="30" width="190" height="195" fill="none" stroke="oklch(1 0 0 / 0.18)" stroke-width="1" />
    <rect x="360" y="30" width="190" height="120" fill="url(#{stage_id}_dots)" stroke="oklch(1 0 0 / 0.12)" stroke-width="0.75" />
    <rect x="360" y="150" width="118" height="75" fill="none" stroke="{accent}" stroke-width="1" stroke-opacity="0.6" />
    <rect x="478" y="150" width="72" height="75" fill="oklch(1 0 0 / 0.03)" stroke="oklch(1 0 0 / 0.12)" stroke-width="0.75" />
    <!-- Espiral Áurea de Fibonacci Estilizada -->
    <path d="M 360 225 A 310 195 0 0 1 50 30" fill="none" stroke="{accent}" stroke-width="1.8" stroke-dasharray="3 3" />
    <path d="M 360 30 A 190 120 0 0 1 550 150" fill="none" stroke="{accent}" stroke-width="1.5" />
    <!-- Cruces de Registro de Imprenta Suiza (+) -->
    <g stroke="oklch(1 0 0 / 0.4)" stroke-width="1">
      <path d="M 46 30 L 54 30 M 50 26 L 50 34" />
      <path d="M 546 30 L 554 30 M 550 26 L 550 34" />
      <path d="M 46 225 L 54 225 M 50 221 L 50 229" />
      <path d="M 546 225 L 554 225 M 550 221 L 550 229" />
      <path d="M 356 30 L 364 30 M 360 26 L 360 34" />
    </g>
    <!-- Micro-Tipografía de Placa Editorial y Coordenadas -->
    <g font-family="monospace" font-size="8" fill="oklch(1 0 0 / 0.5)">
      <text x="65" y="55" letter-spacing="0.1em">{html.escape(figure_lbl)}</text>
      <text x="65" y="70" letter-spacing="0.05em">{html.escape(coord_txt)}</text>
      <text x="65" y="210" letter-spacing="0.1em" fill="{accent}">{html.escape(ratio_lbl)}</text>
      <text x="375" y="170" letter-spacing="0.08em" font-weight="700" fill="oklch(1 0 0)">{html.escape(plate_lbl)}</text>
      <text x="375" y="185" letter-spacing="0.05em">{html.escape(section_lbl)}</text>
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 4. GENERADOR: BEZIER CHART (Curvas Spline Catmull-Rom a Bézier Paramétricas)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_bezier_chart(cls, config: VisualStageConfig) -> str:
        """
        Genera un gráfico financiero o de telemetría trazando una spline continua
        Catmull-Rom a Bézier cúbica conducida por una serie de datos real y pico de telemetría.
        """
        accent = config.accent_color
        stage_id = f"bezier_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "series": [18.0, 24.0, 32.0, 45.0, 60.0, 85.0, 110.0, 140.0, 180.0],
                "title": "VALUATION_ACCUMULATION",
                "badge": "+64.2% ARCHIVE_VALUE",
                "peak": "CHF 180K"
            },
            "finance": {
                "series": [102.5, 108.2, 115.0, 112.4, 128.6, 134.2, 142.8, 155.0, 184.2],
                "title": "TOTAL_VALUE_LOCKED",
                "badge": "+38.4% APY YIELD",
                "peak": "$184.2M"
            },
            "biotech_medicine": {
                "series": [36.2, 36.4, 36.5, 36.8, 36.7, 36.6, 36.5, 36.6],
                "title": "HOMEOSTATIC_EQUILIBRIUM",
                "badge": "STABLE [NORMAL]",
                "peak": "36.6 °C"
            },
            "swiss_editorial": {
                "series": [1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0, 34.0, 55.0],
                "title": "FIBONACCI_HARMONICS",
                "badge": "RATIO 1.618",
                "peak": "55.0 φ"
            },
            "cyber_quantum": {
                "series": [28.0, 42.0, 36.0, 58.0, 52.0, 84.0, 76.0, 95.0, 118.0, 142.0],
                "title": "THROUGHPUT_SPECTROGRAM",
                "badge": "+42.6% OVERFLOW_FREE",
                "peak": "142 req/s"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        raw_series = config.get_param("data_points", "data_series", "series", default=None)
        if raw_series and isinstance(raw_series, list) and len(raw_series) > 0:
            try:
                data = [float(v) for v in raw_series]
            except (ValueError, TypeError):
                data = defaults["series"]
        else:
            data = defaults["series"]

        if len(data) == 1:
            data = [data[0], data[0]]

        n = len(data)
        min_v = min(data)
        max_v = max(data)
        range_v = (max_v - min_v) if max_v != min_v else 1.0

        x_min, x_max = 60.0, 540.0
        y_min, y_max = 40.0, 205.0
        pts: List[Tuple[float, float]] = []

        for idx, val in enumerate(data):
            x = x_min + (idx / (n - 1)) * (x_max - x_min)
            norm = (val - min_v) / range_v
            y = y_max - norm * (y_max - y_min)
            pts.append((x, y))

        path_segments = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2

            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0

            path_segments.append(
                f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}"
            )

        curve_path = " ".join(path_segments)
        area_path = f"{curve_path} L {pts[-1][0]:.2f} {y_max:.2f} L {pts[0][0]:.2f} {y_max:.2f} Z"

        last_pt = pts[-1]
        last_val = data[-1]

        peak_label = config.get_param("peak_label", "metric", "peak", default=None)
        if not peak_label:
            if domain == "cyber_quantum":
                peak_label = f"{last_val:.0f} req/s"
            else:
                peak_label = defaults["peak"]

        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]

        def _fmt_axis_val(v: float) -> str:
            if abs(v) >= 1_000_000:
                return f"{v/1_000_000:.1f}M"
            if abs(v) >= 1_000:
                return f"{v/1_000:.1f}K"
            return f"{v:.1f}"

        y_labels = [
            _fmt_axis_val(max_v),
            _fmt_axis_val(min_v + range_v * 0.66),
            _fmt_axis_val(min_v + range_v * 0.33),
            _fmt_axis_val(min_v),
        ]

        return f"""<div class="aleph-visual-stage aleph-bezier-chart-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge font-mono" style="color:oklch(0.80 0.16 160); border-color:oklch(0.80 0.16 160 / 0.3);">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Curva de Rendimiento Bézier">
    <defs>
      <linearGradient id="{stage_id}_areaGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.32" />
        <stop offset="85%" stop-color="{accent}" stop-opacity="0.02" />
        <stop offset="100%" stop-color="{accent}" stop-opacity="0.0" />
      </linearGradient>
      <linearGradient id="{stage_id}_lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{config.secondary_color}" />
        <stop offset="60%" stop-color="{accent}" />
        <stop offset="100%" stop-color="oklch(1 0 0)" />
      </linearGradient>
      <filter id="{stage_id}_glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <!-- Cuadrícula de Calibración Cartesiana -->
    <g opacity="0.12" stroke="oklch(1 0 0)" stroke-dasharray="2 4">
      <line x1="{x_min}" y1="50" x2="{x_max}" y2="50" />
      <line x1="{x_min}" y1="100" x2="{x_max}" y2="100" />
      <line x1="{x_min}" y1="150" x2="{x_max}" y2="150" />
      <line x1="{x_min}" y1="{y_max}" x2="{x_max}" y2="{y_max}" />
    </g>
    <!-- Etiquetas de Eje Y -->
    <g font-family="monospace" font-size="8" fill="oklch(1 0 0 / 0.4)" text-anchor="end">
      <text x="{x_min - 8}" y="53">{y_labels[0]}</text>
      <text x="{x_min - 8}" y="103">{y_labels[1]}</text>
      <text x="{x_min - 8}" y="153">{y_labels[2]}</text>
      <text x="{x_min - 8}" y="{y_max + 3}">{y_labels[3]}</text>
    </g>
    <!-- Área Rellena con Gradiente -->
    <path d="{area_path}" fill="url(#{stage_id}_areaGrad)" />
    <!-- Trazado de Curva Bézier Paramétrica -->
    <path d="{curve_path}" fill="none" stroke="url(#{stage_id}_lineGrad)" stroke-width="2.5" stroke-linecap="round" filter="url(#{stage_id}_glow)" />
    <!-- Marcador de Pico Activo -->
    <circle cx="{last_pt[0]:.2f}" cy="{last_pt[1]:.2f}" r="12" fill="none" stroke="{accent}" stroke-opacity="0.35" class="aleph-ripple-circle" />
    <circle cx="{last_pt[0]:.2f}" cy="{last_pt[1]:.2f}" r="5" fill="{accent}" />
    <circle cx="{last_pt[0]:.2f}" cy="{last_pt[1]:.2f}" r="2" fill="oklch(1 0 0)" />
    <!-- Tooltip HUD de Telemetría Dinámico -->
    <g transform="translate({last_pt[0] - 68}, {last_pt[1] - 38})">
      <rect width="84" height="26" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.92))" stroke="{accent}" stroke-width="1" />
      <text x="42" y="16" font-family="monospace" font-size="10" font-weight="700" fill="oklch(1 0 0)" text-anchor="middle" class="tabular-nums">{html.escape(str(peak_label))}</text>
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 5. GENERADOR: TOPOLOGY GRAPH (Redes Nodales Dirigidas, DAG y Trenes de Engranajes)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_topology_graph(cls, config: VisualStageConfig) -> str:
        """
        Genera una red nodal dirigida paramétrica (DAG de dependencias, trenes de engranajes
        o pipeline de transformaciones) con nodos jerárquicos por capas, aristas dirigidas
        con cabezas de flecha vectoriales SVG y paquetes de pulsos animados en flujo unidireccional.
        """
        accent = config.accent_color
        secondary = config.secondary_color
        stage_id = f"dag_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "title": "CHRONOMÈTRE_GEAR_TRAIN",
                "badge": "ENGRENAGE // COSC",
                "hub": "ECHAPPEMENT",
                "nodes": ["BARILLET", "ROUE_MOY", "ROUE_SEC", "BALANCIER", "TOURBILLON", "AFFICHAGE"],
                "meta": "ISO 3159 // 28,800 A/h"
            },
            "finance": {
                "title": "DIRECTED_SETTLEMENT_DAG",
                "badge": "FINALITY // 400ms",
                "hub": "ORDER.ROUTER",
                "nodes": ["INGEST.TX", "RISK.CHECK", "BATCH.CLEAR", "ON_CHAIN", "AUDIT.LOG", "MEMPOOL"],
                "meta": "LATENCY: 400ms // ZERO_REVERT"
            },
            "biotech_medicine": {
                "title": "MOLECULAR_PATHWAY_DAG",
                "badge": "CASCADE // ACTIVE",
                "hub": "NUCLEUS.SIG",
                "nodes": ["RECEPTOR", "KINASE.A", "PHOSPHO.B", "EXPRESSION", "ASSAY.RES", "LIGAND"],
                "meta": "FIDELITY: 99.999% // ACTIVE"
            },
            "swiss_editorial": {
                "title": "MODULAR_LAYOUT_PIPELINE",
                "badge": "12-COL // HARMONY",
                "hub": "BASELINE.GRID",
                "nodes": ["TYPO.SCALE", "COL.SPEC", "OPTICAL.KERN", "CANON.EXP", "PRINT.PROO", "MARGIN"],
                "meta": "PHI: 1.618 // MÜLLER-BROCKMANN"
            },
            "cyber_quantum": {
                "title": "DEPENDENCY_DIRECTED_GRAPH",
                "badge": "DAG // ZERO_CYCLE",
                "hub": "SSA.KERNEL",
                "nodes": ["AST.INGEST", "CFG.BUILD", "Z3.SOLVER", "BINARY.EMIT", "VERIFY.OK", "CODEGEN"],
                "meta": "SMT PROOF: UNSAT // 118µs"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]
        hub_lbl = config.get_param("hub_label", default=None) or defaults["hub"]

        raw_nodes = config.get_param("node_labels", default=None)
        if raw_nodes and isinstance(raw_nodes, list) and len(raw_nodes) > 0:
            user_nodes = [str(n) for n in raw_nodes]
        else:
            user_nodes = defaults["nodes"]

        dag_nodes_list = []
        for i in range(6):
            if i < len(user_nodes):
                dag_nodes_list.append(user_nodes[i])
            else:
                dag_nodes_list.append(defaults["nodes"][i % len(defaults["nodes"])])

        # Coordenadas jerárquicas en 5 capas DAG:
        # L0: Ingest (75, 130)
        # L1: Transform A (190, 75), Transform B (190, 185)
        # L2: Hub / Kernel (310, 130)
        # L3: Verify A (430, 75), Verify B (430, 185)
        # L4: Sink (535, 130)
        nodes = [
            {"id": "n0", "x": 30, "y": 112, "w": 85, "h": 36, "lbl": dag_nodes_list[0], "status": "INGEST"},
            {"id": "n1", "x": 145, "y": 57, "w": 90, "h": 36, "lbl": dag_nodes_list[1], "status": "TRANS"},
            {"id": "n2", "x": 145, "y": 167, "w": 90, "h": 36, "lbl": dag_nodes_list[2], "status": "STAGE"},
            {"id": "hub", "x": 265, "y": 110, "w": 95, "h": 40, "lbl": hub_lbl, "status": "KERNEL", "is_hub": True},
            {"id": "n3", "x": 385, "y": 57, "w": 90, "h": 36, "lbl": dag_nodes_list[3], "status": "VERIFY"},
            {"id": "n4", "x": 385, "y": 167, "w": 90, "h": 36, "lbl": dag_nodes_list[4], "status": "AUDIT"},
            {"id": "n5", "x": 500, "y": 112, "w": 85, "h": 36, "lbl": dag_nodes_list[5], "status": "EMIT"},
        ]

        # Aristas dirigidas (con cabezas de flecha vectoriales)
        directed_edges = [
            ("M 115 130 C 130 130, 130 75, 145 75", "e1"),
            ("M 115 130 C 130 130, 130 185, 145 185", "e2"),
            ("M 235 75 C 250 75, 250 130, 265 130", "e3"),
            ("M 235 185 C 250 185, 250 130, 265 130", "e4"),
            ("M 360 130 C 372 130, 372 75, 385 75", "e5"),
            ("M 360 130 C 372 130, 372 185, 385 185", "e6"),
            ("M 475 75 C 488 75, 488 130, 500 130", "e7"),
            ("M 475 185 C 488 185, 488 130, 500 130", "e8"),
            ("M 235 75 C 310 35, 310 35, 385 75", "e9"),  # Bypass superior
        ]

        edges_svg = []
        for path_d, edge_id in directed_edges:
            edges_svg.append(
                f'<path d="{path_d}" stroke="oklch(1 0 0 / 0.14)" stroke-width="1.5" fill="none" marker-end="url(#{stage_id}_dagArrow)" stroke-linecap="round" />'
            )
            edges_svg.append(
                f'<path d="{path_d}" stroke="url(#{stage_id}_pulseGrad)" stroke-width="2.2" fill="none" '
                f'stroke-linecap="round" stroke-dasharray="14 100" class="aleph-pulse-line" />'
            )

        nodes_svg = []
        for n in nodes:
            x, y, w, h = n["x"], n["y"], n["w"], n["h"]
            is_hub = n.get("is_hub", False)
            stroke_col = accent if is_hub else "oklch(1 0 0 / 0.22)"
            stroke_w = "1.8" if is_hub else "1"
            dot_col = accent if is_hub else secondary

            nodes_svg.append(
                f'<g class="aleph-dag-node" transform="translate({x}, {y})">'
                f'<rect width="{w}" height="{h}" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" '
                f'stroke="{stroke_col}" stroke-width="{stroke_w}" />'
                f'<circle cx="12" cy="{h / 2}" r="3.5" fill="{dot_col}" />'
                f'<text x="22" y="{h / 2 - 2}" font-family="monospace" font-size="8.5" font-weight="600" '
                f'fill="oklch(1 0 0 / 0.9)" letter-spacing="0.04em">{html.escape(n["lbl"])}</text>'
                f'<text x="22" y="{h / 2 + 9}" font-family="monospace" font-size="6.5" '
                f'fill="oklch(1 0 0 / 0.45)" letter-spacing="0.08em">{n["status"]}</text>'
                f'</g>'
            )

        badge_border = _border_color_alpha(accent)

        return f"""<div class="aleph-visual-stage aleph-topology-graph-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent}; box-shadow:0 0 8px {accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge" style="color:{accent}; border-color:{badge_border};">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Grafo Dirigido de Dependencias">
    <defs>
      <marker id="{stage_id}_dagArrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{accent}" />
      </marker>
      <linearGradient id="{stage_id}_pulseGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{secondary}" stop-opacity="0" />
        <stop offset="50%" stop-color="{accent}" stop-opacity="1" />
        <stop offset="100%" stop-color="oklch(1 0 0)" stop-opacity="0" />
      </linearGradient>
    </defs>
    <!-- Capas Guía de Fondo -->
    <g opacity="0.08" stroke="oklch(1 0 0)" stroke-dasharray="2 6">
      <line x1="72" y1="20" x2="72" y2="240" />
      <line x1="190" y1="20" x2="190" y2="240" />
      <line x1="312" y1="20" x2="312" y2="240" />
      <line x1="430" y1="20" x2="430" y2="240" />
      <line x1="542" y1="20" x2="542" y2="240" />
      <line x1="20" y1="130" x2="580" y2="130" />
    </g>
    <!-- Aristas Dirigidas con Flechas -->
    <g class="aleph-dag-edges">
      {"".join(edges_svg)}
    </g>
    <!-- Nodos del Grafo por Capas -->
    <g class="aleph-dag-nodes">
      {"".join(nodes_svg)}
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 6. GENERADOR: QUANTUM NETWORK (Redes Complejas con Órbitas y Entrelazamiento)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_quantum_network(cls, config: VisualStageConfig) -> str:
        """
        Genera una red cuántica procedimental con núcleo de entrelazamiento, órbitas
        probabilísticas elípticas, enlaces de interferencia armónica y estados bra-ket.
        """
        accent = config.accent_color
        secondary = config.secondary_color
        stage_id = f"qnet_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "hub": "ATELIER.CENTRAL",
                "nodes": ["SOIE.LYON", "OR.18K", "CUIR.SELL", "TOURBILLON", "FINITION", "ASSEMBLAGE"],
                "title": "ATELIER_SAVOIR_FAIRE",
                "badge": "FAIT MAIN // 100%"
            },
            "finance": {
                "hub": "SETTLEMENT.HUB",
                "nodes": ["ORDER.BOOK", "CLEARING", "ORACLE.FEED", "SWAP.ROUTE", "VAULT.01", "ARBITRAGE"],
                "title": "LIQUIDITY_TOPOLOGY",
                "badge": "DEPTH: $1.42B"
            },
            "biotech_medicine": {
                "hub": "GENOME.CORE",
                "nodes": ["CRISPR.SEQ", "ENZYME.A", "PROTEIN.02", "ASSAY.V4", "RECEPTOR", "CELL.PATH"],
                "title": "BIOMOLECULAR_NETWORK",
                "badge": "FIDELITY: 99.999%"
            },
            "swiss_editorial": {
                "hub": "ZÜRICH.MOD",
                "nodes": ["AXIS.HORIZ", "AXIS.VERT", "GOLDEN.CUT", "CANON.A", "MODULOR", "KERNING"],
                "title": "MODULAR_TOPOLOGY",
                "badge": "RATIO: 1.618"
            },
            "cyber_quantum": {
                "hub": "0x7F-CORE",
                "nodes": ["Q-NODE.01", "Q-NODE.02", "Q-NODE.03", "Q-NODE.04", "GATE.A", "GATE.B"],
                "title": "TOPOLOGICAL_ENTANGLEMENT",
                "badge": "FIDELITY: 99.982%"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        hub_lbl = config.get_param("hub_label", default=None) or defaults["hub"]
        raw_nodes = config.get_param("node_labels", default=None)
        if raw_nodes and isinstance(raw_nodes, list) and len(raw_nodes) > 0:
            user_nodes = [str(n) for n in raw_nodes]
        else:
            user_nodes = defaults["nodes"]

        final_nodes = []
        for i in range(6):
            if i < len(user_nodes):
                final_nodes.append(user_nodes[i])
            else:
                final_nodes.append(defaults["nodes"][i % len(defaults["nodes"])])

        nodes = [
            {"id": "hub", "cx": 300, "cy": 130, "r": 9, "label": hub_lbl, "hub": True},
            {"id": "n1", "cx": 140, "cy": 70, "r": 6, "label": final_nodes[0]},
            {"id": "n2", "cx": 110, "cy": 190, "r": 5, "label": final_nodes[1]},
            {"id": "n3", "cx": 460, "cy": 75, "r": 6, "label": final_nodes[2]},
            {"id": "n4", "cx": 490, "cy": 185, "r": 5, "label": final_nodes[3]},
            {"id": "n5", "cx": 230, "cy": 220, "r": 5, "label": final_nodes[4]},
            {"id": "n6", "cx": 370, "cy": 220, "r": 5, "label": final_nodes[5]},
        ]

        edges = [
            ("M 300 130 Q 210 80 140 70", "p1"),
            ("M 300 130 Q 190 170 110 190", "p2"),
            ("M 300 130 Q 390 85 460 75", "p3"),
            ("M 300 130 Q 410 170 490 185", "p4"),
            ("M 300 130 Q 260 190 230 220", "p5"),
            ("M 300 130 Q 340 190 370 220", "p6"),
            ("M 140 70 Q 100 130 110 190", "p7"),
            ("M 460 75 Q 500 130 490 185", "p8"),
            ("M 230 220 Q 300 245 370 220", "p9"),
        ]

        edges_svg = []
        for path_d, edge_id in edges:
            edges_svg.append(
                f'<path d="{path_d}" stroke="oklch(1 0 0 / 0.08)" stroke-width="1.5" fill="none" stroke-linecap="round" />'
            )
            edges_svg.append(
                f'<path d="{path_d}" stroke="url(#{stage_id}_pulseGrad)" stroke-width="2.5" fill="none" '
                f'stroke-linecap="round" stroke-dasharray="16 140" class="aleph-pulse-line" />'
            )

        nodes_svg = []
        for n in nodes:
            cx, cy, r = n["cx"], n["cy"], n["r"]
            if n.get("hub"):
                nodes_svg.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{r * 2.8}" fill="none" stroke="{accent}" stroke-opacity="0.25" class="aleph-ripple-circle" />'
                    f'<circle cx="{cx}" cy="{cy}" r="{r * 1.8}" fill="none" stroke="{accent}" stroke-opacity="0.5" />'
                    f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{accent}" filter="url(#{stage_id}_glow)" />'
                    f'<circle cx="{cx}" cy="{cy}" r="{r * 0.4}" fill="oklch(1 0 0)" />'
                    f'<text x="{cx}" y="{cy - 16}" text-anchor="middle" font-family="monospace" font-size="9" fill="{accent}" font-weight="600" letter-spacing="0.08em">{html.escape(n["label"])}</text>'
                )
            else:
                nodes_svg.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{r * 1.8}" fill="none" stroke="oklch(1 0 0 / 0.15)" />'
                    f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{secondary}" />'
                    f'<circle cx="{cx}" cy="{cy}" r="{r * 0.4}" fill="oklch(1 0 0)" />'
                    f'<text x="{cx}" y="{cy + 15}" text-anchor="middle" font-family="monospace" font-size="8" fill="oklch(1 0 0 / 0.55)">{html.escape(n["label"])}</text>'
                )

        badge_txt = config.get_param("badge_text", "stage_badge", "badge", "fidelity", default=None) or defaults["badge"]
        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_border = _border_color_alpha(accent)

        return f"""<div class="aleph-visual-stage aleph-quantum-network-stage aleph-topology-graph-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent}; box-shadow:0 0 8px {accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge" style="color:{accent}; border-color:{badge_border};">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Visualizador de Red Cuántica">
    <defs>
      <linearGradient id="{stage_id}_pulseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0" />
        <stop offset="50%" stop-color="{accent}" stop-opacity="1" />
        <stop offset="100%" stop-color="oklch(1 0 0)" stop-opacity="0" />
      </linearGradient>
      <filter id="{stage_id}_glow" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="3.5" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <!-- Órbitas Cuánticas Elípticas de Fondo -->
    <g opacity="0.12" fill="none" stroke="oklch(1 0 0)">
      <line x1="40" y1="130" x2="560" y2="130" stroke-dasharray="2 6" />
      <line x1="300" y1="20" x2="300" y2="240" stroke-dasharray="2 6" />
      <ellipse cx="300" cy="130" rx="110" ry="50" stroke-dasharray="2 6" transform="rotate(-20 300 130)" />
      <ellipse cx="300" cy="130" rx="180" ry="80" stroke-dasharray="3 8" transform="rotate(15 300 130)" />
      <ellipse cx="300" cy="130" rx="240" ry="105" stroke-dasharray="2 10" transform="rotate(-10 300 130)" />
    </g>
    <!-- Aristas con Pulsos Cuánticos -->
    <g class="aleph-qnet-edges">
      {"".join(edges_svg)}
    </g>
    <!-- Nodos del Grafo Cuántico -->
    <g class="aleph-qnet-nodes">
      {"".join(nodes_svg)}
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 7. GENERADOR: RADIAL RADAR (Gráficos Polares y Telemetría Multivariable)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_radial_radar(cls, config: VisualStageConfig) -> str:
        """
        Genera un radar polar / sonar de telemetría multivariable con anillos de rango,
        8 radios azimutales, polígono de cobertura vectorial y haz de barrido animado.
        """
        accent = config.accent_color
        secondary = config.secondary_color
        stage_id = f"radar_{config.seed}"
        domain = cls.detect_semantic_domain(config)
        cx, cy, R = 300, 130, 95

        domain_defaults = {
            "haute_luxury": {
                "title": "CHRONOMETRIC_DISPERSION_RADAR",
                "badge": "ISOCRONISMO: 6-POS",
                "axes": ["DIAL_UP", "DIAL_DN", "CR_LEFT", "CR_RT", "CR_UP", "CR_DN"],
                "values": [0.92, 0.90, 0.88, 0.89, 0.94, 0.91],
                "targets": [("POS-1", 45, 68), ("POS-2", 180, 75), ("POS-3", 290, 80)]
            },
            "finance": {
                "title": "MULTIVARIABLE_RISK_RADAR",
                "badge": "ALPHA // 6-FACTOR",
                "axes": ["VOLATILITY", "LIQUIDITY", "MOMENTUM", "SHARPE", "SORTINO", "BETA"],
                "values": [0.75, 0.92, 0.84, 0.88, 0.82, 0.70],
                "targets": [("ALPHA-1", 30, 65), ("HEDGE-2", 150, 55), ("ARB-3", 240, 78)]
            },
            "biotech_medicine": {
                "title": "BIOMETRIC_POLAR_SCAN",
                "badge": "HOMEOSTASIS 360°",
                "axes": ["SPO2", "HEART_RATE", "PRESSURE", "TEMP", "RESP", "GLUCOSE"],
                "values": [0.95, 0.88, 0.82, 0.91, 0.86, 0.89],
                "targets": [("VIT-01", 60, 72), ("VIT-02", 135, 68), ("VIT-03", 270, 64)]
            },
            "swiss_editorial": {
                "title": "SWISS_TYPOGRAPHIC_RADAR",
                "badge": "CANON 6-AXES",
                "axes": ["KERNING", "LEADING", "MARGIN", "PROPORTION", "WEIGHT", "CONTRAST"],
                "values": [0.95, 0.92, 0.98, 0.90, 0.88, 0.94],
                "targets": [("GRID-A", 45, 78), ("CANON-B", 180, 82), ("AXIS-C", 315, 70)]
            },
            "cyber_quantum": {
                "title": "POLAR_TELEMETRY_RADAR",
                "badge": "SONAR // 8-BAND SCAN",
                "axes": ["LATENCY", "THROUGHPUT", "MEMORY", "Z3_PROOF", "CONCURRENCY", "ISOLATION", "PURITY", "DENSITY"],
                "values": [0.92, 0.88, 0.78, 0.96, 0.85, 0.90, 0.94, 0.86],
                "targets": [("TGT-01", 35, 60), ("TGT-02", 140, 72), ("TGT-03", 245, 65)]
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]

        raw_axes = config.get_param("radar_axes", default=None)
        axes = [str(a) for a in raw_axes] if (raw_axes and isinstance(raw_axes, list)) else defaults["axes"]

        raw_vals = config.get_param("radar_values", default=None)
        if raw_vals and isinstance(raw_vals, list) and len(raw_vals) > 0:
            try:
                values = [float(v) for v in raw_vals]
            except (ValueError, TypeError):
                values = defaults["values"]
        else:
            values = defaults["values"]

        num_spokes = len(axes)
        if len(values) < num_spokes:
            values.extend([0.75] * (num_spokes - len(values)))
        values = values[:num_spokes]

        # Anillos concéntricos de rango
        range_rings_svg = []
        for pct_r, lbl in ((0.25, "25%"), (0.50, "50%"), (0.75, "75%"), (1.00, "100%")):
            curr_r = R * pct_r
            dash = "2 4" if pct_r < 1.0 else "none"
            range_rings_svg.append(
                f'<circle cx="{cx}" cy="{cy}" r="{curr_r:.2f}" fill="none" stroke="oklch(1 0 0 / 0.12)" stroke-width="1" stroke-dasharray="{dash}" />'
            )
            range_rings_svg.append(
                f'<text x="{cx + curr_r * 0.707:.2f}" y="{cy - curr_r * 0.707 - 2:.2f}" font-family="monospace" font-size="6.5" fill="oklch(1 0 0 / 0.35)">{lbl}</text>'
            )

        # Ejes radiales y polígono multivariable
        spokes_svg = []
        poly_pts = []
        vertex_circles_svg = []

        for idx, axis_name in enumerate(axes):
            ang_deg = -90.0 + (idx / num_spokes) * 360.0
            ang_rad = math.radians(ang_deg)

            x_outer = cx + (R + 12) * math.cos(ang_rad)
            y_outer = cy + (R + 12) * math.sin(ang_rad)
            x_line = cx + R * math.cos(ang_rad)
            y_line = cy + R * math.sin(ang_rad)

            spokes_svg.append(
                f'<line x1="{cx}" y1="{cy}" x2="{x_line:.2f}" y2="{y_line:.2f}" stroke="oklch(1 0 0 / 0.16)" stroke-width="1" />'
            )

            # Alineación de texto según cuadrante
            anchor = "middle"
            if math.cos(ang_rad) > 0.3:
                anchor = "start"
            elif math.cos(ang_rad) < -0.3:
                anchor = "end"

            spokes_svg.append(
                f'<text x="{x_outer:.2f}" y="{y_outer + 3:.2f}" text-anchor="{anchor}" font-family="monospace" font-size="7.5" fill="oklch(1 0 0 / 0.55)">{html.escape(axis_name)}</text>'
            )

            val = max(0.05, min(1.0, values[idx]))
            vx = cx + R * val * math.cos(ang_rad)
            vy = cy + R * val * math.sin(ang_rad)
            poly_pts.append(f"{vx:.2f},{vy:.2f}")

            vertex_circles_svg.append(
                f'<circle cx="{vx:.2f}" cy="{vy:.2f}" r="3" fill="{secondary}" stroke="oklch(1 0 0)" stroke-width="0.8" />'
            )

        poly_str = " ".join(poly_pts)

        # Objetivos detectados (blips de radar)
        target_blips_svg = []
        raw_targets = config.get_param("target_pings", default=None)
        targets = raw_targets if (raw_targets and isinstance(raw_targets, list)) else defaults["targets"]

        for item in targets:
            if isinstance(item, tuple) and len(item) == 3:
                t_lbl, t_ang, t_dist = item
            elif isinstance(item, dict):
                t_lbl = item.get("label", "TGT")
                t_ang = item.get("angle", 45)
                t_dist = item.get("distance", 50)
            else:
                continue

            t_rad = math.radians(float(t_ang) - 90.0)
            tx = cx + float(t_dist) * math.cos(t_rad)
            ty = cy + float(t_dist) * math.sin(t_rad)

            target_blips_svg.append(
                f'<g class="aleph-radar-ping">'
                f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="9" fill="none" stroke="{accent}" stroke-opacity="0.4" class="aleph-ripple-circle" />'
                f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="3" fill="oklch(0.80 0.16 160)" />'
                f'<text x="{tx + 8:.2f}" y="{ty - 4:.2f}" font-family="monospace" font-size="6.5" font-weight="600" fill="oklch(0.80 0.16 160)">{html.escape(str(t_lbl))}</text>'
                f'</g>'
            )

        badge_border = _border_color_alpha(accent)

        return f"""<div class="aleph-visual-stage aleph-radial-radar-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge" style="color:{accent}; border-color:{badge_border};">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Telemetría Polar Radial">
    <defs>
      <linearGradient id="{stage_id}_radarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.35" />
        <stop offset="100%" stop-color="{secondary}" stop-opacity="0.10" />
      </linearGradient>
      <filter id="{stage_id}_radarGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2.5" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <!-- Anillos Concéntricos de Cobertura -->
    <g class="aleph-radar-rings">
      {"".join(range_rings_svg)}
    </g>
    <!-- Radios Azimutales y Etiquetas -->
    <g class="aleph-radar-spokes">
      {"".join(spokes_svg)}
    </g>
    <!-- Polígono Multivariable de Telemetría -->
    <polygon points="{poly_str}" fill="url(#{stage_id}_radarGrad)" stroke="{accent}" stroke-width="2" stroke-linejoin="round" filter="url(#{stage_id}_radarGlow)" />
    <!-- Vértices del Polígono -->
    <g>
      {"".join(vertex_circles_svg)}
    </g>
    <!-- Haz de Barrido de Sonar Rotatorio -->
    <g class="aleph-radar-sweep-beam" style="transform-origin: {cx}px {cy}px;">
      <line x1="{cx}" y1="{cy}" x2="{cx + R}" y2="{cy}" stroke="{accent}" stroke-width="1.8" stroke-linecap="round" />
      <polygon points="{cx},{cy} {cx + R},{cy} {cx + R - 6},{cy - 24}" fill="{accent}" opacity="0.16" />
    </g>
    <!-- Contactos / Blips Detectados -->
    <g class="aleph-radar-targets">
      {"".join(target_blips_svg)}
    </g>
  </svg>
</div>"""

    # --------------------------------------------------------------------------
    # 8. GENERADOR: SPECTRAL WAVEFORM (Formas de Onda Cinéticas y Espectro FFT)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_spectral_waveform(cls, config: VisualStageConfig) -> str:
        """
        Genera un analizador de espectro de frecuencia FFT y forma de onda cinética continua,
        con calibración de decibeles (-60 dBFS a 0 dBFS), barras ecualizadoras y peak-holds.
        """
        accent = config.accent_color
        secondary = config.secondary_color
        stage_id = f"spec_{config.seed}"
        domain = cls.detect_semantic_domain(config)

        domain_defaults = {
            "haute_luxury": {
                "title": "ACOUSTIC_RESONANCE_SPECTROGRAM",
                "badge": "4 Hz // 28,800 BPH",
                "sample_rate": "RESONANCE: 99.8 dB",
                "db_range": "-48 dBFS"
            },
            "finance": {
                "title": "HIGH_FREQUENCY_ORDER_SPECTRUM",
                "badge": "NANOSECOND TICK STREAM",
                "sample_rate": "SAMPLING: 10 MHz",
                "db_range": "-18 dBFS"
            },
            "biotech_medicine": {
                "title": "CARDIOPULMONARY_SPECTRAL_WAVE",
                "badge": "ECG // 12-LEAD VECTOR",
                "sample_rate": "SAMPLING: 2000 Hz",
                "db_range": "0.05 - 150 Hz"
            },
            "swiss_editorial": {
                "title": "HARMONIC_FREQUENCY_MODULATOR",
                "badge": "GOLDEN RATIO SPECTRUM",
                "sample_rate": "PHI FREQ: 432 Hz",
                "db_range": "CANON HARMONIC"
            },
            "cyber_quantum": {
                "title": "RF_SPECTRUM_WAVEFORM_ANALYZER",
                "badge": "FFT: 1024 BINS // -112 dBm",
                "sample_rate": "192 kHz // 32-BIT FLOAT",
                "db_range": "-96 dBFS"
            }
        }
        defaults = domain_defaults.get(domain, domain_defaults["cyber_quantum"])

        title_txt = config.get_param("title", "stage_title", "card_title", default=None) or defaults["title"]
        badge_txt = config.get_param("badge_text", "stage_badge", "badge", default=None) or defaults["badge"]

        # 1. Forma de Onda Cinética Superior (Carrier Wave + Modulator)
        # Curva continua entre x=60 y x=540 con centro en y=75
        wave_carrier_d = "M 60 75 Q 120 35 180 75 T 300 75 T 420 75 T 540 75"
        wave_harmonic_d = "M 60 75 Q 90 55 120 75 T 180 75 T 240 75 T 300 75 T 360 75 T 420 75 T 480 75 T 540 75"

        # 2. Barras de Espectro FFT Inferior (28 barras entre x=60 y x=540)
        num_bars = 28
        bar_w = 12.0
        start_x = 60.0
        total_w = 480.0
        gap = (total_w - (num_bars * bar_w)) / (num_bars - 1)
        baseline_y = 220.0

        raw_freqs = config.get_param("frequencies", "spectrum_bars", default=None)
        bars_svg = []

        for i in range(num_bars):
            bx = start_x + i * (bar_w + gap)
            # Altura procedimental según curva armónica natural
            if raw_freqs and isinstance(raw_freqs, list) and i < len(raw_freqs):
                h = float(raw_freqs[i])
            else:
                norm_pos = i / (num_bars - 1)
                # Modelo de energía sonora: realce de graves, valle en medios, pico de presencia y caída
                h = 16.0 + 55.0 * math.sin(norm_pos * math.pi) * (1.0 - 0.25 * math.cos(norm_pos * 3.0 * math.pi))
                if i in (4, 11, 18, 22):
                    h += 12.0  # armónicos resonantes
            h = max(6.0, min(80.0, h))
            by = baseline_y - h

            bars_svg.append(
                f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bar_w:.2f}" height="{h:.2f}" rx="2" fill="url(#{stage_id}_barGrad)" />'
            )
            # Marcador de pico (peak hold)
            bars_svg.append(
                f'<line x1="{bx:.2f}" y1="{by - 4:.2f}" x2="{bx + bar_w:.2f}" y2="{by - 4:.2f}" stroke="{accent}" stroke-width="1.5" stroke-linecap="round" />'
            )

        badge_border = _border_color_alpha(accent)

        return f"""<div class="aleph-visual-stage aleph-spectral-waveform-stage">
  <div class="aleph-stage-hud-header">
    <div class="aleph-stage-status">
      <span class="aleph-live-dot" style="background:{accent};"></span>
      <span class="aleph-stage-status-text">{html.escape(title_txt)}</span>
    </div>
    <span class="aleph-stage-metric-badge font-mono" style="color:{accent}; border-color:{badge_border};">{html.escape(badge_txt)}</span>
  </div>
  <svg viewBox="0 0 600 260" class="aleph-stage-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Analizador de Espectro y Forma de Onda">
    <defs>
      <linearGradient id="{stage_id}_waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{secondary}" />
        <stop offset="60%" stop-color="{accent}" />
        <stop offset="100%" stop-color="oklch(1 0 0)" />
      </linearGradient>
      <linearGradient id="{stage_id}_barGrad" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0%" stop-color="{secondary}" stop-opacity="0.3" />
        <stop offset="65%" stop-color="{accent}" stop-opacity="0.75" />
        <stop offset="100%" stop-color="oklch(1 0 0)" stop-opacity="0.9" />
      </linearGradient>
      <filter id="{stage_id}_waveGlow" x="-10%" y="-30%" width="120%" height="160%">
        <feGaussianBlur stdDeviation="2.5" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <!-- Calibración y Escala de Decibeles -->
    <g opacity="0.12" stroke="oklch(1 0 0)" stroke-dasharray="2 4">
      <line x1="50" y1="45" x2="550" y2="45" />
      <line x1="50" y1="75" x2="550" y2="75" />
      <line x1="50" y1="105" x2="550" y2="105" />
      <line x1="50" y1="{baseline_y}" x2="550" y2="{baseline_y}" />
    </g>
    <!-- Etiquetas de dB -->
    <g font-family="monospace" font-size="7" fill="oklch(1 0 0 / 0.4)" text-anchor="end">
      <text x="45" y="48">+6 dB</text>
      <text x="45" y="78">0 dB</text>
      <text x="45" y="108">-18 dB</text>
      <text x="45" y="{baseline_y + 3}">-60 dB</text>
    </g>
    <!-- Forma de Onda Cinética Superior (Dual Harmonic) -->
    <path d="{wave_harmonic_d}" fill="none" stroke="{secondary}" stroke-width="1.2" stroke-opacity="0.45" />
    <path d="{wave_carrier_d}" fill="none" stroke="url(#{stage_id}_waveGrad)" stroke-width="2.2" stroke-linecap="round" filter="url(#{stage_id}_waveGlow)" />
    <!-- Cursor de Muestreo Activo Temporal -->
    <g transform="translate(375, 40)">
      <line x1="0" y1="0" x2="0" y2="65" stroke="{accent}" stroke-width="1" stroke-dasharray="2 2" />
      <circle cx="0" cy="35" r="4" fill="{accent}" />
      <circle cx="0" cy="35" r="1.5" fill="oklch(1 0 0)" />
      <rect x="6" y="24" width="48" height="18" rx="4" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.9))" stroke="{accent}" stroke-width="0.8" />
      <text x="30" y="36" font-family="monospace" font-size="7.5" font-weight="700" fill="oklch(1 0 0)" text-anchor="middle">PEAK</text>
    </g>
    <!-- Barras del Analizador de Espectro FFT -->
    <g class="aleph-spectrum-bars">
      {"".join(bars_svg)}
    </g>
    <!-- Calibración de Frecuencias de Eje X -->
    <g font-family="monospace" font-size="7" fill="oklch(1 0 0 / 0.45)">
      <text x="60" y="235">32 Hz</text>
      <text x="140" y="235">125 Hz</text>
      <text x="240" y="235">500 Hz</text>
      <text x="350" y="235">2 kHz</text>
      <text x="450" y="235">8 kHz</text>
      <text x="525" y="235">16 kHz</text>
    </g>
  </svg>
</div>"""

    # ==========================================================================
    # RENDERIZADOR GENERAL UNIFICADO (HTML5 Y CSS)
    # ==========================================================================
    @classmethod
    def render_stage_html(
        cls,
        stage_type: Union[VisualStageType, str],
        config: Optional[VisualStageConfig] = None,
        palette: Optional[Dict[str, str]] = None,
        props: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Punto de entrada maestro para renderizar cualquier escenario visual en HTML5.
        Soporta configuración paramétrica completa y hereda paletas de diseño.
        """
        if isinstance(stage_type, VisualStageConfig):
            config = stage_type
            stage_type = config.stage_type
        elif isinstance(stage_type, str):
            st_lower = stage_type.lower()
            if st_lower in ("topology_graph", "topology", "dag", "gear_train"):
                stage_type = VisualStageType.TOPOLOGY_GRAPH
            elif st_lower in ("quantum_network", "quantum", "network", "qnet"):
                stage_type = VisualStageType.QUANTUM_NETWORK
            elif st_lower in ("code_terminal", "terminal", "code"):
                stage_type = VisualStageType.CODE_TERMINAL
            elif st_lower in ("cryo_gauge", "gauge", "tachometer", "dial"):
                stage_type = VisualStageType.CRYO_GAUGE
            elif st_lower in ("radial_radar", "radar_telemetry", "radar", "sonar"):
                stage_type = VisualStageType.RADIAL_RADAR
            elif st_lower in ("spectral_waveform", "waveform", "spectral", "spectrum"):
                stage_type = VisualStageType.SPECTRAL_WAVEFORM
            elif st_lower in ("bezier_chart", "bezier", "chart"):
                stage_type = VisualStageType.BEZIER_CHART
            elif st_lower in ("swiss_geometry", "swiss", "geometry"):
                stage_type = VisualStageType.SWISS_GEOMETRY
            else:
                try:
                    stage_type = VisualStageType(st_lower)
                except ValueError:
                    stage_type = VisualStageType.TOPOLOGY_GRAPH

        cfg = config or VisualStageConfig(stage_type=stage_type)
        if props:
            cfg.props.update(props)

        if palette:
            if "primary" in palette:
                cfg.accent_color = palette["primary"]
            if "secondary" in palette:
                cfg.secondary_color = palette["secondary"]

        if stage_type == VisualStageType.CRYO_GAUGE:
            return cls.generate_cryo_gauge(cfg)
        elif stage_type == VisualStageType.CODE_TERMINAL:
            return cls.generate_code_terminal(cfg)
        elif stage_type == VisualStageType.SWISS_GEOMETRY:
            return cls.generate_swiss_geometry(cfg)
        elif stage_type == VisualStageType.BEZIER_CHART:
            return cls.generate_bezier_chart(cfg)
        elif stage_type == VisualStageType.TOPOLOGY_GRAPH:
            return cls.generate_topology_graph(cfg)
        elif stage_type == VisualStageType.QUANTUM_NETWORK:
            return cls.generate_quantum_network(cfg)
        elif stage_type in (VisualStageType.RADIAL_RADAR, VisualStageType.RADAR_TELEMETRY):
            return cls.generate_radial_radar(cfg)
        elif stage_type == VisualStageType.SPECTRAL_WAVEFORM:
            return cls.generate_spectral_waveform(cfg)
        return cls.generate_topology_graph(cfg)

    render_stage_svg = render_stage_html

    @classmethod
    def get_stage_css(cls) -> str:
        """
        Devuelve las reglas CSS completas y optimizadas para escenografías visuales.
        Totalmente compatible con @layer components y respetuoso de prefers-reduced-motion.
        Cumple 100% con la Invariante Anti-Slop (0 hex, 0 rgba, 0 transition-all).
        """
        return """
  /* ==========================================================================
     ALEPH VISUAL STAGE SYNTHESIZER — PROCEDURAL GRAPHICS & MICRO-UI
     ========================================================================== */
  .aleph-visual-stage {
    position: relative;
    width: 100%;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    border-radius: 14px;
    background: oklch(0.08 0.02 240 / 0.45);
    border: 1px solid oklch(1 0 0 / 0.07);
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: border-color 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .aleph-card:hover .aleph-visual-stage,
  .aleph-bento-card:hover .aleph-visual-stage {
    border-color: oklch(0.85 0.18 200 / 0.25);
    box-shadow: inset 0 0 20px -5px oklch(0.85 0.18 200 / 0.08);
  }
  .aleph-stage-hud-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 14px;
    border-bottom: 1px solid oklch(1 0 0 / 0.06);
    background: oklch(1 0 0 / 0.02);
  }
  .aleph-stage-status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .aleph-live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: oklch(0.85 0.18 200);
    box-shadow: 0 0 8px oklch(0.85 0.18 200);
    animation: alephLivePulse 2s ease-in-out infinite;
  }
  .aleph-stage-status-text {
    font-family: var(--font-mono, monospace);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: oklch(1 0 0 / 0.85);
    text-transform: uppercase;
  }
  .aleph-stage-metric-badge {
    font-family: var(--font-mono, monospace);
    font-size: 0.625rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 2px 7px;
    border-radius: 9999px;
    border: 1px solid oklch(0.85 0.18 200 / 0.25);
    background: oklch(0.85 0.18 200 / 0.06);
    color: oklch(0.82 0.12 205);
  }
  .aleph-stage-svg {
    display: block;
    width: 100%;
    height: auto;
    max-height: 220px;
    shape-rendering: geometricPrecision;
    text-rendering: geometricPrecision;
  }

  /* Animación de Pulsos en Aristas de Grafo y Flujos */
  @keyframes alephPulseFlow {
    0% {
      stroke-dashoffset: 0;
    }
    100% {
      stroke-dashoffset: -156;
    }
  }
  .aleph-pulse-line {
    animation: alephPulseFlow 3.5s linear infinite;
  }

  /* Ondas Concéntricas / Ripple de Nodos */
  @keyframes alephRipple {
    0% {
      transform: scale(0.9);
      opacity: 0.8;
    }
    50% {
      transform: scale(1.15);
      opacity: 0.2;
    }
    100% {
      transform: scale(0.9);
      opacity: 0.8;
    }
  }
  .aleph-ripple-circle {
    transform-origin: center;
    animation: alephRipple 3s ease-in-out infinite;
  }

  /* Barrido Rotatorio de Radar */
  @keyframes alephRadarRotate {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  .aleph-radar-sweep-beam {
    animation: alephRadarRotate 4s linear infinite;
  }

  /* Pulso del Indicador Live */
  @keyframes alephLivePulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
  }

  /* Mini-Terminal de Código */
  .aleph-code-terminal-stage {
    font-size: 0.75rem;
  }
  .aleph-terminal-chrome {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: oklch(1 0 0 / 0.03);
    border-bottom: 1px solid oklch(1 0 0 / 0.08);
  }
  .aleph-terminal-lights {
    display: flex;
    gap: 6px;
  }
  .aleph-terminal-lights .light {
    width: 9px;
    height: 9px;
    border-radius: 50%;
  }
  .aleph-terminal-lights .close { background: oklch(0.68 0.22 25); }
  .aleph-terminal-lights .min { background: oklch(0.82 0.18 75); }
  .aleph-terminal-lights .max { background: oklch(0.72 0.20 145); }
  .aleph-terminal-title {
    font-size: 0.6875rem;
    color: oklch(1 0 0 / 0.6);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .aleph-terminal-meta {
    display: flex;
    gap: 6px;
    align-items: center;
  }
  .aleph-terminal-badge {
    font-size: 0.625rem;
    padding: 1px 6px;
    border-radius: 4px;
    border: 1px solid oklch(1 0 0 / 0.1);
  }
  .aleph-terminal-badge.live {
    background: oklch(0.72 0.19 155 / 0.1);
    color: oklch(0.80 0.16 160);
    border-color: oklch(0.72 0.19 155 / 0.25);
  }
  .aleph-terminal-badge.latency {
    color: oklch(1 0 0 / 0.65);
  }
  .aleph-terminal-body {
    padding: 12px 14px;
    line-height: 1.6;
    color: oklch(0.92 0.01 240);
  }
  .aleph-terminal-line {
    display: flex;
    gap: 12px;
  }
  .aleph-line-number {
    color: oklch(1 0 0 / 0.25);
    user-select: none;
    min-width: 18px;
    text-align: right;
  }
  .aleph-line-code {
    white-space: pre-wrap;
    word-break: break-all;
  }
  .aleph-line-code .tok-kw { color: oklch(0.62 0.24 15); font-weight: 600; }
  .aleph-line-code .tok-mod { color: oklch(0.75 0.14 220); }
  .aleph-line-code .tok-cls { color: oklch(0.80 0.18 80); }
  .aleph-line-code .tok-func { color: oklch(0.72 0.18 285); }
  .aleph-line-code .tok-var { color: oklch(0.92 0.01 240); }
  .aleph-line-code .tok-str { color: oklch(0.80 0.16 160); }
  .aleph-line-code .tok-num { color: oklch(0.68 0.22 45); }
  .aleph-line-code .tok-const { color: oklch(0.75 0.14 220); font-weight: 700; }
  .aleph-line-code .tok-cm { color: oklch(1 0 0 / 0.35); font-style: italic; }
  .aleph-terminal-cursor {
    color: oklch(0.85 0.18 200);
    animation: alephCursorBlink 1s step-end infinite;
  }
  @keyframes alephCursorBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }
  .aleph-terminal-footer {
    display: flex;
    justify-content: space-between;
    padding: 6px 12px;
    font-size: 0.625rem;
    color: oklch(1 0 0 / 0.4);
    border-top: 1px solid oklch(1 0 0 / 0.05);
    background: oklch(0 0 0 / 0.2);
  }

  /* Accesibilidad y Reducción de Movimiento */
  @media (prefers-reduced-motion: reduce) {
    .aleph-pulse-line,
    .aleph-ripple-circle,
    .aleph-radar-sweep-beam,
    .aleph-live-dot,
    .aleph-terminal-cursor {
      animation: none !important;
    }
  }
"""

    # ==========================================================================
    # GENERADOR DE CÓDIGO TSX MODULAR PARA REACT 19 (8 COMPONENTES)
    # ==========================================================================
    @classmethod
    def generate_all_react_components(cls) -> Dict[str, str]:
        """
        Genera el conjunto completo de componentes React 19 TSX para la suite de
        8 escenografías visuales internas canónicas listas para BentoGrid y paneles.
        """
        files: Dict[str, str] = {}

        # 1. CryoGaugeStage.tsx
        files["components/visuals/CryoGaugeStage.tsx"] = """import React from "react";

export interface CryoGaugeStageProps {
  className?: string;
  title?: string;
  value?: string;
  unit?: string;
  metricValue?: string;
  metricUnit?: string;
  dialLabel?: string;
  fillPercentage?: number;
}

export function CryoGaugeStage({
  className = "",
  title = "TELEMETRY_GAUGE",
  value,
  unit,
  metricValue,
  metricUnit,
  dialLabel = "STATUS: OPTIMAL",
  fillPercentage = 0.78,
}: CryoGaugeStageProps) {
  const displayVal = metricValue || value || "99.9";
  const displayUnit = metricUnit || unit || "%";
  const pct = fillPercentage > 1 ? fillPercentage / 100 : fillPercentage;
  const activeOffset = 377 - 377 * pct;

  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-primary/30 text-primary bg-primary/10">
          TELEMETRY ACTIVE
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <circle cx="300" cy="120" r="80" fill="none" stroke="oklch(1 0 0 / 0.08)" strokeWidth="8" strokeDasharray="377" strokeDashoffset="94" transform="rotate(135 300 120)" strokeLinecap="round" />
        <circle cx="300" cy="120" r="80" fill="none" stroke="var(--color-primary, currentColor)" strokeWidth="8" strokeDasharray="377" strokeDashoffset={activeOffset} transform="rotate(135 300 120)" strokeLinecap="round" />
        <g textAnchor="middle" className="font-mono">
          <text x="300" y="125" fontSize="28" fontWeight="700" fill="oklch(1 0 0)">{displayVal}</text>
          <text x="300" y="145" fontSize="11" fontWeight="600" fill="var(--color-primary, currentColor)">{displayUnit}</text>
          <text x="300" y="165" fontSize="8" fill="oklch(1 0 0 / 0.4)">{dialLabel}</text>
        </g>
      </svg>
    </div>
  );
}
export default CryoGaugeStage;
"""

        # 2. CodeTerminalStage.tsx
        files["components/visuals/CodeTerminalStage.tsx"] = """import React from "react";

export interface CodeTerminalStageProps {
  className?: string;
  title?: string;
  statusBadge?: string;
  fileName?: string;
  codeLines?: string[];
}

export function CodeTerminalStage({
  className = "",
  title,
  statusBadge = "● PROVING [UNSAT]",
  fileName = "aleph_smt_prover.py — Z3 Engine",
  codeLines,
}: CodeTerminalStageProps) {
  const displayTitle = title || fileName;
  const lines = codeLines || [
    'from aleph.z3 import Solver, Int',
    '# Formal Verification Proof',
    'solver = Solver(theory="QF_NRA")',
    'solver.add(vw >= 320, overflow_px == 0.0)',
    'assert solver.check() == UNSAT ▋'
  ];

  return (
    <div className={`relative w-full rounded-xl bg-surface/60 border border-border/20 overflow-hidden font-mono text-xs ${className}`}>
      <div className="flex items-center justify-between px-3 py-2 bg-surface/30 border-b border-border/20">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
        </div>
        <span className="text-[11px] text-foreground/60 truncate max-w-[200px]">{displayTitle}</span>
        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
          {statusBadge}
        </span>
      </div>
      <div className="p-3.5 space-y-1 text-foreground/90">
        {lines.map((line, idx) => (
          <div key={idx} className="flex gap-3">
            <span className="text-foreground/30 select-none">{(idx + 1).toString().padStart(2, "0")}</span>
            <span>{line}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between px-3 py-1.5 bg-surface/40 border-t border-border/10 text-[10px] text-foreground/40">
        <span>⎇ main (clean)</span>
        <span>STATUS: NOMINAL</span>
      </div>
    </div>
  );
}
export default CodeTerminalStage;
"""

        # 3. SwissGeometryStage.tsx
        files["components/visuals/SwissGeometryStage.tsx"] = """import React from "react";

export interface SwissGeometryStageProps {
  className?: string;
  title?: string;
  coordinatesText?: string;
  figureLabel?: string;
  ratioLabel?: string;
}

export function SwissGeometryStage({
  className = "",
  title = "GOLDEN_SECTION // § 1.618",
  coordinatesText = "COORD: 47°22'N 8°32'E // ZÜRICH",
  figureLabel = "FIG. 04 — MODULAR HARMONY",
  ratioLabel = "RATIO: 1 : 1.6180339887",
}: SwissGeometryStageProps) {
  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden font-mono ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <span className="text-[11px] font-semibold uppercase text-foreground/80">{title}</span>
        <span className="text-[10px] px-2 py-0.5 rounded border border-border/30 text-foreground/70">SWISS CANON</span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <rect x="50" y="25" width="310" height="190" fill="none" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
        <rect x="360" y="25" width="190" height="190" fill="none" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
        <rect x="360" y="140" width="118" height="75" fill="none" stroke="var(--color-primary, currentColor)" strokeWidth="1" strokeOpacity="0.7" />
        <path d="M 360 215 A 310 190 0 0 1 50 25" fill="none" stroke="var(--color-primary, currentColor)" strokeWidth="1.5" strokeDasharray="3 3" />
        <g stroke="oklch(1 0 0 / 0.4)" strokeWidth="1">
          <path d="M 46 25 L 54 25 M 50 21 L 50 29" />
          <path d="M 546 25 L 554 25 M 550 21 L 550 29" />
        </g>
        <g fontSize="8" fill="oklch(1 0 0 / 0.5)">
          <text x="65" y="50">{figureLabel}</text>
          <text x="65" y="65">{coordinatesText}</text>
          <text x="65" y="200" fill="var(--color-primary, currentColor)">{ratioLabel}</text>
        </g>
      </svg>
    </div>
  );
}
export default SwissGeometryStage;
"""

        # 4. BezierTelemetryStage.tsx
        files["components/visuals/BezierTelemetryStage.tsx"] = """import React from "react";

export interface BezierTelemetryStageProps {
  className?: string;
  title?: string;
  badge?: string;
  metric?: string;
  dataPoints?: number[];
  peakLabel?: string;
}

export function BezierTelemetryStage({
  className = "",
  title = "THROUGHPUT_SPECTROGRAM",
  badge = "+42.6% OPTIMAL",
  metric,
  peakLabel = "1.84M req/s",
}: BezierTelemetryStageProps) {
  const displayPeak = metric || peakLabel;
  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-emerald-500/30 text-emerald-400 bg-emerald-500/10 font-semibold">
          {badge}
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="bezier_area" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-primary, currentColor)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--color-primary, currentColor)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <g opacity="0.12" stroke="oklch(1 0 0)" strokeDasharray="2 4">
          <line x1="60" y1="50" x2="540" y2="50" />
          <line x1="60" y1="110" x2="540" y2="110" />
          <line x1="60" y1="170" x2="540" y2="170" />
        </g>
        <path d="M 60 170 C 140 160, 200 110, 280 120 C 360 130, 420 70, 540 60 L 540 190 L 60 190 Z" fill="url(#bezier_area)" />
        <path d="M 60 170 C 140 160, 200 110, 280 120 C 360 130, 420 70, 540 60" fill="none" stroke="var(--color-primary, currentColor)" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="540" cy="60" r="12" fill="none" stroke="var(--color-primary, currentColor)" strokeOpacity="0.4" />
        <circle cx="540" cy="60" r="5" fill="var(--color-primary, currentColor)" />
        <g transform="translate(450, 25)">
          <rect width="84" height="24" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.9))" stroke="var(--color-primary, currentColor)" strokeWidth="1" />
          <text x="42" y="15" fontFamily="monospace" fontSize="10" fontWeight="700" fill="oklch(1 0 0)" textAnchor="middle">{displayPeak}</text>
        </g>
      </svg>
    </div>
  );
}
export default BezierTelemetryStage;
"""

        # 5. TopologyGraphStage.tsx
        files["components/visuals/TopologyGraphStage.tsx"] = """import React from "react";

export interface TopologyGraphStageProps {
  className?: string;
  title?: string;
  badge?: string;
  hubLabel?: string;
  nodeLabels?: string[];
}

export function TopologyGraphStage({
  className = "",
  title = "DEPENDENCY_DIRECTED_GRAPH",
  badge = "DAG // ZERO_CYCLE",
  hubLabel = "SSA.KERNEL",
  nodeLabels = ["AST.INGEST", "CFG.BUILD", "Z3.SOLVER", "BINARY.EMIT", "VERIFY.OK", "CODEGEN"],
}: TopologyGraphStageProps) {
  const n = [...nodeLabels, "N1", "N2", "N3", "N4", "N5"];

  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-primary/30 text-primary bg-primary/10">
          {badge}
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <defs>
          <marker id="topo_arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--color-primary, currentColor)" />
          </marker>
        </defs>
        <g stroke="oklch(1 0 0 / 0.15)" strokeWidth="1.5" fill="none" markerEnd="url(#topo_arrow)">
          <path d="M 115 120 C 130 120, 130 65, 145 65" />
          <path d="M 115 120 C 130 120, 130 175, 145 175" />
          <path d="M 235 65 C 250 65, 250 120, 265 120" />
          <path d="M 235 175 C 250 175, 250 120, 265 120" />
          <path d="M 360 120 C 372 120, 372 65, 385 65" />
          <path d="M 360 120 C 372 120, 372 175, 385 175" />
          <path d="M 475 65 C 488 65, 488 120, 500 120" />
          <path d="M 475 175 C 488 175, 488 120, 500 120" />
        </g>
        <g>
          <rect x="30" y="102" width="85" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="72" y="124" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[0]}</text>
          <rect x="145" y="47" width="90" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="190" y="69" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[1]}</text>
          <rect x="145" y="157" width="90" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="190" y="179" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[2]}</text>
          <rect x="265" y="100" width="95" height="40" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="var(--color-primary, currentColor)" strokeWidth="1.5" />
          <text x="312" y="124" textAnchor="middle" fontFamily="monospace" fontSize="9" fontWeight="700" fill="var(--color-primary, currentColor)">{hubLabel}</text>
          <rect x="385" y="47" width="90" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="430" y="69" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[3]}</text>
          <rect x="385" y="157" width="90" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="430" y="179" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[4]}</text>
          <rect x="500" y="102" width="85" height="36" rx="6" fill="var(--color-surface, oklch(0.12 0.02 240 / 0.85))" stroke="oklch(1 0 0 / 0.2)" strokeWidth="1" />
          <text x="542" y="124" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[5]}</text>
        </g>
      </svg>
    </div>
  );
}
export default TopologyGraphStage;
"""

        # 6. QuantumNetworkStage.tsx
        files["components/visuals/QuantumNetworkStage.tsx"] = """import React from "react";

export interface QuantumNetworkStageProps {
  className?: string;
  title?: string;
  fidelity?: string;
  accentColor?: string;
  hubLabel?: string;
  nodeLabels?: string[];
}

export function QuantumNetworkStage({
  className = "",
  title = "TOPOLOGICAL_ENTANGLEMENT",
  fidelity = "99.982%",
  accentColor = "var(--color-primary, currentColor)",
  hubLabel = "0x7F-CORE",
  nodeLabels = ["Q-NODE.01", "Q-NODE.02", "Q-NODE.03", "Q-NODE.04", "GATE.A", "GATE.B"],
}: QuantumNetworkStageProps) {
  const n = [...nodeLabels, "N.1", "N.2", "N.3", "N.4", "N.5", "N.6"];
  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden backdrop-blur-md ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold tracking-wider uppercase text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-primary/30 bg-primary/10 text-primary">
          {fidelity}
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="qnet_pulse" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={accentColor} stopOpacity="0" />
            <stop offset="50%" stopColor={accentColor} stopOpacity="1" />
            <stop offset="100%" stopColor="oklch(1 0 0)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <g opacity="0.12" stroke="oklch(1 0 0)" strokeDasharray="2 6">
          <line x1="40" y1="120" x2="560" y2="120" />
          <line x1="300" y1="20" x2="300" y2="220" />
          <ellipse cx="300" cy="120" rx="110" ry="50" fill="none" transform="rotate(-20 300 120)" />
          <ellipse cx="300" cy="120" rx="180" ry="80" fill="none" transform="rotate(15 300 120)" />
        </g>
        <g strokeLinecap="round" fill="none">
          <path d="M 300 120 Q 210 70 140 60" stroke="oklch(1 0 0 / 0.1)" strokeWidth="1.5" />
          <path d="M 300 120 Q 190 160 110 180" stroke="oklch(1 0 0 / 0.1)" strokeWidth="1.5" />
          <path d="M 300 120 Q 390 75 460 65" stroke="oklch(1 0 0 / 0.1)" strokeWidth="1.5" />
          <path d="M 300 120 Q 410 160 490 175" stroke="oklch(1 0 0 / 0.1)" strokeWidth="1.5" />
          <path d="M 300 120 Q 210 70 140 60" stroke="url(#qnet_pulse)" strokeWidth="2.5" strokeDasharray="16 140" />
          <path d="M 300 120 Q 390 75 460 65" stroke="url(#qnet_pulse)" strokeWidth="2.5" strokeDasharray="16 140" />
        </g>
        <g>
          <circle cx="300" cy="120" r="22" fill="none" stroke={accentColor} strokeOpacity="0.25" />
          <circle cx="300" cy="120" r="9" fill={accentColor} />
          <circle cx="300" cy="120" r="3" fill="oklch(1 0 0)" />
          <text x="300" y="105" textAnchor="middle" fontFamily="monospace" fontSize="9" fill={accentColor}>{hubLabel}</text>
          <circle cx="140" cy="60" r="6" fill="var(--color-accent, currentColor)" />
          <text x="140" y="75" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[0]}</text>
          <circle cx="460" cy="65" r="6" fill="var(--color-accent, currentColor)" />
          <text x="460" y="80" textAnchor="middle" fontFamily="monospace" fontSize="8" fill="oklch(1 0 0)">{n[2]}</text>
          <circle cx="110" cy="180" r="5" fill="var(--color-accent, currentColor)" />
          <circle cx="490" cy="175" r="5" fill="var(--color-accent, currentColor)" />
        </g>
      </svg>
    </div>
  );
}
export default QuantumNetworkStage;
"""

        # 7. RadialRadarStage.tsx
        files["components/visuals/RadialRadarStage.tsx"] = """import React from "react";

export interface RadialRadarStageProps {
  className?: string;
  title?: string;
  badge?: string;
  axes?: string[];
  values?: number[];
}

export function RadialRadarStage({
  className = "",
  title = "POLAR_TELEMETRY_RADAR",
  badge = "SONAR // 8-BAND",
  axes = ["LATENCY", "THROUGHPUT", "MEMORY", "Z3_PROOF", "CONCURRENCY", "ISOLATION"],
  values = [0.92, 0.88, 0.78, 0.96, 0.85, 0.90],
}: RadialRadarStageProps) {
  const cx = 300;
  const cy = 120;
  const R = 85;
  const numSpokes = axes.length;

  const points = values.map((val, idx) => {
    const rad = (-90 + (idx / numSpokes) * 360) * (Math.PI / 180);
    const vx = cx + R * val * Math.cos(rad);
    const vy = cy + R * val * Math.sin(rad);
    return `${vx.toFixed(1)},${vy.toFixed(1)}`;
  }).join(" ");

  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-primary/30 text-primary bg-primary/10">
          {badge}
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <circle cx={cx} cy={cy} r={R * 0.33} fill="none" stroke="oklch(1 0 0 / 0.12)" strokeDasharray="2 4" />
        <circle cx={cx} cy={cy} r={R * 0.66} fill="none" stroke="oklch(1 0 0 / 0.12)" strokeDasharray="2 4" />
        <circle cx={cx} cy={cy} r={R} fill="none" stroke="oklch(1 0 0 / 0.16)" />
        {axes.map((ax, idx) => {
          const rad = (-90 + (idx / numSpokes) * 360) * (Math.PI / 180);
          const lx = cx + R * Math.cos(rad);
          const ly = cy + R * Math.sin(rad);
          const tx = cx + (R + 12) * Math.cos(rad);
          const ty = cy + (R + 12) * Math.sin(rad);
          return (
            <g key={idx}>
              <line x1={cx} y1={cy} x2={lx} y2={ly} stroke="oklch(1 0 0 / 0.15)" />
              <text x={tx} y={ty + 3} textAnchor="middle" fontFamily="monospace" fontSize="7" fill="oklch(1 0 0 / 0.6)">{ax}</text>
            </g>
          );
        })}
        <polygon points={points} fill="var(--color-primary, currentColor)" fillOpacity="0.25" stroke="var(--color-primary, currentColor)" strokeWidth="2" strokeLinejoin="round" />
        <line x1={cx} y1={cy} x2={cx + R} y2={cy} stroke="var(--color-primary, currentColor)" strokeWidth="1.5" />
      </svg>
    </div>
  );
}
export default RadialRadarStage;
"""

        # 8. SpectralWaveformStage.tsx
        files["components/visuals/SpectralWaveformStage.tsx"] = """import React from "react";

export interface SpectralWaveformStageProps {
  className?: string;
  title?: string;
  badge?: string;
}

export function SpectralWaveformStage({
  className = "",
  title = "RF_SPECTRUM_WAVEFORM_ANALYZER",
  badge = "FFT: 1024 BINS // -112 dBm",
}: SpectralWaveformStageProps) {
  const bars = [18, 25, 34, 48, 62, 54, 42, 38, 52, 68, 74, 58, 44, 36, 48, 64, 56, 42, 32, 28, 36, 44, 38, 26];

  return (
    <div className={`relative w-full rounded-xl bg-surface/40 border border-border/20 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border/20 bg-surface/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-foreground/80">{title}</span>
        </div>
        <span className="font-mono text-[10px] px-2 py-0.5 rounded-full border border-primary/30 text-primary bg-primary/10">
          {badge}
        </span>
      </div>
      <svg viewBox="0 0 600 240" className="w-full h-auto max-h-[220px]" preserveAspectRatio="xMidYMid meet">
        <g opacity="0.12" stroke="oklch(1 0 0)" strokeDasharray="2 4">
          <line x1="60" y1="40" x2="540" y2="40" />
          <line x1="60" y1="70" x2="540" y2="70" />
          <line x1="60" y1="100" x2="540" y2="100" />
          <line x1="60" y1="200" x2="540" y2="200" />
        </g>
        <path d="M 60 70 Q 120 30 180 70 T 300 70 T 420 70 T 540 70" fill="none" stroke="var(--color-primary, currentColor)" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M 60 70 Q 90 50 120 70 T 180 70 T 240 70 T 300 70 T 360 70 T 420 70 T 480 70 T 540 70" fill="none" stroke="var(--color-accent, currentColor)" strokeWidth="1.2" strokeOpacity="0.4" />
        <g>
          {bars.map((h, i) => {
            const bx = 65 + i * 20;
            const by = 200 - h;
            return (
              <g key={i}>
                <rect x={bx} y={by} width={12} height={h} rx={2} fill="var(--color-primary, currentColor)" fillOpacity="0.75" />
                <line x1={bx} y1={by - 3} x2={bx + 12} y2={by - 3} stroke="var(--color-primary, currentColor)" strokeWidth="1.5" />
              </g>
            );
          })}
        </g>
        <g fontFamily="monospace" fontSize="7" fill="oklch(1 0 0 / 0.45)">
          <text x="65" y="215">32 Hz</text>
          <text x="180" y="215">250 Hz</text>
          <text x="300" y="215">1 kHz</text>
          <text x="420" y="215">4 kHz</text>
          <text x="520" y="215">16 kHz</text>
        </g>
      </svg>
    </div>
  );
}
export default SpectralWaveformStage;
"""

        return files
