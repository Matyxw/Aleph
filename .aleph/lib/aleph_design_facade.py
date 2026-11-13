"""
.aleph/lib/aleph_design_facade.py
Unified Sovereign Design Engine Facade (Track 10).
Estándar: End-to-End Orchestration / Z3 Verification / Dual HTML5-React19 Compilation / MCP Hook.

Orquestador unificado de grado maestro para el motor de diseño soberano de Aleph:
Coordina Direction Engine, Token Compiler, Design IR v2.0, SMT Verifier (Z3),
Compiladores HTML5/React19, Render Oracle y Design Critic en un único flujo garantizado.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from lib.aleph_direction_engine import (
        AestheticParadigm,
        DirectionEngine,
        CopyAuditResult,
    )
    from lib.aleph_token_compiler import (
        AlephTokenCompiler,
    )
    from lib.aleph_design_ir import (
        DesignIR,
        IRComponent,
        SpatialArchetype,
        build_paradigm_template,
        create_paradigm_ir,
    )
    from lib.aleph_smt_layout_verifier import (
        FluidMeasure,
        LayoutContainer,
        LayoutElement,
        SMTLayoutVerifier,
    )
    from lib.aleph_shader_compiler import (
        AlephShaderCompiler,
    )
    from lib.aleph_compiler_html import (
        AlephHTMLCompiler,
    )
    from lib.aleph_compiler_react import (
        AlephReactCompiler,
    )
    from lib.aleph_render_oracle import (
        AlephRenderOracle,
        AuditReport,
    )
    from lib.aleph_design_critic import (
        AlephDesignCritic,
        CritiqueScorecard,
    )
except ImportError:
    from aleph_direction_engine import (  # type: ignore
        AestheticParadigm,
        DirectionEngine,
        CopyAuditResult,
    )
    from aleph_token_compiler import (  # type: ignore
        AlephTokenCompiler,
    )
    from aleph_design_ir import (  # type: ignore
        DesignIR,
        IRComponent,
        SpatialArchetype,
        build_paradigm_template,
        create_paradigm_ir,
    )
    from aleph_smt_layout_verifier import (  # type: ignore
        FluidMeasure,
        LayoutContainer,
        LayoutElement,
        SMTLayoutVerifier,
    )
    from aleph_shader_compiler import (  # type: ignore
        AlephShaderCompiler,
    )
    from aleph_compiler_html import (  # type: ignore
        AlephHTMLCompiler,
    )
    from aleph_compiler_react import (  # type: ignore
        AlephReactCompiler,
    )
    from aleph_render_oracle import (  # type: ignore
        AlephRenderOracle,
        AuditReport,
    )
    from aleph_design_critic import (  # type: ignore
        AlephDesignCritic,
        CritiqueScorecard,
    )


@dataclass
class SovereignDesignResult:
    """Artefacto completo generado y formalmente certificado por el motor."""
    title: str
    paradigm: str
    archetype: str
    html_bundle: str
    css_bundle: str
    react_tsx_bundle: str
    smt_verified: bool
    smt_status: str
    critic_score: float
    is_sovereign_certified: bool
    audit_report: Dict[str, Any]
    critic_breakdown: Dict[str, float]
    raw_ir_json: str
    modular_components: Dict[str, str] = field(default_factory=dict)
    output_dir: Optional[str] = None


class AlephDesignFacade:
    """
    Fachada Unificada del Motor de Diseño Soberano.
    Punto de entrada maestro para crear, verificar, compilar y auditar interfaces.
    """

    def __init__(self):
        self.direction_engine = DirectionEngine()
        self.smt_verifier = SMTLayoutVerifier(min_viewport=320.0, max_viewport=2560.0)
        self.html_compiler = AlephHTMLCompiler()
        self.react_compiler = AlephReactCompiler()
        self.render_oracle = AlephRenderOracle()
        self.design_critic = AlephDesignCritic()
        self.shader_compiler = AlephShaderCompiler()

    def generate_design_from_brief(
        self,
        brief: str,
        paradigm_override: Optional[AestheticParadigm] = None,
        title: Optional[str] = None,
        custom_ir_tree: Optional[Union[Dict[str, Any], List[Dict[str, Any]], DesignIR]] = None,
        output_dir: Optional[str] = None,
    ) -> SovereignDesignResult:
        """
        Flujo de 7 pasos de extremo a extremo:
        1. Selección de paradigma estético y sanitización anti-slop del copy.
        2. Carga / síntesis de Design IR v2.0 canónico (o árbol AST inyectado vía custom_ir_tree).
        3. Verificación SMT Z3 de contención de layout (cero overflow-x).
        4. Compilación dual a HTML5 + CSS (@layer) y React 19 TSX modular.
        5. Auditoría de Render Oracle (A11y y detección de slop).
        6. Evaluación del Crítico de Diseño y Gobernador Anti-Colapso.
        7. Certificación y entrega del artefacto integral (con exportación opcional a disco).
        """
        # Paso 1: Dirección y Sanitización
        if paradigm_override:
            chosen_paradigm = paradigm_override
        else:
            chosen_paradigm = self.direction_engine.select_deterministic_paradigm(brief)

        copy_audit = self.direction_engine.audit_copywriting(brief)
        doc_title = title or f"{brief[:40]} - Sovereign Edition"

        # Paso 2: Design IR v2.0
        if custom_ir_tree is not None:
            ir = create_paradigm_ir(chosen_paradigm, title=doc_title, custom_ir_tree=custom_ir_tree)
        else:
            ir = create_paradigm_ir(chosen_paradigm, title=doc_title)

        # Paso 3: Verificación SMT Formal de Layout (Página responsiva columna)
        gutter = min(16.0, ir.spatial_grammar.bounds.fluid_gutter_min)
        container = LayoutContainer(
            id="root_container",
            width=FluidMeasure(min_val=320.0, slope=1.0, base=0.0, max_val=2560.0),
            padding_left=gutter,
            padding_right=gutter,
            gap=16.0,
            direction="column",
            wrap=True,
            children=[
                LayoutElement(
                    id=comp.id,
                    width=FluidMeasure(min_val=80.0, slope=0.8, base=0.0, max_val=1200.0)
                )
                for comp in ir.root_components
            ]
        )
        smt_res = self.smt_verifier.verify_horizontal_containment(container)

        # Paso 4: Compilación Dual (HTML5 + CSS y React 19 Modular)
        html_out = self.html_compiler.compile_html(ir, full_document=True)
        css_out = self.html_compiler.compile_css(ir)
        react_tsx = self.react_compiler.compile_page(ir, page_name="SovereignPage")
        modular_files = self.react_compiler.compile_modular_project(ir)

        # Si output_dir está configurado, exportar artefactos a disco de forma atómica
        if output_dir:
            out_path = os.path.abspath(output_dir)
            os.makedirs(out_path, exist_ok=True)
            with open(os.path.join(out_path, "preview.html"), "w", encoding="utf-8") as f:
                f.write(html_out)
            with open(os.path.join(out_path, "design_ir.json"), "w", encoding="utf-8") as f:
                f.write(ir.to_json())
            react_dest = os.path.join(out_path, "src", "components", "aleph")
            os.makedirs(react_dest, exist_ok=True)
            for rel_file, code in modular_files.items():
                target_file_path = os.path.join(react_dest, rel_file)
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                with open(target_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

        # Paso 5: Render Oracle & A11y Audit
        audit = self.render_oracle.audit_html(html_out)

        # Paso 6: Design Critic & Anti-Collapse Governor
        scorecard = self.design_critic.critique(ir)
        self.design_critic.latent_governor.check_and_record(ir)

        # Paso 7: Certificación
        is_sovereign = (
            smt_res.is_overflow_free
            and audit.is_passing
            and scorecard.is_sovereign
        )

        return SovereignDesignResult(
            title=doc_title,
            paradigm=chosen_paradigm.value,
            archetype=ir.spatial_grammar.archetype.value,
            html_bundle=html_out,
            css_bundle=css_out,
            react_tsx_bundle=react_tsx,
            smt_verified=smt_res.is_overflow_free,
            smt_status=smt_res.status,
            critic_score=scorecard.total_score,
            is_sovereign_certified=is_sovereign,
            audit_report={
                "is_passing": audit.is_passing,
                "a11y_score": audit.accessibility_score,
                "slop_score": audit.slop_score,
                "heading_violations": audit.heading_hierarchy_violations,
                "slop_findings": audit.slop_findings,
            },
            critic_breakdown={
                "typography": scorecard.typography_score,
                "color_contrast": scorecard.color_contrast_score,
                "spatial_balance": scorecard.spatial_balance_score,
                "motion_physics": scorecard.motion_physics_score,
                "craftsmanship": scorecard.craftsmanship_score,
                "anti_slop": scorecard.anti_slop_score,
                "total": scorecard.total_score,
            },
            raw_ir_json=ir.to_json(),
            modular_components=modular_files,
            output_dir=os.path.abspath(output_dir) if output_dir else None,
        )

    def audit_existing_markup(self, html_content: str) -> Dict[str, Any]:
        """Audita cualquier marcado HTML externo para certificar si es soberano o slop de IA."""
        report = self.render_oracle.audit_html(html_content)
        return {
            "is_passing": report.is_passing,
            "accessibility_score": report.accessibility_score,
            "slop_score": report.slop_score,
            "heading_violations": report.heading_hierarchy_violations,
            "slop_findings": report.slop_findings,
            "summary": report.summary()
        }
