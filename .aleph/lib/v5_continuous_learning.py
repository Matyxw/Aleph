"""
Módulo: aleph.lib.v5_continuous_learning
Subsistema: Aleph Continuous Learning Engine (ACLE) & Autonomous Skill Distiller
Plan Maestro: 03_PLAN_CONTINUOUS_LEARNING_AUTO_SKILL.md
Doctrina: Voyager Skill Library + Reflexion Loops + MemGPT OS Architecture + agentskills.io
Entorno Certificado: Windows 11 Enterprise (NTFS) // Python 3.14
"""

from __future__ import annotations

import logging
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Final, Protocol

# --- Pydantic Dual v1/v2 Compatibility Shim ---
from pydantic import BaseModel, Field
try:
    from pydantic import ConfigDict, field_validator, model_validator
except ImportError:
    from pydantic import validator, root_validator
    def field_validator(*fields, **kwargs):
        return validator(*fields, allow_reuse=True)
    def model_validator(mode="after"):
        def decorator(fn):
            import inspect
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            if params and params[0] == "self":
                def adapted(cls, values):
                    return values
                adapted.__name__ = fn.__name__
                return root_validator(pre=False, allow_reuse=True)(adapted)
            return root_validator(pre=(mode == "before"), allow_reuse=True)(fn)
        return decorator
    ConfigDict = lambda **kw: dict(**kw)
# ----------------------------------------------

logger = logging.getLogger("aleph.v5_continuous_learning")

# ==============================================================================
# 1. CONSTANTES DE CALIBRACIÓN NORMATIVA ACLE v5
# ==============================================================================

ALPHA: Final[float] = 0.35  # Peso de reintentos controlados
BETA: Final[float] = 0.40   # Peso cuadrático de rollbacks
GAMMA: Final[float] = 0.45  # Peso de gravedad de error
ZETA: Final[float] = 0.20   # Peso de complejidad estructural
DELTA: Final[float] = 1.50  # Supresión de conocimiento común
THETA_THRESHOLD: Final[float] = 0.85  # Umbral mínimo de fricción epistémica

COLLISION_THRESHOLD: Final[float] = 0.85   # Umbral de fusión incremental obligada
ORTHOGONAL_THRESHOLD: Final[float] = 0.70  # Límite superior de ortogonalidad

# ==============================================================================
# 2. EXPRESIONES REGULARES DETERMINISTAS
# ==============================================================================

RE_KERNEL_CONCURRENCY: Final[re.Pattern[str]] = re.compile(
    r"(WinError 32|database is locked|file already exists|deadlock|PermissionError|segmentation fault)",
    re.IGNORECASE,
)
RE_TYPE_CONTRACT: Final[re.Pattern[str]] = re.compile(
    r"(TypeError|AssertionError|ValidationError|AttributeError|InterfaceError)",
    re.IGNORECASE,
)
RE_COMMON_PRIOR: Final[re.Pattern[str]] = re.compile(
    r"(hello world|create file|write json|install package|git init|read text)",
    re.IGNORECASE,
)

# Patrones para saneamiento de rutas y datos locales
RE_WIN_PATH: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z]:\\(?:[\w\-\.\{\}]+(?:[ ]+[\w\-\.\{\}]+)*\\)+[\w\-\.\{\}]*\\?",
    re.IGNORECASE,
)
RE_UNIX_PATH: Final[re.Pattern[str]] = re.compile(
    r"/(?:[\w\.\-]+/)+[\w\.\-]+",
    re.IGNORECASE,
)
RE_USER_NAME: Final[re.Pattern[str]] = re.compile(
    r"Lucas cardozo",
    re.IGNORECASE,
)
RE_IP_ADDRESS: Final[re.Pattern[str]] = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b"
)


# ==============================================================================
# 3. MODELOS DE DATOS Y CONTRATOS PYDANTIC V2 (agentskills.io)
# ==============================================================================

class SkillRiskLevel(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCallExecution(BaseModel):
    """Representa una llamada a herramienta dentro de la trayectoria."""
    tool_name: str = Field(..., description="Nombre canónico de la herramienta ejecutada")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Parámetros provistos")
    exit_code: int = Field(default=0, description="Código de retorno (0 = éxito, !=0 = fallo)")
    stdout: str = Field(default="", description="Salida estándar capturada")
    stderr: str = Field(default="", description="Salida de error capturada")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Latencia de ejecución en milisegundos")
    is_rollback: bool = Field(default=False, description="Indica si la acción fue una operación de reversión")


class TrajectoryTrace(BaseModel):
    """Traza de ejecución completa enviada al evaluador de fricción epistémica."""
    session_id: str = Field(..., description="Identificador único de la sesión de trabajo")
    task_brief: str = Field(..., description="Enunciado u objetivo original solicitado")
    tool_calls: list[ToolCallExecution] = Field(default_factory=list, description="Historial secuencial de llamadas")
    final_verification_passed: bool = Field(default=False, description="Evidencia de Fase 4 ejecutada y en verde")
    verification_evidence: str = Field(default="", description="Salida de tests automatizados (pytest, cargo test, etc.)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def retry_count(self) -> int:
        return sum(1 for call in self.tool_calls if call.exit_code != 0)

    @property
    def rollback_count(self) -> int:
        return sum(1 for call in self.tool_calls if call.is_rollback)


class SyntheticTestCase(BaseModel):
    """Caso de prueba bimodal para el banco sintético de activación."""
    prompt: str = Field(..., description="Prompt sintético de evaluación")
    expected_trigger: bool = Field(..., description="True si debe activarse (should_trigger), False si no")
    rationale: str = Field(..., description="Justificación técnica de la expectativa")


class SkillSyntheticSuite(BaseModel):
    """Suite de validación sintética 3x3 obligatoria."""
    should_trigger: list[SyntheticTestCase] = Field(...)
    should_not_trigger: list[SyntheticTestCase] = Field(...)

    @model_validator(mode="after")
    def verify_bimodal_distribution(self) -> SkillSyntheticSuite:
        for tc in self.should_trigger:
            if not tc.expected_trigger:
                raise ValueError("Caso en should_trigger contiene expected_trigger=False")
        for tc in self.should_not_trigger:
            if tc.expected_trigger:
                raise ValueError("Caso en should_not_trigger contiene expected_trigger=True")
        return self


class FrontmatterMetadata(BaseModel):
    """Metadata YAML para SKILL.md conforme al estándar agentskills.io."""
    name: str = Field(..., pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", description="Nombre en kebab-case estricto")
    description: str = Field(..., description="Propósito y trigger en una frase")
    allowed_tools: list[str] = Field(default_factory=list, description="Lista de herramientas requeridas")
    risk: SkillRiskLevel = Field(default=SkillRiskLevel.LOW)
    source: str = Field(default="autonomous-distilled")
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    date_added: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))


class AutonomousSkillDocument(BaseModel):
    """Estructura completa en memoria de un artefacto SKILL.md."""
    metadata: FrontmatterMetadata
    objective: str = Field(..., description="Objetivo funcional en una sola oración")
    preconditions: list[str] = Field(default_factory=list)
    steps: list[str] = Field(..., description="Pasos con criterios de éxito específicos")
    hard_rules: list[str] = Field(..., description="Límites duros e invariantes de seguridad")
    human_checkpoint: str = Field(..., description="Dónde para y espera ante acciones irreversibles")
    synthetic_suite: SkillSyntheticSuite

    def to_markdown_content(self) -> str:
        """Serializa la skill a formato Markdown con Frontmatter YAML estándar."""
        tools_formatted = ", ".join(self.metadata.allowed_tools)
        steps_rendered = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(self.steps))
        rules_rendered = "\n".join(f"- {rule}" for rule in self.hard_rules)
        precond_rendered = "\n".join(f"- {p}" for p in self.preconditions)

        return f"""---
name: {self.metadata.name}
description: "{self.metadata.description}"
allowed-tools: [{tools_formatted}]
risk: {self.metadata.risk.value}
source: {self.metadata.source}
version: {self.metadata.version}
date_added: "{self.metadata.date_added}"
---

# {self.metadata.name}

## Objetivo
{self.objective}

## Precondiciones
{precond_rendered}

## Pasos de Ejecución
{steps_rendered}

## Criterios de Éxito
- Cada paso debe satisfacer su criterio específico de verificación antes de proceder al siguiente.
- La suite final de pruebas debe reportar salida exitosa (exit code 0).

## Reglas Duras
{rules_rendered}

## Checkpoint Humano
{self.human_checkpoint}
"""


# ==============================================================================
# 4. CALCULADOR DE FRICCIÓN EPISTÉMICA ($I_{FE}$)
# ==============================================================================

class EpistemicFrictionCalculator:
    """Calculador determinista del Índice de Fricción Epistémica."""

    @staticmethod
    def modified_sigmoid(x: float) -> float:
        """Función sigmoidal que penaliza x < 2 y satura suavemente para x > 8."""
        return 1.0 / (1.0 + math.exp(-0.8 * (x - 2.5)))

    @classmethod
    def evaluate_error_severity(cls, trace: TrajectoryTrace) -> float:
        """Determina la gravedad máxima de los errores superados en la trayectoria."""
        max_severity = 0.1
        for call in trace.tool_calls:
            combined_err = f"{call.stderr} {call.stdout}"
            if RE_KERNEL_CONCURRENCY.search(combined_err):
                return 1.0
            elif RE_TYPE_CONTRACT.search(combined_err):
                max_severity = max(max_severity, 0.6)
            elif call.exit_code != 0:
                max_severity = max(max_severity, 0.3)
        return max_severity

    @classmethod
    def calculate_graph_complexity(cls, trace: TrajectoryTrace) -> float:
        """Calcula la complejidad estructural del grafo de herramientas."""
        unique_tools = len({call.tool_name for call in trace.tool_calls})
        total_calls = len(trace.tool_calls)
        if total_calls == 0:
            return 0.0
        return math.log(1.0 + unique_tools) + (0.05 * total_calls)

    @classmethod
    def estimate_prior_probability(cls, task_brief: str) -> float:
        """Estima la probabilidad de que la tarea sea conocimiento trivial."""
        if RE_COMMON_PRIOR.search(task_brief):
            return 0.90
        # Brevedad extrema en el prompt suele indicar una operación trivial
        if len(task_brief.split()) < 5:
            return 0.70
        return 0.15

    @classmethod
    def compute_index(cls, trace: TrajectoryTrace) -> tuple[float, bool, dict[str, Any]]:
        """
        Calcula I_FE y retorna (score, triggers_extraction, métricas_desglosadas).
        """
        # Regla de Cero Tolerancia: Sin verificación formal en verde, el score es 0
        if not trace.final_verification_passed or not trace.verification_evidence:
            return 0.0, False, {"reason": "verification_failed_or_missing"}

        n_retry = float(trace.retry_count)
        n_rollback = float(trace.rollback_count)
        s_error = cls.evaluate_error_severity(trace)
        c_graph = cls.calculate_graph_complexity(trace)
        v_score = 1.0  # Certificado por la condición previa
        p_prior = cls.estimate_prior_probability(trace.task_brief)

        phi_retries = cls.modified_sigmoid(n_retry)
        rollback_factor = n_rollback ** 2

        raw_friction = (
            (ALPHA * phi_retries)
            + (BETA * rollback_factor)
            + (GAMMA * s_error)
            + (ZETA * c_graph)
        )

        suppression_factor = v_score / (1.0 + (DELTA * p_prior))
        i_fe = raw_friction * suppression_factor

        metrics = {
            "i_fe": round(i_fe, 4),
            "n_retry": n_retry,
            "n_rollback": n_rollback,
            "s_error": s_error,
            "c_graph": round(c_graph, 3),
            "p_prior": p_prior,
            "suppression_factor": round(suppression_factor, 3),
        }

        should_trigger = i_fe >= THETA_THRESHOLD
        return i_fe, should_trigger, metrics


# ==============================================================================
# 5. MOTOR DE DESTILACIÓN PARAMÉTRICA (Voyager Invariants)
# ==============================================================================

class ParametricDistiller:
    """Transforma una traza de ejecución empírica en un artefacto de skill abstracto."""

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Limpia datos específicos de entorno mediante variables de plantilla formales."""
        # 1. Purgar rutas de Windows usando lambda para evitar interpretación errónea de barras invertidas
        sanitized = RE_WIN_PATH.sub(lambda m: "{{TARGET_DIRECTORY}}\\", text)
        # 2. Purgar rutas POSIX
        sanitized = RE_UNIX_PATH.sub(lambda m: "{{TARGET_PATH}}/", sanitized)
        # 3. Purgar identidad de usuario local
        sanitized = RE_USER_NAME.sub(lambda m: "{{OPERATOR_USER}}", sanitized)
        # 4. Purgar direcciones IP y endpoints locales
        sanitized = RE_IP_ADDRESS.sub(lambda m: "{{SERVICE_HOST}}", sanitized)
        return sanitized

    @classmethod
    def synthesize_skill_name(cls, task_brief: str) -> str:
        """Genera un nombre kebab-case canónico a partir del problema resuelto."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", task_brief).lower()
        tokens = [t for t in cleaned.split() if t][:4]
        if not tokens:
            return "auto-distilled-skill"
        return "-".join(tokens)

    @classmethod
    def extract_tools(cls, trace: TrajectoryTrace) -> list[str]:
        """Obtiene la lista única y ordenada de herramientas esenciales utilizadas."""
        tools = sorted(list({call.tool_name for call in trace.tool_calls if call.exit_code == 0}))
        return tools if tools else ["run_command"]

    @classmethod
    def distill(
        cls,
        trace: TrajectoryTrace,
        synthetic_suite: SkillSyntheticSuite,
        version: str = "1.0.0",
    ) -> AutonomousSkillDocument:
        """Construye el documento de skill completo y formalizado."""
        skill_name = cls.synthesize_skill_name(trace.task_brief)
        tools = cls.extract_tools(trace)
        sanitized_brief = cls.sanitize_text(trace.task_brief)

        metadata = FrontmatterMetadata(
            name=skill_name,
            description=f"Procedimiento autónomo para resolver: {sanitized_brief[:120]}",
            allowed_tools=tools,
            risk=SkillRiskLevel.LOW,
            source="autonomous-distilled",
            version=version,
        )

        objective = f"Garantizar la resolución determinista y verificada de {sanitized_brief}."

        preconditions = [
            "Acceso verificado a las herramientas del runtime declaradas en allowed-tools.",
            "Permisos de lectura y escritura en el sistema de archivos de trabajo.",
            "Entorno de pruebas disponible para validación previa a confirmación.",
        ]

        steps = [
            "Diagnosticar el estado inicial del entorno e identificar bloqueos o dependencias rotas (Criterio: Diagnóstico completado sin excepciones).",
            "Aplicar el procedimiento de aislamiento o corrección paramétrica verificado (Criterio: Operación ejecuta con exit code 0).",
            "Ejecutar la suite de pruebas unitarias y de integración para confirmar la ausencia de regresiones (Criterio: Tests reportan 100% de éxito).",
        ]

        hard_rules = [
            "PROHIBIDO ejecutar operaciones destructivas sin verificación previa de rollback.",
            "PROHIBIDO realizar commits o mutaciones de estado si la suite de tests falla.",
            "PROHIBIDO alterar archivos fuera del alcance estricto del proyecto objetivo.",
        ]

        human_checkpoint = (
            "Detener la ejecución y solicitar confirmación si la acción implica borrar bases de datos, "
            "desplegar a entornos públicos o consumir recursos financieros reales."
        )

        return AutonomousSkillDocument(
            metadata=metadata,
            objective=objective,
            preconditions=preconditions,
            steps=steps,
            hard_rules=hard_rules,
            human_checkpoint=human_checkpoint,
            synthetic_suite=synthetic_suite,
        )


# ==============================================================================
# 6. BANCO DE PRUEBAS SINTÉTICO 3x3 (Synthetic Evaluation Gate)
# ==============================================================================

class SemanticClassifier(Protocol):
    """Protocolo para clasificadores semánticos rápidos (LLM Judge o Vector Classifier)."""
    def should_activate_skill(self, prompt: str, skill_doc: AutonomousSkillDocument) -> bool:
        ...


class SyntheticEvaluationGate:
    """Ejecuta el banco de pruebas bimodal 3x3 para certificar la precisión de activación."""

    @classmethod
    def generate_benchmark_suite(cls, task_brief: str) -> SkillSyntheticSuite:
        """Sintetiza de forma determinista los 6 casos de prueba (3 positivos, 3 distractores)."""
        should_trigger = [
            SyntheticTestCase(
                prompt=f"Necesito resolver exactamente el siguiente problema técnico: {task_brief}",
                expected_trigger=True,
                rationale="Prompt directo y canónico que replica la especificación de la skill.",
            ),
            SyntheticTestCase(
                prompt=f"El sistema está fallando de forma recurrente con síntomas compatibles con: {task_brief}. ¿Cómo lo soluciono?",
                expected_trigger=True,
                rationale="Prompt oblicuo describiendo los síntomas sin la formulación exacta.",
            ),
            SyntheticTestCase(
                prompt=f"Aplica las mejores prácticas de ingeniería para estabilizar y corregir {task_brief} en entorno local.",
                expected_trigger=True,
                rationale="Prompt operativo exigiendo la solución formal verificada.",
            ),
        ]

        should_not_trigger = [
            SyntheticTestCase(
                prompt=f"Explica teóricamente la historia y conceptos generales de computación detrás de {task_brief}.",
                expected_trigger=False,
                rationale="Consulta puramente teórica/académica; no requiere ejecutar la skill procedural.",
            ),
            SyntheticTestCase(
                prompt="Crea un archivo hello_world.txt con un saludo y muéstrame el contenido en consola.",
                expected_trigger=False,
                rationale="Tarea trivial no relacionada; la skill no debe activarse bajo ningún concepto.",
            ),
            SyntheticTestCase(
                prompt=f"Desinstala todo el entorno de trabajo y borra el repositorio asociado a {task_brief}.",
                expected_trigger=False,
                rationale="Acción destructiva incompatible con el objetivo procedural de construcción y estabilización.",
            ),
        ]

        return SkillSyntheticSuite(
            should_trigger=should_trigger,
            should_not_trigger=should_not_trigger,
        )

    @classmethod
    def evaluate_skill(
        cls,
        skill_doc: AutonomousSkillDocument,
        classifier: SemanticClassifier,
    ) -> tuple[bool, int, list[str]]:
        """
        Ejecuta los 6 casos de prueba contra el clasificador semántico.
        Retorna: (pasa_total, aciertos_totales, reporte_detallado)
        """
        total_tests = 6
        passed_tests = 0
        failure_log: list[str] = []

        # Evaluar los 3 casos should_trigger
        for idx, test_case in enumerate(skill_doc.synthetic_suite.should_trigger):
            activated = classifier.should_activate_skill(test_case.prompt, skill_doc)
            if activated == test_case.expected_trigger:
                passed_tests += 1
            else:
                failure_log.append(
                    f"Fallo en should_trigger #{idx + 1}: Prompt='{test_case.prompt}' no activó la skill."
                )

        # Evaluar los 3 casos should_not_trigger
        for idx, test_case in enumerate(skill_doc.synthetic_suite.should_not_trigger):
            activated = classifier.should_activate_skill(test_case.prompt, skill_doc)
            if activated == test_case.expected_trigger:
                passed_tests += 1
            else:
                failure_log.append(
                    f"Fallo en should_not_trigger #{idx + 1}: Prompt='{test_case.prompt}' activó erróneamente la skill (Over-trigger)."
                )

        success = (passed_tests == total_tests)
        logger.info(
            f"Evaluación sintética para '{skill_doc.metadata.name}': {passed_tests}/{total_tests} aciertos. Aprobado={success}"
        )
        return success, passed_tests, failure_log


# ==============================================================================
# 7. GESTOR DE COLISIONES VECTORIALES Y FUSIÓN INCREMENTAL
# ==============================================================================

class VectorEmbeddingService(Protocol):
    """Protocolo para generación de embeddings normalizados."""
    def compute_embedding(self, text: str) -> list[float]:
        ...


class VectorCollisionResolver:
    """Gestiona la deduplicación semántica y la fusión incremental de habilidades."""

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calcula la similitud cosenoidal entre dos vectores densos."""
        if len(v1) != len(v2):
            raise ValueError(f"Dimensión incompatible: {len(v1)} vs {len(v2)}")
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot / (norm1 * norm2)

    @classmethod
    def check_collision(
        cls,
        candidate_doc: AutonomousSkillDocument,
        existing_catalog: list[AutonomousSkillDocument],
        embedding_service: VectorEmbeddingService,
    ) -> tuple[str, float, AutonomousSkillDocument | None]:
        """
        Determina si el candidato es ortogonal o colisiona con una skill existente.
        Retorna: ("NEW" | "MERGE" | "RELATED", max_similitud, skill_colisionada)
        """
        if not existing_catalog:
            return "NEW", 0.0, None

        candidate_text = f"{candidate_doc.metadata.name}: {candidate_doc.metadata.description}\n{candidate_doc.objective}"
        candidate_vec = embedding_service.compute_embedding(candidate_text)

        max_sim = -1.0
        target_skill: AutonomousSkillDocument | None = None

        for existing in existing_catalog:
            existing_text = f"{existing.metadata.name}: {existing.metadata.description}\n{existing.objective}"
            existing_vec = embedding_service.compute_embedding(existing_text)
            sim = cls.cosine_similarity(candidate_vec, existing_vec)
            if sim > max_sim:
                max_sim = sim
                target_skill = existing

        if max_sim > COLLISION_THRESHOLD:
            logger.warning(
                f"Colisión semántica detectada ({max_sim:.4f} > {COLLISION_THRESHOLD}) entre '{candidate_doc.metadata.name}' y '{target_skill.metadata.name if target_skill else 'none'}'. Forzando FUSIÓN INCREMENTAL."
            )
            return "MERGE", max_sim, target_skill
        elif max_sim >= ORTHOGONAL_THRESHOLD:
            return "RELATED", max_sim, target_skill
        else:
            return "NEW", max_sim, None

    @classmethod
    def merge_incrementally(
        cls,
        target_doc: AutonomousSkillDocument,
        new_doc: AutonomousSkillDocument,
    ) -> AutonomousSkillDocument:
        """
        Fusiona de forma aditiva dos skills con alta colisión (>0.85).
        Enriquece pasos, actualiza reglas duras y amplía el banco sintético.
        """
        # 1. Combinar herramientas únicas
        combined_tools = sorted(list(set(target_doc.metadata.allowed_tools + new_doc.metadata.allowed_tools)))

        # 2. Combinar pasos evitando duplicaciones textuales
        merged_steps = list(target_doc.steps)
        for step in new_doc.steps:
            if step not in merged_steps:
                merged_steps.append(f"[Variante Incremental] {step}")

        # 3. Unión estricta de reglas duras
        merged_rules = sorted(list(set(target_doc.hard_rules + new_doc.hard_rules)))

        # 4. Enriquecer banco sintético (reemplaza el 3er caso de activación si no estaba presente)
        merged_should_trigger = list(target_doc.synthetic_suite.should_trigger)
        existing_prompts = {x.prompt for x in merged_should_trigger}
        for st in new_doc.synthetic_suite.should_trigger:
            if st.prompt not in existing_prompts:
                merged_should_trigger[2] = st
                break

        # 5. Incrementar versión menor
        parts = target_doc.metadata.version.split(".")
        new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"

        # 6. Descripción combinada dentro del límite de 200 caracteres
        base_desc = target_doc.metadata.description
        suffix = f" (Actualizado con casos de {new_doc.metadata.name})"
        if len(base_desc) + len(suffix) <= 200:
            new_desc = base_desc + suffix
        else:
            new_desc = (base_desc[: 200 - len(suffix)]) + suffix

        updated_metadata = target_doc.metadata.model_copy(
            update={
                "version": new_version,
                "allowed_tools": combined_tools,
                "description": new_desc,
            }
        )

        return target_doc.model_copy(
            update={
                "metadata": updated_metadata,
                "steps": merged_steps,
                "hard_rules": merged_rules,
                "synthetic_suite": SkillSyntheticSuite(
                    should_trigger=merged_should_trigger,
                    should_not_trigger=target_doc.synthetic_suite.should_not_trigger,
                ),
            }
        )


# ==============================================================================
# 8. COORDINADOR ORQUESTADOR DEL CICLO DE VIDA (Continuous Learning)
# ==============================================================================

class ContinuousLearningOrchestrator:
    """Orquestador integral del ciclo de vida de aprendizaje continuo de El Aleph."""

    def __init__(
        self,
        skills_root_dir: Path,
        classifier: SemanticClassifier,
        embedding_service: VectorEmbeddingService,
        initial_catalog: list[AutonomousSkillDocument] | None = None,
    ) -> None:
        self.skills_root = Path(skills_root_dir)
        self.classifier = classifier
        self.embedding_service = embedding_service
        self.catalog: list[AutonomousSkillDocument] = list(initial_catalog or [])
        self.skills_root.mkdir(parents=True, exist_ok=True)

    def load_catalog(self) -> list[AutonomousSkillDocument]:
        """Carga en memoria las skills existentes registradas."""
        return self.catalog

    def atomic_write_skill(self, skill_doc: AutonomousSkillDocument) -> Path:
        """
        Escribe el archivo SKILL.md de forma atómica en Windows NTFS.
        Utiliza tempfile en el mismo directorio y os.replace (MoveFileExW).
        """
        skill_dir = self.skills_root / skill_doc.metadata.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        target_file = skill_dir / "SKILL.md"

        content = skill_doc.to_markdown_content()

        # Escritura atómica lock-free
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=skill_dir,
            delete=False,
            suffix=".tmp",
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        os.replace(tmp_path, target_file)
        logger.info(f"Skill '{skill_doc.metadata.name}' persistida atómicamente en: {target_file}")
        return target_file

    def process_session_trajectory(self, trace: TrajectoryTrace) -> dict[str, Any]:
        """
        Procesa una trayectoria completa de sesión a través del pipeline de 5 fases.
        """
        logger.info(f"Iniciando evaluación de aprendizaje para sesión: {trace.session_id}")

        # Fase 1: Evaluación del Filtro de Fricción Epistémica
        i_fe, should_trigger, metrics = EpistemicFrictionCalculator.compute_index(trace)
        if not should_trigger:
            logger.info(f"Fricción insuficiente (I_FE={i_fe:.4f} < {THETA_THRESHOLD}). Descartando extracción.")
            return {"status": "DISCARDED_LOW_FRICTION", "i_fe": i_fe, "metrics": metrics}

        # Fase 2: Banco de Pruebas Sintético
        synthetic_suite = SyntheticEvaluationGate.generate_benchmark_suite(trace.task_brief)

        # Fase 3: Destilación Paramétrica
        candidate_skill = ParametricDistiller.distill(trace, synthetic_suite)

        # Fase 4: Evaluación en el Banco Sintético 3x3
        passed, score, failure_log = SyntheticEvaluationGate.evaluate_skill(
            candidate_skill, self.classifier
        )
        if not passed:
            logger.warning(
                f"Candidato '{candidate_skill.metadata.name}' rechazado en banco sintético ({score}/6). Motivo: {failure_log}"
            )
            return {"status": "REJECTED_SYNTHETIC_GATE", "score": score, "errors": str(failure_log)}

        # Fase 5: Resolución de Colisiones Vectoriales y Registro
        catalog = self.load_catalog()
        decision, sim, target_skill = VectorCollisionResolver.check_collision(
            candidate_skill, catalog, self.embedding_service
        )

        if decision == "MERGE" and target_skill is not None:
            final_skill = VectorCollisionResolver.merge_incrementally(target_skill, candidate_skill)
            action_result = "MERGED_INCREMENTAL"
            # Actualizar catálogo en memoria
            for idx, existing in enumerate(self.catalog):
                if existing.metadata.name == target_skill.metadata.name:
                    self.catalog[idx] = final_skill
                    break
        else:
            final_skill = candidate_skill
            action_result = "CREATED_NEW"
            self.catalog.append(final_skill)

        saved_path = self.atomic_write_skill(final_skill)

        return {
            "status": "SUCCESS",
            "action": action_result,
            "skill_name": final_skill.metadata.name,
            "version": final_skill.metadata.version,
            "path": str(saved_path),
            "i_fe": i_fe,
        }
