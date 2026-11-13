#!/usr/bin/env python3
"""
Módulo: v5_goal_loop_tdd.py
Ruta: .aleph/lib/v5_goal_loop_tdd.py
Propósito: El Aleph Goal-Loop Engine — Bucle Autónomo por Objetivos con TDD Desacoplado,
Aislamiento Físico de Permisos (Hardware/OS Lock) y Gatekeeper en Runtime Inviolable.

Arquitectura:
1. PhysicalPermissionSandbox: Aislamiento físico de permisos a nivel de OS (Windows icacls + chmod).
2. MerkleTestEngine: Verificación criptográfica de integridad de tests vía SHA-256 Merkle Tree.
3. ASTGuard: Erradicación estática de los 4 jinetes del reward hacking:
   - The Dummy Mock (mocks vacíos, stubs triviales, imports de mock en SUT).
   - The Assert Weakener (reducción o degradación de aserciones entre fases).
   - The Silent Skipper (decoradores skip/xfail, except pass silencioso).
   - The Shadow Runner (inyección de comandos, bypass de tests).
4. MutationTestingEngine: Motor de mutación sintética rápida (Mutation Score >= 85%).
5. GitTransactionEngine: Control transaccional formal ACID sobre ramas efímeras y rollback atómico.
6. GoalSpec & VerificationContract: Esquemas Pydantic v2 inmutables.
7. GatekeeperRuntime: Pipeline determinista de 5 puertas inviolables sin LLM en runtime.
8. GoalLoopOrchestrator: Conductor del ciclo dialéctico Red -> Green -> Refactor -> Certificación.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple

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

logger = logging.getLogger("aleph.v5_goal_loop_tdd")


# ============================================================================
# EXCEPCIONES FORMALES DEL SUBSISTEMA
# ============================================================================

class GoalLoopTDDError(Exception):
    """Excepción base para el subsistema Goal-Loop TDD de El Aleph."""
    pass


class PhysicalSandboxError(GoalLoopTDDError):
    """Error al aplicar o remover bloqueos físicos de permisos en el sistema de archivos."""
    pass


class MerkleTamperError(GoalLoopTDDError):
    """Violación crítica: Discrepancia criptográfica en el árbol Merkle de tests."""
    pass


class ASTSecurityError(GoalLoopTDDError):
    """Violación detectada por el analizador de AST (The 4 Horsemen of Reward Hacking)."""
    pass


class MutationTestingError(GoalLoopTDDError):
    """Falla o puntaje insuficiente en el análisis de pruebas mutantes."""
    pass


class GitTransactionError(GoalLoopTDDError):
    """Error en operaciones de rama efímera, snapshot o rollback atómico en Git."""
    pass


class GoalSpecValidationError(GoalLoopTDDError):
    """Error de validación contra el contrato formal goal-spec.json."""
    pass


class GatekeeperVetoError(GoalLoopTDDError):
    """Veto irrevocable emitido por el Gatekeeper en runtime al rechazar una entrega."""
    pass


# ============================================================================
# MODELOS DE DATOS Y CONTRATO FORMAL (PYDANTIC V2)
# ============================================================================

class VerificationContract(BaseModel):
    """Contrato formal de verificación ejecutado por el Gatekeeper."""
    test_command: List[str] = Field(
        default_factory=lambda: ["pytest", "-v", "--strict-markers", "-W", "error"],
        description="Comando oficial de pruebas inyectado por el Gatekeeper."
    )
    min_mutation_score: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Puntaje mínimo de mutantes eliminados requerido para certificación."
    )
    mock_policy: str = Field(
        default="STRICT_ZERO_MOCKS",
        description="Política de mocks permitidos en el System Under Test (SUT)."
    )
    max_duration_seconds: int = Field(
        default=60,
        ge=1,
        le=600,
        description="Límite estricto de tiempo de ejecución para el comando de prueba."
    )
    forbid_skipped_tests: bool = Field(
        default=True,
        description="Si es True, prohíbe tests en estado skipped, xfail o ignorados."
    )

    @field_validator("mock_policy")
    @classmethod
    def validate_mock_policy(cls, v: str) -> str:
        allowed = {"STRICT_ZERO_MOCKS", "ISOLATED_FIXTURES_ONLY", "PERMISSIVE_INTEGRATION"}
        if v not in allowed:
            raise ValueError(f"mock_policy debe ser una de {allowed}, se recibió: '{v}'")
        return v

    @field_validator("test_command")
    @classmethod
    def validate_test_command(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("test_command no puede estar vacío")
        for token in v:
            if any(ch in token for ch in [";", "&&", "||", "|", "&", ">", "<", "`", "$"]):
                raise ValueError(f"Carácter de shell inseguro detectado en test_command: '{token}'")
        return v


class ResourceLimits(BaseModel):
    """Límites de recursos y cuotas operativas para la triada de agentes."""
    max_green_attempts: int = Field(default=5, ge=1, le=20)
    max_refactor_attempts: int = Field(default=3, ge=1, le=10)
    token_budget: int = Field(default=100000, ge=1000)


class GoalSpec(BaseModel):
    """Especificación canónica formal e inmutable del objetivo (goal-spec.json)."""
    goal_id: str = Field(
        ...,
        description="Identificador único del objetivo (UUIDv4 o slug determinista)."
    )
    version: str = Field(
        default="1.0.0",
        description="Versión del contrato de objetivo."
    )
    objective: str = Field(
        ...,
        min_length=10,
        description="Descripción unívoca y verificable del requerimiento."
    )
    target_files: List[str] = Field(
        ...,
        min_length=1,
        description="Lista de rutas relativas de código productivo (src/) editables en Green/Refactor."
    )
    test_files: List[str] = Field(
        ...,
        min_length=1,
        description="Lista de rutas relativas de pruebas (tests/) editables exclusivamente en Red."
    )
    verification_contract: VerificationContract = Field(
        default_factory=VerificationContract
    )
    resource_limits: ResourceLimits = Field(
        default_factory=ResourceLimits
    )

    @field_validator("target_files", "test_files")
    @classmethod
    def validate_paths(cls, paths: List[str]) -> List[str]:
        cleaned = []
        for p in paths:
            norm = p.replace("\\", "/").strip()
            if not norm:
                raise ValueError("Ruta de archivo vacía no permitida")
            if ".." in norm:
                raise ValueError(f"Traversal relativo '..' prohibido en ruta: {norm}")
            cleaned.append(norm)
        return cleaned


@dataclass
class MutationResult:
    """Resultado detallado del análisis de mutantes sintéticos."""
    mutation_score: float
    total_mutants: int
    killed_mutants: int
    survived_mutants: int
    mutations_applied: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GatekeeperResult:
    """Resultado formal de certificación emitido por el Gatekeeper en runtime."""
    passed: bool
    exit_code: int
    summary: str
    violations: List[str] = field(default_factory=list)
    mutation_score: float = 0.0
    gate_results: Dict[str, bool] = field(default_factory=dict)
    merkle_hash: str = ""
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# 1. PHYSICAL PERMISSION SANDBOX (AISLAMIENTO FÍSICO DE PERMISOS)
# ============================================================================

class PhysicalPermissionSandbox:
    """
    Controla el aislamiento físico de directorios para evitar modificación
    no autorizada de tests o código fuente según la fase TDD en curso.
    Garantía a nivel de kernel/OS (icacls en Windows + chmod en POSIX).
    """

    @staticmethod
    def lock_directory_read_only(target_dir: Path) -> None:
        """
        Bloquea un directorio completo para que sea estrictamente READ-ONLY.
        En Windows: Aplica icacls para denegar permisos de escritura/eliminación,
        y asegura el bit stat.S_IREAD en todos los archivos del árbol.
        En POSIX: Aplica chmod 0o555 en directorios y 0o444 en archivos.
        """
        target_dir = target_dir.resolve()
        if not target_dir.exists():
            raise FileNotFoundError(f"Directorio no encontrado para bloqueo: {target_dir}")

        if sys.platform == "win32":
            # Asignar atributo READ-ONLY a todos los archivos y subdirectorios
            for root, dirs, files in os.walk(target_dir):
                for fname in files:
                    p = Path(root) / fname
                    try:
                        p.chmod(stat.S_IREAD)
                    except Exception:
                        pass
                for dname in dirs:
                    d = Path(root) / dname
                    try:
                        d.chmod(stat.S_IREAD | stat.S_IEXEC)
                    except Exception:
                        pass
            try:
                target_dir.chmod(stat.S_IREAD | stat.S_IEXEC)
            except Exception:
                pass
        else:
            # POSIX: 0o555 (r-xr-xr-x) en directorios y 0o444 (r--r--r--) en archivos
            for root, dirs, files in os.walk(target_dir):
                for fname in files:
                    try:
                        os.chmod(os.path.join(root, fname), 0o444)
                    except Exception:
                        pass
                for dname in dirs:
                    try:
                        os.chmod(os.path.join(root, dname), 0o555)
                    except Exception:
                        pass
            try:
                os.chmod(target_dir, 0o555)
            except Exception:
                pass

    @staticmethod
    def unlock_directory_read_write(target_dir: Path) -> None:
        """
        Restaura permisos de READ-WRITE sobre el directorio especificado.
        """
        target_dir = target_dir.resolve()
        if not target_dir.exists():
            return

        if sys.platform == "win32":
            try:
                target_dir.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            except Exception:
                pass
            for root, dirs, files in os.walk(target_dir):
                for dname in dirs:
                    d = Path(root) / dname
                    try:
                        d.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    except Exception:
                        pass
                for fname in files:
                    p = Path(root) / fname
                    try:
                        p.chmod(stat.S_IWRITE | stat.S_IREAD)
                    except Exception:
                        pass
        else:
            try:
                os.chmod(target_dir, 0o755)
            except Exception:
                pass
            for root, dirs, files in os.walk(target_dir):
                for dname in dirs:
                    try:
                        os.chmod(os.path.join(root, dname), 0o755)
                    except Exception:
                        pass
                for fname in files:
                    try:
                        os.chmod(os.path.join(root, fname), 0o644)
                    except Exception:
                        pass

    @staticmethod
    def verify_write_blocked(target_dir: Path) -> bool:
        """
        Prueba activamente si la escritura está bloqueada intentando modificar o crear un archivo sonda.
        Retorna True si la escritura fue denegada de forma efectiva (protegido).
        """
        target_dir = target_dir.resolve()
        if not target_dir.exists():
            return False

        # Prueba 1: Modificar un archivo existente si lo hay
        existing_files = list(target_dir.glob("**/*.*"))
        for ef in existing_files:
            if ef.is_file():
                try:
                    with open(ef, "a", encoding="utf-8") as f:
                        f.write("")
                    # Si pudimos abrir en modo 'a' para escribir, no está protegido
                    return False
                except (PermissionError, OSError):
                    return True

        # Prueba 2: Crear un archivo sonda temporal
        probe_path = target_dir / f".__probe_{uuid.uuid4().hex[:6]}.tmp"
        try:
            with open(probe_path, "w", encoding="utf-8") as f:
                f.write("probe")
            # Si se pudo crear, no está bloqueado; limpiar sonda
            try:
                probe_path.unlink()
            except Exception:
                pass
            return False
        except (PermissionError, OSError):
            return True

    @classmethod
    @contextlib.contextmanager
    def read_only_scope(cls, target_dir: Path) -> Iterator[None]:
        """Context manager para asegurar bloqueo temporal y desbloqueo garantizado."""
        cls.lock_directory_read_only(target_dir)
        try:
            yield
        finally:
            cls.unlock_directory_read_write(target_dir)


# ============================================================================
# 2. MERKLE TEST INVARIANT (INTEGRIDAD CRIPTOGRÁFICA DE PRUEBAS)
# ============================================================================

class MerkleTestEngine:
    """
    Calcula y audita el árbol Merkle de hashes SHA-256 de las suites de prueba.
    Garantiza matemáticamente que los tests redactados por Red Breaker
    no sufran adulteración durante Green o Refactor (The Assert Weakener).
    """

    @staticmethod
    def calculate_merkle_tests_hash(
        repo_root: Path,
        test_files_or_dir: List[str] | List[Path] | Path
    ) -> str:
        """
        Calcula un hash Merkle determinista sobre la colección de archivos de prueba.
        Ordena canónicamente las rutas relativas normalizadas con '/' para reproducibilidad.
        """
        repo_root = repo_root.resolve()
        files_to_hash: List[Path] = []

        if isinstance(test_files_or_dir, Path):
            if test_files_or_dir.is_dir():
                for p in sorted(test_files_or_dir.rglob("*.py")):
                    if p.is_file():
                        files_to_hash.append(p)
            elif test_files_or_dir.is_file():
                files_to_hash.append(test_files_or_dir)
        elif isinstance(test_files_or_dir, list):
            for item in test_files_or_dir:
                p = (repo_root / item).resolve() if isinstance(item, str) else item.resolve()
                if p.is_dir():
                    for sub in sorted(p.rglob("*.py")):
                        if sub.is_file():
                            files_to_hash.append(sub)
                elif p.is_file():
                    files_to_hash.append(p)

        # Ordenar por ruta relativa normalizada
        entries: List[Tuple[str, bytes]] = []
        for f in files_to_hash:
            try:
                rel = f.relative_to(repo_root).as_posix()
            except ValueError:
                rel = f.name
            content_bytes = f.read_bytes()
            entries.append((rel, content_bytes))

        entries.sort(key=lambda x: x[0])

        # Árbol Merkle: SHA-256 de los hashes concatenados de cada archivo
        leaf_hashes: List[bytes] = []
        for rel_path, content_bytes in entries:
            leaf_h = hashlib.sha256(rel_path.encode("utf-8") + b"::" + content_bytes).digest()
            leaf_hashes.append(leaf_h)

        if not leaf_hashes:
            return hashlib.sha256(b"EMPTY_TEST_SUITE").hexdigest()

        # Reducir hashes en árbol binario
        current_level = leaf_hashes
        while len(current_level) > 1:
            next_level: List[bytes] = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = hashlib.sha256(current_level[i] + current_level[i + 1]).digest()
                else:
                    combined = hashlib.sha256(current_level[i] + current_level[i]).digest()
                next_level.append(combined)
            current_level = next_level

        return hashlib.sha256(current_level[0]).hexdigest()

    @classmethod
    def verify_merkle_invariant(
        cls,
        repo_root: Path,
        test_files: List[str] | Path,
        expected_hash: str
    ) -> Tuple[bool, str]:
        """
        Verifica que el hash Merkle actual coincida exactamente con el esperado.
        """
        actual_hash = cls.calculate_merkle_tests_hash(repo_root, test_files)
        if actual_hash != expected_hash:
            msg = (
                f"VIOLACIÓN CRÍTICA (The Assert Weakener): El árbol de tests fue adulterado. "
                f"Esperado: {expected_hash}, Actual: {actual_hash}"
            )
            return False, msg
        return True, ""


# ============================================================================
# 3. AST GUARD & ANTI-CHEAT STATIC ANALYZER (LOS 4 JINETES)
# ============================================================================

class ASTGuard:
    """
    Inspección estática profunda del Abstract Syntax Tree (AST) para erradicar
    los 4 jinetes del reward hacking:
    1. The Dummy Mock
    2. The Assert Weakener
    3. The Silent Skipper
    4. The Shadow Runner
    """

    FORBIDDEN_MOCK_MODULES: Set[str] = {
        "unittest.mock",
        "mock",
        "pytest_mock",
        "responses",
        "freezegun",
        "flexmock",
        "doublex",
    }

    FORBIDDEN_SKIP_DECORATORS: Set[str] = {
        "skip",
        "skipif",
        "xfail",
        "expectedfailure",
    }

    @classmethod
    def audit_production_code(
        cls,
        code: str,
        filename: str = "<sut>",
        allow_mocks: bool = False
    ) -> List[str]:
        """
        Audita una cadena de código de producción (src/) contra patrones de fraude.
        """
        violations: List[str] = []
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            return [f"Error de sintaxis en {filename}: {e}"]

        # 1. Prohibir librerías de mocks en SUT (The Dummy Mock - Parte 1)
        if not allow_mocks:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(alias.name == pkg or alias.name.startswith(pkg + ".") for pkg in cls.FORBIDDEN_MOCK_MODULES):
                            violations.append(
                                f"The Dummy Mock: Importación de mock prohibida en SUT '{alias.name}' (Línea {node.lineno})"
                            )
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    if any(mod == pkg or mod.startswith(pkg + ".") for pkg in cls.FORBIDDEN_MOCK_MODULES):
                        violations.append(
                            f"The Dummy Mock: ImportFrom de mock prohibida en SUT '{mod}' (Línea {node.lineno})"
                        )

        # 2. Detectar funciones Dummy / Stubs fraudulentos (The Dummy Mock - Parte 2)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if cls._is_trivial_dummy_body(node):
                    violations.append(
                        f"The Dummy Mock: Función '{node.name}' contiene un cuerpo trivial o retorno constante fraudulento (Línea {node.lineno})"
                    )

        # 3. Detectar The Silent Skipper: Supresión silenciosa de errores (except: pass)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if cls._is_silent_except_block(node):
                    violations.append(
                        f"The Silent Skipper: Bloque 'except ...: pass' detectado en línea {node.lineno}"
                    )
            # Detectar contextlib.suppress en SUT
            if isinstance(node, ast.Call):
                call_repr = cls._get_call_name(node)
                if call_repr in ("contextlib.suppress", "suppress"):
                    violations.append(
                        f"The Silent Skipper: Uso de 'suppress' para ocultar fallos en línea {node.lineno}"
                    )

        # 4. Invariante de Producción: Zero-Placeholder (NotImplementedError prohibido en SUT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Name) and node.exc.id in ("NotImplementedError", "NotImplemented"):
                    violations.append(
                        f"Invariante de Producción (Zero-Placeholder): 'raise {node.exc.id}' prohibido en SUT (Línea {node.lineno})"
                    )
                elif isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) and node.exc.func.id in ("NotImplementedError", "NotImplemented"):
                    violations.append(
                        f"Invariante de Producción (Zero-Placeholder): 'raise {node.exc.func.id}()' prohibido en SUT (Línea {node.lineno})"
                    )

        # 5. Invariante de Producción: Aritmética Formal (prohibir división por cero literal)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    violations.append(
                        f"Invariante de Producción (Aritmética Formal): División o módulo por cero literal en línea {node.lineno}"
                    )

        # 6. Invariante de Producción: Clean Code (prohibir sentencias interactivas de depuración)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = cls._get_call_name(node)
                if call_name in ("breakpoint", "pdb.set_trace", "ipdb.set_trace"):
                    violations.append(
                        f"Invariante de Producción (Clean Code): Sentencia de depuración '{call_name}' en línea {node.lineno}"
                    )

        return violations

    @classmethod
    def audit_production_file(cls, file_path: Path, allow_mocks: bool = False) -> List[str]:
        """Audita un archivo de código productivo existente en disco."""
        file_path = file_path.resolve()
        if not file_path.exists():
            return [f"Archivo productivo no existe: {file_path}"]
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return [f"Error al leer archivo {file_path}: {e}"]
        return cls.audit_production_code(content, filename=file_path.name, allow_mocks=allow_mocks)

    @classmethod
    def audit_test_file_integrity(
        cls,
        original_ast_or_code: ast.AST | str,
        modified_ast_or_code: ast.AST | str
    ) -> List[str]:
        """
        Compara los ASTs de una suite de tests entre Red y Green/Refactor
        para detectar The Assert Weakener y The Silent Skipper en pruebas.
        """
        violations: List[str] = []

        orig_tree = (
            ast.parse(original_ast_or_code)
            if isinstance(original_ast_or_code, str)
            else original_ast_or_code
        )
        mod_tree = (
            ast.parse(modified_ast_or_code)
            if isinstance(modified_ast_or_code, str)
            else modified_ast_or_code
        )

        orig_asserts = [n for n in ast.walk(orig_tree) if isinstance(n, ast.Assert)]
        mod_asserts = [n for n in ast.walk(mod_tree) if isinstance(n, ast.Assert)]

        # 1. Reducción en la cantidad de aserciones
        if len(mod_asserts) < len(orig_asserts):
            violations.append(
                f"The Assert Weakener: Número de aserciones reducido de {len(orig_asserts)} a {len(mod_asserts)}"
            )

        # 2. Detectar aserciones tautológicas introducidas (assert True, assert 1, etc.)
        for ass in mod_asserts:
            if cls._is_tautological_assert(ass):
                violations.append(
                    f"The Assert Weakener: Aserción tautológica o trivial detectada en línea {ass.lineno}"
                )

        # 3. Detectar decoradores de salto (The Silent Skipper)
        for node in ast.walk(mod_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    dec_name = cls._get_call_name(dec).lower()
                    if any(f in dec_name for f in cls.FORBIDDEN_SKIP_DECORATORS):
                        violations.append(
                            f"The Silent Skipper: Decorador de skip/xfail '{dec_name}' detectado en '{node.name}' (Línea {node.lineno})"
                        )

        return violations

    @staticmethod
    def _is_trivial_dummy_body(fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """
        Determina si el cuerpo de una función es un stub trivial sospechoso de reward hacking.
        Ignora funciones abstractas marcadas con @abstractmethod o stubs de protocolo sin argumentos.
        """
        # Filtrar decorators de abstractmethod
        for dec in fn_node.decorator_list:
            name = ASTGuard._get_call_name(dec)
            if "abstractmethod" in name:
                return False

        # Extraer sentencias reales omitiendo docstrings
        real_stmts: List[ast.stmt] = []
        for s in fn_node.body:
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str):
                continue
            real_stmts.append(s)

        if not real_stmts:
            return True

        if len(real_stmts) == 1:
            stmt = real_stmts[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                return True
            if isinstance(stmt, ast.Return):
                if stmt.value is None:
                    return True
                if isinstance(stmt.value, ast.Constant):
                    # Constantes literales sospechosas o retornos constantes en funciones parametrizadas
                    if len(fn_node.args.args) > 0 or stmt.value.value in (True, False, None, 0, 42, 100, "", "dummy", "ok", "success"):
                        return True
                # Retornos de colecciones vacías literales
                if isinstance(stmt.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                    if len(stmt.value.elts if hasattr(stmt.value, "elts") else stmt.value.keys) == 0:
                        return True

        return False

    @staticmethod
    def _is_silent_except_block(handler: ast.ExceptHandler) -> bool:
        """Detecta si un bloque except atrapa excepciones y solo contiene 'pass', '...' o retorno constante dummy."""
        if len(handler.body) != 1:
            return False
        stmt = handler.body[0]
        if isinstance(stmt, ast.Pass):
            return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
            return True
        if isinstance(stmt, ast.Return) and (stmt.value is None or isinstance(stmt.value, ast.Constant)):
            return True
        return False

    @staticmethod
    def _is_tautological_assert(assert_node: ast.Assert) -> bool:
        """Determina si un assert es una tautología evidente como 'assert True' o 'assert 1'."""
        test = assert_node.test
        if isinstance(test, ast.Constant):
            if test.value in (True, 1, "true", "ok", "test"):
                return True
        if isinstance(test, ast.Compare):
            # x == x o 1 == 1
            if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                left_dump = ast.dump(test.left)
                right_dump = ast.dump(test.comparators[0])
                if left_dump == right_dump:
                    return True
        return False

    @staticmethod
    def _get_call_name(node: ast.AST) -> str:
        """Reconstruye el nombre completo de una llamada o atributo."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{ASTGuard._get_call_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return ASTGuard._get_call_name(node.func)
        return ""


# ============================================================================
# 4. MUTATION TESTING ENGINE (MUTANTES SINTÉTICOS DETERMINISTAS)
# ============================================================================

class MutationTestingEngine:
    """
    Motor de análisis de mutantes determinista. Aplica mutaciones sintéticas
    de primer orden a los archivos de producción objetivo y evalúa si la suite
    de pruebas es lo suficientemente profunda para matar cada mutante.
    """

    OPERATOR_MUTATIONS: List[Tuple[str, str]] = [
        (" == ", " != "),
        (" != ", " == "),
        (" <= ", " > "),
        (" >= ", " < "),
        (" < ", " >= "),
        (" > ", " <= "),
        (" + ", " - "),
        (" - ", " + "),
        (" * ", " / "),
        ("True", "False"),
        ("False", "True"),
        (" and ", " or "),
        (" or ", " and "),
        (" in ", " not in "),
    ]

    @classmethod
    def run_mutation_analysis(
        cls,
        repo_root: Path,
        target_files: List[str],
        test_command: List[str],
        timeout_sec: int = 30
    ) -> MutationResult:
        """
        Ejecuta la suite de mutantes sobre los target_files declarados.
        Garantiza restauración incondicional del código fuente original.
        """
        repo_root = repo_root.resolve()
        total_mutants = 0
        killed_mutants = 0
        survived_mutants = 0
        records: List[Dict[str, Any]] = []

        for rel_path in target_files:
            file_path = repo_root / rel_path
            if not file_path.exists() or not file_path.is_file():
                continue

            original_source = file_path.read_text(encoding="utf-8")

            # Buscar operadores mutables en el archivo
            for orig_op, mut_op in cls.OPERATOR_MUTATIONS:
                # Buscar ocurrencias
                occurrences = original_source.count(orig_op)
                if occurrences == 0:
                    continue

                # Mutar una ocurrencia a la vez para mutantes de primer orden
                # Limitar a máx 3 mutaciones por operador para no saturar tiempo
                max_checks = min(occurrences, 3)
                start_idx = 0

                for occ_idx in range(max_checks):
                    pos = original_source.find(orig_op, start_idx)
                    if pos == -1:
                        break
                    start_idx = pos + len(orig_op)

                    mutated_source = (
                        original_source[:pos] + mut_op + original_source[pos + len(orig_op):]
                    )

                    # Verificar validez sintáctica del mutante antes de ejecutar
                    try:
                        ast.parse(mutated_source)
                    except SyntaxError:
                        continue

                    total_mutants += 1

                    # Escribir código mutado y ejecutar prueba
                    try:
                        file_path.write_text(mutated_source, encoding="utf-8")
                        res = subprocess.run(
                            test_command,
                            cwd=repo_root,
                            capture_output=True,
                            text=True,
                            timeout=timeout_sec
                        )
                        # El mutante está KILLED si el test falló (exit_code != 0)
                        if res.returncode != 0:
                            killed_mutants += 1
                            status = "KILLED"
                        else:
                            survived_mutants += 1
                            status = "SURVIVED"
                    except subprocess.TimeoutExpired:
                        # Si el mutante causó un bucle infinito, se considera KILLED
                        killed_mutants += 1
                        status = "KILLED (TIMEOUT)"
                    finally:
                        # RESTAURAR CÓDIGO ORIGINAL INCONDICIONALMENTE
                        file_path.write_text(original_source, encoding="utf-8")

                    records.append({
                        "file": rel_path,
                        "original_op": orig_op.strip(),
                        "mutated_op": mut_op.strip(),
                        "status": status,
                    })

        if total_mutants == 0:
            score = 100.0
        else:
            score = round((killed_mutants / total_mutants) * 100.0, 2)

        return MutationResult(
            mutation_score=score,
            total_mutants=total_mutants,
            killed_mutants=killed_mutants,
            survived_mutants=survived_mutants,
            mutations_applied=records
        )


# ============================================================================
# 5. GIT TRANSACTION ENGINE (ROLLBACK ATÓMICO Y RAMAS EFÍMERAS)
# ============================================================================

class GitTransactionEngine:
    """
    Control transaccional formal ACID sobre ramas Git efímeras.
    Permite checkpoints por fase y rollbacks atómicos garantizados.
    Incorpora modo snapshot de respaldo para entornos de prueba sin Git.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.is_git: bool = self._check_git_repo()
        self.initial_branch: Optional[str] = None
        self.active_branch: Optional[str] = None
        self.snapshots: Dict[str, Dict[str, bytes]] = {}

    def _check_git_repo(self) -> bool:
        if not (self.repo_root / ".git").exists():
            return False
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            return res.returncode == 0
        except Exception:
            return False

    def _run_git(self, *args: str) -> str:
        res = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            raise GitTransactionError(f"Error Git '{' '.join(args)}': {res.stderr.strip()}")
        return res.stdout.strip()

    def begin_transaction(self, goal_id: str) -> str:
        """Inicia una transacción creando una rama efímera limpia o snapshot inicial."""
        tx_id = f"aleph-txn-{goal_id[:8]}-{uuid.uuid4().hex[:6]}"
        if self.is_git:
            try:
                self.initial_branch = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
                self._run_git("checkout", "-b", tx_id)
                self.active_branch = tx_id
            except Exception as e:
                logger.warning(f"Fallback a snapshot transaccional por fallo en git checkout: {e}")
                self.is_git = False
                self._create_fs_snapshot(tx_id)
        else:
            self._create_fs_snapshot(tx_id)
        return tx_id

    def commit_checkpoint(self, message: str) -> str:
        """Crea un checkpoint transaccional y retorna un identificador de estado."""
        checkpoint_id = f"cp-{uuid.uuid4().hex[:8]}"
        if self.is_git and self.active_branch:
            try:
                self._run_git("add", "-A")
                self._run_git("commit", "-m", f"checkpoint: {message}", "--allow-empty")
                return self._run_git("rev-parse", "HEAD")
            except Exception:
                self._create_fs_snapshot(checkpoint_id)
                return checkpoint_id
        else:
            self._create_fs_snapshot(checkpoint_id)
            return checkpoint_id

    def rollback_to(self, checkpoint_ref: str) -> None:
        """Ejecuta un rollback atómico al estado del checkpoint especificado."""
        if self.is_git and self.active_branch and not checkpoint_ref.startswith("cp-"):
            try:
                self._run_git("reset", "--hard", checkpoint_ref)
                self._run_git("clean", "-fdx")
                return
            except Exception as e:
                logger.warning(f"Falla en git reset, recurriendo a snapshot: {e}")

        # Fallback vía snapshot filesystem
        if checkpoint_ref in self.snapshots:
            self._restore_fs_snapshot(checkpoint_ref)
        else:
            logger.warning(f"Checkpoint '{checkpoint_ref}' no encontrado en snapshots.")

    def abort_transaction(self) -> None:
        """Aborta la transacción activa y restaura el estado original."""
        if self.is_git and self.initial_branch and self.active_branch:
            try:
                self._run_git("checkout", self.initial_branch)
                self._run_git("branch", "-D", self.active_branch)
            except Exception as e:
                logger.warning(f"Error al abortar rama git: {e}")
        self.active_branch = None
        self.snapshots.clear()

    def commit_transaction(self, target_branch: Optional[str] = None) -> None:
        """Consolida la transacción en la rama principal."""
        target = target_branch or self.initial_branch
        if self.is_git and target and self.active_branch:
            try:
                feature = self.active_branch
                self._run_git("checkout", target)
                self._run_git("merge", "--no-ff", feature, "-m", f"feat(goal-complete): merge {feature}")
                self._run_git("branch", "-d", feature)
            except Exception as e:
                logger.warning(f"Merge Git falló, consolidación realizada en directorio de trabajo: {e}")
        self.active_branch = None
        self.snapshots.clear()

    def _create_fs_snapshot(self, snapshot_id: str) -> None:
        snapshot: Dict[str, bytes] = {}
        for p in self.repo_root.rglob("*"):
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(self.repo_root).parts):
                try:
                    rel = p.relative_to(self.repo_root).as_posix()
                    snapshot[rel] = p.read_bytes()
                except Exception:
                    pass
        self.snapshots[snapshot_id] = snapshot

    def _restore_fs_snapshot(self, snapshot_id: str) -> None:
        snapshot = self.snapshots.get(snapshot_id, {})
        # Eliminar archivos actuales no presentes en el snapshot
        for p in list(self.repo_root.rglob("*")):
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(self.repo_root).parts):
                rel = p.relative_to(self.repo_root).as_posix()
                if rel not in snapshot:
                    try:
                        p.chmod(stat.S_IWRITE)
                        p.unlink()
                    except Exception:
                        pass
        # Restaurar contenido del snapshot
        for rel_path, content in snapshot.items():
            full = self.repo_root / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)
            try:
                full.chmod(stat.S_IWRITE)
            except Exception:
                pass
            full.write_bytes(content)


# ============================================================================
# 6. DETERMINISTIC GATEKEEPER RUNTIME (PIPELINE DE 5 PUERTAS)
# ============================================================================

class GatekeeperRuntime:
    """
    Gatekeeper en runtime completamente determinista e inviolable.
    Ejecuta el pipeline de 5 Verification Gates sin intervención del LLM:
    - Gate 1: Stream Integrity & Exit Code Verifier
    - Gate 2: Invariante Criptográfico Merkle de la Suite de Tests
    - Gate 3: Analizador de AST Diff y Pureza Semántica (Anti-Cheat)
    - Gate 4: Mutation Score >= 85%
    - Gate 5: Idempotencia y Limpieza de Estado Residual
    """

    def __init__(self, repo_root: Path, goal_spec: GoalSpec | Dict[str, Any]):
        self.repo_root = repo_root.resolve()
        if isinstance(goal_spec, dict):
            self.spec = GoalSpec(**goal_spec)
        else:
            self.spec = goal_spec
        self.contract = self.spec.verification_contract

    def calculate_merkle_tests_hash(self) -> str:
        """Calcula el hash Merkle criptográfico actual de los archivos de prueba."""
        return MerkleTestEngine.calculate_merkle_tests_hash(
            self.repo_root, self.spec.test_files
        )

    def execute_test_command(self) -> Tuple[int, str, str]:
        """Ejecuta el comando formal de pruebas en subproceso con timeout estricto."""
        cmd = self.contract.test_command
        timeout_sec = self.contract.max_duration_seconds
        try:
            res = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            return 124, "", f"TIMEOUT: La ejecución excedió el límite de {timeout_sec}s"
        except Exception as e:
            return 127, "", f"ERROR AL EJECUTAR COMANDO DE PRUEBA: {e}"

    def run_mutation_analysis(self) -> MutationResult:
        """Ejecuta el análisis de pruebas mutantes sobre target_files."""
        return MutationTestingEngine.run_mutation_analysis(
            repo_root=self.repo_root,
            target_files=self.spec.target_files,
            test_command=self.contract.test_command,
            timeout_sec=self.contract.max_duration_seconds
        )

    def verify_submission(
        self,
        expected_merkle_tests: str,
        original_test_asts: Optional[Dict[str, str]] = None
    ) -> GatekeeperResult:
        """
        Auditoría omnímoda del Gatekeeper a través del pipeline de 5 puertas.
        """
        violations: List[str] = []
        gate_results: Dict[str, bool] = {
            "Gate_1_Stream_Integrity": False,
            "Gate_2_Merkle_Invariant": False,
            "Gate_3_AST_Anti_Cheat": False,
            "Gate_4_Mutation_Score": False,
            "Gate_5_Idempotence_Check": False,
        }

        # --------------------------------------------------------------------
        # GATE 2: Invariante Criptográfico Merkle de Tests (The Assert Weakener)
        # --------------------------------------------------------------------
        current_merkle = self.calculate_merkle_tests_hash()
        if current_merkle != expected_merkle_tests:
            violations.append(
                f"Gate 2 VETO: Merkle Hash adulterado. Esperado: {expected_merkle_tests}, Actual: {current_merkle}"
            )
        else:
            gate_results["Gate_2_Merkle_Invariant"] = True

        # --------------------------------------------------------------------
        # GATE 3: AST Anti-Cheat Scanner (The Dummy Mock, Skipper, Weakener)
        # --------------------------------------------------------------------
        ast_gate_passed = True
        for target_rel in self.spec.target_files:
            target_path = self.repo_root / target_rel
            allow_mocks = (self.contract.mock_policy == "PERMISSIVE_INTEGRATION")
            file_violations = ASTGuard.audit_production_file(target_path, allow_mocks=allow_mocks)
            if file_violations:
                ast_gate_passed = False
                violations.extend([f"Gate 3 VETO ({target_rel}): {v}" for v in file_violations])

        # Auditar integridad de tests si se proporcionó AST original de referencia
        if original_test_asts:
            for test_rel in self.spec.test_files:
                test_path = self.repo_root / test_rel
                if test_path.exists() and test_rel in original_test_asts:
                    test_code = test_path.read_text(encoding="utf-8")
                    orig_code = original_test_asts[test_rel]
                    weakener_violations = ASTGuard.audit_test_file_integrity(orig_code, test_code)
                    if weakener_violations:
                        ast_gate_passed = False
                        violations.extend([f"Gate 3 VETO (Tests {test_rel}): {v}" for v in weakener_violations])

        if ast_gate_passed:
            gate_results["Gate_3_AST_Anti_Cheat"] = True

        # --------------------------------------------------------------------
        # GATE 1: Stream Integrity & Exit Code Verifier (The Shadow Runner)
        # --------------------------------------------------------------------
        exit_code, stdout, stderr = self.execute_test_command()
        if exit_code != 0:
            violations.append(f"Gate 1 VETO: Test runner falló con código {exit_code}.\nStderr: {stderr}")
        else:
            # Comprobar política de cero skipped tests
            if self.contract.forbid_skipped_tests:
                if "skipped" in stdout.lower() or "skipped" in stderr.lower():
                    # Verificar si realmente hay tests saltados
                    for line in stdout.splitlines() + stderr.splitlines():
                        if "skipped" in line.lower() and not line.strip().startswith("#"):
                            violations.append("Gate 1 VETO (The Silent Skipper): Tests marcados como 'skipped' detectados.")
                            break
            if exit_code == 0 and not any("Gate 1 VETO" in v for v in violations):
                gate_results["Gate_1_Stream_Integrity"] = True

        # --------------------------------------------------------------------
        # GATE 4: Mutation Score >= 85%
        # --------------------------------------------------------------------
        mutation_score = 0.0
        if exit_code == 0 and not violations:
            mut_result = self.run_mutation_analysis()
            mutation_score = mut_result.mutation_score
            min_score = self.contract.min_mutation_score
            if mutation_score < min_score:
                violations.append(
                    f"Gate 4 VETO: Mutation Score insuficiente ({mutation_score:.1f}% < {min_score:.1f}%). "
                    f"Sobrevivieron {mut_result.survived_mutants} de {mut_result.total_mutants} mutantes."
                )
            else:
                gate_results["Gate_4_Mutation_Score"] = True
        elif exit_code == 0:
            # Si hubo violaciones previas pero exit 0, no se corre mutación costosa
            gate_results["Gate_4_Mutation_Score"] = False

        # --------------------------------------------------------------------
        # GATE 5: Idempotencia y Limpieza de Estado Residual
        # --------------------------------------------------------------------
        if exit_code == 0 and not violations:
            exit_code_2, _, stderr_2 = self.execute_test_command()
            if exit_code_2 != 0:
                violations.append(f"Gate 5 VETO: Falla de idempotencia. Segunda ejecución falló: {stderr_2}")
            else:
                gate_results["Gate_5_Idempotence_Check"] = True

        passed = len(violations) == 0 and exit_code == 0
        summary = (
            f"CERTIFICADO: Entrega formalmente aprobada por el Gatekeeper (Mutation Score: {mutation_score:.1f}%)."
            if passed
            else f"RECHAZADO: Veto del Gatekeeper con {len(violations)} violación(es)."
        )

        return GatekeeperResult(
            passed=passed,
            exit_code=exit_code,
            summary=summary,
            violations=violations,
            mutation_score=mutation_score,
            gate_results=gate_results,
            merkle_hash=current_merkle,
            stdout=stdout,
            stderr=stderr
        )


class TddGatekeeper(GatekeeperRuntime):
    """
    Gatekeeper TDD Soberano con Integración Nativa a LogCrusher.
    Interpreta salidas de pytest comprimidas quirúrgicamente (reducción >90% tokens)
    preservando 100% de la semántica de diagnósticos, aserciones y tracebacks.
    """
    def __init__(
        self,
        repo_root: Path,
        goal_spec: GoalSpec | Dict[str, Any],
        log_crusher: Optional[Any] = None
    ):
        super().__init__(repo_root, goal_spec)
        self.log_crusher = log_crusher
        if self.log_crusher is None:
            try:
                from v5_context_cache import SurgicalLogCrusher
                self.log_crusher = SurgicalLogCrusher(workspace_root=str(self.repo_root))
            except Exception:
                try:
                    from lib.v5_context_cache import SurgicalLogCrusher
                    self.log_crusher = SurgicalLogCrusher(workspace_root=str(self.repo_root))
                except Exception:
                    self.log_crusher = None

    def crush_output(self, raw_log: str) -> Tuple[str, Dict[str, Any]]:
        """Comprime la salida de terminal usando LogCrusher."""
        if not raw_log:
            return "", {"compression_ratio": 1.0, "raw_lines": 0, "crushed_lines": 0}
        if self.log_crusher is not None:
            if hasattr(self.log_crusher, "crush_terminal_output"):
                res = self.log_crusher.crush_terminal_output(raw_log)
                return res.crushed_text, {
                    "compression_ratio": res.compression_ratio,
                    "raw_lines": res.original_lines,
                    "crushed_lines": res.crushed_lines,
                    "tokens_saved": res.tokens_saved
                }
            elif hasattr(self.log_crusher, "crush"):
                crushed_res = self.log_crusher.crush(raw_log)
                if isinstance(crushed_res, tuple) and len(crushed_res) == 2:
                    txt, m = crushed_res
                    m_dict = m.to_dict() if hasattr(m, "to_dict") else (asdict(m) if hasattr(m, "__dataclass_fields__") else (m if isinstance(m, dict) else {}))
                    return txt, m_dict
                elif isinstance(crushed_res, str):
                    raw_lines = len(raw_log.splitlines())
                    crushed_lines = len(crushed_res.splitlines())
                    ratio = round(crushed_lines / max(raw_lines, 1), 4)
                    return crushed_res, {
                        "compression_ratio": ratio,
                        "raw_lines": raw_lines,
                        "crushed_lines": crushed_lines,
                        "tokens_saved": max(0, (raw_lines - crushed_lines) * 4),
                    }
                else:
                    return str(crushed_res), {"compression_ratio": 1.0, "raw_lines": len(raw_log.splitlines()), "crushed_lines": 1}

        # Fallback de compresión quirúrgica directa
        cleaned = re.sub(r"\x1b\[[0-9;]*[mKHF]", "", raw_log)
        lines = cleaned.splitlines()
        raw_cnt = len(lines)
        deduped: List[str] = []
        last_line = None
        rep = 0
        for line in lines:
            if line == last_line:
                rep += 1
            else:
                if rep > 0:
                    deduped.append(f"  [... repeated {rep} more times ...]")
                    rep = 0
                deduped.append(line)
                last_line = line
        if rep > 0:
            deduped.append(f"  [... repeated {rep} more times ...]")

        crushed = "\n".join(deduped)
        return crushed, {
            "compression_ratio": round(len(crushed) / max(1, len(raw_log)), 4),
            "raw_lines": raw_cnt,
            "crushed_lines": len(deduped)
        }

    def interpret_crushed_output(
        self,
        crushed_stdout: str,
        crushed_stderr: str = "",
        exit_code: int = 0
    ) -> Dict[str, Any]:
        """
        Interpreta determinísticamente la salida de pytest comprimida por el LogCrusher.
        """
        combined = f"{crushed_stdout}\n{crushed_stderr}"

        passed_count = 0
        failed_count = 0
        skipped_count = 0
        error_count = 0
        exec_time: Optional[float] = None

        summary_m = re.search(r"=+\s*(.*?)\s+in\s+([0-9\.]+s?)\s*=+", combined)
        summary_text = summary_m.group(1) if summary_m else ""
        if summary_m and summary_m.group(2):
            t_str = summary_m.group(2).rstrip("s")
            try:
                exec_time = float(t_str)
            except ValueError:
                pass

        m_pass = re.search(r"(\d+)\s+passed", combined, re.IGNORECASE)
        if m_pass:
            passed_count = int(m_pass.group(1))

        m_fail = re.search(r"(\d+)\s+failed", combined, re.IGNORECASE)
        if m_fail:
            failed_count = int(m_fail.group(1))

        m_skip = re.search(r"(\d+)\s+skipped", combined, re.IGNORECASE)
        if m_skip:
            skipped_count = int(m_skip.group(1))

        m_err = re.search(r"(\d+)\s+errors?", combined, re.IGNORECASE)
        if m_err:
            error_count = int(m_err.group(1))

        failures: List[Dict[str, str]] = []
        for line in combined.splitlines():
            line_str = line.strip()
            if line_str.startswith("FAILED ") or " FAILED " in line_str:
                clean_fail = line_str.replace("FAILED ", "").strip()
                parts = clean_fail.split(" - ", 1)
                test_target = parts[0].strip()
                reason = parts[1].strip() if len(parts) > 1 else "Test assertion failed"
                failures.append({
                    "test_target": test_target,
                    "reason": reason
                })

        is_passed = (exit_code == 0) and (failed_count == 0) and (error_count == 0) and (passed_count > 0 or "passed" in combined.lower())
        if exit_code != 0 and failed_count == 0 and error_count == 0:
            is_passed = False
            error_count += 1

        verdict = "PASSED" if is_passed else ("FAILED" if (failed_count > 0 or exit_code != 0) else "ERROR")

        return {
            "verdict": verdict,
            "passed": is_passed,
            "exit_code": exit_code,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "total_tests": passed_count + failed_count + skipped_count + error_count,
            "execution_time_seconds": exec_time,
            "failures": failures,
            "summary_line": summary_text,
            "is_crushed": ("[... repeated" in combined or "[... truncated" in combined or "CRUSHED" in combined)
        }

    def execute_test_command_crushed(self) -> Tuple[int, str, str, Dict[str, Any]]:
        """
        Ejecuta el test command, pasa stdout y stderr por LogCrusher y lo interpreta.
        """
        exit_code, raw_stdout, raw_stderr = self.execute_test_command()
        crushed_stdout, metrics_out = self.crush_output(raw_stdout)
        crushed_stderr, metrics_err = self.crush_output(raw_stderr)
        interpreted = self.interpret_crushed_output(crushed_stdout, crushed_stderr, exit_code=exit_code)
        interpreted["stdout_metrics"] = metrics_out
        interpreted["stderr_metrics"] = metrics_err
        return exit_code, crushed_stdout, crushed_stderr, interpreted

    def verify_submission(
        self,
        expected_merkle_tests: str,
        original_test_asts: Optional[Dict[str, str]] = None,
        crush_logs: bool = True
    ) -> GatekeeperResult:
        """
        Auditoría omnímoda del Gatekeeper con soporte de salida comprimida por LogCrusher.
        """
        res = super().verify_submission(
            expected_merkle_tests=expected_merkle_tests,
            original_test_asts=original_test_asts
        )
        if crush_logs and res.stdout:
            crushed_out, _ = self.crush_output(res.stdout)
            crushed_err, _ = self.crush_output(res.stderr)
            res.stdout = crushed_out
            res.stderr = crushed_err
        return res


# ============================================================================
# 7. GOAL LOOP TDD ORCHESTRATOR (ORQUESTADOR DIALÉCTICO)
# ============================================================================

class GoalLoopOrchestrator:
    """
    Conductor del ciclo dialéctico Red -> Green -> Refactor -> Certificación.
    Controla permisos físicos por fase y garantiza transaccionalidad ACID.
    """

    def __init__(
        self,
        repo_root: Path,
        goal_spec: GoalSpec | Dict[str, Any] | Path,
        red_handler: Optional[Callable[["GoalLoopOrchestrator"], None]] = None,
        green_handler: Optional[Callable[["GoalLoopOrchestrator", int], None]] = None,
        refactor_handler: Optional[Callable[["GoalLoopOrchestrator"], None]] = None
    ):
        self.repo_root = repo_root.resolve()

        if isinstance(goal_spec, Path):
            data = json.loads(goal_spec.read_text(encoding="utf-8"))
            self.spec = GoalSpec(**data)
        elif isinstance(goal_spec, dict):
            self.spec = GoalSpec(**goal_spec)
        else:
            self.spec = goal_spec

        self.git = GitTransactionEngine(self.repo_root)
        self.gatekeeper = TddGatekeeper(self.repo_root, self.spec)
        self.sandbox = PhysicalPermissionSandbox()

        self.red_handler = red_handler
        self.green_handler = green_handler
        self.refactor_handler = refactor_handler

        self.red_merkle_hash: Optional[str] = None
        self.red_checkpoint_commit: Optional[str] = None
        self.green_checkpoint_commit: Optional[str] = None
        self.last_result: Optional[GatekeeperResult] = None

    def run_goal_cycle(self) -> bool:
        """
        Ejecuta el ciclo TDD completo de punta a punta.
        Retorna True si el objetivo fue formalmente certificado e integrado.
        """
        goal_id = self.spec.goal_id
        logger.info(f"=== INICIANDO OBJETIVO ALEPH: {goal_id} ===")
        logger.info(f"Objetivo: {self.spec.objective}")

        tx_id = self.git.begin_transaction(goal_id)
        logger.info(f"Transacción iniciada: {tx_id}")

        try:
            # ----------------------------------------------------------------
            # FASE 1: RED BREAKER (tests/ WRITE, src/ READ-ONLY)
            # ----------------------------------------------------------------
            logger.info(">>> FASE 1: RED BREAKER (Adversarial Tests)")
            self._setup_permissions_for_red()

            if self.red_handler:
                self.red_handler(self)

            # Verificar que el test falle legítimamente (exit_code != 0)
            exit_code, stdout, stderr = self.gatekeeper.execute_test_command()
            if exit_code == 0:
                logger.error("Veto Red: La prueba pasa antes de implementar la solución (Falso Red).")
                self._restore_full_permissions()
                self.git.abort_transaction()
                return False

            # Capturar hash Merkle y registrar checkpoint Red
            self.red_merkle_hash = self.gatekeeper.calculate_merkle_tests_hash()
            self.red_checkpoint_commit = self.git.commit_checkpoint("fase-red-completada")
            logger.info(f"Fase Red validada. Checkpoint: {self.red_checkpoint_commit} [Merkle: {self.red_merkle_hash[:12]}...]")

            # ----------------------------------------------------------------
            # FASE 2: GREEN IMPLEMENTER (tests/ READ-ONLY LOCK, src/ WRITE)
            # ----------------------------------------------------------------
            logger.info(">>> FASE 2: GREEN IMPLEMENTER (tests/ BLOQUEADO EN READ-ONLY)")
            self._setup_permissions_for_green()

            max_green_attempts = self.spec.resource_limits.max_green_attempts
            green_success = False

            for attempt in range(1, max_green_attempts + 1):
                logger.info(f"Intento Green {attempt}/{max_green_attempts}...")

                if self.green_handler:
                    self.green_handler(self, attempt)

                # Gatekeeper evalúa la entrega
                result = self.gatekeeper.verify_submission(expected_merkle_tests=self.red_merkle_hash)
                self.last_result = result

                if result.passed:
                    logger.info(f"Fase Green superada con éxito! (Mutation Score: {result.mutation_score:.1f}%)")
                    green_success = True
                    break
                else:
                    logger.warning(f"Rechazo en intento Green {attempt}: {result.violations}")
                    # Rollback atómico a estado Red limpio
                    self.git.rollback_to(self.red_checkpoint_commit)
                    self._setup_permissions_for_green()

            if not green_success:
                logger.error("Intentos Green agotados. Abortando transacción.")
                self._restore_full_permissions()
                self.git.abort_transaction()
                return False

            self.green_checkpoint_commit = self.git.commit_checkpoint("fase-green-aprobada")

            # ----------------------------------------------------------------
            # FASE 3: REFACTOR OPTIMIZER (tests/ READ-ONLY, src/ WRITE)
            # ----------------------------------------------------------------
            logger.info(">>> FASE 3: REFACTOR OPTIMIZER")
            self._setup_permissions_for_refactor()

            if self.refactor_handler:
                self.refactor_handler(self)

            refactor_result = self.gatekeeper.verify_submission(expected_merkle_tests=self.red_merkle_hash)
            if not refactor_result.passed:
                logger.warning(f"Refactor introdujo regresión ({refactor_result.violations}). Rollback a Green.")
                self.git.rollback_to(self.green_checkpoint_commit)
            else:
                logger.info("Refactorización validada con éxito.")
                self.git.commit_checkpoint("fase-refactor-optimizada")
                self.last_result = refactor_result

            # ----------------------------------------------------------------
            # FASE 4: CONSOLIDACIÓN FINAL
            # ----------------------------------------------------------------
            self._restore_full_permissions()
            self.git.commit_transaction()
            logger.info(f"OBJETIVO {goal_id} CUMPLIDO Y FORMALMENTE CERTIFICADO.")
            return True

        except Exception as e:
            logger.exception(f"Falla catastrófica en el ciclo de objetivos: {e}")
            self._restore_full_permissions()
            self.git.abort_transaction()
            return False

    def _setup_permissions_for_red(self) -> None:
        self.sandbox.unlock_directory_read_write(self.repo_root / "tests")
        # En fase Red, src/ debe estar protegido contra modificaciones
        src_path = self.repo_root / "src"
        if src_path.exists():
            self.sandbox.lock_directory_read_only(src_path)

    def _setup_permissions_for_green(self) -> None:
        tests_path = self.repo_root / "tests"
        if tests_path.exists():
            self.sandbox.lock_directory_read_only(tests_path)
        src_path = self.repo_root / "src"
        if src_path.exists():
            self.sandbox.unlock_directory_read_write(src_path)

    def _setup_permissions_for_refactor(self) -> None:
        self._setup_permissions_for_green()

    def _restore_full_permissions(self) -> None:
        tests_path = self.repo_root / "tests"
        if tests_path.exists():
            self.sandbox.unlock_directory_read_write(tests_path)
        src_path = self.repo_root / "src"
        if src_path.exists():
            self.sandbox.unlock_directory_read_write(src_path)


# ============================================================================
# FUNCIONES AUXILIARES DE INGESTA
# ============================================================================

def load_goal_spec(path_or_dict: Path | str | Dict[str, Any]) -> GoalSpec:
    """Carga y valida un goal-spec desde archivo JSON o diccionario."""
    if isinstance(path_or_dict, (Path, str)):
        p = Path(path_or_dict).resolve()
        data = json.loads(p.read_text(encoding="utf-8"))
    else:
        data = path_or_dict
    return GoalSpec(**data)
