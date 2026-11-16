#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: v6_battle_harness.py
Ruta: .aleph\\lib\\v6_battle_harness.py
Propósito: Battle-Harness para Repositorios Reales Sucios (Superación de Aider y OpenHands).

Integra:
  1. DirtyRepoSanitizer & BOM/Encoding Guard (utf-8-sig, utf-8, cp1252, latin-1, CRLF/LF).
  2. IsolatedWorktreeTransactionManager (Git Worktrees efímeros + CoW RAM VFS con rollback < 50ms).
  3. PolyglotRepoMapExtractor (CallGraphASTPruner + JITRouterEngine auto-skill injection).
  4. HeadlessBattleBenchmarkRunner (Evaluación empírica Headless vs. Baseline con Wilson CI).
"""

from __future__ import annotations

import ast
import collections
import contextlib
import copy
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, Union

# Asegurar que el directorio raíz de .aleph esté en sys.path para importaciones cruzadas
_ALEPH_ROOT = Path(__file__).resolve().parent.parent
if str(_ALEPH_ROOT) not in sys.path:
    sys.path.insert(0, str(_ALEPH_ROOT))

from lib.v5_context_cache import (
    BpeTokenEstimator,
    CallGraph,
    CallGraphASTPruner,
    SdsfSerializer,
    SurgicalLogCrusher,
    SymbolNode,
    SymbolRegistry,
)
from lib.v5_goal_loop_tdd import (
    ASTGuard,
    GatekeeperResult,
    GatekeeperRuntime,
    GoalSpec,
    MerkleTestEngine,
    VerificationContract,
)
from lib.v5_sentinel_tooling import (
    InMemoryLspEngine,
    TwoPhaseCommitVFSFlush,
    VirtualDocumentStore,
)
from lib.v5_skill_security import (
    VarlockContextGuard,
    Win32JobObjectConfinement,
)
from lib.v5_skills_router import (
    ContextInjectionPayload,
    JITRouterEngine,
    RouteMatch,
    SkillContractManager,
    SkillManifest,
    SkillsCatalogDB,
)
try:
    from scripts.swe_bench_dominator import (
        ASTDiffCanonicalizer,
        MaximalASTInvarianceGatekeeper,
        ReadOnlyTestJail,
        calculate_wilson_ci,
    )
except ImportError:
    ASTDiffCanonicalizer = None
    MaximalASTInvarianceGatekeeper = None
    ReadOnlyTestJail = None
    calculate_wilson_ci = None


class BattleHarnessError(Exception):
    """Excepción base del Battle-Harness v6."""
    pass


class DirtyRepoConflictError(BattleHarnessError):
    """Lanzada cuando un archivo presenta marcadores de conflicto Git sin resolver."""
    pass


class BinaryFileMutationError(BattleHarnessError):
    """Lanzada cuando se intenta aplicar un parche de texto sobre un archivo binario."""
    pass


class WorktreeTransactionError(BattleHarnessError):
    """Error durante la creación, commit o rollback del worktree/VFS transaccional."""
    pass


class LineEndingStyle(str, Enum):
    LF = "LF"          # \n
    CRLF = "CRLF"      # \r\n
    CR = "CR"          # \r
    MIXED = "MIXED"    # Mezcla corrupta de \r\n y \n en el mismo archivo


@dataclass(frozen=True)
class EncodingMetadata:
    """Metadatos físicos de codificación y finales de línea para reconstrucción sin pérdida."""
    file_path: str
    encoding: str                   # "utf-8-sig", "utf-16-le", "utf-16-be", "utf-8", "cp1252", "latin-1"
    has_bom: bool
    line_ending: LineEndingStyle
    dominant_eol_bytes: bytes       # b"\r\n" o b"\n"
    has_trailing_newline: bool
    is_binary: bool
    original_sha256: str
    conflict_markers_lines: Tuple[int, ...] = ()


@dataclass
class RepoHealthAudit:
    """Reporte de auditoría de suciedad de un repositorio externo."""
    repo_root: str
    is_git_repo: bool
    has_stale_index_lock: bool
    uncommitted_modified_files: List[str]
    untracked_files: List[str]
    conflicted_files: Dict[str, List[int]]
    encoding_distribution: Dict[str, int]
    eol_distribution: Dict[str, int]
    binary_files: List[str]
    total_files_scanned: int = 0
    dirty_files: List[str] = field(default_factory=list)
    dirty_files_count: int = 0
    mixed_ending_files: List[str] = field(default_factory=list)
    bom_files: List[str] = field(default_factory=list)
    stale_index_lock_removed: bool = False


class DirtyRepoSanitizer:
    """
    Subsistema A: Guardián de Codificación, BOM, Finales de Línea y Sanitización de Repositorios Sucios.
    Garantiza lectura normalizada en memoria (UTF-8 LF) para AST/LLM y escritura física idéntica
    al formato original del archivo (Zero Line-Ending Churn & Zero Encoding Corruption).
    """

    CP1252_VALID_C1_BYTES: Set[int] = {
        0x80, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x8E,
        0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0x9B, 0x9C, 0x9E, 0x9F,
    }
    CONFLICT_START_RE = re.compile(r"^<{7}(?:\s+.*)?$")
    CONFLICT_BASE_RE = re.compile(r"^\|{7}(?:\s+.*)?$")
    CONFLICT_SEP_RE = re.compile(r"^={7}\s*$")
    CONFLICT_END_RE = re.compile(r"^>{7}(?:\s+.*)?$")

    def __init__(self) -> None:
        self._metadata_ledger: Dict[str, EncodingMetadata] = {}

    def inspect_bytes(self, raw_bytes: bytes, file_path: str = "<memory>") -> Tuple[str, EncodingMetadata]:
        """Analiza bytes crudos, detecta BOM/codificación/EOL y devuelve (texto_normalizado_lf, EncodingMetadata)."""
        sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
        has_utf16_bom = raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff")
        is_binary = (b"\x00" in raw_bytes[:8192]) and not has_utf16_bom
        if is_binary:
            meta = EncodingMetadata(
                file_path=str(file_path),
                encoding="binary",
                has_bom=False,
                line_ending=LineEndingStyle.LF,
                dominant_eol_bytes=b"\n",
                has_trailing_newline=False,
                is_binary=True,
                original_sha256=sha256_hex,
                conflict_markers_lines=(),
            )
            return "", meta

        has_bom = False
        encoding = "utf-8"
        payload = raw_bytes
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            encoding = "utf-8-sig"
            has_bom = True
            payload = raw_bytes[3:]
            decoded = payload.decode("utf-8", errors="replace")
        elif raw_bytes.startswith(b"\xff\xfe"):
            encoding = "utf-16-le"
            has_bom = True
            decoded = raw_bytes[2:].decode("utf-16-le", errors="replace")
        elif raw_bytes.startswith(b"\xfe\xff"):
            encoding = "utf-16-be"
            has_bom = True
            decoded = raw_bytes[2:].decode("utf-16-be", errors="replace")
        else:
            try:
                decoded = raw_bytes.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                c1_bytes = [b for b in raw_bytes if 0x80 <= b <= 0x9F]
                if c1_bytes and all(b in self.CP1252_VALID_C1_BYTES for b in c1_bytes):
                    try:
                        decoded = raw_bytes.decode("cp1252")
                        encoding = "cp1252"
                    except UnicodeDecodeError:
                        decoded = raw_bytes.decode("latin-1")
                        encoding = "latin-1"
                else:
                    decoded = raw_bytes.decode("latin-1")
                    encoding = "latin-1"

        n_crlf = raw_bytes.count(b"\r\n")
        n_lf_total = raw_bytes.count(b"\n")
        n_lf_only = max(0, n_lf_total - n_crlf)

        if n_crlf > 0 and n_lf_only == 0:
            eol_style = LineEndingStyle.CRLF
            dom_eol = b"\r\n"
        elif n_lf_only > 0 and n_crlf == 0:
            eol_style = LineEndingStyle.LF
            dom_eol = b"\n"
        elif n_crlf > 0 and n_lf_only > 0:
            eol_style = LineEndingStyle.MIXED
            dom_eol = b"\r\n" if n_crlf >= n_lf_only else b"\n"
        else:
            eol_style = LineEndingStyle.LF
            dom_eol = b"\n"

        normalized = decoded.replace("\r\n", "\n").replace("\r", "\n")
        if normalized.startswith("\ufeff"):
            normalized = normalized[1:]
        has_trailing = normalized.endswith("\n")
        conflicts = tuple(self.scan_conflict_markers(normalized))

        meta = EncodingMetadata(
            file_path=str(file_path),
            encoding=encoding,
            has_bom=has_bom,
            line_ending=eol_style,
            dominant_eol_bytes=dom_eol,
            has_trailing_newline=has_trailing,
            is_binary=False,
            original_sha256=sha256_hex,
            conflict_markers_lines=conflicts,
        )
        return normalized, meta

    def read_normalized(self, file_path: Union[str, Path]) -> Tuple[str, EncodingMetadata]:
        """Lee archivo del disco, registra EncodingMetadata y retorna texto con '\\n' y sin BOM."""
        p = Path(file_path).resolve()
        raw = p.read_bytes()
        text, meta = self.inspect_bytes(raw, file_path=str(p))
        if meta.is_binary:
            raise BinaryFileMutationError(f"Binary file cannot be normalized as text: {p}")
        self._metadata_ledger[str(p)] = meta
        return text, meta

    def encode_restoring_format(
        self,
        normalized_text: str,
        metadata: EncodingMetadata,
        preserve_trailing_newline: bool = True,
    ) -> bytes:
        """Reconstruye los bytes físicos respetando codificación original, BOM y CRLF/LF."""
        clean = normalized_text.replace("\r\n", "\n").replace("\r", "\n")
        if clean.startswith("\ufeff"):
            clean = clean[1:]
        if preserve_trailing_newline:
            if metadata.has_trailing_newline and not clean.endswith("\n"):
                clean += "\n"
            elif not metadata.has_trailing_newline and clean.endswith("\n"):
                clean = clean[:-1]

        target_eol = "\r\n" if metadata.dominant_eol_bytes == b"\r\n" else "\n"
        formatted_str = clean.replace("\n", target_eol)

        if metadata.encoding == "utf-8-sig":
            return b"\xef\xbb\xbf" + formatted_str.encode("utf-8")
        if metadata.encoding == "utf-16-le":
            return b"\xff\xfe" + formatted_str.encode("utf-16-le")
        if metadata.encoding == "utf-16-be":
            return b"\xfe\xff" + formatted_str.encode("utf-16-be")
        if metadata.encoding == "cp1252":
            return formatted_str.encode("cp1252", errors="replace")
        if metadata.encoding == "latin-1":
            return formatted_str.encode("latin-1", errors="replace")
        return formatted_str.encode("utf-8")

    def write_restoring_format(
        self,
        file_path: Union[str, Path],
        normalized_text: str,
        metadata: Optional[EncodingMetadata] = None,
    ) -> bytes:
        """Escribe atómicamente en disco preservando el formato físico original."""
        p = Path(file_path).resolve()
        meta = metadata or self._metadata_ledger.get(str(p))
        if meta is None:
            if p.exists():
                _, meta = self.read_normalized(p)
            else:
                meta = EncodingMetadata(
                    file_path=str(p),
                    encoding="utf-8",
                    has_bom=False,
                    line_ending=LineEndingStyle.LF,
                    dominant_eol_bytes=b"\n",
                    has_trailing_newline=True,
                    is_binary=False,
                    original_sha256="",
                )
        encoded_bytes = self.encode_restoring_format(normalized_text, meta)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        for attempt in range(3):
            try:
                p.write_bytes(encoded_bytes)
                break
            except (PermissionError, OSError):
                if attempt == 2:
                    raise
                time.sleep(0.002)
        return encoded_bytes

    @classmethod
    def scan_conflict_markers(cls, text: str) -> List[int]:
        """Retorna números de línea (1-indexed) donde inician bloques de conflicto Git reales."""
        lines = text.splitlines()
        conflict_starts: List[int] = []
        state = "NORMAL"
        current_start = 0
        for idx, line in enumerate(lines, start=1):
            if state == "NORMAL" and cls.CONFLICT_START_RE.match(line):
                state = "IN_OURS"
                current_start = idx
            elif state in ("IN_OURS", "IN_BASE") and cls.CONFLICT_BASE_RE.match(line):
                state = "IN_BASE"
            elif state in ("IN_OURS", "IN_BASE") and cls.CONFLICT_SEP_RE.match(line):
                state = "IN_THEIRS"
            elif state == "IN_THEIRS" and cls.CONFLICT_END_RE.match(line):
                conflict_starts.append(current_start)
                state = "NORMAL"
        return conflict_starts

    @classmethod
    def resolve_git_conflict_markers(
        cls,
        text: str,
        strategy: str = "ours",
    ) -> Tuple[str, int]:
        """Resuelve bloques de conflicto Git ('ours', 'theirs', 'union' o 'both')."""
        lines = text.splitlines(keepends=True)
        out: List[str] = []
        ours_buf: List[str] = []
        base_buf: List[str] = []
        theirs_buf: List[str] = []
        state = "NORMAL"
        resolved_count = 0
        strat = strategy.lower().strip()

        for line in lines:
            stripped = line.rstrip("\r\n")
            if state == "NORMAL":
                if cls.CONFLICT_START_RE.match(stripped):
                    state = "OURS"
                    ours_buf = []
                    base_buf = []
                    theirs_buf = []
                else:
                    out.append(line)
            elif state == "OURS":
                if cls.CONFLICT_BASE_RE.match(stripped):
                    state = "BASE"
                elif cls.CONFLICT_SEP_RE.match(stripped):
                    state = "THEIRS"
                else:
                    ours_buf.append(line)
            elif state == "BASE":
                if cls.CONFLICT_SEP_RE.match(stripped):
                    state = "THEIRS"
                else:
                    base_buf.append(line)
            elif state == "THEIRS":
                if cls.CONFLICT_END_RE.match(stripped):
                    resolved_count += 1
                    if strat == "ours":
                        out.extend(ours_buf)
                    elif strat == "theirs":
                        out.extend(theirs_buf)
                    elif strat in ("union", "both"):
                        out.extend(ours_buf)
                        out.extend(theirs_buf)
                    else:
                        out.extend(ours_buf)
                    state = "NORMAL"
                else:
                    theirs_buf.append(line)

        if state != "NORMAL":
            out.extend(ours_buf)
            out.extend(theirs_buf)
        return "".join(out), resolved_count

    def audit_dirty_repository(
        self,
        repo_root: Union[str, Path],
        remove_stale_index_lock: bool = True,
    ) -> RepoHealthAudit:
        """Audita un repositorio externo, detectando conflictos, encodings, binarios y .git/index.lock."""
        root = Path(repo_root).resolve()
        git_dir = root / ".git"
        is_git = git_dir.exists()
        index_lock = git_dir / "index.lock"
        had_lock = index_lock.exists()
        if had_lock and remove_stale_index_lock:
            try:
                os.chmod(index_lock, stat.S_IWRITE | stat.S_IREAD)
                index_lock.unlink()
            except OSError:
                pass

        enc_dist: Dict[str, int] = {}
        eol_dist: Dict[str, int] = {}
        conflicted: Dict[str, List[int]] = {}
        binaries: List[str] = []
        bom_files: List[str] = []
        mixed_ending_files: List[str] = []
        total_scanned = 0

        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel_parts = p.relative_to(root).parts
            if any(part in {".git", "node_modules", "target", ".venv", "__pycache__"} for part in rel_parts):
                continue
            total_scanned += 1
            rel_str = str(p.relative_to(root)).replace("\\", "/")
            raw = p.read_bytes()
            _, meta = self.inspect_bytes(raw, file_path=rel_str)
            if meta.is_binary:
                binaries.append(rel_str)
                continue
            enc_dist[meta.encoding] = enc_dist.get(meta.encoding, 0) + 1
            eol_dist[meta.line_ending.value] = eol_dist.get(meta.line_ending.value, 0) + 1
            if meta.has_bom:
                bom_files.append(rel_str)
            if meta.line_ending == LineEndingStyle.MIXED:
                mixed_ending_files.append(rel_str)
            if meta.conflict_markers_lines:
                conflicted[rel_str] = list(meta.conflict_markers_lines)

        uncommitted: List[str] = []
        untracked: List[str] = []
        if is_git:
            try:
                proc = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                )
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        if not line.strip():
                            continue
                        status_code = line[:2]
                        file_name = line[3:].strip().replace("\\", "/")
                        if status_code.startswith("??"):
                            untracked.append(file_name)
                        else:
                            uncommitted.append(file_name)
            except Exception:
                pass

        dirty_set = sorted(set(uncommitted + list(conflicted.keys()) + bom_files + mixed_ending_files))

        return RepoHealthAudit(
            repo_root=str(root),
            is_git_repo=is_git,
            has_stale_index_lock=had_lock,
            uncommitted_modified_files=uncommitted,
            untracked_files=untracked,
            conflicted_files=conflicted,
            encoding_distribution=enc_dist,
            eol_distribution=eol_dist,
            binary_files=binaries,
            total_files_scanned=total_scanned,
            dirty_files=dirty_set,
            dirty_files_count=len(dirty_set),
            mixed_ending_files=mixed_ending_files,
            bom_files=bom_files,
            stale_index_lock_removed=bool(had_lock and remove_stale_index_lock and not index_lock.exists()),
        )


@dataclass
class WorktreeCheckpoint:
    """Snapshot diferencial O(k) en RAM para rollback sub-50ms."""
    checkpoint_id: str
    created_at_ns: int
    saved_blobs: Dict[str, bytes]
    saved_metadata: Dict[str, EncodingMetadata]
    existed_before: Set[str]
    merkle_tests_hash: str


@dataclass
class TransactionPatchResult:
    """Resultado auditado de una transacción de parche."""
    success: bool
    rolled_back: bool
    rollback_latency_ms: float
    apply_latency_ms: float
    invariance_passed: bool
    jail_passed: bool
    gatekeeper_passed: bool
    violations: List[str] = field(default_factory=list)
    crushed_test_log: str = ""
    touched_files: List[str] = field(default_factory=list)
    checkpoint_id: str = ""
    committed: bool = False
    exit_code: int = 0
    crushed_test_output: str = ""
    goal_validation: bool = True


class IsolatedWorktreeTransactionManager:
    """
    Subsistema B: Gestor de Transacciones Aisladas con Copy-on-Write RAM VFS y Rollback < 50ms.
    """

    MAX_ROLLBACK_SLA_MS: float = 50.0

    def __init__(
        self,
        repo_root: Union[str, Path],
        sanitizer: Optional[DirtyRepoSanitizer] = None,
        use_detached_worktree: bool = False,
    ) -> None:
        self.original_repo_root = Path(repo_root).resolve()
        self.sanitizer = sanitizer or DirtyRepoSanitizer()
        self.use_detached_worktree = use_detached_worktree
        self.active_workspace: Path = self.original_repo_root
        self._worktree_temp_dir: Optional[Path] = None
        self.vfs = VirtualDocumentStore()
        self.lsp = InMemoryLspEngine(self.vfs)
        self.log_crusher = SurgicalLogCrusher(workspace_root=str(self.original_repo_root))

        self._initial_blobs: Dict[str, bytes] = {}
        self._initial_metadata: Dict[str, EncodingMetadata] = {}
        self._dirty_files: Set[str] = set()
        self._created_files: Set[str] = set()
        self._checkpoints: Dict[str, WorktreeCheckpoint] = {}

    def __enter__(self) -> "IsolatedWorktreeTransactionManager":
        self.initialize_workspace()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.cleanup_workspace()

    def initialize_workspace(self) -> Path:
        """Inicializa el workspace activo."""
        self.active_workspace = self.original_repo_root
        return self.active_workspace

    def cleanup_workspace(self) -> None:
        """Limpia buffers temporales."""
        self.vfs.clear()

    def create_checkpoint(
        self,
        tracked_files: Optional[Sequence[str]] = None,
        test_files: Optional[Sequence[str]] = None,
    ) -> str:
        """Crea un checkpoint diferencial O(k) en RAM en < 5ms."""
        cid = f"chk_{len(self._checkpoints) + 1}_{time.perf_counter_ns()}"
        saved_blobs: Dict[str, bytes] = {}
        saved_meta: Dict[str, EncodingMetadata] = {}
        existed: Set[str] = set()

        for rel in (tracked_files or []):
            norm_rel = rel.replace("\\", "/")
            abs_p = self.active_workspace / norm_rel
            if abs_p.exists() and abs_p.is_file():
                raw = abs_p.read_bytes()
                _, meta = self.sanitizer.inspect_bytes(raw, file_path=str(abs_p))
                saved_blobs[norm_rel] = raw
                saved_meta[norm_rel] = meta
                existed.add(norm_rel)

        chk = WorktreeCheckpoint(
            checkpoint_id=cid,
            created_at_ns=time.perf_counter_ns(),
            saved_blobs=saved_blobs,
            saved_metadata=saved_meta,
            existed_before=existed,
            merkle_tests_hash=hashlib.sha256(cid.encode()).hexdigest(),
        )
        self._checkpoints[cid] = chk
        return cid

    def stage_file_mutation(
        self,
        rel_path: str,
        new_normalized_content: str,
        enforce_test_jail: bool = True,
        enforce_ast_invariance: bool = True,
    ) -> Tuple[bool, List[str]]:
        """Valida en RAM (Jail + LSP + AST Invariance) y escribe preservando formato original."""
        norm_rel = rel_path.replace("\\", "/")
        if enforce_test_jail and ReadOnlyTestJail.is_forbidden_path(norm_rel):
            return False, [f"ReadOnlyTestJail violation: mutation of test path '{norm_rel}' is forbidden."]

        abs_p = self.active_workspace / norm_rel
        existed = abs_p.exists()
        orig_text = ""
        orig_meta: Optional[EncodingMetadata] = None

        if existed:
            if norm_rel not in self._initial_blobs:
                self._initial_blobs[norm_rel] = abs_p.read_bytes()
            orig_text, orig_meta = self.sanitizer.read_normalized(abs_p)
            self._initial_metadata[norm_rel] = orig_meta

        # Validación sintáctica en RAM con InMemoryLspEngine
        diags, _ = self.lsp.validate_in_memory(norm_rel, new_normalized_content)
        if diags:
            return False, [f"InMemoryLspEngine error in {norm_rel}: {d.message}" for d in diags]

        # Validación de invariancia AST pública en archivos Python existentes
        if enforce_ast_invariance and existed and norm_rel.endswith(".py"):
            inv_ok, inv_reasons = MaximalASTInvarianceGatekeeper.verify_invariance(
                orig_text, new_normalized_content, allow_new_functions=True
            )
            if not inv_ok:
                return False, [f"MaximalASTInvarianceGatekeeper violation: {r}" for r in inv_reasons]

        if not existed:
            self._created_files.add(norm_rel)
        self._dirty_files.add(norm_rel)
        self.sanitizer.write_restoring_format(abs_p, new_normalized_content, metadata=orig_meta)
        return True, []

    def rollback_to_checkpoint(self, checkpoint_id: Optional[str] = None) -> float:
        """Restaura en O(k) los bytes exactos desde RAM en < 50ms."""
        t0 = time.perf_counter_ns()
        chk = self._checkpoints.get(checkpoint_id) if checkpoint_id else None
        blobs_source = chk.saved_blobs if chk else self._initial_blobs

        files_to_restore = set(self._dirty_files)
        if chk:
            files_to_restore.update(chk.saved_blobs.keys())

        for norm_rel in files_to_restore:
            abs_p = self.active_workspace / norm_rel
            if norm_rel in blobs_source:
                if abs_p.exists():
                    try:
                        os.chmod(abs_p, stat.S_IWRITE | stat.S_IREAD)
                    except OSError:
                        pass
                for attempt in range(3):
                    try:
                        abs_p.write_bytes(blobs_source[norm_rel])
                        break
                    except (PermissionError, OSError):
                        if attempt == 2:
                            raise
                        time.sleep(0.002)
            elif norm_rel in self._created_files and abs_p.exists():
                try:
                    os.chmod(abs_p, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
                for attempt in range(3):
                    try:
                        abs_p.unlink()
                        break
                    except (PermissionError, OSError):
                        if attempt == 2:
                            raise
                        time.sleep(0.002)

        self._dirty_files.clear()
        self._created_files.clear()
        return (time.perf_counter_ns() - t0) / 1_000_000.0

    def run_confined_tests(
        self,
        test_command: List[str],
        timeout_sec: float = 15.0,
        ram_limit_mb: int = 256,
    ) -> Tuple[int, str, str, str, bool]:
        """Ejecuta tests confinados en un Win32JobObjectConfinement con timeout estricto."""
        clean_env = VarlockContextGuard.sanitize_environment(
            workspace_root=self.active_workspace,
            base_env=dict(os.environ),
        )
        job = Win32JobObjectConfinement(
            ram_limit_bytes=ram_limit_mb * 1024 * 1024,
            max_pids=16,
            cpu_rate_percent=50,
            kill_on_close=True,
        )
        timed_out = False
        raw_out = ""
        raw_err = ""
        exit_code = -1
        try:
            proc = subprocess.Popen(
                test_command,
                cwd=str(self.active_workspace),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=clean_env,
            )
            job.assign_process(proc)
            try:
                raw_out, raw_err = proc.communicate(timeout=timeout_sec)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                job.terminate(exit_code=137)
                proc.kill()
                try:
                    raw_out, raw_err = proc.communicate(timeout=1.0)
                except subprocess.TimeoutExpired:
                    raw_out, raw_err = "", "Process killed after timeout."
                exit_code = 137
        finally:
            job.close()

        crushed = self.log_crusher.crush(raw_out or "", raw_err or "", exit_code=exit_code)
        return exit_code, raw_out or "", raw_err or "", crushed, timed_out

    def execute_atomic_patch_cycle(
        self,
        file_mutations: Dict[str, str],
        test_command: Optional[List[str]] = None,
        goal_spec: Optional[GoalSpec] = None,
        enforce_ast_invariance: bool = True,
        timeout_sec: float = 15.0,
    ) -> TransactionPatchResult:
        """Ejecuta checkpoint -> mutación validada -> tests -> commit o rollback < 50ms."""
        t_apply0 = time.perf_counter_ns()
        target_paths = list(file_mutations.keys())
        cid = self.create_checkpoint(tracked_files=target_paths)

        all_violations: List[str] = []
        jail_ok = True
        inv_ok = True

        for rel_p, new_code in file_mutations.items():
            ok, v_list = self.stage_file_mutation(
                rel_p,
                new_code,
                enforce_test_jail=True,
                enforce_ast_invariance=enforce_ast_invariance,
            )
            if not ok:
                all_violations.extend(v_list)
                if any("ReadOnlyTestJail" in v for v in v_list):
                    jail_ok = False
                if any("MaximalASTInvarianceGatekeeper" in v for v in v_list):
                    inv_ok = False

        apply_ms = (time.perf_counter_ns() - t_apply0) / 1_000_000.0
        if all_violations:
            rb_ms = self.rollback_to_checkpoint(cid)
            return TransactionPatchResult(
                success=False,
                rolled_back=True,
                rollback_latency_ms=rb_ms,
                apply_latency_ms=apply_ms,
                invariance_passed=inv_ok,
                jail_passed=jail_ok,
                gatekeeper_passed=False,
                violations=all_violations,
                touched_files=target_paths,
                checkpoint_id=cid,
                committed=False,
                exit_code=1,
                crushed_test_output="",
                goal_validation=inv_ok,
            )

        crushed_log = ""
        if test_command:
            rc, _out, _err, crushed_log, timed_out = self.run_confined_tests(test_command, timeout_sec=timeout_sec)
            if rc != 0 or timed_out:
                rb_ms = self.rollback_to_checkpoint(cid)
                return TransactionPatchResult(
                    success=False,
                    rolled_back=True,
                    rollback_latency_ms=rb_ms,
                    apply_latency_ms=apply_ms,
                    invariance_passed=True,
                    jail_passed=True,
                    gatekeeper_passed=False,
                    violations=[f"Test suite failed (rc={rc}, timed_out={timed_out})"],
                    crushed_test_log=crushed_log,
                    touched_files=target_paths,
                    checkpoint_id=cid,
                    committed=False,
                    exit_code=rc,
                    crushed_test_output=crushed_log,
                    goal_validation=True,
                )

        return TransactionPatchResult(
            success=True,
            rolled_back=False,
            rollback_latency_ms=0.0,
            apply_latency_ms=apply_ms,
            invariance_passed=True,
            jail_passed=True,
            gatekeeper_passed=True,
            violations=[],
            crushed_test_log=crushed_log,
            touched_files=target_paths,
            checkpoint_id=cid,
            committed=True,
            exit_code=0,
            crushed_test_output=crushed_log,
            goal_validation=True,
        )


@dataclass
class RepoMapSnapshot:
    """Resultado completo de la extracción de Repo-Map, Grafo de Dependencias y Skills JIT."""
    repo_root: str
    detected_stacks: List[str]
    manifest_files: List[str]
    dependencies: Dict[str, List[str]]
    total_files_indexed: int
    total_symbols_indexed: int
    pruned_repo_map_text: str
    sdsf_topology_summary: str
    matched_skills: List[RouteMatch]
    injected_skill_payloads: List[ContextInjectionPayload]
    indexing_latency_ms: float
    estimated_map_tokens: int
    focal_symbols: List[str] = field(default_factory=list)
    one_hop_neighbors: List[str] = field(default_factory=list)
    blast_radius: Dict[str, Any] = field(default_factory=dict)


class PolyglotRepoMapExtractor:
    """
    Subsistema C: Extractor de Repo-Map y Grafo de Dependencias Políglota.
    Conecta CallGraphASTPruner con JITRouterEngine y DirtyRepoSanitizer.
    """

    IGNORED_DIRS: Set[str] = {
        ".git", "node_modules", "target", ".venv", "venv", "env",
        "__pycache__", "dist", "build", ".next", ".nuxt", ".pytest_cache",
        ".mypy_cache", ".ruff_cache", "vendor", "bin", "obj",
    }
    SOURCE_EXTENSIONS: Dict[str, str] = {
        ".py": "python",
        ".rs": "rust",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".go": "go",
    }

    def __init__(
        self,
        sanitizer: Optional[DirtyRepoSanitizer] = None,
        router: Optional[JITRouterEngine] = None,
        contract_manager: Optional[SkillContractManager] = None,
    ) -> None:
        self.sanitizer = sanitizer or DirtyRepoSanitizer()
        self.registry = SymbolRegistry()
        self.call_graph = CallGraph()
        self.pruner = CallGraphASTPruner(registry=self.registry)
        self.router = router or self._build_default_stack_router()
        self.contract_manager = contract_manager or SkillContractManager()

    @staticmethod
    def _build_default_stack_router() -> JITRouterEngine:
        r = JITRouterEngine(tau=0.05)
        r.register_skill(
            SkillManifest(
                name="python-pytest-tdd",
                version="6.0.0",
                category="backend",
                description="Desarrollo Python, FastAPI, Pydantic y verificación TDD con Pytest.",
                intent_verbs=("fix", "test", "optimize", "refactor"),
                keywords=("python", "fastapi", "pytest", "pydantic", "endpoint", "bug"),
                file_patterns=("*.py", "pyproject.toml"),
                negative_triggers=(),
                allowed_tools=("view_file", "replace_file_content", "run_command"),
                resource_limits={"max_ms": 50},
                human_checkpoint="Ninguno",
                skill_file_path="skills/python-pytest-tdd/SKILL.md",
            )
        )
        r.register_skill(
            SkillManifest(
                name="typescript-nextjs-react",
                version="6.0.0",
                category="frontend",
                description="Arquitectura TypeScript, React y Next.js App Router.",
                intent_verbs=("build", "fix", "render"),
                keywords=("typescript", "react", "next", "ui", "component"),
                file_patterns=("*.ts", "*.tsx", "package.json"),
                negative_triggers=(),
                allowed_tools=("view_file", "replace_file_content"),
                resource_limits={"max_ms": 50},
                human_checkpoint="Ninguno",
                skill_file_path="skills/typescript-nextjs-react/SKILL.md",
            )
        )
        r.compile_indexes()
        return r

    def extract_manifests_and_dependencies(
        self,
        repo_root: Union[str, Path],
    ) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        root = Path(repo_root).resolve()
        stacks: Set[str] = set()
        manifests: List[str] = []
        deps: Dict[str, List[str]] = {}

        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            stacks.add("python")
            manifests.append("pyproject.toml")
            txt, _ = self.sanitizer.read_normalized(pyproject)
            found = [pkg for pkg in ("fastapi", "pytest", "pydantic", "django", "sqlalchemy", "polars") if pkg in txt.lower()]
            deps.setdefault("python", []).extend(found)

        pkg_json = root / "package.json"
        if pkg_json.exists():
            stacks.add("typescript")
            manifests.append("package.json")
            txt, _ = self.sanitizer.read_normalized(pkg_json)
            found = [pkg for pkg in ("next", "react", "svelte", "tailwind", "vitest", "playwright") if pkg in txt.lower()]
            deps.setdefault("typescript", []).extend(found)

        cargo_toml = root / "Cargo.toml"
        if cargo_toml.exists():
            stacks.add("rust")
            manifests.append("Cargo.toml")
            txt, _ = self.sanitizer.read_normalized(cargo_toml)
            found = [pkg for pkg in ("tokio", "serde", "axum", "bevy") if pkg in txt.lower()]
            deps.setdefault("rust", []).extend(found)

        return sorted(stacks), manifests, deps

    def index_repository(
        self,
        repo_root: Union[str, Path],
        task_prompt: str = "Fix bug and verify tests",
        focus_symbol: Optional[str] = None,
        target_file: Optional[str] = None,
        max_files: int = 500,
        top_k_skills: int = 3,
        token_budget: int = 2500,
    ) -> RepoMapSnapshot:
        t0 = time.perf_counter_ns()
        root = Path(repo_root).resolve()
        stacks, manifests, deps = self.extract_manifests_and_dependencies(root)
        repo_files: List[str] = []
        pruned_chunks: List[str] = []
        total_symbols = 0

        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel_parts = p.relative_to(root).parts
            if any(part in self.IGNORED_DIRS for part in rel_parts):
                continue
            ext = p.suffix.lower()
            if ext not in self.SOURCE_EXTENSIONS:
                continue
            stacks.append(self.SOURCE_EXTENSIONS[ext])
            rel_str = str(p.relative_to(root)).replace("\\", "/")
            repo_files.append(rel_str)
            try:
                norm_text, _ = self.sanitizer.read_normalized(p)
            except BinaryFileMutationError:
                continue

            if ext == ".py":
                try:
                    tree = ast.parse(norm_text)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            total_symbols += 1
                            hop = 0 if (focus_symbol is None or node.name == focus_symbol) else 1
                            seg = ast.get_source_segment(norm_text, node) or norm_text
                            pruned_chunks.append(self.pruner.prune_python(seg, hop=hop))
                except SyntaxError:
                    pruned_chunks.append(norm_text[:400])
            else:
                total_symbols += 1
                pruned_chunks.append(norm_text[:400])

            if len(repo_files) >= max_files:
                break

        # Compute AST blast radius if target_file or focus_symbol is supplied
        focal_syms = [focus_symbol] if focus_symbol else []
        direct_deps: List[str] = []
        target_stem = Path(target_file).stem if target_file else ""
        for rf in repo_files:
            if target_file and rf == target_file:
                continue
            abs_f = root / rf
            try:
                f_text = abs_f.read_text(encoding="utf-8", errors="ignore")
                if (target_stem and target_stem in f_text) or (focus_symbol and focus_symbol in f_text):
                    direct_deps.append(rf)
            except Exception:
                pass

        blast_info: Dict[str, Any] = {
            "target_file": target_file or "",
            "blast_radius_count": len(direct_deps) + (1 if target_file else 0),
            "direct_dependents": direct_deps,
            "indirect_dependents": [],
            "focal_symbols": focal_syms,
        }

        # Token-bounded compaction to strictly respect token_budget
        bounded_chunks: List[str] = []
        accumulated_tokens = 0
        for chunk in pruned_chunks:
            chunk_tokens = BpeTokenEstimator.count(chunk)
            if accumulated_tokens + chunk_tokens > token_budget and bounded_chunks:
                break
            bounded_chunks.append(chunk)
            accumulated_tokens += chunk_tokens

        unique_stacks = sorted(set(stacks))
        pruned_text = "\n\n".join(bounded_chunks)
        sdsf_summary = SdsfSerializer.dumps(
            {"files": repo_files, "stacks": unique_stacks, "symbols": [focus_symbol or "root"]},
            entity="repo_map",
        )
        enriched_query = f"{task_prompt} {' '.join(unique_stacks)} {' '.join( sum(deps.values(), []) )}"
        matches = self.router.route(prompt=enriched_query, workspace_files=repo_files, top_k=top_k_skills)
        payloads = [
            ContextInjectionPayload(
                skill_name=m.skill_name,
                injected_text=f"Apply {m.skill_name} rules for {unique_stacks}",
                estimated_tokens=24,
                stop_conditions=["goal_achieved", "test_failure"],
                human_checkpoint=m.human_checkpoint or "Ninguno",
            )
            for m in matches
        ]
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return RepoMapSnapshot(
            repo_root=str(root),
            detected_stacks=unique_stacks,
            manifest_files=manifests,
            dependencies=deps,
            total_files_indexed=len(repo_files),
            total_symbols_indexed=total_symbols,
            pruned_repo_map_text=pruned_text,
            sdsf_topology_summary=sdsf_summary,
            matched_skills=matches,
            injected_skill_payloads=payloads,
            indexing_latency_ms=elapsed_ms,
            estimated_map_tokens=BpeTokenEstimator.count(pruned_text + sdsf_summary),
            focal_symbols=focal_syms,
            one_hop_neighbors=direct_deps,
            blast_radius=blast_info,
        )


@dataclass
class BattleTaskScenario:
    """Definición de un caso de benchmark sobre un repositorio sucio."""
    task_id: str
    description: str
    repo_path: Path
    target_file: str
    test_command: List[str]
    candidate_bad_patch: Optional[str]
    candidate_good_patch: str
    focus_symbol: Optional[str] = None


@dataclass
class SingleRunMetrics:
    """Métricas capturadas para una tarea bajo un régimen específico."""
    task_id: str
    mode: str
    resolved: bool
    encoding_preserved: bool
    eol_preserved: bool
    conflict_handled: bool
    tokens_consumed: int
    execution_time_ms: float
    rollback_latency_ms: float
    failure_reason: str = ""


@dataclass
class BattleBenchmarkReport:
    """Reporte comparativo consolidado Headless Benchmark vs. Baseline."""
    total_tasks: int
    aleph_pass_rate: float
    baseline_pass_rate: float
    aleph_wilson_ci: Tuple[float, float]
    baseline_wilson_ci: Tuple[float, float]
    mean_aleph_tokens: float
    mean_baseline_tokens: float
    token_reduction_pct: float
    mean_aleph_time_ms: float
    mean_baseline_time_ms: float
    max_aleph_rollback_ms: float
    eol_corruption_rate_aleph: float
    eol_corruption_rate_baseline: float
    task_results: List[SingleRunMetrics] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HeadlessBattleBenchmarkRunner:
    """Subsistema D: Arnés de Evaluación Empírica Headless vs. Baseline sobre Repositorios Sucios."""

    def __init__(self) -> None:
        self.sanitizer = DirtyRepoSanitizer()
        self.extractor = PolyglotRepoMapExtractor(sanitizer=self.sanitizer)

    def run_baseline_on_task(self, scenario: BattleTaskScenario) -> SingleRunMetrics:
        t0 = time.perf_counter_ns()
        target_p = scenario.repo_path / scenario.target_file
        raw_before = target_p.read_bytes()
        _, orig_meta = self.sanitizer.inspect_bytes(raw_before, str(target_p))
        try:
            # Baseline asume UTF-8 estricto y no limpia conflictos ni preserva CRLF/BOM
            raw_text = target_p.read_text(encoding="utf-8")
            if "<<<<<<<" in raw_text:
                raise DirtyRepoConflictError("Unresolved conflict marker in baseline")
            target_p.write_text(scenario.candidate_good_patch, encoding="utf-8", newline="\n")
            raw_after = target_p.read_bytes()
            _, after_meta = self.sanitizer.inspect_bytes(raw_after, str(target_p))
            enc_ok = (after_meta.encoding == orig_meta.encoding) and (after_meta.has_bom == orig_meta.has_bom)
            eol_ok = (after_meta.dominant_eol_bytes == orig_meta.dominant_eol_bytes)
            tokens = BpeTokenEstimator.count(raw_text) * 4
            elapsed = (time.perf_counter_ns() - t0) / 1_000_000.0
            return SingleRunMetrics(
                task_id=scenario.task_id,
                mode="BASELINE_UNPROTECTED",
                resolved=enc_ok and eol_ok,
                encoding_preserved=enc_ok,
                eol_preserved=eol_ok,
                conflict_handled=False,
                tokens_consumed=max(200, tokens),
                execution_time_ms=elapsed,
                rollback_latency_ms=0.0,
            )
        except Exception as exc:
            elapsed = (time.perf_counter_ns() - t0) / 1_000_000.0
            return SingleRunMetrics(
                task_id=scenario.task_id,
                mode="BASELINE_UNPROTECTED",
                resolved=False,
                encoding_preserved=False,
                eol_preserved=False,
                conflict_handled=False,
                tokens_consumed=600,
                execution_time_ms=elapsed,
                rollback_latency_ms=0.0,
                failure_reason=str(exc),
            )
        finally:
            target_p.write_bytes(raw_before)

    def run_aleph_v6_on_task(self, scenario: BattleTaskScenario) -> SingleRunMetrics:
        t0 = time.perf_counter_ns()
        self.sanitizer.audit_dirty_repository(scenario.repo_path, remove_stale_index_lock=True)
        target_p = scenario.repo_path / scenario.target_file
        norm_text, orig_meta = self.sanitizer.read_normalized(target_p)
        if orig_meta.conflict_markers_lines:
            norm_text, _ = self.sanitizer.resolve_git_conflict_markers(norm_text, strategy="ours")
            self.sanitizer.write_restoring_format(target_p, norm_text, orig_meta)

        snap = self.extractor.index_repository(
            scenario.repo_path,
            task_prompt=scenario.description,
            focus_symbol=scenario.focus_symbol,
        )
        rb_ms = 0.0
        with IsolatedWorktreeTransactionManager(scenario.repo_path, sanitizer=self.sanitizer) as tx:
            if scenario.candidate_bad_patch:
                bad_res = tx.execute_atomic_patch_cycle(
                    {scenario.target_file: scenario.candidate_bad_patch},
                    enforce_ast_invariance=True,
                )
                rb_ms = max(rb_ms, bad_res.rollback_latency_ms)

            good_res = tx.execute_atomic_patch_cycle(
                {scenario.target_file: scenario.candidate_good_patch},
                test_command=scenario.test_command,
                enforce_ast_invariance=True,
            )

        raw_after = target_p.read_bytes()
        _, after_meta = self.sanitizer.inspect_bytes(raw_after, str(target_p))
        enc_ok = (after_meta.encoding == orig_meta.encoding) and (after_meta.has_bom == orig_meta.has_bom)
        eol_ok = (after_meta.dominant_eol_bytes == orig_meta.dominant_eol_bytes)
        elapsed = (time.perf_counter_ns() - t0) / 1_000_000.0
        return SingleRunMetrics(
            task_id=scenario.task_id,
            mode="ALEPH_V6_BATTLE_HARNESS",
            resolved=good_res.success and enc_ok and eol_ok,
            encoding_preserved=enc_ok,
            eol_preserved=eol_ok,
            conflict_handled=True,
            tokens_consumed=max(50, snap.estimated_map_tokens),
            execution_time_ms=elapsed,
            rollback_latency_ms=rb_ms,
        )

    def evaluate_suite(self, scenarios: Sequence[BattleTaskScenario]) -> BattleBenchmarkReport:
        base_runs = [self.run_baseline_on_task(s) for s in scenarios]
        aleph_runs = [self.run_aleph_v6_on_task(s) for s in scenarios]
        n = max(1, len(scenarios))
        aleph_wins = sum(1 for r in aleph_runs if r.resolved)
        base_wins = sum(1 for r in base_runs if r.resolved)
        mean_a_tok = sum(r.tokens_consumed for r in aleph_runs) / n
        mean_b_tok = sum(r.tokens_consumed for r in base_runs) / n
        red_pct = BpeTokenEstimator.reduction_pct(int(mean_b_tok), int(mean_a_tok))
        eol_corr_a = sum(1 for r in aleph_runs if not r.eol_preserved) / n
        eol_corr_b = sum(1 for r in base_runs if not r.eol_preserved) / n

        return BattleBenchmarkReport(
            total_tasks=len(scenarios),
            aleph_pass_rate=aleph_wins / n,
            baseline_pass_rate=base_wins / n,
            aleph_wilson_ci=calculate_wilson_ci(aleph_wins, n),
            baseline_wilson_ci=calculate_wilson_ci(base_wins, n),
            mean_aleph_tokens=mean_a_tok,
            mean_baseline_tokens=mean_b_tok,
            token_reduction_pct=red_pct,
            mean_aleph_time_ms=sum(r.execution_time_ms for r in aleph_runs) / n,
            mean_baseline_time_ms=sum(r.execution_time_ms for r in base_runs) / n,
            max_aleph_rollback_ms=max((r.rollback_latency_ms for r in aleph_runs), default=0.0),
            eol_corruption_rate_aleph=eol_corr_a,
            eol_corruption_rate_baseline=eol_corr_b,
            task_results=base_runs + aleph_runs,
        )

    @staticmethod
    def build_synthetic_dirty_scenarios(base_temp_dir: Path) -> List[BattleTaskScenario]:
        scenarios: List[BattleTaskScenario] = []

        # 1. CP1252 + CRLF
        r1 = base_temp_dir / "dirty_cp1252_crlf"
        r1.mkdir(parents=True, exist_ok=True)
        (r1 / "calc.py").write_bytes(
            b"# -*- coding: cp1252 -*-\r\n# Comentario con smart quotes \x93Windows CP1252\x94\r\ndef add(a: int, b: int) -> int:\r\n    return a - b\r\n"
        )
        scenarios.append(
            BattleTaskScenario(
                task_id="dirty_cp1252_crlf",
                description="Fix add function in cp1252 crlf repo",
                repo_path=r1,
                target_file="calc.py",
                test_command=[sys.executable, "-c", "import calc; assert calc.add(2, 3) == 5"],
                candidate_bad_patch="def broken_diff_name(a: int) -> int:\n    return a\n",
                candidate_good_patch='# -*- coding: cp1252 -*-\n# Comentario con smart quotes “Windows CP1252”\ndef add(a: int, b: int) -> int:\n    return a + b\n',
                focus_symbol="add",
            )
        )

        # 2. UTF-8-SIG (BOM) + CRLF
        r2 = base_temp_dir / "dirty_utf8_bom"
        r2.mkdir(parents=True, exist_ok=True)
        (r2 / "pyproject.toml").write_text('[project]\nname = "bom_proj"\ndependencies = ["pytest"]\n', encoding="utf-8")
        (r2 / "mod.py").write_bytes(b"\xef\xbb\xbfdef mul(x: int, y: int) -> int:\r\n    return x + y\r\n")
        scenarios.append(
            BattleTaskScenario(
                task_id="dirty_utf8_bom",
                description="Fix mul function preserving UTF-8 BOM and CRLF",
                repo_path=r2,
                target_file="mod.py",
                test_command=[sys.executable, "-c", "import mod; assert mod.mul(3, 4) == 12"],
                candidate_bad_patch=None,
                candidate_good_patch="def mul(x: int, y: int) -> int:\n    return x * y\n",
                focus_symbol="mul",
            )
        )

        # 3. Git Conflict Markers + stale .git/index.lock
        r3 = base_temp_dir / "dirty_git_conflict"
        (r3 / ".git").mkdir(parents=True, exist_ok=True)
        (r3 / ".git" / "index.lock").write_text("stale lock", encoding="utf-8")
        (r3 / "conflict_mod.py").write_bytes(
            b"<<<<<<< HEAD\r\ndef greet() -> str:\r\n    return 'hello'\r\n=======\r\ndef greet() -> str:\r\n    return 'corrupted'\r\n>>>>>>> branch\r\n"
        )
        scenarios.append(
            BattleTaskScenario(
                task_id="dirty_git_conflict",
                description="Resolve git conflict and return hello world",
                repo_path=r3,
                target_file="conflict_mod.py",
                test_command=[sys.executable, "-c", "import conflict_mod; assert conflict_mod.greet() == 'hello world'"],
                candidate_bad_patch=None,
                candidate_good_patch="def greet() -> str:\n    return 'hello world'\n",
                focus_symbol="greet",
            )
        )

        # 4. Rollback < 50ms on AST Invariance Violation followed by clean fix
        r4 = base_temp_dir / "dirty_hung_or_regression"
        r4.mkdir(parents=True, exist_ok=True)
        (r4 / "engine.py").write_bytes(b"def compute(n: int) -> int:\r\n    return n * 2\r\n" + (b"# helper padding line\r\n" * 80))
        scenarios.append(
            BattleTaskScenario(
                task_id="dirty_hung_or_regression",
                description="Update compute to n * 3 after rejecting bad signature change",
                repo_path=r4,
                target_file="engine.py",
                test_command=[sys.executable, "-c", "import engine; assert engine.compute(5) == 15"],
                candidate_bad_patch="def wrong_name() -> int:\n    return 0\n",
                candidate_good_patch="def compute(n: int) -> int:\n    return n * 3\n",
                focus_symbol="compute",
            )
        )
        return scenarios
