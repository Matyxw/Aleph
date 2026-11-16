#!/usr/bin/env python3
"""
.aleph/scripts/update_design_ir_ch2.py
Aplica los enriquecimientos y blindajes canónicos del Capítulo 2 a aleph_design_ir.py.
Encapsulado en función ejecutable para permitir importación segura sin efectos colaterales.
"""
from pathlib import Path
import re

def apply_design_ir_ch2_enrichments(ir_path: Path | None = None) -> Path:
    if ir_path is None:
        ir_path = Path(__file__).resolve().parent.parent / "lib" / "aleph_design_ir.py"
    content = ir_path.read_text(encoding="utf-8")

    # 1. Asegurar alias canónicos en AestheticParadigm
    if 'EDITORIAL_ELEGANCE = "literary_editorial"' not in content:
        content = content.replace(
            'LITERARY_EDITORIAL = "literary_editorial"',
            'LITERARY_EDITORIAL = "literary_editorial"\n    EDITORIAL_ELEGANCE = "literary_editorial"  # Alias canónico V7.0'
        )

    if 'RETRO_FUTURISM = "retro_futurist"' not in content:
        content = content.replace(
            'RETRO_FUTURIST = "retro_futurist"',
            'RETRO_FUTURIST = "retro_futurist"\n    RETRO_FUTURISM = "retro_futurist"  # Alias canónico V7.0'
        )

    # 2. Actualizar _build_rich_6section_template para enriquecer componentes con interaction_role y spotlight_tracking
    old_navbar = """    # 1. NAVBAR [ORIENT]
        nav_brand = IRComponent(
            id=f"{p_val}_nav_brand",
            component_type="badge",
            task_phase=TaskPhase.ORIENT,
            props={"text": brand_name, "role": "brand", "variant": "subtle"}
        )
        nav_item_1 = IRComponent(
            id=f"{p_val}_nav_item_1",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Arquitectura", "href": "#architecture"}
        )
        nav_item_2 = IRComponent(
            id=f"{p_val}_nav_item_2",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Especificación SMT", "href": "#smt"}
        )
        nav_item_3 = IRComponent(
            id=f"{p_val}_nav_item_3",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Telemetría", "href": "#telemetry"}
        )
        nav_item_4 = IRComponent(
            id=f"{p_val}_nav_item_4",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Benchmarks", "href": "#benchmarks"}
        )
        nav_cta = IRComponent(
            id=f"{p_val}_nav_cta",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=primary_btn_matrix,
            props={"label": "Terminal Soberana", "variant": "primary"}
        )"""

    new_navbar = """    # 1. NAVBAR [ORIENT]
        nav_brand = IRComponent(
            id=f"{p_val}_nav_brand",
            component_type="badge",
            interaction_role=InteractionRole.BADGE_CHIP,
            task_phase=TaskPhase.ORIENT,
            props={"text": brand_name, "role": "brand", "variant": "subtle"}
        )
        nav_item_1 = IRComponent(
            id=f"{p_val}_nav_item_1",
            component_type="button",
            interaction_role=InteractionRole.NAV_LINK,
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Arquitectura", "href": "#architecture"}
        )
        nav_item_2 = IRComponent(
            id=f"{p_val}_nav_item_2",
            component_type="button",
            interaction_role=InteractionRole.NAV_LINK,
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Especificación SMT", "href": "#smt"}
        )
        nav_item_3 = IRComponent(
            id=f"{p_val}_nav_item_3",
            component_type="button",
            interaction_role=InteractionRole.NAV_LINK,
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Telemetría", "href": "#telemetry"}
        )
        nav_item_4 = IRComponent(
            id=f"{p_val}_nav_item_4",
            component_type="button",
            interaction_role=InteractionRole.NAV_LINK,
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Benchmarks", "href": "#benchmarks"}
        )
        nav_cta = IRComponent(
            id=f"{p_val}_nav_cta",
            component_type="button",
            interaction_role=InteractionRole.ACTION_PRIMARY,
            is_interactive=True,
            spotlight_tracking=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=primary_btn_matrix,
            props={"label": "Terminal Soberana", "variant": "primary"}
        )"""

    old_hero_badge = """    # 2. HERO STAGE [ORIENT]
        hero_badge = IRComponent(
            id=f"{p_val}_hero_badge",
            component_type="badge",
            task_phase=TaskPhase.ORIENT,
            props={"text": "v7.0 Soberano", "variant": "outline"}
        )"""

    new_hero_badge = """    # 2. HERO STAGE [ORIENT]
        hero_badge = IRComponent(
            id=f"{p_val}_hero_badge",
            component_type="badge",
            interaction_role=InteractionRole.BADGE_CHIP,
            task_phase=TaskPhase.ORIENT,
            props={"text": "v7.0 Soberano", "variant": "outline"}
        )"""

    old_hero_btn = """    hero_btn_sec = IRComponent(
            id=f"{p_val}_hero_btn_sec",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Auditoría de Invariantes", "variant": "ghost"}
        )"""

    new_hero_btn = """    hero_btn_sec = IRComponent(
            id=f"{p_val}_hero_btn_sec",
            component_type="button",
            interaction_role=InteractionRole.ACTION_GHOST,
            is_interactive=True,
            task_phase=TaskPhase.ORIENT,
            state_matrix=ghost_btn_matrix,
            props={"label": "Auditoría de Invariantes", "variant": "ghost"}
        )"""

    old_metrics = """    # 3. METRIC TICKER [WORK]
        m1 = IRComponent(
            id=f"{p_val}_metric_lat",
            component_type="metric_ticker",
            task_phase=TaskPhase.WORK,
            props={"label": "Latencia p99", "value": "120 µs", "delta": "-42%", "tabular_nums": True}
        )
        m2 = IRComponent(
            id=f"{p_val}_metric_tps",
            component_type="metric_ticker",
            task_phase=TaskPhase.WORK,
            props={"label": "Throughput", "value": "1.42 M req/s", "delta": "+88%", "tabular_nums": True}
        )
        m3 = IRComponent(
            id=f"{p_val}_metric_smt",
            component_type="metric_ticker",
            task_phase=TaskPhase.WORK,
            props={"label": "Verificación SMT Z3", "value": "100% UNSAT", "delta": "0 overflow", "tabular_nums": True}
        )
        m4 = IRComponent(
            id=f"{p_val}_metric_mem",
            component_type="metric_ticker",
            task_phase=TaskPhase.WORK,
            props={"label": "Huella Memoria", "value": "4.2 MB", "delta": "Zero-leak", "tabular_nums": True}
        )"""

    new_metrics = """    # 3. METRIC TICKER [WORK]
        m1 = IRComponent(
            id=f"{p_val}_metric_lat",
            component_type="metric_ticker",
            interaction_role=InteractionRole.METRIC_COUNTER,
            task_phase=TaskPhase.WORK,
            props={"label": "Latencia p99", "value": "120 µs", "delta": "-42%", "tabular_nums": True}
        )
        m2 = IRComponent(
            id=f"{p_val}_metric_tps",
            component_type="metric_ticker",
            interaction_role=InteractionRole.METRIC_COUNTER,
            task_phase=TaskPhase.WORK,
            props={"label": "Throughput", "value": "1.42 M req/s", "delta": "+88%", "tabular_nums": True}
        )
        m3 = IRComponent(
            id=f"{p_val}_metric_smt",
            component_type="metric_ticker",
            interaction_role=InteractionRole.METRIC_COUNTER,
            task_phase=TaskPhase.WORK,
            props={"label": "Verificación SMT Z3", "value": "100% UNSAT", "delta": "0 overflow", "tabular_nums": True}
        )
        m4 = IRComponent(
            id=f"{p_val}_metric_mem",
            component_type="metric_ticker",
            interaction_role=InteractionRole.METRIC_COUNTER,
            task_phase=TaskPhase.WORK,
            props={"label": "Huella Memoria", "value": "4.2 MB", "delta": "Zero-leak", "tabular_nums": True}
        )"""

    old_bento_action = """    card_action = IRComponent(
            id=action_id,
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.WORK,
            island=code_island,
            state_matrix=accent_btn_matrix,
            spatial_intent={"grid_column": "span 8"},
            props={"label": action_label, "grid_span": "col-span-8"}
        )"""

    new_bento_action = """    card_action = IRComponent(
            id=action_id,
            component_type="button",
            interaction_role=InteractionRole.ACTION_SECONDARY,
            is_interactive=True,
            spotlight_tracking=True,
            task_phase=TaskPhase.WORK,
            island=code_island,
            state_matrix=accent_btn_matrix,
            spatial_intent={"grid_column": "span 8"},
            props={"label": action_label, "grid_span": "col-span-8"}
        )"""

    old_telem = """    # 5. TELEMETRY PANEL [WORK]
        telem_head = IRComponent(
            id=f"{p_val}_telem_head",
            component_type="headline",
            task_phase=TaskPhase.WORK,
            max_lines=2,
            props={"text": "Matriz de Telemetría en Tiempo Real"}
        )
        telem_r1 = IRComponent(
            id=f"{p_val}_telem_r1",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Blink Render Time", "value": "12.4ms", "status": "VERIFIED"}
        )
        telem_r2 = IRComponent(
            id=f"{p_val}_telem_r2",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Z3 SMT Invariant", "value": "UNSAT", "status": "OPTIMAL"}
        )
        telem_r3 = IRComponent(
            id=f"{p_val}_telem_r3",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Cumulative Layout Shift", "value": "0.000", "status": "IMMUTABLE"}
        )
        telem_act = IRComponent(
            id=f"{p_val}_telem_act",
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.WORK,
            state_matrix=ghost_btn_matrix,
            props={"label": "Actualizar Muestreo"}
        )"""

    new_telem = """    # 5. TELEMETRY PANEL [WORK]
        telem_head = IRComponent(
            id=f"{p_val}_telem_head",
            component_type="headline",
            task_phase=TaskPhase.WORK,
            max_lines=2,
            props={"text": "Matriz de Telemetría en Tiempo Real", "is_headline": True}
        )
        telem_r1 = IRComponent(
            id=f"{p_val}_telem_r1",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Blink Render Time", "value": "12.4ms", "status": "VERIFIED"}
        )
        telem_r2 = IRComponent(
            id=f"{p_val}_telem_r2",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Z3 SMT Invariant", "value": "UNSAT", "status": "OPTIMAL"}
        )
        telem_r3 = IRComponent(
            id=f"{p_val}_telem_r3",
            component_type="card",
            task_phase=TaskPhase.WORK,
            props={"metric": "Cumulative Layout Shift", "value": "0.000", "status": "IMMUTABLE"}
        )
        telem_act = IRComponent(
            id=f"{p_val}_telem_act",
            component_type="button",
            interaction_role=InteractionRole.ACTION_GHOST,
            is_interactive=True,
            task_phase=TaskPhase.WORK,
            state_matrix=ghost_btn_matrix,
            props={"label": "Actualizar Muestreo"}
        )"""

    old_cta_foot = """    # 6. CTA BANNER [CONFIRM]
        cta_title = IRComponent(
            id=f"{p_val}_cta_title",
            component_type="headline",
            task_phase=TaskPhase.CONFIRM,
            max_lines=2,
            props={"text": "Despliegue Determinista Soberano"}
        )
        cta_sub = IRComponent(
            id=f"{p_val}_cta_sub",
            component_type="text",
            task_phase=TaskPhase.CONFIRM,
            props={"text": "Sin dependencias de CDN, sin suscripciones a APIs externas y con verificación formal."}
        )
        confirm_btn = IRComponent(
            id=confirm_id,
            component_type="button",
            is_interactive=True,
            task_phase=TaskPhase.CONFIRM,
            state_matrix=primary_btn_matrix,
            props={"label": confirm_label}
        )
        cta_banner = IRComponent(
            id=f"{p_val}_cta_banner",
            component_type="cta_banner",
            task_phase=TaskPhase.CONFIRM,
            children=[cta_title, cta_sub, confirm_btn]
        )

        # 7. FOOTER [CONFIRM]
        foot_brand = IRComponent(
            id=f"{p_val}_foot_brand",
            component_type="badge",
            task_phase=TaskPhase.CONFIRM,
            props={"text": brand_name, "role": "brand"}
        )"""

    new_cta_foot = """    # 6. CTA BANNER [CONFIRM]
        cta_title = IRComponent(
            id=f"{p_val}_cta_title",
            component_type="headline",
            task_phase=TaskPhase.CONFIRM,
            max_lines=2,
            props={"text": "Despliegue Determinista Soberano", "is_headline": True}
        )
        cta_sub = IRComponent(
            id=f"{p_val}_cta_sub",
            component_type="text",
            task_phase=TaskPhase.CONFIRM,
            props={"text": "Sin dependencias de CDN, sin suscripciones a APIs externas y con verificación formal."}
        )
        confirm_btn = IRComponent(
            id=confirm_id,
            component_type="button",
            interaction_role=InteractionRole.ACTION_PRIMARY,
            is_interactive=True,
            spotlight_tracking=True,
            task_phase=TaskPhase.CONFIRM,
            state_matrix=primary_btn_matrix,
            props={"label": confirm_label, "variant": "primary"}
        )
        cta_banner = IRComponent(
            id=f"{p_val}_cta_banner",
            component_type="cta_banner",
            task_phase=TaskPhase.CONFIRM,
            children=[cta_title, cta_sub, confirm_btn]
        )

        # 7. FOOTER [CONFIRM]
        foot_brand = IRComponent(
            id=f"{p_val}_foot_brand",
            component_type="badge",
            interaction_role=InteractionRole.BADGE_CHIP,
            task_phase=TaskPhase.CONFIRM,
            props={"text": brand_name, "role": "brand"}
        )"""

    # Normalizar saltos de línea para el reemplazo
    def normalize(s):
        return s.replace("\r\n", "\n")

    content_norm = normalize(content)

    replacements = [
        (normalize(old_navbar), normalize(new_navbar)),
        (normalize(old_hero_badge), normalize(new_hero_badge)),
        (normalize(old_hero_btn), normalize(new_hero_btn)),
        (normalize(old_metrics), normalize(new_metrics)),
        (normalize(old_bento_action), normalize(new_bento_action)),
        (normalize(old_telem), normalize(new_telem)),
        (normalize(old_cta_foot), normalize(new_cta_foot)),
    ]

    for old, new in replacements:
        if old in content_norm:
            content_norm = content_norm.replace(old, new, 1)
            print("Reemplazo exitoso en _build_rich_6section_template")
        else:
            print("WARNING: no se encontró bloque:", old[:40])

    # Ahora perfeccionar cada uno de los 12 paradigmas en create_paradigm_ir
    # Paradigm 1: SWISS_INTERNATIONAL (0px radius estricto, alta tensión ortogonal, 12-col)
    old_swiss_surf = '"base": SurfaceToken(name="base", border_width_px=1.0, border_radius_scale={"none": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0})'
    new_swiss_surf = '"base": SurfaceToken(name="base", border_width_px=1.0, border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0})'
    content_norm = content_norm.replace(old_swiss_surf, new_swiss_surf)

    # Paradigm 2: LITERARY_EDITORIAL / EDITORIAL_ELEGANCE (0-2px radius, serif alta jerarquía, papel d50 o marfil)
    old_lit_block = """    # ========================================================================
        # 2. LITERARY EDITORIAL
        # ========================================================================
        elif paradigm == AestheticParadigm.LITERARY_EDITORIAL:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.96, 0.015, 80.0), hex_value="#F7F4EE", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.20, 0.01, 60.0), hex_value="#1F1B18", role="on_surface", wcag_contrast_on_surface=14.2),
                    "primary": ColorToken(name="primary", oklch=(0.42, 0.12, 35.0), hex_value="#7F2B1D", role="primary", wcag_contrast_on_surface=7.8),
                    "border": ColorToken(name="border", oklch=(0.88, 0.02, 75.0), hex_value="#E2DCD2", role="border")
                },
                surfaces={"parchment": SurfaceToken(name="parchment", border_width_px=0.5)}
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.EDITORIAL_STAGGERED,
                bounds=SpatialBounds(max_container_width=960.0)
            )
            typography = TypographySystem(
                primary_family="Newsreader, Charter, Georgia, serif",
                mono_family="Courier Prime, monospace",
                cls_overrides={"primary": cls_metric},
                scales={
                    "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(2.2rem, 3vw + 1rem, 3.5rem)", line_height_ratio=1.18, is_headline=True, max_lines=3),
                    "body": TypeScaleLevel(name="body", font_size_clamp="clamp(1.1rem, 0.2vw + 1rem, 1.25rem)", line_height_ratio=1.65)
                }
            )"""

    new_lit_block = """    # ========================================================================
        # 2. LITERARY EDITORIAL / EDITORIAL ELEGANCE
        # ========================================================================
        elif paradigm in (AestheticParadigm.LITERARY_EDITORIAL, AestheticParadigm.EDITORIAL_ELEGANCE):
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.965, 0.012, 85.0), hex_value="#F7F4EE", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.20, 0.01, 60.0), hex_value="#1F1B18", role="on_surface", wcag_contrast_on_surface=14.2),
                    "primary": ColorToken(name="primary", oklch=(0.42, 0.12, 35.0), hex_value="#7F2B1D", role="primary", wcag_contrast_on_surface=7.8),
                    "border": ColorToken(name="border", oklch=(0.88, 0.02, 75.0), hex_value="#E2DCD2", role="border")
                },
                shadows={
                    "editorial_subtle": ShadowToken(name="editorial_subtle", elevation_level=1, x=0, y=2, blur=4, spread=0, color="oklch(0.20 0.02 50 / 0.04)")
                },
                surfaces={
                    "parchment": SurfaceToken(
                        name="parchment",
                        border_width_px=0.5,
                        border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 1.0, "lg": 2.0, "full": 2.0},
                        noise_grain_opacity=0.04
                    )
                }
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.EDITORIAL_STAGGERED,
                bounds=SpatialBounds(max_container_width=960.0, columns=12)
            )
            typography = TypographySystem(
                primary_family="Newsreader, Instrument Serif, Charter, Georgia, serif",
                mono_family="Courier Prime, monospace",
                cls_overrides={"primary": cls_metric},
                scales={
                    "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(2.2rem, 3vw + 1rem, 3.5rem)", line_height_ratio=1.18, is_headline=True, max_lines=3),
                    "body": TypeScaleLevel(name="body", font_size_clamp="clamp(1.1rem, 0.2vw + 1rem, 1.25rem)", line_height_ratio=1.65)
                }
            )
            assets = SovereignAssets(
                noises={
                    "paper_texture": NoiseTexture(texture_id="paper_texture", noise_type="simplex", frequency=0.75, octaves=3, opacity=0.04)
                }
            )"""

    content_norm = content_norm.replace(normalize(old_lit_block), normalize(new_lit_block))

    # Paradigm 3: INDUSTRIAL_BRUTALIST (0-3px bisel chapa, alta densidad DIN SCADA)
    old_ind_block = """    # ========================================================================
        # 3. INDUSTRIAL BRUTALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.INDUSTRIAL_BRUTALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.22, 0.005, 260.0), hex_value="#1F2124", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.005, 260.0), hex_value="#E8EAED", role="on_surface", wcag_contrast_on_surface=13.0),
                    "primary": ColorToken(name="primary", oklch=(0.75, 0.16, 75.0), hex_value="#F5A623", role="primary", wcag_contrast_on_surface=9.5),
                    "border": ColorToken(name="border", oklch=(0.40, 0.005, 260.0), hex_value="#4A4E57", role="border")
                },
                surfaces={"steel": SurfaceToken(name="steel", border_width_px=2.0, surface_treatment=SurfaceTreatment.RAW_OUTLINE)}
            )
            spatial = SpatialGrammar(archetype=SpatialArchetype.TELEMETRY_DASHBOARD)
            typography = TypographySystem(
                primary_family="JetBrains Mono, monospace",
                mono_family="JetBrains Mono, monospace",
                cls_overrides={"primary": cls_metric},
                scales={
                    "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(1.8rem, 2vw + 1rem, 2.8rem)", line_height_ratio=1.1, is_headline=True, max_lines=2)
                }
            )"""

    new_ind_block = """    # ========================================================================
        # 3. INDUSTRIAL BRUTALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.INDUSTRIAL_BRUTALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.22, 0.005, 260.0), hex_value="#1F2124", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.005, 260.0), hex_value="#E8EAED", role="on_surface", wcag_contrast_on_surface=13.0),
                    "primary": ColorToken(name="primary", oklch=(0.75, 0.16, 75.0), hex_value="#F5A623", role="primary", wcag_contrast_on_surface=9.5),
                    "border": ColorToken(name="border", oklch=(0.40, 0.005, 260.0), hex_value="#4A4E57", role="border")
                },
                shadows={
                    "machined": ShadowToken(name="machined", elevation_level=2, x=0, y=2, blur=4, spread=0, color="oklch(0 0 0 / 0.35)")
                },
                surfaces={
                    "steel": SurfaceToken(
                        name="steel",
                        border_width_px=2.0,
                        surface_treatment=SurfaceTreatment.RAW_OUTLINE,
                        border_radius_scale={"none": 0.0, "xs": 1.0, "sm": 1.0, "md": 2.0, "lg": 3.0, "full": 3.0}
                    )
                }
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.TELEMETRY_DASHBOARD,
                bounds=SpatialBounds(columns=12, fluid_gutter_min=8.0, fluid_gutter_max=16.0)
            )
            typography = TypographySystem(
                primary_family="DIN 1451, DIN Pro, Univers Next, JetBrains Mono, monospace",
                mono_family="JetBrains Mono, monospace",
                cls_overrides={"primary": cls_metric},
                scales={
                    "h1": TypeScaleLevel(name="h1", font_size_clamp="clamp(1.8rem, 2vw + 1rem, 2.8rem)", line_height_ratio=1.1, is_headline=True, max_lines=2)
                }
            )
            assets = SovereignAssets(
                noises={
                    "cast_metal": NoiseTexture(texture_id="cast_metal", noise_type="perlin", frequency=0.92, octaves=4, opacity=0.06)
                }
            )"""

    content_norm = content_norm.replace(normalize(old_ind_block), normalize(new_ind_block))

    # Paradigm 4: HAUTE_LUXURY (0px ortogonal, 70% espacio negativo, oro viejo/obsidiana)
    old_lux_block = """    # ========================================================================
        # 4. HAUTE LUXURY
        # ========================================================================
        elif paradigm == AestheticParadigm.HAUTE_LUXURY:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.12, 0.008, 280.0), hex_value="#0B0B0D", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.95, 0.015, 85.0), hex_value="#FAF8F5", role="on_surface", wcag_contrast_on_surface=16.8),
                    "primary": ColorToken(name="primary", oklch=(0.76, 0.11, 85.0), hex_value="#D4AF37", role="primary", wcag_contrast_on_surface=9.2),
                    "border": ColorToken(name="border", oklch=(0.30, 0.02, 85.0), hex_value="#3A3424", role="border")
                },
                shadows={"soft": ShadowToken(name="soft", elevation_level=2, x=0, y=8, blur=24, spread=-4, color="oklch(0 0 0 / 0.6)", ambient_occlusion=0.4)},
                surfaces={"velvet": SurfaceToken(name="velvet", border_width_px=0.5)}
            )
            spatial = SpatialGrammar(archetype=SpatialArchetype.GOLDEN_SPIRAL_FLOW)"""

    new_lux_block = """    # ========================================================================
        # 4. HAUTE LUXURY
        # ========================================================================
        elif paradigm == AestheticParadigm.HAUTE_LUXURY:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.12, 0.008, 280.0), hex_value="#0B0B0D", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.95, 0.015, 85.0), hex_value="#FAF8F5", role="on_surface", wcag_contrast_on_surface=16.8),
                    "primary": ColorToken(name="primary", oklch=(0.76, 0.11, 85.0), hex_value="#D4AF37", role="primary", wcag_contrast_on_surface=9.2),
                    "border": ColorToken(name="border", oklch=(0.30, 0.02, 85.0), hex_value="#3A3424", role="border")
                },
                shadows={"soft": ShadowToken(name="soft", elevation_level=2, x=0, y=8, blur=24, spread=-4, color="oklch(0 0 0 / 0.6)", ambient_occlusion=0.4)},
                surfaces={
                    "velvet": SurfaceToken(
                        name="velvet",
                        border_width_px=0.5,
                        border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0}
                    )
                }
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.GOLDEN_SPIRAL_FLOW,
                asymmetric_ratio=1.618,
                rhythm_gap_scale={"xs": 8.0, "sm": 16.0, "md": 32.0, "lg": 48.0, "xl": 64.0, "2xl": 96.0, "3xl": 128.0}
            )"""

    content_norm = content_norm.replace(normalize(old_lux_block), normalize(new_lux_block))

    # Paradigm 5: CINEMATIC_WEBGL (12-16px, atmósfera GLSL, HUD periférico)
    old_cine_surf = 'surfaces={"lens": SurfaceToken(name="lens", backdrop_blur_px=16.0, surface_treatment=SurfaceTreatment.GLASSMORPHIC)}'
    new_cine_surf = """surfaces={
                    "lens": SurfaceToken(
                        name="lens",
                        backdrop_blur_px=16.0,
                        surface_treatment=SurfaceTreatment.GLASSMORPHIC,
                        border_radius_scale={"none": 0.0, "xs": 6.0, "sm": 8.0, "md": 12.0, "lg": 16.0, "full": 9999.0}
                    )
                }"""
    content_norm = content_norm.replace(old_cine_surf, new_cine_surf)

    # Paradigm 6: BENTO_HYPERGRID (squircle continuo, encastre diofántico)
    old_bento_surf = 'surfaces={"bento_card": SurfaceToken(name="bento_card", border_radius_scale={"card": 20.0}, border_width_px=1.0)}'
    new_bento_surf = """surfaces={
                    "bento_card": SurfaceToken(
                        name="bento_card",
                        border_radius_scale={"none": 0.0, "xs": 8.0, "sm": 12.0, "md": 18.0, "lg": 24.0, "squircle": 20.0, "card": 20.0, "full": 9999.0},
                        border_width_px=1.0,
                        backdrop_blur_px=16.0
                    )
                }"""
    content_norm = content_norm.replace(old_bento_surf, new_bento_surf)

    # Paradigm 7: NEO_BRUTALIST (offset duro 4px negro, bordes 3px, saturación pura)
    old_neo_block = """    # ========================================================================
        # 7. NEO BRUTALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.NEO_BRUTALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.99, 0.01, 90.0), hex_value="#FFFDF8", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="on_surface", wcag_contrast_on_surface=17.2),
                    "primary": ColorToken(name="primary", oklch=(0.65, 0.26, 355.0), hex_value="#FF4081", role="primary", wcag_contrast_on_surface=5.8),
                    "border": ColorToken(name="border", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="border")
                },
                shadows={"hard_pop": ShadowToken(name="hard_pop", elevation_level=3, x=5, y=5, blur=0, spread=0, color="oklch(0.05 0 0)")},
                surfaces={"blocky": SurfaceToken(name="blocky", border_width_px=3.0, border_radius_scale={"none": 0.0})}
            )"""

    new_neo_block = """    # ========================================================================
        # 7. NEO BRUTALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.NEO_BRUTALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.99, 0.01, 90.0), hex_value="#FFFDF8", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="on_surface", wcag_contrast_on_surface=17.2),
                    "primary": ColorToken(name="primary", oklch=(0.65, 0.26, 355.0), hex_value="#FF4081", role="primary", wcag_contrast_on_surface=5.8),
                    "border": ColorToken(name="border", oklch=(0.05, 0.0, 0.0), hex_value="#000000", role="border")
                },
                shadows={"hard_pop": ShadowToken(name="hard_pop", elevation_level=3, x=4, y=4, blur=0, spread=0, color="#000000")},
                surfaces={"blocky": SurfaceToken(name="blocky", border_width_px=3.0, border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0})}
            )"""
    content_norm = content_norm.replace(normalize(old_neo_block), normalize(new_neo_block))

    # Paradigm 8: ORGANIC_TACTILE (radios asimétricos biomórficos, fibras lino/algodón)
    old_org_surf = 'surfaces={"clay": SurfaceToken(name="clay", border_radius_scale={"pebble": 28.0}, border_width_px=1.5, surface_treatment=SurfaceTreatment.TACTILE_EMBOSS)}'
    new_org_surf = """surfaces={
                    "clay": SurfaceToken(
                        name="clay",
                        border_radius_scale={"none": 0.0, "xs": 8.0, "sm": 14.0, "md": 22.0, "lg": 32.0, "pebble": 28.0, "biomorphic": 36.0, "full": 9999.0},
                        border_width_px=1.5,
                        surface_treatment=SurfaceTreatment.TACTILE_EMBOSS,
                        noise_grain_opacity=0.06
                    )
                }"""
    content_norm = content_norm.replace(old_org_surf, new_org_surf)

    # Paradigm 9: CYBER_TELEMETRY (0px o micro-bisel, CRT scanlines, verde fósforo)
    old_cyber_block = """    # ========================================================================
        # 9. CYBER TELEMETRY
        # ========================================================================
        elif paradigm == AestheticParadigm.CYBER_TELEMETRY:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.10, 0.02, 145.0), hex_value="#020A05", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.88, 0.24, 145.0), hex_value="#00FF66", role="on_surface", wcag_contrast_on_surface=13.5),
                    "primary": ColorToken(name="primary", oklch=(0.78, 0.20, 80.0), hex_value="#FFB000", role="primary", wcag_contrast_on_surface=10.2),
                    "border": ColorToken(name="border", oklch=(0.30, 0.10, 145.0), hex_value="#0B381A", role="border")
                },
                surfaces={"phosphor_crt": SurfaceToken(name="phosphor_crt", surface_treatment=SurfaceTreatment.SCANLINE, border_width_px=1.0)}
            )
            spatial = SpatialGrammar(archetype=SpatialArchetype.TELEMETRY_DASHBOARD)"""

    new_cyber_block = """    # ========================================================================
        # 9. CYBER TELEMETRY
        # ========================================================================
        elif paradigm == AestheticParadigm.CYBER_TELEMETRY:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.10, 0.02, 145.0), hex_value="#020A05", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.88, 0.24, 145.0), hex_value="#00FF66", role="on_surface", wcag_contrast_on_surface=13.5),
                    "primary": ColorToken(name="primary", oklch=(0.78, 0.20, 80.0), hex_value="#FFB000", role="primary", wcag_contrast_on_surface=10.2),
                    "border": ColorToken(name="border", oklch=(0.30, 0.10, 145.0), hex_value="#0B381A", role="border")
                },
                shadows={"hud_glow": ShadowToken(name="hud_glow", elevation_level=1, x=0, y=0, blur=8, spread=1, color="oklch(0.88 0.24 145 / 0.35)")},
                surfaces={
                    "phosphor_crt": SurfaceToken(
                        name="phosphor_crt",
                        surface_treatment=SurfaceTreatment.SCANLINE,
                        border_width_px=1.0,
                        border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0}
                    )
                }
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.TELEMETRY_DASHBOARD,
                bounds=SpatialBounds(columns=12, fluid_gutter_min=4.0, fluid_gutter_max=8.0)
            )"""
    content_norm = content_norm.replace(normalize(old_cyber_block), normalize(new_cyber_block))

    # Paradigm 10: RETRO_FUTURIST / RETRO_FUTURISM (cápsula arcade o CRT 8px, switches, bloom cálido)
    old_retro_block = """    # ========================================================================
        # 10. RETRO FUTURIST
        # ========================================================================
        elif paradigm == AestheticParadigm.RETRO_FUTURIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.18, 0.10, 310.0), hex_value="#241442", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.05, 70.0), hex_value="#FFF0E6", role="on_surface", wcag_contrast_on_surface=12.5),
                    "primary": ColorToken(name="primary", oklch=(0.68, 0.22, 40.0), hex_value="#FF5E36", role="primary", wcag_contrast_on_surface=6.8),
                    "border": ColorToken(name="border", oklch=(0.40, 0.18, 330.0), hex_value="#661C66", role="border")
                },
                surfaces={"synth": SurfaceToken(name="synth", border_radius_scale={"panel": 12.0}, border_width_px=2.0)}
            )"""

    new_retro_block = """    # ========================================================================
        # 10. RETRO FUTURIST / RETRO FUTURISM
        # ========================================================================
        elif paradigm in (AestheticParadigm.RETRO_FUTURIST, AestheticParadigm.RETRO_FUTURISM):
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.18, 0.10, 310.0), hex_value="#241442", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.92, 0.05, 70.0), hex_value="#FFF0E6", role="on_surface", wcag_contrast_on_surface=12.5),
                    "primary": ColorToken(name="primary", oklch=(0.68, 0.22, 40.0), hex_value="#FF5E36", role="primary", wcag_contrast_on_surface=6.8),
                    "border": ColorToken(name="border", oklch=(0.40, 0.18, 330.0), hex_value="#661C66", role="border")
                },
                shadows={
                    "warm_bloom": ShadowToken(name="warm_bloom", elevation_level=3, x=0, y=4, blur=16, spread=2, color="oklch(0.68 0.22 40 / 0.4)")
                },
                surfaces={
                    "synth": SurfaceToken(
                        name="synth",
                        border_radius_scale={"none": 0.0, "xs": 4.0, "sm": 8.0, "md": 8.0, "lg": 16.0, "arcade": 8.0, "panel": 8.0, "full": 9999.0},
                        border_width_px=2.0
                    )
                }
            )"""
    content_norm = content_norm.replace(normalize(old_retro_block), normalize(new_retro_block))

    # Paradigm 11: DOCUMENT_MINIMALIST (0px en contenedores, columna axial limpia, cero tarjetas vacías)
    old_doc_block = """    # ========================================================================
        # 11. DOCUMENT MINIMALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.DOCUMENT_MINIMALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(1.0, 0.0, 0.0), hex_value="#FFFFFF", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.10, 0.0, 0.0), hex_value="#1A1A1A", role="on_surface", wcag_contrast_on_surface=18.5),
                    "primary": ColorToken(name="primary", oklch=(0.50, 0.16, 255.0), hex_value="#0969DA", role="primary", wcag_contrast_on_surface=4.8),
                    "border": ColorToken(name="border", oklch=(0.85, 0.0, 0.0), hex_value="#D0D7DE", role="border")
                },
                surfaces={"doc": SurfaceToken(name="doc", border_width_px=1.0)}
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.HERO_MONOLITH,
                bounds=SpatialBounds(max_container_width=740.0)
            )"""

    new_doc_block = """    # ========================================================================
        # 11. DOCUMENT MINIMALIST
        # ========================================================================
        elif paradigm == AestheticParadigm.DOCUMENT_MINIMALIST:
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(1.0, 0.0, 0.0), hex_value="#FFFFFF", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.10, 0.0, 0.0), hex_value="#1A1A1A", role="on_surface", wcag_contrast_on_surface=18.5),
                    "primary": ColorToken(name="primary", oklch=(0.50, 0.16, 255.0), hex_value="#0969DA", role="primary", wcag_contrast_on_surface=4.8),
                    "border": ColorToken(name="border", oklch=(0.85, 0.0, 0.0), hex_value="#D0D7DE", role="border")
                },
                shadows={"flat": ShadowToken(name="flat", elevation_level=0, x=0, y=0, blur=0, spread=0, color="transparent")},
                surfaces={
                    "doc": SurfaceToken(
                        name="doc",
                        border_width_px=1.0,
                        border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0}
                    )
                }
            )
            spatial = SpatialGrammar(
                archetype=SpatialArchetype.HERO_MONOLITH,
                bounds=SpatialBounds(max_container_width=740.0, columns=12)
            )"""
    content_norm = content_norm.replace(normalize(old_doc_block), normalize(new_doc_block))

    # Paradigm 12: DECONSTRUCTIVIST (clip-path fragmentado, ángulos rotados no-euclidianos)
    old_decon_block = """    # ========================================================================
        # 12. DECONSTRUCTIVIST
        # ========================================================================
        else:  # AestheticParadigm.DECONSTRUCTIVIST
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.10, 0.005, 0.0), hex_value="#0A0A0A", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.98, 0.0, 0.0), hex_value="#FFFFFF", role="on_surface", wcag_contrast_on_surface=19.2),
                    "primary": ColorToken(name="primary", oklch=(0.60, 0.30, 20.0), hex_value="#FF0055", role="primary", wcag_contrast_on_surface=5.7),
                    "border": ColorToken(name="border", oklch=(0.40, 0.01, 0.0), hex_value="#333333", role="border")
                },
                surfaces={"fragment": SurfaceToken(name="fragment", border_width_px=2.0)}
            )"""

    new_decon_block = """    # ========================================================================
        # 12. DECONSTRUCTIVIST
        # ========================================================================
        else:  # AestheticParadigm.DECONSTRUCTIVIST
            tokens = PerceptualTokens(
                colors={
                    "surface": ColorToken(name="surface", oklch=(0.10, 0.005, 0.0), hex_value="#0A0A0A", role="surface"),
                    "on_surface": ColorToken(name="on_surface", oklch=(0.98, 0.0, 0.0), hex_value="#FFFFFF", role="on_surface", wcag_contrast_on_surface=19.2),
                    "primary": ColorToken(name="primary", oklch=(0.60, 0.30, 20.0), hex_value="#FF0055", role="primary", wcag_contrast_on_surface=5.7),
                    "border": ColorToken(name="border", oklch=(0.40, 0.01, 0.0), hex_value="#333333", role="border")
                },
                shadows={"shattered": ShadowToken(name="shattered", elevation_level=4, x=-8, y=12, blur=0, spread=0, color="oklch(0.15 0 0 / 0.85)")},
                surfaces={
                    "fragment": SurfaceToken(
                        name="fragment",
                        border_width_px=2.0,
                        border_radius_scale={"none": 0.0, "xs": 0.0, "sm": 0.0, "md": 0.0, "lg": 0.0, "full": 0.0}
                    )
                }
            )"""
    content_norm = content_norm.replace(normalize(old_decon_block), normalize(new_decon_block))

    # Guardar de vuelta
    ir_path.write_text(content_norm, encoding="utf-8")
    print("aleph_design_ir.py actualizado exitosamente!")
    return ir_path


if __name__ == "__main__":
    apply_design_ir_ch2_enrichments()
