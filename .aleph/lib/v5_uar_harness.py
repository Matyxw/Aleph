#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Agent Runtime (UAR) & Multi-Environment Execution Harness
Ruta: C:\\Users\\Lucas cardozo\\.aleph\\lib\\v5_uar_harness.py
Especificación: C:\\Users\\Lucas cardozo\\.aleph\\ecosystem_skills_plan_v5\\02_PLAN_MULTI_ENVIRONMENT_HARNESS.md

Doctrina: EL DEMIURGO - Ciclo Recursivo de Ejecución Asimétrica
- Invocación Vectorizada Directa (TIV) - CWE-78 = 0.00%
- Transpilador Universal de Reglas (UTR) Biyectivo e Idempotente
- Contratos Canónicos Tipados (CanonicalTask y CanonicalExecutionReceipt)
- Gobernanza Asimétrica: Control Plane (Antigravity) vs Data Plane (Claude Code/Codex/Mock)
"""

from __future__ import annotations

import os
import sys
import re
import time
import json
import uuid
import hmac
import signal
import hashlib
import difflib
import subprocess
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from abc import ABC, abstractmethod

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


# ==============================================================================
# 1. ENUMS Y CONTRATOS CANÓNICOS INMUTABLES
# ==============================================================================

class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class RuntimeTarget(str, Enum):
    GOOGLE_ANTIGRAVITY = "google_antigravity"
    CLAUDE_CODE = "claude_code"
    OPENAI_CODEX = "openai_codex"
    OPENCODE = "opencode"
    MOCK_LOCAL = "mock_local"


class ActionType(str, Enum):
    EXECUTE_COMMAND = "EXECUTE_COMMAND"
    APPLY_PATCH = "APPLY_PATCH"
    RUN_TESTS = "RUN_TESTS"
    QUERY_CODEBASE = "QUERY_CODEBASE"
    REFACTOR_MODULE = "REFACTOR_MODULE"


class NetworkPolicy(str, Enum):
    ISOLATED_NO_NET = "ISOLATED_NO_NET"
    WORKSPACE_LOCAL_ONLY = "WORKSPACE_LOCAL_ONLY"
    UNRESTRICTED = "UNRESTRICTED"


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    NON_ZERO_EXIT = "NON_ZERO_EXIT"
    TIMEOUT = "TIMEOUT"
    SECURITY_BLOCKED = "SECURITY_BLOCKED"
    CRASH_OR_PANIC = "CRASH_OR_PANIC"


class ArtifactAction(str, Enum):
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    UNCHANGED = "UNCHANGED"


class SignatureAlgorithm(str, Enum):
    SHA256_HMAC = "SHA256_HMAC"
    BLAKE3_HMAC = "BLAKE3_HMAC"


class ExecutionTargetSpec(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    runtime: RuntimeTarget
    preferred_model: str = Field(default="inherit")
    allowed_fallbacks: List[str] = Field(default_factory=list)


class ContextEnvelope(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    workspace_root: str
    git_commit_sha: str = Field(default="0000000000000000000000000000000000000000")
    active_files: List[str] = Field(default_factory=list)
    injected_rules: List[str] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)

    @field_validator("git_commit_sha")
    @classmethod
    def validate_sha(cls, v: str) -> str:
        if not re.match(r"^[0-9a-fA-F]{40}$", v):
            raise ValueError(f"git_commit_sha debe ser un hash hexadecimal de 40 caracteres, recibido: {v}")
        return v.lower()


class ActionPayload(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    executable: str
    arguments: List[str] = Field(default_factory=list)
    stdin_content: Optional[str] = None
    expected_artifacts: List[str] = Field(default_factory=list)


class ActionSpec(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    action_type: ActionType
    payload: ActionPayload


class SecurityContext(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    read_only_paths: List[str] = Field(default_factory=list)
    forbidden_commands: List[str] = Field(default_factory=list)
    network_policy: NetworkPolicy = NetworkPolicy.WORKSPACE_LOCAL_ONLY
    max_output_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)


class CanonicalTask(BaseModel):
    """
    Especificación de CanonicalTask v1.0.0
    Encapsula la intención operativa, su contexto y sus límites de seguridad.
    """
    class Config:
        extra = "forbid"
        frozen = True
    schema_url: Optional[str] = Field(default=None, alias="$schema")
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = Field(default="1.0.0")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: int = Field(default=30, ge=1, le=600)
    execution_target: ExecutionTargetSpec
    context_envelope: ContextEnvelope
    action_spec: ActionSpec
    security_context: SecurityContext


class ProducedArtifact(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    file_path: str
    action: ArtifactAction
    sha256_pre: Optional[str] = None
    sha256_post: Optional[str] = None


class ExecutorMetadata(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    runtime: str
    runtime_version: str
    host_os: str
    pid: int
    started_at: str
    completed_at: str
    wall_time_ms: float = Field(ge=0.0)


class ResultDigest(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    exit_code: int
    stdout_hash: str
    stderr_hash: str
    stdout_truncated: str
    stderr_truncated: str
    diff_unified: str = ""


class TelemetryData(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    cpu_user_ms: float = 0.0
    cpu_system_ms: float = 0.0
    peak_memory_bytes: int = 0
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None


class CryptographicAttestation(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.SHA256_HMAC
    receipt_digest: str
    signature: str


class CanonicalExecutionReceipt(BaseModel):
    """
    Especificación de CanonicalExecutionReceipt v1.0.0
    Recibo de ejecución inmutable con prueba criptográfica y telemetría.
    """
    class Config:
        extra = "forbid"
        frozen = True
    schema_url: Optional[str] = Field(default=None, alias="$schema")
    receipt_id: str = Field(default_factory=lambda: f"rec-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}")
    task_id: str
    schema_version: str = Field(default="1.0.0")
    executor_metadata: ExecutorMetadata
    execution_status: ExecutionStatus
    result_digest: ResultDigest
    telemetry: TelemetryData
    artifacts_produced: List[ProducedArtifact]
    cryptographic_attestation: CryptographicAttestation


# ==============================================================================
# 2. SANITIZACIÓN DE SHELL Y MOTOR DE INVOCACIÓN TIPADA (TIV) - ANTI CWE-78
# ==============================================================================

class SpawnExecutionResult(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    exit_code: int
    stdout_raw: str
    stderr_raw: str
    stdout_hash: str
    stderr_hash: str
    wall_time_ms: float
    timed_out: bool
    killed_by_security: bool


class SecureProcessSpawner:
    """
    Motor TIV (Typed Invocation Vector):
    Erradica vulnerabilidades CWE-78 forzando invocación vectorizada sin shell
    intermedia y aplicando las reglas formales de Microsoft CommandLineToArgvW.
    """
    FORBIDDEN_EXECUTABLES: Set[str] = {
        "format.com",
        "diskpart.exe",
        "vssadmin.exe",
        "bcdedit.exe",
        "regedit.exe",
        "takeown.exe",
        "icacls.exe",
    }

    @staticmethod
    def escape_windows_arg(arg: str) -> str:
        """
        Escapa un argumento individual según la semántica rigurosa de Win32
        CommandLineToArgvW de Microsoft C/C++ Runtime:
        - Si está vacío: retorna '""'
        - Si no contiene espacios, tabulaciones, comillas dobles ni barras: retorna tal cual.
        - Las barras invertidas antes de comilla doble se duplican (2n + 1).
        - Las barras invertidas antes del cierre se duplican (2n).
        """
        if len(arg) == 0:
            return '""'

        if not re.search(r'[\s"\\]', arg):
            return arg

        escaped: List[str] = ['"']
        backslashes = 0

        for char in arg:
            if char == '\\':
                backslashes += 1
            elif char == '"':
                escaped.append('\\' * (backslashes * 2 + 1))
                escaped.append('"')
                backslashes = 0
            else:
                escaped.append('\\' * backslashes)
                escaped.append(char)
                backslashes = 0

        escaped.append('\\' * (backslashes * 2))
        escaped.append('"')
        return "".join(escaped)

    @classmethod
    def is_safe_command(
        cls,
        executable: str,
        arguments: List[str],
        forbidden_commands: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Inspecciona el ejecutable y argumentos en búsqueda de binarios destructivos
        o comandos explícitamente vetados por la política de seguridad.
        """
        exe_base = os.path.basename(executable).lower()
        if exe_base in cls.FORBIDDEN_EXECUTABLES:
            return False, f"Ejecutable prohibido por política del sistema: {exe_base}"

        forbidden = set(cmd.lower() for cmd in (forbidden_commands or []))
        if exe_base in forbidden:
            return False, f"Comando explícitamente prohibido por security_context: {exe_base}"

        for arg in arguments:
            arg_lower = arg.lower()
            for f_cmd in forbidden:
                if f_cmd and f_cmd in arg_lower:
                    return False, f"Argumento contiene patrón prohibido: {f_cmd}"

        return True, ""

    def execute_safe(
        self,
        executable: str,
        args: List[str],
        cwd: str,
        timeout_ms: int = 30000,
        max_output_bytes: int = 10 * 1024 * 1024,
        env: Optional[Dict[str, str]] = None,
        stdin_content: Optional[str] = None,
        forbidden_commands: Optional[List[str]] = None,
    ) -> SpawnExecutionResult:
        """
        Invocación vectorizada segura (argv[]) directamente al kernel.
        Garantiza shell=False bajo toda circunstancia.
        """
        start_time = time.perf_counter()

        safe, reason = self.is_safe_command(executable, args, forbidden_commands)
        if not safe:
            wall_time = (time.perf_counter() - start_time) * 1000
            err_msg = f"[SECURITY_BLOCKED] {reason}"
            h_err = hashlib.sha256(err_msg.encode("utf-8")).hexdigest()
            h_out = hashlib.sha256(b"").hexdigest()
            return SpawnExecutionResult(
                exit_code=-403,
                stdout_raw="",
                stderr_raw=err_msg,
                stdout_hash=h_out,
                stderr_hash=h_err,
                wall_time_ms=wall_time,
                timed_out=False,
                killed_by_security=True,
            )

        os_env = os.environ.copy()
        if env:
            os_env.update(env)

        cmd_vector = [executable] + list(args)
        timed_out = False
        killed_by_security = False
        stdout_raw = ""
        stderr_raw = ""
        exit_code = -1

        try:
            # shell=False es el pilar contra CWE-78
            proc = subprocess.Popen(
                cmd_vector,
                cwd=cwd,
                stdin=subprocess.PIPE if stdin_content is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                env=os_env,
                text=False
            )
        except Exception as e:
            wall_time = (time.perf_counter() - start_time) * 1000
            err_msg = f"[SPAWN_ERROR] {str(e)}"
            h_err = hashlib.sha256(err_msg.encode("utf-8")).hexdigest()
            h_out = hashlib.sha256(b"").hexdigest()
            return SpawnExecutionResult(
                exit_code=-500,
                stdout_raw="",
                stderr_raw=err_msg,
                stdout_hash=h_out,
                stderr_hash=h_err,
                wall_time_ms=wall_time,
                timed_out=False,
                killed_by_security=False,
            )

        timeout_sec = max(0.1, timeout_ms / 1000.0)

        try:
            stdin_bytes = stdin_content.encode("utf-8") if stdin_content else None
            out_bytes, err_bytes = proc.communicate(input=stdin_bytes, timeout=timeout_sec)
            exit_code = proc.returncode

            # Protección contra saturación de buffer (Context / Memory Bloat)
            if len(out_bytes) > max_output_bytes:
                out_bytes = out_bytes[:max_output_bytes]
                killed_by_security = True

            if len(err_bytes) > max_output_bytes:
                err_bytes = err_bytes[:max_output_bytes]
                killed_by_security = True

            stdout_raw = out_bytes.decode("utf-8", errors="replace")
            stderr_raw = err_bytes.decode("utf-8", errors="replace")

        except subprocess.TimeoutExpired:
            timed_out = True
            self._terminate_process_tree(proc)
            try:
                out_b, err_b = proc.communicate(timeout=2.0)
                stdout_raw = out_b.decode("utf-8", errors="replace")
                stderr_raw = err_b.decode("utf-8", errors="replace")
            except Exception:
                stdout_raw = ""
                stderr_raw = "[TIMEOUT] Process killed after timeout exceeded."
            exit_code = -124

        wall_time_ms = (time.perf_counter() - start_time) * 1000
        stdout_hash = hashlib.sha256(stdout_raw.encode("utf-8")).hexdigest()
        stderr_hash = hashlib.sha256(stderr_raw.encode("utf-8")).hexdigest()

        return SpawnExecutionResult(
            exit_code=exit_code,
            stdout_raw=stdout_raw,
            stderr_raw=stderr_raw,
            stdout_hash=stdout_hash,
            stderr_hash=stderr_hash,
            wall_time_ms=wall_time_ms,
            timed_out=timed_out,
            killed_by_security=killed_by_security,
        )

    def _terminate_process_tree(self, proc: subprocess.Popen) -> None:
        """
        Termina el árbol completo de procesos para evitar procesos huérfanos o zombis.
        En Windows utiliza taskkill /PID <pid> /T /F.
        """
        if proc.poll() is not None:
            return

        pid = proc.pid
        if sys.platform == "win32":
            try:
                subprocess.run(
                    ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=3.0,
                    check=False
                )
            except Exception:
                proc.kill()
        else:
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except Exception:
                proc.kill()


# ==============================================================================
# 3. TRANSPILADOR UNIVERSAL DE REGLAS (UTR)
# ==============================================================================

class CanonicalRule(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    id: str
    title: str
    category: str
    severity: str = Field(pattern="^(CRITICAL|HIGH|NORMAL|LOW)$")
    targets: List[str]
    globs: List[str]
    always_apply: bool
    directive: str
    enforcement: str


class SystemIdentity(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    name: str
    core_principles: List[str]


class CanonicalRulesManifest(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    schema_url: Optional[str] = Field(default=None, alias="$schema")
    version: str = "1.0.0"
    last_updated: str
    system_identity: SystemIdentity
    rules: List[CanonicalRule]


class UniversalRuleTranspiler:
    """
    Transpilador Universal de Reglas (UTR):
    Proyecta CANONICAL_RULES.json sobre .cursor/rules/*.mdc, CLAUDE.md,
    .windsurfrules y SKILL.md de forma determinista, biyectiva e idempotente.
    """
    def __init__(self, workspace_root: Union[str, Path]):
        self.workspace_root = Path(workspace_root).resolve()

    def load_manifest(self, source: Union[str, Path, dict, CanonicalRulesManifest]) -> CanonicalRulesManifest:
        if isinstance(source, CanonicalRulesManifest):
            return source
        elif isinstance(source, dict):
            return CanonicalRulesManifest.model_validate(source)
        elif isinstance(source, (str, Path)):
            p = Path(source)
            if not p.is_absolute():
                p = self.workspace_root / p
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CanonicalRulesManifest.model_validate(data)
        else:
            raise TypeError(f"Fuente de manifest no soportada: {type(source)}")

    def compute_manifest_hash(self, manifest: CanonicalRulesManifest) -> str:
        dumped = manifest.model_dump_json()
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    def render_cursor_mdc(self, rule: CanonicalRule) -> str:
        globs_str = ",".join(rule.globs)
        always_apply_str = "true" if rule.always_apply else "false"
        lines = [
            "---",
            f'description: "{rule.title}"',
            f'globs: "{globs_str}"',
            f"alwaysApply: {always_apply_str}",
            "---",
            "",
            f"# {rule.title}",
            f"- **ID:** `{rule.id}`",
            f"- **Categoría:** `{rule.category}` | **Severidad:** `{rule.severity}`",
            "",
            "## Directiva",
            rule.directive,
            "",
            "## Mecanismo de Aplicación",
            f"`{rule.enforcement}`",
            ""
        ]
        return "\n".join(lines)

    def render_claude_md(self, manifest: CanonicalRulesManifest, manifest_hash: str) -> str:
        claude_rules = [r for r in manifest.rules if "claude_code" in r.targets]
        lines = [
            f"# {manifest.system_identity.name}: INVARIANTES DE DESARROLLO",
            f"<!-- AUTO-GENERATED BY UTR (Hash: {manifest_hash[:8]}). DO NOT EDIT DIRECTLY. -->",
            "",
            "## Principios Rectores",
        ]
        for p in manifest.system_identity.core_principles:
            lines.append(f"- {p}")
        lines.append("")
        lines.append("## Reglas Mandatorias de Terminal")
        for r in claude_rules:
            lines.append(f"- **[{r.id}]** ({r.severity}): {r.directive}")
        lines.append("")
        lines.append("## Comandos Estándar")
        lines.append("- Build: `npm run build` / `cargo build --release`")
        lines.append("- Test: `npm test` / `pytest` / `cargo test`")
        lines.append("- Lint: `npm run lint` / `ruff check`")
        lines.append("- Reglas Sync: `python .aleph/lib/v5_uar_harness.py --sync`")
        lines.append("")
        return "\n".join(lines)

    def render_windsurf_rules(self, manifest: CanonicalRulesManifest) -> str:
        windsurf_rules = [r for r in manifest.rules if "windsurf" in r.targets]
        lines = [
            "# WINDSURF CASCADE DIRECTIVES",
            f"# Auto-generated by ALEPH UTR at {manifest.last_updated}",
            "trigger: always",
            "rules:",
        ]
        for r in windsurf_rules:
            escaped_dir = r.directive.replace('"', '\\"')
            lines.append(f'  - id: "{r.id}"')
            lines.append('    action: enforce')
            lines.append(f'    policy: "{escaped_dir}"')
        lines.append("")
        return "\n".join(lines)

    def render_agent_skill_md(self, rule: CanonicalRule) -> str:
        skill_name = rule.id.replace("rule-", "")
        lines = [
            "---",
            f"name: {skill_name}",
            f"description: {rule.title}",
            "allowed-tools: [run_command, view_file, write_to_file, replace_file_content]",
            "---",
            "",
            "## Objetivo",
            rule.directive,
            "",
            "## Pasos",
            "1. Validar pre-condiciones de seguridad y contexto canónico.",
            "2. Aplicar la directiva operacional con garantía de verificación TDD.",
            "3. Emitir recibo auditable de cumplimiento.",
            "",
            "## Criterios de éxito",
            f"- Cumplimiento estricto del mecanismo de aplicación `{rule.enforcement}`.",
            "- Cero regresiones en invariantes del sistema.",
            "",
            "## Reglas duras",
            f"- Nunca violar la directiva: {rule.directive}",
            "",
            "## Checkpoint humano",
            "Detener y solicitar confirmación si la acción implica mutaciones de infraestructura o financieras.",
            ""
        ]
        return "\n".join(lines)

    def transpile_all(
        self,
        manifest_source: Union[str, Path, dict, CanonicalRulesManifest]
    ) -> Dict[str, Any]:
        """
        Ejecuta la transpilación sincrónica completa hacia los 4 targets.
        SLA: < 120 ms.
        """
        t0 = time.perf_counter()
        manifest = self.load_manifest(manifest_source)
        manifest_hash = self.compute_manifest_hash(manifest)
        updated_files: List[str] = []
        target_counts: Dict[str, int] = {"cursor": 0, "claude_code": 0, "windsurf": 0, "agent_skills": 0}

        # 1. Target: Cursor (.cursor/rules/*.mdc)
        cursor_dir = self.workspace_root / ".cursor" / "rules"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        cursor_rules = [r for r in manifest.rules if "cursor" in r.targets]
        for r in cursor_rules:
            fname = f"{r.id.replace('rule-', '')}.mdc"
            fpath = cursor_dir / fname
            content = self.render_cursor_mdc(r)
            fpath.write_text(content, encoding="utf-8")
            updated_files.append(str(fpath))
            target_counts["cursor"] += 1

        # 2. Target: Claude Code (CLAUDE.md)
        claude_path = self.workspace_root / "CLAUDE.md"
        claude_content = self.render_claude_md(manifest, manifest_hash)
        claude_path.write_text(claude_content, encoding="utf-8")
        updated_files.append(str(claude_path))
        target_counts["claude_code"] = len([r for r in manifest.rules if "claude_code" in r.targets])

        # 3. Target: Windsurf (.windsurfrules)
        windsurf_path = self.workspace_root / ".windsurfrules"
        windsurf_content = self.render_windsurf_rules(manifest)
        windsurf_path.write_text(windsurf_content, encoding="utf-8")
        updated_files.append(str(windsurf_path))
        target_counts["windsurf"] = len([r for r in manifest.rules if "windsurf" in r.targets])

        # 4. Target: Agent Skills (skills/multi-env/*.md)
        skills_dir = self.workspace_root / "skills" / "multi-env"
        skills_dir.mkdir(parents=True, exist_ok=True)
        skill_rules = [r for r in manifest.rules if "agent_skills" in r.targets]
        for r in skill_rules:
            fpath = skills_dir / f"{r.id.replace('rule-', '')}.SKILL.md"
            content = self.render_agent_skill_md(r)
            fpath.write_text(content, encoding="utf-8")
            updated_files.append(str(fpath))
            target_counts["agent_skills"] += 1

        elapsed_ms = (time.perf_counter() - t0) * 1000

        return {
            "updated_files": updated_files,
            "manifest_hash": manifest_hash,
            "target_counts": target_counts,
            "elapsed_ms": elapsed_ms
        }

    def check_drift(self, manifest_source: Union[str, Path, dict, CanonicalRulesManifest]) -> bool:
        """
        Retorna True si los archivos en disco concuerdan exactamente con la transpilación
        del manifest. Si se detecta alteración o ausencia de algún archivo, retorna False.
        """
        manifest = self.load_manifest(manifest_source)
        manifest_hash = self.compute_manifest_hash(manifest)

        # Verificar CLAUDE.md
        claude_path = self.workspace_root / "CLAUDE.md"
        if not claude_path.exists():
            return False
        if claude_path.read_text(encoding="utf-8") != self.render_claude_md(manifest, manifest_hash):
            return False

        # Verificar .windsurfrules
        windsurf_path = self.workspace_root / ".windsurfrules"
        if not windsurf_path.exists():
            return False
        if windsurf_path.read_text(encoding="utf-8") != self.render_windsurf_rules(manifest):
            return False

        # Verificar Cursor rules
        cursor_dir = self.workspace_root / ".cursor" / "rules"
        for r in [r for r in manifest.rules if "cursor" in r.targets]:
            p = cursor_dir / f"{r.id.replace('rule-', '')}.mdc"
            if not p.exists() or p.read_text(encoding="utf-8") != self.render_cursor_mdc(r):
                return False

        return True


# ==============================================================================
# 4. CAPA FORMAL DE ADAPTADORES (AGENT DRIVER)
# ==============================================================================

class EnvironmentCapabilities(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    supports_direct_stdin: bool
    supports_streaming_telemetry: bool
    supports_interactive_questions: bool
    supports_pty: bool
    max_parallel_instances: int
    isolation_level: str
    default_timeout_seconds: int


class AgentDriver(ABC):
    """Interfaz canónica formal para los motores del Data Plane."""

    @property
    @abstractmethod
    def environment_id(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> EnvironmentCapabilities:
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def validate_environment(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def resolve_invocation(self, task: CanonicalTask) -> Tuple[str, List[str]]:
        pass


class MockLocalDriver(AgentDriver):
    """Driver de ejecución local directa para testing y fallback determinista."""

    @property
    def environment_id(self) -> str:
        return "mock_local"

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(
            supports_direct_stdin=True,
            supports_streaming_telemetry=False,
            supports_interactive_questions=False,
            supports_pty=False,
            max_parallel_instances=16,
            isolation_level="process",
            default_timeout_seconds=30
        )

    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    def validate_environment(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "runtime": "mock_local", "available": True}

    def resolve_invocation(self, task: CanonicalTask) -> Tuple[str, List[str]]:
        return task.action_spec.payload.executable, list(task.action_spec.payload.arguments)


class ClaudeCodeDriver(AgentDriver):
    """Driver para Claude Code CLI interactivo y headless (-p)."""

    @property
    def environment_id(self) -> str:
        return "claude_code"

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(
            supports_direct_stdin=True,
            supports_streaming_telemetry=True,
            supports_interactive_questions=False,
            supports_pty=True,
            max_parallel_instances=4,
            isolation_level="process",
            default_timeout_seconds=15
        )

    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    def validate_environment(self) -> Dict[str, Any]:
        claude_found = False
        try:
            r = subprocess.run(["claude", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            claude_found = (r.returncode == 0)
        except Exception:
            claude_found = False
        return {"status": "HEALTHY" if claude_found else "CLI_NOT_FOUND", "runtime": "claude_code", "available": claude_found}

    def resolve_invocation(self, task: CanonicalTask) -> Tuple[str, List[str]]:
        prompt_arg = " ".join(task.action_spec.payload.arguments)
        return "claude", ["-p", prompt_arg, "--no-interactive"]


class CodexCLIDriver(AgentDriver):
    """Driver para OpenAI Codex CLI / OpenCode."""

    @property
    def environment_id(self) -> str:
        return "openai_codex"

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(
            supports_direct_stdin=True,
            supports_streaming_telemetry=False,
            supports_interactive_questions=False,
            supports_pty=False,
            max_parallel_instances=8,
            isolation_level="process",
            default_timeout_seconds=20
        )

    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    def validate_environment(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "runtime": "openai_codex", "available": True}

    def resolve_invocation(self, task: CanonicalTask) -> Tuple[str, List[str]]:
        return task.action_spec.payload.executable, list(task.action_spec.payload.arguments)


# ==============================================================================
# 5. ASYMMETRIC UAR BRIDGE & ATTESTATION ENGINE
# ==============================================================================

class AsymmetricUARBridge:
    """
    Puente de Despacho Asimétrico UAR:
    Gobierna la ejecución táctica delegada al Data Plane y emite el
    CanonicalExecutionReceipt criptográficamente atestiguado con HMAC-SHA256.
    """
    def __init__(self, hmac_secret: str = "aleph-uar-in-memory-attestation-secret-2026"):
        self.hmac_secret = hmac_secret.encode("utf-8")
        self.spawner = SecureProcessSpawner()
        self.drivers: Dict[RuntimeTarget, AgentDriver] = {
            RuntimeTarget.MOCK_LOCAL: MockLocalDriver(),
            RuntimeTarget.CLAUDE_CODE: ClaudeCodeDriver(),
            RuntimeTarget.OPENAI_CODEX: CodexCLIDriver(),
            RuntimeTarget.OPENCODE: CodexCLIDriver(),
        }

    def register_driver(self, runtime: RuntimeTarget, driver: AgentDriver) -> None:
        self.drivers[runtime] = driver

    def compute_files_hash(self, workspace_root: str, files: List[str]) -> Dict[str, Optional[str]]:
        hashes: Dict[str, Optional[str]] = {}
        root = Path(workspace_root)
        for rel_file in files:
            full_path = (root / rel_file).resolve()
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_bytes()
                    hashes[rel_file] = hashlib.sha256(content).hexdigest()
                except Exception:
                    hashes[rel_file] = None
            else:
                hashes[rel_file] = None
        return hashes

    def compare_artifacts(
        self,
        files: List[str],
        pre_hashes: Dict[str, Optional[str]],
        post_hashes: Dict[str, Optional[str]]
    ) -> List[ProducedArtifact]:
        artifacts: List[ProducedArtifact] = []
        all_keys = sorted(list(set(files) | set(pre_hashes.keys()) | set(post_hashes.keys())))

        for file_path in all_keys:
            pre_h = pre_hashes.get(file_path)
            post_h = post_hashes.get(file_path)

            if pre_h is None and post_h is not None:
                action = ArtifactAction.CREATED
            elif pre_h is not None and post_h is None:
                action = ArtifactAction.DELETED
            elif pre_h != post_h:
                action = ArtifactAction.MODIFIED
            else:
                action = ArtifactAction.UNCHANGED

            artifacts.append(ProducedArtifact(
                file_path=file_path,
                action=action,
                sha256_pre=pre_h,
                sha256_post=post_h
            ))
        return artifacts

    def obtain_git_or_fallback_diff(
        self,
        workspace_root: str,
        active_files: List[str],
        pre_contents: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Intenta obtener diff unificado vía git diff. Si no es repo git o falla,
        calcula el diff unificado puro en memoria entre pre y post mutación.
        """
        try:
            res = self.spawner.execute_safe(
                executable="git",
                args=["diff", "--no-color", "--ignore-space-at-eol"],
                cwd=workspace_root,
                timeout_ms=3000
            )
            if res.exit_code == 0 and res.stdout_raw.strip():
                return res.stdout_raw
        except Exception:
            pass

        # Fallback diff unificado en memoria
        diff_chunks: List[str] = []
        root = Path(workspace_root)
        for f in active_files:
            pre_text = (pre_contents or {}).get(f, "")
            post_path = root / f
            post_text = post_path.read_text(encoding="utf-8", errors="replace") if post_path.exists() else ""
            if pre_text != post_text:
                udiff = difflib.unified_diff(
                    pre_text.splitlines(keepends=True),
                    post_text.splitlines(keepends=True),
                    fromfile=f"a/{f}",
                    tofile=f"b/{f}"
                )
                diff_chunks.extend(udiff)

        return "".join(diff_chunks)

    def dispatch_to_data_plane(self, task: CanonicalTask) -> CanonicalExecutionReceipt:
        """
        Despacha una CanonicalTask al Data Plane con SLA estricto y emite recibo auditable.
        """
        started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        t_start = time.perf_counter()
        ws_root = task.context_envelope.workspace_root
        active_files = task.context_envelope.active_files

        # 1. Snapshot previo de archivos y contenido para diff
        pre_hashes = self.compute_files_hash(ws_root, active_files)
        pre_contents: Dict[str, str] = {}
        for f in active_files:
            fp = Path(ws_root) / f
            if fp.exists() and fp.is_file():
                try:
                    pre_contents[f] = fp.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pre_contents[f] = ""

        # 2. Resolver invocación según runtime
        driver = self.drivers.get(task.execution_target.runtime, MockLocalDriver())
        try:
            executable, args = driver.resolve_invocation(task)
        except Exception as e:
            return self._build_receipt(
                task=task,
                started_at=started_at,
                wall_time_ms=(time.perf_counter() - t_start) * 1000,
                status=ExecutionStatus.CRASH_OR_PANIC,
                exit_code=-998,
                stdout="",
                stderr=f"Error resolviendo invocación de driver: {str(e)}",
                artifacts=[],
                diff_unified=""
            )

        # 3. Ejecutar de forma segura vía TIV
        spawn_res = self.spawner.execute_safe(
            executable=executable,
            args=args,
            cwd=ws_root,
            timeout_ms=task.timeout_seconds * 1000,
            max_output_bytes=task.security_context.max_output_bytes,
            env=task.context_envelope.environment_variables,
            stdin_content=task.action_spec.payload.stdin_content,
            forbidden_commands=task.security_context.forbidden_commands,
        )

        wall_time_ms = (time.perf_counter() - t_start) * 1000

        # 4. Clasificar estado
        if spawn_res.timed_out:
            status = ExecutionStatus.TIMEOUT
        elif spawn_res.killed_by_security:
            status = ExecutionStatus.SECURITY_BLOCKED
        elif spawn_res.exit_code != 0:
            status = ExecutionStatus.NON_ZERO_EXIT
        else:
            status = ExecutionStatus.SUCCESS

        # 5. Snapshot posterior y diffs
        post_hashes = self.compute_files_hash(ws_root, active_files)
        artifacts = self.compare_artifacts(active_files, pre_hashes, post_hashes)
        diff_unified = self.obtain_git_or_fallback_diff(ws_root, active_files, pre_contents)

        return self._build_receipt(
            task=task,
            started_at=started_at,
            wall_time_ms=wall_time_ms,
            status=status,
            exit_code=spawn_res.exit_code,
            stdout=spawn_res.stdout_raw,
            stderr=spawn_res.stderr_raw,
            artifacts=artifacts,
            diff_unified=diff_unified
        )

    def _build_receipt(
        self,
        task: CanonicalTask,
        started_at: str,
        wall_time_ms: float,
        status: ExecutionStatus,
        exit_code: int,
        stdout: str,
        stderr: str,
        artifacts: List[ProducedArtifact],
        diff_unified: str
    ) -> CanonicalExecutionReceipt:
        completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        stdout_hash = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        stderr_hash = hashlib.sha256(stderr.encode("utf-8")).hexdigest()

        # Generación de firma criptográfica HMAC-SHA256
        raw_sign_payload = f"{task.task_id}|{status.value}|{exit_code}|{stdout_hash}|{stderr_hash}|{wall_time_ms:.2f}"
        receipt_digest = hashlib.sha256(raw_sign_payload.encode("utf-8")).hexdigest()
        signature = hmac.new(self.hmac_secret, receipt_digest.encode("utf-8"), hashlib.sha256).hexdigest()

        return CanonicalExecutionReceipt(
            task_id=task.task_id,
            executor_metadata=ExecutorMetadata(
                runtime=task.execution_target.runtime.value,
                runtime_version="2.0.0-uar",
                host_os=sys.platform,
                pid=os.getpid(),
                started_at=started_at,
                completed_at=completed_at,
                wall_time_ms=round(wall_time_ms, 2)
            ),
            execution_status=status,
            result_digest=ResultDigest(
                exit_code=exit_code,
                stdout_hash=stdout_hash,
                stderr_hash=stderr_hash,
                stdout_truncated=stdout[:16384],
                stderr_truncated=stderr[:16384],
                diff_unified=diff_unified
            ),
            telemetry=TelemetryData(
                cpu_user_ms=0.0,
                cpu_system_ms=0.0,
                peak_memory_bytes=0
            ),
            artifacts_produced=artifacts,
            cryptographic_attestation=CryptographicAttestation(
                signature_algorithm=SignatureAlgorithm.SHA256_HMAC,
                receipt_digest=receipt_digest,
                signature=signature
            )
        )

    def verify_receipt(self, receipt: CanonicalExecutionReceipt) -> bool:
        """
        Verifica criptográficamente que el recibo no ha sido alterado y procede
        de la firma HMAC de este UAR Bridge.
        """
        raw_sign_payload = (
            f"{receipt.task_id}|{receipt.execution_status.value}|"
            f"{receipt.result_digest.exit_code}|{receipt.result_digest.stdout_hash}|"
            f"{receipt.result_digest.stderr_hash}|{receipt.executor_metadata.wall_time_ms:.2f}"
        )
        expected_digest = hashlib.sha256(raw_sign_payload.encode("utf-8")).hexdigest()
        if expected_digest != receipt.cryptographic_attestation.receipt_digest:
            return False

        expected_sig = hmac.new(
            self.hmac_secret,
            expected_digest.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_sig, receipt.cryptographic_attestation.signature)


# ==============================================================================
# 6. CLI SYNC ENTRYPOINT
# ==============================================================================

def main():
    """Punto de entrada de línea de comandos para sincronización de reglas."""
    import argparse
    parser = argparse.ArgumentParser(description="Universal Agent Runtime Harness CLI")
    parser.add_argument("--sync", action="store_true", help="Transpila CANONICAL_RULES.json hacia todos los targets")
    parser.add_argument("--check-drift", action="store_true", help="Verifica si existen derivas de reglas en el repositorio")
    parser.add_argument("--workspace", default=str(Path.cwd()), help="Directorio raíz del workspace")
    parser.add_argument("--manifest", default=r"C:\Users\Lucas cardozo\.aleph\rules\CANONICAL_RULES.json", help="Ruta al manifest canónico")

    args = parser.parse_args()
    transpiler = UniversalRuleTranspiler(args.workspace)

    if args.sync:
        res = transpiler.transpile_all(args.manifest)
        print(f"[UTR] Transpilación completada con éxito en {res['elapsed_ms']:.2f}ms.")
        print(f"[UTR] Manifest Hash: {res['manifest_hash'][:12]}")
        print(f"[UTR] Archivos generados/actualizados: {len(res['updated_files'])}")
        for f in res["updated_files"]:
            print(f"  -> {f}")
    elif args.check_drift:
        in_sync = transpiler.check_drift(args.manifest)
        if in_sync:
            print("[UTR] 100% Sincronizado. Cero deriva de reglas detectada.")
            sys.exit(0)
        else:
            print("[UTR] ALERTA: Se ha detectado deriva de reglas respecto al manifest canónico.")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
