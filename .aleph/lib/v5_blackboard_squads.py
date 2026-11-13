#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El Aleph v5.0 - Blackboard DAG & Squads Role Orchestrator
Ruta: .aleph/lib/v5_blackboard_squads.py
Doctrina: EL DEMIURGO - Coordinación Determinista, Desacoplamiento de Roles,
           Roles como Funciones Puras, Aislamiento Epistémico y Circuit Breakers.
"""

from __future__ import annotations

import os
import re
import ast
import json
import shlex
import hashlib
import threading
import subprocess
from enum import Enum
from typing import List, Dict, Any, Optional, Literal, Callable, Tuple, Sequence, Union
from datetime import datetime, timezone
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


# ============================================================================
# 1. EXCEPCIONES Y ERRORES DE GOBERNANZA AGÉNTICA
# ============================================================================

class BlackboardError(Exception):
    """Excepción base para fallas en el motor Blackboard."""
    pass


class EpistemicFirewallViolation(BlackboardError):
    """Violación de aislamiento epistémico entre roles agénticos."""
    pass


class CircuitBreakerTrippedError(BlackboardError):
    """Se disparó un Circuit Breaker determinista."""
    pass


class TokenCeilingExceededError(CircuitBreakerTrippedError):
    """Techo rígido de tokens superado (Hard Stop absoluto)."""
    pass


class ContextBudgetExceededError(BlackboardError):
    """El Context Packet supera el presupuesto rígido (< 4,000 tokens)."""
    pass


class RegressionDetectedError(BlackboardError):
    """Regression Sentinel: Se detectó una regresión en la Golden Test Suite."""
    pass


class SecurityVetoError(BlackboardError):
    """Zero Trust: Auditor de Seguridad emitió un Veto Unilateral."""
    pass


class TautologicalTestError(BlackboardError):
    """El test propuesto pasa sin implementación (Fase Roja inválida)."""
    pass


# ============================================================================
# 2. ENUMERACIONES Y ESTADOS DEL SISTEMA
# ============================================================================

class RoleType(str, Enum):
    INVESTIGADOR = "Investigador"
    ARQUITECTO = "Arquitecto"
    TESTER_TDD = "TesterTdd"
    CODER_GREEN = "CoderGreen"
    REVIEWER_HOSTIL = "ReviewerHostil"
    AUDITOR_SEGURIDAD = "AuditorSeguridad"


class TaskStatus(str, Enum):
    TICKET_INGESTED = "TicketIngested"
    RESEARCHING = "Researching"
    ARCHITECTING = "Architecting"
    TESTING_RED = "TestingRed"
    CODING_GREEN = "CodingGreen"
    REVIEWING = "Reviewing"
    AUDITING_SECURITY = "AuditingSecurity"
    COMMITTED = "Committed"
    CIRCUIT_BREAKER_TRIPPED = "CircuitBreakerTripped"
    QUARANTINED = "Quarantined"


class BlackboardEventType(str, Enum):
    TICKET_INGESTED = "TicketIngested"
    RESEARCH_COMPLETED = "ResearchCompleted"
    CONTRACT_DRAFTED = "ContractDrafted"
    TESTS_RED_CONFIRMED = "TestsRedConfirmed"
    CODE_GREEN_PROPOSED = "CodeGreenProposed"
    CRITIQUE_COMPLETED = "CritiqueCompleted"
    SECURITY_APPROVED = "SecurityApproved"
    SECURITY_VETOED = "SecurityVetoed"
    CIRCUIT_BREAKER_TRIGGERED = "CircuitBreakerTriggered"
    TASK_COMMITTED = "TaskCommitted"


class TokenBudgetZone(str, Enum):
    NOMINAL = "NOMINAL"                          # 0% - 70%
    AGGRESSIVE_AST_PRUNING = "AGGRESSIVE_AST_PRUNING"  # 70% - 85%
    CRITICAL_THROTTLE = "CRITICAL_THROTTLE"      # 85% - 100%
    HARD_STOP = "HARD_STOP"                      # >= 100%


# ============================================================================
# 3. MODELOS DE DATOS: CONTEXT PACKETS TIPADOS (PYDANTIC V2)
# ============================================================================

class TaskTicketPacket(BaseModel):
    ticket_id: str = Field(..., pattern=r"^TICK-[0-9]{4,8}$")
    title: str = Field(...)
    description: str
    acceptance_criteria: List[str] = Field(...)
    budget_tokens_max: int = Field(default=150000, le=150000)
    max_tdd_iterations: int = Field(default=3, le=3)
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AstSymbolAffected(BaseModel):
    file_path: str
    symbol_name: str
    symbol_type: Literal["function", "class", "method", "struct", "trait"]
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)

    @model_validator(mode="after")
    def validate_lines(self) -> AstSymbolAffected:
        if self.line_end < self.line_start:
            raise ValueError(
                f"line_end ({self.line_end}) no puede ser menor a line_start ({self.line_start})"
            )
        return self


class ResearchPacket(BaseModel):
    ticket_id: str
    target_files: List[str] = Field(...)
    ast_symbols_affected: List[AstSymbolAffected]
    call_graph_upstream: List[str] = Field(default_factory=list)
    call_graph_downstream: List[str] = Field(default_factory=list)
    existing_invariants: List[str] = Field(...)


class TypeContract(BaseModel):
    type_name: str
    schema_definition: str
    language: Literal["rust", "python", "typescript"]


class FunctionSignatureSpec(BaseModel):
    signature: str
    pre_conditions: List[str] = Field(...)
    post_conditions: List[str] = Field(...)


class ArchitectureContractPacket(BaseModel):
    ticket_id: str
    adr_id: str = Field(..., pattern=r"^ADR-[0-9]{3,6}$")
    decision_summary: str
    alternatives_discarded: List[Dict[str, str]] = Field(...)
    type_contracts: List[TypeContract]
    function_signatures: List[FunctionSignatureSpec]
    required_invariants: List[str]

    @field_validator("alternatives_discarded")
    def validate_alternatives(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        for item in v:
            if "alternative" not in item or "rejection_reason" not in item:
                raise ValueError("Cada alternativa debe contener 'alternative' y 'rejection_reason'")
        return v


class TestFileEntry(BaseModel):
    __test__ = False
    path: str
    content: str

    @field_validator("path")
    def validate_test_path(cls, v: str) -> str:
        v_clean = v.replace("\\", "/").lower()
        if not ("test" in v_clean or v_clean.endswith("_spec.rs")):
            raise ValueError(
                f"La ruta del test debe pertenecer al directorio de tests o tener prefijo/sufijo test: {v}"
            )
        return v


class TddRedPacket(BaseModel):
    ticket_id: str
    test_files: List[TestFileEntry] = Field(...)
    execution_command: str
    expected_failure_pattern: str = Field(...)
    red_phase_verified: Literal[True] = True
    red_phase_stdout: str


class CoderGreenPacket(BaseModel):
    ticket_id: str
    patch_unified_diff: str = Field(...)
    modified_files: List[str] = Field(...)
    ast_hunk_hashes: List[str] = Field(default_factory=list)
    green_phase_verified: Literal[True] = True
    green_phase_stdout: str
    local_tokens_consumed: int = Field(default=0, ge=0)

    @field_validator("patch_unified_diff")
    def validate_diff_format(cls, v: str) -> str:
        if not ("--- " in v and "+++ " in v and "@@ " in v):
            raise ValueError("El patch_unified_diff no tiene formato válido de unified diff de Git")
        return v

    @model_validator(mode="after")
    def compute_hunk_hashes(self) -> CoderGreenPacket:
        if not self.ast_hunk_hashes and self.patch_unified_diff:
            sha = hashlib.sha256(self.patch_unified_diff.encode("utf-8")).hexdigest()
            self.ast_hunk_hashes = [sha]
        return self


class CritiqueIssue(BaseModel):
    severity: Literal["P0", "P1", "P2"]
    file_path: str
    line_number: Optional[int] = None
    description: str
    counter_example: Optional[str] = None


class ComplexityMetric(BaseModel):
    cyclomatic_complexity_max: int
    time_complexity_asymptotic: str


class AdversarialReviewPacket(BaseModel):
    ticket_id: str
    critique_id: str
    verdict: Literal["APPROVED", "REFACTOR_REQUESTED"]
    issues: List[CritiqueIssue] = Field(default_factory=list)
    complexity_assessment: ComplexityMetric

    @model_validator(mode="after")
    def enforce_verdict_consistency(self) -> AdversarialReviewPacket:
        has_p0 = any(issue.severity == "P0" for issue in self.issues)
        if has_p0 and self.verdict == "APPROVED":
            raise ValueError(
                "Inconsistencia: No se puede emitir veredicto APPROVED con incidencias P0 activas"
            )
        return self


class SecurityAuditPacket(BaseModel):
    ticket_id: str
    audit_id: str
    verdict: Literal["APPROVED", "VETOED"]
    sandbox_escape_detected: bool = False
    secrets_leak_detected: bool = False
    command_injection_detected: bool = False
    path_traversal_detected: bool = False
    cwe_violations: List[str] = Field(default_factory=list)
    veto_reason: Optional[str] = None

    @model_validator(mode="after")
    def enforce_security_veto(self) -> SecurityAuditPacket:
        violations = (
            self.sandbox_escape_detected
            or self.secrets_leak_detected
            or self.command_injection_detected
            or self.path_traversal_detected
            or len(self.cwe_violations) > 0
        )
        if violations and self.verdict != "VETOED":
            raise ValueError(
                "Infracción Crítica: Se detectaron amenazas de seguridad. El veredicto DEBE ser VETOED"
            )
        if self.verdict == "VETOED" and not self.veto_reason:
            raise ValueError("Un veredicto VETOED exige una justificación formal en veto_reason")
        return self


# ============================================================================
# 4. ENVELOPE DE TRANSMISIÓN Y VALIDACIÓN EN RUNTIME
# ============================================================================

class ContextPacketEnvelope(BaseModel):
    ticket_id: str
    producer_role: RoleType
    schema_version: str = "v5.0"
    token_cost: int = Field(default=0, ge=0)
    payload_json: str
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate_payload(self) -> BaseModel:
        """
        Runtime Schema Validation Guardrail: Valida y deserializa la carga útil
        según el rol productor correspondiente.
        """
        data = json.loads(self.payload_json)
        match self.producer_role:
            case RoleType.INVESTIGADOR:
                return ResearchPacket.model_validate(data)
            case RoleType.ARQUITECTO:
                return ArchitectureContractPacket.model_validate(data)
            case RoleType.TESTER_TDD:
                return TddRedPacket.model_validate(data)
            case RoleType.CODER_GREEN:
                return CoderGreenPacket.model_validate(data)
            case RoleType.REVIEWER_HOSTIL:
                return AdversarialReviewPacket.model_validate(data)
            case RoleType.AUDITOR_SEGURIDAD:
                return SecurityAuditPacket.model_validate(data)
            case _:
                raise ValueError(f"Rol desconocido: {self.producer_role}")


# ============================================================================
# 5. ESTADO Y GOBERNANZA DE CIRCUIT BREAKERS
# ============================================================================

class CircuitBreakerState:
    """
    Controlador Determinista de Límites Rígidos y Zonas de Consumo.
    """
    def __init__(self, max_iter: int = 3, max_tokens: int = 150000):
        self.tdd_iterations: int = 0
        self.max_tdd_iterations: int = min(max_iter, 3)
        self.tokens_consumed: int = 0
        self.max_tokens_ceiling: int = min(max_tokens, 150000)
        self.is_tripped: bool = False
        self.trip_reason: Optional[str] = None

    def get_zone(self) -> TokenBudgetZone:
        ratio = self.tokens_consumed / max(1, self.max_tokens_ceiling)
        if ratio < 0.70:
            return TokenBudgetZone.NOMINAL
        elif ratio < 0.85:
            return TokenBudgetZone.AGGRESSIVE_AST_PRUNING
        elif ratio < 1.00:
            return TokenBudgetZone.CRITICAL_THROTTLE
        else:
            return TokenBudgetZone.HARD_STOP

    def record_tokens(self, tokens: int) -> None:
        if self.is_tripped:
            raise CircuitBreakerTrippedError(
                f"Transacción rechazada: Circuit Breaker disparado previamente ({self.trip_reason})"
            )
        self.tokens_consumed += max(0, tokens)
        if self.tokens_consumed >= self.max_tokens_ceiling:
            self.is_tripped = True
            err = (
                f"HARD STOP: Techo de tokens superado "
                f"({self.tokens_consumed}/{self.max_tokens_ceiling}). "
                "Operación cancelada determinísticamente."
            )
            self.trip_reason = err
            raise TokenCeilingExceededError(err)

    def increment_tdd_iteration(self) -> int:
        if self.is_tripped:
            raise CircuitBreakerTrippedError(
                f"Transacción rechazada: Circuit Breaker ya activo ({self.trip_reason})"
            )
        self.tdd_iterations += 1
        if self.tdd_iterations > self.max_tdd_iterations:
            self.is_tripped = True
            err = (
                f"CIRCUIT BREAKER: Máximas iteraciones TDD alcanzadas "
                f"({self.tdd_iterations}/{self.max_tdd_iterations})"
            )
            self.trip_reason = err
            raise CircuitBreakerTrippedError(err)
        return self.tdd_iterations

    def trip(self, reason: str) -> None:
        self.is_tripped = True
        self.trip_reason = reason


# ============================================================================
# 6. MOTOR BLACKBOARD CONCURRENTE (DAG DESACOPLADO)
# ============================================================================

class BlackboardEngine:
    """
    Blackboard Central Hearsay-II de El Aleph.
    Garantiza:
      1. Cero chat conversacional libre. Solo hechos verificados y contratos tipados.
      2. Validación estricta en frontera con Pydantic v2.
      3. Ejecución segura ante hilos (RLock).
      4. Bus de eventos determinista para máquinas de estado reactivas.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self.tasks_status: Dict[str, TaskStatus] = {}
        self.packets_store: Dict[str, List[ContextPacketEnvelope]] = {}
        self.breakers: Dict[str, CircuitBreakerState] = {}
        self.events_log: List[Dict[str, Any]] = []
        self._event_listeners: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        with self._lock:
            self._event_listeners.append(listener)

    def _emit_event(self, event_type: BlackboardEventType, ticket_id: str, payload: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "event_type": event_type.value,
            "ticket_id": ticket_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "payload": payload or {}
        }
        self.events_log.append(event)
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception:
                pass

    def ingest_ticket(self, ticket: TaskTicketPacket) -> None:
        with self._lock:
            if ticket.ticket_id in self.tasks_status:
                raise BlackboardError(f"Ticket {ticket.ticket_id} ya existe en el Blackboard")

            self.tasks_status[ticket.ticket_id] = TaskStatus.TICKET_INGESTED
            self.packets_store[ticket.ticket_id] = []
            self.breakers[ticket.ticket_id] = CircuitBreakerState(
                max_iter=ticket.max_tdd_iterations,
                max_tokens=ticket.budget_tokens_max
            )
            self._emit_event(BlackboardEventType.TICKET_INGESTED, ticket.ticket_id, ticket.model_dump())

    def post_packet(self, envelope: ContextPacketEnvelope) -> TaskStatus:
        with self._lock:
            ticket_id = envelope.ticket_id
            if ticket_id not in self.tasks_status:
                raise BlackboardError(f"Ticket {ticket_id} no registrado en Blackboard")

            breaker = self.breakers[ticket_id]
            if breaker.is_tripped:
                raise CircuitBreakerTrippedError(
                    f"Transacción rechazada: Circuit Breaker disparado ({breaker.trip_reason})"
                )

            # 1. Registrar consumo de tokens y verificar límite duro
            try:
                breaker.record_tokens(envelope.token_cost)
            except TokenCeilingExceededError as e:
                self.tasks_status[ticket_id] = TaskStatus.CIRCUIT_BREAKER_TRIPPED
                self._emit_event(BlackboardEventType.CIRCUIT_BREAKER_TRIGGERED, ticket_id, {"reason": str(e)})
                raise

            # 2. Runtime Schema Validation Guardrail (Rechazo en frontera)
            validated_model = envelope.validate_payload()

            # 3. Transición de Estado y Disparo de Eventos
            new_status: TaskStatus
            match envelope.producer_role:
                case RoleType.INVESTIGADOR:
                    self._emit_event(BlackboardEventType.RESEARCH_COMPLETED, ticket_id)
                    new_status = TaskStatus.ARCHITECTING

                case RoleType.ARQUITECTO:
                    self._emit_event(BlackboardEventType.CONTRACT_DRAFTED, ticket_id)
                    new_status = TaskStatus.TESTING_RED

                case RoleType.TESTER_TDD:
                    self._emit_event(BlackboardEventType.TESTS_RED_CONFIRMED, ticket_id)
                    new_status = TaskStatus.CODING_GREEN

                case RoleType.CODER_GREEN:
                    self._emit_event(BlackboardEventType.CODE_GREEN_PROPOSED, ticket_id)
                    new_status = TaskStatus.REVIEWING

                case RoleType.REVIEWER_HOSTIL:
                    review = validated_model
                    assert isinstance(review, AdversarialReviewPacket)
                    if review.verdict == "REFACTOR_REQUESTED":
                        # Solicitar refactor al Coder
                        self._emit_event(BlackboardEventType.CRITIQUE_COMPLETED, ticket_id, {"verdict": "REFACTOR_REQUESTED"})
                        new_status = TaskStatus.CODING_GREEN
                    else:
                        self._emit_event(BlackboardEventType.CRITIQUE_COMPLETED, ticket_id, {"verdict": "APPROVED"})
                        new_status = TaskStatus.AUDITING_SECURITY

                case RoleType.AUDITOR_SEGURIDAD:
                    audit = validated_model
                    assert isinstance(audit, SecurityAuditPacket)
                    if audit.verdict == "VETOED":
                        reason = audit.veto_reason or "Veto Unilateral Zero Trust"
                        breaker.trip(reason)
                        new_status = TaskStatus.QUARANTINED
                        self.tasks_status[ticket_id] = new_status
                        self._emit_event(BlackboardEventType.SECURITY_VETOED, ticket_id, {"reason": reason})
                        self.packets_store[ticket_id].append(envelope)
                        return new_status
                    else:
                        self._emit_event(BlackboardEventType.SECURITY_APPROVED, ticket_id)
                        new_status = TaskStatus.COMMITTED
                        self._emit_event(BlackboardEventType.TASK_COMMITTED, ticket_id)

                case _:
                    raise ValueError(f"Rol no mapeado: {envelope.producer_role}")

            self.tasks_status[ticket_id] = new_status
            self.packets_store[ticket_id].append(envelope)
            return new_status

    def handle_tdd_failure(self, ticket_id: str, reason: str = "") -> TaskStatus:
        with self._lock:
            breaker = self.breakers.get(ticket_id)
            if not breaker:
                raise BlackboardError(f"Ticket {ticket_id} no registrado")

            try:
                iteration = breaker.increment_tdd_iteration()
                st = TaskStatus.CODING_GREEN
                self.tasks_status[ticket_id] = st
                self._emit_event(BlackboardEventType.CIRCUIT_BREAKER_TRIGGERED, ticket_id, {
                    "action": "tdd_retry",
                    "iteration": iteration,
                    "reason": reason
                })
                return st
            except CircuitBreakerTrippedError as e:
                st = TaskStatus.CIRCUIT_BREAKER_TRIPPED
                self.tasks_status[ticket_id] = st
                self._emit_event(BlackboardEventType.CIRCUIT_BREAKER_TRIGGERED, ticket_id, {
                    "action": "hard_stop",
                    "reason": str(e)
                })
                raise

    def get_packets(self, ticket_id: str) -> List[ContextPacketEnvelope]:
        with self._lock:
            return list(self.packets_store.get(ticket_id, []))

    def get_latest_packet(self, ticket_id: str, role: Optional[RoleType] = None) -> Optional[ContextPacketEnvelope]:
        with self._lock:
            packets = self.packets_store.get(ticket_id, [])
            if not role:
                return packets[-1] if packets else None
            for p in reversed(packets):
                if p.producer_role == role:
                    return p
            return None

    def get_task_status(self, ticket_id: str) -> Optional[TaskStatus]:
        with self._lock:
            return self.tasks_status.get(ticket_id)

    def get_breaker(self, ticket_id: str) -> Optional[CircuitBreakerState]:
        with self._lock:
            return self.breakers.get(ticket_id)

    def get_events(self, ticket_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if ticket_id is None:
                return list(self.events_log)
            return [e for e in self.events_log if e.get("ticket_id") == ticket_id]


# ============================================================================
# 7. ROLES COMO FUNCIONES PURAS Y AISLAMIENTO EPISTÉMICO
# ============================================================================

def run_investigador_role(
    ticket: TaskTicketPacket,
    target_files: List[str],
    ast_symbols: List[AstSymbolAffected],
    existing_invariants: List[str],
    upstream: Optional[List[str]] = None,
    downstream: Optional[List[str]] = None
) -> ResearchPacket:
    """
    Rol 1: Investigador (O_RDONLY).
    Función pura: Genera ResearchPacket a partir del AST y el filesystem.
    Firewall Epistémico: Prohibido proponer código o soluciones futuras.
    """
    return ResearchPacket(
        ticket_id=ticket.ticket_id,
        target_files=target_files,
        ast_symbols_affected=ast_symbols,
        call_graph_upstream=upstream or [],
        call_graph_downstream=downstream or [],
        existing_invariants=existing_invariants
    )


def run_arquitecto_role(
    ticket: TaskTicketPacket,
    research: ResearchPacket,
    adr_id: str,
    decision_summary: str,
    alternatives_discarded: List[Dict[str, str]],
    type_contracts: List[TypeContract],
    function_signatures: List[FunctionSignatureSpec],
    required_invariants: List[str]
) -> ArchitectureContractPacket:
    """
    Rol 2: Arquitecto.
    Función pura: Genera ArchitectureContractPacket formal (ADR + Contratos de tipos).
    Firewall Epistémico: Prohibido escribir implementación de producción.
    """
    return ArchitectureContractPacket(
        ticket_id=ticket.ticket_id,
        adr_id=adr_id,
        decision_summary=decision_summary,
        alternatives_discarded=alternatives_discarded,
        type_contracts=type_contracts,
        function_signatures=function_signatures,
        required_invariants=required_invariants
    )


def run_tester_tdd_role(
    ticket: TaskTicketPacket,
    contract: ArchitectureContractPacket,
    test_files: List[TestFileEntry],
    execution_command: str,
    expected_failure_pattern: str,
    red_phase_stdout: str
) -> TddRedPacket:
    """
    Rol 3: Tester TDD (Red Phase / Blind Testing).
    Función pura: Genera la suite de tests que DEBE FALLAR con expected_failure_pattern.
    Firewall Epistémico: Blind Testing absoluto. NUNCA recibe el CoderGreenPacket ni el parche.
    """
    return TddRedPacket(
        ticket_id=ticket.ticket_id,
        test_files=test_files,
        execution_command=execution_command,
        expected_failure_pattern=expected_failure_pattern,
        red_phase_verified=True,
        red_phase_stdout=red_phase_stdout
    )


def run_coder_green_role(
    research: ResearchPacket,
    contract: ArchitectureContractPacket,
    red_packet: TddRedPacket,
    patch_unified_diff: str,
    modified_files: List[str],
    green_phase_stdout: str,
    local_tokens_consumed: int = 0
) -> CoderGreenPacket:
    """
    Rol 4: Coder (Green Phase / Parche Mínimo).
    Función pura: Produce el unified diff que pone en verde los tests de red_packet.
    Firewall Epistémico: ESTRICTAMENTE PROHIBIDO modificar archivos de tests.
    """
    # Verificación de Firewall: El Coder no puede tocar tests
    for f in modified_files:
        f_norm = f.replace("\\", "/").lower()
        if "test" in f_norm or f_norm.endswith("_spec.rs"):
            raise EpistemicFirewallViolation(
                f"Violación de Firewall: El Coder tiene prohibido modificar archivos de prueba: {f}"
            )

    return CoderGreenPacket(
        ticket_id=contract.ticket_id,
        patch_unified_diff=patch_unified_diff,
        modified_files=modified_files,
        green_phase_verified=True,
        green_phase_stdout=green_phase_stdout,
        local_tokens_consumed=local_tokens_consumed
    )


def run_reviewer_hostil_role(
    contract: ArchitectureContractPacket,
    red_packet: TddRedPacket,
    coder_packet: CoderGreenPacket,
    critique_id: str,
    verdict: Literal["APPROVED", "REFACTOR_REQUESTED"],
    issues: List[CritiqueIssue],
    complexity: ComplexityMetric
) -> AdversarialReviewPacket:
    """
    Rol 5: Reviewer Hostil (Fase 5 Demiurgo).
    Función pura: Audita diff y complejidad algorítmica.
    Firewall Epistémico: No recibe justificaciones verbales del Coder.
    """
    return AdversarialReviewPacket(
        ticket_id=contract.ticket_id,
        critique_id=critique_id,
        verdict=verdict,
        issues=issues,
        complexity_assessment=complexity
    )


def run_auditor_seguridad_role(
    ticket: TaskTicketPacket,
    contract: ArchitectureContractPacket,
    coder_packet: CoderGreenPacket,
    audit_id: str,
    sandbox_escape: bool = False,
    secrets_leak: bool = False,
    command_injection: bool = False,
    path_traversal: bool = False,
    cwe_violations: Optional[List[str]] = None,
    veto_reason: Optional[str] = None
) -> SecurityAuditPacket:
    """
    Rol 6: Auditor de Seguridad (Zero Trust Sentinel).
    Función pura: Emite veredicto binario con Veto Unilateral e irrevocable si hay riesgos.
    """
    has_threat = (
        sandbox_escape
        or secrets_leak
        or command_injection
        or path_traversal
        or bool(cwe_violations)
    )
    verdict: Literal["APPROVED", "VETOED"] = "VETOED" if has_threat else "APPROVED"
    reason = veto_reason
    if has_threat and not reason:
        reason = "Amenaza de seguridad detectada: Veto Unilateral Zero Trust"

    return SecurityAuditPacket(
        ticket_id=ticket.ticket_id,
        audit_id=audit_id,
        verdict=verdict,
        sandbox_escape_detected=sandbox_escape,
        secrets_leak_detected=secrets_leak,
        command_injection_detected=command_injection,
        path_traversal_detected=path_traversal,
        cwe_violations=cwe_violations or [],
        veto_reason=reason
    )


# ============================================================================
# 8. PODA AST Y TRACEBACK SQUEEZER (< 4,000 TOKENS POR CONTEXT PACKET)
# ============================================================================

def estimate_tokens(text: str) -> int:
    """Estimación determinista de tokens (heurística 1 token ~ 3.6 chars)."""
    if not text:
        return 0
    return max(1, int(len(text) / 3.6))


def verify_context_packet_budget(packet_json: str, max_tokens: int = 4000) -> int:
    """
    Verifica que el paquete serializado no sobrepase el presupuesto estricto.
    """
    tokens = estimate_tokens(packet_json)
    if tokens > max_tokens:
        raise ContextBudgetExceededError(
            f"Context Packet excede el límite rígido: {tokens} tokens > {max_tokens} tokens"
        )
    return tokens


def slice_ast_context(source_code: str, target_symbols: List[str], max_tokens: int = 4000) -> str:
    """
    AST Slicing Quirúrgico: Conserva clases, firmas, decoradores y docstrings breves.
    Reemplaza cuerpos de funciones no objetivo con '...  # [AST Pruned: body omitted]'
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # Fallback si no es Python o tiene sintaxis rota
        lines = source_code.splitlines()
        return "\n".join(lines[:120]) + ("\n... [Truncated]" if len(lines) > 120 else "")

    class AstPruner(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
            if node.name not in target_symbols:
                # Podar cuerpo reemplazándolo con Pass / Ellipsis
                node.body = [ast.Expr(value=ast.Constant(value=...))]
            return node

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
            if node.name not in target_symbols:
                node.body = [ast.Expr(value=ast.Constant(value=...))]
            return node

    pruned_tree = AstPruner().visit(tree)
    ast.fix_missing_locations(pruned_tree)
    try:
        pruned_code = ast.unparse(pruned_tree)
    except Exception:
        pruned_code = source_code

    if estimate_tokens(pruned_code) > max_tokens:
        # Poda secundaria por líneas si todavía excede
        lines = pruned_code.splitlines()
        max_lines = int(max_tokens * 3.6 / 40)
        return "\n".join(lines[:max_lines]) + "\n# ... [AST Hard Pruned]"
    return pruned_code


def squeeze_traceback(raw_traceback: str, max_lines: int = 20) -> str:
    """
    Traceback Squeezing: Extrae aserciones fallidas y omite frames internos de librerías.
    """
    lines = raw_traceback.splitlines()
    filtered: List[str] = []
    capture = False

    for line in lines:
        # Omitir frames de pytest y site-packages
        if "site-packages" in line or "pytest" in line and "test_" not in line:
            continue
        if "E   assert" in line or "AssertionError" in line or "FAILED" in line or "ERROR" in line:
            filtered.append(line)
            capture = True
        elif capture and (line.startswith("E ") or line.startswith(">")):
            filtered.append(line)
        elif "test_" in line and ("def " in line or ".py:" in line):
            filtered.append(line)

    if not filtered:
        # Fallback a las últimas líneas relevantes
        filtered = lines[-max_lines:] if len(lines) > max_lines else lines

    return "\n".join(filtered[:max_lines])


# ============================================================================
# 9. ORQUESTADOR DE SANDBOX Y REGRESSION SENTINEL
# ============================================================================

class SquadOrchestrator:
    """
    Orquestador de Sandbox y Guardián de Regresiones (Regression Sentinel).
    Maneja ejecución en subprocesos, Git atomic rollback y verificación TDD.
    """
    def __init__(
        self,
        workspace_path: str = ".",
        blackboard: Optional[BlackboardEngine] = None,
        max_tokens: int = 150000,
        max_iter: int = 3
    ):
        self.workspace_path = workspace_path
        self.blackboard = blackboard or BlackboardEngine()
        self.max_tokens = min(max_tokens, 150000)
        self.max_iter = min(max_iter, 3)
        self.tokens_accumulated = 0
        self.tdd_iteration = 0
        self.baseline_tests_passed = 0

    def run_command(self, cmd: Union[str, Sequence[str]], timeout_sec: int = 45) -> subprocess.CompletedProcess:
        """Ejecuta un comando vectorizado (argv[], shell=False, CWE-78 = 0%) en el sandbox del workspace."""
        if isinstance(cmd, str):
            raw_tokens = shlex.split(cmd, posix=(os.name != "nt"))
            argv = [t[1:-1] if len(t) >= 2 and t[0] == t[-1] and t[0] in ('"', "'") else t for t in raw_tokens]
        else:
            argv = [str(part) for part in cmd]
        if not argv:
            raise ValueError("El comando a ejecutar no puede estar vacío.")
        return subprocess.run(
            argv,
            shell=False,
            cwd=self.workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )

    def record_tokens(self, count: int) -> None:
        self.tokens_accumulated += max(0, count)
        if self.tokens_accumulated >= self.max_tokens:
            raise TokenCeilingExceededError(
                f"HARD STOP: Techo de tokens superado ({self.tokens_accumulated}/{self.max_tokens}). "
                "Operación cancelada determinísticamente."
            )

    def capture_baseline_tests(self, test_cmd: str) -> int:
        """Regression Sentinel: Registra el conteo de tests que pasan antes del parche."""
        res = self.run_command(test_cmd)
        passed = self._extract_passed_count(res.stdout + " " + res.stderr)
        self.baseline_tests_passed = passed
        return passed

    def _extract_passed_count(self, output: str) -> int:
        # Busca patrones tipo '14 passed', '1 passed, 0 failed'
        match = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Fallback a conteo de 'ok' o 'PASSED'
        return len(re.findall(r"\bPASSED\b", output))

    def rollback_workspace(self) -> None:
        """Rollback atómico mediante Git Reset."""
        self.run_command("git reset --hard HEAD")
        self.run_command("git clean -fd")

    def verify_tdd_red(self, test_cmd: str, expected_pattern: str) -> bool:
        """
        Verifica que la suite de pruebas falle determinísticamente.
        Si pasa en verde sin código, rechaza de inmediato (Tautological Test).
        """
        res = self.run_command(test_cmd)
        if res.returncode == 0:
            raise TautologicalTestError(
                "Los tests pasan en verde sin implementación. Suite tautológica rechazada."
            )
        combined = (res.stdout or "") + "\n" + (res.stderr or "")
        if expected_pattern not in combined:
            return False
        return True

    def verify_tdd_green(self, test_cmd: str) -> bool:
        """Verifica que todos los tests pasen en verde con el parche aplicado."""
        res = self.run_command(test_cmd)
        return res.returncode == 0

    def verify_regressions(self, full_suite_cmd: str) -> bool:
        """
        Regression Sentinel: Invariante de monotonicidad de pruebas preexistentes.
        """
        res = self.run_command(full_suite_cmd)
        current_passed = self._extract_passed_count((res.stdout or "") + " " + (res.stderr or ""))
        if res.returncode != 0 or current_passed < self.baseline_tests_passed:
            self.rollback_workspace()
            raise RegressionDetectedError(
                f"Regresión detectada: {current_passed} passed < {self.baseline_tests_passed} baseline."
            )
        return True
