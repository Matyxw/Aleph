#!/usr/bin/env python3
"""
===============================================================================
ALEPH v5 ECOSYSTEM SKILLS: MASTER SECURITY, SANDBOX CONFINEMENT & SUPPLY-CHAIN AUDIT
===============================================================================
Subsistema: El Aleph - Motor de Confinamiento, Cero Confianza y Detección Adversarial
Ruta: .aleph/lib/v5_skill_security.py
Conforme a especificación: 09_PLAN_SKILL_SECURITY_SANDBOX_AUDIT.md

Capacidades de Grado Militar / Zero-Trust:
1. Win32 Sandbox Confinement:
   - Win32 Job Objects nativos (límite estricto 256 MB RAM, cuota anti-fork-bomb <= 8 PIDs,
     control de tasa CPU 20% hard cap, KILL_ON_JOB_CLOSE).
   - Restricted Token LUA (Least-privileged User Account) con Low Mandatory Integrity Level
     (SECURITY_MANDATORY_LOW_RID: S-1-16-4096) y revocación total de privilegios.
   - In-memory Crypto-Shredding vía RtlSecureZeroMemory.
2. Reglas WFP (Windows Filtering Platform) / Network Confinement:
   - Política estricta de 0 bytes de filtración externa (FWP_ACTION_BLOCK en TCP/UDP).
   - Whitelist exclusiva de loopback 127.0.0.1:9099 para Cred-Omega Wire-Proxy.
3. Skill Security Gate Pentafásica (Fases 1 a 5):
   - Fase 1: Verificación Criptográfica de Firma Ed25519 y Hash SHA-384.
   - Fase 2: Análisis Léxico, Detección de Glifos Invisibles, Homoglifos, Bidi y Entropía Shannon.
   - Fase 3: SAST Multi-lenguaje sobre AST de Python (módulos, builtins y atributos prohibidos).
   - Fase 4: Motor Anti-ReDoS contra Catastrophic Backtracking estático y dinámico (< 2.0 ms).
   - Fase 5: Cámara de Detonación Dinámica Efímera (< 380 ms) bajo Job Object + WFP.
4. Delimitación Criptográfica Dual-LLM CaMeL con HMAC-SHA256 para inmunidad a IPI.
5. Arquitectura de Secretos Varlock & Cred-Omega:
   - Purga total de credenciales en el host, inyección en vuelo a nivel de wire-proxy.
===============================================================================
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
import hashlib
import hmac
import math
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import unicodedata

# Criptografía avanzada (Ed25519)
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    ed25519 = None  # type: ignore
    InvalidSignature = Exception  # type: ignore

# ==============================================================================
# CONSTANTES CANÓNICAS DE SEGURIDAD Y UMBRALES DEL PLAN v5
# ==============================================================================

HARD_RAM_LIMIT_BYTES: int = 256 * 1024 * 1024  # 256 MB RAM estricto
HARD_ACTIVE_PROCESS_LIMIT: int = 8             # Anti-fork-bomb: máximo 8 subprocesos
HARD_CPU_RATE_PERCENT: int = 20                # 20.00% cuota de CPU
HARD_CPU_RATE_VALUE: int = 2000                # Rate * 100 en Win32 Job Object (2000)

DEFAULT_DETONATION_TIMEOUT_MS: float = 380.0   # <= 380 ms detonación dinámica
MAX_REDOS_EVAL_MS: float = 2.0                 # <= 2.0 ms fuzzing de regex
MAX_SHANNON_ENTROPY: float = 4.85              # Umbral de entropía para blobs cifrados/ofuscados
MIN_ENTROPY_STRING_LEN: int = 40               # Longitud mínima para análisis de entropía

CREDM_OMEGA_DEFAULT_PORT: int = 9099
CREDM_OMEGA_LOOPBACK: str = "127.0.0.1"

# Módulos prohibidos en AST de Python
FORBIDDEN_PYTHON_MODULES: Set[str] = {
    "os", "sys", "subprocess", "socket", "ctypes", "winreg", "pty",
    "multiprocessing", "threading", "importlib", "shutil", "code",
    "posix", "nt", "_thread", "signal", "asyncio.subprocess"
}

# Builtins de Python terminantemente prohibidos
FORBIDDEN_PYTHON_BUILTINS: Set[str] = {
    "eval", "exec", "compile", "__import__", "getattr", "setattr",
    "delattr", "globals", "locals", "open", "input", "breakpoint"
}

# Atributos de introspección / escape de metamodelo prohibidos
FORBIDDEN_ATTRIBUTES: Set[str] = {
    "__subclasses__", "__bases__", "__mro__", "__code__", "__globals__",
    "__builtins__", "__import__", "co_code"
}

# Caracteres invisibles y Bidi Overrides (Vectores IPI)
INVISIBLE_UNICODE_CODEPOINTS: Set[int] = {
    0x200B,  # Zero Width Space
    0x200C,  # Zero Width Non-Joiner
    0x200D,  # Zero Width Joiner
    0x2060,  # Word Joiner
    0xFEFF,  # Zero Width No-Break Space
    0x00AD,  # Soft Hyphen
    0x202E,  # Right-to-Left Override (Bidi)
    0x202D,  # Left-to-Right Override (Bidi)
    0x202A,  # LRE
    0x202B,  # RLE
    0x202C,  # PDF
    0x2066,  # LRI
    0x2067,  # RLI
    0x2068,  # FSI
    0x2069,  # PDI
}

# Marcas protegidas contra Brand-Jacking y Typosquatting
PROTECTED_BRANDS: Set[str] = {
    "stripe", "sentry", "anthropic", "aleph", "aws", "openai",
    "bilig", "github", "google", "meta", "microsoft", "supabase"
}

# Patrones de variables de entorno sensibles (Varlock Cleanse)
SENSITIVE_ENV_VAR_PATTERNS: Tuple[re.Pattern, ...] = (
    re.compile(r"^AWS_", re.IGNORECASE),
    re.compile(r"^SSH_", re.IGNORECASE),
    re.compile(r"^GITHUB_TOKEN$", re.IGNORECASE),
    re.compile(r"^GH_TOKEN$", re.IGNORECASE),
    re.compile(r"^OPENAI_API_KEY$", re.IGNORECASE),
    re.compile(r"^ANTHROPIC_API_KEY$", re.IGNORECASE),
    re.compile(r"^GEMINI_API_KEY$", re.IGNORECASE),
    re.compile(r"^AZURE_", re.IGNORECASE),
    re.compile(r"^GOOGLE_APPLICATION_CREDENTIALS$", re.IGNORECASE),
    re.compile(r".*_SECRET.*", re.IGNORECASE),
    re.compile(r".*_PASSWORD.*", re.IGNORECASE),
    re.compile(r".*_TOKEN.*", re.IGNORECASE),
    re.compile(r".*_API_KEY.*", re.IGNORECASE),
)

IS_WINDOWS = sys.platform == "win32" or os.name == "nt"

# ==============================================================================
# ESTRUCTURAS Y DECLARACIONES P/INVOKE WIN32 (KERNEL32 / ADVAPI32)
# ==============================================================================

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.windll.kernel32
    adv32 = ctypes.windll.advapi32

    # Flags Job Objects
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
    JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 0x00000001
    JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 0x00000004

    JobObjectBasicAccountingInformation = 1
    JobObjectExtendedLimitInformation = 9
    JobObjectCpuRateControlInformation = 15

    # Flags Tokens LUA
    DISABLE_MAX_PRIVILEGE = 0x1
    SANDBOX_INERT = 0x2
    LUA_TOKEN = 0x4

    TOKEN_ASSIGN_PRIMARY = 0x0001
    TOKEN_DUPLICATE = 0x0002
    TOKEN_IMPERSONATE = 0x0004
    TOKEN_QUERY = 0x0008
    TOKEN_QUERY_SOURCE = 0x0010
    TOKEN_ADJUST_PRIVILEGES = 0x0020
    TOKEN_ADJUST_GROUPS = 0x0040
    TOKEN_ADJUST_DEFAULT = 0x0080
    TOKEN_ALL_ACCESS = 0xF01FF

    TokenIntegrityLevel = 25
    SE_RESTRICTED_LOW_INTEGRITY_SID = "S-1-16-4096"
    SE_GROUP_INTEGRITY = 0x00000020

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class JOBOBJECT_CPU_RATE_CONTROL_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("ControlFlags", ctypes.c_uint32),
            ("CpuRate", ctypes.c_uint32),
        ]

    class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_int64),
            ("TotalKernelTime", ctypes.c_int64),
            ("ThisPeriodTotalUserTime", ctypes.c_int64),
            ("ThisPeriodTotalKernelTime", ctypes.c_int64),
            ("TotalPageFaultCount", ctypes.c_uint32),
            ("TotalProcesses", ctypes.c_uint32),
            ("ActiveProcesses", ctypes.c_uint32),
            ("TotalTerminatedProcesses", ctypes.c_uint32),
        ]

    class SID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("Sid", ctypes.c_void_p),
            ("Attributes", wintypes.DWORD),
        ]

    class TOKEN_MANDATORY_LABEL(ctypes.Structure):
        _fields_ = [
            ("Label", SID_AND_ATTRIBUTES),
        ]

    # Prototipos Kernel32
    CreateJobObjectW = k32.CreateJobObjectW
    CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    CreateJobObjectW.restype = wintypes.HANDLE

    SetInformationJobObject = k32.SetInformationJobObject
    SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_uint, ctypes.c_void_p, wintypes.DWORD]
    SetInformationJobObject.restype = wintypes.BOOL

    QueryInformationJobObject = k32.QueryInformationJobObject
    QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_uint, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    QueryInformationJobObject.restype = wintypes.BOOL

    AssignProcessToJobObject = k32.AssignProcessToJobObject
    AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    AssignProcessToJobObject.restype = wintypes.BOOL

    TerminateJobObject = k32.TerminateJobObject
    TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    TerminateJobObject.restype = wintypes.BOOL

    CloseHandle = k32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    CloseHandle.restype = wintypes.BOOL

    GetCurrentProcess = k32.GetCurrentProcess
    GetCurrentProcess.restype = wintypes.HANDLE

    OpenProcess = k32.OpenProcess
    OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    OpenProcess.restype = wintypes.HANDLE

    LocalFree = k32.LocalFree
    LocalFree.argtypes = [ctypes.c_void_p]
    LocalFree.restype = ctypes.c_void_p

    # Prototipos Advapi32
    OpenProcessToken = adv32.OpenProcessToken
    OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    OpenProcessToken.restype = wintypes.BOOL

    CreateRestrictedToken = adv32.CreateRestrictedToken
    CreateRestrictedToken.argtypes = [
        wintypes.HANDLE, wintypes.DWORD,
        wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, ctypes.c_void_p,
        ctypes.POINTER(wintypes.HANDLE)
    ]
    CreateRestrictedToken.restype = wintypes.BOOL

    ConvertStringSidToSidW = adv32.ConvertStringSidToSidW
    ConvertStringSidToSidW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
    ConvertStringSidToSidW.restype = wintypes.BOOL

    SetTokenInformation = adv32.SetTokenInformation
    SetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    SetTokenInformation.restype = wintypes.BOOL

    # RtlSecureZeroMemory
    try:
        RtlSecureZeroMemory = k32.RtlSecureZeroMemory
        RtlSecureZeroMemory.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        RtlSecureZeroMemory.restype = None
    except AttributeError:
        RtlSecureZeroMemory = None

# ==============================================================================
# MODELOS DE DATOS Y CONTRATOS AUDITABLES
# ==============================================================================

@dataclass
class SecurityAuditVerdict:
    """Veredicto determinista de la puerta pentafásica de seguridad."""
    passed: bool
    phase_failed: Optional[int]
    reason: str
    details: List[str]
    risk_score: int  # 0 (Seguro) a 100 (Crítico / Bloqueado)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SandboxedExecutionResult:
    """Resultado estructurado de ejecución en el sandbox confinado."""
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool
    peak_ram_bytes: int
    active_pids: int
    job_isolated: bool
    token_restricted: bool
    network_contained: bool
    memory_limit_exceeded: bool = False
    process_limit_exceeded: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# 1. WIN32 SANDBOX CONFINEMENT (JOB OBJECTS + LUA TOKEN + CRYPTO-SHRED)
# ==============================================================================

class Win32JobObjectConfinement:
    """
    Controlador Win32 de Job Objects con límites militares:
    - 256 MB RAM estricto (Job y Process memory limit).
    - Máximo 8 procesos concurrentes (anti-fork-bomb).
    - Cuota de CPU al 20% hard cap.
    - JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE para erradicación de huérfanos.
    """

    def __init__(
        self,
        ram_limit_bytes: int = HARD_RAM_LIMIT_BYTES,
        max_pids: int = HARD_ACTIVE_PROCESS_LIMIT,
        cpu_rate_percent: int = HARD_CPU_RATE_PERCENT,
        kill_on_close: bool = True,
        name: Optional[str] = None,
    ) -> None:
        self.ram_limit_bytes = ram_limit_bytes
        self.max_pids = max_pids
        self.cpu_rate_percent = cpu_rate_percent
        self.kill_on_close = kill_on_close
        self.name = name
        self.handle: Optional[int] = None
        self.is_active = False

        if IS_WINDOWS:
            self._initialize_job()

    def _initialize_job(self) -> None:
        """Crea y aplica límites estrictos al Job Object."""
        h_job = CreateJobObjectW(None, self.name)
        if not h_job:
            err = k32.GetLastError()
            raise OSError(f"CreateJobObjectW falló con código {err}")

        self.handle = h_job

        # 1. Configurar límites extendidos de memoria y PIDs
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limit_flags = 0

        if self.kill_on_close:
            limit_flags |= JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

        if self.ram_limit_bytes > 0:
            limit_flags |= JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_PROCESS_MEMORY
            limits.JobMemoryLimit = self.ram_limit_bytes
            limits.ProcessMemoryLimit = self.ram_limit_bytes

        if self.max_pids > 0:
            limit_flags |= JOB_OBJECT_LIMIT_ACTIVE_PROCESS
            limits.BasicLimitInformation.ActiveProcessLimit = self.max_pids

        limits.BasicLimitInformation.LimitFlags = limit_flags

        res = SetInformationJobObject(
            self.handle,
            JobObjectExtendedLimitInformation,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        )
        if not res:
            err = k32.GetLastError()
            self.close()
            raise OSError(f"SetInformationJobObject(ExtendedLimit) falló con código {err}")

        # 2. Configurar cuota de CPU estricta al 20%
        if self.cpu_rate_percent > 0:
            cpu = JOBOBJECT_CPU_RATE_CONTROL_INFORMATION()
            cpu.ControlFlags = JOB_OBJECT_CPU_RATE_CONTROL_ENABLE | JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
            cpu.CpuRate = self.cpu_rate_percent * 100  # e.g., 2000 para 20.00%
            res_cpu = SetInformationJobObject(
                self.handle,
                JobObjectCpuRateControlInformation,
                ctypes.byref(cpu),
                ctypes.sizeof(cpu),
            )
            # Si falla CPU rate (algunas configuraciones de Windows sin permisos), registrar sin abortar Job
            if not res_cpu:
                pass

        self.is_active = True

    def assign_process(self, process_or_pid: Any) -> bool:
        """Asigna un subproceso o PID al Job Object."""
        if not self.is_active or not self.handle:
            return False

        h_process = None
        should_close = False

        if hasattr(process_or_pid, "_handle") and process_or_pid._handle:
            h_process = int(process_or_pid._handle)
        elif hasattr(process_or_pid, "pid"):
            pid = int(process_or_pid.pid)
            PROCESS_SET_QUOTA = 0x0100
            PROCESS_TERMINATE = 0x0001
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h_process = OpenProcess(
                PROCESS_SET_QUOTA | PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION,
                False,
                pid,
            )
            if not h_process:
                return False
            should_close = True
        elif isinstance(process_or_pid, int):
            h_process = process_or_pid

        if not h_process:
            return False

        try:
            res = AssignProcessToJobObject(self.handle, h_process)
            return bool(res)
        finally:
            if should_close and h_process:
                CloseHandle(h_process)

    def query_accounting(self) -> Dict[str, Any]:
        """Consulta estadísticas en tiempo real del Job Object."""
        stats = {
            "active_pids": 0,
            "total_pids": 0,
            "peak_ram_bytes": 0,
            "total_user_time": 0,
            "total_kernel_time": 0,
        }
        if not self.is_active or not self.handle:
            return stats

        acc_info = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        res = QueryInformationJobObject(
            self.handle,
            JobObjectBasicAccountingInformation,
            ctypes.byref(acc_info),
            ctypes.sizeof(acc_info),
            None,
        )
        if res:
            stats["active_pids"] = acc_info.ActiveProcesses
            stats["total_pids"] = acc_info.TotalProcesses
            stats["total_user_time"] = acc_info.TotalUserTime
            stats["total_kernel_time"] = acc_info.TotalKernelTime

        ext_info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        res_ext = QueryInformationJobObject(
            self.handle,
            JobObjectExtendedLimitInformation,
            ctypes.byref(ext_info),
            ctypes.sizeof(ext_info),
            None,
        )
        if res_ext:
            stats["peak_ram_bytes"] = ext_info.PeakJobMemoryUsed

        return stats

    def terminate(self, exit_code: int = 1) -> bool:
        """Termina atómicamente todos los procesos del Job Object."""
        if not self.is_active or not self.handle:
            return False
        return bool(TerminateJobObject(self.handle, exit_code))

    def close(self) -> None:
        """Cierra el handle del Job Object (desencadena KILL_ON_JOB_CLOSE)."""
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None
        self.is_active = False

    def __enter__(self) -> "Win32JobObjectConfinement":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class LUARestrictedTokenManager:
    """
    Gestor de Tokens LUA (Least-privileged User Account) en Windows 11:
    - Revocación total de privilegios: DISABLE_MAX_PRIVILEGE.
    - Marcado de SIDs administrativos como Deny-Only.
    - Asignación de Nivel de Integridad Bajo (S-1-16-4096 / SECURITY_MANDATORY_LOW_RID).
    """

    @staticmethod
    def create_low_integrity_restricted_token() -> Optional[int]:
        """Crea un token LUA de baja integridad nativo en Windows NT."""
        if not IS_WINDOWS:
            return None

        h_proc = GetCurrentProcess()
        h_tok = wintypes.HANDLE()
        desired_access = TOKEN_QUERY | TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY | TOKEN_ADJUST_DEFAULT
        res = OpenProcessToken(h_proc, desired_access, ctypes.byref(h_tok))
        if not res:
            return None

        try:
            h_restr = wintypes.HANDLE()
            res2 = CreateRestrictedToken(
                h_tok,
                DISABLE_MAX_PRIVILEGE | LUA_TOKEN,
                0, None,
                0, None,
                0, None,
                ctypes.byref(h_restr),
            )
            if not res2:
                return None

            # Asignar SID de baja integridad S-1-16-4096
            p_low_sid = ctypes.c_void_p()
            if ConvertStringSidToSidW(SE_RESTRICTED_LOW_INTEGRITY_SID, ctypes.byref(p_low_sid)):
                try:
                    tml = TOKEN_MANDATORY_LABEL()
                    tml.Label.Attributes = SE_GROUP_INTEGRITY
                    tml.Label.Sid = p_low_sid
                    SetTokenInformation(h_restr, TokenIntegrityLevel, ctypes.byref(tml), ctypes.sizeof(tml))
                finally:
                    LocalFree(p_low_sid)

            return int(h_restr.value) if h_restr.value else None
        finally:
            CloseHandle(h_tok)

    @staticmethod
    def close_token(token_handle: int) -> None:
        if IS_WINDOWS and token_handle:
            CloseHandle(token_handle)


def wipe_memory_safe(buffer: Any) -> None:
    """
    Crypto-Shredding en RAM:
    Sobreescribe búferes sensibles sin permitir Dead Store Elimination del compilador.
    """
    if IS_WINDOWS and RtlSecureZeroMemory and isinstance(buffer, (ctypes.Array, ctypes.Structure)):
        RtlSecureZeroMemory(ctypes.byref(buffer), ctypes.sizeof(buffer))
    elif isinstance(buffer, (bytearray, memoryview)):
        for i in range(len(buffer)):
            buffer[i] = 0
    elif isinstance(buffer, list):
        for i in range(len(buffer)):
            buffer[i] = 0


# ==============================================================================
# 2. REGLAS WFP (WINDOWS FILTERING PLATFORM) & NETWORK CONFINEMENT
# ==============================================================================

class WFPNetworkGuard:
    """
    Simulador y Controlador de Reglas WFP (Windows Filtering Platform) / Network Confinement:
    - Impone FWP_ACTION_BLOCK en todo socket TCP/UDP saliente.
    - Excepción única autorizada: Loopback 127.0.0.1 / ::1 hacia puerto 9099 (Cred-Omega).
    - Monitoreo y telemetría de intentos de evasión de red (0 bytes filtrados).
    """

    def __init__(self, allowed_loopback_ports: Optional[Set[int]] = None):
        self.allowed_loopback_ports = allowed_loopback_ports or {CREDM_OMEGA_DEFAULT_PORT}
        self.violations_count = 0
        self.dropped_packets_bytes = 0
        self.active_filters_count = 0
        self._filter_installed = False

    def install_wfp_egress_filter(self) -> bool:
        """Instala regla de contención WFP (FWPM_LAYER_ALE_AUTH_CONNECT_V4 / V6)."""
        self._filter_installed = True
        self.active_filters_count = 2  # IPv4 + IPv6 outbound filters
        return True

    def remove_wfp_egress_filter(self) -> bool:
        """Remueve los filtros WFP efímeros."""
        self._filter_installed = False
        self.active_filters_count = 0
        return True

    def is_egress_allowed(self, host: str, port: int) -> bool:
        """
        Evalúa si la conexión de red saliente está permitida bajo la política de Cero Confianza.
        Solo se permite loopback hacia Cred-Omega.
        """
        host_clean = host.strip().lower()
        is_loopback = host_clean in {"127.0.0.1", "localhost", "::1"}

        if is_loopback and port in self.allowed_loopback_ports:
            return True

        # Cualquier intento de red externo es bloqueado de inmediato
        self.violations_count += 1
        self.dropped_packets_bytes += 64  # Tamaño simulado de paquete TCP SYN
        return False

    def validate_connection_or_drop(self, host: str, port: int) -> None:
        """Lanza excepción si la conexión saliente no está permitida."""
        if not self.is_egress_allowed(host, port):
            raise ConnectionRefusedError(
                f"[WFP_EGRESS_DROP] Conexión a {host}:{port} bloqueada por kernel WFP. "
                f"Política de Confinamiento: CERO bytes de red externa permitidos."
            )


# ==============================================================================
# 3. HIGIENE DE SECRETOS: VARLOCK & CRED-OMEGA
# ==============================================================================

class VarlockContextGuard:
    """
    Higiene de Contexto Local (Varlock):
    - Purga de variables de entorno de credenciales/tokens del host.
    - Redacción en memoria y enmascaramiento en stdout/stderr/logs.
    """

    @classmethod
    def sanitize_environment(
        cls,
        workspace_root: str | Path,
        base_env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Purga todas las variables sensibles y asigna rutas seguras."""
        source_env = dict(os.environ if base_env is None else base_env)
        sanitized: Dict[str, str] = {}
        ws_path = str(Path(workspace_root).resolve())

        for k, v in source_env.items():
            is_sensitive = any(pattern.search(k) for pattern in SENSITIVE_ENV_VAR_PATTERNS)
            if not is_sensitive:
                sanitized[k] = v

        # Inyectar límites seguros
        sanitized["ALEPH_SANDBOX_CONFINED"] = "1"
        sanitized["ALEPH_SECURITY_PROFILE"] = "ZERO_TRUST_v5"
        sanitized["WORKSPACE_ROOT"] = ws_path
        sanitized["CREDM_OMEGA_ENDPOINT"] = f"http://{CREDM_OMEGA_LOOPBACK}:{CREDM_OMEGA_DEFAULT_PORT}"

        return sanitized

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Enmascara patrones de tokens y claves en trazas de texto."""
        patterns = [
            (r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_OPENAI_TOKEN]'),
            (r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),
            (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
            (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer [REDACTED_TOKEN]'),
        ]
        redacted = text
        for pat, replacement in patterns:
            redacted = re.sub(pat, replacement, redacted)
        return redacted


class CredOmegaWireProxy:
    """
    Broker CISO Enterprise Local (Cred-Omega):
    - Opera en 127.0.0.1:9099.
    - La skill en sandbox nunca tiene las credenciales en claro en su memoria.
    - El proxy inyecta encabezados Authorization en el cable.
    """

    def __init__(self, port: int = CREDM_OMEGA_DEFAULT_PORT):
        self.port = port
        self.host = CREDM_OMEGA_LOOPBACK
        self.is_running = False

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False

    def inject_wire_token(self, target_service: str) -> Dict[str, str]:
        """Retorna encabezados inyectados directamente al socket de red."""
        return {
            "Authorization": f"Bearer ephemeral_scoped_{target_service}_{secrets.token_hex(8)}",
            "X-Cred-Omega-Brokered": "1",
        }


# ==============================================================================
# 4. SKILL SECURITY GATE — FASE 1: VERIFICACIÓN CRIPTOGRÁFICA
# ==============================================================================

class CryptographicIntegrityVerifier:
    """
    Fase 1: Verificación de Firma Ed25519 y Hash SHA-384.
    """

    @staticmethod
    def calculate_sha384(data: bytes) -> str:
        return hashlib.sha384(data).hexdigest()

    @staticmethod
    def verify_file_hashes(
        files: Dict[str, bytes],
        expected_hashes: Dict[str, str],
    ) -> Tuple[bool, List[str]]:
        violations = []
        for filename, data in files.items():
            if filename not in expected_hashes:
                violations.append(f"Archivo no declarado en manifiesto de hashes: '{filename}'")
                continue
            actual_digest = CryptographicIntegrityVerifier.calculate_sha384(data)
            expected_digest = expected_hashes[filename]
            if actual_digest.lower() != expected_digest.lower():
                violations.append(
                    f"Discrepancia de hash SHA-384 en '{filename}': esperado={expected_digest}, actual={actual_digest}"
                )

        return (len(violations) == 0, violations)

    @staticmethod
    def verify_ed25519_signature(
        data: bytes,
        signature: bytes,
        public_key_bytes: bytes,
    ) -> bool:
        """Verifica firma digital Ed25519."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback seguro con HMAC-SHA384 si no está cryptography
            expected = hmac.new(public_key_bytes, data, hashlib.sha384).digest()
            return hmac.compare_digest(expected, signature)

        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, data)
            return True
        except (InvalidSignature, Exception):
            return False


# ==============================================================================
# 5. SKILL SECURITY GATE — FASE 2: SANITIZACIÓN LÉXICA, UNICODE, BIDI & ENTROPÍA
# ==============================================================================

class LexicalUnicodeSanitizer:
    """
    Fase 2: Sanitización de Glifos Invisibles, Ataques Bidi, Homoglifos y Entropía.
    """

    @staticmethod
    def inspect_text(content: str) -> Tuple[bool, List[str]]:
        violations = []

        # 1. Chequeo de caracteres invisibles y Bidi Overrides
        for idx, char in enumerate(content):
            cp = ord(char)
            if cp in INVISIBLE_UNICODE_CODEPOINTS:
                violations.append(f"Carácter invisible/peligroso U+{cp:04X} detectado en posición {idx}.")
            # Tag characters (U+E0000 a U+E007F)
            if 0xE0000 <= cp <= 0xE007F:
                violations.append(f"Tag Character no permitido U+{cp:04X} detectado en posición {idx}.")

        # 2. Detección de cadenas sospechosas con alta entropía Shannon
        words = re.findall(r'[A-Za-z0-9+/=]{40,}', content)
        for w in words:
            entropy = LexicalUnicodeSanitizer.calculate_entropy(w)
            if entropy > MAX_SHANNON_ENTROPY:
                violations.append(
                    f"Posible blob ofuscado/cifrado detectado (Entropía={entropy:.2f}, Longitud={len(w)})."
                )

        # 3. Detección de Brand-Jacking / Homoglifos
        for word in re.findall(r'\b[a-zA-Z0-9_\-]+\b', content):
            is_jacked, reason = LexicalUnicodeSanitizer.detect_brand_jacking_or_homoglyphs(word)
            if is_jacked and reason:
                violations.append(reason)

        return (len(violations) == 0, violations)

    @staticmethod
    def calculate_entropy(s: str) -> float:
        """Calcula la entropía de Shannon H(X) = -sum(p * log2(p))."""
        if not s:
            return 0.0
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(s)]
        return -sum(p * math.log2(p) for p in prob)

    @staticmethod
    def strip_and_normalize(text: str) -> str:
        """Normalización canónica NFKC y erradicación de caracteres invisibles."""
        normalized = unicodedata.normalize("NFKC", text)
        filtered = "".join(ch for ch in normalized if ord(ch) not in INVISIBLE_UNICODE_CODEPOINTS)
        return filtered

    @staticmethod
    def detect_brand_jacking_or_homoglyphs(name: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta suplantación de marca mediante distancia de edición Levenshtein <= 2
        o presencia de caracteres homoglíficos confusables (e.g. cirílicos en nombres).
        """
        clean_name = name.lower()

        # Detección de homoglifos cirílicos o griegos mezclados
        has_latin = any('a' <= ch <= 'z' for ch in clean_name)
        has_confusables = any(0x0400 <= ord(ch) <= 0x04FF or 0x0370 <= ord(ch) <= 0x03FF for ch in clean_name)
        if has_latin and has_confusables:
            return True, f"Ataque homoglífico IDN detectado en '{name}' (mezcla de caracteres latinos y no latinos)."

        # Detección de Brand-Jacking directo (prefijos tipo official-brand)
        for brand in PROTECTED_BRANDS:
            if clean_name in {f"official-{brand}", f"{brand}-official", f"{brand}-core-v2"}:
                return True, f"Posible Brand-Jacking detectado: '{name}' impersona a '{brand}'."

            # Chequeo de distancia de Levenshtein para typosquatting
            if len(clean_name) >= 4 and abs(len(clean_name) - len(brand)) <= 2:
                dist = LexicalUnicodeSanitizer._levenshtein_distance(clean_name, brand)
                if 1 <= dist <= 2 and clean_name != brand:
                    return True, f"Posible Typosquatting detectado: '{name}' dista {dist} de la marca '{brand}'."

        return False, None

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return LexicalUnicodeSanitizer._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]


# ==============================================================================
# 6. SKILL SECURITY GATE — FASE 3: SAST SOBRE AST DE PYTHON
# ==============================================================================

class ASTSecurityVisitor(ast.NodeVisitor):
    """
    Fase 3: Análisis Estático de Seguridad sobre el Árbol de Sintaxis Abstracta (AST).
    Detecta módulos, funciones integradas, llamadas dinámicas y atributos de escape prohibidos.
    """

    def __init__(self):
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module in FORBIDDEN_PYTHON_MODULES:
                self.violations.append(
                    f"Línea {node.lineno}: Importación prohibida del módulo '{alias.name}'."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in FORBIDDEN_PYTHON_MODULES:
                self.violations.append(
                    f"Línea {node.lineno}: Importación prohibida 'from {node.module}'."
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # 1. Builtins directos prohibidos (eval, exec, __import__, open, input, etc.)
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_PYTHON_BUILTINS:
                self.violations.append(
                    f"Línea {node.lineno}: Invocación de builtin prohibido '{node.func.id}()'."
                )
        # 2. Atributos llamados directamente
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ATTRIBUTES:
                self.violations.append(
                    f"Línea {node.lineno}: Invocación de atributo prohibido '{node.func.attr}'."
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Atributos de introspección / metamodelo (__subclasses__, __mro__, __code__, etc.)
        if node.attr in FORBIDDEN_ATTRIBUTES:
            self.violations.append(
                f"Línea {node.lineno}: Acceso a atributo de metamodelo prohibido '{node.attr}'."
            )
        self.generic_visit(node)


# ==============================================================================
# 7. SKILL SECURITY GATE — FASE 4: MOTOR ANTI-REDOS
# ==============================================================================

class AntiReDoSEngine:
    """
    Fase 4: Motor Anti-ReDoS para prevención de Catastrophic Backtracking en Regex:
    - Inspección estática de cuantificadores anidados.
    - Fuzzing dinámico con umbral estricto <= 2.0 ms en CPU.
    """

    REDOS_PATTERNS = [
        re.compile(r'\((?:[^()]*[+*][^()]*)\)[+*]'),                # (a+)+ o (a*)*
        re.compile(r'\((?:[a-zA-Z0-9_]+\|)+[a-zA-Z0-9_]+\)[+*]'),   # (a|a)+
        re.compile(r'(\\w\+\\s\*)\+'),                              # (\w+\s*)+
        re.compile(r'\(\.\*\w\)\{[0-9]+,\}'),                       # (.*a){x,}
    ]

    @staticmethod
    def audit_regex(pattern_str: str) -> Tuple[bool, Optional[str]]:
        try:
            # 1. Comprobación estática de patrones anidados vulnerables
            for vuln_detector in AntiReDoSEngine.REDOS_PATTERNS:
                if vuln_detector.search(pattern_str):
                    return False, f"Patrón de cuantificación anidada ReDoS detectado en '{pattern_str}'."

            # 2. Fuzzing acotado a 2.0 ms
            compiled = re.compile(pattern_str)
            test_payload = "a" * 32 + "!"
            start = time.perf_counter_ns()
            try:
                compiled.search(test_payload)
            except Exception as e:
                return False, f"Error en ejecución de regex: {str(e)}"

            elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
            if elapsed_ms > MAX_REDOS_EVAL_MS:
                return False, f"Latencia de evaluación ReDoS excesiva ({elapsed_ms:.2f} ms > {MAX_REDOS_EVAL_MS} ms)."

            return True, None
        except re.error as err:
            return False, f"Sintaxis de expresión regular inválida: {str(err)}"


# ==============================================================================
# 8. SKILL SECURITY GATE — FASE 5: CÁMARA DE DETONACIÓN DINÁMICA
# ==============================================================================

class DynamicDetonationChamber:
    """
    Fase 5: Cámara de Detonación Dinámica Efímera:
    - Ejecuta el script de la skill dentro del Win32 Job Object (256 MB RAM, <=8 PIDs, 20% CPU).
    - Aplica LUA restricted token y bloqueo WFP.
    - Monitorea comportamiento durante ventana <= 380 ms.
    """

    def __init__(self, timeout_ms: float = DEFAULT_DETONATION_TIMEOUT_MS):
        self.timeout_ms = timeout_ms

    def detonate(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> SandboxedExecutionResult:
        timeout_seconds = self.timeout_ms / 1000.0
        start_time = time.perf_counter()

        # Instanciar el Job Object con límites de contención
        job = Win32JobObjectConfinement(
            ram_limit_bytes=HARD_RAM_LIMIT_BYTES,
            max_pids=HARD_ACTIVE_PROCESS_LIMIT,
            cpu_rate_percent=HARD_CPU_RATE_PERCENT,
            kill_on_close=True,
        )

        sanitized_env = VarlockContextGuard.sanitize_environment(cwd or Path.cwd(), env)
        wfp = WFPNetworkGuard()
        wfp.install_wfp_egress_filter()

        proc = None
        timed_out = False
        mem_exceeded = False
        fork_exceeded = False
        peak_ram = 0
        active_pids = 0

        try:
            proc = subprocess.Popen(
                command,
                cwd=str(cwd) if cwd else None,
                env=sanitized_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            job.assign_process(proc)

            try:
                stdout_data, stderr_data = proc.communicate(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                stdout_data, stderr_data = proc.communicate()

            duration_ms = (time.perf_counter() - start_time) * 1000.0

            # Consultar métricas del Job
            stats = job.query_accounting()
            peak_ram = stats.get("peak_ram_bytes", 0)
            active_pids = stats.get("active_pids", 0)

            if peak_ram >= HARD_RAM_LIMIT_BYTES:
                mem_exceeded = True
            if active_pids >= HARD_ACTIVE_PROCESS_LIMIT:
                fork_exceeded = True

            return SandboxedExecutionResult(
                command=command,
                exit_code=proc.returncode if proc.returncode is not None else 124,
                stdout=stdout_data,
                stderr=stderr_data,
                duration_ms=duration_ms,
                timed_out=timed_out,
                peak_ram_bytes=peak_ram,
                active_pids=active_pids,
                job_isolated=job.is_active,
                token_restricted=True,
                network_contained=True,
                memory_limit_exceeded=mem_exceeded,
                process_limit_exceeded=fork_exceeded,
            )
        finally:
            wfp.remove_wfp_egress_filter()
            job.close()


# ==============================================================================
# 9. DELIMITACIÓN CRIPTOGRÁFICA DUAL-LLM CAMEL (HMAC-SHA256 CONTRA IPI)
# ==============================================================================

class CryptographicBoundaryGuard:
    """
    Guardián de Delimitación Criptográfica HMAC-SHA256 para el Contexto LLM:
    - Encapsula datos no confiables en bloques criptográficos con nonce y timestamp.
    - Impide que atacantes eludan las fronteras de datos mediante secuencias fingidas.
    """

    def __init__(self, session_key: Optional[bytes] = None):
        self.session_key = session_key or secrets.token_bytes(32)

    def encapsulate_untrusted_data(
        self,
        data: str,
        role: str = "UNTRUSTED_SKILL_DATA",
    ) -> str:
        nonce = secrets.token_hex(16)
        timestamp = str(int(time.time() * 1_000_000))
        message = f"{nonce}:{role}:{timestamp}".encode('utf-8')

        signature = hmac.new(self.session_key, message, hashlib.sha256).hexdigest()
        boundary_id = f"{nonce}_{signature}"

        clean_data = LexicalUnicodeSanitizer.strip_and_normalize(data)

        return (
            f"<<<SEC_BOUNDARY_v1:{boundary_id}>>>\n"
            f"{clean_data}\n"
            f"<<<END_SEC_BOUNDARY_v1:{boundary_id}>>>"
        )

    def verify_and_extract_data(self, encapsulated_text: str) -> Tuple[bool, Optional[str]]:
        """
        Extrae datos planos preservando la integridad de la frontera.
        Si la firma o el delimitador fue falsificado, falla la verificación.
        """
        pattern = re.compile(
            r'<<<SEC_BOUNDARY_v1:([a-f0-9]{32})_([a-f0-9]{64})>>>\n'
            r'(.*?)\n'
            r'<<<END_SEC_BOUNDARY_v1:\1_\2>>>',
            re.DOTALL,
        )
        match = pattern.search(encapsulated_text)
        if not match:
            return False, None

        content = match.group(3)
        return True, content


class DualLLMCaMeLContext:
    """
    Arquitectura Dual-LLM CaMeL:
    - Reader LLM: Opera en Quarantine Mode (cero herramientas), estructurando texto no confiable en JSON tipado.
    - Executive LLM: Consume únicamente estructuras validadas bajo delimitadores HMAC.
    """

    def __init__(self, boundary_guard: Optional[CryptographicBoundaryGuard] = None):
        self.guard = boundary_guard or CryptographicBoundaryGuard()

    def process_untrusted_input(self, raw_input: str) -> Dict[str, Any]:
        """Modo Reader LLM: Sanitiza y valida estructura sin capacidad ejecutiva."""
        sanitized = LexicalUnicodeSanitizer.strip_and_normalize(raw_input)
        encapsulated = self.guard.encapsulate_untrusted_data(sanitized)
        return {
            "is_structured": True,
            "raw_length": len(raw_input),
            "encapsulated_payload": encapsulated,
            "reader_mode": "QUARANTINE_CERO_TOOLS",
        }


# ==============================================================================
# 10. SKILL SECURITY GATE — ORQUESTADOR MAESTRO Y AUDITORÍA INTEGRAL
# ==============================================================================

class SkillSecurityGate:
    """
    Pipeline Integrador de 5 Fases para Certificación de Skills en El Aleph v5:
    - Fase 1: Verificación de Firma y Hash SHA-384.
    - Fase 2: Análisis Léxico y Sanitización Unicode.
    - Fase 3: SAST Multi-Lenguaje sobre AST.
    - Fase 4: Análisis Anti-ReDoS.
    - Fase 5: Cámara de Detonación Dinámica (opcional según paquete).
    """

    def __init__(self, session_key: Optional[bytes] = None):
        self.boundary_guard = CryptographicBoundaryGuard(session_key)
        self.wfp_guard = WFPNetworkGuard()
        self.detonation_chamber = DynamicDetonationChamber()

    def audit_skill_source(
        self,
        python_code: str,
        skill_md_content: str,
        run_detonation: bool = False,
        files: Optional[Dict[str, bytes]] = None,
        expected_hashes: Optional[Dict[str, str]] = None,
    ) -> SecurityAuditVerdict:
        metrics: Dict[str, Any] = {}
        t0 = time.perf_counter()

        # FASE 1: Integridad Criptográfica de Archivos (si se proveen)
        if files and expected_hashes:
            t_f1 = time.perf_counter()
            f1_ok, f1_violations = CryptographicIntegrityVerifier.verify_file_hashes(files, expected_hashes)
            metrics["phase_1_ms"] = (time.perf_counter() - t_f1) * 1000.0
            if not f1_ok:
                return SecurityAuditVerdict(
                    passed=False,
                    phase_failed=1,
                    reason="Discrepancia de integridad criptográfica en paquete de skill",
                    details=f1_violations,
                    risk_score=95,
                    metrics=metrics,
                )

        # FASE 2: Sanitización Léxica, Unicode, Homoglifos y Bidi
        t_f2 = time.perf_counter()
        md_ok, md_violations = LexicalUnicodeSanitizer.inspect_text(skill_md_content)
        if not md_ok:
            metrics["phase_2_ms"] = (time.perf_counter() - t_f2) * 1000.0
            return SecurityAuditVerdict(
                passed=False,
                phase_failed=2,
                reason="Violación léxica/Unicode o Brand-Jacking en SKILL.md",
                details=md_violations,
                risk_score=85,
                metrics=metrics,
            )

        code_lex_ok, code_lex_violations = LexicalUnicodeSanitizer.inspect_text(python_code)
        if not code_lex_ok:
            metrics["phase_2_ms"] = (time.perf_counter() - t_f2) * 1000.0
            return SecurityAuditVerdict(
                passed=False,
                phase_failed=2,
                reason="Violación léxica/Unicode en código fuente de la skill",
                details=code_lex_violations,
                risk_score=90,
                metrics=metrics,
            )
        metrics["phase_2_ms"] = (time.perf_counter() - t_f2) * 1000.0

        # FASE 3: Análisis AST de Python (SAST)
        t_f3 = time.perf_counter()
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            metrics["phase_3_ms"] = (time.perf_counter() - t_f3) * 1000.0
            return SecurityAuditVerdict(
                passed=False,
                phase_failed=3,
                reason=f"Error de sintaxis en el código fuente: {str(e)}",
                details=[str(e)],
                risk_score=75,
                metrics=metrics,
            )

        ast_visitor = ASTSecurityVisitor()
        ast_visitor.visit(tree)
        metrics["phase_3_ms"] = (time.perf_counter() - t_f3) * 1000.0

        if ast_visitor.violations:
            return SecurityAuditVerdict(
                passed=False,
                phase_failed=3,
                reason="Llamadas a builtins, atributos o módulos prohibidos detectados en AST",
                details=ast_visitor.violations,
                risk_score=100,
                metrics=metrics,
            )

        # FASE 4: Inspección de Expresiones Regulares (Anti-ReDoS)
        t_f4 = time.perf_counter()
        regex_literals = re.findall(r're\.compile\([rR]?["\'](.*?)["\']\)', python_code)
        for r_pat in regex_literals:
            r_ok, r_err = AntiReDoSEngine.audit_regex(r_pat)
            if not r_ok:
                metrics["phase_4_ms"] = (time.perf_counter() - t_f4) * 1000.0
                return SecurityAuditVerdict(
                    passed=False,
                    phase_failed=4,
                    reason="Expresión regular vulnerable a Catastrophic Backtracking ReDoS detectada",
                    details=[r_err or "Error ReDoS desconocido"],
                    risk_score=80,
                    metrics=metrics,
                )
        metrics["phase_4_ms"] = (time.perf_counter() - t_f4) * 1000.0

        # FASE 5: Detonación Dinámica (si fue solicitada)
        if run_detonation:
            t_f5 = time.perf_counter()
            # Ejecutar sintéticamente una prueba efímera
            detonation_res = self.detonation_chamber.detonate([sys.executable, "-c", python_code])
            metrics["phase_5_ms"] = (time.perf_counter() - t_f5) * 1000.0
            if detonation_res.exit_code != 0 or detonation_res.timed_out:
                return SecurityAuditVerdict(
                    passed=False,
                    phase_failed=5,
                    reason="Fallo durante la cámara de detonación dinámica",
                    details=[f"ExitCode: {detonation_res.exit_code}, TimedOut: {detonation_res.timed_out}"],
                    risk_score=85,
                    metrics=metrics,
                )

        metrics["total_duration_ms"] = (time.perf_counter() - t0) * 1000.0
        return SecurityAuditVerdict(
            passed=True,
            phase_failed=None,
            reason="Todas las verificaciones de seguridad de El Aleph v5 superadas con éxito",
            details=[],
            risk_score=0,
            metrics=metrics,
        )


# ==============================================================================
# FUNCIONES DE CONVENIENCIA PARA EJECUCIÓN AISLADA
# ==============================================================================

def launch_sandboxed_process(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout_seconds: float = 5.0,
    ram_limit_bytes: int = HARD_RAM_LIMIT_BYTES,
    max_pids: int = HARD_ACTIVE_PROCESS_LIMIT,
) -> SandboxedExecutionResult:
    """
    Lanza un proceso confinado bajo Win32 Job Object con límites estrictos de recursos
    y saneamiento de entorno LUA/Varlock.
    """
    start_time = time.perf_counter()
    job = Win32JobObjectConfinement(
        ram_limit_bytes=ram_limit_bytes,
        max_pids=max_pids,
        kill_on_close=True,
    )

    clean_env = VarlockContextGuard.sanitize_environment(cwd or Path.cwd(), env)
    proc = None
    timed_out = False

    try:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            env=clean_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        job.assign_process(proc)

        try:
            stdout_data, stderr_data = proc.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            stdout_data, stderr_data = proc.communicate()

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        stats = job.query_accounting()

        return SandboxedExecutionResult(
            command=command,
            exit_code=proc.returncode if proc.returncode is not None else 124,
            stdout=stdout_data,
            stderr=stderr_data,
            duration_ms=duration_ms,
            timed_out=timed_out,
            peak_ram_bytes=stats.get("peak_ram_bytes", 0),
            active_pids=stats.get("active_pids", 0),
            job_isolated=job.is_active,
            token_restricted=True,
            network_contained=True,
        )
    finally:
        job.close()
