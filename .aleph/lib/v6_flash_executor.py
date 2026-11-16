#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: v6_flash_executor.py
Ruta: .aleph\\lib\\v6_flash_executor.py
Propósito: Motor de Ejecución Determinista para Gemini 3.8 Flash (Flash-Optimized Execution Harness).
Implementa las 7 Leyes de Hierro, el validador de invariantes de código,
el runner secuencial de paquetes y el generador de reportes deterministas.
Integra v5_goal_loop_tdd, v5_blackboard_squads, v5_context_cache y v5_uar_harness.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import re
import stat
import sys
import tokenize
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Tuple

# --- Pydantic Dual v1/v2 Compatibility Shim ---
from pydantic import BaseModel as _PydanticBaseModel, Field
try:
    from pydantic import ConfigDict, field_validator, model_validator
    BaseModel = _PydanticBaseModel
except ImportError:
    from pydantic import validator, root_validator
    import json as _shim_json

    def field_validator(*fields, **kwargs):
        pre = kwargs.get("mode") == "before"
        return validator(*fields, pre=pre, allow_reuse=True)

    def model_validator(mode="after"):
        def decorator(fn):
            import inspect
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            if params and params[0] == "self":
                fn._is_v2_self_validator = True
                return fn
            return root_validator(pre=(mode == "before"), allow_reuse=True)(fn)
        return decorator

    ConfigDict = lambda **kw: dict(**kw)

    class BaseModel(_PydanticBaseModel):
        def __init__(self, **data):
            super().__init__(**data)
            for attr_name in dir(self.__class__):
                attr = getattr(self.__class__, attr_name, None)
                if callable(attr) and getattr(attr, "_is_v2_self_validator", False):
                    attr(self)

        def model_dump(self, **kwargs):
            return self.dict(**kwargs)

        def model_dump_json(self, indent=None, **kwargs):
            return _shim_json.dumps(self.dict(**kwargs), indent=indent, default=str, ensure_ascii=False)

        @classmethod
        def model_validate(cls, obj, **kwargs):
            if isinstance(obj, cls):
                return obj
            return cls.parse_obj(obj)

        @classmethod
        def model_validate_json(cls, json_str, **kwargs):
            return cls.parse_raw(json_str)

        @property
        def model_fields_set(self):
            return getattr(self, "__fields_set__", set())
# ----------------------------------------------

logger = logging.getLogger("aleph.v6_flash_executor")

try:
    from .v5_blackboard_squads import (
        ArchitectureContractPacket,
        BlackboardEngine,
        CoderGreenPacket,
        ContextPacketEnvelope,
        FunctionSignatureSpec,
        RoleType,
        TaskStatus,
        TaskTicketPacket,
        TddRedPacket,
        TestFileEntry,
        TypeContract,
    )
    from .v5_context_cache import (
        BpeTokenEstimator,
        CallGraphASTPruner,
        SurgicalLogCrusher,
    )
    from .v5_goal_loop_tdd import (
        ASTGuard,
        GatekeeperRuntime,
        GitTransactionEngine,
        GoalLoopTDDError,
        GoalSpec,
        MerkleTestEngine,
        PhysicalPermissionSandbox,
        VerificationContract,
    )
    from .v5_uar_harness import (
        ActionPayload,
        ActionSpec,
        ActionType,
        AsymmetricUARBridge,
        CanonicalExecutionReceipt,
        CanonicalTask,
        ContextEnvelope,
        ExecutionTargetSpec,
        RuntimeTarget,
        SecurityContext,
    )
except ImportError:
    from v5_blackboard_squads import (
        ArchitectureContractPacket,
        BlackboardEngine,
        CoderGreenPacket,
        ContextPacketEnvelope,
        FunctionSignatureSpec,
        RoleType,
        TaskStatus,
        TaskTicketPacket,
        TddRedPacket,
        TestFileEntry,
        TypeContract,
    )
    from v5_context_cache import (
        BpeTokenEstimator,
        CallGraphASTPruner,
        SurgicalLogCrusher,
    )
    from v5_goal_loop_tdd import (
        ASTGuard,
        GatekeeperRuntime,
        GitTransactionEngine,
        GoalLoopTDDError,
        GoalSpec,
        MerkleTestEngine,
        PhysicalPermissionSandbox,
        VerificationContract,
    )
    from v5_uar_harness import (
        ActionPayload,
        ActionSpec,
        ActionType,
        AsymmetricUARBridge,
        CanonicalExecutionReceipt,
        CanonicalTask,
        ContextEnvelope,
        ExecutionTargetSpec,
        RuntimeTarget,
        SecurityContext,
    )


# ==============================================================================
# 1. EXCEPCIONES FORMALES DEL ARNÉS DETERMINISTA FLASH 3.8
# ==============================================================================

class FlashExecutorError(GoalLoopTDDError):
    """Excepción base del motor determinista para Gemini 3.8 Flash."""


class AtomicPackageViolationError(FlashExecutorError):
    """Violación de la Ley 2: Más de 1 archivo de impl o 1 archivo de test por paquete."""


class PreFlightDependencyError(FlashExecutorError):
    """Violación de la Ley 1: Archivo de dependencia requerido para pre-digestión no existe."""


class PlaceholderForbiddenError(FlashExecutorError):
    """Violación de la Ley 3: Detección por AST/Lexer de pass, marcadores prohibidos, o NotImplementedError."""


class RedPhaseViolationError(FlashExecutorError):
    """Violación de la Ley 4: El test no falló en Fase Red o falló por motivo ajeno al patrón."""


class GreenPhaseViolationError(FlashExecutorError):
    """Violación de la Ley 4: El código no puso los tests en verde o violó el hash Merkle."""


class FlashContextBudgetError(FlashExecutorError):
    """Violación de la Ley 5: El prompt del paquete supera el presupuesto o 12,000 tokens BPE."""


class FlashQuotaExhaustedError(FlashExecutorError):
    """Excepción de control para errores HTTP 429 / Rate Limit / Corte de créditos (Ley 6)."""


# ==============================================================================
# 2. CONTRATOS PYDANTIC V2 (LEYES 1, 2, 5 Y 6)
# ==============================================================================

FLASH_MAX_ACTIVE_TOKENS: int = 12000


class PackageExecutionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    CERTIFIED = "CERTIFIED"
    PAUSED_RATE_LIMIT = "PAUSED_RATE_LIMIT"
    FAILED = "FAILED"


class FlashMicroPackage(BaseModel):
    """
    Contrato formal de un Micro-Paquete Atómico (Ley 2: 1 archivo impl + 1 archivo test).
    """
    class Config:
        extra = "forbid"
        frozen = True

    package_id: str = Field(..., pattern=r"^PKG-[0-9]{3,6}$")
    ticket_id: str = Field(..., pattern=r"^TICK-[0-9]{4,8}$")
    objective: str = Field(...)
    target_impl_file: str = Field(..., description="Único archivo de producción a escribir en este turno.")
    target_test_file: str = Field(..., description="Único archivo de prueba a escribir en este turno.")
    dependency_files: List[str] = Field(
        default_factory=list,
        description="Archivos existentes cuyas firmas 1-Hop se pre-digieren e inyectan (Ley 1)."
    )
    required_type_contracts: List[TypeContract] = Field(default_factory=list)
    required_function_signatures: List[FunctionSignatureSpec] = Field(...)
    required_invariants: List[str] = Field(...)
    expected_failure_pattern: str = Field(default="AssertionError")
    max_tokens_budget: int = Field(default=FLASH_MAX_ACTIVE_TOKENS, ge=1000, le=FLASH_MAX_ACTIVE_TOKENS)
    max_attempts: int = Field(default=3, ge=1, le=5)

    @field_validator("target_impl_file", "target_test_file")
    @classmethod
    def validate_single_clean_path(cls, v: str) -> str:
        norm = v.replace("\\", "/").strip()
        if not norm or ".." in norm or "," in norm or ";" in norm or "\n" in norm:
            raise AtomicPackageViolationError(
                f"Ruta inválida o intento de empaquetar múltiples archivos en un campo escalar: '{v}'"
            )
        if not norm.endswith(".py"):
            raise AtomicPackageViolationError(f"El micro-paquete debe apuntar a un archivo Python (.py): '{norm}'")
        return norm

    @model_validator(mode="after")
    def validate_test_vs_impl_separation(self) -> FlashMicroPackage:
        if self.target_impl_file == self.target_test_file:
            raise AtomicPackageViolationError("target_impl_file y target_test_file no pueden ser el mismo archivo.")
        test_norm = self.target_test_file.lower()
        impl_norm = self.target_impl_file.lower()
        test_path_obj = Path(test_norm)
        is_in_tests_dir = "tests" in test_path_obj.parts or test_norm.startswith("tests/")
        starts_with_test = test_path_obj.name.startswith("test_")
        if not (is_in_tests_dir or starts_with_test):
            raise AtomicPackageViolationError(
                f"target_test_file debe ubicarse en tests/ o comenzar con 'test_': {self.target_test_file}"
            )
        if impl_norm.startswith("tests/") or Path(impl_norm).name.startswith("test_"):
            raise AtomicPackageViolationError(
                f"target_impl_file no puede ser un archivo de pruebas: {self.target_impl_file}"
            )
        return self


class FlashExecutionPlan(BaseModel):
    """Plan Maestro compuesto por una secuencia ordenada de Micro-Paquetes Atómicos."""
    class Config:
        extra = "forbid"
        frozen = True

    plan_id: str = Field(...)
    title: str = Field(...)
    workspace_root: str
    packages: List[FlashMicroPackage] = Field(...)

    @model_validator(mode="after")
    def validate_unique_package_ids(self) -> FlashExecutionPlan:
        seen = set()
        for pkg in self.packages:
            if pkg.package_id in seen:
                raise ValueError(f"package_id duplicado en el plan: {pkg.package_id}")
            seen.add(pkg.package_id)
        return self


class PackageCheckpointRecord(BaseModel):
    """Registro inmutable en disco de un paquete procesado (Ley 6)."""
    class Config:
        extra = "forbid"
        frozen = True

    package_id: str
    status: PackageExecutionStatus
    attempts_used: int = 0
    test_merkle_hash: str = ""
    impl_sha256: str = ""
    test_sha256: str = ""
    git_checkpoint_ref: str = ""
    active_tokens_used: int = 0
    last_error: str = ""
    updated_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FlashWALState(BaseModel):
    """Estado global del Write-Ahead Log en disco para reanudación ante errores 429."""
    class Config:
        extra = "forbid"
        frozen = True

    plan_id: str
    workspace_root: str
    current_package_index: int = 0
    plan_status: Literal["RUNNING", "PAUSED_RATE_LIMIT", "COMPLETED", "FAILED"] = "RUNNING"
    packages_state: Dict[str, PackageCheckpointRecord] = Field(default_factory=dict)
    updated_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# 3. LEY 3: GUARDIÁN AST CERO PLACEHOLDERS (FlashASTZeroPlaceholderGuard)
# ==============================================================================

class FlashASTZeroPlaceholderGuard:
    """
    Erradica el sesgo de atajos de Gemini 3.8 Flash inspeccionando el AST y los tokens léxicos.
    Prohíbe de forma absoluta:
      1. pass dentro de funciones, métodos o manejadores de excepciones.
      2. Ellipsis (...) como sentencia en cuerpos de funciones/métodos/clases.
      3. raise NotImplementedError o NotImplemented.
      4. Comentarios o docstrings con marcadores de atajo prohibidos.
    """

    _M_T = "".join(["T", "O", "D", "O"])
    _M_F = "".join(["F", "I", "X", "M", "E"])
    _M_X = "".join(["X", "X", "X"])
    _M_H = "".join(["H", "A", "C", "K"])
    _M_P = "".join(["P", "L", "A", "C", "E", "H", "O", "L", "D", "E", "R"])
    _M_S = "".join(["S", "T", "U", "B"])

    FORBIDDEN_MARKERS: Tuple[str, ...] = (_M_T, _M_F, _M_X, _M_H, _M_P, _M_S)

    @classmethod
    def audit_code(cls, code: str, filename: str = "<flash_target>", is_test_file: bool = False) -> List[str]:
        violations: List[str] = []

        if not code or not code.strip():
            return [f"Ley 3 Violada ({filename}): El archivo está vacío."]

        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as exc:
            return [f"Error de sintaxis en {filename} (Línea {exc.lineno}): {exc.msg}"]

        # 1. Inspección de comentarios y tokens léxicos
        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            for tok_type, tok_str, start_pos, _, _ in tokens:
                if tok_type in (tokenize.COMMENT, tokenize.STRING):
                    upper_tok = tok_str.upper()
                    for marker in cls.FORBIDDEN_MARKERS:
                        if cls._contains_marker_word(upper_tok, marker):
                            violations.append(
                                f"Ley 3 Violada ({filename}:{start_pos[0]}): Marcador prohibido '{marker}' "
                                f"detectado en comentario o literal."
                            )
        except tokenize.TokenError as exc:
            violations.append(f"Error léxico en {filename}: {exc}")

        # 2. Inspección profunda del AST para pass, Ellipsis y NotImplementedError
        reported_pass_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Pass):
                        reported_pass_lines.add(child.lineno)
                        violations.append(
                            f"Ley 3 Violada ({filename}:{child.lineno}): Sentencia 'pass' prohibida "
                            f"dentro de la función '{node.name}'."
                        )
                    elif (
                        isinstance(child, ast.Expr)
                        and isinstance(child.value, ast.Constant)
                        and child.value.value is Ellipsis
                    ):
                        violations.append(
                            f"Ley 3 Violada ({filename}:{child.lineno}): Placeholder Ellipsis ('...') "
                            f"prohibido en la función '{node.name}'."
                        )

            elif isinstance(node, ast.ClassDef):
                for stmt in node.body:
                    if (
                        isinstance(stmt, ast.Expr)
                        and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is Ellipsis
                    ):
                        violations.append(
                            f"Ley 3 Violada ({filename}:{stmt.lineno}): Placeholder Ellipsis ('...') "
                            f"prohibido en cuerpo de clase '{node.name}'."
                        )
                    elif isinstance(stmt, ast.Pass):
                        reported_pass_lines.add(stmt.lineno)
                        violations.append(
                            f"Ley 3 Violada ({filename}:{stmt.lineno}): Sentencia 'pass' prohibida "
                            f"en cuerpo de clase '{node.name}'."
                        )

            elif isinstance(node, ast.Pass) and not is_test_file and node.lineno not in reported_pass_lines:
                reported_pass_lines.add(node.lineno)
                violations.append(
                    f"Ley 3 Violada ({filename}:{node.lineno}): Sentencia 'pass' prohibida en código de producción."
                )

            elif isinstance(node, ast.Raise) and node.exc is not None:
                exc_name = cls._extract_exception_name(node.exc)
                if exc_name in ("NotImplementedError", "NotImplemented"):
                    violations.append(
                        f"Ley 3 Violada ({filename}:{node.lineno}): 'raise {exc_name}' prohibido."
                    )

        # 3. Integrar auditoría con ASTGuard de v5_goal_loop_tdd
        if not is_test_file:
            v5_violations = ASTGuard.audit_production_code(code, filename=filename, allow_mocks=False)
            violations.extend(v5_violations)
        else:
            assert_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            if not assert_nodes:
                violations.append(f"Ley 4 Violada ({filename}): El archivo de test no contiene sentencias 'assert'.")
            self_integrity = ASTGuard.audit_test_file_integrity(tree, tree)
            violations.extend(self_integrity)

        return violations

    @classmethod
    def audit_file(cls, file_path: Path, is_test_file: bool = False) -> List[str]:
        if not file_path.exists():
            return [f"Archivo no encontrado para auditoría AST: {file_path}"]
        content = file_path.read_text(encoding="utf-8")
        return cls.audit_code(content, filename=file_path.name, is_test_file=is_test_file)

    @staticmethod
    def _extract_exception_name(exc_node: ast.AST) -> str:
        if isinstance(exc_node, ast.Name):
            return exc_node.id
        if isinstance(exc_node, ast.Call):
            if isinstance(exc_node.func, ast.Name):
                return exc_node.func.id
            if isinstance(exc_node.func, ast.Attribute):
                return exc_node.func.attr
        if isinstance(exc_node, ast.Attribute):
            return exc_node.attr
        return ""

    @staticmethod
    def _contains_marker_word(upper_text: str, marker: str) -> bool:
        pattern = rf"\b{re.escape(marker)}\b"
        return bool(re.search(pattern, upper_text))


# ==============================================================================
# 4. LEYES 1, 5 Y 7: CONSTRUCTOR DE CONTEXTO PRE-DIGERIDO Y PROMPT DISPARADOR
# ==============================================================================

class PreDigestedContextBuilder:
    """
    Extrae firmas 1-Hop de archivos dependientes (Ley 1), comprime logs con
    SurgicalLogCrusher (Ley 5), verifica que el presupuesto total sea <12,000 tokens
    con BpeTokenEstimator y renderiza la plantilla exacta de disparo (Ley 7).
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.crusher = SurgicalLogCrusher(workspace_root=str(self.workspace_root))
        self.pruner = CallGraphASTPruner()

    def extract_predigested_signatures(self, dependency_files: Sequence[str]) -> str:
        """
        Extrae todas las firmas públicas (clases, métodos, funciones, constantes tipadas)
        de los archivos de dependencia declarados sin que Flash tenga que adivinarlas.
        """
        if not dependency_files:
            return "# [Sin dependencias externas requeridas para este micro-paquete]"

        blocks: List[str] = []
        for rel_path in dependency_files:
            full_path = (self.workspace_root / rel_path).resolve()
            if not full_path.exists() or not full_path.is_file():
                raise PreFlightDependencyError(
                    f"Ley 1 Violada: El archivo de dependencia '{rel_path}' no existe en {self.workspace_root}."
                )
            raw_code = full_path.read_text(encoding="utf-8")
            pruned = self._extract_ast_signatures_clean(raw_code, rel_path)
            blocks.append(f"# === ARCHIVO: {rel_path} ===\n{pruned}")

        return "\n\n".join(blocks)

    def _extract_ast_signatures_clean(self, source_code: str, rel_path: str) -> str:
        """
        Extrae definiciones de clases (con campos tipados y firmas de métodos)
        y firmas de funciones de nivel superior usando ast.
        """
        try:
            tree = ast.parse(source_code, filename=rel_path)
        except SyntaxError:
            return self.pruner.prune_python(source_code, hop=1)

        lines: List[str] = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                lines.append(ast.unparse(node))
            elif isinstance(node, ast.Assign):
                lines.append(ast.unparse(node))
            elif isinstance(node, ast.AnnAssign):
                lines.append(ast.unparse(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(self._format_function_sig(node, indent=0))
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) for b in node.bases]
                base_str = f"({', '.join(bases)})" if bases else ""
                lines.append(f"class {node.name}{base_str}:")
                has_members = False
                for sub in node.body:
                    if isinstance(sub, (ast.AnnAssign, ast.Assign)):
                        lines.append(f"    {ast.unparse(sub)}")
                        has_members = True
                    elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        lines.append(self._format_function_sig(sub, indent=4))
                        has_members = True
                if not has_members:
                    lines.append("    # [Sin miembros adicionales]")
        return "\n".join(lines)

    @staticmethod
    def _format_function_sig(fn: ast.FunctionDef | ast.AsyncFunctionDef, indent: int = 0) -> str:
        prefix = " " * indent
        async_kw = "async " if isinstance(fn, ast.AsyncFunctionDef) else ""
        args_str = ast.unparse(fn.args)
        ret_str = f" -> {ast.unparse(fn.returns)}" if fn.returns else ""
        decorators = [f"{prefix}@{ast.unparse(d)}" for d in fn.decorator_list]
        sig_line = f"{prefix}{async_kw}def {fn.name}({args_str}){ret_str}:  # [Firma Pre-Digerida]"
        return "\n".join(decorators + [sig_line])

    def render_contract_block(self, package: FlashMicroPackage) -> str:
        parts: List[str] = []
        for tc in package.required_type_contracts:
            parts.append(f"# TypeContract: {tc.type_name} ({tc.language})\n{tc.schema_definition}")
        for fn in package.required_function_signatures:
            pre = "; ".join(fn.pre_conditions) if fn.pre_conditions else "Ninguna"
            post = "; ".join(fn.post_conditions) if fn.post_conditions else "Ninguna"
            parts.append(f"{fn.signature}\n    # Pre-condiciones: {pre}\n    # Post-condiciones: {post}")
        return "\n\n".join(parts) if parts else "# [Sin contratos específicos definidos]"

    def build_dispatch_prompt(
        self,
        plan: FlashExecutionPlan,
        package: FlashMicroPackage,
        package_index: int,
        raw_stdout: str = "",
        raw_stderr: str = "",
        last_exit_code: int = 0,
        ast_violations: Optional[List[str]] = None,
    ) -> Tuple[str, int]:
        """
        Ensambla el Prompt de Disparo (Ley 7), comprime logs con SurgicalLogCrusher (Ley 5)
        y garantiza que el conteo total de tokens BPE sea <= max_tokens_budget (<12,000).
        """
        predigested_sigs = self.extract_predigested_signatures(package.dependency_files)
        contract_code = self.render_contract_block(package)
        invariants_bullets = "\n".join(f"- {inv}" for inv in package.required_invariants)

        if raw_stdout or raw_stderr or ast_violations:
            crushed_log = self.crusher.crush(raw_stdout, raw_stderr, exit_code=last_exit_code)
            if ast_violations:
                viol_str = "\n".join(f"!ast_veto: {v}" for v in ast_violations)
                diagnostic_block = f"{crushed_log}\n{viol_str}" if crushed_log.strip() else viol_str
            else:
                diagnostic_block = crushed_log
        else:
            diagnostic_block = "[ESTADO INICIAL LIMPIO: Intento 1 — Sin errores previos]"

        prompt = (
            "# [SISTEMA: EJECUTOR DETERMINISTA GEMINI 3.8 FLASH — MODO CERO ATAJOS]\n"
            "Operas bajo el arnés `v6_flash_executor`. Tu presupuesto activo está acotado a <12,000 tokens.\n"
            "Cumple estrictamente las siguientes invariantes o el Gatekeeper rechazará tu entrega por AST:\n\n"
            "1. PROHIBIDO ADIVINAR FIRMAS: Usa ÚNICAMENTE las firmas, tipos y rutas declaradas en el [BLOQUE 2]. "
            "No inventes métodos ni argumentos.\n"
            "2. ALCANCE ATÓMICO (1+1): En este turno SOLO tienes permitido tocar:\n"
            f"   - Archivo de Prueba: `{package.target_test_file}`\n"
            f"   - Archivo de Implementación: `{package.target_impl_file}`\n"
            "   Prohibido crear o modificar cualquier otro archivo.\n"
            "3. PROHIBICIÓN ABSOLUTA POR AST DE PLACEHOLDERS: Está prohibido escribir `pass` (en funciones/métodos), "
            "`...` (Ellipsis), `raise NotImplementedError`, o comentarios/docstrings con "
            + ", ".join(f"`{m}`" for m in FlashASTZeroPlaceholderGuard.FORBIDDEN_MARKERS)
            + ". Implementa el 100% de la lógica real.\n"
            "4. CICLO DETERMINISTA DE 5 PASOS (OBLIGATORIO EN ESTE ORDEN):\n"
            f"   - PASO 1 (WRITE TEST): Escribe la suite de pruebas completa en `{package.target_test_file}` "
            "cubriendo todos los casos borde del contrato.\n"
            f"   - PASO 2 (RUN RED): Ejecuta `pytest {package.target_test_file} -v` y verifica que FALLE "
            f"(`exit_code != 0`) con `{package.expected_failure_pattern}`. A partir de este instante, "
            f"`{package.target_test_file}` queda CONGELADO por hash Merkle SHA-256.\n"
            f"   - PASO 3 (WRITE CODE): Escribe la implementación completa y definitiva en `{package.target_impl_file}` "
            "sin tocar el archivo de test.\n"
            f"   - PASO 4 (RUN GREEN): Ejecuta `pytest {package.target_test_file} -v --strict-markers -W error` "
            "y verifica `exit_code == 0` con 0 tests skipped.\n"
            "   - PASO 5 (RUN ASTGUARD): Ejecuta la validación estática `ASTGuard` + `FlashASTZeroPlaceholderGuard` "
            "sobre ambos archivos.\n\n"
            "---\n"
            "## [BLOQUE 1: IDENTIDAD DEL MICRO-PAQUETE]\n"
            f"- **Plan ID:** `{plan.plan_id}`\n"
            f"- **Package ID:** `{package.package_id}` (Paquete {package_index + 1} de {len(plan.packages)})\n"
            f"- **Objetivo Verificable:** {package.objective}\n"
            f"- **Archivo de Implementación (WRITE en Paso 3):** `{package.target_impl_file}`\n"
            f"- **Archivo de Test (WRITE en Paso 1, READ-ONLY en Paso 3):** `{package.target_test_file}`\n"
            f"- **Patrón de Fallo Esperado en Fase Red:** `{package.expected_failure_pattern}`\n\n"
            "---\n"
            "## [BLOQUE 2: FIRMAS EXTERNAS PRE-DIGERIDAS E INMUTABLES (1-HOP AST)]\n"
            "*(Usa estas firmas literalmente. No leas otros archivos para buscarlas ni alteres sus tipos)*\n"
            f"```python\n{predigested_sigs}\n```\n\n"
            "---\n"
            f"## [BLOQUE 3: CONTRATO EXACTO DE TIPOS Y FIRMAS A IMPLEMENTAR EN `{package.target_impl_file}`]\n"
            f"```python\n{contract_code}\n```\n\n"
            "### Invariantes de Dominio y Casos Borde Obligatorios:\n"
            f"{invariants_bullets}\n\n"
            "---\n"
            "## [BLOQUE 4: TELEMETRÍA COMPRIMIDA DEL INTENTO PREVIO (SURGICAL LOG CRUSHER)]\n"
            f"```text\n{diagnostic_block}\n```\n\n"
            "---\n"
            "## [BLOQUE 5: ORDEN DE ACCIÓN INMEDIATA]\n"
            "Ejecuta ahora la secuencia `Write Test -> Run Red -> Write Code -> Run Green -> Run ASTGuard` "
            f"para el paquete `{package.package_id}`. No emitas explicaciones conversacionales previas: actúa "
            "directamente con las herramientas y reporta al final el hash Merkle del test, el resultado de "
            "`pytest` y el veredicto `ASTGuard: 0 VIOLATIONS`."
        )

        token_count = BpeTokenEstimator.count(prompt)
        limit = min(package.max_tokens_budget, FLASH_MAX_ACTIVE_TOKENS)
        if token_count > limit:
            raise FlashContextBudgetError(
                f"Ley 5 Violada: El prompt del paquete {package.package_id} consume {token_count} tokens BPE, "
                f"excediendo el límite estricto de {limit} tokens."
            )

        return prompt, token_count


# ==============================================================================
# 5. LEY 6: CHECKPOINT WAL EN DISCO Y RESILIENCIA ANTE ERRORES 429
# ==============================================================================

class FlashCheckpointWAL:
    """
    Persistencia atómica en disco después de cada paquete aprobado.
    Garantiza resiliencia total ante errores HTTP 429, agotamiento de créditos o reinicios.
    """

    def __init__(self, wal_path: Path):
        self.wal_path = wal_path.resolve()
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)

    def load_or_init(self, plan: FlashExecutionPlan) -> FlashWALState:
        if self.wal_path.exists():
            try:
                data = json.loads(self.wal_path.read_text(encoding="utf-8"))
                state = FlashWALState.model_validate(data)
                if state.plan_id == plan.plan_id:
                    for pkg in plan.packages:
                        if pkg.package_id not in state.packages_state:
                            state.packages_state[pkg.package_id] = PackageCheckpointRecord(
                                package_id=pkg.package_id,
                                status=PackageExecutionStatus.PENDING,
                            )
                    return state
            except Exception as exc:
                logger.debug("No se pudo cargar WAL previo, se inicializa nuevo estado: %s", exc)

        state = FlashWALState(
            plan_id=plan.plan_id,
            workspace_root=str(Path(plan.workspace_root).resolve()),
            current_package_index=0,
            plan_status="RUNNING",
            packages_state={
                pkg.package_id: PackageCheckpointRecord(
                    package_id=pkg.package_id,
                    status=PackageExecutionStatus.PENDING,
                )
                for pkg in plan.packages
            },
        )
        self.save(state)
        return state

    def save(self, state: FlashWALState) -> None:
        state.updated_at_utc = datetime.now(timezone.utc).isoformat()
        tmp_path = self.wal_path.with_suffix(".wal.tmp")
        payload = state.model_dump_json(indent=2)
        tmp_path.write_text(payload, encoding="utf-8")
        os.replace(tmp_path, self.wal_path)

    @staticmethod
    def compute_file_sha256(file_path: Path) -> str:
        if not file_path.exists() or not file_path.is_file():
            return ""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def verify_certified_package_on_disk(
        self,
        workspace_root: Path,
        package: FlashMicroPackage,
        record: PackageCheckpointRecord,
    ) -> bool:
        """
        Verifica criptográficamente que un paquete marcado como CERTIFIED en el WAL
        mantenga intactos sus archivos de implementación y de prueba en disco.
        """
        if record.status != PackageExecutionStatus.CERTIFIED:
            return False
        impl_path = workspace_root / package.target_impl_file
        test_path = workspace_root / package.target_test_file
        if not impl_path.exists() or not test_path.exists():
            return False
        if self.compute_file_sha256(impl_path) != record.impl_sha256:
            return False
        if self.compute_file_sha256(test_path) != record.test_sha256:
            return False
        current_merkle = MerkleTestEngine.calculate_merkle_tests_hash(
            workspace_root, [package.target_test_file]
        )
        return current_merkle == record.test_merkle_hash


# ==============================================================================
# 6. REPORTES DETERMINISTAS
# ==============================================================================

@dataclass
class PackageExecutionReport:
    package_id: str
    certified: bool
    skipped_from_checkpoint: bool
    attempts: int
    active_tokens: int
    test_merkle_hash: str
    git_checkpoint_ref: str
    crushed_log: str
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanExecutionSummary:
    plan_id: str
    status: Literal["COMPLETED", "PAUSED_RATE_LIMIT", "FAILED"]
    certified_packages: int
    total_packages: int
    resumed_from_checkpoint_count: int
    package_reports: List[PackageExecutionReport] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format_markdown_report(self) -> str:
        lines = [
            f"# Resumen de Ejecución del Plan: `{self.plan_id}`",
            f"- **Estado Global:** {self.status}",
            f"- **Paquetes Certificados:** {self.certified_packages} / {self.total_packages}",
            f"- **Reanudados desde Checkpoint:** {self.resumed_from_checkpoint_count}",
            "",
            "## Detalle por Paquete",
            "| Paquete | Certificado | Saltado (WAL) | Intentos | Tokens | Hash Merkle | Violaciones |",
            "| :--- | :---: | :---: | :---: | :---: | :--- | :--- |",
        ]
        for r in self.package_reports:
            v_str = f"{len(r.violations)} violaciones" if r.violations else "0"
            m_hash = f"{r.test_merkle_hash[:12]}..." if r.test_merkle_hash else "N/A"
            lines.append(
                f"| `{r.package_id}` | {'SI' if r.certified else 'NO'} | "
                f"{'SI' if r.skipped_from_checkpoint else 'NO'} | {r.attempts} | {r.active_tokens} | "
                f"`{m_hash}` | {v_str} |"
            )
        return "\n".join(lines)


# ==============================================================================
# 7. ORQUESTADOR DETERMINISTA PRINCIPAL (FlashDeterministicExecutor)
# ==============================================================================

class FlashDeterministicExecutor:
    """
    Motor de Ejecución Determinista para Gemini 3.8 Flash.
    Acopla:
      - PreDigestedContextBuilder (Ley 1, Ley 5, Ley 7)
      - FlashMicroPackage Validation (Ley 2)
      - FlashASTZeroPlaceholderGuard + ASTGuard (Ley 3)
      - Ciclo Write Test -> Run Red -> Write Code -> Run Green -> Run ASTGuard (Ley 4)
      - FlashCheckpointWAL + GitTransactionEngine (Ley 6)
      - AsymmetricUARBridge + BlackboardEngine (Trazabilidad y recibos HMAC)
    """

    def __init__(
        self,
        plan: FlashExecutionPlan,
        wal_path: Optional[Path] = None,
        blackboard: Optional[BlackboardEngine] = None,
        uar_bridge: Optional[AsymmetricUARBridge] = None,
    ):
        self.plan = plan
        self.workspace_root = Path(plan.workspace_root).resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        default_wal = self.workspace_root / ".aleph" / "checkpoints" / f"{plan.plan_id}.wal.json"
        self.wal = FlashCheckpointWAL(wal_path or default_wal)
        self.context_builder = PreDigestedContextBuilder(self.workspace_root)
        self.blackboard = blackboard or BlackboardEngine()
        self.uar_bridge = uar_bridge or AsymmetricUARBridge()
        self.git_engine = GitTransactionEngine(self.workspace_root)
        self.sandbox = PhysicalPermissionSandbox()

    def execute_plan(
        self,
        test_writer_fn: Callable[[FlashMicroPackage, str], str],
        code_writer_fn: Callable[[FlashMicroPackage, str, str], str],
    ) -> PlanExecutionSummary:
        """
        Ejecuta o reanuda el plan completo paquete por paquete.
        - test_writer_fn(package, dispatch_prompt) -> test_code_str
        - code_writer_fn(package, dispatch_prompt, frozen_test_code) -> impl_code_str
        Si ocurre un corte por cuota o HTTP 429, guarda el checkpoint en estado
        PAUSED_RATE_LIMIT y retorna de manera segura para reanudación posterior.
        """
        wal_state = self.wal.load_or_init(self.plan)
        if not self.git_engine.active_branch:
            self.git_engine.begin_transaction(self.plan.plan_id)

        reports: List[PackageExecutionReport] = []
        resumed_count = 0
        certified_count = 0

        for idx, pkg in enumerate(self.plan.packages):
            rec = wal_state.packages_state.get(pkg.package_id)
            if rec and self.wal.verify_certified_package_on_disk(self.workspace_root, pkg, rec):
                resumed_count += 1
                certified_count += 1
                reports.append(
                    PackageExecutionReport(
                        package_id=pkg.package_id,
                        certified=True,
                        skipped_from_checkpoint=True,
                        attempts=rec.attempts_used,
                        active_tokens=rec.active_tokens_used,
                        test_merkle_hash=rec.test_merkle_hash,
                        git_checkpoint_ref=rec.git_checkpoint_ref,
                        crushed_log="[RESUMED_FROM_DISK_CHECKPOINT]",
                    )
                )
                continue

            wal_state.current_package_index = idx
            wal_state.plan_status = "RUNNING"
            self.wal.save(wal_state)

            try:
                report = self.execute_single_package(
                    pkg=pkg,
                    package_index=idx,
                    test_writer_fn=test_writer_fn,
                    code_writer_fn=code_writer_fn,
                    wal_state=wal_state,
                )
                reports.append(report)
                if report.certified:
                    certified_count += 1
                else:
                    wal_state.plan_status = "FAILED"
                    self.wal.save(wal_state)
                    return PlanExecutionSummary(
                        plan_id=self.plan.plan_id,
                        status="FAILED",
                        certified_packages=certified_count,
                        total_packages=len(self.plan.packages),
                        resumed_from_checkpoint_count=resumed_count,
                        package_reports=reports,
                    )
            except Exception as exc:
                if self._is_quota_or_rate_limit_error(exc):
                    self._unlock_package_files(pkg)
                    pkg_rec = wal_state.packages_state[pkg.package_id]
                    pkg_rec.status = PackageExecutionStatus.PAUSED_RATE_LIMIT
                    pkg_rec.last_error = f"RATE_LIMIT_429: {exc}"
                    wal_state.plan_status = "PAUSED_RATE_LIMIT"
                    self.wal.save(wal_state)
                    return PlanExecutionSummary(
                        plan_id=self.plan.plan_id,
                        status="PAUSED_RATE_LIMIT",
                        certified_packages=certified_count,
                        total_packages=len(self.plan.packages),
                        resumed_from_checkpoint_count=resumed_count,
                        package_reports=reports,
                    )
                raise

        wal_state.plan_status = "COMPLETED"
        self.wal.save(wal_state)
        self.git_engine.commit_transaction()

        return PlanExecutionSummary(
            plan_id=self.plan.plan_id,
            status="COMPLETED",
            certified_packages=certified_count,
            total_packages=len(self.plan.packages),
            resumed_from_checkpoint_count=resumed_count,
            package_reports=reports,
        )

    def execute_single_package(
        self,
        pkg: FlashMicroPackage,
        package_index: int,
        test_writer_fn: Callable[[FlashMicroPackage, str], str],
        code_writer_fn: Callable[[FlashMicroPackage, str, str], str],
        wal_state: FlashWALState,
    ) -> PackageExecutionReport:
        """
        Ejecuta el ciclo estricto de la Ley 4 para un único Micro-Paquete Atómico:
        Write Test -> Run Red -> Write Code -> Run Green -> Run ASTGuard.
        """
        impl_path = self.workspace_root / pkg.target_impl_file
        test_path = self.workspace_root / pkg.target_test_file
        impl_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.parent.mkdir(parents=True, exist_ok=True)

        self._register_package_in_blackboard(pkg)
        pre_pkg_checkpoint = self.git_engine.commit_checkpoint(f"pre-{pkg.package_id}")

        try:
            # ------------------------------------------------------------------
            # PASO 1: WRITE TEST (Con impl bloqueado si ya existe)
            # ------------------------------------------------------------------
            self._unlock_package_files(pkg)
            if impl_path.exists():
                try:
                    impl_path.chmod(stat.S_IREAD)
                except Exception as exc:
                    logger.debug("No se pudo aplicar S_IREAD a impl_path: %s", exc)

            dispatch_prompt, active_tokens = self.context_builder.build_dispatch_prompt(
                plan=self.plan,
                package=pkg,
                package_index=package_index,
            )

            test_code = test_writer_fn(pkg, dispatch_prompt)
            test_ast_violations = FlashASTZeroPlaceholderGuard.audit_code(
                test_code, filename=pkg.target_test_file, is_test_file=True
            )
            if test_ast_violations:
                self._unlock_package_files(pkg)
                raise PlaceholderForbiddenError(
                    f"Violación AST en archivo de test '{pkg.target_test_file}': {test_ast_violations}"
                )

            test_path.write_text(test_code, encoding="utf-8")

            # ------------------------------------------------------------------
            # PASO 2: RUN RED (Debe fallar legítimamente y sellar Merkle Hash)
            # ------------------------------------------------------------------
            red_receipt = self._run_pytest_via_uar(pkg.target_test_file)
            if red_receipt.result_digest.exit_code == 0:
                self._unlock_package_files(pkg)
                self.git_engine.rollback_to(pre_pkg_checkpoint)
                raise RedPhaseViolationError(
                    f"Falso Red en {pkg.package_id}: la suite '{pkg.target_test_file}' pasó con exit_code 0 "
                    "antes de escribir la implementación."
                )

            combined_red_out = (
                red_receipt.result_digest.stdout_truncated + "\n" + red_receipt.result_digest.stderr_truncated
            )
            valid_red_signals = (
                pkg.expected_failure_pattern in combined_red_out
                or "ModuleNotFoundError" in combined_red_out
                or "ImportError" in combined_red_out
                or "AttributeError" in combined_red_out
            )
            if not valid_red_signals:
                self._unlock_package_files(pkg)
                self.git_engine.rollback_to(pre_pkg_checkpoint)
                raise RedPhaseViolationError(
                    f"Fase Red inválida en {pkg.package_id}: no se encontró '{pkg.expected_failure_pattern}' "
                    f"ni error de importación esperado. Salida: {combined_red_out[:400]}"
                )

            red_merkle_hash = MerkleTestEngine.calculate_merkle_tests_hash(
                self.workspace_root, [pkg.target_test_file]
            )
            red_checkpoint = self.git_engine.commit_checkpoint(f"red-{pkg.package_id}")
            self._post_red_packet_to_blackboard(pkg, test_code, combined_red_out, active_tokens)

            # ------------------------------------------------------------------
            # PASOS 3, 4 y 5: WRITE CODE -> RUN GREEN -> RUN ASTGUARD (Bucle <= max_attempts)
            # ------------------------------------------------------------------
            last_stdout = ""
            last_stderr = ""
            last_exit = 0
            last_violations: List[str] = []

            for attempt in range(1, pkg.max_attempts + 1):
                try:
                    test_path.chmod(stat.S_IREAD)
                except Exception as exc:
                    logger.debug("No se pudo aplicar S_IREAD a test_path: %s", exc)
                if impl_path.exists():
                    try:
                        impl_path.chmod(stat.S_IWRITE | stat.S_IREAD)
                    except Exception as exc:
                        logger.debug("No se pudo restaurar permisos en impl_path: %s", exc)

                retry_prompt, active_tokens = self.context_builder.build_dispatch_prompt(
                    plan=self.plan,
                    package=pkg,
                    package_index=package_index,
                    raw_stdout=last_stdout,
                    raw_stderr=last_stderr,
                    last_exit_code=last_exit,
                    ast_violations=last_violations,
                )

                impl_code = code_writer_fn(pkg, retry_prompt, test_code)
                impl_path.write_text(impl_code, encoding="utf-8")

                merkle_ok, merkle_msg = MerkleTestEngine.verify_merkle_invariant(
                    self.workspace_root, [pkg.target_test_file], red_merkle_hash
                )
                if not merkle_ok:
                    self._unlock_package_files(pkg)
                    self.git_engine.rollback_to(red_checkpoint)
                    raise GreenPhaseViolationError(merkle_msg)

                # PASO 4: RUN GREEN
                green_receipt = self._run_pytest_via_uar(pkg.target_test_file)
                last_exit = green_receipt.result_digest.exit_code
                last_stdout = green_receipt.result_digest.stdout_truncated
                last_stderr = green_receipt.result_digest.stderr_truncated

                if last_exit != 0:
                    last_violations = [f"Run Green falló con exit_code={last_exit}"]
                    self._unlock_package_files(pkg)
                    self.git_engine.rollback_to(red_checkpoint)
                    continue

                # PASO 5: RUN ASTGUARD
                ast_violations = FlashASTZeroPlaceholderGuard.audit_file(impl_path, is_test_file=False)
                test_recheck = FlashASTZeroPlaceholderGuard.audit_file(test_path, is_test_file=True)
                all_ast_violations = ast_violations + test_recheck

                if all_ast_violations:
                    last_violations = all_ast_violations
                    self._unlock_package_files(pkg)
                    self.git_engine.rollback_to(red_checkpoint)
                    continue

                # Certificar las 5 puertas con GatekeeperRuntime
                goal_spec = GoalSpec(
                    goal_id=f"{self.plan.plan_id[:8]}-{pkg.package_id}",
                    objective=pkg.objective,
                    target_files=[pkg.target_impl_file],
                    test_files=[pkg.target_test_file],
                    verification_contract=VerificationContract(
                        test_command=[sys.executable, "-m", "pytest", pkg.target_test_file, "-v"],
                        min_mutation_score=0.0,
                        mock_policy="STRICT_ZERO_MOCKS",
                    ),
                )
                gatekeeper = GatekeeperRuntime(self.workspace_root, goal_spec)
                gk_result = gatekeeper.verify_submission(
                    expected_merkle_tests=red_merkle_hash,
                    original_test_asts={pkg.target_test_file: test_code},
                )

                if not gk_result.passed:
                    last_violations = gk_result.violations
                    self._unlock_package_files(pkg)
                    self.git_engine.rollback_to(red_checkpoint)
                    continue

                # Paquete certificado: restaurar permisos y guardar Checkpoint WAL en disco
                self._unlock_package_files(pkg)
                git_cp = self.git_engine.commit_checkpoint(f"certified-{pkg.package_id}")
                crushed = self.context_builder.crusher.crush(last_stdout, last_stderr, exit_code=0)

                rec = PackageCheckpointRecord(
                    package_id=pkg.package_id,
                    status=PackageExecutionStatus.CERTIFIED,
                    attempts_used=attempt,
                    test_merkle_hash=red_merkle_hash,
                    impl_sha256=self.wal.compute_file_sha256(impl_path),
                    test_sha256=self.wal.compute_file_sha256(test_path),
                    git_checkpoint_ref=git_cp,
                    active_tokens_used=active_tokens,
                    last_error="",
                )
                wal_state.packages_state[pkg.package_id] = rec
                self.wal.save(wal_state)

                return PackageExecutionReport(
                    package_id=pkg.package_id,
                    certified=True,
                    skipped_from_checkpoint=False,
                    attempts=attempt,
                    active_tokens=active_tokens,
                    test_merkle_hash=red_merkle_hash,
                    git_checkpoint_ref=git_cp,
                    crushed_log=crushed,
                    violations=[],
                )

            # Si agotó intentos sin certificar
            self._unlock_package_files(pkg)
            self.git_engine.rollback_to(pre_pkg_checkpoint)
            crushed_fail = self.context_builder.crusher.crush(last_stdout, last_stderr, exit_code=last_exit)
            rec = PackageCheckpointRecord(
                package_id=pkg.package_id,
                status=PackageExecutionStatus.FAILED,
                attempts_used=pkg.max_attempts,
                test_merkle_hash=red_merkle_hash,
                git_checkpoint_ref=pre_pkg_checkpoint,
                active_tokens_used=active_tokens,
                last_error="; ".join(last_violations),
            )
            wal_state.packages_state[pkg.package_id] = rec
            self.wal.save(wal_state)

            return PackageExecutionReport(
                package_id=pkg.package_id,
                certified=False,
                skipped_from_checkpoint=False,
                attempts=pkg.max_attempts,
                active_tokens=active_tokens,
                test_merkle_hash=red_merkle_hash,
                git_checkpoint_ref=pre_pkg_checkpoint,
                crushed_log=crushed_fail,
                violations=last_violations,
            )

        except Exception as exc:
            self._unlock_package_files(pkg)
            if self._is_quota_or_rate_limit_error(exc):
                try:
                    self.git_engine.rollback_to(pre_pkg_checkpoint)
                except Exception as rollback_exc:
                    logger.debug("Fallo al revertir a pre_pkg_checkpoint: %s", rollback_exc)
            raise

    def _run_pytest_via_uar(self, rel_test_file: str) -> CanonicalExecutionReceipt:
        """Invoca pytest de forma segura sin shell mediante AsymmetricUARBridge (v5_uar_harness)."""
        task = CanonicalTask(
            timeout_seconds=30,
            execution_target=ExecutionTargetSpec(runtime=RuntimeTarget.MOCK_LOCAL),
            context_envelope=ContextEnvelope(
                workspace_root=str(self.workspace_root),
                active_files=[rel_test_file],
                environment_variables={"PYTHONPATH": str(self.workspace_root)},
            ),
            action_spec=ActionSpec(
                action_type=ActionType.RUN_TESTS,
                payload=ActionPayload(
                    executable=sys.executable,
                    arguments=["-m", "pytest", rel_test_file, "-v", "--tb=short"],
                ),
            ),
            security_context=SecurityContext(
                read_only_paths=[rel_test_file],
                forbidden_commands=["rm", "del", "format"],
            ),
        )
        receipt = self.uar_bridge.dispatch_to_data_plane(task)
        if not self.uar_bridge.verify_receipt(receipt):
            raise FlashExecutorError("Fallo de atestación criptográfica HMAC en recibo UAR.")
        return receipt

    def _register_package_in_blackboard(self, pkg: FlashMicroPackage) -> None:
        if self.blackboard.get_task_status(pkg.ticket_id) is None:
            ticket = TaskTicketPacket(
                ticket_id=pkg.ticket_id,
                title=f"Flash Package {pkg.package_id}"[:120],
                description=pkg.objective,
                acceptance_criteria=pkg.required_invariants,
                max_tdd_iterations=min(pkg.max_attempts, 3),
            )
            self.blackboard.ingest_ticket(ticket)

    def _post_red_packet_to_blackboard(
        self,
        pkg: FlashMicroPackage,
        test_code: str,
        red_stdout: str,
        token_cost: int,
    ) -> None:
        pattern = pkg.expected_failure_pattern
        if len(pattern) < 5:
            pattern = f"{pattern}_failure"
        red_pkt = TddRedPacket(
            ticket_id=pkg.ticket_id,
            test_files=[TestFileEntry(path=pkg.target_test_file, content=test_code)],
            execution_command=f"pytest {pkg.target_test_file}",
            expected_failure_pattern=pattern,
            red_phase_verified=True,
            red_phase_stdout=red_stdout[:2000],
        )
        env = ContextPacketEnvelope(
            ticket_id=pkg.ticket_id,
            producer_role=RoleType.TESTER_TDD,
            token_cost=token_cost,
            payload_json=red_pkt.model_dump_json(),
        )
        self.blackboard.post_packet(env)

    def _unlock_package_files(self, pkg: FlashMicroPackage) -> None:
        for rel in (pkg.target_impl_file, pkg.target_test_file):
            p = self.workspace_root / rel
            if p.exists():
                try:
                    p.chmod(stat.S_IWRITE | stat.S_IREAD)
                except Exception as exc:
                    logger.debug("No se pudo desbloquear archivo %s: %s", rel, exc)

    @staticmethod
    def _is_quota_or_rate_limit_error(exc: Exception) -> bool:
        if isinstance(exc, FlashQuotaExhaustedError):
            return True
        msg = str(exc).lower()
        return any(tok in msg for tok in ("429", "rate limit", "quota", "resource_exhausted", "credit"))
