# -*- coding: utf-8 -*-
"""
ALEPH ELICITATION & DECISION GOVERNANCE ENGINE (v5)
Módulo Soberano de Alineación de Intención, Detección Discovery-First y Matriz Bezos
Ruta: C:\\Users\\Lucas cardozo\\.aleph\\lib\\v5_human_elicitation.py
Doctrina: EL DEMIURGO - 100% Verificación, Primeros Principios, Cero Sycophancy
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Soporte para tomllib (Python 3.11+) con fallback seguro
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


# ============================================================================
# 1. MODELOS DE DATOS & ONTOLOGÍA DE DECISIÓN
# ============================================================================

class DecisionType(Enum):
    TYPE_1_IRREVERSIBLE = "TYPE_1_IRREVERSIBLE"   # One-way door: Requiere parada y entrevista obligatoria
    TYPE_2_REVERSIBLE   = "TYPE_2_REVERSIBLE"     # Two-way door: Ejecución autónoma inmediata


class DecisionDomain(Enum):
    DATABASE_SCHEMA     = "DATABASE_SCHEMA"
    SECURITY_AUTH       = "SECURITY_AUTH"
    API_CONTRACT        = "API_CONTRACT"
    DEPENDENCY          = "DEPENDENCY"
    INTERNAL_REFACTOR   = "INTERNAL_REFACTOR"
    TESTING             = "TESTING"
    CONFIGURATION       = "CONFIGURATION"
    PRODUCTION_DEPLOY   = "PRODUCTION_DEPLOY"
    FINANCIAL_RESOURCE  = "FINANCIAL_RESOURCE"
    EXTERNAL_NETWORK    = "EXTERNAL_NETWORK"


@dataclass(frozen=True)
class DecisionContext:
    action_id: str
    description: str
    domain: DecisionDomain
    is_hard_limit: bool = False
    estimated_p_correct: float = 0.5         # P(correct) ∈ [0, 1]
    estimated_cost_error: float = 10.0        # Costo de error directo si falla
    estimated_cost_rollback: float = 5.0      # Costo de reversión (git revert, backup restore)
    interruption_cost: float = 50.0           # Costo cognitivo de desviar al humano
    opportunity_cost_rate: float = 1.0        # Costo de mantener el pipeline detenido
    affects_external_systems: bool = False    # Network calls, external APIs, destructive side effects


@dataclass
class HighLeverageQuestion:
    id: str
    category: str                             # 'Boundary', 'Munger_Inversion', 'Trade_Off', 'Verification'
    prompt_text: str
    options: List[str]
    recommended_option: str
    rationale: str


@dataclass(frozen=True)
class TDDAtomicTask:
    task_id: str
    phase: str                                # 'RED', 'GREEN', 'REFACTOR'
    target_file: Path
    estimated_minutes: int                    # Debe estar acotado entre 2 y 5 min
    specification: str
    verification_command: str
    expected_exit_code: int = 0


@dataclass
class ElicitationSummary:
    action_id: str
    decision_type: DecisionType
    eve_score: float
    resolved_silently: bool
    resolution_source: Optional[str] = None
    adr_path: Optional[Path] = None
    execution_permitted: bool = False
    details: str = ""


# ============================================================================
# 2. MOTOR DISCOVERY FIRST (Escaneo Silencioso del Entorno)
# ============================================================================

class DiscoveryFirstScanner:
    """
    Inspecciona exhaustivamente el repositorio para resolver preguntas
    antes de invocar cualquier interrupción humana.
    Capas:
    1. Manifiestos y Configuración de Runtime
    2. Grafo de Código y Sintaxis (AST)
    3. Memoria Histórica y ADRs Existentes
    4. Estado Operacional del VCS
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)

    def detect_runtime_stack(self) -> Dict[str, Any]:
        """Detecta lenguajes, frameworks de test, linters y gestores de paquetes configurados."""
        stack_info: Dict[str, Any] = {
            "languages": [],
            "test_frameworks": [],
            "package_managers": [],
            "linters": [],
            "adr_count": 0,
        }

        # 1. Python
        pyproject = self.workspace_root / "pyproject.toml"
        requirements = self.workspace_root / "requirements.txt"
        setup_py = self.workspace_root / "setup.py"
        pytest_ini = self.workspace_root / "pytest.ini"
        conftest_py = self.workspace_root / "conftest.py"

        is_python = (
            pyproject.exists()
            or requirements.exists()
            or setup_py.exists()
            or pytest_ini.exists()
            or conftest_py.exists()
            or any(self.workspace_root.glob("*.py"))
        )
        if is_python:
            if "Python" not in stack_info["languages"]:
                stack_info["languages"].append("Python")
            if "pip" not in stack_info["package_managers"]:
                stack_info["package_managers"].append("pip")

            # Frameworks de test Python
            if pytest_ini.exists() or conftest_py.exists():
                if "pytest" not in stack_info["test_frameworks"]:
                    stack_info["test_frameworks"].append("pytest")
            elif pyproject.exists():
                try:
                    content = pyproject.read_text(encoding="utf-8")
                    if "pytest" in content or "tool.pytest" in content:
                        if "pytest" not in stack_info["test_frameworks"]:
                            stack_info["test_frameworks"].append("pytest")
                except Exception:
                    pass

            # Linters Python
            if (self.workspace_root / "ruff.toml").exists() or (self.workspace_root / ".ruff.toml").exists():
                stack_info["linters"].append("ruff")
            if (self.workspace_root / ".flake8").exists():
                stack_info["linters"].append("flake8")

        # 2. Rust
        cargo_toml = self.workspace_root / "Cargo.toml"
        if cargo_toml.exists():
            stack_info["languages"].append("Rust")
            stack_info["package_managers"].append("cargo")
            stack_info["test_frameworks"].append("cargo-test")
            if (self.workspace_root / "clippy.toml").exists():
                stack_info["linters"].append("clippy")

        # 3. TypeScript / JavaScript
        package_json = self.workspace_root / "package.json"
        if package_json.exists():
            stack_info["languages"].append("TypeScript/JavaScript")
            stack_info["package_managers"].append("npm")
            try:
                pkg_data = json.loads(package_json.read_text(encoding="utf-8"))
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "jest" in deps:
                    stack_info["test_frameworks"].append("jest")
                if "vitest" in deps:
                    stack_info["test_frameworks"].append("vitest")
                if "mocha" in deps:
                    stack_info["test_frameworks"].append("mocha")
                if "eslint" in deps or (self.workspace_root / ".eslintrc.json").exists() or (self.workspace_root / ".eslintrc.js").exists():
                    stack_info["linters"].append("eslint")
            except Exception:
                pass

        # 4. Go
        go_mod = self.workspace_root / "go.mod"
        if go_mod.exists():
            stack_info["languages"].append("Go")
            stack_info["package_managers"].append("go-modules")
            stack_info["test_frameworks"].append("go test")

        # ADR count
        adr_dir = self.workspace_root / "docs" / "adr"
        if adr_dir.exists():
            stack_info["adr_count"] = len(list(adr_dir.glob("*.md")))

        return stack_info

    def query_existing_adrs(self, query_keyword: str) -> List[Path]:
        """Busca decisiones previas tomadas en docs/adr/."""
        adr_dir = self.workspace_root / "docs" / "adr"
        if not adr_dir.exists():
            return []

        matches: List[Path] = []
        pattern = re.compile(re.escape(query_keyword), re.IGNORECASE)
        for adr_file in sorted(adr_dir.glob("*.md")):
            try:
                content = adr_file.read_text(encoding="utf-8")
                if pattern.search(content) or pattern.search(adr_file.name):
                    matches.append(adr_file)
            except Exception:
                continue
        return matches

    def scan_python_ast(self, py_file_path: Path) -> Dict[str, List[str]]:
        """
        Inspección estructural AST (Capa 2):
        Extrae clases, métodos y funciones para evitar preguntar por estructuras existentes.
        """
        target = py_file_path if py_file_path.is_absolute() else self.workspace_root / py_file_path
        if not target.exists():
            return {"classes": [], "functions": []}

        try:
            tree = ast.parse(target.read_text(encoding="utf-8"))
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            return {"classes": classes, "functions": functions}
        except Exception:
            return {"classes": [], "functions": []}

    def scan_vcs_status(self) -> Dict[str, Any]:
        """Inspecciona el estado del repositorio Git (Capa 4)."""
        vcs_info = {"is_git": False, "branch": "", "dirty": False, "untracked": 0}
        git_dir = self.workspace_root / ".git"
        if not git_dir.exists():
            return vcs_info

        vcs_info["is_git"] = True
        try:
            branch_out = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=2,
            )
            if branch_out.returncode == 0:
                vcs_info["branch"] = branch_out.stdout.strip()

            status_out = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=2,
            )
            if status_out.returncode == 0:
                lines = [l for l in status_out.stdout.splitlines() if l.strip()]
                vcs_info["dirty"] = len(lines) > 0
                vcs_info["untracked"] = len([l for l in lines if l.startswith("??")])
        except Exception:
            pass

        return vcs_info

    def can_resolve_silently(self, question_subject: str) -> Optional[str]:
        """
        Determina si una pregunta técnica sobre dependencias, tests, lenguajes o configs
        puede ser respondida de forma determinista leyendo el repo.
        """
        stack = self.detect_runtime_stack()
        q_lower = question_subject.lower()

        # 1. Frameworks de test
        if any(term in q_lower for term in ["test", "framework de prueba", "pruebas", "testing"]):
            if stack["test_frameworks"]:
                return f"Resuelto silenciosamente por Discovery First: Se utiliza {stack['test_frameworks'][0]}"

        # 2. Lenguaje / Stack
        if any(term in q_lower for term in ["lenguaje", "stack", "motor", "language"]):
            if stack["languages"]:
                return f"Resuelto silenciosamente por Discovery First: Stack detectado = {', '.join(stack['languages'])}"

        # 3. Gestores de paquetes
        if any(term in q_lower for term in ["package manager", "gestor de paquetes", "instalador"]):
            if stack["package_managers"]:
                return f"Resuelto silenciosamente por Discovery First: Gestor = {stack['package_managers'][0]}"

        # 4. Linters / Formateadores
        if any(term in q_lower for term in ["linter", "formateador", "formato", "estilo"]):
            if stack["linters"]:
                return f"Resuelto silenciosamente por Discovery First: Linter = {stack['linters'][0]}"

        # 5. ADR previo
        prior_adrs = self.query_existing_adrs(question_subject)
        if prior_adrs:
            return f"Resuelto por ADR existente: {prior_adrs[0].name}"

        return None


# ============================================================================
# 3. CLASIFICADOR BEZOS DE DECISIÓN (Cálculo Formal de EV)
# ============================================================================

class BezosDecisionClassifier:
    """
    Evalúa el Expected Value of Elicitation (EVE) para clasificar decisiones
    en Tipo 1 (One-way door) o Tipo 2 (Two-way door).
    """

    def __init__(self, eve_threshold: float = 0.0):
        self.eve_threshold = eve_threshold

    def calculate_eve(self, ctx: DecisionContext) -> float:
        """
        Calcula: EVE = (1 - P_correct) * (V_success + C_error + C_rollback) - C_interrupt - C_wait
        Reglas duras:
        - Si es hard limit o afecta sistemas externos (network, prod), EVE = +inf (Tipo 1 forzoso).
        - Si el costo de error y reversión es trivial (< 5.0), EVE = -100.0 (Tipo 2 forzoso).
        """
        # Hard limits y mutaciones externas
        if ctx.is_hard_limit or ctx.affects_external_systems:
            return float("inf")

        # Reversión trivial y radio de explosión contenido
        if ctx.estimated_cost_rollback < 5.0 and ctx.estimated_cost_error < 5.0:
            return -100.0

        v_success = 100.0  # Normalizado
        risk_exposure = (1.0 - ctx.estimated_p_correct) * (
            v_success + ctx.estimated_cost_error + ctx.estimated_cost_rollback
        )
        cost_of_asking = ctx.interruption_cost + (ctx.opportunity_cost_rate * 10.0)

        eve = risk_exposure - cost_of_asking
        return eve

    def classify(self, ctx: DecisionContext) -> Tuple[DecisionType, float, str]:
        eve = self.calculate_eve(ctx)
        if eve > self.eve_threshold or ctx.is_hard_limit or ctx.affects_external_systems:
            reason = (
                f"Acción Tipo 1 (Puerta de Una Vía). EVE={eve:.2f} > {self.eve_threshold}. "
                f"Riesgo de error no compensa la interrupción. STOP requerido."
            )
            return DecisionType.TYPE_1_IRREVERSIBLE, eve, reason
        else:
            reason = (
                f"Acción Tipo 2 (Puerta de Dos Vías). EVE={eve:.2f} <= {self.eve_threshold}. "
                f"Acción reversible a bajo costo. Ejecutar de inmediato sin permiso."
            )
            return DecisionType.TYPE_2_REVERSIBLE, eve, reason


# ============================================================================
# 4. ORQUESTADOR DE ENTREVISTA ESTRATÉGICA (/grill-me & rich-elicitation)
# ============================================================================

class StrategicGrillOrchestrator:
    """
    Gestiona la entrevista socrática de alto rigor (/grill-me).
    Formula preguntas de alto apalancamiento, una a la vez, con recomendaciones explícitas.
    Incorpora defensas contra la trampa de adulación (anti-sycophancy).
    """

    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max_rounds
        self.current_round = 0
        self.interview_log: List[Dict[str, Any]] = []

    def generate_boundary_question(
        self, subject: str, dilemma: str, opt_a: str, opt_b: str, rec: str, rationale: str
    ) -> HighLeverageQuestion:
        self.current_round += 1
        return HighLeverageQuestion(
            id=f"HLQ_BOUND_{len(self.interview_log) + 1}",
            category="Boundary",
            prompt_text=f"Respecto a '{subject}': Bajo condiciones extremas de {dilemma}, ¿cómo debe responder el sistema?",
            options=[opt_a, opt_b],
            recommended_option=rec,
            rationale=rationale,
        )

    def generate_munger_inversion_question(
        self, failure_mode: str, prevention_a: str, prevention_b: str, rec: str, rationale: str
    ) -> HighLeverageQuestion:
        self.current_round += 1
        return HighLeverageQuestion(
            id=f"HLQ_MUNGER_{len(self.interview_log) + 1}",
            category="Munger_Inversion",
            prompt_text=f"Inversión Hostil: Si el objetivo de un atacante o bug fuera inducir '{failure_mode}', ¿cuál de estas dos defensas estructurales adoptamos?",
            options=[prevention_a, prevention_b],
            recommended_option=rec,
            rationale=rationale,
        )

    def generate_tradeoff_question(
        self, subject: str, short_term_gain: str, long_term_debt: str, opt_a: str, opt_b: str, rec: str, rationale: str
    ) -> HighLeverageQuestion:
        self.current_round += 1
        return HighLeverageQuestion(
            id=f"HLQ_TRADEOFF_{len(self.interview_log) + 1}",
            category="Trade_Off",
            prompt_text=f"Trade-Off Asimétrico en '{subject}': Ganancia rápida ({short_term_gain}) vs Deuda técnica ({long_term_debt}). ¿Qué camino adoptamos?",
            options=[opt_a, opt_b],
            recommended_option=rec,
            rationale=rationale,
        )

    def generate_verification_question(
        self, subject: str, falsification_target: str, opt_a: str, opt_b: str, rec: str, rationale: str
    ) -> HighLeverageQuestion:
        self.current_round += 1
        return HighLeverageQuestion(
            id=f"HLQ_VERIF_{len(self.interview_log) + 1}",
            category="Verification",
            prompt_text=f"Criterio de Verificación Popperiano para '{subject}': ¿Qué test cuantificable falsará la implementación si falla '{falsification_target}'?",
            options=[opt_a, opt_b],
            recommended_option=rec,
            rationale=rationale,
        )

    def format_question_for_user(self, q: HighLeverageQuestion) -> str:
        """Formatea la pregunta en Markdown limpio sin decoración superflua."""
        lines = [
            f"**[Elicitación Estratégica - {q.category}]** {q.prompt_text}\n",
            "Opciones:",
        ]
        for opt in q.options:
            if opt == q.recommended_option:
                lines.append(f"- **(Recommended)** {opt}")
            else:
                lines.append(f"- {opt}")
        lines.append(f"\n*Fundamento Técnico de la Recomendación:* {q.rationale}")
        return "\n".join(lines)

    def record_human_decision(
        self, question_id: str, chosen_option: str, rationale_override: Optional[str] = None
    ) -> None:
        self.interview_log.append({
            "question_id": question_id,
            "chosen_option": chosen_option,
            "rationale_override": rationale_override,
            "round": self.current_round,
        })

    def check_anti_sycophancy(self, user_decision: str, invariants: List[str]) -> Optional[str]:
        """
        Detecta si la decisión del usuario colisiona con invariantes conocidos del sistema.
        Retorna advertencia hostil/técnica si hay colisión, o None si es coherente.
        """
        user_dec_lower = user_decision.lower()
        for inv in invariants:
            inv_lower = inv.lower()
            # Si el usuario decide omitir o deshabilitar un invariante crítico
            if any(term in user_dec_lower for term in ["desactivar", "ignorar", "omitir", "disable", "skip"]):
                if any(word in inv_lower for word in user_dec_lower.split()):
                    return (
                        f"ALERTA ANTI-SYCOPHANCY: La decisión elegida viola el invariante de sistema: '{inv}'. "
                        f"Esto comprará deuda técnica no lineal o fallos catastróficos en runtime."
                    )
        return None

    def is_converged(self) -> bool:
        """Indica si se obtuvo una resolución sin exceder las rondas máximas."""
        return len(self.interview_log) > 0 and self.current_round <= self.max_rounds

    def rounds_exhausted(self) -> bool:
        return self.current_round >= self.max_rounds


# ============================================================================
# 5. SINCRONIZADOR BRAIN-TO-DOCS (Generación Dinámica de ADRs y README)
# ============================================================================

class BrainToDocsSynchronizer:
    """
    Destila de inmediato cada decisión pactada en la entrevista estratégica
    en un archivo ADR inmutable numerado (docs/adr/NNNN-*.md).
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.adr_dir = self.workspace_root / "docs" / "adr"
        self.adr_dir.mkdir(parents=True, exist_ok=True)

    def get_next_adr_index(self) -> int:
        existing = list(self.adr_dir.glob("*.md"))
        if not existing:
            return 1
        indices: List[int] = []
        for p in existing:
            match = re.match(r"^(\d+)-", p.name)
            if match:
                indices.append(int(match.group(1)))
        return max(indices) + 1 if indices else 1

    def create_adr(
        self,
        title: str,
        context: str,
        decision: str,
        consequences_positive: List[str],
        consequences_negative: List[str],
        alternatives_evaluated: Optional[List[Dict[str, str]]] = None,
        verification_criteria: Optional[str] = None,
        author: str = "Aleph Intent Alignment Engine",
    ) -> Path:
        idx = self.get_next_adr_index()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{idx:04d}-{slug}.md"
        filepath = self.adr_dir / filename

        pos_lines = "\n".join([f"- {item}" for item in consequences_positive])
        neg_lines = "\n".join([f"- {item}" for item in consequences_negative])

        alternatives_block = ""
        if alternatives_evaluated:
            alt_lines = []
            for i, alt in enumerate(alternatives_evaluated, 1):
                name = alt.get("name", f"Alternativa {i}")
                loss_reason = alt.get("loss_reason", "Costo superior o menor seguridad")
                debt = alt.get("debt", "Deuda de mantenimiento")
                alt_lines.append(f"{i}. **{name}:**\n   - *Por qué pierde:* {loss_reason}\n   - *Deuda:* {debt}")
            alternatives_block = "## Alternativas Evaluadas y Descartadas\n" + "\n".join(alt_lines) + "\n\n"

        verif_block = ""
        if verification_criteria:
            verif_block = f"## Criterio de Verificación Falsable (Popperiano)\n{verification_criteria}\n\n"

        adr_content = f"""# ADR {idx:04d}: {title}

## Estado
ACEPTADO (Ratificado vía /grill-me y Matriz Bezos Tipo 1)

## Autor y Origen
- **Entrevistador:** {author}
- **Estado de Aprobación:** Ratificado

## Contexto Técnico
{context}

{alternatives_block}## Decisión Arquitectónica
{decision}

## Consecuencias y Trade-offs
### Ganancias (Ventaja Asimétrica):
{pos_lines}

### Deuda Técnica Comprada / Costos Aceptados:
{neg_lines}

{verif_block}"""
        filepath.write_text(adr_content, encoding="utf-8")
        return filepath

    def update_readme_vision(self, vision_summary: str, section_header: str = "## Arquitectura y Visión Estratégica (L1)") -> Path:
        """Actualiza o crea el archivo README.md con la visión estratégica consolidada."""
        readme_path = self.workspace_root / "README.md"
        block = f"\n\n{section_header}\n{vision_summary}\n"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            if section_header in content:
                # Reemplazar sección existente
                pattern = re.compile(rf"{re.escape(section_header)}.*?(?=\n## |\Z)", re.DOTALL)
                new_content = pattern.sub(f"{section_header}\n{vision_summary}\n", content)
                readme_path.write_text(new_content, encoding="utf-8")
            else:
                readme_path.write_text(content + block, encoding="utf-8")
        else:
            readme_path.write_text(f"# Proyecto Aleph\n{block}", encoding="utf-8")
        return readme_path


# ============================================================================
# 6. DESCOMPRESOR ATÓMICO TDD L1-L5 (2 a 5 Minutos por Micro-Tarea)
# ============================================================================

class TDDAtomicDecompressor:
    """
    Transforma especificaciones arquitectónicas L3/L4 en un checklist
    ultradetallado de tareas indivisibles de 2 a 5 minutos.
    Evita la hiper-atomización mediante coalescencia y control de lote (máx 8 tareas/lote).
    """

    @staticmethod
    def validate_task_granularity(task: TDDAtomicTask) -> bool:
        """Garantiza que la tarea esté estrictamente acotada entre 2 y 5 minutos."""
        if task is None:
            return False
        return 2 <= task.estimated_minutes <= 5

    @staticmethod
    def render_markdown_checklist(tasks: List[TDDAtomicTask]) -> str:
        lines = ["## Checklist de Ejecución Atómica TDD (Nivel 5)\n"]
        for t in tasks:
            lines.append(f"- [ ] **Tarea {t.task_id}: [{t.phase}]** ({t.estimated_minutes} min)")
            lines.append(f"  - **Archivo Target:** `{t.target_file}`")
            lines.append(f"  - **Especificación:** {t.specification}")
            lines.append(f"  - **Comando de Verificación:** `{t.verification_command}`")
            lines.append(f"  - **Código de Salida Esperado:** `{t.expected_exit_code}`\n")
        return "\n".join(lines)

    @classmethod
    def decompress_module_to_tdd_cycle(
        cls,
        module_name: str,
        target_src: Path,
        target_test: Path,
        verification_cmd: str,
        test_spec: str,
        impl_spec: str,
        refactor_spec: str,
    ) -> List[TDDAtomicTask]:
        """
        Genera el ciclo indivisible RED -> GREEN -> REFACTOR para un módulo,
        garantizando granularidad de 2 a 5 minutos por paso.
        """
        slug = re.sub(r"[^A-Za-z0-9]+", "-", module_name).upper()
        t_red = TDDAtomicTask(
            task_id=f"L5-{slug}-01",
            phase="RED",
            target_file=target_test,
            estimated_minutes=3,
            specification=test_spec,
            verification_command=verification_cmd,
            expected_exit_code=1,  # Falla demostrando ausencia
        )
        t_green = TDDAtomicTask(
            task_id=f"L5-{slug}-02",
            phase="GREEN",
            target_file=target_src,
            estimated_minutes=4,
            specification=impl_spec,
            verification_command=verification_cmd,
            expected_exit_code=0,  # Pasa exitosamente
        )
        t_refactor = TDDAtomicTask(
            task_id=f"L5-{slug}-03",
            phase="REFACTOR",
            target_file=target_src,
            estimated_minutes=3,
            specification=refactor_spec,
            verification_command=verification_cmd,
            expected_exit_code=0,
        )

        return [t_red, t_green, t_refactor]

    @classmethod
    def coalesce_task_batches(
        cls, tasks: List[TDDAtomicTask], max_batch_size: int = 8
    ) -> List[List[TDDAtomicTask]]:
        """
        Mitigación Falla 3: Divide checklists largos en lotes coherentes
        de no más de `max_batch_size` tareas para evitar fatiga de contexto.
        """
        batches = []
        for i in range(0, len(tasks), max_batch_size):
            batches.append(tasks[i : i + max_batch_size])
        return batches


# ============================================================================
# 7. MOTOR SOBERANO INTEGRADO: AlephElicitationEngine
# ============================================================================

class AlephElicitationEngine:
    """
    Fachada unificada del Subsistema Soberano de Elicitación y Gobernanza:
    Coordina Discovery First, Clasificador Bezos, Orquestador Grill-Me,
    Brain-to-Docs y Descompresor L5.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.discovery = DiscoveryFirstScanner(self.workspace_root)
        self.classifier = BezosDecisionClassifier(eve_threshold=0.0)
        self.grill = StrategicGrillOrchestrator(max_rounds=3)
        self.sync = BrainToDocsSynchronizer(self.workspace_root)
        self.decompressor = TDDAtomicDecompressor()

    def evaluate_intent(
        self,
        action_id: str,
        description: str,
        domain: DecisionDomain,
        question_subject: Optional[str] = None,
        is_hard_limit: bool = False,
        estimated_p_correct: float = 0.5,
        estimated_cost_error: float = 10.0,
        estimated_cost_rollback: float = 5.0,
        affects_external_systems: bool = False,
    ) -> ElicitationSummary:
        """
        Ejecuta el protocolo completo de gobernanza:
        1. Discovery First (silencioso)
        2. Clasificación Bezos (EV)
        3. Determinación de ruta (Auto Tipo 2 vs Parada Tipo 1)
        """
        # Capa 1: Si hay una pregunta planteada, intentar resolverla silenciosamente
        if question_subject:
            silent_res = self.discovery.can_resolve_silently(question_subject)
            if silent_res:
                return ElicitationSummary(
                    action_id=action_id,
                    decision_type=DecisionType.TYPE_2_REVERSIBLE,
                    eve_score=-100.0,
                    resolved_silently=True,
                    resolution_source=silent_res,
                    execution_permitted=True,
                    details="Resuelto silenciosamente por Discovery First sin molestar al operador.",
                )

        # Capa 2: Clasificación de decisión formal
        ctx = DecisionContext(
            action_id=action_id,
            description=description,
            domain=domain,
            is_hard_limit=is_hard_limit,
            estimated_p_correct=estimated_p_correct,
            estimated_cost_error=estimated_cost_error,
            estimated_cost_rollback=estimated_cost_rollback,
            affects_external_systems=affects_external_systems,
        )

        dec_type, eve_score, reason = self.classifier.classify(ctx)

        if dec_type == DecisionType.TYPE_2_REVERSIBLE:
            return ElicitationSummary(
                action_id=action_id,
                decision_type=dec_type,
                eve_score=eve_score,
                resolved_silently=False,
                execution_permitted=True,
                details=reason,
            )
        else:
            return ElicitationSummary(
                action_id=action_id,
                decision_type=dec_type,
                eve_score=eve_score,
                resolved_silently=False,
                execution_permitted=False,
                details=reason,
            )

    def crystallize_decision(
        self,
        title: str,
        context: str,
        decision: str,
        consequences_positive: List[str],
        consequences_negative: List[str],
        alternatives_evaluated: Optional[List[Dict[str, str]]] = None,
        verification_criteria: Optional[str] = None,
    ) -> Path:
        """Guarda la decisión en un ADR formal auditado."""
        return self.sync.create_adr(
            title=title,
            context=context,
            decision=decision,
            consequences_positive=consequences_positive,
            consequences_negative=consequences_negative,
            alternatives_evaluated=alternatives_evaluated,
            verification_criteria=verification_criteria,
        )
