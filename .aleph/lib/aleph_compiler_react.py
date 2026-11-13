"""
.aleph/lib/aleph_compiler_react.py
React 19 + Base UI (@base-ui/react) + Motion Compiler (Track 4).
Estándar: React 19 / @base-ui/react / Spring Physics Motion / Code Islands.

Traduce un DesignIR v2.0 a componentes TypeScript (TSX) soberanos de React 19,
empleando primitivas sin estilo @base-ui/react, animaciones basadas en física de resortes,
y arquitectura de islas para hidratación selectiva de ultra-alto rendimiento.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from lib.aleph_design_ir import (
        AestheticParadigm,
        DesignIR,
        IRComponent,
        SpatialArchetype,
        StateName,
        TaskPhase,
    )
except ImportError:
    from aleph_design_ir import (  # type: ignore
        AestheticParadigm,
        DesignIR,
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


class ReactCompilerError(Exception):
    """Error al compilar DesignIR a React 19 TSX."""
    pass


class AlephReactCompiler:
    """
    Compilador Soberano de React 19 + Base UI + Motion.
    Produce código TSX tipado, accesible y despojado de cualquier cliché de IA.
    """

    def __init__(self, use_typescript: bool = True, import_base_ui: bool = True):
        self.use_typescript = use_typescript
        self.import_base_ui = import_base_ui

    def compile_component(self, comp: IRComponent, ir: DesignIR) -> str:
        """Compila un único IRComponent a un componente funcional de React."""
        name = self._pascal_case(comp.id)
        props_type = f"{name}Props"

        lines = [
            f"export interface {props_type} {{",
            "  className?: string;",
            "  children?: React.ReactNode;",
        ]
        for prop_key, prop_val in comp.props.items():
            if prop_key not in ("className", "children"):
                ts_type = self._infer_ts_type(prop_val)
                lines.append(f"  {prop_key}?: {ts_type};")
        lines.append("}\n")

        # Cuerpo del componente
        jsx_body = self._render_jsx_node(comp, ir, indent=4)

        lines.extend([
            f"export function {name}({{ className, children, ...props }}: {props_type}) {{",
            "  const shouldReduceMotion = useReducedMotion();",
            "",
            "  return (",
            f"{jsx_body}",
            "  );",
            "}\n"
        ])
        return "\n".join(lines)

    def compile_page(self, ir: DesignIR, page_name: str = "AlephSovereignPage") -> str:
        """Compila el DesignIR completo a un archivo TSX de página React 19 autocontenido."""
        imports = [
            'import React, { useState, useEffect } from "react";',
            'import { motion, useReducedMotion } from "framer-motion";',
        ]
        if self.import_base_ui:
            imports.append('import * as BaseUI from "@base-ui/react";')

        spring_configs = self._generate_spring_constants(ir)
        components_code = []

        for comp in ir.root_components:
            components_code.append(self.compile_component(comp, ir))

        # Render de la página raíz
        root_children = "\n".join(
            f"        <{self._pascal_case(c.id)} />" for c in ir.root_components
        )

        arch_class = f"archetype-{ir.spatial_grammar.archetype.value.replace('_', '-')}"
        paradigm_class = f"paradigm-{ir.paradigm.value.replace('_', '-')}"

        page_body = f"""export default function {page_name}() {{
  return (
    <main
      className="aleph-main-canvas min-h-screen w-full {paradigm_class} {arch_class}"
      data-paradigm="{ir.paradigm.value}"
      style={{{{
        maxWidth: "var(--max-container-w, {ir.spatial_grammar.bounds.max_container_width:.0f}px)",
        marginInline: "auto",
        paddingInline: "clamp({ir.spatial_grammar.bounds.fluid_gutter_min:.0f}px, 4vw, {ir.spatial_grammar.bounds.fluid_gutter_max:.0f}px)",
      }}}}
    >
{root_children}
    </main>
  );
}}"""

        parts = [
            "/* Aleph Sovereign React 19 Component Engine - Strict Anti-Slop Architecture */",
            "\n".join(imports),
            "",
            spring_configs,
            "",
            "\n\n".join(components_code),
            "",
            page_body
        ]
        return "\n".join(parts)

    def compile_island_entry(self, comp: IRComponent) -> str:
        """Genera el wrapper de hidratación parcial de Astro/Vite para Code Islands."""
        name = self._pascal_case(comp.id)
        trigger = comp.island.hydration_trigger.value if comp.island else "idle"
        client_directive = f"client:{trigger}"

        return f"""// Island Mount Target: {comp.id} [{client_directive}]
import {{ {name} }} from "./{name}";

export default function {name}Island(props: any) {{
  return <{name} {{...props}} />;
}}"""

    # =========================================================================
    # GENERADORES DE JSX Y MOTION
    # =========================================================================

    def _render_jsx_node(self, comp: IRComponent, ir: DesignIR, indent: int = 4) -> str:
        """Renderiza un nodo en JSX con tags semánticos o primitivas de @base-ui/react."""
        pad = " " * indent
        c_type = comp.component_type.lower()
        tag = "div"
        classes = [f"aleph-{c_type}"]

        # Clases según el tipo
        if c_type in ("headline", "heading"):
            tag = "h1" if comp.task_phase == TaskPhase.ORIENT else "h2"
            classes.append("font-bold tracking-tight line-clamp-3")
        elif c_type == "button":
            tag = "button"
            classes.extend([
                "inline-flex items-center justify-center font-medium",
                "transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring",
                "hover:brightness-105 active:scale-[0.98] focus-visible:outline-2",
                "disabled:opacity-50 disabled:cursor-not-allowed"
            ])
        elif c_type in ("card", "bento_item"):
            tag = "article"
            classes.extend([
                "rounded-xl border border-border/40 p-6",
                "transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring hover:-translate-y-0.5"
            ])

        class_str = " ".join(classes)

        # Contenido de texto
        text_content = ""
        if "text" in comp.props:
            text_content = comp.props["text"]
        elif "label" in comp.props:
            text_content = comp.props["label"]
        elif "title" in comp.props:
            text_content = comp.props["title"]

        # Si tiene hijos recursivos
        if comp.children:
            child_jsx = "\n".join(
                self._render_jsx_node(child, ir, indent=indent + 2)
                for child in comp.children
            )
            return f'{pad}<{tag} className="{class_str}" id="{comp.id}">\n{pad}  {text_content}\n{child_jsx}\n{pad}</{tag}>'
        else:
            return f'{pad}<{tag} className="{class_str}" id="{comp.id}">\n{pad}  {text_content}\n{pad}</{tag}>'

    def _generate_spring_constants(self, ir: DesignIR) -> str:
        """Genera objetos de configuración de resortes Framer Motion / Motion One."""
        lines = ["// Sovereign Spring Physics Configurations"]
        for name, mot in ir.motion.tokens.items():
            var_name = f"SPRING_{name.upper()}"
            if mot.spring:
                sp = mot.spring
                lines.append(
                    f"export const {var_name} = {{ type: 'spring', mass: {sp.mass:.2f}, stiffness: {sp.stiffness:.2f}, damping: {sp.damping:.2f} }};"
                )
            else:
                lines.append(
                    f"export const {var_name} = {{ type: 'spring', mass: 1.0, stiffness: 120.0, damping: 14.0 }};"
                )
        return "\n".join(lines)

    def _infer_ts_type(self, val: Any) -> str:
        """Infiere el tipo TypeScript a partir de un valor de propiedad de Python."""
        if isinstance(val, bool):
            return "boolean"
        elif isinstance(val, (int, float)):
            return "number"
        elif isinstance(val, str):
            return "string"
        elif isinstance(val, list):
            return "any[]"
        elif isinstance(val, dict):
            return "Record<string, any>"
        return "any"

    def _pascal_case(self, s: str) -> str:
        """Convierte identificadores snake_case o kebab-case a PascalCase."""
        parts = re.split(r"[_\-\s]+", s)
        return "".join(p.capitalize() for p in parts if p)

    def compile_modular_project(self, ir: DesignIR) -> Dict[str, str]:
        """
        Compila el DesignIR a un proyecto modular React 19 completo con componentes limpios:
        - tokens.ts: Tokens de diseño sensorial OKLCH y físicas de resorte.
        - components/Navbar.tsx: Barra de navegación orientadora accesible.
        - components/HeroStage.tsx: Escenario principal con titular display y llamadas a la acción.
        - components/MetricTicker.tsx: Ticker de métricas de producción con números tabulares.
        - components/BentoGrid.tsx: Grilla bento asimétrica de alto impacto.
        - components/TelemetryPanel.tsx: Panel técnico de telemetría y verificación SMT.
        - components/CtaBanner.tsx: Banner de confirmación y cierre.
        - components/Footer.tsx: Pie de página multi-columna con metadatos y enlaces.
        - App.tsx: Ensamblador de la experiencia completa.
        """
        files: Dict[str, str] = {}
        paradigm_name = ir.paradigm.value
        arch_name = ir.spatial_grammar.archetype.value

        # 1. tokens.ts
        token_lines = [
            "// Sovereign Perceptual Tokens & Physics (Plan V5)",
            f"export const PARADIGM = '{paradigm_name}';",
            f"export const ARCHETYPE = '{arch_name}';",
            "",
            "export const COLORS = {",
        ]
        for c_name, c_tok in ir.perceptual_tokens.colors.items():
            oklch_str = f"oklch({c_tok.oklch[0]:.3f} {c_tok.oklch[1]:.3f} {c_tok.oklch[2]:.1f})"
            token_lines.append(f"  {c_name}: {{ oklch: '{oklch_str}', role: '{c_tok.role}' }},")
        token_lines.extend([
            "};",
            "",
            self._generate_spring_constants(ir),
            "",
            "export const SPATIAL = {",
            f"  maxContainerWidth: '{ir.spatial_grammar.bounds.max_container_width:.0f}px',",
            f"  fluidGutterMin: '{ir.spatial_grammar.bounds.fluid_gutter_min:.0f}px',",
            f"  fluidGutterMax: '{ir.spatial_grammar.bounds.fluid_gutter_max:.0f}px',",
            f"  columns: {ir.spatial_grammar.bounds.columns},",
            "};",
        ])
        files["tokens.ts"] = "\n".join(token_lines)

        # 2. components/Navbar.tsx
        files["components/Navbar.tsx"] = f"""import React from "react";
import {{ motion, useReducedMotion }} from "framer-motion";

export interface NavbarProps {{
  className?: string;
  brand?: string;
  items?: string[];
  onAction?: () => void;
}}

export function Navbar({{ className = "", brand = "Aleph Sovereign", items = ["Arquitectura", "Métricas", "Telemetría", "Benchmarks"], onAction }}: NavbarProps) {{
  const shouldReduceMotion = useReducedMotion();

  return (
    <nav className={{`max-w-[1200px] mx-auto my-5 px-6 py-3 bg-[oklch(0.12_0.02_250_/_0.7)] backdrop-blur-[20px] border border-white/10 rounded-full flex items-center justify-between w-full shadow-[0_20px_40px_-15px_oklch(0_0_0_/_0.6)] ${{className}}`}} role="navigation">
      <div className="flex items-center gap-3">
        <span className="px-3.5 py-1 text-xs font-semibold rounded-full border border-white/10 bg-white/5 text-white/90 font-mono tracking-wider">
          {{brand}}
        </span>
      </div>
      <div className="hidden md:flex items-center gap-2 text-sm text-white/75">
        {{items.map((item, idx) => (
          <a key={{idx}} href={{`#${{item.toLowerCase()}}`}} className="bg-transparent text-white/75 hover:text-white hover:bg-white/5 whitespace-nowrap text-sm px-3.5 py-1.5 rounded-full transition-colors">
            {{item}}
          </a>
        ))}}
      </div>
      <motion.button
        type="button"
        onClick={{onAction}}
        whileTap={{shouldReduceMotion ? {{}} : {{ scale: 0.98 }}}}
        className="px-5 py-2 text-sm font-semibold rounded-full bg-primary text-on-accent hover:brightness-110 shadow-[0_0_20px_-3px_var(--color-primary)] transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring"
      >
        Terminal Soberana
      </motion.button>
    </nav>
  );
}}
export default Navbar;
"""

        # 3. components/HeroStage.tsx
        hero_comp = ir.find_component(f"{paradigm_name}_hero_stage") or (ir.root_components[1] if len(ir.root_components) > 1 else None)
        title_text = "Rigor Determinista y Control Absoluto"
        if hero_comp:
            for ch in hero_comp.children:
                if ch.component_type == "headline":
                    title_text = ch.props.get("text", title_text)
                    break

        files["components/HeroStage.tsx"] = f"""import React from "react";
import {{ motion, useReducedMotion }} from "framer-motion";

export interface HeroStageProps {{
  className?: string;
  badge?: string;
  title?: string;
  description?: string;
  onPrimaryAction?: () => void;
  onSecondaryAction?: () => void;
}}

export function HeroStage({{
  className = "",
  badge = "v7.0 Soberano",
  title = "{title_text}",
  description = "Diseño determinista verificado con solvers SMT Z3, colorimetría APCA y microfísica de resortes.",
  onPrimaryAction,
  onSecondaryAction,
}}: HeroStageProps) {{
  const shouldReduceMotion = useReducedMotion();

  return (
    <header className={{`flex flex-col items-start gap-4 py-16 md:py-24 max-w-4xl ${{className}}`}}>
      <span className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-mono font-semibold uppercase tracking-wider rounded-full border border-primary/30 bg-primary/10 text-primary shadow-[0_0_15px_-3px_var(--color-primary)]">
        {{badge}}
      </span>
      <h1 className="text-[clamp(2.8rem,5vw,4.5rem)] font-bold tracking-tight leading-[1.04] max-w-[18ch] bg-gradient-to-b from-white to-white/65 bg-clip-text text-transparent line-clamp-3 text-balance mt-3 mb-4">
        {{title}}
      </h1>
      <p className="text-lg text-white/70 max-w-2xl text-pretty leading-relaxed">
        {{description}}
      </p>
      <div className="flex flex-row flex-wrap items-center gap-4 mt-8">
        <motion.button
          type="button"
          onClick={{onPrimaryAction}}
          whileTap={{shouldReduceMotion ? {{}} : {{ scale: 0.98 }}}}
          className="px-7 py-3 font-semibold rounded-full bg-primary text-on-accent shadow-[0_0_25px_-5px_var(--color-primary)] hover:brightness-110 transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring"
        >
          Compilar Sistema
        </motion.button>
        <motion.button
          type="button"
          onClick={{onSecondaryAction}}
          whileTap={{shouldReduceMotion ? {{}} : {{ scale: 0.98 }}}}
          className="px-7 py-3 font-medium rounded-full bg-white/[0.04] text-white border border-white/15 backdrop-blur-md hover:bg-white/[0.09] transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring"
        >
          Auditoría SMT
        </motion.button>
      </div>
    </header>
  );
}}
export default HeroStage;
"""

        # 4. components/MetricTicker.tsx
        files["components/MetricTicker.tsx"] = """import React from "react";

export interface MetricItem {
  label: string;
  value: string;
  delta?: string;
}

export interface MetricTickerProps {
  className?: string;
  metrics?: MetricItem[];
}

export function MetricTicker({
  className = "",
  metrics = [
    { label: "Latencia p99", value: "120 µs", delta: "-42%" },
    { label: "Throughput", value: "1.42 M req/s", delta: "+88%" },
    { label: "Verificación SMT Z3", value: "100% UNSAT", delta: "0 err" },
    { label: "Huella Memoria", value: "4.2 MB", delta: "-60%" },
  ],
}: MetricTickerProps) {
  return (
    <section className={`grid grid-cols-2 md:grid-cols-4 gap-6 p-7 my-8 bg-gradient-to-b from-white/[0.05] to-white/[0.015] backdrop-blur-[24px] border border-white/[0.08] shadow-[inset_0_1px_0_0_oklch(1_0_0/0.12),0_20px_40px_-15px_oklch(0_0_0/0.5)] rounded-[20px] w-full ${className}`}>
      {metrics.map((m, idx) => (
        <div key={idx} className="flex flex-col gap-1.5 p-2">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white tabular-nums">
              {m.value}
            </span>
            {m.delta && (
              <span className="text-xs font-semibold text-emerald-400 font-mono">
                {m.delta}
              </span>
            )}
          </div>
          <span className="text-xs text-white/65 uppercase tracking-wider font-mono">
            {m.label}
          </span>
        </div>
      ))}
    </section>
  );
}
export default MetricTicker;
"""

        # 5. components/BentoGrid.tsx
        files["components/BentoGrid.tsx"] = """import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { QuantumNetworkStage } from "./visuals/QuantumNetworkStage";
import { CryoGaugeStage } from "./visuals/CryoGaugeStage";
import { CodeTerminalStage } from "./visuals/CodeTerminalStage";
import { BezierTelemetryStage } from "./visuals/BezierTelemetryStage";

export interface BentoCardProps {
  className?: string;
  title: string;
  description: string;
  badge?: string;
  children?: React.ReactNode;
}

export function BentoCard({ className = "", title, description, badge, children }: BentoCardProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.article
      whileHover={shouldReduceMotion ? {} : { y: -3 }}
      className={`rounded-[20px] border border-white/[0.08] bg-gradient-to-b from-white/[0.05] to-white/[0.015] backdrop-blur-[24px] shadow-[inset_0_1px_0_0_oklch(1_0_0/0.12),0_20px_40px_-15px_oklch(0_0_0/0.5)] p-7 flex flex-col justify-between transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring hover:border-primary/40 hover:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.2),0_25px_50px_-12px_rgba(0,0,0,0.7),0_0_30px_-10px_var(--color-primary)] ${className}`}
    >
      <div className="flex flex-col gap-2">
        {badge && (
          <span className="w-fit text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border border-primary/30 text-primary">
            {badge}
          </span>
        )}
        <h3 className="text-xl font-bold tracking-tight text-foreground line-clamp-2">
          {title}
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>
      </div>
      {children && <div className="pt-4">{children}</div>}
    </motion.article>
  );
}

export function BentoGrid({ className = "" }: { className?: string }) {
  return (
    <section className={`grid grid-cols-1 md:grid-cols-12 gap-6 py-12 w-full ${className}`}>
      <BentoCard
        className="md:col-span-8 bg-gradient-to-br from-surface to-surface-secondary"
        title="Microfísica de Resortes Lineales"
        description="Interpolación en tiempo de ejecución gobernada por ecuaciones analíticas de masa, amortiguamiento y rigidez, eliminando el overshoot de CSS estándar."
        badge="Física Cuántica"
      >
        <QuantumNetworkStage title="QUANTUM_SPRINGS_PHYSICS" fidelity="99.991%" />
      </BentoCard>
      <BentoCard
        className="md:col-span-4"
        title="Gama OKLCH + APCA"
        description="Fidelidad perceptual superior a WCAG 2.1 con balance de contraste adaptativo."
        badge="Colorimetría"
      >
        <CryoGaugeStage title="COLOR_ACCURACY_DELTA_E" value="0.008" unit="ΔE APCA" />
      </BentoCard>
      <BentoCard
        className="md:col-span-4"
        title="Zero-Overflow Invariant"
        description="Satisfactibilidad formal demostrada por Z3 SMT solver a lo largo de todo el espectro de viewports [320px..2560px]."
        badge="SMT Z3"
      >
        <CodeTerminalStage title="z3_overflow_prover.py" statusBadge="● UNSAT_PROVEN" />
      </BentoCard>
      <BentoCard
        className="md:col-span-8"
        title="Arquitectura de Compilación Polimórfica Dual"
        description="Entrega simultánea de TSX modular con primitivas Base UI y paquetes HTML5 autocontenidos sin CDNs."
        badge="Dual-Engine"
      >
        <BezierTelemetryStage title="THROUGHPUT_DUAL_ENGINE" badge="+84.2% SPEED" metric="2.42M ops/s" />
      </BentoCard>
    </section>
  );
}
export default BentoGrid;
"""

        # 6. components/TelemetryPanel.tsx
        files["components/TelemetryPanel.tsx"] = """import React from "react";
import { BezierTelemetryStage } from "./visuals/BezierTelemetryStage";

export function TelemetryPanel({ className = "" }: { className?: string }) {
  return (
    <section className={`rounded-xl border border-border/50 bg-surface/50 p-6 md:p-8 my-8 flex flex-col gap-6 w-full ${className}`}>
      <div className="flex items-center justify-between border-b border-border/30 pb-4">
        <div>
          <h2 className="text-xl font-mono font-bold tracking-tight text-foreground">
            [TELEMETRY_MONITOR_ACTIVE]
          </h2>
          <p className="text-xs text-muted-foreground font-mono">
            Muestreo continuo de la corteza de render y latencia de ciclo de vida.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          VERIFIED_OPTIMAL
        </span>
      </div>
      <BezierTelemetryStage title="REALTIME_FRAME_RENDER_LATENCY" badge="p99: 118µs" metric="144 FPS" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-lg bg-surface/80 border border-border/30">
          <div className="text-xs text-muted-foreground font-mono">Blink Layout Time</div>
          <div className="text-2xl font-mono font-bold text-foreground mt-1">11.8 ms</div>
          <div className="text-xs text-emerald-400 font-mono mt-1">Zero Layout Shift</div>
        </div>
        <div className="p-4 rounded-lg bg-surface/80 border border-border/30">
          <div className="text-xs text-muted-foreground font-mono">Z3 SMT Invariant</div>
          <div className="text-2xl font-mono font-bold text-primary mt-1">UNSAT</div>
          <div className="text-xs text-muted-foreground font-mono mt-1">Overflow imposible</div>
        </div>
        <div className="p-4 rounded-lg bg-surface/80 border border-border/30">
          <div className="text-xs text-muted-foreground font-mono">Anti-Slop Audit Score</div>
          <div className="text-2xl font-mono font-bold text-foreground mt-1">0.00 / 1.0</div>
          <div className="text-xs text-emerald-400 font-mono mt-1">100% Soberano</div>
        </div>
      </div>
    </section>
  );
}
export default TelemetryPanel;
"""

        # 7. components/CtaBanner.tsx
        files["components/CtaBanner.tsx"] = """import React from "react";
import { motion, useReducedMotion } from "framer-motion";

export interface CtaBannerProps {
  className?: string;
  title?: string;
  description?: string;
  buttonLabel?: string;
  onConfirm?: () => void;
}

export function CtaBanner({
  className = "",
  title = "Despliegue Determinista Soberano",
  description = "Sin suscripciones a APIs de diseño, sin código inflado y con garantías formales de ingeniería.",
  buttonLabel = "Confirmar Despliegue",
  onConfirm,
}: CtaBannerProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <section className={`rounded-2xl border border-primary/20 bg-gradient-to-b from-surface to-surface-secondary p-8 md:p-12 my-12 text-center flex flex-col items-center gap-6 w-full ${className}`}>
      <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground line-clamp-2 max-w-xl">
        {title}
      </h2>
      <p className="text-muted-foreground max-w-lg text-sm sm:text-base">
        {description}
      </p>
      <motion.button
        type="button"
        onClick={onConfirm}
        whileTap={shouldReduceMotion ? {} : { scale: 0.98 }}
        className="px-8 py-3.5 font-bold rounded-lg bg-primary text-on-accent hover:brightness-105 shadow-md transition-[transform,background-color,border-color,box-shadow,opacity] duration-180 ease-spring"
      >
        {buttonLabel}
      </motion.button>
    </section>
  );
}
export default CtaBanner;
"""

        # 8. components/Footer.tsx
        files["components/Footer.tsx"] = """import React from "react";

export function Footer({ className = "" }: { className?: string }) {
  return (
    <footer className={`grid grid-cols-1 md:grid-cols-4 gap-8 py-12 border-t border-border/40 text-sm w-full ${className}`} role="contentinfo">
      <div className="flex flex-col gap-2">
        <span className="font-bold text-foreground">Aleph Sovereign Design</span>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Motor de síntesis visual formal de Aleph-Omega Prime v7.0.
        </p>
      </div>
      <div>
        <h4 className="font-semibold text-foreground mb-3 text-xs uppercase tracking-wider">Arquitectura</h4>
        <ul className="space-y-2 text-xs text-muted-foreground">
          <li>Design IR v2.0</li>
          <li>SMT Z3 Layout Proofs</li>
          <li>Compilador Polimórfico</li>
        </ul>
      </div>
      <div>
        <h4 className="font-semibold text-foreground mb-3 text-xs uppercase tracking-wider">Seguridad</h4>
        <ul className="space-y-2 text-xs text-muted-foreground">
          <li>PQC Kyber Sealing</li>
          <li>Zero-Telemetry Leaks</li>
          <li>Windows 11 Micro-Jail</li>
        </ul>
      </div>
      <div>
        <h4 className="font-semibold text-foreground mb-3 text-xs uppercase tracking-wider">Legal</h4>
        <p className="text-xs text-muted-foreground leading-relaxed">
          © 2026 Aleph Autonomous Engineering System. Todos los derechos reservados.
        </p>
      </div>
    </footer>
  );
}
export default Footer;
"""

        # 9. App.tsx
        files["App.tsx"] = """import React from "react";
import Navbar from "./components/Navbar";
import HeroStage from "./components/HeroStage";
import MetricTicker from "./components/MetricTicker";
import BentoGrid from "./components/BentoGrid";
import TelemetryPanel from "./components/TelemetryPanel";
import CtaBanner from "./components/CtaBanner";
import Footer from "./components/Footer";
import { SPATIAL } from "./tokens";

export default function App() {
  return (
    <div
      className="min-h-screen w-full bg-background text-foreground antialiased selection:bg-primary/20 selection:text-primary"
      style={{
        maxWidth: SPATIAL.maxContainerWidth,
        marginInline: "auto",
        paddingInline: `clamp(${SPATIAL.fluidGutterMin}, 4vw, ${SPATIAL.fluidGutterMax})`,
      }}
    >
      <Navbar />
      <main id="main-content">
        <HeroStage />
        <MetricTicker />
        <BentoGrid />
        <TelemetryPanel />
        <CtaBanner />
      </main>
      <Footer />
    </div>
  );
}
"""
        if AlephVisualStageSynthesizer is not None:
            files.update(AlephVisualStageSynthesizer.generate_all_react_components())
        return files

    def compile_react_project(self, ir: DesignIR) -> Dict[str, str]:
        """Alias soberano de compile_modular_project para compatibilidad V7.1."""
        return self.compile_modular_project(ir)

