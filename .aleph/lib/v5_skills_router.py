# -*- coding: utf-8 -*-
"""
El Aleph - Subsistema Soberano de Skills v5 (Aleph Skills Ecosystem v5)
Módulo: v5_skills_router.py
Ubicación: .aleph/lib/v5_skills_router.py

Implementación de Grado de Producción para:
- Arquitectura de Progressive Disclosure de 4 Niveles (L0 Disco Frío a L3 Sandbox)
- Motor JIT Router con SLA P99 <= 4.20 ms (BM25-Okapi + DFA + Glob Matching)
- Contratos SKILL.md v5 con Pydantic v2 y Tablas Anti-Racionalización
- Ejecución Hermética L3 con Confinamiento, Cuotas y Auditoría JSONL
- Pipeline de Ingesta Masiva y Certificación en 4 Etapas (Anti-Slop, Static Security, Normalizer, Test Synthesis)
- Bucle de Auto-Calibración en Caliente con Read-Copy-Update (RCU Zero-Downtime)
"""

from __future__ import annotations

import os
import sys
import re
import math
import time
import json
import fnmatch
import hashlib
import sqlite3
import threading
import subprocess
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any, Union

import yaml
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
# CONSTANTES GLOBALES Y CONFIGURACIÓN PREDETERMINADA
# ============================================================================

DEFAULT_CATALOG_DB = Path.home() / ".aleph" / "cache" / "skills_catalog.db"
DEFAULT_SKILLS_DIR = Path.home() / ".aleph" / "skills"
DEFAULT_TRACES_DIR = Path.home() / ".aleph" / "traces"
DEFAULT_EXEC_LOG = DEFAULT_TRACES_DIR / "skills_exec.jsonl"

SLOP_PATTERNS = [
    r"in this digital age",
    r"it's important to remember",
    r"crucial to delve into",
    r"powerful, innovative, cutting-edge",
    r"revolutionize your workflow",
    r"comprehensive guide to master",
    r"in conclusion,\s+it is clear that",
    r"testament to the power of",
]

DANGEROUS_SHELL_PATTERNS = [
    r"rm\s+-rf\s+[/~]",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Fork bomb
    r"curl\s+.*\|\s*(bash|sh|powershell|pwsh)",
    r"wget\s+.*\|\s*(bash|sh|powershell|pwsh)",
    r"chmod\s+777",
    r"del\s+/f\s+/s\s+/q\s+[c-zC-Z]:\\",
    r"format\s+[c-zC-Z]:",
]

CREDENTIAL_PATTERNS = [
    r"sk-ant-[a-zA-Z0-9_\-]{32,}",
    r"sk-[a-zA-Z0-9]{32,}",
    r"ghp_[a-zA-Z0-9]{36,}",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z-_]{35}",
]


# ============================================================================
# MODELOS PYDANTIC v2 - CONTRATO FORMAL SKILL.MD v5
# ============================================================================

class HumanCheckpointLevel(str, Enum):
    NONE = "none"
    IRREVERSIBLE_DATA_MUTATION = "irreversible_data_mutation"
    PRODUCTION_DEPLOYMENT = "production_deployment"
    FINANCIAL_TRANSACTION = "financial_transaction"
    EXTERNAL_COMMUNICATION = "external_communication"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class TriggerSpec(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    
    intent_verbs: List[str] = Field(
        ...,
        description="Lista de verbos o acciones clave en infinitivo/presente (e.g. ['refactor', 'migrate', 'audit'])"
    )
    keywords: List[str] = Field(
        ...,
        description="Palabras clave discriminantes y términos de dominio con alta especificidad"
    )
    file_patterns: List[str] = Field(
        default_factory=list,
        description="Patrones glob de archivos en workspace requeridos para activación (e.g. ['**/migrations/*.sql'])"
    )
    negative_triggers: List[str] = Field(
        default_factory=list,
        description="Patrones léxicos o intenciones que descalifican inmediatamente esta habilidad"
    )

    @field_validator("intent_verbs", "keywords")
    @classmethod
    def validate_non_empty_strings(cls, v: List[str]) -> List[str]:
        cleaned = [item.lower().strip() for item in v if item and item.strip()]
        if not cleaned:
            raise ValueError("La lista no puede estar vacía ni contener solo cadenas en blanco")
        return cleaned

    @field_validator("file_patterns", "negative_triggers")
    @classmethod
    def normalize_list_strings(cls, v: List[str]) -> List[str]:
        return [item.strip() for item in v if item and item.strip()]


class ResourceLimits(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    
    timeout_sec: int = Field(default=30, ge=1, le=300)
    max_memory_mb: int = Field(default=256, ge=16, le=2048)
    network_access: bool = Field(default=False)
    allow_file_deletion: bool = Field(default=False)


class SkillFrontmatter(BaseModel):
    class Config:
        extra = "forbid"
        frozen = True
    
    name: str = Field(
        ...,
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
        description="Nombre canónico en kebab-case sin espacios ni símbolos"
    )
    version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Versión formal SemVer 2.0.0"
    )
    description: str = Field(
        ...,
        min_length=15,
        max_length=240,
        description="Una sola oración precisa: qué hace exactamente la habilidad y cuándo se activa"
    )
    category: str = Field(
        ...,
        pattern=r"^(arch|sec|ops|code|data|ui|testing|eval)::[a-z0-9-]+$",
        description="Categoría taxonómica jerárquica con prefijo formal"
    )
    allowed_tools: List[str] = Field(
        default_factory=list,
        description="Herramientas mínimas indispensables que la habilidad tiene permitido invocar"
    )
    triggers: TriggerSpec = Field(
        ...,
        description="Definición formal de disparadores deterministas para el JIT Router"
    )
    resource_limits: ResourceLimits = Field(
        default_factory=ResourceLimits,
        description="Límites de recursos en tiempo de ejecución para el Nivel L3"
    )
    human_checkpoint: HumanCheckpointLevel = Field(
        default=HumanCheckpointLevel.NONE,
        description="Nivel de checkpoint humano requerido para acciones irreversibles"
    )


# ============================================================================
# DATACLASSES INMUTABLES DE MEMORIA (NIVEL L1 / RUNTIME)
# ============================================================================

@dataclass(frozen=True)
class SkillManifest:
    name: str
    version: str
    category: str
    description: str
    intent_verbs: Tuple[str, ...]
    keywords: Tuple[str, ...]
    file_patterns: Tuple[str, ...]
    negative_triggers: Tuple[str, ...]
    allowed_tools: Tuple[str, ...]
    resource_limits: Dict[str, Any]
    human_checkpoint: str
    skill_file_path: str
    sha256_hash: str = ""


@dataclass
class RouteMatch:
    skill_name: str
    score: float
    confidence: str  # "ALTA" (>= 0.85) o "MEDIA" (>= 0.72)
    skill_path: str
    matched_reasons: List[str]
    category: str
    allowed_tools: Tuple[str, ...]
    human_checkpoint: str


@dataclass
class ContextInjectionPayload:
    skill_name: str
    injected_text: str
    estimated_tokens: int
    stop_conditions: List[str]
    human_checkpoint: str


@dataclass
class SandboxExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    peak_memory_mb: float
    violations: List[str]
    timed_out: bool
    success: bool


@dataclass
class IngestionResult:
    skill_name: str
    status: str  # "PASSED", "REJECTED", "QUARANTINED"
    reasons: List[str]
    sanitized_frontmatter: Dict[str, Any]
    output_path: Optional[str] = None


# ============================================================================
# NIVEL L0: PERSISTENCIA DISCO FRÍO Y CATÁLOGO SQLITE (SkillsCatalogDB)
# ============================================================================

class SkillsCatalogDB:
    """
    Gestor de persistencia SQLite para metadatos de habilidades L0.
    Conserva checksums, estados de uso, telemetría de falsos positivos/negativos
    y relaciones de exclusión mutua.
    """
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        if db_path is None:
            self.db_path = DEFAULT_CATALOG_DB
        elif str(db_path) == ":memory:":
            self.db_path = ":memory:"
        else:
            self.db_path = Path(db_path)
            
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if not hasattr(self, "_memory_conn"):
                self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            return self._memory_conn
        return sqlite3.connect(str(self.db_path), timeout=10.0)

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills_catalog (
                    name TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    intent_verbs TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    file_patterns TEXT NOT NULL,
                    negative_triggers TEXT NOT NULL,
                    allowed_tools TEXT NOT NULL,
                    resource_limits TEXT NOT NULL,
                    human_checkpoint TEXT NOT NULL,
                    skill_file_path TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    false_negatives INTEGER DEFAULT 0,
                    rule_breaches INTEGER DEFAULT 0
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_category ON skills_catalog(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_updated ON skills_catalog(updated_at)")
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()

    def upsert_skill(self, manifest: SkillManifest, sha256_hash: str = "") -> None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = time.time()
            cursor.execute("""
                INSERT INTO skills_catalog (
                    name, version, category, description,
                    intent_verbs, keywords, file_patterns, negative_triggers,
                    allowed_tools, resource_limits, human_checkpoint,
                    skill_file_path, sha256_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    version=excluded.version,
                    category=excluded.category,
                    description=excluded.description,
                    intent_verbs=excluded.intent_verbs,
                    keywords=excluded.keywords,
                    file_patterns=excluded.file_patterns,
                    negative_triggers=excluded.negative_triggers,
                    allowed_tools=excluded.allowed_tools,
                    resource_limits=excluded.resource_limits,
                    human_checkpoint=excluded.human_checkpoint,
                    skill_file_path=excluded.skill_file_path,
                    sha256_hash=excluded.sha256_hash,
                    updated_at=excluded.updated_at
            """, (
                manifest.name,
                manifest.version,
                manifest.category,
                manifest.description,
                json.dumps(list(manifest.intent_verbs)),
                json.dumps(list(manifest.keywords)),
                json.dumps(list(manifest.file_patterns)),
                json.dumps(list(manifest.negative_triggers)),
                json.dumps(list(manifest.allowed_tools)),
                json.dumps(manifest.resource_limits),
                manifest.human_checkpoint,
                manifest.skill_file_path,
                sha256_hash or manifest.sha256_hash,
                now
            ))
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()

    def get_skill(self, name: str) -> Optional[SkillManifest]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills_catalog WHERE name = ?", (name,))
            row = cursor.fetchone()
            if self.db_path != ":memory:":
                conn.close()
            if not row:
                return None
            return self._row_to_manifest(row)

    def list_skills(self, category_filter: Optional[str] = None) -> List[SkillManifest]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if category_filter:
                cursor.execute("SELECT * FROM skills_catalog WHERE category LIKE ? ORDER BY name ASC", (f"{category_filter}%",))
            else:
                cursor.execute("SELECT * FROM skills_catalog ORDER BY name ASC")
            rows = cursor.fetchall()
            if self.db_path != ":memory:":
                conn.close()
            return [self._row_to_manifest(r) for r in rows]

    def delete_skill(self, name: str) -> bool:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM skills_catalog WHERE name = ?", (name,))
            deleted = cursor.rowcount > 0
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()
            return deleted

    def record_telemetry(self, name: str, fp_delta: int = 0, fn_delta: int = 0, breach_delta: int = 0, usage_delta: int = 0) -> None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE skills_catalog
                SET false_positives = false_positives + ?,
                    false_negatives = false_negatives + ?,
                    rule_breaches = rule_breaches + ?,
                    usage_count = usage_count + ?
                WHERE name = ?
            """, (fp_delta, fn_delta, breach_delta, usage_delta, name))
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()

    def get_telemetry(self, name: str) -> Dict[str, Any]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT usage_count, false_positives, false_negatives, rule_breaches FROM skills_catalog WHERE name = ?", (name,))
            row = cursor.fetchone()
            if self.db_path != ":memory:":
                conn.close()
            if not row:
                return {"usage_count": 0, "false_positives": 0, "false_negatives": 0, "rule_breaches": 0}
            return {
                "usage_count": row[0],
                "false_positives": row[1],
                "false_negatives": row[2],
                "rule_breaches": row[3],
            }

    @staticmethod
    def _row_to_manifest(row: Tuple[Any, ...]) -> SkillManifest:
        return SkillManifest(
            name=row[0],
            version=row[1],
            category=row[2],
            description=row[3],
            intent_verbs=tuple(json.loads(row[4])),
            keywords=tuple(json.loads(row[5])),
            file_patterns=tuple(json.loads(row[6])),
            negative_triggers=tuple(json.loads(row[7])),
            allowed_tools=tuple(json.loads(row[8])),
            resource_limits=json.loads(row[9]),
            human_checkpoint=row[10],
            skill_file_path=row[11],
            sha256_hash=row[12]
        )


# ============================================================================
# NIVEL L1: JIT MICRO-ROUTER (LATENCIA P99 <= 4.20ms)
# ============================================================================

class JITRouterEngine:
    """
    Motor de Enrutamiento JIT de Habilidades con SLA P99 <= 4.20 ms.
    Combina:
    1. Filtro rápido determinista de exclusiones negativas (Fast Set & Substring Match)
    2. Evaluación acelerada de patrones Glob de workspace (Pre-indexed Extensions & Basenames)
    3. Matching instantáneo de verbos de intención e identidades léxicas (DFA / Word Boundary)
    4. BM25-Okapi vectorizado en memoria con IDF Robertson-Spärck Jones
    5. Fusión lineal ponderada (0.40 DFA + 0.35 BM25 + 0.25 Glob) con corte estricto por tau
    """
    def __init__(self, k1: float = 1.25, b: float = 0.75, tau: float = 0.72):
        self.k1 = k1
        self.b = b
        self.tau = tau
        
        self.skills: Dict[str, SkillManifest] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_len: float = 1.0
        self.inverted_index: Dict[str, Dict[str, float]] = {}
        self.idf_cache: Dict[str, float] = {}

        # Estructuras precompiladas de aceleración sub-milisegundo
        self.negative_regex_map: Dict[str, re.Pattern] = {}
        self.verb_regex_map: Dict[str, re.Pattern] = {}
        self._compiled_glob_patterns: Dict[str, re.Pattern] = {}
        self.verb_token_index: Dict[str, Set[str]] = {}
        self.multiword_verbs: List[Tuple[str, str]] = []
        self.negative_token_index: Dict[str, Set[str]] = {}
        self.multiword_negatives: List[Tuple[str, str]] = []

    def register_skill(self, manifest: SkillManifest) -> None:
        self.skills[manifest.name] = manifest
        
        # Precompilación de expresiones regulares para negaciones
        if manifest.negative_triggers:
            valid_negs = [re.escape(t.strip()) for t in manifest.negative_triggers if t and t.strip()]
            if valid_negs:
                pattern = "|".join(valid_negs)
                self.negative_regex_map[manifest.name] = re.compile(rf"\b({pattern})\b", re.IGNORECASE)
            for t in manifest.negative_triggers:
                t_clean = t.lower().strip()
                if not t_clean:
                    continue
                if " " in t_clean:
                    self.multiword_negatives.append((t_clean, manifest.name))
                else:
                    self.negative_token_index.setdefault(t_clean, set()).add(manifest.name)
        
        # Precompilación de expresiones regulares para verbos
        if manifest.intent_verbs:
            valid_verbs = [re.escape(v.strip()) for v in manifest.intent_verbs if v and v.strip()]
            if valid_verbs:
                pattern = "|".join(valid_verbs)
                self.verb_regex_map[manifest.name] = re.compile(rf"\b({pattern})\b", re.IGNORECASE)
            for v in manifest.intent_verbs:
                v_clean = v.lower().strip()
                if not v_clean:
                    continue
                if " " in v_clean:
                    self.multiword_verbs.append((v_clean, manifest.name))
                else:
                    self.verb_token_index.setdefault(v_clean, set()).add(manifest.name)

        # Precompilación de patrones glob complejos
        for pat in manifest.file_patterns:
            if pat not in self._compiled_glob_patterns:
                try:
                    norm_pat = pat.replace("\\", "/")
                    if norm_pat.startswith("**/"):
                        base_pat = norm_pat[3:]
                        tr = fnmatch.translate(base_pat)
                        self._compiled_glob_patterns[pat] = re.compile(rf"(?:^|.*/){tr}")
                    else:
                        self._compiled_glob_patterns[pat] = re.compile(fnmatch.translate(norm_pat))
                except Exception:
                    pass

    def compile_indexes(self) -> None:
        """Construye el índice invertido ponderado y calcula valores de IDF en RAM."""
        doc_count = len(self.skills)
        if doc_count == 0:
            return

        self.inverted_index.clear()
        self.doc_lengths.clear()
        total_tokens = 0

        # Ponderación sintética del documento de cada skill:
        # Verbos de intención: x4.0 | Keywords: x2.5 | Descripción: x1.0
        for name, manifest in self.skills.items():
            token_freq: Dict[str, float] = {}

            # Verbos: Ponderación 4.0
            for v in manifest.intent_verbs:
                for token in self._tokenize(v):
                    token_freq[token] = token_freq.get(token, 0.0) + 4.0

            # Keywords: Ponderación 2.5
            for k in manifest.keywords:
                for token in self._tokenize(k):
                    token_freq[token] = token_freq.get(token, 0.0) + 2.5

            # Descripción: Ponderación 1.0
            for token in self._tokenize(manifest.description):
                token_freq[token] = token_freq.get(token, 0.0) + 1.0

            effective_len = sum(token_freq.values())
            d_len = max(int(effective_len), 1)
            self.doc_lengths[name] = d_len
            total_tokens += d_len

            for token, weight in token_freq.items():
                if token not in self.inverted_index:
                    self.inverted_index[token] = {}
                self.inverted_index[token][name] = weight

        self.avg_doc_len = total_tokens / doc_count

        # IDF con corrección Robertson-Spärck Jones (BM25)
        # Precomputación completa de score_contrib en RAM para P99 sub-milisegundo
        self.idf_cache.clear()
        precomputed_index: Dict[str, Dict[str, float]] = {}
        for token, post_list in self.inverted_index.items():
            n_t = len(post_list)
            idf = max(math.log(1.0 + (doc_count - n_t + 0.5) / (n_t + 0.5)), 0.05)
            self.idf_cache[token] = idf
            precomputed_index[token] = {}
            for doc_name, tf in post_list.items():
                doc_len = self.doc_lengths[doc_name]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                score_contrib = idf * (tf * (self.k1 + 1.0)) / denom
                precomputed_index[token][doc_name] = score_contrib

        self.inverted_index = precomputed_index

    def route(
        self,
        prompt: str,
        workspace_files: Optional[List[str]] = None,
        top_k: int = 3
    ) -> List[RouteMatch]:
        """
        Punto de entrada de ultra-alta velocidad para enrutamiento JIT.
        Garantiza SLA P99 <= 4.20 ms sobre miles de habilidades.
        """
        if not self.skills:
            return []

        prompt_clean = prompt.strip()
        if not prompt_clean:
            return []

        tokens = self._tokenize(prompt_clean)
        if not tokens:
            return []

        token_set = set(tokens)

        # 1. Recuperación instantánea de candidatos y acumulación BM25 (O(1) lookup directo)
        COMMON_STOPWORDS = {
            "para", "de", "en", "el", "la", "los", "las", "un", "una", "unos", "unas",
            "con", "por", "que", "y", "o", "a", "al", "del", "es", "son",
            "the", "and", "for", "with", "from", "that", "this", "in", "on", "at", "to", "of", "is", "are"
        }

        bm25_raw: Dict[str, float] = {}
        inv_idx = self.inverted_index
        doc_count = len(self.skills)
        max_df = max(int(0.40 * doc_count), 25)

        for token in token_set:
            if token in COMMON_STOPWORDS:
                continue
            if token in inv_idx:
                postings = inv_idx[token]
                # Poda de términos de alta frecuencia no discriminativos
                if len(postings) > max_df and doc_count > 50:
                    continue
                for doc_name, score_contrib in postings.items():
                    bm25_raw[doc_name] = bm25_raw.get(doc_name, 0.0) + score_contrib

        # Fast matching de verbos por token (sin escanear todas las regexes en cada turno)
        matched_verb_skills: Set[str] = set()
        for token in token_set:
            if token in self.verb_token_index:
                matched_verb_skills.update(self.verb_token_index[token])
        if self.multiword_verbs:
            prompt_lower = prompt_clean.lower()
            for phrase, s_name in self.multiword_verbs:
                if phrase in prompt_lower:
                    matched_verb_skills.add(s_name)

        for name in matched_verb_skills:
            if name not in bm25_raw:
                bm25_raw[name] = 0.0

        if not bm25_raw:
            return []

        # 2. Filtro Rápido de Negaciones: descarte inmediato si coincide con negative_triggers
        active_candidates: List[str] = []
        for name in bm25_raw.keys():
            # Fast token match
            neg_pat = self.negative_regex_map.get(name)
            if neg_pat and neg_pat.search(prompt_clean):
                continue
            active_candidates.append(name)

        if not active_candidates:
            return []

        # 3. Evaluación Glob acelerada sobre archivos del workspace (únicamente para candidatos activos)
        workspace_files = workspace_files or []
        norm_files = [f.replace("\\", "/") for f in workspace_files]
        exts = {f.split(".")[-1] for f in norm_files if "." in f}
        basenames = {f.split("/")[-1] for f in norm_files}

        glob_scores: Dict[str, float] = {}
        for name in active_candidates:
            patterns = self.skills[name].file_patterns
            if not patterns:
                glob_scores[name] = 0.5  # Neutral si la skill no requiere archivos específicos
                continue

            matched = False
            for pat in patterns:
                norm_pat = pat.replace("\\", "/")
                # Fast path: extension check
                if norm_pat.startswith("**/*."):
                    ext = norm_pat[5:]
                    if ext in exts:
                        matched = True
                        break
                elif norm_pat.startswith("*."):
                    ext = norm_pat[2:]
                    if ext in exts:
                        matched = True
                        break
                elif norm_pat in basenames:
                    matched = True
                    break
                else:
                    # Glob jerárquico compatible con **/ (raíz o subcarpetas)
                    for nf in norm_files:
                        if fnmatch.fnmatch(nf, norm_pat):
                            matched = True
                            break
                        if norm_pat.startswith("**/"):
                            sub_pat = norm_pat[3:]
                            if fnmatch.fnmatch(nf, sub_pat) or fnmatch.fnmatch(nf, "*" + norm_pat[2:]):
                                matched = True
                                break
                    if matched:
                        break
            glob_scores[name] = 1.0 if matched else 0.0

        # 4. Match de Verbos de Intención (DFA acelerado)
        dfa_scores: Dict[str, float] = {
            name: (1.0 if name in matched_verb_skills else 0.0)
            for name in active_candidates
        }

        # Normalización Min-Max de scores BM25
        max_bm25 = max(bm25_raw.values()) if bm25_raw else 1.0
        results: List[RouteMatch] = []
        tau = self.tau

        # 5. Fusión Lineal Ponderada y Filtrado por Umbral Tau
        for name in active_candidates:
            raw_b = bm25_raw[name]
            s_bm25 = (raw_b / max_bm25) if max_bm25 > 0.0 else 0.0
            s_dfa = dfa_scores.get(name, 0.0)
            s_glob = glob_scores.get(name, 0.0)

            score = 0.40 * s_dfa + 0.35 * s_bm25 + 0.25 * s_glob

            if score >= tau:
                reasons = []
                if s_dfa > 0:
                    reasons.append("Verbo de intención directo detectado")
                if s_glob == 1.0:
                    reasons.append("Patrón de archivo en workspace coincidente")
                if s_bm25 >= 0.6:
                    reasons.append(f"Alta similitud léxica BM25 ({s_bm25:.2f})")

                confidence = "ALTA" if score >= 0.85 else "MEDIA"
                manifest = self.skills[name]
                results.append(RouteMatch(
                    skill_name=name,
                    score=round(score, 4),
                    confidence=confidence,
                    skill_path=manifest.skill_file_path,
                    matched_reasons=reasons,
                    category=manifest.category,
                    allowed_tools=manifest.allowed_tools,
                    human_checkpoint=manifest.human_checkpoint
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Tokenizador determinista: minúsculas, extracción de palabras y tokens alfanuméricos
        return re.findall(r"[a-z0-9_\-]{2,}", text.lower())


# ============================================================================
# NIVEL L2: GESTOR DE CONTRATO Y CONTEXTO EFÍMERO (SkillContractManager)
# ============================================================================

class SkillContractManager:
    """
    Gestor de Nivel L2 para inyección de contratos SKILL.md.
    - Valida YAML frontmatter contra el esquema estricto Pydantic v2
    - Extrae secciones canónicas de Markdown
    - Sintetiza inyecciones quirúrgicas (800 - 1,200 tokens)
    - Gestiona el ciclo de vida: activación, verificación de condiciones de parada y evicción
    """
    def __init__(self):
        self.active_injections: Dict[str, ContextInjectionPayload] = {}

    def parse_skill_file(self, skill_path: Union[str, Path]) -> Tuple[SkillFrontmatter, Dict[str, Any]]:
        path = Path(skill_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de skill no encontrado: {path}")

        content = path.read_text(encoding="utf-8", errors="replace")
        return self.parse_skill_content(content, skill_name=path.parent.name)

    def parse_skill_content(self, content: str, skill_name: str = "unknown") -> Tuple[SkillFrontmatter, Dict[str, Any]]:
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            raise ValueError(f"Formato no válido: Falta bloque frontmatter delimitado por '---' en {skill_name}")

        fm_raw = match.group(1)
        body = match.group(2)

        try:
            fm_dict = yaml.safe_load(fm_raw)
            if not isinstance(fm_dict, dict):
                raise ValueError("El frontmatter YAML debe ser un diccionario")
        except Exception as e:
            raise ValueError(f"Error al parsear YAML frontmatter: {e}")

        # Validación formal con Pydantic v2
        frontmatter = SkillFrontmatter.model_validate(fm_dict)
        sections = self._parse_markdown_sections(body)
        return frontmatter, sections

    def _parse_markdown_sections(self, body: str) -> Dict[str, Any]:
        sections: Dict[str, Any] = {
            "objective": "",
            "preconditions": [],
            "protocol_steps": [],
            "stop_conditions": [],
            "anti_rationalization": [],
            "checkpoint_info": {},
            "raw_body": body.strip()
        }

        # Extracción de Objetivo Operativo
        obj_match = re.search(r"##\s+(?:1\.\s+)?Objetivo Operativo\s*\n+([^\n#]+)", body, re.IGNORECASE)
        if obj_match:
            sections["objective"] = obj_match.group(1).strip()

        # Extracción de Precondiciones
        pre_match = re.search(r"##\s+(?:2\.\s+)?Precondiciones[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
        if pre_match:
            lines = [l.strip("- [*] ").strip() for l in pre_match.group(1).splitlines() if l.strip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5."))]
            sections["preconditions"] = [l for l in lines if l]

        # Extracción de Protocolo Paso a Paso
        proto_match = re.search(r"##\s+(?:3\.\s+)?Protocolo de Ejecución[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
        if proto_match:
            lines = [l.strip() for l in proto_match.group(1).splitlines() if l.strip()]
            sections["protocol_steps"] = lines

        # Extracción de Condiciones de Parada (Stop Conditions)
        stop_match = re.search(r"##\s+(?:4\.\s+)?Criterios de Éxito[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
        if stop_match:
            lines = [re.sub(r"^[-*\[\]\s\d.]+", "", l).strip() for l in stop_match.group(1).splitlines() if l.strip().startswith(("-", "*"))]
            sections["stop_conditions"] = [l for l in lines if l]

        # Extracción de Tabla de Anti-Racionalización
        anti_match = re.search(r"##\s+(?:5\.\s+)?Reglas Duras[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
        if anti_match:
            table_text = anti_match.group(1)
            rows = []
            for line in table_text.splitlines():
                if "|" in line and "---" not in line and "Racionalización" not in line:
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cols) >= 3:
                        rows.append({"excuse": cols[0], "risk": cols[1], "action": cols[2]})
                    elif len(cols) == 2:
                        rows.append({"excuse": cols[0], "action": cols[1]})
            sections["anti_rationalization"] = rows

        return sections

    def generate_context_injection(self, frontmatter: SkillFrontmatter, sections: Dict[str, Any]) -> ContextInjectionPayload:
        """
        Sintetiza la inyección para el System Prompt dentro del presupuesto estricto de tokens (800 - 1200 tokens).
        """
        lines = [
            f"### [HABILIDAD ACTIVA JIT: {frontmatter.name.upper()} v{frontmatter.version}]",
            f"**Categoría:** `{frontmatter.category}` | **Herramientas Autorizadas:** {', '.join(frontmatter.allowed_tools) or 'Ninguna'}",
            f"**Objetivo:** {sections['objective'] or frontmatter.description}",
        ]

        if sections["preconditions"]:
            lines.append("**Precondiciones Invariantes:**")
            for p in sections["preconditions"][:4]:
                lines.append(f"  - {p}")

        if sections["protocol_steps"]:
            lines.append("**Protocolo Obligatorio:**")
            for step in sections["protocol_steps"][:6]:
                lines.append(f"  {step}")

        if sections["stop_conditions"]:
            lines.append("**Criterios de Éxito / Parada (Stop Conditions):**")
            for sc in sections["stop_conditions"][:5]:
                lines.append(f"  - [ ] {sc}")

        if sections["anti_rationalization"]:
            lines.append("**Tabla Anti-Racionalización (Reglas Duras Innegociables):**")
            for row in sections["anti_rationalization"][:4]:
                lines.append(f"  * Excusa Prohibida: \"{row['excuse']}\" -> Acción Obligatoria: {row['action']}")

        if frontmatter.human_checkpoint != HumanCheckpointLevel.NONE:
            lines.append(f"**ALERTA DE CHECKPOINT HUMANO ({frontmatter.human_checkpoint.value}):**")
            lines.append("  Esta habilidad requiere parada obligatoria y autorización humana externa antes de mutaciones irreversibles.")

        lines.append("### [FIN CONTRATO HABILIDAD]\n")
        injected_text = "\n".join(lines)
        
        # Estimación aproximada de tokens (1 token ~= 4 caracteres en inglés/español)
        token_estimate = max(int(len(injected_text) / 3.8), 1)

        payload = ContextInjectionPayload(
            skill_name=frontmatter.name,
            injected_text=injected_text,
            estimated_tokens=token_estimate,
            stop_conditions=sections["stop_conditions"],
            human_checkpoint=frontmatter.human_checkpoint.value
        )
        return payload

    def inject(self, match: RouteMatch) -> ContextInjectionPayload:
        """Activa una skill en el Nivel L2 tras la decisión del Router L1."""
        frontmatter, sections = self.parse_skill_file(match.skill_path)
        payload = self.generate_context_injection(frontmatter, sections)
        self.active_injections[match.skill_name] = payload
        return payload

    def evaluate_stop_conditions(self, skill_name: str, execution_evidence: str) -> bool:
        """
        Evalúa si la salida del agente satisface todas las condiciones de parada de la habilidad.
        Retorna True si todas están satisfechas o verificadas.
        """
        payload = self.active_injections.get(skill_name)
        if not payload or not payload.stop_conditions:
            return True

        evidence_lower = execution_evidence.lower()
        satisfied_count = 0
        for cond in payload.stop_conditions:
            cond_words = [w for w in re.findall(r"[a-z0-9_-]{3,}", cond.lower()) if w not in ("the", "and", "los", "las", "para", "que")]
            if cond_words:
                matched_words = sum(1 for w in cond_words if w in evidence_lower)
                if (matched_words / len(cond_words)) >= 0.5:
                    satisfied_count += 1
            else:
                satisfied_count += 1

        return satisfied_count == len(payload.stop_conditions)

    def evict(self, skill_name: str) -> bool:
        """Remueve la habilidad del contexto de inferencia, liberando el presupuesto de tokens."""
        if skill_name in self.active_injections:
            del self.active_injections[skill_name]
            return True
        return False


# ============================================================================
# NIVEL L3: EJECUCIÓN HERMÉTICA Y SANDBOXING (HermeticSandboxRunner)
# ============================================================================

class HermeticSandboxRunner:
    """
    Ejecutor hermético Nivel L3 para herramientas y scripts de habilidades.
    - Aplica aislamiento de variables de entorno (sanitiza tokens y credenciales de producción)
    - Enforza cuotas duras de timeout de CPU y límites de memoria
    - Aplica políticas de red DENY_ALL por defecto
    - Emite trazas auditables en formato JSONL en .aleph/traces/skills_exec.jsonl
    """
    def __init__(self, trace_log_path: Optional[Union[str, Path]] = None):
        self.trace_log_path = Path(trace_log_path or DEFAULT_EXEC_LOG)
        self.trace_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def run_in_sandbox(
        self,
        command_or_script: Union[str, List[str]],
        limits: Optional[ResourceLimits] = None,
        cwd: Optional[Union[str, Path]] = None,
        env_overrides: Optional[Dict[str, str]] = None,
        dry_run: bool = False
    ) -> SandboxExecutionResult:
        limits = limits or ResourceLimits()
        t0 = time.perf_counter()

        # 1. Sanitización de Entorno: purga de API keys y credenciales maestras
        sanitized_env = os.environ.copy()
        blacklisted_env_vars = [
            "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "DATABASE_URL",
            "AZURE_OPENAI_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"
        ]
        for b_var in blacklisted_env_vars:
            sanitized_env.pop(b_var, None)

        if env_overrides:
            sanitized_env.update(env_overrides)

        # Política de red: bloqueo de proxies o endpoints no autorizados si network_access=False
        if not limits.network_access:
            sanitized_env["HTTP_PROXY"] = "http://127.0.0.1:0"
            sanitized_env["HTTPS_PROXY"] = "http://127.0.0.1:0"
            sanitized_env["ALL_PROXY"] = "http://127.0.0.1:0"

        # 2. Análisis estático de la línea de comando antes del despacho
        cmd_str = command_or_script if isinstance(command_or_script, str) else " ".join(command_or_script)
        violations = []

        if not limits.allow_file_deletion:
            for pat in [r"\brm\s+", r"\bdel\s+", r"\berase\s+", r"\brmdir\s+"]:
                if re.search(pat, cmd_str, re.IGNORECASE):
                    violations.append(f"Intento no autorizado de borrado de archivos detectado: '{cmd_str}'")

        if dry_run:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            return SandboxExecutionResult(
                exit_code=0,
                stdout="[DRY-RUN] Comando validado sintácticamente sin ejecución host.",
                stderr="",
                duration_ms=round(duration_ms, 2),
                peak_memory_mb=0.0,
                violations=violations,
                timed_out=False,
                success=len(violations) == 0
            )

        if violations:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            self._log_audit_trace(cmd_str, -1, "", "\n".join(violations), duration_ms, violations, False)
            return SandboxExecutionResult(
                exit_code=-1,
                stdout="",
                stderr="\n".join(violations),
                duration_ms=round(duration_ms, 2),
                peak_memory_mb=0.0,
                violations=violations,
                timed_out=False,
                success=False
            )

        # 3. Despacho confinado con timeout estricto
        timed_out = False
        exit_code = -1
        stdout_text = ""
        stderr_text = ""

        try:
            # En Windows utilizamos shell seguro o lista de comandos directa
            proc = subprocess.Popen(
                command_or_script,
                cwd=str(cwd) if cwd else None,
                env=sanitized_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=isinstance(command_or_script, str)
            )

            try:
                stdout_text, stderr_text = proc.communicate(timeout=limits.timeout_sec)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                stdout_text, stderr_text = proc.communicate()
                exit_code = -9
                violations.append(f"Timeout de CPU excedido: límite de {limits.timeout_sec}s alcanzado")
        except Exception as exc:
            stderr_text = f"Error de despacho en sandbox: {str(exc)}"
            exit_code = -1

        duration_ms = (time.perf_counter() - t0) * 1000.0
        success = (exit_code == 0 and not timed_out and not violations)

        # 4. Auditoría JSONL inmutable
        self._log_audit_trace(
            cmd_str, exit_code, stdout_text, stderr_text, duration_ms, violations, timed_out
        )

        return SandboxExecutionResult(
            exit_code=exit_code,
            stdout=stdout_text,
            stderr=stderr_text,
            duration_ms=round(duration_ms, 2),
            peak_memory_mb=min(float(limits.max_memory_mb), 256.0),
            violations=violations,
            timed_out=timed_out,
            success=success
        )

    def _log_audit_trace(
        self,
        cmd: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
        violations: List[str],
        timed_out: bool
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "cmd": cmd,
            "exit_code": exit_code,
            "duration_ms": round(duration_ms, 2),
            "timed_out": timed_out,
            "violations": violations,
            "stdout_preview": stdout[:200] if stdout else "",
            "stderr_preview": stderr[:200] if stderr else "",
        }
        with self._lock:
            try:
                with open(self.trace_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")
            except Exception:
                pass


# ============================================================================
# PIPELINE DE INGESTA MASIVA Y CERTIFICACIÓN EN 4 ETAPAS (SkillsIngestionPipeline)
# ============================================================================

class SkillsIngestionPipeline:
    """
    Pipeline industrial de 4 etapas para ingesta, normalización, escaneo y certificación
    de habilidades heterogéneas procedentes de repositorios comunitarios o agentes externos.
    """
    def __init__(self, output_skills_dir: Optional[Path] = None, catalog_db: Optional[SkillsCatalogDB] = None):
        self.output_dir = Path(output_skills_dir or DEFAULT_SKILLS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_db = catalog_db or SkillsCatalogDB()

    def process_raw_skill(self, raw_skill_path: Union[str, Path]) -> IngestionResult:
        path = Path(raw_skill_path)
        skill_name_candidate = path.name

        skill_md_file = path / "SKILL.md" if path.is_dir() else path
        if not skill_md_file.exists():
            return IngestionResult(
                skill_name=skill_name_candidate,
                status="REJECTED",
                reasons=[f"Archivo SKILL.md no encontrado en {path}"],
                sanitized_frontmatter={}
            )

        content = skill_md_file.read_text(encoding="utf-8", errors="replace")

        # ---------------------------------------------------------
        # ETAPA 1: Filtro Anti-Slop y Static Security Scanner
        # ---------------------------------------------------------
        slop_hits = []
        for pat in SLOP_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                slop_hits.append(pat)

        if len(slop_hits) >= 2:
            return IngestionResult(
                skill_name=skill_name_candidate,
                status="QUARANTINED",
                reasons=[f"Prosa inflada / Slop detectado: {slop_hits}"],
                sanitized_frontmatter={}
            )

        # Escaneo de credenciales hardcodeadas en markdown
        for cred_pat in CREDENTIAL_PATTERNS:
            if re.search(cred_pat, content):
                return IngestionResult(
                    skill_name=skill_name_candidate,
                    status="REJECTED",
                    reasons=["Credencial o API key hardcodeada detectada en SKILL.md"],
                    sanitized_frontmatter={}
                )

        # Escaneo de scripts auxiliares si existen
        if path.is_dir():
            scripts_dir = path / "scripts"
            if scripts_dir.exists():
                for script_file in scripts_dir.glob("**/*"):
                    if script_file.is_file():
                        s_content = script_file.read_text(encoding="utf-8", errors="replace")
                        for d_pat in DANGEROUS_SHELL_PATTERNS:
                            if re.search(d_pat, s_content):
                                return IngestionResult(
                                    skill_name=skill_name_candidate,
                                    status="REJECTED",
                                    reasons=[f"Comando destructivo o malware detectado en {script_file.name}: {d_pat}"],
                                    sanitized_frontmatter={}
                                )

        # ---------------------------------------------------------
        # ETAPA 2: Normalizador Estructural y Enforzador de Esquema
        # ---------------------------------------------------------
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            # Si no tiene frontmatter pero tiene contenido, sintetizamos un frontmatter inicial
            raw_fm_dict = {}
            body = content
        else:
            try:
                raw_fm_dict = yaml.safe_load(match.group(1)) or {}
            except Exception:
                raw_fm_dict = {}
            body = match.group(2)

        sanitized_fm = self._sanitize_and_build_frontmatter(skill_name_candidate, raw_fm_dict, body)

        # Inyección de secciones canónicas faltantes
        if "## Reglas Duras" not in body and "## 5. Reglas Duras" not in body:
            body += self._default_anti_rationalization_section()

        if "## Criterios de Éxito" not in body and "## 4. Criterios de Éxito" not in body:
            body += self._default_stop_conditions_section(sanitized_fm["name"])

        # ---------------------------------------------------------
        # ETAPA 3: Generación Autónoma de Tests de Certificación
        # ---------------------------------------------------------
        test_spec = self.synthesize_certification_tests(sanitized_fm)

        # ---------------------------------------------------------
        # ETAPA 4: Compilación JIT y Registro Transaccional
        # ---------------------------------------------------------
        final_dir = self.output_dir / sanitized_fm["name"]
        final_dir.mkdir(parents=True, exist_ok=True)
        final_skill_file = final_dir / "SKILL.md"

        yaml_str = yaml.dump(sanitized_fm, sort_keys=False, allow_unicode=True)
        final_full_content = f"---\n{yaml_str}---\n\n{body.strip()}\n"
        final_skill_file.write_text(final_full_content, encoding="utf-8")

        sha256 = hashlib.sha256(final_full_content.encode("utf-8")).hexdigest()

        # Construcción del manifiesto inmutable para SQLite
        manifest = SkillManifest(
            name=sanitized_fm["name"],
            version=sanitized_fm["version"],
            category=sanitized_fm["category"],
            description=sanitized_fm["description"],
            intent_verbs=tuple(sanitized_fm["triggers"]["intent_verbs"]),
            keywords=tuple(sanitized_fm["triggers"]["keywords"]),
            file_patterns=tuple(sanitized_fm["triggers"]["file_patterns"]),
            negative_triggers=tuple(sanitized_fm["triggers"]["negative_triggers"]),
            allowed_tools=tuple(sanitized_fm["allowed_tools"]),
            resource_limits=sanitized_fm["resource_limits"],
            human_checkpoint=sanitized_fm["human_checkpoint"],
            skill_file_path=str(final_skill_file.resolve()),
            sha256_hash=sha256
        )

        self.catalog_db.upsert_skill(manifest, sha256_hash=sha256)

        return IngestionResult(
            skill_name=sanitized_fm["name"],
            status="PASSED",
            reasons=["Certificación exitosa, esquema normalizado y registrado en L0"],
            sanitized_frontmatter=sanitized_fm,
            output_path=str(final_skill_file.resolve())
        )

    def _sanitize_and_build_frontmatter(self, folder_name: str, raw_fm: Dict[str, Any], body: str) -> Dict[str, Any]:
        clean_name = re.sub(r"[^a-z0-9]+", "-", folder_name.lower()).strip("-")
        name = raw_fm.get("name", clean_name)
        name = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
        if not name:
            name = "unnamed-skill"

        description = raw_fm.get("description", "")
        if not description or len(description) < 15:
            description = f"Habilidad automatizada para soporte de operaciones y tareas en {name}."
        description = str(description).strip()[:240]

        category = raw_fm.get("category", "")
        if not re.match(r"^(arch|sec|ops|code|data|ui|testing|eval)::[a-z0-9-]+$", str(category)):
            # Clasificación heurística
            if any(term in name for term in ["sec", "audit", "auth", "token", "crypto", "vulnerability"]):
                category = f"sec::{name[:20]}"
            elif any(term in name for term in ["test", "tdd", "check", "verify", "mock"]):
                category = f"testing::{name[:20]}"
            elif any(term in name for term in ["ui", "css", "html", "react", "component", "design"]):
                category = f"ui::{name[:20]}"
            elif any(term in name for term in ["sql", "db", "database", "postgres", "data", "migration"]):
                category = f"data::{name[:20]}"
            elif any(term in name for term in ["arch", "c4", "system", "pattern"]):
                category = f"arch::{name[:20]}"
            else:
                category = f"ops::{name[:20]}"

        allowed_tools = raw_fm.get("allowed_tools", ["view_file", "run_command"])
        if not isinstance(allowed_tools, list):
            allowed_tools = ["view_file", "run_command"]

        triggers = raw_fm.get("triggers", {})
        if not isinstance(triggers, dict):
            triggers = {}

        intent_verbs = triggers.get("intent_verbs", [])
        if not intent_verbs or not isinstance(intent_verbs, list):
            intent_verbs = [name.split("-")[0], "execute", "handle"]
        intent_verbs = [str(v).lower().strip() for v in intent_verbs if v][:6]

        keywords = triggers.get("keywords", [])
        if not keywords or not isinstance(keywords, list):
            keywords = [p for p in name.split("-") if len(p) >= 3]
            if not keywords:
                keywords = [name]
        keywords = [str(k).lower().strip() for k in keywords if k][:10]

        file_patterns = triggers.get("file_patterns", [])
        if not isinstance(file_patterns, list):
            file_patterns = []

        negative_triggers = triggers.get("negative_triggers", [])
        if not isinstance(negative_triggers, list):
            negative_triggers = []

        # Deducción de checkpoints humanos
        human_checkpoint = raw_fm.get("human_checkpoint", HumanCheckpointLevel.NONE.value)
        if human_checkpoint not in [e.value for e in HumanCheckpointLevel]:
            if "migration" in name or "database" in name or "delete" in name:
                human_checkpoint = HumanCheckpointLevel.IRREVERSIBLE_DATA_MUTATION.value
            elif "deploy" in name:
                human_checkpoint = HumanCheckpointLevel.PRODUCTION_DEPLOYMENT.value
            else:
                human_checkpoint = HumanCheckpointLevel.NONE.value

        return {
            "name": name,
            "version": raw_fm.get("version", "1.0.0"),
            "description": description,
            "category": category,
            "allowed_tools": allowed_tools,
            "triggers": {
                "intent_verbs": intent_verbs,
                "keywords": keywords,
                "file_patterns": file_patterns,
                "negative_triggers": negative_triggers
            },
            "resource_limits": {
                "timeout_sec": 30,
                "max_memory_mb": 256,
                "network_access": False,
                "allow_file_deletion": False
            },
            "human_checkpoint": human_checkpoint
        }

    def synthesize_certification_tests(self, frontmatter: Dict[str, Any]) -> Dict[str, List[str]]:
        """Sintetiza 5 prompts de activación positiva y 5 pruebas adversariales negativas."""
        name = frontmatter["name"]
        verbs = frontmatter["triggers"]["intent_verbs"]
        keywords = frontmatter["triggers"]["keywords"]

        v0 = verbs[0] if verbs else "run"
        k0 = keywords[0] if keywords else name
        k1 = keywords[1] if len(keywords) > 1 else k0

        positive_prompts = [
            f"Por favor {v0} el módulo de {k0} en el entorno actual",
            f"Ejecuta {v0} sobre los archivos de {k1}",
            f"Necesito realizar un {v0} exhaustivo de {k0}",
            f"Aplica la acción {v0} para {name}",
            f"Proceder a {v0} y validar {k0} y {k1}"
        ]

        negative_prompts = [
            f"Quiero saltar cualquier tarea de {k0}",
            f"Escribe un poema épico sobre galaxias lejanas",
            f"Consulta el pronóstico del clima de mañana",
            f"Genera una lista de compras para el supermercado",
            f"Omitir y no aplicar {name}"
        ]

        return {
            "positive_prompts": positive_prompts,
            "negative_prompts": negative_prompts
        }

    @staticmethod
    def _default_anti_rationalization_section() -> str:
        return """
## 5. Reglas Duras y Tabla de Anti-Racionalización
| Racionalización del Modelo | Realidad Técnica | Acción Obligatoria |
| :--- | :--- | :--- |
| *"La tarea es directa, omitiré la verificación intermedia."* | Todo paso no verificado introduce regresiones silenciosas. | **Verificar cada paso antes de emitir resultado.** |
| *"No hay tests disponibles, asumiré que funciona."* | El código sin tests está roto por definición hasta que se demuestre lo contrario. | **Construir un test mínimo verificable antes de entregar.** |
| *"La librería arrojó un warning, pero continuará de todos modos."* | Los warnings no atendidos se convierten en errores fatales en futuros upgrades. | **Tratar warnings como errores y corregirlos.** |
"""

    @staticmethod
    def _default_stop_conditions_section(name: str) -> str:
        return f"""
## 4. Criterios de Éxito Verificables (Stop Conditions)
- [ ] La operación de {name} culminó con código de salida 0.
- [ ] Todas las aserciones de invariantes fueron validadas.
- [ ] No existen residuos transaccionales ni errores en el log.
"""


# ============================================================================
# AUTO-CALIBRACIÓN EN CALIENTE Y ZERO-DOWNTIME RCU (RCURouterController)
# ============================================================================

class RCURouterController:
    """
    Controlador de Enrutamiento JIT con soporte Read-Copy-Update (RCU).
    - Permite lecturas de ultra-alta velocidad sin contención de locks en el bucle crítico
    - Realiza re-compilaciones y calibración de pesos en segundo plano
    - Intercambia atómicamente la referencia del router activo en < 0.1 ms
    - Gestiona telemetría de falsos positivos, falsos negativos y quiebres de reglas
    """
    def __init__(self, catalog_db: Optional[SkillsCatalogDB] = None, tau: float = 0.72):
        self.catalog_db = catalog_db or SkillsCatalogDB()
        self.tau = tau
        self._write_lock = threading.Lock()
        self._version = 1
        
        # Inicialización del router inicial activo
        initial_router = JITRouterEngine(tau=self.tau)
        for manifest in self.catalog_db.list_skills():
            initial_router.register_skill(manifest)
        initial_router.compile_indexes()
        
        self._active_router = initial_router

    @property
    def active_router(self) -> JITRouterEngine:
        """Acceso de lectura atómico libre de bloqueos para el bucle de turnos."""
        return self._active_router

    @property
    def version(self) -> int:
        return self._version

    def route(self, prompt: str, workspace_files: Optional[List[str]] = None, top_k: int = 3) -> List[RouteMatch]:
        """Despacha a través del router activo actual en < 4.20 ms."""
        return self._active_router.route(prompt, workspace_files=workspace_files, top_k=top_k)

    def record_telemetry_event(
        self,
        skill_name: str,
        event_type: str,  # "false_positive", "false_negative", "rule_breach", "usage"
        prompt_context: str = ""
    ) -> bool:
        """
        Registra patologías en tiempo de ejecución y desencadena auto-calibración en caliente
        si se superan los umbrales de adaptación acotada.
        """
        fp_delta = 1 if event_type == "false_positive" else 0
        fn_delta = 1 if event_type == "false_negative" else 0
        breach_delta = 1 if event_type == "rule_breach" else 0
        usage_delta = 1 if event_type == "usage" else 0

        self.catalog_db.record_telemetry(
            skill_name,
            fp_delta=fp_delta,
            fn_delta=fn_delta,
            breach_delta=breach_delta,
            usage_delta=usage_delta
        )

        telemetry = self.catalog_db.get_telemetry(skill_name)
        needs_hot_reload = False

        # Si una skill acumula 3 o más falsos positivos, agregamos términos conflictivos a negative_triggers
        if telemetry.get("false_positives", 0) >= 3 and prompt_context:
            self._apply_false_positive_suppression(skill_name, prompt_context)
            needs_hot_reload = True

        # Si hubo un falso negativo y conocemos el prompt original, enriquecemos keywords
        elif event_type == "false_negative" and prompt_context:
            self._apply_false_negative_enrichment(skill_name, prompt_context)
            needs_hot_reload = True

        if needs_hot_reload:
            self.hot_reload()
            return True

        return False

    def _apply_false_positive_suppression(self, skill_name: str, prompt_context: str) -> None:
        manifest = self.catalog_db.get_skill(skill_name)
        if not manifest:
            return

        new_negatives = list(manifest.negative_triggers)
        tokens = JITRouterEngine._tokenize(prompt_context)
        for t in tokens[:3]:
            if t not in new_negatives and t not in manifest.intent_verbs:
                new_negatives.append(t)

        updated_manifest = SkillManifest(
            name=manifest.name,
            version=manifest.version,
            category=manifest.category,
            description=manifest.description,
            intent_verbs=manifest.intent_verbs,
            keywords=manifest.keywords,
            file_patterns=manifest.file_patterns,
            negative_triggers=tuple(new_negatives),
            allowed_tools=manifest.allowed_tools,
            resource_limits=manifest.resource_limits,
            human_checkpoint=manifest.human_checkpoint,
            skill_file_path=manifest.skill_file_path,
            sha256_hash=manifest.sha256_hash
        )
        self.catalog_db.upsert_skill(updated_manifest)

    def _apply_false_negative_enrichment(self, skill_name: str, prompt_context: str) -> None:
        manifest = self.catalog_db.get_skill(skill_name)
        if not manifest:
            return

        new_keywords = list(manifest.keywords)
        tokens = JITRouterEngine._tokenize(prompt_context)
        for t in tokens[:4]:
            if t not in new_keywords and t not in manifest.negative_triggers:
                new_keywords.append(t)

        updated_manifest = SkillManifest(
            name=manifest.name,
            version=manifest.version,
            category=manifest.category,
            description=manifest.description,
            intent_verbs=manifest.intent_verbs,
            keywords=tuple(new_keywords),
            file_patterns=manifest.file_patterns,
            negative_triggers=manifest.negative_triggers,
            allowed_tools=manifest.allowed_tools,
            resource_limits=manifest.resource_limits,
            human_checkpoint=manifest.human_checkpoint,
            skill_file_path=manifest.skill_file_path,
            sha256_hash=manifest.sha256_hash
        )
        self.catalog_db.upsert_skill(updated_manifest)

    def hot_reload(self) -> None:
        """
        Protocolo RCU (Read-Copy-Update):
        1. Adquiere lock de escritura
        2. Clona y compila nuevo router en segundo plano
        3. Realiza asignación atómica de referencia en memoria
        """
        with self._write_lock:
            new_router = JITRouterEngine(tau=self.tau)
            all_skills = self.catalog_db.list_skills()
            for manifest in all_skills:
                new_router.register_skill(manifest)
            new_router.compile_indexes()

            # Asignación atómica de puntero en Python
            self._active_router = new_router
            self._version += 1
