"""
.aleph/lib/aleph_direction_engine.py
Direction Engine & Catalog of 12 Human Aesthetic Paradigms.
Estándar: Aleph Sovereign Design Engine / DFII & Anti-Slop Architecture.

Gobernanza de intenciones estéticas, cálculo del índice DFII,
selección determinista de arquetipos y motor de eliminación de copy genérico de IA.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class AestheticParadigm(str, Enum):
    SWISS_INTERNATIONAL = "swiss_international"
    LITERARY_EDITORIAL = "literary_editorial"
    INDUSTRIAL_BRUTALIST = "industrial_brutalist"
    HAUTE_LUXURY = "haute_luxury"
    CINEMATIC_WEBGL = "cinematic_webgl"
    BENTO_HYPERGRID = "bento_hypergrid"
    NEO_BRUTALIST = "neo_brutalist"
    ORGANIC_TACTILE = "organic_tactile"
    CYBER_TELEMETRY = "cyber_telemetry"
    RETRO_FUTURIST = "retro_futurist"
    DOCUMENT_MINIMALIST = "document_minimalist"
    DECONSTRUCTIVIST = "deconstructivist"


@dataclass
class ParadigmSpec:
    paradigm: AestheticParadigm
    name_display: str
    thesis: str
    typography_display: List[str]
    typography_body: List[str]
    color_strategy: str
    banned_defaults: List[str]
    signature_micro_details: List[str]
    recommended_archetypes: List[str]


@dataclass
class DFIIScore:
    """Design Feasibility & Impact Index (DFII). Rango objetivo: 10 a 15."""
    impact: int        # 1 a 5
    fit: int           # 1 a 5
    feasibility: int   # 1 a 5
    performance: int   # 1 a 5
    consistency_risk: int  # 1 a 5

    @property
    def total(self) -> int:
        return (self.impact + self.fit + self.feasibility + self.performance) - self.consistency_risk

    @property
    def is_acceptable(self) -> bool:
        return self.total >= 8

    @property
    def is_supreme(self) -> bool:
        return self.total >= 12


@dataclass
class CopyAuditResult:
    is_clean: bool
    banned_cliches_detected: List[str]
    authenticity_score: float  # 0.0 a 1.0
    recommendations: List[str]


# 25 Clichés Lingüísticos Universales de IA ("AI Marketing Slop")
AI_COPY_CLICHES = [
    r"\bsupercharge\b",
    r"\bunleash\b",
    r"\bseamlessly\b",
    r"\bnext-gen\b",
    r"\bnext generation\b",
    r"\bempower\b",
    r"\belevate your\b",
    r"\bgame-changer\b",
    r"\brevolutionize\b",
    r"\btailored to your needs\b",
    r"\bharness the power\b",
    r"\bcutting-edge\b",
    r"\bunlock the potential\b",
    r"\binnovative solution\b",
    r"\ball-in-one platform\b",
    r"\bdelve into\b",
    r"\bstreamline your\b",
    r"\btransform the way\b",
    r"\beffortlessly\b",
    r"\bfoster collaboration\b",
    r"\bpave the way\b",
    r"\ba testament to\b",
    r"\bin today's fast-paced\b",
    r"\blook no further\b",
    r"\bthe ultimate tool\b"
]


class DirectionEngine:
    """
    Motor soberano de dirección estética, gobernanza de paradigmas y auditoría de slop.
    """

    def __init__(self):
        self._paradigm_catalog: Dict[AestheticParadigm, ParadigmSpec] = self._build_catalog()

    def _build_catalog(self) -> Dict[AestheticParadigm, ParadigmSpec]:
        return {
            AestheticParadigm.SWISS_INTERNATIONAL: ParadigmSpec(
                paradigm=AestheticParadigm.SWISS_INTERNATIONAL,
                name_display="Estilo Tipográfico Internacional (Suizo)",
                thesis="Racionalismo matemático, eliminación del ornamento, orden objetivo.",
                typography_display=["General Sans", "Cabinet Grotesk"],
                typography_body=["General Sans", "Helvetica Neue (OFL alternative)"],
                color_strategy="Monocromo estricto con un único acento funcional de alta señal (Rojo Internacional).",
                banned_defaults=["Gradientes lineales violeta", "Bordes redondeados grandes", "Lucide icons en cajas"],
                signature_micro_details=["Divisores 1px matemáticos", "Numeración 01/ 02/", "Alineación izquierda con bandera derecha desigual"],
                recommended_archetypes=["editorial_split", "cinematic_wide_stage"]
            ),
            AestheticParadigm.LITERARY_EDITORIAL: ParadigmSpec(
                paradigm=AestheticParadigm.LITERARY_EDITORIAL,
                name_display="Editorial y Periodismo Literario",
                thesis="Calidez de la imprenta tradicional, dignidad intelectual y placer de la lectura prolongada.",
                typography_display=["Instrument Serif", "Fraunces", "Newsreader"],
                typography_body=["Newsreader", "Charis SIL"],
                color_strategy="Fondos tono pergamino/marfil con tinta carbón suave y acento verde biblioteca.",
                banned_defaults=["Modo oscuro con grano artificial", "Botones con sombras duras", "Tarjetas bento de tecnología"],
                signature_micro_details=["Capitulares monumentales (Drop caps)", "Notas al pie en popovers anclados", "Puntuación colgada"],
                recommended_archetypes=["editorial_split", "dense_data_monolith"]
            ),
            AestheticParadigm.INDUSTRIAL_BRUTALIST: ParadigmSpec(
                paradigm=AestheticParadigm.INDUSTRIAL_BRUTALIST,
                name_display="Brutalismo Industrial Utilitario (Braun / Teenage Engineering)",
                thesis="La forma sigue a la función de manera radical. El objeto como herramienta de precisión.",
                typography_display=["JetBrains Mono", "Space Mono"],
                typography_body=["Geist Mono", "JetBrains Mono"],
                color_strategy="Gris anodizado, negro mate antirreflectante con acento amarillo maquinaria o naranja industrial.",
                banned_defaults=["Inter/Roboto", "Gradients pastel", "Sombras difusas flotantes"],
                signature_micro_details=["Rótulos troquelados en mayúsculas", "Tornillos SVG en esquinas", "Indicadores de estado LED discretos"],
                recommended_archetypes=["dense_data_monolith", "asymmetric_overlap"]
            ),
            AestheticParadigm.HAUTE_LUXURY: ParadigmSpec(
                paradigm=AestheticParadigm.HAUTE_LUXURY,
                name_display="Alta Costura y Lujo Silencioso (Atelier)",
                thesis="Exclusividad, calma aristocrática, hasta 70% de espacio negativo intencional.",
                typography_display=["Syne", "Instrument Serif"],
                typography_body=["Plus Jakarta Sans (Light)", "Epilogue"],
                color_strategy="Negro obsidiana profundo, blanco hueso, tonos piedra, lino y arena. Cero colores primarios.",
                banned_defaults=["Colores saturados", "Llamadas a la acción urgentes", "Iconos Lucide repetitivos"],
                signature_micro_details=["Espaciado de caracteres expandido (letter-spacing: 0.15em)", "Transiciones de opacidad lentas (800ms)", "Ausencia de bordes visibles"],
                recommended_archetypes=["cinematic_wide_stage", "pinned_gallery"]
            ),
            AestheticParadigm.CINEMATIC_WEBGL: ParadigmSpec(
                paradigm=AestheticParadigm.CINEMATIC_WEBGL,
                name_display="Cinemático Inmersivo WebGL (Awwwards Site of the Year)",
                thesis="Frontera tecnológica, tridimensionalidad y shaders procedurales a 60 FPS.",
                typography_display=["Clash Display", "Syne"],
                typography_body=["Satoshi", "Cabinet Grotesk"],
                color_strategy="Fondos abisales oscuros con iluminación volumétrica dinámica generada en GPU.",
                banned_defaults=["Templates estáticos planos", "Imágenes de stock sin tratar", "Falta de soporte prefers-reduced-motion"],
                signature_micro_details=["Canvas WebGL interactivo en background", "Scroll pinning con deformación de lente", "Cursor magnético fluido"],
                recommended_archetypes=["cinematic_wide_stage", "pinned_gallery"]
            ),
            AestheticParadigm.BENTO_HYPERGRID: ParadigmSpec(
                paradigm=AestheticParadigm.BENTO_HYPERGRID,
                name_display="Bento Hyper-Grid Arquitectónico (Linear / Vercel Pro)",
                thesis="Densidad estructurada, ingeniería de precisión para herramientas técnicas de alto rendimiento.",
                typography_display=["Satoshi", "Plus Jakarta Sans"],
                typography_body=["Plus Jakarta Sans", "Satoshi"],
                color_strategy="Modo oscuro enriquecido en OKLCH, bordes translúcidos con micro-resplandores radiales de cursor.",
                banned_defaults=["Celdas vacías en la cuadrícula", "Tarjetas simétricas 1x1 repetitivas", "Falta de font-variant tabular"],
                signature_micro_details=["Squircles con corner-smoothing", "Encastre matemático diofántico sin huecos", "Badges translúcidos"],
                recommended_archetypes=["gapless_bento", "dense_data_monolith"]
            ),
            AestheticParadigm.NEO_BRUTALIST: ParadigmSpec(
                paradigm=AestheticParadigm.NEO_BRUTALIST,
                name_display="Neo-Brutalismo Lúdico (Figma / Gumroad)",
                thesis="Energía accesible, alta saturación, bordes sólidos gruesos y sombras duras sin desenfoque.",
                typography_display=["Clash Display (Bold)", "Syne Extra Bold"],
                typography_body=["Plus Jakarta Sans", "Outfit"],
                color_strategy="Bloques de color planos hiper-saturados (Amarillo flúor, Azul Klein) con contraste negro puro.",
                banned_defaults=["Sombras suaves difusas", "Bordes tenues de 1px con baja opacidad", "Tipografías neutras finas"],
                signature_micro_details=["Sombras duras de 4px sin blur (box-shadow: 4px 4px 0 #000)", "Botones que se hunden al pulsar", "Badges con rotación angular -2deg"],
                recommended_archetypes=["asymmetric_overlap", "gapless_bento"]
            ),
            AestheticParadigm.ORGANIC_TACTILE: ParadigmSpec(
                paradigm=AestheticParadigm.ORGANIC_TACTILE,
                name_display="Orgánico, Táctil y Cálido (Biofílico / Cerámica)",
                thesis="Conexión con lo humano, artesanía física, texturas naturales y rechazo a la frialdad sintética.",
                typography_display=["Fraunces", "Instrument Serif"],
                typography_body=["Epilogue", "Plus Jakarta Sans"],
                color_strategy="Paleta de arcilla, terracota, salvia y carbón vegetal con iluminación difusa.",
                banned_defaults=["Colores cian o neón", "Bordes rectangulares afilados", "Animaciones mecánicas lineales"],
                signature_micro_details=["Curvas Bézier paramétricas suaves", "Filtros SVG de ruido de papel de algodón", "Elevación neumórfica blanda"],
                recommended_archetypes=["editorial_split", "asymmetric_overlap"]
            ),
            AestheticParadigm.CYBER_TELEMETRY: ParadigmSpec(
                paradigm=AestheticParadigm.CYBER_TELEMETRY,
                name_display="Telemetría y Ciberdefensa (Palantir / Anduril)",
                thesis="Densidad informativa extrema, latencia cero percibida, monitoreo crítico operacional.",
                typography_display=["JetBrains Mono", "Geist Mono"],
                typography_body=["JetBrains Mono", "Geist Mono"],
                color_strategy="Negro terminal absoluto con textos en fósforo verde o ámbar, cian espectral y rojo alerta.",
                banned_defaults=["Espacio negativo excesivo vacío", "Animaciones decorativas lentas", "Tarjetas redondeadas grandes"],
                signature_micro_details=["Coordenadas cartesianas perimetrales", "Telemetría en streaming con latencia ms", "Tablas con tabular-nums estrictos"],
                recommended_archetypes=["dense_data_monolith", "gapless_bento"]
            ),
            AestheticParadigm.RETRO_FUTURIST: ParadigmSpec(
                paradigm=AestheticParadigm.RETRO_FUTURIST,
                name_display="Retro-Futurismo Técnico y Estética Cyber-Deck",
                thesis="Nostalgia de las interfaces de computación de los 80/90 con renderizado moderno en GPU.",
                typography_display=["Space Mono", "JetBrains Mono"],
                typography_body=["Space Mono", "Geist Mono"],
                color_strategy="Monocromo fósforo ámbar o verde sobre fondo carbón con destellos de tubo CRT.",
                banned_defaults=["Modo claro genérico", "Gradientes de Figma", "Iconos minimalistas finos"],
                signature_micro_details=["Scanlines sutiles por shader", "Barras de progreso en bloques discretos", "Bordes biselados retro"],
                recommended_archetypes=["dense_data_monolith", "asymmetric_overlap"]
            ),
            AestheticParadigm.DOCUMENT_MINIMALIST: ParadigmSpec(
                paradigm=AestheticParadigm.DOCUMENT_MINIMALIST,
                name_display="Minimalismo Centrado en Documento (Notion / Substack Pro)",
                thesis="Reverencia absoluta por el texto y las ideas. La interfaz desaparece ante la lectura.",
                typography_display=["Newsreader", "Instrument Serif"],
                typography_body=["Newsreader", "Charis SIL"],
                color_strategy="Fondo niebla ultra-claro, tinta gris oscuro #1a1a1a para confort visual prolongado.",
                banned_defaults=["Distracciones de navegación pesadas", "Banners flotantes", "Shaders animados en lectura"],
                signature_micro_details=["Columna única central de 680-740px", "Menús contextuales auto-ocultables", "Tiempo estimado de lectura"],
                recommended_archetypes=["editorial_split", "cinematic_wide_stage"]
            ),
            AestheticParadigm.DECONSTRUCTIVIST: ParadigmSpec(
                paradigm=AestheticParadigm.DECONSTRUCTIVIST,
                name_display="Deconstructivismo Tipográfico Experimental (David Carson)",
                thesis="Desafío a la cuadrícula euclidiana. Tensión visual y tipografía como escultura viva.",
                typography_display=["Syne", "Clash Display"],
                typography_body=["Cabinet Grotesk", "General Sans"],
                color_strategy="Blanco y negro con estallidos abrasivos de azul eléctrico o amarillo flúor.",
                banned_defaults=["Cuadrícula de 12 columnas simétrica", "Tarjetas predecibles", "Textos de cuerpo alineados al centro"],
                signature_micro_details=["Textos monumentales cortados en márgenes", "Rotación tipográfica 90 grados", "Deformación por SVG displacement"],
                recommended_archetypes=["asymmetric_overlap", "cinematic_wide_stage"]
            ),
        }

    def get_spec(self, paradigm: AestheticParadigm) -> ParadigmSpec:
        return self._paradigm_catalog[paradigm]

    def select_deterministic_paradigm(self, brief: str) -> AestheticParadigm:
        """
        Selecciona determinísticamente uno de los 12 paradigmas basándose en el hash del brief
        y en el análisis semántico de palabras clave del dominio.
        """
        brief_lower = brief.lower()
        
        # Mapeos directos por dominio semántico
        if any(w in brief_lower for w in ["luxury", "lujo", "atelier", "fashion", "perfume", "reloj"]):
            return AestheticParadigm.HAUTE_LUXURY
        if any(w in brief_lower for w in ["editorial", "ensayo", "periodismo", "literari", "revista", "libro"]):
            return AestheticParadigm.LITERARY_EDITORIAL
        if any(w in brief_lower for w in ["industrial", "braun", "hardware", "mecanic", "audio", "device", "apollo"]):
            return AestheticParadigm.INDUSTRIAL_BRUTALIST
        if any(w in brief_lower for w in ["telemetr", "satelite", "cyber", "defensa", "radar", "militar", "scada", "security"]):
            return AestheticParadigm.CYBER_TELEMETRY
        if any(w in brief_lower for w in ["cinematic", "webgl", "3d", "shader", "awwwards", "inmersiv"]):
            return AestheticParadigm.CINEMATIC_WEBGL
        if any(w in brief_lower for w in ["retro", "80s", "90s", "cyberdeck", "crt", "terminal"]):
            return AestheticParadigm.RETRO_FUTURIST
        if any(w in brief_lower for w in ["organic", "tierra", "natural", "ceramica", "biologic", "sustentab"]):
            return AestheticParadigm.ORGANIC_TACTILE
        if any(w in brief_lower for w in ["neo-brutalist", "pop", "figma", "gumroad", "divertid", "sticker"]):
            return AestheticParadigm.NEO_BRUTALIST
        if any(w in brief_lower for w in ["document", "notion", "lectura", "substack", "minimal"]):
            return AestheticParadigm.DOCUMENT_MINIMALIST
        if any(w in brief_lower for w in ["experimental", "deconstruct", "carson", "caos", "arte"]):
            return AestheticParadigm.DECONSTRUCTIVIST
        if any(w in brief_lower for w in ["bento", "linear", "dashboard", "analytics", "saas", "tech"]):
            return AestheticParadigm.BENTO_HYPERGRID

        # Fallback pseudo-aleatorio determinista por hash SHA-256
        h = int(hashlib.sha256(brief.encode("utf-8")).hexdigest(), 16)
        all_paradigms = list(AestheticParadigm)
        return all_paradigms[h % len(all_paradigms)]

    def audit_copywriting(self, text: str) -> CopyAuditResult:
        """
        Audita el texto de la interfaz para detectar frases vacías o clichés de marketing de IA.
        """
        detected = []
        for pat in AI_COPY_CLICHES:
            if re.search(pat, text, re.IGNORECASE):
                # Extrae el término limpio
                clean_term = pat.replace(r"\b", "")
                detected.append(clean_term)

        total_words = len(text.split())
        if total_words == 0:
            score = 1.0
        else:
            penalty = len(detected) * 0.20
            score = max(0.0, 1.0 - penalty)

        recs = []
        if detected:
            recs.append(f"Erradicar los clichés detectados: {', '.join(detected)}.")
            recs.append("Reemplazar por copy específico del dominio con métricas numéricas concretas (ej. '180ms p99' en vez de 'lightning-fast').")

        return CopyAuditResult(
            is_clean=len(detected) == 0,
            banned_cliches_detected=detected,
            authenticity_score=round(score, 2),
            recommendations=recs
        )

    def evaluate_dfii(
        self,
        impact: int,
        fit: int,
        feasibility: int,
        performance: int,
        consistency_risk: int
    ) -> DFIIScore:
        """Calcula el Design Feasibility & Impact Index."""
        return DFIIScore(
            impact=max(1, min(5, impact)),
            fit=max(1, min(5, fit)),
            feasibility=max(1, min(5, feasibility)),
            performance=max(1, min(5, performance)),
            consistency_risk=max(1, min(5, consistency_risk))
        )

    # Aliases de conveniencia e interoperabilidad
    select_paradigm_for_domain = select_deterministic_paradigm
    audit_copy = audit_copywriting
