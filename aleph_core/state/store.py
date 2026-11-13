"""
Motor de Persistencia y Manejo Atómico de Estado (v2.6.0).
Implementa SQLite con WAL, mutaciones atómicas en 2 fases en disco y tablas para:
- epistemic_claims
- state_leases
- task_ledger
- algorithmic_rules (Bitácora de reglas SI -> ENTONCES -> EVITAR con deduplicación)
- knowledge_graph (Nodos y aristas de memoria semántica a largo plazo)
- session_checkpoints (Checkpointing jerárquico y compresión contextual estructural zlib)
- semantic_task_cache (Caché semántica exacta y de normalización AST libre de embeddings / costo $0)
"""
import os
import sqlite3
import json
import time
import zlib
import base64
import uuid
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
from aleph_core.config import DB_PATH, SQLITE_TIMEOUT_SEC, DEFAULT_LEASE_TIMEOUT_SEC
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus

@dataclass
class SessionCheckpoint:
    checkpoint_id: str
    session_id: str
    step_number: int
    parent_checkpoint_id: Optional[str]
    active_rule_ids: List[str]
    compact_summary: str
    working_memory_json: str
    compressed_state_blob: str
    created_at: float = field(default_factory=time.time)

@dataclass
class CachedTaskResult:
    cache_key: str
    task_type: str
    input_hash: str
    ast_canonical_hash: Optional[str]
    output_payload: Any
    epistemic_status: str
    proof_hash: Optional[str]
    hit_count: int
    created_at: float

class StateStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connection(self):
        """Context manager que asegura apertura con WAL y cierre determinista de handles (crucial en Windows/Linux)."""
        conn = sqlite3.connect(str(self.db_path), timeout=SQLITE_TIMEOUT_SEC)
        conn.row_factory = sqlite3.Row
        try:
            res = conn.execute("PRAGMA journal_mode = WAL;").fetchone()
            if not res or str(res[0]).lower() != "wal":
                conn.execute("PRAGMA journal_mode = MEMORY;")
        except sqlite3.OperationalError:
            conn.close()
            import tempfile
            fallback = Path(tempfile.gettempdir()) / self.db_path.name
            self.db_path = fallback
            conn = sqlite3.connect(str(self.db_path), timeout=SQLITE_TIMEOUT_SEC)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS epistemic_claims (
                    claim_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    proof_hash TEXT,
                    proof_output TEXT,
                    verified_at REAL,
                    metadata_json TEXT
                );

                CREATE TABLE IF NOT EXISTS state_leases (
                    resource_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    acquired_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS task_ledger (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    input_payload TEXT NOT NULL,
                    output_payload TEXT,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    completed_at REAL
                );

                CREATE TABLE IF NOT EXISTS algorithmic_rules (
                    rule_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    friction_pattern TEXT NOT NULL,
                    if_condition TEXT NOT NULL,
                    then_action TEXT NOT NULL,
                    avoid_anti_pattern TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Activa',
                    confidence REAL NOT NULL DEFAULT 0.90,
                    hit_count INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS kg_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS kg_edges (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    PRIMARY KEY (source_id, target_id, relation)
                );

                CREATE TABLE IF NOT EXISTS session_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    parent_checkpoint_id TEXT,
                    active_rule_ids TEXT NOT NULL,
                    compact_summary TEXT NOT NULL,
                    working_memory_json TEXT NOT NULL,
                    compressed_state_blob TEXT NOT NULL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS semantic_task_cache (
                    cache_key TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    ast_canonical_hash TEXT,
                    output_payload_json TEXT NOT NULL,
                    epistemic_status TEXT NOT NULL,
                    proof_hash TEXT,
                    hit_count INTEGER NOT NULL DEFAULT 1,
                    created_at REAL NOT NULL,
                    last_accessed_at REAL NOT NULL
                );
            """)
            conn.commit()

    def save_claim(self, claim: EpistemicClaim):
        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO epistemic_claims
                (claim_id, description, payload_json, status, proof_hash, proof_output, verified_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim.claim_id,
                claim.description,
                json.dumps(claim.payload, ensure_ascii=False),
                claim.status.value,
                claim.proof_hash,
                claim.proof_output,
                claim.verified_at,
                json.dumps(claim.metadata, ensure_ascii=False)
            ))
            conn.commit()

    def get_claim(self, claim_id: str) -> Optional[EpistemicClaim]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM epistemic_claims WHERE claim_id = ?", (claim_id,)
            ).fetchone()
            if not row:
                return None
            return EpistemicClaim(
                claim_id=row["claim_id"],
                description=row["description"],
                payload=json.loads(row["payload_json"]),
                status=EpistemicStatus(row["status"]),
                proof_hash=row["proof_hash"],
                proof_output=row["proof_output"],
                verified_at=row["verified_at"],
                metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {}
            )

    def list_claims(self, status: Optional[EpistemicStatus] = None) -> List[EpistemicClaim]:
        with self._connection() as conn:
            if status:
                rows = conn.execute("SELECT * FROM epistemic_claims WHERE status = ? ORDER BY verified_at DESC", (status.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM epistemic_claims ORDER BY verified_at DESC").fetchall()
            return [
                EpistemicClaim(
                    claim_id=r["claim_id"],
                    description=r["description"],
                    payload=json.loads(r["payload_json"]),
                    status=EpistemicStatus(r["status"]),
                    proof_hash=r["proof_hash"],
                    proof_output=r["proof_output"],
                    verified_at=r["verified_at"],
                    metadata=json.loads(r["metadata_json"]) if r["metadata_json"] else {}
                )
                for r in rows
            ]

    def record_task_start(self, task_id: str, task_type: str, input_payload: Dict[str, Any]):
        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_ledger
                (task_id, task_type, input_payload, status, created_at)
                VALUES (?, ?, ?, 'RUNNING', ?)
            """, (task_id, task_type, json.dumps(input_payload, ensure_ascii=False), time.time()))
            conn.commit()

    def record_task_completion(self, task_id: str, status: str, output_payload: Any = None):
        with self._connection() as conn:
            conn.execute("""
                UPDATE task_ledger
                SET status = ?, output_payload = ?, completed_at = ?
                WHERE task_id = ?
            """, (status, json.dumps(output_payload, ensure_ascii=False) if output_payload is not None else None, time.time(), task_id))
            conn.commit()

    def acquire_lease(self, resource_id: str, agent_id: str, timeout_sec: float = DEFAULT_LEASE_TIMEOUT_SEC) -> bool:
        now = time.time()
        expires = now + timeout_sec
        with self._connection() as conn:
            conn.execute("DELETE FROM state_leases WHERE resource_id = ? AND expires_at < ?", (resource_id, now))
            try:
                conn.execute(
                    "INSERT INTO state_leases (resource_id, agent_id, acquired_at, expires_at) VALUES (?, ?, ?, ?)",
                    (resource_id, agent_id, now, expires)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def release_lease(self, resource_id: str, agent_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                "DELETE FROM state_leases WHERE resource_id = ? AND agent_id = ?",
                (resource_id, agent_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def atomic_write_file(target_path: Path, content: str) -> None:
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            dir=str(target_path.parent),
            prefix=f".{target_path.name}.",
            suffix=".tmp",
        )
        temp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target_path)
        except BaseException:
            if temp_path.exists():
                temp_path.unlink()
            raise

    # Métodos nativos de Checkpointing Jerárquico y Compresión Contextual
    def create_session_checkpoint(
        self,
        session_id: str,
        step_number: int,
        working_memory: Dict[str, Any],
        compact_summary: str,
        active_rule_ids: List[str],
        parent_checkpoint_id: Optional[str] = None
    ) -> SessionCheckpoint:
        cid = f"chk_{uuid.uuid4().hex[:12]}"
        mem_str = json.dumps(working_memory, ensure_ascii=False)
        compressed = base64.b64encode(zlib.compress(mem_str.encode("utf-8"))).decode("ascii")

        chk = SessionCheckpoint(
            checkpoint_id=cid,
            session_id=session_id,
            step_number=step_number,
            parent_checkpoint_id=parent_checkpoint_id,
            active_rule_ids=active_rule_ids,
            compact_summary=compact_summary,
            working_memory_json=mem_str,
            compressed_state_blob=compressed,
            created_at=time.time()
        )

        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO session_checkpoints
                (checkpoint_id, session_id, step_number, parent_checkpoint_id, active_rule_ids, compact_summary, working_memory_json, compressed_state_blob, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chk.checkpoint_id, chk.session_id, chk.step_number, chk.parent_checkpoint_id,
                json.dumps(chk.active_rule_ids), chk.compact_summary, chk.working_memory_json,
                chk.compressed_state_blob, chk.created_at
            ))
            conn.commit()
        return chk

    def load_latest_session_checkpoint(self, session_id: str) -> Optional[SessionCheckpoint]:
        with self._connection() as conn:
            row = conn.execute("""
                SELECT * FROM session_checkpoints
                WHERE session_id = ?
                ORDER BY step_number DESC, created_at DESC
                LIMIT 1
            """, (session_id,)).fetchone()
            if not row:
                return None
            return SessionCheckpoint(
                checkpoint_id=row["checkpoint_id"],
                session_id=row["session_id"],
                step_number=row["step_number"],
                parent_checkpoint_id=row["parent_checkpoint_id"],
                active_rule_ids=json.loads(row["active_rule_ids"]),
                compact_summary=row["compact_summary"],
                working_memory_json=row["working_memory_json"],
                compressed_state_blob=row["compressed_state_blob"],
                created_at=row["created_at"]
            )

    @staticmethod
    def restore_checkpoint_memory(checkpoint: SessionCheckpoint) -> Dict[str, Any]:
        raw_bytes = zlib.decompress(base64.b64decode(checkpoint.compressed_state_blob.encode("ascii")))
        return json.loads(raw_bytes.decode("utf-8"))

    # ==============================================================
    # CACHÉ SEMÁNTICA EXACTA + CANONIZACIÓN AST (NIVEL 9 v2.6.0)
    # ==============================================================
    @staticmethod
    def compute_ast_canonical_hash(code_snippet: str) -> Optional[str]:
        """Calcula un hash SHA-256 canónico normalizado sobre el AST ignorando comentarios y espacios."""
        try:
            import ast
            tree = ast.parse(code_snippet)
            # ast.dump normaliza nombres y estructura eliminando comentarios y espacios arbitrarios
            dumped = ast.dump(tree, include_attributes=False)
            return hashlib.sha256(dumped.encode("utf-8")).hexdigest()
        except Exception:
            return None

    @staticmethod
    def compute_payload_hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def query_semantic_cache(
        self,
        task_type: str,
        input_payload: Dict[str, Any],
        formal_source_code: Optional[str] = None
    ) -> Optional[CachedTaskResult]:
        inp_hash = self.compute_payload_hash(input_payload)
        ast_hash = self.compute_ast_canonical_hash(formal_source_code) if formal_source_code else None
        now = time.time()

        with self._connection() as conn:
            row = None
            if ast_hash:
                # Búsqueda por identidad canónica estructural AST
                row = conn.execute("""
                    SELECT * FROM semantic_task_cache
                    WHERE task_type = ? AND ast_canonical_hash = ?
                    LIMIT 1
                """, (task_type, ast_hash)).fetchone()

            if not row:
                # Búsqueda por hash exacto del payload de entrada
                row = conn.execute("""
                    SELECT * FROM semantic_task_cache
                    WHERE task_type = ? AND input_hash = ?
                    LIMIT 1
                """, (task_type, inp_hash)).fetchone()

            if not row:
                return None

            conn.execute("""
                UPDATE semantic_task_cache
                SET hit_count = hit_count + 1, last_accessed_at = ?
                WHERE cache_key = ?
            """, (now, row["cache_key"]))
            conn.commit()

            return CachedTaskResult(
                cache_key=row["cache_key"],
                task_type=row["task_type"],
                input_hash=row["input_hash"],
                ast_canonical_hash=row["ast_canonical_hash"],
                output_payload=json.loads(row["output_payload_json"]),
                epistemic_status=row["epistemic_status"],
                proof_hash=row["proof_hash"],
                hit_count=row["hit_count"] + 1,
                created_at=row["created_at"]
            )

    def store_semantic_cache(
        self,
        task_type: str,
        input_payload: Dict[str, Any],
        output_payload: Any,
        epistemic_status: str,
        proof_hash: Optional[str],
        formal_source_code: Optional[str] = None
    ) -> str:
        inp_hash = self.compute_payload_hash(input_payload)
        ast_hash = self.compute_ast_canonical_hash(formal_source_code) if formal_source_code else None
        now = time.time()
        cache_key = f"cache_{hashlib.sha256(f'{task_type}:{inp_hash}:{ast_hash}'.encode('utf-8')).hexdigest()[:16]}"

        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO semantic_task_cache
                (cache_key, task_type, input_hash, ast_canonical_hash, output_payload_json, epistemic_status, proof_hash, hit_count, created_at, last_accessed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                cache_key,
                task_type,
                inp_hash,
                ast_hash,
                json.dumps(output_payload, ensure_ascii=False),
                epistemic_status,
                proof_hash,
                now,
                now
            ))
            conn.commit()
        return cache_key
